"""Keep development and held-out routing cases distinct and non-vacuous."""
import csv
import unittest
from pathlib import Path


CASES = Path(__file__).resolve().parents[1] / "capabilities/evals/mission-router"
KINDS = {"representative", "non_trigger", "adversarial"}


def read_cases(name):
    with (CASES / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


class MissionRouterCasesTests(unittest.TestCase):
    def test_both_matrices_have_distinct_30_case_coverage(self):
        seen = set()
        for name in ("cases.csv", "holdout.csv"):
            rows = read_cases(name)
            self.assertEqual(len(rows), 30, name)
            self.assertEqual({row["__metadata:kind"] for row in rows}, KINDS)
            for row in rows:
                case_id = row["__metadata:case_id"]
                self.assertTrue(case_id)
                self.assertNotIn(case_id, seen)
                seen.add(case_id)
                self.assertTrue(row["intent"].strip())
                self.assertIn(row["expected_status"], {"candidate", "abstain", "any"})
                if row["expected_status"] == "any":
                    self.assertEqual(row["__metadata:kind"], "adversarial")

    def test_held_out_intents_are_not_development_intents(self):
        development = {row["intent"].casefold() for row in read_cases("cases.csv")}
        held_out = {row["intent"].casefold() for row in read_cases("holdout.csv")}
        self.assertFalse(development & held_out)


if __name__ == "__main__":
    unittest.main()
