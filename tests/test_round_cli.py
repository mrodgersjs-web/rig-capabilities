"""The round verdict has to reach whoever ran the round.

`rig_capabilities.rounds` already refuses a replayed diff by exiting 1
(`tests.test_round_record` proves that). The verdict stopped there:
`bin/rig-capabilities round` printed the report and fell through to `return 0`,
and the `capabilities_round` MCP handler returned the dict, which the transport
rendered as `isError: false`. A cron, a CI step, or an agent that checks `$?`
instead of reading JSON therefore recorded a refusal — a BLOCKED-REPLAY, a
blocked lane, a red gate — as a successful round.

These tests pin the three surfaces to one answer:

  module    `python3 -m rig_capabilities.rounds`   -> exit_code   (covered elsewhere)
  CLI       `bin/rig-capabilities round`           -> process rc  == report exit_code
  MCP       `capabilities_round`                   -> ToolError   when exit_code != 0

The CLI cases run the real command against the real estate with `--dry`, which
`rounds.run_round` guarantees never appends to `record.jsonl`
(`appended = 0 if dry else append_record(...)`), so the test leaves no residue.
"""
from __future__ import annotations

import importlib.util
import io
import json
import contextlib
import subprocess
import sys
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities import rounds  # noqa: E402
from rig_capabilities.catalog import Repo  # noqa: E402
from rig_capabilities.mcp_stdio import ToolError  # noqa: E402
from rig_capabilities.server import build_server  # noqa: E402


def _load_cli():
    """Load `bin/rig-capabilities` (extensionless) as a module."""
    name = "rig_capabilities_cli_under_test"
    loader = SourceFileLoader(name, str(REPO_ROOT / "bin" / "rig-capabilities"))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


class RoundCliTests(unittest.TestCase):
    def test_cli_process_rc_matches_report(self):
        """Real command, real report: rc must equal the report's own exit_code."""
        proc = subprocess.run(
            [str(REPO_ROOT / "bin" / "rig-capabilities"), "round", "misc",
             "--dry", "--n", "1", "--budget", "1"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=900)
        head = proc.stdout.find("{")
        self.assertGreaterEqual(head, 0,
                                f"no report printed; stderr={proc.stderr[-400:]}")
        report = json.JSONDecoder().raw_decode(proc.stdout[head:])[0]
        self.assertIn("exit_code", report, "report lost its verdict field")
        self.assertEqual(proc.returncode, int(report["exit_code"] or 0),
                         f"rc={proc.returncode} but report says "
                         f"exit_code={report['exit_code']}")
        # the dry round still has to be a real round, or the equality above is
        # comparing two zeros of an empty run. `run_round` reports the flag as
        # `dry` and the number of done-test evaluations it was allowed to spend.
        self.assertTrue(report.get("dry"), sorted(report)[:8])
        self.assertGreater(int(report.get("eval_budget_effective") or 0), 0,
                           "a round with no evaluation budget proves nothing")

    def test_main_returns_the_reported_code(self):
        """In-process: a report that says 1 must make main() return 1."""
        cli = _load_cli()
        original = rounds.run_round
        rounds.run_round = lambda *a, **k: {
            "exit_code": 1, "dry_run": True, "lane": "misc",
            "action": "rejected-repeat", "verdicts": ["BLOCKED-REPLAY"],
        }
        argv = sys.argv
        try:
            sys.argv = ["rig-capabilities", "round", "misc", "--dry"]
            with contextlib.redirect_stdout(io.StringIO()) as buf:
                rc = cli.main()
        finally:
            sys.argv = argv
            rounds.run_round = original
        self.assertEqual(rc, 1, f"main() swallowed the verdict (rc={rc})")
        self.assertIn("BLOCKED-REPLAY", buf.getvalue(),
                      "the report must still be printed, not just its code")

    def test_main_returns_zero_on_a_clean_round(self):
        """Non-vacuity: the previous test is not an unconditional 1."""
        cli = _load_cli()
        original = rounds.run_round
        rounds.run_round = lambda *a, **k: {
            "exit_code": 0, "dry_run": True, "lane": "misc",
            "action": "would-apply", "verdicts": ["ACCEPTED"],
        }
        argv = sys.argv
        try:
            sys.argv = ["rig-capabilities", "round", "misc", "--dry"]
            with contextlib.redirect_stdout(io.StringIO()):
                rc = cli.main()
        finally:
            sys.argv = argv
            rounds.run_round = original
        self.assertEqual(rc, 0)

    def test_mcp_handler_raises_when_refused(self):
        srv = build_server(Repo(REPO_ROOT))
        original = rounds.run_round
        rounds.run_round = lambda *a, **k: {
            "exit_code": 1, "lane": "misc", "action": "rejected-repeat",
            "verdicts": ["BLOCKED-REPLAY"],
            "diff_hash": "0123456789abcdef",
        }
        try:
            with self.assertRaises(ToolError) as caught:
                srv.handlers["capabilities_round"]({"lane": "misc"})
        finally:
            rounds.run_round = original
        text = str(caught.exception)
        self.assertIn("BLOCKED-REPLAY", text, text[:200])
        self.assertIn("0123456789abcdef", text,
                      "the refusing record line must survive into the error")

    def test_mcp_handler_returns_normally_on_a_clean_round(self):
        srv = build_server(Repo(REPO_ROOT))
        original = rounds.run_round
        rounds.run_round = lambda *a, **k: {
            "exit_code": 0, "lane": "misc", "verdicts": ["ACCEPTED"],
        }
        try:
            out = srv.handlers["capabilities_round"]({"lane": "misc"})
        finally:
            rounds.run_round = original
        self.assertEqual(out["exit_code"], 0)
        self.assertEqual(out["verdicts"], ["ACCEPTED"])


if __name__ == "__main__":
    unittest.main()
