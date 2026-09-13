"""rig_build live-Postgres proofs (B42/B43/B47/B48).

Companion to tests/test_build_store.py, which proves the PORTABLE laws on an
in-memory sqlite harness and names what it CANNOT prove
(BLOCKED_NEEDS_LIVE_PROOF: triggers, role grants, RLS, the migrate path,
psycopg2). This module runs against a THROWAWAY Postgres cluster created in a
temp directory with `initdb`, listening only on a free loopback port that this
process owns and removes — never a shared/live database (that is B11/B12 and
needs the typed Gate-D approval). If the substrate (initdb/pg_ctl or
psycopg2) is absent, every test SKIPS with the named reason and the receipts
record UNAVAILABLE; an honest skip beats a fabricated pass.

Proofs:
  B42  scripts/ddl_rig_build.sql applied twice through build_migrate.apply
       is idempotent and lossless (rows survive the re-apply); verify()
       re-reads the live catalog. Receipt carries ddl_sha256.
  B43  migrations 0001+0002 applied via measure_store.apply_migrations;
       three login roles, each a member of exactly one of
       rig_build_read / rig_build_worker / rig_build_verifier, get real
       database-level refusals for what the role does not allow, and the
       superuser/service_role bypass is DETECTED and reported, never
       silently used to launder a denial into a no-op.
  B47  an outbox claim lease and a run fencing token survive a killed
       connection: the zombie worker's stale-fence commit is refused while
       a fresh claim from another session succeeds; the DB trigger also
       refuses any fencing-token decrease.
  B48  outbox delivery is idempotent (replayed intake packet ->
       already_routed, exactly one row) and an ambiguous ack settles only
       through evidence-gated reconciliation — never a blind resend.

Receipts land in runs/agentic-stack-buildout/backend/proofs/ — one per
proof item, each with pg_version, ddl_sha256 and the verdict.
"""
from __future__ import annotations

import datetime as _dt
import glob as _glob
import hashlib
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

from rig_capabilities import build_intake, build_migrate, build_store, \
    measure_store

REPO = Path(__file__).resolve().parent.parent
PROOF_DIR = REPO / "runs" / "agentic-stack-buildout" / "backend" / "proofs"

STORE_DB = "rb_store"     # scripts/ddl_rig_build.sql world (build_store)
MEASURE_DB = "rb_measure"  # migrations 0001+0002 world (measure_store)

CELL = "L1-D1-A1-I1"
PACK_SHA = "f4" * 32
SHA_A = "a" * 64

try:
    import psycopg2
    import psycopg2.errors
    HAVE_PSYCOPG2 = True
    PSYCOPG2_ERROR = ""
except ImportError as exc:  # honest substrate check — skip, never fake
    HAVE_PSYCOPG2 = False
    PSYCOPG2_ERROR = str(exc)

STATE: dict = {"status": "unavailable", "reason": "", "tmp": None,
               "port": None, "pg_version": None, "env_saved": {}}
RECEIPTS: dict = {}

LOGIN_ROLES = {"rig_build_read": "proof_read_login",
               "rig_build_worker": "proof_worker_login",
               "rig_build_verifier": "proof_verifier_login"}


def _find_pg_bin(name: str) -> str | None:
    path = shutil.which(name)
    if path:
        return path
    for cand in (_glob.glob("/opt/homebrew/opt/postgresql*/bin/" + name)
                 + _glob.glob(str(Path.home() / ".homebrew/opt/postgresql*/bin/" + name))
                 + _glob.glob(str(Path.home() / ".homebrew/bin/" + name))):
        if os.access(cand, os.X_OK):
            return cand
    return None


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _ddl_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _apply_token() -> str:
    return build_migrate.CONFIRM_TOKEN + _ddl_sha(build_store.DDL_PATH)[:12]


def _dsn(db: str, user: str = "postgres") -> str:
    return f"host=127.0.0.1 port={STATE['port']} user={user} dbname={db}"


def _conn(db: str, user: str = "postgres"):
    return psycopg2.connect(_dsn(db, user), connect_timeout=10)


def _bypassed(conn) -> bool:
    """True when this session's principal would silently see every denial
    as a no-op (superuser or rolbypassrls — the service_role laundering
    path named in 0002_rig_build_roles.sql)."""
    with conn.cursor() as cur:
        cur.execute("SELECT rolsuper OR rolbypassrls FROM pg_roles "
                    "WHERE rolname = current_user")
        return bool(cur.fetchone()[0])


