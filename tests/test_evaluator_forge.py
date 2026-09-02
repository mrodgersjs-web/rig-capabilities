"""Regression suite for the forged-evaluator gate (`validate_forge.py`).

The claim under test: a derived rubric must rank a real exemplar strictly
above its degraded twin, and every structural clause of the scoring record
(weight, weight-sum, path resolution, actually-degraded negative, localized
RED finding, declared margin) bites with exit 2 — while exit 1 stays reserved
for a refusal to judge (a missing file), never conflated with a verdict.

Every RED fixture is a permanent planted failure kept from the asset build;
the last test proves the gate is not theater by copying the checker, neutering
the ranking clause, and showing the inverted-ranking fixture flips to exit 0
(gate blind) while the untouched checker still returns 2.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSET = REPO / "capabilities" / "skills" / "evaluator-forge-from-exemplars"
CHECKER = ASSET / "validate_forge.py"
FIX = ASSET / "fixtures"

GREEN = [
    ("rubric_valid.yaml", "scores_valid.jsonl"),
    ("rubric_margin_exact.yaml", "scores_valid.jsonl"),  # gap == margin: boundary is clean
]

# fixture pair -> the clause its stderr must name
RED = [
    (("rubric_no_weight.yaml", "scores_valid.jsonl"), "has no weight"),
    (("rubric_weights_105.yaml", "scores_valid.jsonl"), "not 100"),
    (("rubric_valid.yaml", "scores_missing_path.jsonl"), "does not resolve"),
    (("rubric_valid.yaml", "scores_negative_identical.jsonl"), "byte-identical"),
    (("rubric_valid.yaml", "scores_rank_inverted.jsonl"), "fails to rank"),
    (("rubric_valid.yaml", "scores_unlocalized_finding.jsonl"), "not localized"),
    (("rubric_margin_90.yaml", "scores_valid.jsonl"), "below the declared margin"),
]


def _run(checker: Path, rubric: str, scores: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(checker), str(FIX / rubric), str(FIX / scores)],
        capture_output=True, text=True, cwd=REPO)


class CleanCases(unittest.TestCase):
    def test_green_forms_exit_zero(self):
        for rubric, scores in GREEN:
            with self.subTest(rubric=rubric):
                p = _run(CHECKER, rubric, scores)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertIn("CLEAN", p.stdout)


class RedCases(unittest.TestCase):
    def test_every_plant_exits_two_naming_its_clause(self):
        for (rubric, scores), clause in RED:
            with self.subTest(rubric=rubric, scores=scores):
                p = _run(CHECKER, rubric, scores)
                self.assertEqual(p.returncode, 2, f"{rubric}+{scores}: {p.stderr}")
                self.assertIn(clause, p.stderr)

    def test_clause_messages_are_all_distinct(self):
        clauses = {clause for _, clause in RED}
        self.assertEqual(len(clauses), len(RED), "two plants must not share one clause")

    def test_rank_inverted_names_both_totals(self):
        p = _run(CHECKER, "rubric_valid.yaml", "scores_rank_inverted.jsonl")
        self.assertEqual(p.returncode, 2)
        self.assertRegex(p.stderr, r"scored 25 .* at 100")


class Refusal(unittest.TestCase):
    def test_missing_rubric_is_refusal_not_verdict(self):
        p = subprocess.run(
            [sys.executable, str(CHECKER), str(FIX / "nope.yaml"),
             str(FIX / "scores_valid.jsonl")],
            capture_output=True, text=True, cwd=REPO)
        self.assertEqual(p.returncode, 1, p.stderr)
        self.assertIn("REFUSING", p.stderr)


class GateNotTheater(unittest.TestCase):
    def test_neutering_the_ranking_clause_blinds_the_gate(self):
        original = _run(CHECKER, "rubric_valid.yaml", "scores_rank_inverted.jsonl")
        self.assertEqual(original.returncode, 2, "the live gate stopped biting")
        src = CHECKER.read_text(encoding="utf-8")
        neutered = src.replace("gap = totals.get(twin, 0.0) - totals[path]",
                               "gap = 1e9  # plant: ranking clause disabled")
        self.assertNotEqual(neutered, src, "patch site moved; update this test")
        with tempfile.TemporaryDirectory() as td:
            blind = Path(td) / "validate_forge_blind.py"
            blind.write_text(neutered, encoding="utf-8")
            p = subprocess.run(
                [sys.executable, str(blind), str(FIX / "rubric_valid.yaml"),
                 str(FIX / "scores_rank_inverted.jsonl")],
                capture_output=True, text=True, cwd=REPO)
        self.assertEqual(p.returncode, 0,
                         "plant did not blind the gate: the ranking clause is "
                         "not the load-bearing one this suite claims")


class CheckerDiscipline(unittest.TestCase):
    def test_checker_is_stdlib_only_and_write_free(self):
        src = CHECKER.read_text(encoding="utf-8")
        self.assertIsNone(
            re.search(r"^\s*(?:import|from)\s+(?!__future__\b)(?:subprocess|requests|yaml|os)\b",
                      src, re.M),
            "checker may only use the stdlib set it declares (no subprocess/yaml/os)")
        self.assertIsNone(re.search(r"\bopen\([^)]*['\"]w", src),
                          "checker must write nothing")


if __name__ == "__main__":
    unittest.main()
