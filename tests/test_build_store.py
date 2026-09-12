"""rig_build store tests — NO live database, no mocks pretending to be one.

Harness: the APPLY-PORTABLE section of scripts/ddl_rig_build.sql, run through
the documented mechanical adaptation (CREATE SCHEMA dropped, rig_build. prefix
stripped) into an in-memory sqlite3 database. That proves the PORTABLE laws:
primary keys, unique constraints (idempotency key, append sequence), foreign
keys, CHECK constraints, and every store-layer guard (fencing, hash
verification, mint refusal, lease expiry, evidence-gated reconciliation).

What sqlite CANNOT prove is listed in BLOCKED_NEEDS_LIVE_PROOF and printed —
the Postgres-only database law (plpgsql append/immutability/fencing triggers,
role grants, RLS) is NOT claimed green here. Running the suite prints the
list; a clean run means the portable surface plus the store guards hold, not
that the schema is applied anywhere.
"""
import json
import sqlite3
import unittest

from rig_capabilities import build_store

CELL = "L1-D1-A1-I1"
PACK_SHA = "f4" * 32
SHA_A = "a" * 64
SHA_B = "b" * 64
T0 = "2026-09-12T00:00:00+00:00"

BLOCKED_NEEDS_LIVE_PROOF = [
    "run_events UPDATE/DELETE refusal by plpgsql trigger for EVERY role "
    "(sqlite harness has no triggers; only the store guard + PK are proven)",
    "run_events sequence-continuity trigger under concurrent cross-connection "
    "inserts (store guard proven single-connection only)",
    "cell_contracts / process_versions / approval_refs immutability triggers",
    "runs fencing_token monotonicity trigger",
    "least-privilege grants: rig_build_data_plane has no UPDATE/DELETE on "
    "append-only/frozen tables and no DELETE anywhere (B20/B43)",
    "RLS policies and the no-anonymous-exposure guarantee (needs live PG)",
    "build_migrate apply/verify against a real target incl. the identity "
    "probe (blocked on B11/B12: scoped credential + approval)",
    "psycopg2 code path of build_store.connect (driver present; no target "
    "reachable without the approved credential)",
]


def _harness():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(build_store.portable_ddl_sqlite())
    return conn


def _seed(conn):
    build_store.put_cell_contract(
        conn, cell_id=CELL, criteria_version="v1",
        contract={"done_test": ["pytest"], "buyer_metric": "activation"},
        criteria_pack_sha256=PACK_SHA, sealed_by="TestSeal")
    build_store.register_process_version(
        conn, process_key="intake", version="1", definition={"cadence": "on_demand"},
        declared_owner="python-intake", registered_by="TestSeal")


