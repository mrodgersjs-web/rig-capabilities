"""Tests for informative-first round selection and the eval budget.

The claim under test is narrow: a round should spend its evaluations where the
outcome is uncertain, must not spend more than it declared, and must not call an
upgrade a graduation when it broke a check the library had always seen green.
"""

import json
import tempfile
import unittest
from pathlib import Path

from rig_capabilities import selection

REPO = Path(__file__).resolve().parent.parent


def _row(rid, score=50.0, runs=4, passes=2, checks=None, kind="skill"):
    info = selection.informativeness(passes, runs)
    need = (100.0 - score) / 100.0
    return {"id": rid, "kind": kind, "source": "canonical", "score": score,
            "asset": {"id": rid}, "runs": runs, "passes": passes,
            "checks": checks or {}, "informative": round(info, 4),
            "value": round(need * info, 6), "unproven": runs == 0,
            "reason": ("unproven" if runs == 0 else
                       "flaky" if 0 < passes < runs else
                       "always-passes" if passes == runs else "always-fails")}


class _Repo:
    """Only .root is needed by check_history."""

    def __init__(self, root):
        self.root = str(root)


class Informativeness(unittest.TestCase):
    def test_decided_records_lose_information_as_evidence_grows(self):
        """Laplace smoothing keeps a floor: 1/1 looks uncertain, 40/40 does not.

        A strictly-zero score for any unanimous record would be wrong too — a single
        green run is thin evidence — so what must hold is monotonicity and ordering,
        not an exact zero.
        """
        self.assertGreater(selection.informativeness(1, 1),
                           selection.informativeness(10, 10))
        self.assertGreater(selection.informativeness(10, 10),
                           selection.informativeness(40, 40))
        self.assertLess(selection.informativeness(40, 40), 0.1)
        self.assertAlmostEqual(selection.informativeness(0, 0), 1.0, places=6)

    def test_unproven_is_maximally_uncertain_not_passing(self):
        self.assertAlmostEqual(selection.informativeness(0, 0), 1.0, places=3)

    def test_flaky_beats_both_extremes(self):
        self.assertGreater(selection.informativeness(3, 6),
                           selection.informativeness(6, 6))
        self.assertGreater(selection.informativeness(3, 6),
                           selection.informativeness(0, 6))

    def test_range(self):
        for runs in range(0, 30):
            for passes in range(0, runs + 1):
                v = selection.informativeness(passes, runs)
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 1.0 + 1e-9)


