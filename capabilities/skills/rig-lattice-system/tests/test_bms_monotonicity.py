"""Planted-failure regression for the BMS failure_cost sign defect (S08).

Before the fix, raw_score() used +failure_cost*0.4, so maximum-consequence
work scored as maximum confidence and routed to A1 (zero-budget, no model in
the decision path). These tests pin the corrected contract: confidence is
non-increasing in failure_cost, and the exact defect case never yields A1.
They FAIL on the pre-fix bytes (bms.py @ HEAD sha ba5749f8...) and must stay
in the permanent suite.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rig_lattice.lattice.bms import compute_bms  # noqa: E402
from rig_lattice.lattice.constants import BMSMode, Level  # noqa: E402


class TestFailureCostSign(unittest.TestCase):
    def test_defect_case_not_a1(self):
        """fc=0.95, rv=0.0, mc=1.0, L1 pre-fix: raw 0.68 + 0.35 -> A1."""
        r = compute_bms(
            failure_cost=0.95, reversibility=0.0, mechanism_clarity=1.0,
            level=Level.L1,
        )
        self.assertIsNot(r.mode, BMSMode.A1)
        self.assertLess(r.confidence, 0.75)

    def test_monotonic_nonincreasing_in_failure_cost(self):
        for rv, mc, lv in ((0.0, 1.0, Level.L1), (0.5, 0.5, Level.L4),
                           (1.0, 0.0, Level.L7), (0.2, 0.8, Level.L3)):
            fcs = [round(0.05 + 0.1 * i, 2) for i in range(10)]
            confs = [
                compute_bms(fc, rv, mc, level=lv).confidence for fc in fcs
            ]
            for lo, hi in zip(fcs, fcs[1:]):
                clo = compute_bms(lo, rv, mc, level=lv).confidence
                chi = compute_bms(hi, rv, mc, level=lv).confidence
                self.assertGreaterEqual(
                    clo, chi, f"confidence rose as failure_cost grew {lo}->{hi}"
                )

    def test_monotonic_nonincreasing_in_past_failure_rate(self):
        base = compute_bms(0.2, 0.8, 0.8, level=Level.L2)
        worst = compute_bms(0.2, 0.8, 0.8, past_failure_rate=1.0, level=Level.L2)
        self.assertGreaterEqual(base.confidence, worst.confidence)

    def test_corrected_weights(self):
        """raw = (1-failure_cost)*0.4 + reversibility*0.3 + mechanism_clarity*0.3."""
        r = compute_bms(failure_cost=0.0, reversibility=0.0,
                        mechanism_clarity=0.0, level=Level.L4)
        self.assertAlmostEqual(r.raw, 0.4, places=9)
        r = compute_bms(failure_cost=1.0, reversibility=0.0,
                        mechanism_clarity=0.0, level=Level.L4)
        self.assertAlmostEqual(r.raw, 0.0, places=9)

    def test_threshold_boundaries_exact(self):
        # 0.75 is A1, 0.45 is A2, 0.25 is A3 (docstring contract, L4 bonus 0.0)
        from rig_lattice.lattice.bms import score_to_mode
        self.assertIs(score_to_mode(0.75), BMSMode.A1)
        self.assertIs(score_to_mode(0.74), BMSMode.A2)
        self.assertIs(score_to_mode(0.45), BMSMode.A2)
        self.assertIs(score_to_mode(0.44), BMSMode.A3)
        self.assertIs(score_to_mode(0.25), BMSMode.A3)
        self.assertIs(score_to_mode(0.24), BMSMode.A4)


if __name__ == "__main__":
    unittest.main()
