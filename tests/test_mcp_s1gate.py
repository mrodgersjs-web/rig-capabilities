"""The System-1 gate (Jev) riding the capability MCP server.

Pinned contract, in the order it would hurt to break:

1. the tool is registered AND has a handler (a spec without a binding answers
   nothing, and a handler without a spec is unreachable from a harness);
2. nothing prints to stdout -- stdout is the JSON-RPC channel, so a stray print
   inside the gate corrupts the transport for every other tool on the server;
3. a provider failure comes back as `fail_closed` DATA, not as a crash and not
   as a pass (law 1: an unrun gate is never consent);
4. `calibrate` can never write (law 3: enforcing is a human decision), and no
   caller-supplied key can smuggle it;
5. the caps that bound spend are real, because `rank`/`improve` multiply live
   Jev calls inside a single tool turn.

Every gate call here is mocked or offline except `list`/`stats`/`recent`/
`show`/`selftest`, so the suite costs nothing and survives the API being down.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import s1gate, s1gate_bridge, server  # noqa: E402
from rig_capabilities.mcp_stdio import ToolError  # noqa: E402


class _FakeResult:
    """Stand-in for GateResult -- only the keys the bridge adds matter here."""

    def __init__(self, verdict="PASS", advisory=True):
        self.verdict, self.advisory = verdict, advisory

    def to_dict(self):
        return {"rubric": "post.linkedin", "verdict": self.verdict,
                "enforced": not self.advisory, "reasons": [], "answers": {},
                "model": "jev-test", "latency_ms": 12, "advisory": self.advisory,
                "state_sha256": "x" * 64, "state_preview": "draft", "error": None,
                "decision_id": 1}


class S1GateToolTests(unittest.TestCase):
    """Write-capable verbs run against a throwaway decision log: a test that
    labels the corpus or records a fail-closed BLOCK into ~/.rig/s1gate is a
    test poisoning the very data calibration is later measured against."""

    @classmethod
    def setUpClass(cls):
        cls.srv = server.build_server()

    def call(self, args):
        # NOT cls.call = handlers[...]: a function stored as a CLASS attribute
        # becomes a bound method and silently receives `self` as the args dict.
        return self.srv.handlers["capabilities_s1gate"](args)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        patcher = mock.patch.object(s1gate, "DB_PATH",
                                    Path(self._tmp.name) / "decisions.db")
        patcher.start()
        self.addCleanup(patcher.stop)

    # -- 1. wiring ---------------------------------------------------------
    def test_tool_is_registered_with_a_handler(self):
        spec = next((t for t in server.TOOLS
                     if t["name"] == "capabilities_s1gate"), None)
        self.assertIsNotNone(spec, "capabilities_s1gate missing from TOOLS")
        self.assertIn("capabilities_s1gate", self.srv.handlers)

    def test_schema_action_enum_matches_the_bridge(self):
        spec = next(t for t in server.TOOLS if t["name"] == "capabilities_s1gate")
        props = spec["inputSchema"]["properties"]
        self.assertEqual(props["action"]["enum"], list(s1gate_bridge.ACTIONS))
        self.assertEqual(spec["inputSchema"]["required"], ["action"])

    # -- 2. stdout discipline ---------------------------------------------
    def test_no_verb_writes_to_stdout(self):
        """A print() anywhere in the gate would corrupt the JSON-RPC channel."""
        for args in ({"action": "list"}, {"action": "stats"},
                     {"action": "recent", "limit": 3}, {"action": "bogus"}):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                self.call(args)
            self.assertEqual(buf.getvalue(), "",
                             "%s leaked to stdout" % args["action"])

    def test_list_reports_every_rubric_and_its_mode(self):
        # (reads rubric JSONs from the repo, never the decision log)
        out = self.call({"action": "list"})
        self.assertTrue(out["ran"])
        self.assertGreaterEqual(out["count"], 13)
        names = {r["rubric"] for r in out["rubrics"]}
        for want in ("post.linkedin", "code.diff", "comment.linkedin",
                     "nil.jacob"):
            self.assertIn(want, names)
        for row in out["rubrics"]:
            self.assertIn(row["mode"], ("advisory", "ENFORCING"))
        self.assertIsInstance(out["enforcing"], list)

    def test_lane_c_stays_never_auto(self):
        out = self.call({"action": "show", "rubric": "nil.jacob"})
        self.assertTrue(out["never_auto"],
                        "Lane C lost its never_auto flag: a machine PASS on a "
                        "minor's content must never read as authorisation")

    # -- 3. fail closed ----------------------------------------------------
    def test_provider_failure_returns_fail_closed_data_not_a_pass(self):
        with mock.patch("rig_capabilities.s1gate.evaluate",
                        side_effect=RuntimeError("URLError: refused")):
            out = self.call({"action": "check", "rubric": "post.linkedin",
                             "text": "a draft", "subject": "t"})
        self.assertFalse(out["ran"])
        self.assertTrue(out["fail_closed"])
        self.assertNotEqual(out.get("verdict"), "PASS")
        self.assertIn("URLError", out["reason"])

    def test_billable_verbs_refuse_a_missing_subject(self):
        for action, args in (("check", {"text": "a draft"}),
                             ("rank", {"candidates": ["a", "b"]}),
                             ("improve", {"text": "a draft"})):
            with self.assertRaises(ToolError, msg=action) as cm:
                self.call({"action": action, "rubric": "post.linkedin",
                           "subject": "  ", **args})
            self.assertIn("subject", str(cm.exception))

    def test_unknown_action_is_data_not_an_exception(self):
        out = self.call({"action": "nope"})
        self.assertFalse(out["ran"])
        self.assertEqual(out["reason"], "unknown_action:nope")
        self.assertEqual(out["actions"], list(s1gate_bridge.ACTIONS))

    # -- 4. law 3: calibrate cannot write ----------------------------------
    def test_calibrate_is_dry_run_and_refuses_a_write_key(self):
        captured = {}

        def fake_calibrate(rubric, signal, **kw):
            captured.update(rubric=rubric, signal=signal, **kw)
            return {"certified": False, "rubric": rubric, "n": 0}

        def fake_report(result):
            return "dry report (certified=%s)" % result["certified"]

        with mock.patch("rig_capabilities.s1gate_calibrate.calibrate_rubric",
                        fake_calibrate), \
                mock.patch("rig_capabilities.s1gate_calibrate.report",
                           fake_report):
            out = self.call({"action": "calibrate", "rubric": "code.diff",
                             "signal": "weakened_test.noul"})
            self.assertTrue(out["dry_run"])
            self.assertIs(captured["write"], False)
            self.assertIn("--write", out["to_enforce"])
            with self.assertRaises(ToolError):
                self.call({"action": "calibrate", "rubric": "code.diff",
                           "signal": "weakened_test.noul", "write": True})

    def test_closed_schema_refuses_unknown_keys(self):
        with self.assertRaises(ToolError):
            self.call({"action": "list", "verdict": "PASS"})

    def test_unknown_rubric_names_the_packs_instead_of_failing_later(self):
        with self.assertRaises(ToolError) as cm:
            self.call({"action": "check", "rubric": "post.linkeind",
                       "text": "a draft"})
        msg = str(cm.exception)
        self.assertIn("post.linkedin", msg, "refusal should list the real packs")

    def test_rubric_required_for_the_rubric_verbs(self):
        for action in ("show", "check", "rank", "improve", "calibrate"):
            args = {"action": action}
            if action in ("check", "improve"):
                args["text"] = "x"
            if action == "rank":
                args["candidates"] = ["x", "y"]
            if action == "calibrate":
                args["signal"] = "q.noul"
            with self.assertRaises(ToolError, msg=action):
                self.call(args)

    # -- 5. spend caps ----------------------------------------------------
    def test_rank_caps_candidates_and_requires_two(self):
        with self.assertRaises(ToolError):
            self.call({"action": "rank", "rubric": "post.linkedin",
                       "subject": "t", "candidates": ["only one"]})
        with self.assertRaises(ToolError):
            self.call({"action": "rank", "rubric": "post.linkedin",
                       "subject": "t", "candidates": ["c%d" % i for i in range(26)]})

    def test_improve_caps_iterations(self):
        with self.assertRaises(ToolError):
            self.call({"action": "improve", "rubric": "post.linkedin",
                       "subject": "t", "text": "draft", "max_iterations": 99})

    def test_check_needs_non_empty_text_under_the_size_cap(self):
        for bad in ("", "   ", None):
            with self.assertRaises(ToolError):
                self.call({"action": "check", "rubric": "post.linkedin",
                           "subject": "t", "text": bad})
        over = "z" * (s1gate_bridge.MAX_ARTIFACT_CHARS + 1)
        with self.assertRaises(ToolError):
            self.call({"action": "check", "rubric": "post.linkedin",
                       "subject": "t", "text": over})

    def test_check_passes_through_a_gate_verdict(self):
        with mock.patch("rig_capabilities.s1gate.evaluate",
                        return_value=_FakeResult()):
            out = self.call({"action": "check", "rubric": "post.linkedin",
                             "text": "a draft", "subject": "t"})
        self.assertTrue(out["ran"])
        self.assertEqual(out["verdict"], "PASS")
        self.assertEqual(out["decision_id"], 1)
        self.assertIn("law_6", out)
        self.assertTrue(out["enforced_note"].startswith("advisory"))

    def test_label_refuses_a_missing_decision_and_a_bad_label(self):
        with self.assertRaises(ToolError):
            self.call({"action": "label", "decision_id": 99_999_999,
                       "label": "good"})
        with self.assertRaises(ToolError):
            self.call({"action": "label", "decision_id": 1, "label": "maybe"})

    def test_selftest_proves_the_gate_without_the_api(self):
        out = self.call({"action": "selftest"})
        self.assertTrue(out["ran"], str(out.get("stdout")) + str(out.get("stderr")))
        self.assertEqual(out["exit_code"], 0)
        # The string comes from bin/rig-s1gate's own stdout, so this asserts the
        # subprocess really ran rather than the wrapper reporting success.
        self.assertIn("rule engine", out["stdout"])


class S1GateRealLogReadOnlyTests(unittest.TestCase):
    """Read-only verbs against the LIVE decision log, because they index rows
    by column name (ts/advisory/state_preview) and a temp DB with zero rows
    would pass a broken key lookup. Skipped, never faked, if there is no log."""

    @classmethod
    def setUpClass(cls):
        cls.srv = server.build_server()
        if not s1gate.DB_PATH.is_file():
            raise unittest.SkipTest(f"no decision log at {s1gate.DB_PATH}")

    def call(self, args):
        return self.srv.handlers["capabilities_s1gate"](args)

    def test_stats_counts_the_live_corpus(self):
        out = self.call({"action": "stats"})
        self.assertTrue(out["ran"])
        self.assertGreater(out["total"], 0, "stats reported zero against a "
                            "non-empty decisions.db -- the query is broken")
        self.assertEqual(sum(out["verdicts"].values()), out["total"])
        self.assertLessEqual(out["labelled"] + out["unlabelled"], out["total"])

    def test_recent_returns_real_rows_with_the_documented_keys(self):
        out = self.call({"action": "recent", "limit": 5})
        self.assertEqual(out["count"], len(out["rows"]))
        self.assertGreater(out["count"], 0)
        for row in out["rows"]:
            for key in ("id", "ts", "rubric", "verdict", "label", "advisory",
                        "model", "latency_ms"):
                self.assertIn(key, row)

    def test_review_of_a_real_id_carries_the_state_preview(self):
        rows = self.call({"action": "recent", "limit": 5})["rows"]
        out = self.call({"action": "review", "decision_id": rows[0]["id"]})
        self.assertEqual(out["id"], rows[0]["id"])
        self.assertIn(out["verdict"], ("PASS", "ESCALATE", "BLOCK"))
        self.assertIsInstance(out["answers"], dict)


if __name__ == "__main__":
    unittest.main(verbosity=2)
