"""A green `pass` has to say how much of it actually ran.

`done_tests.run_asset` skips a `done_when` entry it cannot parse (the house
convention lets a prose row sit in `done_when`, e.g. "a session of this type
completes with its gate green") and deliberately never invokes mutating MCP
entries. Both are recorded with `ok: None` and both were excluded from `pass`
in silence: an asset with ten running checks and five decorative ones printed
`"pass": true` exactly like an asset with fifteen real checks. That is the same
failure shape as a check that is always green — it just fails quietly.

The fix is additive (so no existing consumer breaks): `ran`, `unrunnable`, and
`unrunnable_forms` join the verdict, and the invariant
`ran + unrunnable == len(results)` is what a caller can assert.
"""
from __future__ import annotations

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
import sys  # noqa: E402
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities.catalog import Repo  # noqa: E402
from rig_capabilities.done_tests import run_asset  # noqa: E402

# An asset known to carry one prose row (verified against the index, and
# re-verified by test_prose_row_is_the_one_unrunnable_form below).
PROSE_ASSET = "mh-05-asset-pruning-session.yaml"
CLEAN_ASSET = "adversarial-agent-orchestration.md"


class RanAccountingTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo(REPO_ROOT)

    def _verdict(self, asset_id: str) -> dict:
        out = run_asset(self.repo, asset_id)
        self.assertIn("ran", out, "verdict lost its `ran` field")
        self.assertIn("unrunnable", out, "verdict lost its `unrunnable` field")
        results = out["results"]
        self.assertEqual(out["ran"] + out["unrunnable"], len(results),
                         f"{asset_id}: ran({out['ran']}) + "
                         f"unrunnable({out['unrunnable']}) != results({len(results)})")
        return out

    def test_counts_account_for_every_entry(self):
        self._verdict(PROSE_ASSET)
        self._verdict(CLEAN_ASSET)

    def test_prose_row_is_named_not_swallowed(self):
        out = self._verdict(PROSE_ASSET)
        self.assertGreater(out["unrunnable"], 0,
                           "the prose convention row must be counted")
        forms = [u["form"] for u in out["unrunnable_forms"]]
        self.assertTrue(any("session of this type" in f for f in forms), forms)
        for u in out["unrunnable_forms"]:
            self.assertTrue(u["detail"], f"{u['form']!r} counted without a reason")

    def test_pass_ignores_unrunnable_but_reports_it(self):
        """`pass` keeps its old meaning; the count is what changed."""
        out = self._verdict(PROSE_ASSET)
        ran_ok = [r["ok"] for r in out["results"] if r["ok"] is not None]
        self.assertEqual(out["pass"], all(ran_ok) and bool(ran_ok))
        self.assertNotIn(None, ran_ok, "an unrunnable row leaked into `ran`")

    def test_a_clean_asset_reports_zero(self):
        """Non-vacuity: the counter is not always nonzero."""
        out = self._verdict(CLEAN_ASSET)
        self.assertEqual(out["unrunnable"], 0, out["unrunnable_forms"])

    def test_unknown_asset_still_fails_loudly(self):
        out = run_asset(self.repo, "no-such-asset-2031.md")
        self.assertFalse(out["pass"])
        self.assertEqual(out.get("ran", 0), 0, out.get("ran"))


if __name__ == "__main__":
    unittest.main()
