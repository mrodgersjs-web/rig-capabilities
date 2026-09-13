"""B31 intake worker behavior: the refusals are the contract.

sqlite harness per test_build_store (portable DDL, no live DB, no mocks).
"""
import hashlib
import sqlite3
import unittest

from rig_capabilities import build_store
from rig_capabilities import build_intake

CELL = "L1-D1-A1-R"
URL = "https://example.test/guide"
BODY = "deterministic intake body"


def _conn():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(build_store.portable_ddl_sqlite())
    build_store.put_cell_contract(
        conn, cell_id=CELL, criteria_version="v1",
        contract={"done_test": ["intake"]},
        criteria_pack_sha256="f4" * 32, sealed_by="T")
    build_store.register_process_version(
        conn, process_key="intake", version="1", definition={},
        declared_owner="python-intake", registered_by="T")
    return conn


def _packet(**over):
    p = {"cell_id": CELL, "criteria_version": "v1", "process_key": "intake",
         "process_version": "1", "route": "document",
         "source": {"url": URL, "provider": "t", "kind": "guide",
                    "content": BODY,
                    "content_sha256": hashlib.sha256(BODY.encode()).hexdigest()}}
    for k, v in over.items():
        if k in p["source"]:
            p["source"][k] = v
        else:
            p[k] = v
    return p


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.conn = _conn()
        self.addCleanup(self.conn.close)

    def test_happy_path_persists_and_routes_exactly_once(self):
        out = build_intake.ingest(self.conn, _packet())
        self.assertEqual(out["status"], "started")
        self.assertEqual(out["effect"], "routed")
        self.assertEqual(out["topic"], "intake.document")
        self.assertEqual(
            out["dedupe_key"], hashlib.sha256(URL.encode()).hexdigest())
        rows = build_intake.pending(self.conn)
        self.assertEqual(len(rows), 1)
        # replay: re-ingesting the same packet forks nothing
        again = build_intake.ingest(self.conn, _packet())
        self.assertEqual(again["status"], "replayed")
        self.assertEqual(again["effect"], "already_routed")
        self.assertEqual(again["run_id"], out["run_id"])
        self.assertEqual(len(build_intake.pending(self.conn)), 1)

    def test_tampered_content_hash_refused(self):
        with self.assertRaises(build_intake.Refused) as cm:
            build_intake.ingest(self.conn, _packet(content_sha256="0" * 64))
        self.assertIn("tampered", str(cm.exception))

    def test_unknown_route_refused_no_default(self):
        with self.assertRaises(build_intake.Refused) as cm:
            build_intake.ingest(self.conn, _packet(route="kestra"))
        self.assertIn("no default", str(cm.exception))

    def test_missing_and_unknown_keys_refused(self):
        p = _packet()
        del p["route"]
        with self.assertRaises(build_intake.Refused):
            build_intake.validate(p)
        p = _packet()
        p["surprise"] = True
        with self.assertRaises(build_intake.Refused):
            build_intake.validate(p)

    def test_malformed_cell_refused(self):
        with self.assertRaises(build_intake.Refused):
            build_intake.ingest(self.conn, _packet(cell_id="L9-D1-A1-R"))

    def test_source_without_content_is_pending_not_fetched(self):
        p = _packet()
        del p["source"]["content"]
        del p["source"]["content_sha256"]
        out = build_intake.ingest(self.conn, p)
        self.assertEqual(out["document"], "accepted")
        cur = build_store._exec(
            self.conn, "SELECT retrieval_status FROM rig_build.source_documents")
        self.assertEqual(build_store._fetch_rows(cur)[0]["retrieval_status"],
                         "PENDING")


if __name__ == "__main__":
    unittest.main()