def setUpModule():
    if not HAVE_PSYCOPG2:
        STATE["reason"] = (f"UNAVAILABLE: psycopg2 import failed: "
                           f"{PSYCOPG2_ERROR}")
        raise unittest.SkipTest(STATE["reason"])
    missing = [n for n in ("initdb", "pg_ctl") if not _find_pg_bin(n)]
    if missing:
        STATE["reason"] = ("UNAVAILABLE: no Postgres server binary on this "
                           "host (" + ", ".join(missing) + ") and docker use "
                           "was declined for a shared daemon; refusing to "
                           "touch any non-throwaway target")
        raise unittest.SkipTest(STATE["reason"])

    tmp = Path(tempfile.mkdtemp(prefix="rig_build_proof_pg_"))
    data = tmp / "data"
    port = _free_port()
    STATE.update(tmp=tmp, port=port)
    try:
        subprocess.run([_find_pg_bin("initdb"), "-D", str(data),
                        "-U", "postgres", "-A", "trust", "--no-sync"],
                       check=True, capture_output=True, text=True, timeout=180)
        subprocess.run([_find_pg_bin("pg_ctl"), "-D", str(data), "-w", "-t", "60",
                        "-l", str(tmp / "pg.log"), "start", "-o",
                        f"-p {port} -k {tmp} -h 127.0.0.1"],
                       check=True, capture_output=True, text=True, timeout=120)
    except Exception as exc:
        log = ""
        try:
            log = (tmp / "pg.log").read_text()[-2000:]
        except OSError:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
        STATE.update(status="unavailable", tmp=None,
                     reason=f"UNAVAILABLE: throwaway cluster failed to "
                            f"start: {exc} :: {log}")
        raise unittest.SkipTest(STATE["reason"])

    # point the house env at THIS cluster only — any accidental fallback
    # hits the throwaway, never rig-dev-db.
    for var in ("RIG_CAP_DSN", "RIG_BUILD_DATABASE_URL"):
        STATE["env_saved"][var] = os.environ.get(var)
        os.environ[var] = _dsn("postgres")

    boot = _conn("postgres")
    boot.autocommit = True
    with boot.cursor() as cur:
        cur.execute("SHOW server_version")
        STATE["pg_version"] = cur.fetchone()[0]
        for db in (STORE_DB, MEASURE_DB):
            cur.execute(f"CREATE DATABASE {db}")
    # the measure world: the real migration path for 0001 + 0002
    mconn = _conn(MEASURE_DB)
    measure_store.apply_migrations(mconn)
    with mconn, mconn.cursor() as cur:
        for grp, login in LOGIN_ROLES.items():
            cur.execute(f"CREATE ROLE {login} LOGIN")
            cur.execute(f"GRANT {grp} TO {login}")
    mconn.close()
    boot.close()
    STATE["status"] = "live"


def tearDownModule():
    facts = {"pg_version": STATE.get("pg_version"),
             "ddl_sha256": _ddl_sha(build_store.DDL_PATH),
             "cluster": {"tmp_root": str(STATE.get("tmp")),
                         "port": STATE.get("port"),
                         "databases": [STORE_DB, MEASURE_DB]}}
    teardown = {"cluster_stopped": False, "port_closed": False}
    if STATE["status"] == "live":
        tmp, port = STATE["tmp"], STATE["port"]
        subprocess.run([_find_pg_bin("pg_ctl"), "-D", str(tmp / "data"),
                        "-m", "fast", "-w", "-t", "60", "stop"],
                       check=False, capture_output=True, text=True)
        teardown["cluster_stopped"] = True
        for _ in range(50):
            with socket.socket() as s:
                s.settimeout(0.5)
                if s.connect_ex(("127.0.0.1", port)) != 0:
                    teardown["port_closed"] = True
                    break
            time.sleep(0.2)
        shutil.rmtree(tmp, ignore_errors=True)
        teardown["tmp_removed"] = not tmp.exists()
    for var, old in STATE["env_saved"].items():
        if old is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = old

    PROOF_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    items = {"b42_repeatability": "B42", "b43_role_isolation": "B43",
             "b47_claim_fencing": "B47", "b48_outbox_reconciliation": "B48"}
    for key, item in items.items():
        doc = RECEIPTS.get(key) or {
            "verdict": "UNVERIFIED",
            "reason": STATE.get("reason") or "test did not complete"}
        doc = {"proof": key, "spec_item": item, "executed_at": stamp,
               **facts, **doc}
        (PROOF_DIR / f"{key}.json").write_text(
            json.dumps(doc, indent=2, sort_keys=True) + "\n")
    (PROOF_DIR / "cluster_lifecycle.json").write_text(
        json.dumps({"executed_at": stamp, **facts, "teardown": teardown,
                    "rule": "throwaway temp cluster only; never a shared "
                            "or live database"}, indent=2, sort_keys=True)
        + "\n")


