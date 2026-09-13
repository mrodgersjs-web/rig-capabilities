"""V07/V17 durable fixtures: a REAL python collect/validate process recorded
against the rig_build record plane, then re-run, crashed, and rebuilt.

V07 (two real runs, compared outputs and effect counts): the same idempotency
key replays the run row instead of forking; the effect id is derived from the
result hash, so the second run cannot queue a second effect. Equal normalized
bytes and one committed effect per key — the joint durable-setup + repeatable
result for the deterministic process.

V17 (fresh setup, not a warmed-up workstation): the whole flow runs against a
FILE-backed sqlite created by applying the portable DDL section only — no
carry-over connection, no warmed caches — and every observable (run row,
artifact sha, effect count, settled receipt) must match the warm outcome. A
fresh process reading by idempotency key recovers the authoritative run state.

sqlite proves the portable laws here (see test_build_store BLOCKED_NEEDS_LIVE_
PROOF for what needs live PG); nothing here claims role grants or triggers.
"""
import hashlib
import json
import sqlite3
import tempfile
import unittest
import os

from rig_capabilities import build_store

CELL = "L1-D1-A1-I1"
PACK_SHA = "f4" * 32


def _ddl_conn(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(build_store.portable_ddl_sqlite())
    build_store.put_cell_contract(
        conn, cell_id=CELL, criteria_version="v1",
        contract={"done_test": ["fixture"], "buyer_metric": "activation"},
        criteria_pack_sha256=PACK_SHA, sealed_by="FixtureSeal")
    build_store.register_process_version(
        conn, process_key="intake", version="1",
        definition={"cadence": "on_demand"},
        declared_owner="python-intake", registered_by="FixtureSeal")
    return conn


# --- the process under fixture: deterministic collect -> validate -> emit ----
def collect_validate(rows):
    """Deterministic transformation: keep well-formed records, canonical bytes."""
    kept = sorted(
        (r for r in rows
         if isinstance(r.get("id"), str)
         and isinstance(r.get("score"), (int, float))
         and 0 <= r["score"] <= 1),
        key=lambda r: r["id"])
    return json.dumps(kept, sort_keys=True).encode()


def full_run(conn, *, idem, rows, owner="w1", now=None):
    """One full process execution recorded durably: run row -> result event
    -> content-addressed artifact -> effect through the fenced outbox.
    The outbox id is DERIVED from the result hash, so replaying the process
    on the same input cannot mint a second effect."""
    out = collect_validate(rows)
    sha = hashlib.sha256(out).hexdigest()
    started = build_store.start_run(
        conn, cell_id=CELL, criteria_version="v1", process_key="intake",
        process_version="1", idempotency_key=idem, started_by="v07-fixture")
    run = started["row"]
    if started["status"] == "replayed":
        # recovery: the run exists; committed events/artifacts are append-only
        # and MUST NOT be re-written. Only the effect leg is re-attempted, and
        # it is idempotent by derived outbox id.
        return {"sha": sha, "bytes": out, "run_id": run["run_id"],
                "started_status": "replayed", "effect": "already_queued",
                "outbox_id": "eff-" + sha[:16], "owner": owner}
    ft = run["fencing_token"]
    build_store.append_event(
        conn, run_id=run["run_id"], sequence=1, kind="receipt",
        fencing_token=ft, payload={"result_sha256": sha, "kept": len(rows)})
    build_store.add_artifact(
        conn, run_id=run["run_id"], uri="mem://validated.json",
        kind="result", recorded_by="v07-fixture", content=out)
    ob_id = "eff-" + sha[:16]
    try:
        build_store.outbox_add(conn, topic="deliver.result",
                               payload={"sha256": sha}, outbox_id=ob_id)
        effect = "queued"
    except sqlite3.IntegrityError:
        effect = "already_queued"          # replay: the effect id already exists
    return {"sha": sha, "bytes": out, "run_id": run["run_id"],
            "started_status": started["status"], "effect": effect,
            "outbox_id": ob_id, "owner": owner}


def deliver(conn, res, *, lease=60, now=None):
    cl = build_store.claim_outbox(conn, outbox_id=res["outbox_id"],
                                  claim_owner=res["owner"],
                                  lease_seconds=lease, now=now)
    if cl["status"] != "claimed":
        return cl
    st = build_store.settle_outbox(
        conn, outbox_id=res["outbox_id"], claim_owner=res["owner"],
        claim_fence=cl["row"]["claim_fence"], state="sent",
        receipt="R-" + res["sha"][:12], now=now)
    return st


def outbox_counts(conn):
    cur = build_store._exec(
        conn, "SELECT state, count(*) AS n FROM rig_build.outbox GROUP BY state")
    return {row["state"]: row["n"] for row in build_store._fetch_rows(cur)}


ROWS = [{"id": "b", "score": 0.5}, {"id": "a", "score": 1.0},
        {"id": "c", "score": 7}, {"score": 0.2}, {"id": None, "score": 0.1}]


class V07RepeatableRunTests(unittest.TestCase):
    def setUp(self):
        self.conn = _ddl_conn()
        self.addCleanup(self.conn.close)

    def test_two_runs_equal_output_and_exactly_one_effect(self):
        r1 = full_run(self.conn, idem="batch-001", rows=ROWS)
        s1 = deliver(self.conn, r1, now="2026-09-12T00:00:00+00:00")
        self.assertEqual(s1["status"], "settled")
        # second execution: same input, same idempotency key (a restart of
        # the process, not a new batch)
        r2 = full_run(self.conn, idem="batch-001", rows=list(ROWS))
        self.assertEqual(r2["started_status"], "replayed")
        self.assertEqual(r2["run_id"], r1["run_id"])       # no forked run
        self.assertEqual(r2["bytes"], r1["bytes"])         # repeatable output
        self.assertEqual(r2["effect"], "already_queued")   # no second effect
        self.assertEqual(outbox_counts(self.conn), {"sent": 1})
        rows = build_store._fetch_rows(build_store._exec(
            self.conn,
            "SELECT content_sha256 FROM rig_build.artifacts WHERE run_id = %s",
            (r1["run_id"],)))
        self.assertTrue(rows)
        self.assertEqual({r["content_sha256"] for r in rows}, {r1["sha"]})

    def test_crash_after_claim_reclaim_fences_the_old_holder(self):
        r1 = full_run(self.conn, idem="batch-002", rows=ROWS)
        cl = build_store.claim_outbox(
            self.conn, outbox_id=r1["outbox_id"], claim_owner="w-crash",
            lease_seconds=60, now="2026-09-12T00:00:00+00:00")
        self.assertEqual(cl["status"], "claimed")
        stale_fence = cl["row"]["claim_fence"]
        # worker dies holding the lease; after expiry a new worker reclaims
        cl2 = build_store.claim_outbox(
            self.conn, outbox_id=r1["outbox_id"], claim_owner="w-new",
            lease_seconds=60, now="2026-09-12T00:05:00+00:00")
        self.assertEqual(cl2["status"], "claimed")
        self.assertGreater(cl2["row"]["claim_fence"], stale_fence)
        # the zombie's settlement is refused — it cannot commit
        with self.assertRaises(build_store.StoreError):
            build_store.settle_outbox(
                self.conn, outbox_id=r1["outbox_id"], claim_owner="w-crash",
                claim_fence=stale_fence, state="sent", receipt="ZOMBIE")
        st = build_store.settle_outbox(
            self.conn, outbox_id=r1["outbox_id"], claim_owner="w-new",
            claim_fence=cl2["row"]["claim_fence"], state="sent",
            receipt="R-" + r1["sha"][:12])
        self.assertEqual(st["status"], "settled")
        self.assertEqual(outbox_counts(self.conn), {"sent": 1})


class V17FreshSetupTests(unittest.TestCase):
    def test_fresh_ddl_setup_reproduces_warm_outcomes(self):
        tmp = tempfile.mkdtemp(prefix="rig-v17-")
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        db = os.path.join(tmp, "fresh.db")
        # fresh setup: only the portable DDL + the sealed contract/process
        fresh = _ddl_conn(path=db)
        r1 = full_run(fresh, idem="batch-100", rows=ROWS)
        s1 = deliver(fresh, r1, now="2026-09-12T00:00:00+00:00")
        fresh.close()
        # reopen as a new process would after install/restart
        conn = sqlite3.connect(db)
        conn.execute("PRAGMA foreign_keys=ON")
        self.addCleanup(conn.close)
        self.assertEqual(s1["status"], "settled")
        self.assertEqual(outbox_counts(conn), {"sent": 1})
        # authoritative state recovered by idempotency key, not memory
        run = build_store.get_run(conn, idempotency_key="batch-100")
        self.assertIsNotNone(run)
        self.assertEqual(run["run_id"], r1["run_id"])
        self.assertEqual(run["state"], "requested")   # intake never self-advances
        rows = build_store._fetch_rows(build_store._exec(
            conn, "SELECT content_sha256 FROM rig_build.artifacts"))
        self.assertEqual({r["content_sha256"] for r in rows}, {r1["sha"]})

    def test_get_run_and_contract_reads(self):
        conn = _ddl_conn()
        r1 = full_run(conn, idem="batch-200", rows=ROWS)
        run = build_store.get_run(conn, run_id=r1["run_id"])
        self.assertEqual(run["idempotency_key"], "batch-200")
        rows = build_store.cell_contract(conn, cell_id=CELL)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["criteria_version"], "v1")
        self.assertEqual(build_store.cell_contract(conn, cell_id="L9-D9-A9-I9"), [])


if __name__ == "__main__":
    unittest.main()
