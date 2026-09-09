"""Estate ledger classifier and corroboration-parser fixtures.

Covers the three KeepAlive shapes (True / False / conditional dict), the
launchctl and lsof parsers against captured real output, and the launchd
classification decisions derived from them.
"""

import sys
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "capabilities/skills/rig-determinism-85"
sys.path.insert(0, str(SKILL))

from estate_ledger import (  # noqa: E402
    _classify_launchd,
    _label_pids,
    _listener_pids,
    _plist_facts,
)

CAPTURED_LAUNCHCTL = (
    "PID\tStatus\tLabel\n"
    "-\t0\tcom.apple.SafariHistoryServiceAgent\n"
    "501\t0\tai.rig.apps.keepalive\n"
    "-\t78\tcom.rig.dead.job\n"
    "268\t0\tai.claude-code-router\n"
)

CAPTURED_LSOF = "p268\nf30\nn127.0.0.1:52726\np678\nf15\nn*:58155\np999\nf7\nn127.0.0.1:52726->140.82.113.25:443\n"


class PlistFactsTests(unittest.TestCase):
    def test_keepalive_true_is_unconditional(self) -> None:
        self.assertTrue(_plist_facts({"KeepAlive": True})["keepalive_unconditional"])
        self.assertFalse(_plist_facts({"KeepAlive": True})["keepalive_conditional"])

    def test_keepalive_false_is_no_lifetime(self) -> None:
        f = _plist_facts({"KeepAlive": False})
        self.assertFalse(f["keepalive_unconditional"])
        self.assertFalse(f["keepalive_conditional"])

    def test_keepalive_conditional_dict_is_not_unconditional(self) -> None:
        f = _plist_facts({"KeepAlive": {"SuccessfulExit": False, "Crashed": True}})
        self.assertFalse(f["keepalive_unconditional"])
        self.assertTrue(f["keepalive_conditional"])


class ParserTests(unittest.TestCase):
    def test_label_pids_reads_pid_status_label_columns(self) -> None:
        pids = _label_pids(CAPTURED_LAUNCHCTL)
        self.assertEqual(pids, {"ai.rig.apps.keepalive": 501, "ai.claude-code-router": 268})

    def test_listener_pids_keeps_every_listening_name(self) -> None:
        listeners = _listener_pids(CAPTURED_LSOF)
        # 999 is an outbound connection (-> remote), not a LISTEN-only capture,
        # but with -sTCP:LISTEN filtering the capture would never contain it;
        # the parser records every n-line following a p-line, which is correct
        # for LISTEN-filtered input.
        self.assertEqual(listeners[268], "127.0.0.1:52726")
        self.assertEqual(listeners[678], "*:58155")


class ClassifyTests(unittest.TestCase):
    def _stats(self) -> dict:
        return {"plists": 0, "vendor_skipped": 0, "resident": 0, "periodic": 0,
                "needs_review": 0, "unreadable": 0}

    def _classify(self, plist, corroboration=None):
        return _classify_launchd("test.job", Path("/tmp/test.job.plist"), plist,
                                 self._stats(), corroboration)

    def test_conditional_keepalive_with_schedule_is_periodic_not_resident(self) -> None:
        rec = self._classify({"KeepAlive": {"SuccessfulExit": False},
                              "StartInterval": 300})
        self.assertEqual((rec["class"], rec["action"]), ("periodic", "move"))
        self.assertEqual(rec["expected_framework"], "kestra_pydantic")

    def test_unconditional_keepalive_alone_needs_review(self) -> None:
        rec = self._classify({"KeepAlive": True, "RunAtLoad": True})
        self.assertEqual((rec["class"], rec["action"]), ("needs_review", "review"))

    def test_watch_paths_are_source_proven_resident(self) -> None:
        rec = self._classify({"WatchPaths": ["/tmp/watched"], "RunAtLoad": True})
        self.assertEqual((rec["class"], rec["action"]), ("resident", "keep"))
        self.assertEqual(rec["evidence"]["resident_service"]["resource_kind"],
                         "watched_directory")
        self.assertEqual(rec["expected_framework"], "launchd")



    def test_resource_plus_schedule_is_contradiction_review(self) -> None:
        rec = self._classify({"WatchPaths": ["/tmp/watched"], "StartInterval": 60})
        self.assertEqual((rec["class"], rec["action"]), ("needs_review", "review"))

    def test_lsof_corroboration_proves_resident(self) -> None:
        rec = self._classify({"KeepAlive": True, "RunAtLoad": True},
                             corroboration={"test.job": "127.0.0.1:8744"})
        self.assertEqual((rec["class"], rec["action"]), ("resident", "keep"))
        self.assertIn("OS corroboration", rec["evidence"]["resident_service"]["resource_detail"])

    def test_plain_periodic_moves_to_kestra(self) -> None:
        rec = self._classify({"StartCalendarInterval": {"Hour": 8, "Minute": 0}})
        self.assertEqual((rec["class"], rec["action"]), ("periodic", "move"))

    def test_no_markers_is_review(self) -> None:
        rec = self._classify({"ProgramArguments": ["/bin/true"]})
        self.assertEqual((rec["class"], rec["action"]), ("needs_review", "review"))

class ValidatorTests(unittest.TestCase):
    def _clean(self) -> dict:
        return {
            "schema": "rig.d85.estate-ledger.v1",
            "jobs": [
                {"job_id": "a", "class": "resident", "action": "keep",
                 "evidence": {"resident_service": {"resource_kind": "listening_socket",
                                                    "resource_detail": "Sockets in plist"}},
                 "expected_framework": "launchd", "note": ""},
                {"job_id": "b", "class": "periodic", "action": "move",
                 "evidence": {}, "expected_framework": "kestra_pydantic", "note": ""},
                {"job_id": "c", "class": "needs_review", "action": "review",
                 "evidence": None, "expected_framework": None, "note": ""},
            ],
        }

    def test_clean_ledger_validates(self) -> None:
        from estate_validator import validate
        self.assertEqual(validate(self._clean()), [])

    def test_tampered_verdict_is_flagged(self) -> None:
        from estate_validator import validate
        ledger = self._clean()
        ledger["jobs"][1]["expected_framework"] = "temporal"
        problems = validate(ledger)
        self.assertTrue(any("decision table says" in p for p in problems))

    def test_review_with_verdict_is_flagged(self) -> None:
        from estate_validator import validate
        ledger = self._clean()
        ledger["jobs"][2]["expected_framework"] = "kestra_pydantic"
        self.assertTrue(any("review must stay undecided" in p for p in validate(ledger)))

    def test_duplicate_job_id_is_flagged(self) -> None:
        from estate_validator import validate
        ledger = self._clean()
        ledger["jobs"][1]["job_id"] = "a"
        self.assertTrue(any("duplicate job_id" in p for p in validate(ledger)))

    def test_decided_without_evidence_is_flagged(self) -> None:
        from estate_validator import validate
        ledger = self._clean()
        ledger["jobs"][0]["evidence"] = None
        self.assertTrue(any("without dict evidence" in p for p in validate(ledger)))


if __name__ == "__main__":
    unittest.main()