class RigBuildLivePostgresProofs(unittest.TestCase):
    def setUp(self):
        if STATE["status"] != "live":
            self.skipTest(STATE["reason"])

    # -- helpers ----------------------------------------------------------

    def _seed_frozen(self, conn):
        build_store.put_cell_contract(
            conn, cell_id=CELL, criteria_version="v1",
            contract={"done_test": ["pytest"], "buyer_metric": "activation"},
            criteria_pack_sha256=PACK_SHA, sealed_by="ProofSeal")
        build_store.register_process_version(
            conn, process_key="intake", version="1",
            definition={"cadence": "on_demand"},
            declared_owner="python-intake", registered_by="ProofSeal")

    def _ensure_store_ddl(self):
        try:
            if build_migrate.verify(_dsn(STORE_DB)).get("verdict") == "PASS":
                return
        except psycopg2.Error:
            pass  # schema not present yet
        doc = build_migrate.apply(_dsn(STORE_DB), _apply_token())
        self.assertEqual(doc["status"], "applied", doc.get("error"))

    def _count(self, conn, sql, params=None):
        with conn.cursor() as cur:
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            n = cur.fetchone()[0]
        conn.commit()  # release locks: an idle-in-transaction read would
        # starve the re-apply's ACCESS EXCLUSIVE ALTER TABLE (B42 proved
        # this the hard way)
        return n

    def _expect_denied(self, conn, sql, params=None,
                       needle="permission denied"):
        try:
            with conn.cursor() as cur:
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
        except psycopg2.errors.InsufficientPrivilege as exc:
            conn.rollback()
            self.assertIn(needle, str(exc).lower(), str(exc))
            return str(exc).strip()
        except psycopg2.Error as exc:
            conn.rollback()
            self.fail(f"expected a permission-denied refusal, got "
                      f"{type(exc).__name__}: {exc}")
        self.fail("expected a permission-denied refusal; statement succeeded")

    # -- B42: repeatable migration ----------------------------------------

    def test_b42_apply_twice_is_idempotent_and_lossless(self):
        sha = _ddl_sha(build_store.DDL_PATH)
        token = build_migrate.CONFIRM_TOKEN + sha[:12]
        refused = build_migrate.apply(_dsn(STORE_DB), "wrong-token")
        self.assertEqual(refused["status"], "refused")
        self.assertFalse(refused["applied"])

        first = build_migrate.apply(_dsn(STORE_DB), token)
        self.assertEqual(first["status"], "applied", first.get("error"))
        self.assertEqual(first["ddl_sha256"], sha)
        self.assertEqual(first["identity_probe"],
                         {"current_database": STORE_DB, "current_user":
                          "postgres"},
                         "apply must probe the throwaway target first")

        conn = build_store.connect(_dsn(STORE_DB))
        try:
            self._seed_frozen(conn)
            build_store.outbox_add(conn, topic="proof.b42", payload={"n": 42},
                                   outbox_id="b42-marker")
            before = self._count(conn, "SELECT count(*) FROM rig_build.outbox")

            second = build_migrate.apply(_dsn(STORE_DB), token)
            self.assertEqual(second["status"], "applied",
                             f"re-apply must be idempotent: {second}")
            self.assertEqual(self._count(conn, "SELECT count(*) FROM "
                                              "rig_build.outbox"), before,
                             "re-apply destroyed rows")
            with conn.cursor() as cur:
                cur.execute("SELECT topic, state, payload FROM rig_build"
                            ".outbox WHERE outbox_id='b42-marker'")
                row = cur.fetchone()
            self.assertEqual(row[0], "proof.b42")
            self.assertEqual(row[2], {"n": 42})
        finally:
            conn.close()

        verdict = build_migrate.verify(_dsn(STORE_DB))
        self.assertEqual(verdict["verdict"], "PASS", verdict)
        RECEIPTS["b42_repeatability"] = {
            "verdict": "PROVEN",
            "details": {"apply_twice_idempotent": True,
                        "data_survived_reapply": True,
                        "wrong_token_refused": True,
                        "identity_probe": first["identity_probe"],
                        "verify": {k: verdict[k] for k in
                                   ("verdict", "constraint_count",
                                    "policies", "roles")}}}

    # -- B43: role isolation ----------------------------------------------

    def test_b43_role_isolation_with_bypass_detection(self):
        drv = _conn(MEASURE_DB)
        # positive control: the detector exists and is not vacuous — it
        # FLAGS the superuser, so denials can never be laundered silently.
        self.assertTrue(_bypassed(drv),
                        "bypass detector failed to flag the superuser")
        conns = {}
        for login in LOGIN_ROLES.values():
            c = _conn(MEASURE_DB, login)
            self.assertFalse(_bypassed(c),
                             f"{login} must not bypass privileges; proofs "
                             "run through it would be theater")
            conns[login] = c
        read, worker, verifier = (conns[LOGIN_ROLES[g]] for g in
                                  ("rig_build_read", "rig_build_worker",
                                   "rig_build_verifier"))
        try:
            # read: full visibility, no writes anywhere
            self._count(read, "SELECT count(*) FROM rig_build.trial")
            matrix = {"read_select_trial": "ok"}
            matrix["read_insert_trace"] = self._expect_denied(
                read, "INSERT INTO rig_build.trace (cell, trial_id, seq) "
                      "VALUES ('x','y',1)")
            matrix["read_exec_record_trial"] = self._expect_denied(
                read, "SELECT rig_build.record_trial('x','y',1,'f','m','n',"
                      "'%s','pass',NULL,'{}'::jsonb,false,now(),now())"
                      % SHA_A)

            # worker: records attempts and events; no verdict surface,
            # no direct edits, no qualification.
            now = _dt.datetime.now(_dt.timezone.utc)
            row = measure_store.record_trial(
                worker, cell="proof:b43", trial_id="t1", attempt_seq=1,
                family="claude", model="m", node="n", task_sha=SHA_A,
                outcome="pass", durable=False, started_at=now, finished_at=now)
            self.assertEqual(row["outcome"], "pass")
            self.assertEqual(row["recorded_by"], "proof_worker_login",
                             "SECURITY INVOKER must keep the real identity")
            matrix["worker_record_trial"] = "ok (recorded_by honest)"
            measure_store.append_event(worker, cell="proof:b43",
                                       trial_id="t1", event="proof")
            matrix["worker_insert_trace"] = "ok"
            # the trial INSERT grant opens only the NAMED function: a direct
            # INSERT is still refused by the trigger, for the granted role too
            try:
                with self.assertRaises(psycopg2.errors.RaiseException) as ctx:
                    worker.cursor().execute(
                        "INSERT INTO rig_build.trial (cell, trial_id, "
                        "attempt_seq, family, model, node, task_sha, outcome,"
                        " started_at, finished_at) VALUES ('x','y',1,'f','m',"
                        "'n','%s','pass',now(),now())" % SHA_A)
                matrix["worker_direct_insert_trial"] = str(ctx.exception)
                worker.rollback()
            except AssertionError:
                self.fail("worker direct INSERT into trial succeeded — the "
                          "named-function trigger law was opened by the grant")
            self.assertEqual(self._count(read, "SELECT count(*) FROM "
                                               "rig_build.trial"), 1,
                             "read must see the worker's row")
            matrix["worker_insert_verdict"] = self._expect_denied(
                worker, "INSERT INTO rig_build.verdict (cell, family, "
                        "verdict, candidate_commit, candidate_tree, "
                        "verdict_at) VALUES ('c','f','FAILED','" + "a" * 40 +
                        "','" + "b" * 40 + "',now())")
            matrix["worker_direct_update_outbox"] = self._expect_denied(
                worker, "UPDATE rig_build.outbox SET state='sent' "
                        "WHERE topic='proof.b43'")
            matrix["worker_delete_trace"] = self._expect_denied(
                worker, "DELETE FROM rig_build.trace WHERE cell='proof:b43'")
            matrix["worker_exec_record_qualification"] = self._expect_denied(
                worker, "SELECT rig_build.record_qualification('proof:b43',1)")

            # worker's granted verbs still work, and the state machine
            # binds even a permitted caller.
            with drv, drv.cursor() as cur:
                cur.execute("INSERT INTO rig_build.outbox (topic, payload) "
                            "VALUES ('proof.b43','{}'::jsonb) "
                            "RETURNING outbox_id")
                oid = cur.fetchone()[0]
            row = measure_store.outbox_set_state(
                worker, outbox_id=oid, next_state="unknown",
                note="ambiguous ack (proof)")
            self.assertEqual(row["state"], "unknown")
            try:
                with self.assertRaises(psycopg2.errors.RaiseException) as ctx:
                    measure_store.outbox_set_state(
                        worker, outbox_id=oid, next_state="sent")
                matrix["worker_illegal_transition"] = str(ctx.exception)
                drv.commit()
            finally:
                worker.rollback()

            # verifier: the only family with verdict writes AND the
            # qualification EXECUTE — which still cannot mint without
            # the quorum the function itself re-checks.
            vrow = measure_store.record_verdict(
                verifier, cell="proof:b43", family="claude",
                verdict="PERFECT", candidate_commit="a" * 40,
                candidate_tree="b" * 40,
                verdict_at=_dt.datetime.now(_dt.timezone.utc))
            matrix["verifier_insert_verdict"] = "ok"
            matrix["verifier_insert_trace"] = self._expect_denied(
                verifier, "INSERT INTO rig_build.trace (cell, trial_id, seq)"
                          " VALUES ('x','y',9)")
            matrix["verifier_exec_record_trial"] = self._expect_denied(
                verifier, "SELECT rig_build.record_trial('x','y',7,'f','m',"
                          "'n','%s','pass',NULL,'{}'::jsonb,false,now(),now()"
                          ")" % SHA_A)
            with self.assertRaises(psycopg2.errors.RaiseException) as ctx:
                measure_store.record_qualification(
                    verifier, cell="proof:b43",
                    verdict_id=vrow["verdict_id"])
            msg = str(ctx.exception)
            verifier.rollback()
            self.assertIn("quorum", msg, msg)
            matrix["verifier_qualification_reaches_guard"] = (
                msg + " — EXECUTE granted, mint still refused by the "
                      "1-attempt < 72 quorum the function enforces")
        finally:
            for c in list(conns.values()) + [drv]:
                c.close()
        RECEIPTS["b43_role_isolation"] = {
            "verdict": "PROVEN",
            "ddl_sha256_0001": _ddl_sha(
                measure_store.MIGRATIONS_DIR / "0001_rig_build.sql"),
            "ddl_sha256_0002": _ddl_sha(
                measure_store.MIGRATIONS_DIR / "0002_rig_build_roles.sql"),
            "details": {"bypass_detector_flags_superuser": True,
                        "all_three_logins_non_superuser": True,
                        "matrix": matrix}}

    # -- B47: fencing after a crash ---------------------------------------

    def test_b47_stale_claim_after_killed_connection_is_refused(self):
        self._ensure_store_ddl()
        conn = build_store.connect(_dsn(STORE_DB))
        self._seed_frozen(conn)
        build_store.outbox_add(conn, topic="proof.b47", payload={"item": 1},
                               outbox_id="b47-lease")

        conn_a = build_store.connect(_dsn(STORE_DB))
        claim_a = build_store.claim_outbox(conn_a, outbox_id="b47-lease",
                                           claim_owner="worker-A",
                                           lease_seconds=1)
        self.assertEqual(claim_a["status"], "claimed")
        self.assertEqual(claim_a["row"]["claim_fence"], 1)
        # a live lease is honoured — no double delivery while A holds it
        self.assertEqual(build_store.claim_outbox(
            conn, outbox_id="b47-lease", claim_owner="thief")["status"],
            "not_claimable")

        # crash: kill A's backend mid-flight, never released
        with conn.cursor() as cur:
            cur.execute("SELECT pg_terminate_backend(%s)",
                        (conn_a.get_backend_pid(),))
            self.assertTrue(cur.fetchone()[0])
        conn.commit()
        try:
            conn_a.close()
        except Exception:
            pass
        time.sleep(2.5)  # past the 1s lease

        conn_b = build_store.connect(_dsn(STORE_DB))
        claim_b = build_store.claim_outbox(conn_b, outbox_id="b47-lease",
                                           claim_owner="worker-B",
                                           lease_seconds=120)
        self.assertEqual(claim_b["status"], "claimed",
                         "fresh claim must succeed after lease expiry")
        self.assertEqual(claim_b["row"]["claim_fence"], 2)

        zombie = build_store.connect(_dsn(STORE_DB))
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.settle_outbox(zombie, outbox_id="b47-lease",
                                      claim_owner="worker-A", claim_fence=1,
                                      state="sent", receipt="ghost-ack")
        self.assertIn("stale", str(ctx.exception))
        self.assertEqual(self._count(
            conn, "SELECT count(*) FROM rig_build.outbox WHERE "
                  "outbox_id='b47-lease' AND state='claimed' AND "
                  "claim_fence=2"), 1, "stale commit must not move the row")
        done = build_store.settle_outbox(conn_b, outbox_id="b47-lease",
                                         claim_owner="worker-B",
                                         claim_fence=2, state="sent",
                                         receipt="msg-b47")
        self.assertEqual(done["status"], "settled")
        zombie.close()

        # run-side fencing: takeover raises the token, stale writers are
        # refused, and the DB trigger forbids any decrease for every role.
        run = build_store.start_run(conn, cell_id=CELL, criteria_version="v1",
                                    process_key="intake", process_version="1",
                                    idempotency_key="proof:b47:run",
                                    started_by="proof")
        run_id = run["row"]["run_id"]
        build_store.append_event(conn, run_id=run_id, sequence=1,
                                 kind="transition", fencing_token=1)
        with conn.cursor() as cur:
            cur.execute("UPDATE rig_build.runs SET fencing_token = "
                        "fencing_token + 1 WHERE run_id=%s", (run_id,))
        conn.commit()
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.append_event(conn, run_id=run_id, sequence=2,
                                     kind="transition", fencing_token=1)
        self.assertIn("stale", str(ctx.exception))
        build_store.append_event(conn, run_id=run_id, sequence=2,
                                 kind="transition", fencing_token=2)
        with self.assertRaises(psycopg2.errors.RaiseException) as ctx:
            with conn.cursor() as cur:
                cur.execute("UPDATE rig_build.runs SET fencing_token = 1 "
                            "WHERE run_id=%s", (run_id,))
        conn.rollback()
        self.assertIn("may not decrease", str(ctx.exception))
        conn.close(); conn_b.close()
        RECEIPTS["b47_claim_fencing"] = {
            "verdict": "PROVEN",
            "details": {
                "live_lease_respects_first_claim": True,
                "crash_via_pg_terminate_backend": True,
                "stale_fence_settle_refused": True,
                "fresh_claim_after_expiry_succeeds": "fence 1 -> 2",
                "run_takeover_stale_writer_refused": True,
                "fencing_decrease_refused_by_trigger": True}}

    # -- B48: outbox reconciliation ----------------------------------------

    def test_b48_duplicate_packet_delivery_is_idempotent(self):
        self._ensure_store_ddl()
        conn = build_store.connect(_dsn(STORE_DB))
        self._seed_frozen(conn)
        content = "b48 fetched bytes " + "z" * 32
        packet = {
            "cell_id": CELL, "criteria_version": "v1",
            "process_key": "intake", "process_version": "1",
            "route": "document",
            "source": {"url": "https://proof.test/b48/doc",
                       "provider": "proof", "kind": "document",
                       "content": content,
                       "content_sha256": hashlib.sha256(
                           content.encode()).hexdigest()}}
        first = build_intake.ingest(conn, packet)
        self.assertEqual(first["effect"], "routed")
        second = build_intake.ingest(conn, packet)
        self.assertEqual(second["effect"], "already_routed",
                         "replay must not route a second command")
        self.assertEqual(second["run_id"], first["run_id"])
        self.assertEqual(second["status"], "replayed")
        oid = "cmd-" + first["dedupe_key"][:16]
        self.assertEqual(self._count(
            conn, "SELECT count(*) FROM rig_build.outbox WHERE outbox_id=%s",
            (oid,)), 1, "duplicate routing effect")
        self.assertEqual(self._count(
            conn, "SELECT count(*) FROM rig_build.runs WHERE "
                  "idempotency_key=%s", ("intake:" + first["dedupe_key"],)), 1)
        self.assertEqual(self._count(
            conn, "SELECT count(*) FROM rig_build.source_documents WHERE "
                  "dedupe_key=%s", (first["dedupe_key"],)), 1)
        # delivery level: a settled/claimed row cannot be double-claimed
        self.assertEqual(build_store.claim_outbox(
            conn, outbox_id=oid, claim_owner="w1")["status"], "claimed")
        self.assertEqual(build_store.claim_outbox(
            conn, outbox_id=oid, claim_owner="w2")["status"], "not_claimable")
        conn.close()
        RECEIPTS.setdefault("b48_outbox_reconciliation", {"verdict": "PROVEN",
                                                          "details": {}})
        RECEIPTS["b48_outbox_reconciliation"]["details"][
            "duplicate_packet"] = {
                "first_effect": "routed", "second_effect": "already_routed",
                "outbox_rows": 1, "run_rows": 1, "document_rows": 1,
                "double_claim": "not_claimable"}

    def test_b48_ambiguous_ack_reconciles_with_evidence_only(self):
        self._ensure_store_ddl()
        conn = build_store.connect(_dsn(STORE_DB))
        build_store.outbox_add(conn, topic="proof.b48", payload={"n": 1},
                               outbox_id="b48-ambiguous")
        claim = build_store.claim_outbox(conn, outbox_id="b48-ambiguous",
                                         claim_owner="w1", lease_seconds=30)
        fence = claim["row"]["claim_fence"]
        # provider accepted (effect happened), ack lost in transit
        build_store.settle_outbox(conn, outbox_id="b48-ambiguous",
                                  claim_owner="w1", claim_fence=fence,
                                  state="unknown",
                                  error="connection dropped after the "
                                        "effect, before the ack")
        # unknown is never re-claimable (blind resend is structurally out)
        self.assertEqual(build_store.claim_outbox(
            conn, outbox_id="b48-ambiguous", claim_owner="w1",
            now="2099-01-01T00:00:00+00:00")["status"], "not_claimable")
        # a blind pending settlement is refused before touching the row
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.settle_outbox(conn, outbox_id="b48-ambiguous",
                                      claim_owner="w1", claim_fence=fence,
                                      state="pending")
        self.assertIn("never 'pending'", str(ctx.exception))
        # reconciliation without named evidence is refused
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.reconcile_unknown(conn, outbox_id="b48-ambiguous",
                                          resolution="sent",
                                          expected_fence=fence,
                                          evidence="  ")
        self.assertIn("evidence", str(ctx.exception))
        # wrong fence is refused — never a blind transition
        with self.assertRaises(build_store.StoreError) as ctx:
            build_store.reconcile_unknown(conn, outbox_id="b48-ambiguous",
                                          resolution="sent",
                                          expected_fence=fence + 99,
                                          evidence="read-back pm-42")
        done = build_store.reconcile_unknown(
            conn, outbox_id="b48-ambiguous", resolution="sent",
            expected_fence=fence,
            evidence="provider read-back: message id pm-42 already stored")
        self.assertEqual(done["status"], "reconciled")
        self.assertEqual(done["row"]["state"], "sent")
        self.assertEqual(self._count(
            conn, "SELECT attempt_count FROM rig_build.outbox WHERE "
                  "outbox_id='b48-ambiguous'"), 1,
            "reconciliation must never re-deliver")
        # a second delivery attempt on a settled row is refused outright
        self.assertEqual(build_store.claim_outbox(
            conn, outbox_id="b48-ambiguous", claim_owner="w1",
            now="2099-01-01T00:00:00+00:00")["status"], "not_claimable")
        conn.close()
        RECEIPTS.setdefault("b48_outbox_reconciliation", {"verdict": "PROVEN",
                                                          "details": {}})
        RECEIPTS["b48_outbox_reconciliation"]["details"]["ambiguous_ack"] = {
            "settled_to_unknown": True,
            "unknown_never_reclaimable": True,
            "blind_pending_refused": True,
            "reconcile_without_evidence_refused": True,
            "reconcile_wrong_fence_refused": True,
            "evidence_gated_reconcile": "sent",
            "attempt_count_after_reconcile": 1}

if __name__ == "__main__":
    unittest.main()
