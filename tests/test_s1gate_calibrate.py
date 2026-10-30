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

from rig_capabilities import s1gate, s1gate_bridge, s1gate_calibrate as cal
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
            self.log.label_signal(i + 1, "alpha.noul", lab)
            self.log.label_signal(i + 1, "beta.noul", lab)


def separable(n=50):
    """Good rows score low-noul on alpha, bad rows high -- clean separation."""
    out = []
    for i in range(n):
        out.append((0.10 + 0.002 * (i % 10), "good"))
        if len(out) < n:
            out.append((0.90 - 0.002 * (i % 10), "bad"))
    return out[:n]


class TestPerRuleCalibration(CalibrateBase):
    def test_calibration_hash_binds_signal_value_model_and_provenance(self):
        row = {"id": 1, "rubric": "t.calib", "state_sha256": "state",
               "answers_json": json.dumps({"alpha": {"noul": 0.1}}),
               "signal_label": "good", "model": "jev-one",
               "signal_labelled_by": "construction", "signal_labelled_at": 1.0}
        base = cal._labeled_hash([row], "alpha.noul")
        for change in (
            {"answers_json": json.dumps({"alpha": {"noul": 0.9}})},
            {"model": "jev-two"},
            {"signal_labelled_by": "mcp-agent"},
            {"signal_label": "bad"},
        ):
            self.assertNotEqual(base, cal._labeled_hash([{**row, **change}], "alpha.noul"))

    def test_signal_label_requires_a_real_answer(self):
        did = self.log.record(_result("t.calib", {"alpha": {"noul": 0.8}}, "BLOCK"), subject="s1")
        with self.assertRaisesRegex(ValueError, "no answer"):
            self.log.label_signal(did, "beta.noul", "bad")
        with self.assertRaisesRegex(ValueError, "question.attr"):
            self.log.label_signal(did, "beta", "bad")
        with self.assertRaisesRegex(ValueError, "decision not found"):
            self.log.label_signal(did + 1, "alpha.noul", "bad")

    def test_mcp_agent_labels_are_not_calibration_ground_truth(self):
        for i, (v, lab) in enumerate(separable()):
            ans = {"alpha": {"type": "noul", "noul": v},
                   "beta": {"type": "noul", "noul": 1 - v}}
            did = self.log.record(_result("t.calib", ans, "BLOCK"), subject="m%d" % i)
            self.log.label_signal(did, "alpha.noul", lab, by="mcp-agent")
        res = cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                                   db_path=self.db, rubric_dir=self.rdir, write=True)
        self.assertEqual(res["n_labelled"], 0)
        self.assertFalse(res["certified"])

    def test_multi_question_calibration_rejects_global_labels(self):
        for i, (v, lab) in enumerate(separable()):
            ans = {"alpha": {"type": "noul", "noul": v},
                   "beta": {"type": "noul", "noul": 1 - v}}
            did = self.log.record(_result("t.calib", ans, "BLOCK"), subject="g%d" % i)
            self.log.label(did, lab)
        res = cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                                   db_path=self.db, rubric_dir=self.rdir, write=True)
        self.assertFalse(res["certified"])
        self.assertEqual(res["n_labelled"], 0)
        self.assertEqual(res["label_scope"], "signal")

    def test_signal_labels_do_not_contaminate_another_question(self):
        self.seed(separable())
        for did in range(1, 51):
            self.log.label_signal(did, "beta.noul", "bad" if did % 2 else "good")
        alpha = cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                                     db_path=self.db, rubric_dir=self.rdir)
        self.assertFalse(alpha["certified"])  # dry run never certifies
        self.assertGreaterEqual(alpha["holdout"]["recall"], 0.5)
        self.assertEqual(self.log.labelled_signal("t.calib", "alpha.noul")[0]["signal_label"], "good")
        self.assertEqual(self.log.labelled_signal("t.calib", "beta.noul")[0]["signal_label"], "bad")

    def test_prefix_collision_cannot_certify_or_rewrite_another_signal(self):
        path = self.rdir / "t.calib.json"
        raw = json.loads(path.read_text())
        raw["rules"] = [{"when": "alpha.noulty >= 0.60", "verdict": "BLOCK", "reason": "other"}]
        path.write_text(json.dumps(raw))
        before = path.read_bytes()
        self.seed(separable())
        with self.assertRaisesRegex(ValueError, "0 rules match"):
            cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                                 db_path=self.db, rubric_dir=self.rdir, write=True)
        self.assertEqual(path.read_bytes(), before)

    def test_mixed_models_cannot_certify_unseen_model(self):
        for i, (v, lab) in enumerate(separable()):
            ans = {"alpha": {"type": "noul", "noul": v},
                   "beta": {"type": "noul", "noul": 1 - v}}
            result = _result("t.calib", ans, "BLOCK")
            result.model = "jev-one" if i % 2 else "jev-two"
            did = self.log.record(result, subject="m%d" % i)
            self.log.label_signal(did, "alpha.noul", lab)
        res = cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                                   db_path=self.db, rubric_dir=self.rdir, write=True)
        self.assertFalse(res["certified"])
        self.assertIn("mixed", res["reason"])
        self.assertFalse(s1gate.load_rubric("t.calib", self.rdir).rule_enforces(
            RUBRIC["rules"][0], model="unseen-model"))

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

    def test_legacy_multi_question_certificate_is_advisory(self):
        self.seed(separable())
        cal.calibrate_rubric("t.calib", ("alpha", "noul"), direction="above",
                             db_path=self.db, rubric_dir=self.rdir, write=True)
        path = self.rdir / "t.calib.json"
        raw = json.loads(path.read_text())
        raw["calibration"]["rules"]["alpha.noul"].pop("label_scope")
        path.write_text(json.dumps(raw))
        rb = s1gate.load_rubric("t.calib", self.rdir)
        self.assertFalse(rb.enforcing)
        with mock.patch.object(s1gate, "list_rubrics", return_value=["t.calib"]), \
             mock.patch.object(s1gate, "load_rubric", return_value=rb):
            listing = s1gate_bridge._list({})
            detail = s1gate_bridge._show({"rubric": "t.calib"})
        self.assertEqual(listing["rubrics"][0]["mode"], "advisory")
        self.assertEqual(listing["enforcing"], [])
        self.assertFalse(detail["enforcing"])
        self.assertEqual(detail["mode"], "advisory")
        res = self._evaluate(0.99)
        self.assertEqual(res.verdict, s1gate.ESCALATE)
        self.assertTrue(res.advisory)

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
