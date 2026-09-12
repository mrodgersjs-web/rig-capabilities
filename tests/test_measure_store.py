"""Adversarial tests for the rig_build durable backend.

Real Postgres (no mocks): a scratch database is created on the local server,
both migrations applied, and every invariant attacked through role switches,
direct SQL, and the store API. Skips only when psycopg2 or the server is
genuinely absent.
"""
import datetime as dt
import os
import re
import shutil
import subprocess
import unittest
import uuid

import psycopg2
from psycopg2 import errors as pg_errors
from psycopg2 import errorcodes

from rig_capabilities import measure_store

SHA_A = "a" * 64
TREE_A = "b" * 40
COMMIT_A = "c" * 40


def _server_available():
    if shutil.which("psql") is None:
        return False
    try:
        import psycopg2  # noqa: F401
    except ImportError:
        return False
    try:
        conn = psycopg2.connect("host=/tmp port=5432 dbname=postgres user=" + os.environ["USER"],
                                connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


@unittest.skipUnless(_server_available(), "local postgres or psycopg2 unavailable")
class RigBuildStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dbname = "rig_build_test_" + uuid.uuid4().hex[:10]
        cls.maint = psycopg2.connect(
            f"host=/tmp port=5432 dbname=postgres user={os.environ['USER']}")
        cls.maint.autocommit = True
        with cls.maint.cursor() as cur:
            cur.execute(f'CREATE DATABASE "{cls.dbname}"')
        cls.conn = measure_store.connect(
            f"host=/tmp port=5432 dbname={cls.dbname} user={os.environ['USER']}")
        measure_store.apply_migrations(cls.conn)
        cls.conn.close()

    @classmethod
    def tearDownClass(cls):
        with cls.maint.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{cls.dbname}" WITH (FORCE)')
        cls.maint.close()

    def setUp(self):
        self.conn = measure_store.connect(
            f"host=/tmp port=5432 dbname={self.dbname} user={os.environ['USER']}")
        with self.conn, self.conn.cursor() as cur:
            cur.execute("TRUNCATE rig_build.qualification, rig_build.seal_link,"
                        " rig_build.quality_score, rig_build.verdict, rig_build.trace,"
                        " rig_build.trial, rig_build.outbox CASCADE")
        self.t0 = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=48)

    def tearDown(self):
        self.conn.close()

    # helpers -------------------------------------------------------------
    def seed_quorum(self, cell="C42", n=72, durable=12, verdict="VERIFIED"):
        for i in range(n):
            measure_store.record_trial(
                self.conn, cell=cell, trial_id=f"t{i:03d}", attempt_seq=1,
                family="claude", model="opus", node="main", task_sha=SHA_A,
                outcome="pass", artifact_tree=TREE_A, durable=i < durable,
                started_at=self.t0 + dt.timedelta(minutes=21 * i),
                finished_at=self.t0 + dt.timedelta(minutes=21 * i + 5))
        v = measure_store.record_verdict(
            self.conn, cell=cell, family="hermes", verdict=verdict,
            candidate_commit=COMMIT_A, candidate_tree=TREE_A, verdict_at=self.t0)
        return v["verdict_id"]

    def denial(self, sql, params=None, role="rig_build_worker", exc=None):
        """SET ROLE must survive the aborted-tx rollbacks: commit it, and
        re-assert after every denial (rollback restores last committed role)."""
        exc = exc or pg_errors.InsufficientPrivilege
        self.conn.rollback()
        with self.conn.cursor() as cur:
            cur.execute(f"SET ROLE {role}")
            cur.execute("SELECT current_user")
            self.assertEqual(cur.fetchone()[0], role)
        self.conn.commit()
        try:
            with self.assertRaises(exc) as cm:
                with self.conn.cursor() as cur:
                    cur.execute(sql, params)
            return cm.exception
        finally:
            self.conn.rollback()

    # store happy paths ----------------------------------------------------
    def test_trial_roundtrip_and_attempt_key_uniqueness(self):
        row = measure_store.record_trial(
            self.conn, cell="C01", trial_id="t1", attempt_seq=1, family="claude",
            model="sonnet", node="main", task_sha=SHA_A, outcome="pass",
            started_at=self.t0, finished_at=self.t0 + dt.timedelta(seconds=5))
        self.assertEqual(row["outcome"], "pass")
        self.assertEqual(row["recorded_by"], os.environ["USER"])
        with self.assertRaises(psycopg2.IntegrityError):
            measure_store.record_trial(
                self.conn, cell="C01", trial_id="t1", attempt_seq=1, family="claude",
                model="sonnet", node="main", task_sha=SHA_A, outcome="fail",
                started_at=self.t0, finished_at=self.t0)
        self.conn.rollback()
        # second attempt on the same trial is legal
        r2 = measure_store.record_trial(
            self.conn, cell="C01", trial_id="t1", attempt_seq=2, family="claude",
            model="sonnet", node="main", task_sha=SHA_A, outcome="fail",
            started_at=self.t0, finished_at=self.t0 + dt.timedelta(seconds=9))
        self.assertEqual(r2["attempt_seq"], 2)

    def test_event_sequence_no_gap_no_dup(self):
        e1 = measure_store.append_event(self.conn, cell="C02", trial_id="t1", event="start")
        e2 = measure_store.append_event(self.conn, cell="C02", trial_id="t1", event="end")
        self.assertEqual((e1["seq"], e2["seq"]), (1, 2))
        other = measure_store.append_event(self.conn, cell="C02", trial_id="t2", event="start")
        self.assertEqual(other["seq"], 1)

    def test_python_boundary_validation_rejects_before_sql(self):
        with self.assertRaises(measure_store.StoreError):
            measure_store.record_trial(self.conn, cell="C03", trial_id="t", attempt_seq=0,
                                     family="f", model="m", node="n", task_sha="nope",
                                     outcome="pass", started_at=self.t0, finished_at=self.t0)
        with self.assertRaises(measure_store.StoreError):
            measure_store.record_trial(self.conn, cell="C03", trial_id="t", attempt_seq=1,
                                     family="f", model="m", node="n", task_sha=SHA_A,
                                     outcome="launched", started_at=self.t0, finished_at=self.t0)
        with self.assertRaises(measure_store.StoreError):
            measure_store.record_verdict(self.conn, cell="C03", family="f", verdict="LGTM",
                                       candidate_commit=COMMIT_A, candidate_tree=TREE_A,
                                       verdict_at=self.t0)

    # role isolation -------------------------------------------------------
    def test_worker_cannot_touch_verdict_quality_or_qualification(self):
        self.seed_quorum(cell="C10")
        self.denial(
            "INSERT INTO rig_build.verdict (cell, family, verdict, candidate_commit,"
            " candidate_tree, verdict_at) VALUES ('C10','x','VERIFIED',%s,%s,now())",
            (COMMIT_A, TREE_A))
        self.denial("SELECT rig_build.record_qualification('C10', 1)")
        self.denial("UPDATE rig_build.trial SET outcome = 'pass' WHERE cell='C10'")

    def test_read_role_is_select_only(self):
        self.denial(
            "INSERT INTO rig_build.trace (cell, trial_id, seq, event) VALUES ('x','y',1,'z')",
            role="rig_build_read")
        self.conn.rollback()
        with self.conn.cursor() as cur:
            cur.execute("SET ROLE rig_build_read")
        self.conn.commit()
        with self.conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM rig_build.verdict")
            cur.fetchone()
        self.conn.rollback()

    # append-only triggers fire even for the superuser owner ---------------
    def test_append_only_tables_refuse_owner_mutation(self):
        ev = measure_store.append_event(self.conn, cell="C04", trial_id="t", event="x")
        for stmt in ("DELETE FROM rig_build.trace WHERE id = %s".replace("%s", str(ev["id"])),
                     "UPDATE rig_build.trace SET event = 'rewritten' WHERE id = %s".replace("%s", str(ev["id"]))):
            with self.assertRaises(pg_errors.RaiseException) as cm:
                self.conn.cursor().execute(stmt)
            self.assertIn("append-only", str(cm.exception))
            self.conn.rollback()

    def test_quality_score_requires_existing_attempt(self):
        with self.assertRaises(psycopg2.IntegrityError):
            measure_store.record_quality(self.conn, cell="C05", trial_id="ghost",
                                       attempt_seq=1, rubric="r", score=88)
        self.conn.rollback()

    # qualification is derived, never hand-written --------------------------
    def test_qualification_requires_pass_family_verdict(self):
        vid = self.seed_quorum(cell="C20", verdict="PARTIAL")
        with self.assertRaises(pg_errors.RaiseException) as cm:
            measure_store.record_qualification(self.conn, cell="C20", verdict_id=vid)
        self.assertIn("PERFECT|VERIFIED", str(cm.exception))
        self.conn.rollback()

    def test_qualification_requires_full_quorum(self):
        vid = self.seed_quorum(cell="C21", n=71)
        with self.assertRaises(pg_errors.RaiseException) as cm:
            measure_store.record_qualification(self.conn, cell="C21", verdict_id=vid)
        self.assertRegex(str(cm.exception), r"n=\d+ < 72")
        self.conn.rollback()
        # 72 attempts but only 9 durable
        vid = self.seed_quorum(cell="C22", n=72, durable=9)
        with self.assertRaises(pg_errors.RaiseException) as cm:
            measure_store.record_qualification(self.conn, cell="C22", verdict_id=vid)
        self.assertIn("durable-arm", str(cm.exception))
        self.conn.rollback()

    def test_qualification_happy_path_then_immutable(self):
        vid = self.seed_quorum(cell="C23")
        q = measure_store.record_qualification(self.conn, cell="C23", verdict_id=vid)
        self.assertGreaterEqual(q["n_attempts"], 72)
        self.assertGreaterEqual(q["span_hours"], 24)
        self.assertIsNotNone(measure_store.qualification(self.conn, "C23"))
        self.assertIsNone(measure_store.qualification(self.conn, "NOPE"))
        with self.assertRaises(psycopg2.IntegrityError):
            measure_store.record_qualification(self.conn, cell="C23", verdict_id=vid)
        self.conn.rollback()
        with self.assertRaises(pg_errors.RaiseException):
            self.conn.cursor().execute("DELETE FROM rig_build.qualification WHERE cell='C23'")
        self.conn.rollback()

    # outbox: ambiguous ack is a state, never an auto-resend ----------------
    def test_outbox_direct_state_edit_refused(self):
        ob = measure_store.outbox_new(self.conn, topic="notify", payload={"n": 1})
        with self.assertRaises(pg_errors.RaiseException) as cm:
            self.conn.cursor().execute(
                "UPDATE rig_build.outbox SET state='reconciled' WHERE outbox_id=%s",
                (ob["outbox_id"],))
        self.assertIn("named functions", str(cm.exception))
        self.conn.rollback()

    def test_outbox_state_machine_transitions(self):
        ob = measure_store.outbox_new(self.conn, topic="notify", payload={"n": 1})
        oid = ob["outbox_id"]
        with self.assertRaises(pg_errors.RaiseException):
            measure_store.outbox_set_state(self.conn, outbox_id=oid, next_state="reconciled")
        self.conn.rollback()
        # ambiguous ack requires the reconciliation note
        with self.assertRaises(pg_errors.RaiseException) as cm:
            measure_store.outbox_set_state(self.conn, outbox_id=oid, next_state="unknown")
        self.assertIn("note", str(cm.exception))
        self.conn.rollback()
        st = measure_store.outbox_set_state(self.conn, outbox_id=oid, next_state="unknown",
                                          note="provider 504, ack unknown")
        self.assertEqual(st["state"], "unknown")
        self.assertEqual(st["attempts"], 0)  # unknown never counts as an attempt
        st = measure_store.outbox_set_state(self.conn, outbox_id=oid, next_state="pending",
                                          note="reconciled: provider confirms not received")
        self.assertEqual((st["state"], st["attempts"]), ("pending", 1))
        measure_store.outbox_set_state(self.conn, outbox_id=oid, next_state="sent")
        st = measure_store.outbox_set_state(self.conn, outbox_id=oid, next_state="reconciled",
                                          note="receipt 0192 seen")
        self.assertEqual(st["state"], "reconciled")
        with self.assertRaises(pg_errors.RaiseException):
            measure_store.outbox_set_state(self.conn, outbox_id=oid, next_state="pending")
        self.conn.rollback()

    def test_seal_link_binds_trials(self):
        measure_store.record_trial(self.conn, cell="C30", trial_id="t", attempt_seq=1,
                                 family="f", model="m", node="n", task_sha=SHA_A,
                                 outcome="pass", started_at=self.t0, finished_at=self.t0)
        n = measure_store.link_seal(self.conn, packet_hash=SHA_A,
                                  links=[("trial", "C30|t|1"), ("verdict", "7")])
        self.assertEqual(n, 2)  # both links inserted
        with self.assertRaises(measure_store.StoreError):
            measure_store.link_seal(self.conn, packet_hash="not-a-hash", links=[("trial", "x")])


if __name__ == "__main__":
    unittest.main()
