"""Per-rule calibration: certify one rule, bind it to its hashes, and refuse
decorations. Offline and deterministic -- synthetic labelled ledgers only.

Regression coverage for UltraPlan V2 W04:
- whole-rubric flag must no longer launder uncertified rules (per-rule enforcement)
- a signal with no matching rule is REFUSED without writing the file
- certifying is valid only while rubric/rule hashes match (stale = advisory again)
- a threshold that fits train but breaks holdout never ships
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rig_capabilities import s1gate, s1gate_calibrate as cal
from rig_capabilities.s1gate import DecisionLog, GateResult

RUBRIC = {
    "name": "t.calib",
    "stage": "test",
    "lane": "build",
    "description": "test pack",
    "questions": {
        "alpha": {"instructions": "i", "type": "noul"},
        "beta": {"instructions": "b", "type": "noul"},
    },
    "rules": [
        {"when": "alpha.noul >= 0.60", "verdict": "BLOCK", "reason": "a bad"},
        {"when": "beta.noul <= 0.40", "verdict": "BLOCK", "reason": "b bad"},
    ],
}


def _result(rubric, answers, verdict):
    return GateResult(rubric=rubric, verdict=verdict, enforced=False, advisory=True,
                      reasons=[], answers=answers, model="jev-test", latency_ms=1,
                      state_sha256="x")


class CalibrateBase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.rdir = self.tmp / "rubrics"
        self.rdir.mkdir()
        (self.rdir / "t.calib.json").write_text(json.dumps(RUBRIC))
        self.db = self.tmp / "decisions.db"
        self.log = DecisionLog(self.db)

    def tearDown(self):
        self.log.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def seed(self, signal_vals, direction="above"):
        """signal_vals: [(value, label)] for the `alpha` question; beta mirrors alpha
        inversely so both signals exist per row."""
        import json as j
        for i, (v, lab) in enumerate(signal_vals):
            ans = {"alpha": {"type": "noul", "noul": v},
                   "beta": {"type": "noul", "noul": 1 - v}}
            self.log.record(_result("t.calib", ans, "BLOCK"), subject="s%d" % i)
            self.log.label(i + 1, lab)


def separable(n=50):
    """Good rows score low-noul on alpha, bad rows high -- clean separation."""
    out = []
    for i in range(n):
        out.append((0.10 + 0.002 * (i % 10), "good"))
        if len(out) < n:
            out.append((0.90 - 0.002 * (i % 10), "bad"))
    return out[:n]


class TestPerRuleCalibration(CalibrateBase):
    def test_certifies_one_rule_only(self):
        self.seed(separable())
        res = cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                                   db_path=self.db, rubric_dir=self.rdir, write=True)
        self.assertTrue(res["certified"], res["reason"])
        self.assertFalse(res.get("rubric_calibrated"),
                         "beta is uncertified: the pack as a whole cannot be calibrated")
        rb = s1gate.load_rubric("t.calib", self.rdir)
        rules = {s1gate._rule_signal(r): r for r in rb.rules}
        self.assertTrue(rb.rule_enforces(rules["alpha.noul"], model="jev-test"))
        self.assertFalse(rb.rule_enforces(rules["beta.noul"], model="jev-test"))

    def test_unmatched_signal_refused_without_write(self):
        self.seed(separable())
        before = (self.rdir / "t.calib.json").read_bytes()
        with self.assertRaises(ValueError):
            cal.calibrate_rubric("t.calib", ("nosuch", "noul"), db_path=self.db,
                                 rubric_dir=self.rdir, write=True)
        self.assertEqual(before, (self.rdir / "t.calib.json").read_bytes(),
                         "refusal must not write configuration")

    def test_editing_the_rule_voids_certification(self):
        self.seed(separable())
        cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                             db_path=self.db, rubric_dir=self.rdir, write=True)
        p = self.rdir / "t.calib.json"
        raw = json.loads(p.read_text())
        for r in raw["rules"]:
            if r["when"].startswith("alpha.noul"):
                r["reason"] = "silently reworded"  # drift, not calibration
        p.write_text(json.dumps(raw))
        rb = s1gate.load_rubric("t.calib", self.rdir)
        rule = next(r for r in rb.rules if r["when"].startswith("alpha.noul"))
        self.assertFalse(rb.rule_enforces(rule, model="jev-test"),
                         "a hand-edit must drop the rule back to advisory")

    def test_model_switch_voids_certification(self):
        self.seed(separable())
        cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                             db_path=self.db, rubric_dir=self.rdir, write=True)
        rb = s1gate.load_rubric("t.calib", self.rdir)
        rule = next(r for r in rb.rules if r["when"].startswith("alpha.noul"))
        self.assertTrue(rb.rule_enforces(rule, model="jev-test"))
        self.assertFalse(rb.rule_enforces(rule, model="jev-next-year"),
                         "thresholds measured under one judge do not transfer to another")

    def test_in_sample_fit_fails_holdout_and_never_ships(self):
        # The train sweep finds a threshold that flags every train bad and no train
        # good; the stride split parks the two boundary good rows in holdout where
        # the same threshold loses all its recall. In-sample fit, out-of-sample dead.
        vals = [(0.10, "good")] * 20 + [(0.92, "good")] * 5 + [(0.90, "bad")] * 30
        self.seed(vals)
        res = cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                                   max_false_block_rate=0.01,
                                   db_path=self.db, rubric_dir=self.rdir, write=True)
        self.assertFalse(res["certified"], res["reason"])
        raw = json.loads((self.rdir / "t.calib.json").read_text())
        self.assertNotIn("rules", raw.get("calibration") or {},
                         "no certification may be written when holdout fails")

    def test_second_certification_does_not_void_the_first(self):
        self.seed(separable())
        cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                             db_path=self.db, rubric_dir=self.rdir, write=True)
        cal.calibrate_rubric("t.calib", ("beta", "noul"), direction="below",
                             db_path=self.db, rubric_dir=self.rdir, write=True)
        rb = s1gate.load_rubric("t.calib", self.rdir)
        self.assertTrue(rb.calibrated, "both rules certified -> whole pack calibrated")
        for r in rb.rules:
            self.assertTrue(rb.rule_enforces(r, model="jev-test"), r["when"])


class TestPerRuleEnforcement(CalibrateBase):
    def _evaluate(self, alpha_noul):
        answers = {"alpha": {"type": "noul", "noul": alpha_noul},
                   "beta": {"type": "noul", "noul": 0.9}}
        with mock.patch.object(s1gate, "ask", return_value={"model": "jev-test", "answers": answers}):
            return s1gate.evaluate(s1gate.load_rubric("t.calib", self.rdir), "state",
                                   model="jev-test")

    def test_uncertified_rule_downgrades_block_to_annotate(self):
        res = self._evaluate(0.95)
        self.assertEqual(res.verdict, s1gate.ESCALATE)
        self.assertTrue(res.advisory)
        self.assertTrue(any("not calibrated" in r for r in res.reasons))

    def test_certified_rule_keeps_block_teeth(self):
        self.seed(separable())
        cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                             db_path=self.db, rubric_dir=self.rdir, write=True)
        res = self._evaluate(0.99)
        self.assertEqual(res.verdict, s1gate.BLOCK)
        self.assertTrue(res.enforced)

    def test_certified_alpha_does_notlaunder_beta(self):
        self.seed(separable())
        cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                             db_path=self.db, rubric_dir=self.rdir, write=True)
        answers = {"alpha": {"type": "noul", "noul": 0.10},
                   "beta": {"type": "noul", "noul": 0.05}}  # beta trips, alpha clean
        with mock.patch.object(s1gate, "ask", return_value={"model": "jev-test", "answers": answers}):
            res = s1gate.evaluate(s1gate.load_rubric("t.calib", self.rdir), "state")
        self.assertEqual(res.verdict, s1gate.ESCALATE)
        self.assertTrue(res.advisory, "uncertified beta may annotate, never enforce")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
