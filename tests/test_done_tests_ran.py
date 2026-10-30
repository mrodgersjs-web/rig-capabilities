"""Done-tests reject stale, noncanonical, skipped, or nonaffirmative checks.

The runner reports `ran`, `unrunnable`, and `unrunnable_forms`. A green pass
requires every criterion to execute and pass against the current canonical
source. The invariant `ran + unrunnable == len(results)` remains checkable.
"""
from __future__ import annotations

import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace

REPO_ROOT = Path(__file__).resolve().parent.parent
import sys  # noqa: E402
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities.catalog import Repo  # noqa: E402
from rig_capabilities.done_tests import _run_form, run_asset  # noqa: E402

# Controlled prose fixture: catalog improvements must not erase this negative case.
PROSE_ASSET = "prose-fixture"
CLEAN_ASSET = "adversarial-agent-orchestration.md"


class RanAccountingTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo(REPO_ROOT)
        self.fixture_repo = SimpleNamespace(
            root=REPO_ROOT,
            _sha_file=lambda _path: "fixture-sha",
            load_index=lambda: {"assets": [{
                "id": PROSE_ASSET, "source": "canonical",
                "abs_path": str(REPO_ROOT / "pyproject.toml"), "sha": "fixture-sha",
                "quality": {"done_when": [
                    "file:pyproject.toml",
                    "a session of this type completes with its gate green",
                ]},
            }]},
        )

    def _verdict(self, asset_id: str) -> dict:
        out = run_asset(self.fixture_repo if asset_id == PROSE_ASSET else self.repo,
                        asset_id)
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

    def test_unrunnable_form_blocks_pass_and_is_reported(self):
        out = self._verdict(PROSE_ASSET)
        ran_ok = [r["ok"] for r in out["results"] if r["ok"] is not None]
        self.assertFalse(out["pass"])
        self.assertTrue(all(ran_ok))
        self.assertNotIn(None, ran_ok, "an unrunnable row leaked into `ran`")

    def test_noncanonical_done_test_cannot_execute(self):
        fixture = SimpleNamespace(
            root=REPO_ROOT,
            load_index=lambda: {"assets": [{"id": "external", "source": "external",
                                            "quality": {"done_when": ["cmd:true"]}}]},
        )
        out = run_asset(fixture, "external")
        self.assertFalse(out["pass"])
        self.assertEqual(out["ran"], 0)
        self.assertEqual(out["results"][0]["form"], "lookup")
        explicit = run_asset(fixture, "external", source="external")
        self.assertFalse(explicit["pass"])
        self.assertEqual(explicit["results"][0]["form"], "source")

    def test_missing_source_binding_cannot_execute(self):
        fixture = SimpleNamespace(
            root=REPO_ROOT,
            load_index=lambda: {"assets": [{"id": "unbound", "source": "canonical",
                                            "quality": {"done_when": ["cmd:true"]}}]},
        )
        out = run_asset(fixture, "unbound")
        self.assertFalse(out["pass"])
        self.assertEqual(out["ran"], 0)
        self.assertEqual(out["results"][0]["form"], "source")

    def test_mcp_failure_payload_does_not_pass(self):
        repo = SimpleNamespace(root=REPO_ROOT)
        blocked = _run_form(repo, "mcp", "fake", lambda _tool, _args: {"status": "BLOCKED"})
        unknown = _run_form(repo, "mcp", "fake", lambda _tool, _args: {"total": 1})
        passed = _run_form(repo, "mcp", "fake", lambda _tool, _args: {"status": "PASS"})
        contradictory = _run_form(repo, "mcp", "fake", lambda _tool, _args: {"pass": False, "status": "PASS"})
        self.assertFalse(blocked["ok"])
        self.assertFalse(unknown["ok"])
        self.assertFalse(contradictory["ok"])
        self.assertTrue(passed["ok"])

    def test_file_and_grep_cannot_read_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "outside-link").symlink_to("/dev/null")
            repo = SimpleNamespace(root=root)
            for path in ("/dev/null", "../outside", "outside-link"):
                self.assertFalse(_run_form(repo, "file", path)["ok"], path)
                self.assertFalse(_run_form(repo, "grep", (path, ".*"))["ok"], path)

    def test_a_clean_asset_reports_zero(self):
        """Non-vacuity: the counter is not always nonzero."""
        out = self._verdict(CLEAN_ASSET)
        self.assertEqual(out["unrunnable"], 0, out["unrunnable_forms"])

    def test_unknown_asset_still_fails_loudly(self):
        out = run_asset(self.repo, "no-such-asset-2031.md")
        self.assertFalse(out["pass"])
        self.assertEqual(out.get("ran", 0), 0, out.get("ran"))

    def test_changed_source_cannot_pass_cached_done_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Repo(Path(tmp))
            skill = repo.cap_root / "skills" / "sample"
            skill.mkdir(parents=True)
            source = skill / "SKILL.md"
            source.write_text("---\nname: sample\ndescription: Sample skill\n"
                              "done_when:\n  - file:capabilities/skills/sample/SKILL.md\n"
                              "---\n# Sample\n")
            repo.load_index(force=True)
            self.assertTrue(run_asset(repo, "sample")["pass"])
            source.write_text(source.read_text() + "Changed after index.\n")
            stale = run_asset(repo, "sample")
            self.assertFalse(stale["pass"])
            self.assertEqual(stale["ran"], 0)
            self.assertEqual(stale["results"][0]["form"], "source")
            repo.load_index(force=True)
            self.assertTrue(run_asset(repo, "sample")["pass"])


if __name__ == "__main__":
    unittest.main()