class RigBuildStoreTests(unittest.TestCase):
    def setUp(self):
        self.conn = _harness()
        _seed(self.conn)

    def tearDown(self):
        self.conn.close()

    # -- DDL shape (B06 freeze) ------------------------------------------------

    def test_ddl_covers_nine_entities_with_keys(self):
        sec = build_store.ddl_sections()["APPLY-PORTABLE"]
        for entity in ("cell_contracts", "process_versions", "cell_bindings",
                       "runs", "run_events", "artifacts", "approval_refs",
                       "source_documents", "outbox"):
            self.assertIn(f"CREATE TABLE IF NOT EXISTS rig_build.{entity}",
                          sec, entity)
            self.assertIn(f"PRIMARY KEY", sec.split(
                f"rig_build.{entity} (")[1].split(");")[0], entity)
        self.assertIn("idempotency_key     text        NOT NULL UNIQUE", sec)
        self.assertIn("PRIMARY KEY (run_id, sequence)", sec)
        self.assertIn("FOREIGN KEY", sec)
        rollback = build_store.ddl_sections()["ROLLBACK"]
        self.assertIn("DROP TABLE IF EXISTS rig_build.outbox", rollback)
        self.assertIn("rig_build", rollback)
        header = build_store.DDL_PATH.read_text()
        self.assertIn("NEVER", header)  # catalog-sync truncation law is stated

    def test_sqlite_harness_never_carries_pg_only_law(self):
        adapted = build_store.portable_ddl_sqlite()
        statements = "\n".join(ln for ln in adapted.splitlines()
                               if not ln.strip().startswith("--"))
        self.assertIn("PRIMARY KEY", statements.upper())
        for marker in ("TRIGGER", "GRANT", "ROLE", "ROW LEVEL SECURITY"):
            self.assertNotIn(marker, statements.upper(), marker)

    # -- frozen records (B14) ---------------------------------------------------

    def test_contract_replay_is_a_noop_and_rewrite_is_refused(self):
        again = build_store.put_cell_contract(
            self.conn, cell_id=CELL, criteria_version="v1",
            contract={"done_test": ["pytest"], "buyer_metric": "activation"},
            criteria_pack_sha256=PACK_SHA, sealed_by="TestSeal")
        self.assertEqual(again["status"], "replay_confirmed")
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.put_cell_contract(
                self.conn, cell_id=CELL, criteria_version="v1",
                contract={"done_test": ["rm -rf"]},
                criteria_pack_sha256=PACK_SHA, sealed_by="Attacker")
        self.assertIn("frozen contract differs", str(ctx.exception))
        n = self.conn.execute(
            "SELECT count(*) FROM cell_contracts").fetchone()[0]
        self.assertEqual(n, 1)

    def test_contract_outside_authority_refused(self):
        with self.assertRaises(build_store.StoreError):
            build_store.put_cell_contract(
                self.conn, cell_id="L9-9-Z9-X9", criteria_version="v1",
                contract={}, criteria_pack_sha256=PACK_SHA, sealed_by="x")

    def test_process_version_rewrite_refused(self):
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.register_process_version(
                self.conn, process_key="intake", version="1",
                definition={"cadence": "every_minute"},
                declared_owner="python-intake", registered_by="Attacker")
        self.assertIn("frozen", str(ctx.exception))

    def test_binding_requires_sealed_records_and_T_types(self):
        with self.assertRaises(build_store.StoreError):
            build_store.bind_cell(
                self.conn, cell_id=CELL, criteria_version="v9",
                process_key="intake", process_version="1", work_type="T1",
                owner="python-intake", bound_by="x")
        with self.assertRaises(build_store.StoreError):
            build_store.bind_cell(
                self.conn, cell_id=CELL, criteria_version="v1",
                process_key="intake", process_version="1", work_type="T9",
                owner="python-intake", bound_by="x")
        out = build_store.bind_cell(
            self.conn, cell_id=CELL, criteria_version="v1",
            process_key="intake", process_version="1", work_type="T1",
            owner="python-intake", bound_by="TestSeal")
        self.assertEqual(out["status"], "bound")

    # -- runs (B15) --------------------------------------------------------------

    def _run(self, key="op-1"):
        return build_store.start_run(
            self.conn, cell_id=CELL, criteria_version="v1",
            process_key="intake", process_version="1",
            idempotency_key=key, started_by="TestSeal")

    def test_idempotency_key_replays_never_forks(self):
        first = self._run()
        self.assertEqual(first["status"], "started")
        for _ in range(3):
            replay = self._run()
            self.assertEqual(replay["status"], "replayed")
            self.assertEqual(replay["row"]["run_id"], first["row"]["run_id"])
        n = self.conn.execute("SELECT count(*) FROM runs").fetchone()[0]
        self.assertEqual(n, 1)

    # -- events: sequence + fencing -----------------------------------------------

    def _started(self):
        return self._run()["row"]["run_id"]

    def test_event_sequence_duplicate_and_gap_refused(self):
        run = self._started()
        for seq in (1, 2):
            out = build_store.append_event(
                self.conn, run_id=run, sequence=seq, kind="transition",
                fencing_token=1, payload={"i": seq})
            self.assertEqual(out["status"], "appended")
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.append_event(self.conn, run_id=run, sequence=2,
                                     kind="transition", fencing_token=1)
        self.assertIn("duplicate/out-of-order", str(ctx.exception))
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.append_event(self.conn, run_id=run, sequence=5,
                                     kind="checkpoint", fencing_token=1)
        self.assertIn("gap", str(ctx.exception))
        n = self.conn.execute(
            "SELECT count(*) FROM run_events").fetchone()[0]
        self.assertEqual(n, 2)

    def test_stale_fencing_token_cannot_commit(self):
        run = self._started()
        build_store.append_event(self.conn, run_id=run, sequence=1,
                                 kind="transition", fencing_token=1)
        # lease taken over elsewhere: run fence advances (PG guards this with
        # the monotonicity trigger; here the harness advances it directly)
        self.conn.execute("UPDATE runs SET fencing_token=2 WHERE run_id=?",
                          (run,))
        self.conn.commit()
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.append_event(self.conn, run_id=run, sequence=2,
                                     kind="checkpoint", fencing_token=1)
        self.assertIn("stale fencing token", str(ctx.exception))
        # the current holder lands the same event
        out = build_store.append_event(self.conn, run_id=run, sequence=2,
                                       kind="checkpoint", fencing_token=2)
        self.assertEqual(out["status"], "appended")

    # -- artifacts (B16) -----------------------------------------------------------

    def test_artifact_hash_mismatch_refused_nothing_stored(self):
        run = self._started()
        content = b"the bytes that exist"
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.add_artifact(
                self.conn, run_id=run, uri="local://evidence/out.txt",
                kind="receipt", recorded_by="TestSeal", content=content,
                content_sha256=SHA_A)
        self.assertIn("hash mismatch", str(ctx.exception))
        n = self.conn.execute("SELECT count(*) FROM artifacts").fetchone()[0]
        self.assertEqual(n, 0)
        out = build_store.add_artifact(
            self.conn, run_id=run, uri="local://evidence/out.txt",
            kind="receipt", recorded_by="TestSeal", content=content)
        self.assertEqual(out["content_sha256"],
                         build_store._sha256(content))
        again = build_store.add_artifact(
            self.conn, run_id=run, uri="local://evidence/out.txt",
            kind="receipt", recorded_by="TestSeal", content=content)
        self.assertEqual(again["status"], "replay_confirmed")

    def test_artifact_requires_a_real_run(self):
        with self.assertRaises(build_store.StoreError):
            build_store.add_artifact(
                self.conn, run_id="nope", uri="local://x", kind="receipt",
                recorded_by="TestSeal", content=b"x")

    # -- approval references (B17) ----------------------------------------------------

    def test_no_minting_verb_exists_at_all(self):
        for name in ("set_qualified", "approve_omission", "mark_pass",
                     "approve", "qualify", "set_approved"):
            self.assertFalse(hasattr(build_store, name), name)

    def test_approval_ref_is_reference_only(self):
        approvals = [r for r in self.conn.execute(
            "PRAGMA table_info(approval_refs)").fetchall()]
        cols = {r[1] for r in approvals}
        self.assertTrue(cols.isdisjoint(
            {"status", "verdict", "approved", "qualified", "state"}), cols)
        out = build_store.add_approval_ref(
            self.conn, authority_ledger="gate-d", external_ref="req-7712",
            subject_kind="cell_omission", subject_id=CELL,
            requested_by="TestSeal", recorded_by="TestSeal")
        self.assertEqual(out["status"], "referenced")
        self.assertIn("reference only", out["note"])

    def test_caller_submitted_pass_flag_refused(self):
        base = dict(authority_ledger="gate-d", external_ref="req-7713",
                    subject_kind="cell_omission", subject_id=CELL,
                    requested_by="TestSeal", recorded_by="TestSeal")
        for detail in ({"pass": True}, {"verdict": "PASS"},
                       {"note": {"qualified": "yes"}}, {"flag": "approved"},
                       {"chain": [{"ok": "passed"}]}):
            with self.assertRaises(build_store.StoreError, msg=str(detail)):
                build_store.add_approval_ref(self.conn, detail=detail, **base)
        n = self.conn.execute("SELECT count(*) FROM approval_refs") \
                     .fetchone()[0]
        self.assertEqual(n, 0)

    def test_self_authority_and_caller_refused(self):
        with self.assertRaises(build_store.StoreError):
            build_store.add_approval_ref(
                self.conn, authority_ledger="self", external_ref="trust-me",
                subject_kind="run", subject_id="r1",
                requested_by="x", recorded_by="x")
        with self.assertRaises(build_store.StoreError):
            build_store.add_approval_ref(
                self.conn, authority_ledger="gate-d", external_ref="caller:1",
                subject_kind="run", subject_id="r1",
                requested_by="x", recorded_by="x")

    # -- source documents (B18) ---------------------------------------------------------

    def test_source_document_dedupe_and_resume(self):
        url = "https://example.test/tutorial"
        key = build_store._sha256(url.encode())
        first = build_store.put_source_document(
            self.conn, dedupe_key=key, url=url, provider="prov",
            kind="official_howto", expected_artifact="snapshot+sha256")
        self.assertEqual(first["status"], "accepted")
        again = build_store.put_source_document(
            self.conn, dedupe_key=key, url=url, provider="prov",
            kind="official_howto", retrieval_status="FETCHING")
        self.assertEqual(again["status"], "advanced")
        self.assertEqual(again["row"]["attempt_count"], 1)
        n = self.conn.execute(
            "SELECT count(*) FROM source_documents").fetchone()[0]
        self.assertEqual(n, 1)  # dedupe key: same row, never a second accept

    def test_fetched_without_hash_is_not_evidence(self):
        key = build_store._sha256(b"https://example.test/x")
        with self.assertRaises(build_store.StoreError):
            build_store.put_source_document(
                self.conn, dedupe_key=key, url="https://example.test/x",
                provider="prov", kind="official_howto",
                retrieval_status="FETCHED")

    # -- outbox (B19) ----------------------------------------------------------------------

    def _queued(self):
        return build_store.outbox_add(
            self.conn, topic="notify", payload={"n": 1})["row"]["outbox_id"]

    def test_claim_lease_expiry_and_stale_worker_fencing(self):
        oid = self._queued()
        a = build_store.claim_outbox(self.conn, outbox_id=oid,
                                     claim_owner="workerA", lease_seconds=60,
                                     now=T0)
        self.assertEqual(a["status"], "claimed")
        live = build_store.claim_outbox(self.conn, outbox_id=oid,
                                        claim_owner="workerB",
                                        lease_seconds=60,
                                        now="2026-09-12T00:00:30+00:00")
        self.assertEqual(live["status"], "not_claimable")  # lease honoured
        taken = build_store.claim_outbox(self.conn, outbox_id=oid,
                                         claim_owner="workerB",
                                         lease_seconds=60,
                                         now="2026-09-12T00:02:00+00:00")
        self.assertEqual(taken["status"], "claimed")       # lease expired
        self.assertEqual(taken["row"]["claim_fence"], 2)
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.settle_outbox(self.conn, outbox_id=oid,
                                      claim_owner="workerA", claim_fence=1,
                                      state="sent", receipt="ack-1",
                                      now="2026-09-12T00:02:01+00:00")
        self.assertIn("stale", str(ctx.exception))         # B47: crash-resume
        out = build_store.settle_outbox(self.conn, outbox_id=oid,
                                        claim_owner="workerB", claim_fence=2,
                                        state="sent", receipt="ack-1",
                                        now="2026-09-12T00:02:02+00:00")
        self.assertEqual(out["row"]["state"], "sent")

    def test_sent_requires_receipt_unknown_requires_reconciliation(self):
        oid = self._queued()
        c = build_store.claim_outbox(self.conn, outbox_id=oid,
                                     claim_owner="w", lease_seconds=60, now=T0)
        fence = c["row"]["claim_fence"]
        with self.assertRaises(build_store.StoreError):
            build_store.settle_outbox(self.conn, outbox_id=oid,
                                      claim_owner="w", claim_fence=fence,
                                      state="sent", now=T0)
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.settle_outbox(self.conn, outbox_id=oid,
                                      claim_owner="w", claim_fence=fence,
                                      state="pending", now=T0)
        self.assertIn("blind resend", str(ctx.exception))
        out = build_store.settle_outbox(
            self.conn, outbox_id=oid, claim_owner="w", claim_fence=fence,
            state="unknown", error="timeout before ack", now=T0)
        self.assertEqual(out["row"]["state"], "unknown")
        # an unknown row cannot be re-claimed (no blind resend path)
        self.assertEqual(build_store.claim_outbox(
            self.conn, outbox_id=oid, claim_owner="w2", lease_seconds=60,
            now="2026-09-12T10:00:00+00:00")["status"], "not_claimable")
        # ... and reconcile demands named evidence
        with self.assertRaises(build_store.StoreError):
            build_store.reconcile_unknown(self.conn, outbox_id=oid,
                                          resolution="pending",
                                          expected_fence=fence, evidence=" ")
        row = self.conn.execute(
            "SELECT state FROM outbox WHERE outbox_id=?", (oid,)).fetchone()
        self.assertEqual(row[0], "unknown")  # refusal left it honest
        rec = build_store.reconcile_unknown(
            self.conn, outbox_id=oid, resolution="pending",
            expected_fence=fence,
            evidence="provider GET /jobs/ack-1 => 404 not-found, resend safe",
            now="2026-09-12T10:05:00+00:00")
        self.assertEqual(rec["row"]["state"], "pending")
        # re-queue goes through a FRESH fence, the old holder is dead
        # (settle requires a live claimed row; the pending row is not
        # settle-able by the dead holder — see the refusal below)
        with self.assertRaises(build_store.StoreError):
            build_store.settle_outbox(self.conn, outbox_id=oid,
                                      claim_owner="w", claim_fence=fence,
                                      state="sent", receipt="x", now=T0)
        new = build_store.claim_outbox(self.conn, outbox_id=oid,
                                       claim_owner="w3", lease_seconds=60,
                                       now="2026-09-12T10:06:00+00:00")
        self.assertEqual(new["status"], "claimed")
        self.assertGreater(new["row"]["claim_fence"], fence)

    def test_blocked_list_is_reported_not_faked(self):
        # The suite's honesty contract: PG-only law is named, never faked.
        self.assertGreaterEqual(len(BLOCKED_NEEDS_LIVE_PROOF), 5)
        print("\nBLOCKED — needs live-target proof (not claimed by sqlite):")
        for item in BLOCKED_NEEDS_LIVE_PROOF:
            print("  *", item)


if __name__ == "__main__":
    unittest.main()
