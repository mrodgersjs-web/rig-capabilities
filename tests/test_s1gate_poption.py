"""Per-option probability signals (`q.p.<option>`) must be calibratable.

Before 2026-09-28 `_rule_signal('risk.p.yes >= 0.5')` returned 'risk.p', so two
rules on one choice question collided and `label_signal` refused the signal:
no binary-choice gate could ever be certified.
"""
import json
import tempfile
import unittest
from pathlib import Path

from rig_capabilities import s1gate
from rig_capabilities.s1gate import DecisionLog, GateResult, _rule_signal, load_rubric
from rig_capabilities.s1gate_calibrate import calibrate_rubric


class TestPOptionSignal(unittest.TestCase):
    def test_rule_signal_keeps_option(self):
        self.assertEqual(_rule_signal({"when": "risk.p.yes >= 0.5"}), "risk.p.yes")
        self.assertEqual(_rule_signal({"when": "risk.p.no <= 0.90"}), "risk.p.no")
        self.assertEqual(_rule_signal({"when": "lane.confidence <= 0.90"}), "lane.confidence")
        self.assertEqual(_rule_signal({"when": "x.noul >= 0.9"}), "x.noul")

    def test_label_and_calibrate_p_option(self):
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            rub = {"name": "t.binary", "stage": "t", "lane": "t", "description": "t",
                   "questions": {"risk": {"type": "choice", "instructions": "yes or no",
                                          "criteria": {"yes": "bad", "no": "fine"}}},
                   "rules": [{"when": "risk.p.yes >= 0.5", "verdict": "BLOCK", "reason": "bad"},
                             {"when": "risk.p.no <= 0.90", "verdict": "ESCALATE", "reason": "unsure"}]}
            (td / "t.binary.json").write_text(json.dumps(rub))
            log = DecisionLog(td / "d.db")
            ids = []
            for i in range(40):
                bad = i % 2 == 0
                py = 0.97 if bad else 0.02
                res = GateResult(rubric="t.binary", verdict="PASS", enforced=False, advisory=True,
                                 reasons=[], answers={"risk": {"type": "choice", "choice": "yes" if bad else "no",
                                                               "confidence": 0.95,
                                                               "probabilities": {"yes": py, "no": 1 - py}}},
                                 model=s1gate.JEV_MODEL, latency_ms=1, state_sha256="%064d" % i,
                                 state_preview="")
                did = log.record(res, "t")
                log.label_signal(did, "risk.p.yes", "bad" if bad else "good", by="suite:test")
                ids.append(did)
            with self.assertRaises(ValueError):
                log.label_signal(ids[0], "risk.p", "bad")
            log.close()
            out = calibrate_rubric("t.binary", ("risk", "p.yes"), direction="above",
                                   db_path=td / "d.db", rubric_dir=td, write=True)
            self.assertTrue(out["certified"], out["reason"])
            rb = load_rubric("t.binary", td)
            rule = next(r for r in rb.rules if _rule_signal(r) == "risk.p.yes")
            self.assertTrue(rb.rule_enforces(rule))
            other = next(r for r in rb.rules if _rule_signal(r) == "risk.p.no")
            self.assertFalse(rb.rule_enforces(other))
            ok, _ = s1gate.eval_condition({"risk": {"probabilities": {"yes": 0.99}}}, rule["when"])
            self.assertTrue(ok)

    def test_enforcement_binds_to_answering_model_not_alias(self):
        """Certified for jev-1.13.0, requested as the alias: must enforce."""
        import rig_capabilities.s1gate as s
        from unittest import mock
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            rub = {"name": "t.bind", "stage": "t", "lane": "t", "description": "t",
                   "questions": {"risk": {"type": "choice", "instructions": "yes or no",
                                          "criteria": {"yes": "bad", "no": "fine"}}},
                   "rules": [{"when": "risk.p.yes >= 0.5", "verdict": "BLOCK", "reason": "bad"}]}
            rb = s.Rubric(**rub)
            rub["calibration"] = {"rules": {"risk.p.yes": {
                "label_scope": "signal", "model": "jev-1.13.0",
                "rule_sha256": s.rule_canonical_sha(rub["rules"][0]),
                "rubric_sha256": s.rubric_canonical_sha(rb)}}}
            (td / "t.bind.json").write_text(json.dumps(rub))
            loaded = load_rubric("t.bind", td)
            body = {"model": "jev-1.13.0", "answers": {"risk": {"type": "choice", "choice": "yes",
                    "confidence": 0.99, "probabilities": {"yes": 0.99, "no": 0.01}}}}
            with mock.patch.object(s, "ask", return_value=body):
                res = s.evaluate(loaded, "rm -rf /")
            self.assertEqual(res.verdict, "BLOCK")
            self.assertTrue(res.enforced, res.reasons)
            body["model"] = "jev-1.14.0"   # version moved: certification voids
            with mock.patch.object(s, "ask", return_value=body):
                res2 = s.evaluate(loaded, "rm -rf /")
            self.assertFalse(res2.enforced)
            self.assertEqual(res2.verdict, "ESCALATE")

    def test_tie_middle_is_opt_in_and_max_margin(self):
        from rig_capabilities.s1gate_calibrate import choose_operating_point, sweep
        pairs = [(0.95, "bad"), (0.9, "bad"), (0.05, "good"), (0.0, "good")]
        pts = sweep(pairs, steps=21, direction="above")
        low = choose_operating_point(pts)
        mid = choose_operating_point(pts, tie="middle")
        self.assertLessEqual(low.threshold, 0.1)          # historical: hugs the good class
        self.assertTrue(0.4 <= mid.threshold <= 0.6, mid.threshold)
        self.assertEqual((mid.recall, mid.false_block_rate), (1.0, 0.0))


    def test_tie_declared_keeps_stated_bar(self):
        from rig_capabilities.s1gate_calibrate import choose_operating_point, sweep
        pairs = [(0.5, "bad"), (0.6, "bad"), (0.97, "good"), (1.0, "good")]
        pts = sweep(pairs, steps=51, direction="below")
        dec = choose_operating_point(pts, tie="declared", declared=0.90)
        self.assertAlmostEqual(dec.threshold, 0.90, delta=0.02)
        self.assertEqual((dec.recall, dec.false_block_rate), (1.0, 0.0))
        low = choose_operating_point(pts)
        self.assertLess(low.threshold, 0.7)     # default would loosen the bar


if __name__ == "__main__":
    unittest.main()
