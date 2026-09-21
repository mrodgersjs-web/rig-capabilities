import unittest
from rig_capabilities.ultra_learn import evaluate, schedule, MIN_TRIALS

class TestOutcomes(unittest.TestCase):
    def test_thin_evidence_cannot_conclude_either_way(self):
        r = evaluate({"wins": 5, "trials": 30}, {"wins": 1, "trials": 4})
        self.assertEqual(r["outcome"], "insufficient_evidence")

    def test_no_gain_is_no_change_not_a_rejection(self):
        r = evaluate({"wins": 15, "trials": 30}, {"wins": 16, "trials": 30})
        self.assertEqual(r["outcome"], "no_change")   # +0.033 <= 0.05 margin

    def test_worse_candidate_is_rejected_with_gap(self):
        r = evaluate({"wins": 15, "trials": 30}, {"wins": 9, "trials": 30})
        self.assertEqual(r["outcome"], "candidate_rejected")
        self.assertAlmostEqual(r["gap"], 0.2)

    def test_clear_win_becomes_promotion_candidate_never_auto_adopted(self):
        r = evaluate({"wins": 12, "trials": 30}, {"wins": 21, "trials": 30})
        self.assertEqual(r["outcome"], "promotion_candidate")
        self.assertEqual(r.get("adopt"), "human-only")

    def test_schedule_is_sorted_deduped_and_ignores_nonpositive_horizons(self):
        s = schedule(1000.0, horizons=(30, 7, 30, 0, -5))
        self.assertEqual(s, [1000 + 7 * 86400, 1000 + 30 * 86400])

if __name__ == "__main__":
    unittest.main()
