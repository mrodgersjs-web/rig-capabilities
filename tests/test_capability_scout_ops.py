"""Weekly-scout ops: dedupe / diff / seal / guard, proven by exit code.

The compounding-loop discipline: a weekly cron that re-queues last week's
evidence, silently rewrites a sealed week, or keeps reporting success after it
stopped finding anything is indistinguishable from a working one — until these
gates make each failure a non-zero exit.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OPS = REPO / "scripts" / "capability_scout_ops.py"


def _week(root: Path, week: str, arx, repos, slugs=("code4ai",)):
    d = root / week
    d.mkdir(parents=True)
    (d / "week.json").write_text(json.dumps({
        "schema": "capability-scout-week-v1", "week": week,
        "sources": [{"slug": s} for s in slugs],
        "arxiv_verified": {a: {"resolved": True} for a in arx},
        "repos_verified": {r: {"verified": True} for r in repos}}), encoding="utf-8")


def _run(*args, out=None):
    cmd = [sys.executable, str(OPS), *args]
    if out:
        cmd += ["--out", str(out)]
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=120)


class ScoutOpsTests(unittest.TestCase):
    def setUp(self):
        self.td = Path(tempfile.mkdtemp(prefix="scout-ops-"))
        _week(self.td, "2026-W35", ["arXiv:2608.11111"], ["org/a"])
        _week(self.td, "2026-W36", ["arXiv:2608.11111", "arXiv:2608.22222"],
              ["org/a", "org/b"])

    def test_dedupe_reports_only_new_ids(self):
        p = _run("dedupe", "--week", "2026-W36", out=self.td)
        self.assertEqual(p.returncode, 0, p.stderr)
        rep = json.loads(p.stdout)
        self.assertEqual(rep["new_ids"], ["arXiv:2608.22222", "org/b"])
        self.assertEqual(rep["repeat_ids"], ["arXiv:2608.11111", "org/a"])

    def test_diff_is_the_set_delta(self):
        p = _run("diff", "--a", "2026-W35", "--b", "2026-W36", out=self.td)
        rep = json.loads(p.stdout)
        self.assertEqual(rep["added"], ["arXiv:2608.22222", "org/b"])
        self.assertEqual(rep["removed"], [])
        self.assertEqual(rep["retained"], ["arXiv:2608.11111", "org/a"])

    def test_seal_is_idempotent_and_catches_a_rewrite(self):
        self.assertEqual(_run("seal", "--week", "2026-W36", out=self.td).returncode, 0)
        self.assertEqual(_run("seal", "--week", "2026-W36", "--check",
                              out=self.td).returncode, 0)
        # order does not change the seal
        wj = self.td / "2026-W36" / "week.json"
        d = json.loads(wj.read_text())
        d["arxiv_verified"] = dict(reversed(list(d["arxiv_verified"].items())))
        wj.write_text(json.dumps(d), encoding="utf-8")
        self.assertEqual(_run("seal", "--week", "2026-W36", "--check",
                              out=self.td).returncode, 0, "reorder must not break the seal")
        # a real content change does
        d["arxiv_verified"]["arXiv:9999.99999"] = {"resolved": True}
        wj.write_text(json.dumps(d), encoding="utf-8")
        p = _run("seal", "--week", "2026-W36", "--check", out=self.td)
        self.assertEqual(p.returncode, 2)
        self.assertIn("SEAL_MISMATCH", p.stdout)

    def test_guard_flags_a_stalled_cron(self):
        p = _run("guard", "--cadence-days", "7", "--now", "2027-01-01", out=self.td)
        self.assertEqual(p.returncode, 2)
        self.assertIn("STALLED", p.stdout)

    def test_guard_flags_source_drift(self):
        _week(self.td, "2026-W40", ["arXiv:2608.4"], [], slugs=("someone-else",))
        p = _run("guard", "--cadence-days", "7", "--now", "2026-10-08", out=self.td)
        self.assertEqual(p.returncode, 2)
        self.assertIn("DRIFT", p.stdout)

    def test_guard_green_when_fresh_and_aligned(self):
        p = _run("guard", "--cadence-days", "7", "--now", "2026-09-05", out=self.td)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_guard_is_not_theater(self):
        """Out-of-band plant: disable the stall clause -> a 4-month-old cron passes."""
        src = OPS.read_text(encoding="utf-8")
        anchor = "        if age > 2 * cadence_days:"
        self.assertIn(anchor, src)
        with tempfile.TemporaryDirectory() as pd:
            planted = Path(pd) / "ops.py"
            planted.write_text(src.replace(anchor, "        if False:  # PLANT"),
                               encoding="utf-8")
            p = subprocess.run(
                [sys.executable, str(planted), "guard", "--cadence-days", "7",
                 "--now", "2027-01-01", "--out", str(self.td)],
                cwd=REPO, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, "planted guard should miss the stall")


if __name__ == "__main__":
    unittest.main()
