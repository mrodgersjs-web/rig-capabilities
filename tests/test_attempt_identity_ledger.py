"""Attempt-identity ledger: the gate's own regression suite.

Pins the exit-code contract of
`capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py`
fixture by fixture, and pins the two properties the matrix done-test names:

1. equal weight — a 2-step run and a 50-step run of one task both claim
   per-attempt weight 1:1 and the verdict does not move; the step-weighted
   claim (50 steps => weight 50) exits 2;
2. one reward per attempt — a second reward row on one rollout_id exits 2.

`ran` is never `clean`: exit 1 (refusal) is asserted distinct from 0 and 2.
Fixture-only, subprocess-only, deterministic, writes nothing into the repo.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ASSET = REPO_ROOT / "capabilities" / "data" / "attempt-identity-ledger-and-equal-weight"
CHECKER = ASSET / "validate_ledger.py"
FX = ASSET / "fixtures"


def run_checker(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(CHECKER), *args],
                          cwd=cwd or REPO_ROOT, capture_output=True, text=True,
                          timeout=60)


class GreenTests(unittest.TestCase):
    def test_balanced_ledger_is_clean(self):
        p = run_checker(str(FX / "ledger_valid.jsonl"))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("4 attempt(s)", p.stdout)

    def test_short_and_long_run_carry_identical_weight(self):
        """The matrix done-test: plant the 50-step run, the verdict does not move."""
        short = run_checker(str(FX / "ledger_short_run.jsonl"),
                            "--expect-weight", "task-demo=1:1", "--show-weight")
        long = run_checker(str(FX / "ledger_long_run.jsonl"),
                           "--expect-weight", "task-demo=1:1", "--show-weight")
        self.assertEqual(short.returncode, 0, short.stdout + short.stderr)
        self.assertEqual(long.returncode, 0, long.stdout + long.stderr)
        self.assertIn("task task-demo: weight=1.0 reward_sum=1 steps=2", short.stdout)
        self.assertIn("task task-demo: weight=1.0 reward_sum=1 steps=50", long.stdout)


class RedPlantTests(unittest.TestCase):
    """Each plant is the failure the gate exists to catch; kept forever."""

    def assert_plant_red(self, fixture: str, *extra: str):
        p = run_checker(str(FX / fixture), *extra)
        self.assertEqual(p.returncode, 2, f"{fixture}: {p.stdout}{p.stderr}")
        return p

    def test_double_reward_is_red(self):
        p = self.assert_plant_red("ledger_double_reward.jsonl")
        self.assertIn("double_reward", p.stdout)

    def test_orphan_step_rows_are_red(self):
        p = self.assert_plant_red("ledger_orphan_step.jsonl")
        self.assertIn("orphan_step_rows", p.stdout)

    def test_unknown_end_reason_is_red(self):
        p = self.assert_plant_red("ledger_unknown_end_reason.jsonl")
        self.assertIn("unknown_end_reason", p.stdout)

    def test_nonbinary_reward_is_red(self):
        p = self.assert_plant_red("ledger_nonbinary_reward.jsonl")
        self.assertIn("is not the integer 0 or 1", p.stdout)
        # bool is an int subclass; `reward: true` must not smuggle a 1 through
        self.assertIn("reward True", p.stdout)

    def test_reward_without_task_is_red(self):
        p = self.assert_plant_red("ledger_reward_missing_task.jsonl")
        self.assertIn("reward_missing_fields: task_id", p.stdout)

    def test_step_weighted_claim_is_red(self):
        """The very bias this asset closes: 50 steps claiming weight 50."""
        p = self.assert_plant_red("ledger_long_run.jsonl",
                                  "--expect-weight", "task-demo=50:1")
        self.assertIn("equal_weight_claim_failed", p.stdout)

    def test_zero_attempt_ledger_is_red_not_vacuous_green(self):
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "empty.jsonl"
            empty.write_text("", encoding="utf-8")
            p = run_checker(str(empty))
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("ledger_has_no_attempts", p.stdout)

    def test_duplicate_step_seq_is_red(self):
        with tempfile.TemporaryDirectory() as td:
            dup = Path(td) / "dup.jsonl"
            dup.write_text(
                '{"row":"step","rollout_id":"r","seq":1,"event":"model_call"}\n'
                '{"row":"step","rollout_id":"r","seq":1,"event":"tool_event"}\n'
                '{"row":"reward","rollout_id":"r","task_id":"t",'
                '"end_reason":"verified","reward":1}\n', encoding="utf-8")
            p = run_checker(str(dup))
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertIn("duplicate_step_seq", p.stdout)


class RefusalTests(unittest.TestCase):
    """Exit 1 is a refusal to judge, distinct from clean (0) and guilty (2)."""

    def test_missing_file_refuses(self):
        p = run_checker(str(FX / "no_such_ledger.jsonl"))
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)

    def test_unparseable_weight_claim_refuses(self):
        p = run_checker(str(FX / "ledger_valid.jsonl"),
                        "--expect-weight", "not-a-claim")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("usage_error", p.stdout + p.stderr)

    def test_usage_error_refuses_with_one_not_two(self):
        p = run_checker()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)


class AssetHygieneTests(unittest.TestCase):
    def test_descriptor_exemplar_and_fixtures_exist(self):
        self.assertTrue((ASSET / "DATA.md").is_file())
        self.assertTrue((ASSET / "validate_ledger.py").is_file())
        ge = (REPO_ROOT / "examples" / "great" / "agent-engineering" /
              "attempt-identity-ledger-and-equal-weight.md")
        self.assertTrue(ge.is_file())
        self.assertGreater(ge.stat().st_size, 400)
        names = {p.name for p in FX.iterdir()}
        for plant in ("ledger_double_reward.jsonl", "ledger_orphan_step.jsonl",
                      "ledger_unknown_end_reason.jsonl",
                      "ledger_nonbinary_reward.jsonl",
                      "ledger_reward_missing_task.jsonl"):
            self.assertIn(plant, names)


if __name__ == "__main__":
    unittest.main()
