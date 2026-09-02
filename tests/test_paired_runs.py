"""Paired-run evidence: a claim is admissible only from a one-variable pair,
and recorded negatives may not be deleted.

Fixtures are the permanent regression cases; each planted-defect fixture must
keep going RED, and the checker must never rewrite the ledger it adjudicates.
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from rig_capabilities.paired_runs import canonical_hash, check  # noqa: E402

FIX = REPO_ROOT / "examples" / "fixtures" / "paired-runs"


class PairedRunTests(unittest.TestCase):
    def test_valid_pair_green(self):
        """One named difference, correctness improved, cost <2x: admissible."""
        self.assertEqual(check(FIX / "valid_pair.jsonl"), 0)

    def test_two_variables_differ_red(self):
        """skill AND model moved: the pair proves nothing and is rejected."""
        self.assertEqual(check(FIX / "two_variables.jsonl"), 1)

    def test_no_pair_red(self):
        """An improvement claim with no frozen counterpart is noise."""
        self.assertEqual(check(FIX / "no_pair.jsonl"), 1)

    def test_identical_config_red(self):
        """Hash-for-hash identical configs cannot 'improve' anything."""
        self.assertEqual(check(FIX / "same_config.jsonl"), 1)

    def test_cost_regression_red(self):
        """Unchanged correctness at 2.5x tokens is a regression (arXiv:2608.11888)."""
        self.assertEqual(check(FIX / "cost_regression.jsonl"), 1)

    def test_retained_negative_missing_red(self):
        """A negative id recorded in the baseline ledger may not vanish."""
        self.assertEqual(check(FIX / "ledger_dropped_negative.jsonl",
                               baseline=FIX / "baseline_ledger.jsonl"), 1)

    def test_retained_negatives_green(self):
        """Superset ledger (everything retained, more recorded): admissible."""
        self.assertEqual(check(FIX / "ledger_keeps_negative.jsonl",
                               baseline=FIX / "baseline_ledger.jsonl"), 0)

    def test_missing_cost_field_red(self):
        """A claimed pair with no token count fails: both axes are mandatory."""
        import json, tempfile
        rows = [json.loads(l) for l in
                (FIX / "valid_pair.jsonl").read_text().splitlines() if l.strip()]
        pair = [r for r in rows if r["pair_id"] == "P-77"]
        del pair[1]["tokens"]  # claimed side loses its cost evidence
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "ledger.jsonl"
            f.write_text("".join(json.dumps(r) + "\n" for r in pair))
            self.assertEqual(check(f), 1)

    def test_tampered_config_hash_red(self):
        """Editing a config after recording must not survive the recompute."""
        import json, tempfile
        rows = [json.loads(l) for l in
                (FIX / "valid_pair.jsonl").read_text().splitlines() if l.strip()]
        pair = [r for r in rows if r["pair_id"] == "P-77"]
        pair[1]["config"]["model"] = "rig-fable5-jailbroken-twin"  # stale hash now lies
        self.assertNotEqual(pair[1]["config_hash"],
                            canonical_hash(pair[1]["config"]))
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "ledger.jsonl"
            f.write_text("".join(json.dumps(r) + "\n" for r in pair))
            self.assertEqual(check(f), 1)

    def test_checker_never_rewrites_the_ledger(self):
        """Retention is enforced, editing is never performed — read-only, always."""
        for name in ("valid_pair.jsonl", "two_variables.jsonl",
                     "ledger_dropped_negative.jsonl"):
            f = FIX / name
            before = f.read_bytes()
            check(f, baseline=FIX / "baseline_ledger.jsonl")
            self.assertEqual(f.read_bytes(), before, f"{name} was mutated")


class CliTests(unittest.TestCase):
    """Exit codes are the contract the harness proofs and done_when depend on."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "rig_capabilities" / "paired_runs.py"),
             *args], capture_output=True, text=True, cwd=REPO_ROOT)

    def test_cli_green_exit_zero_with_deltas(self):
        r = self._run("check", "examples/fixtures/paired-runs/valid_pair.jsonl")
        self.assertEqual(r.returncode, 0)
        self.assertIn("delta=improved", r.stdout)
        self.assertIn("tokens 48200->51800", r.stdout)

    def test_cli_red_exit_one(self):
        r = self._run("check", "examples/fixtures/paired-runs/two_variables.jsonl")
        self.assertEqual(r.returncode, 1)
        self.assertIn("two_variables_differ", r.stderr)

    def test_cli_retention_diff_exit_one(self):
        r = self._run("check",
                      "examples/fixtures/paired-runs/ledger_dropped_negative.jsonl",
                      "--baseline",
                      "examples/fixtures/paired-runs/baseline_ledger.jsonl")
        self.assertEqual(r.returncode, 1)
        self.assertIn("retained_negative_missing", r.stderr)

    def test_unreadable_ledger_is_red_not_green(self):
        r = self._run("check", "examples/fixtures/paired-runs/nope.jsonl")
        self.assertEqual(r.returncode, 1)
        self.assertIn("unreadable", r.stderr)


if __name__ == "__main__":
    unittest.main()
