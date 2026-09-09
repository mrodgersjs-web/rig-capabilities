"""Estate ledger classifier and corroboration-parser fixtures.

Covers the three KeepAlive shapes (True / False / conditional dict), the
launchctl and lsof parsers against captured real output, and the launchd
classification decisions derived from them.
"""

import json
import os
import plistlib
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / "capabilities/skills/rig-determinism-85"
sys.path.insert(0, str(SKILL))

import estate_validator  # noqa: E402
import estate_ledger
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
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="d85-validator-")
        self.addCleanup(temp.cleanup)
        Path(temp.name, "enforcement.json").write_text(json.dumps({"roots": [temp.name], "ttl_hours": 24}))
        env = patch.dict(os.environ, {"RIG_D85_HOME": temp.name})
        env.start()
        self.addCleanup(env.stop)

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


class TestLauncherRule(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="d85-estate-")
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.epoch = 1788980438
        self.config = self.home / "enforcement.json"
        self.config.write_text(json.dumps({
            "roots": [str(self.home)], "ttl_hours": 24, "launcher_epoch": self.epoch,
        }))
        env = patch.dict(os.environ, {"RIG_D85_HOME": str(self.home)})
        env.start()
        self.addCleanup(env.stop)

    def test_builder_to_validator_uses_source_mtime_and_preserves_legacy_backlog(self):
        agents = self.home / "Library/LaunchAgents"
        agents.mkdir(parents=True)
        for name, stamp in (("legacy", self.epoch - 1), ("boundary", self.epoch), ("new", self.epoch + 1)):
            path = agents / f"{name}.plist"
            path.write_bytes(plistlib.dumps({"StartInterval": 60}))
            os.utime(path, (stamp, stamp))
        with patch.object(Path, "home", return_value=self.home), \
             patch.object(estate_ledger, "_label_pids", return_value={}), \
             patch.object(estate_ledger, "_listener_pids", return_value={}):
            ledger = estate_ledger.build_ledger()
        records = {job["job_id"]: job for job in ledger["jobs"]}
        self.assertEqual(records["new"]["modified_at_source"], {
            "path": str(agents / "new.plist"), "field": "stat.st_mtime", "value": self.epoch + 1,
        })
        self.assertEqual(estate_validator._parse_ts(records["new"]["modified_at"]),
                         datetime.fromtimestamp(self.epoch + 1, timezone.utc))
        problems = estate_validator.validate(ledger)
        self.assertEqual({p.split(":")[0] for p in problems}, {"boundary", "new"})
        self.assertEqual(ledger["_grandfathered_launcher_missing"], 1)
        self.assertEqual(estate_validator.validate(ledger), problems)
        self.assertEqual(ledger["_grandfathered_launcher_missing"], 1)
        launcher = self.home / "job.py"
        launcher.write_text("print('fixture')\n")
        for name in ("boundary", "new"):
            records[name]["launcher"] = str(launcher)
        self.assertEqual(estate_validator.validate(ledger), [])

    def test_undated_or_invalid_job_is_not_automatically_legacy(self):
        for modified in (None, "invalid", float("nan"), True):
            with self.subTest(modified=modified):
                ledger = {"jobs": [{"job_id": "new-undated", "class": "needs_review", "action": "review", "modified_at": modified}]}
                problems = estate_validator.validate(ledger)
                self.assertTrue(any("new-undated" in p and "launcher" in p for p in problems), problems)
                self.assertEqual(ledger["_grandfathered_launcher_missing"], 0)

    def test_invalid_epoch_and_missing_config_fail_closed(self):
        self.config.write_text(json.dumps({"launcher_epoch": "not a timestamp"}))
        self.assertTrue(any("launcher_epoch invalid" in p for p in estate_validator.validate({"jobs": []})))
        self.config.unlink()
        self.assertTrue(any("config unreadable" in p for p in estate_validator.validate({"jobs": []})))

    def test_numeric_epoch_and_offset_timestamp_compare_in_utc(self):
        numeric = estate_validator._parse_ts(self.epoch)
        self.assertEqual(numeric, datetime.fromtimestamp(self.epoch, timezone.utc))
        self.assertEqual(estate_validator._parse_ts("2026-09-09T12:00:00-06:00"),
                         estate_validator._parse_ts("2026-09-09T18:00:00Z"))

    def test_hermes_root_and_profile_stores_have_distinct_job_ids(self):
        paths = [self.home / ".hermes/cron/jobs.json",
                 self.home / ".hermes/profiles/team/cron/jobs.json"]
        for path in paths:
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"jobs": [{"id": "shared", "enabled": True, "state": "scheduled"}]}))
            os.utime(path, (self.epoch + 1, self.epoch + 1))
        (self.home / ".hermes/jobs.json").write_text('{"jobs":[{"id":"stale","enabled":true}]}')
        with patch.object(Path, "home", return_value=self.home):
            records, summary = estate_ledger._hermes_summary()
        self.assertEqual({r["job_id"] for r in records}, {"hermes:root:shared", "hermes:team:shared"})
        self.assertEqual({r["origin"] for r in records}, {str(p) for p in paths})
        self.assertEqual(summary["enabled"], 2)
        self.assertEqual(len(estate_validator.validate({"jobs": records})), 2)


if __name__ == "__main__":
    unittest.main()