class History(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / ".context" / "quality-runs"
        d.mkdir(parents=True)
        (d / "2026-09-01T000000.json").write_text(json.dumps({"rows": [
            {"id": "a", "pass": True, "results": [{"form": "file:x.md", "ok": True}]},
            {"id": "b", "pass": False, "results": [{"form": "grep:y", "ok": False}]}]}))
        (d / "2026-09-02T000000.json").write_text(json.dumps({"rows": [
            {"id": "a", "pass": True, "results": [{"form": "file:x.md", "ok": True}]},
            {"id": "b", "pass": True, "results": [{"form": "grep:y", "ok": True}]}]}))

    def test_counts_per_asset_and_per_check(self):
        h = selection.check_history(_Repo(self.tmp))
        self.assertEqual(h["a"], {"runs": 2, "passes": 2,
                                  "checks": {"file:x.md": {"ok": 2, "runs": 2}}})
        self.assertEqual((h["b"]["runs"], h["b"]["passes"]), (2, 1))

    def test_unreadable_file_is_skipped_not_fatal(self):
        (self.tmp / ".context" / "quality-runs" / "broken.json").write_text("{oops")
        h = selection.check_history(_Repo(self.tmp))
        self.assertIn("a", h)

    def test_missing_dir_is_empty_history(self):
        self.assertEqual(selection.check_history(_Repo(self.tmp / "nope")), {})

    def test_real_repo_history_is_nonempty(self):
        """The estate has 80+ recorded runs; zero here means the path moved."""
        h = selection.check_history(_Repo(REPO))
        self.assertTrue(h, ".context/quality-runs produced no history")
        self.assertTrue(any(v["runs"] >= 2 for v in h.values()))


class Regression(unittest.TestCase):
    def test_always_green_check_going_red_is_a_regression(self):
        row = _row("a", checks={"file:x.md": {"ok": 4, "runs": 4}})
        bad = selection.regressed_checks(row, [{"form": "file:x.md", "ok": False}])
        self.assertEqual(bad, ["file:x.md"])

    def test_new_check_going_red_is_not_a_regression(self):
        row = _row("a", checks={"file:x.md": {"ok": 4, "runs": 4}})
        self.assertEqual(selection.regressed_checks(
            row, [{"form": "grep:new", "ok": False}]), [])

    def test_already_flaky_check_going_red_is_not_a_regression(self):
        row = _row("a", checks={"grep:y": {"ok": 2, "runs": 4}})
        self.assertEqual(selection.regressed_checks(
            row, [{"form": "grep:y", "ok": False}]), [])

    def test_green_run_reports_nothing(self):
        row = _row("a", checks={"file:x.md": {"ok": 4, "runs": 4}})
        self.assertEqual(selection.regressed_checks(
            row, [{"form": "file:x.md", "ok": True}]), [])


class Select(unittest.TestCase):
    def setUp(self):
        self._orig = selection.scored_rows
        selection.scored_rows = lambda repo, lane: [
            _row("always-green", score=10.0, runs=8, passes=8),
            _row("flaky", score=20.0, runs=8, passes=4),
            _row("unproven", score=60.0, runs=0, passes=0),
            _row("always-fails", score=30.0, runs=8, passes=0),
        ]

    def tearDown(self):
        selection.scored_rows = self._orig

    def test_informative_ranks_uncertain_above_decided(self):
        sel = selection.select(_Repo("."), "x", n=4)
        order = [s["id"] for s in sel["selected"]]
        self.assertEqual(order[0], "flaky")
        self.assertNotIn("always-green", order[:1])
        self.assertEqual(sel["strategy"], "informative-first")

    def test_strategies_disagree_on_the_first_pick(self):
        """Weakest-first puts always-green (score 20) on top; informative must not."""
        weakest = selection.select(_Repo("."), "x", n=4, strategy="weakest")
        informative = selection.select(_Repo("."), "x", n=4)
        self.assertEqual(weakest["selected"][0]["id"], "always-green")
        self.assertNotEqual(informative["selected"][0]["id"], "always-green")
        self.assertEqual([s["id"] for s in weakest["selected"]][:1], ["always-green"])

    def test_budget_caps_evaluation_and_defers_the_rest_by_value(self):
        sel = selection.select(_Repo("."), "x", n=4, budget=1)
        self.assertEqual(sel["eval_budget_effective"], 1)
        self.assertEqual([s["id"] for s in sel["selected"]], ["flaky"])
        self.assertTrue(sel["deferred"])
        self.assertNotIn("flaky", [d["id"] for d in sel["deferred"]])
        # deferred keeps its value so the next round can see what it skipped
        self.assertTrue(all("value" in d for d in sel["deferred"]))

    def test_budget_zero_selects_nothing_but_keeps_the_report(self):
        sel = selection.select(_Repo("."), "x", n=4, budget=0)
        self.assertEqual(sel["selected"], [])
        self.assertEqual(len(sel["deferred"]), 4)

    def test_oversized_budget_is_clamped_to_candidates(self):
        sel = selection.select(_Repo("."), "x", n=4, budget=99)
        self.assertEqual(sel["eval_budget_effective"], 4)

    def test_unknown_strategy_is_refused(self):
        with self.assertRaises(ValueError):
            selection.select(_Repo("."), "x", n=2, strategy="vibes")

    def test_rows_by_id_carries_check_history_for_the_gate(self):
        sel = selection.select(_Repo("."), "x", n=4)
        self.assertEqual(sel["rows_by_id"]["flaky"]["runs"], 8)

    def test_unproven_is_labelled_as_unproven(self):
        sel = selection.select(_Repo("."), "x", n=4)
        by = {s["id"]: s for s in sel["selected"]}
        self.assertTrue(by["unproven"]["unproven"])
        self.assertEqual(by["unproven"]["reason"], "unproven")

    def test_a_fully_decided_lane_says_which_ordering_ran(self):
        selection.scored_rows = lambda repo, lane: [
            _row("green-hard", score=10.0, runs=20, passes=20),
            _row("green-easy", score=90.0, runs=20, passes=20),
            _row("dead", score=30.0, runs=20, passes=0),
        ]
        sel = selection.select(_Repo("."), "x", n=3)
        self.assertEqual(sel["fallback"], "no-uncertain-candidates")
        self.assertEqual(sel["uncertain_candidates"], 0)
        # with no uncertainty the honest ordering is weakest-first, by score
        self.assertEqual([s["id"] for s in sel["selected"]],
                         ["green-hard", "dead", "green-easy"])

    def test_one_uncertain_asset_defeats_the_fallback(self):
        selection.scored_rows = lambda repo, lane: [
            _row("green-hard", score=10.0, runs=20, passes=20),
            _row("maybe", score=80.0, runs=4, passes=2),
        ]
        sel = selection.select(_Repo("."), "x", n=2)
        self.assertEqual(sel["fallback"], "")
        self.assertEqual(sel["uncertain_candidates"], 1)
        self.assertEqual(sel["selected"][0]["id"], "maybe")

    def test_explicit_weakest_never_reports_a_fallback(self):
        selection.scored_rows = lambda repo, lane: [
            _row("green", score=10.0, runs=20, passes=20)]
        sel = selection.select(_Repo("."), "x", n=1, strategy="weakest")
        self.assertEqual(sel["fallback"], "")


class RoundSignature(unittest.TestCase):
    def test_run_round_admits_budget_and_strategy(self):
        import inspect

        from rig_capabilities.rounds import run_round
        p = inspect.signature(run_round).parameters
        self.assertIn("budget", p)
        self.assertEqual(p["strategy"].default, "informative")


if __name__ == "__main__":
    unittest.main(verbosity=2)
