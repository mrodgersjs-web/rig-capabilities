"""Tests for the RIG System-1 Gate.

These assert expected VALUES, not merely "did not throw". A suite whose only
verb is "it ran" is a dead-button inventory, not a gate.

No network: the provider is stubbed. The live-API evidence lives in the
decision log, not in unit tests.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from rig_capabilities import s1gate
from rig_capabilities.s1gate_calibrate import Point, choose_operating_point, sweep


def _rubric(**over):
    base = dict(
        name="t", stage="verify", lane="build", description="test",
        questions={"bad": {"type": "noul", "instructions": "x"}},
        rules=[{"when": "bad.noul >= 0.60", "verdict": "BLOCK", "reason": "bad"}],
        confidence_floor=0.35, calibrated=True,
    )
    base.update(over)
    return s1gate.Rubric(**base)


class TestConditionEngine(unittest.TestCase):
    def test_noul_above_threshold_is_true(self):
        got, _ = s1gate.eval_condition({"a": {"type": "noul", "noul": 0.92}}, "a.noul >= 0.60")
        self.assertIs(got, True)

    def test_noul_below_threshold_is_false(self):
        got, _ = s1gate.eval_condition({"a": {"type": "noul", "noul": 0.10}}, "a.noul >= 0.60")
        self.assertIs(got, False)

    def test_missing_field_is_undecidable_not_false(self):
        got, note = s1gate.eval_condition({}, "nope.noul >= 0.5")
        self.assertIsNone(got)
        self.assertIn("missing field", note)

    def test_unparseable_rule_is_undecidable(self):
        got, note = s1gate.eval_condition({"a": {"noul": 0.5}}, "this is not a rule")
        self.assertIsNone(got)
        self.assertIn("unparseable", note)

    def test_choice_equality(self):
        ans = {"a": {"type": "choice", "choice": "billing"}}
        self.assertIs(s1gate.eval_condition(ans, "a.choice == billing")[0], True)
        self.assertIs(s1gate.eval_condition(ans, "a.choice == sales")[0], False)

    def test_choice_rejects_ordering_operators(self):
        got, note = s1gate.eval_condition({"a": {"type": "choice", "choice": "x"}}, "a.choice >= 1")
        self.assertIsNone(got)
        self.assertIn("only == and !=", note)

    def test_probability_of_named_option(self):
        ans = {"a": {"type": "choice", "probabilities": {"billing": 0.84}}}
        self.assertIs(s1gate.eval_condition(ans, "a.p.billing >= 0.80")[0], True)

    def test_no_eval_injection(self):
        got, _ = s1gate.eval_condition({"a": {"noul": 1}}, "__import__('os').system('true')")
        self.assertIsNone(got)


class TestVerdicts(unittest.TestCase):
    def _run(self, answers, rubric=None):
        body = {"model": "jev-test", "answers": answers}
        with mock.patch.object(s1gate, "ask", return_value=body):
            return s1gate.evaluate(rubric or _rubric(), "some state")

    def test_clean_artifact_passes(self):
        res = self._run({"bad": {"type": "noul", "noul": 0.01}})
        self.assertEqual(res.verdict, s1gate.PASS)
        self.assertTrue(res.ok)

    def test_tripped_rule_blocks_when_calibrated(self):
        res = self._run({"bad": {"type": "noul", "noul": 0.95}})
        self.assertEqual(res.verdict, s1gate.BLOCK)
        self.assertTrue(res.enforced)
        self.assertFalse(res.ok)

    def test_uncalibrated_rubric_cannot_block(self):
        res = self._run({"bad": {"type": "noul", "noul": 0.95}}, _rubric(calibrated=False))
        self.assertEqual(res.verdict, s1gate.ESCALATE)
        self.assertTrue(res.advisory)
        self.assertFalse(res.enforced)
        self.assertTrue(any("not calibrated" in r for r in res.reasons))

    def test_block_beats_escalate(self):
        rb = _rubric(rules=[
            {"when": "bad.noul >= 0.10", "verdict": "ESCALATE", "reason": "e"},
            {"when": "bad.noul >= 0.60", "verdict": "BLOCK", "reason": "b"},
        ])
        self.assertEqual(self._run({"bad": {"type": "noul", "noul": 0.9}}, rb).verdict, s1gate.BLOCK)

    def test_undecidable_rule_escalates_never_passes(self):
        rb = _rubric(rules=[{"when": "absent.noul >= 0.5", "verdict": "BLOCK", "reason": "x"}])
        res = self._run({"bad": {"type": "noul", "noul": 0.0}}, rb)
        self.assertEqual(res.verdict, s1gate.ESCALATE)

    def test_bimodal_score_below_confidence_floor_escalates(self):
        """The live probe that motivated this: score 1.39, confidence 0.0,
        probability mass split 0.46/0.42 across opposite ends."""
        rb = _rubric(
            questions={"risk": {"type": "score", "instructions": "x", "criteria": ["a", "b", "c", "d"]}},
            rules=[{"when": "risk.score >= 3.0", "verdict": "BLOCK", "reason": "high"}],
        )
        res = self._run({"risk": {"type": "score", "score": 1.39, "confidence": 0.0,
                                  "probabilities": {"0": 0.46, "1": 0.11, "2": 0.01, "3": 0.42}}}, rb)
        self.assertEqual(res.verdict, s1gate.ESCALATE)
        self.assertTrue(any("low confidence" in r for r in res.reasons))

    def test_noul_absence_of_confidence_is_not_zero_confidence(self):
        res = self._run({"bad": {"type": "noul", "noul": 0.01}})
        self.assertEqual(res.verdict, s1gate.PASS)
        self.assertFalse(any("low confidence" in r for r in res.reasons))

    def test_never_auto_downgrades_a_pass(self):
        res = self._run({"bad": {"type": "noul", "noul": 0.0}}, _rubric(never_auto=True))
        self.assertEqual(res.verdict, s1gate.ESCALATE)
        self.assertTrue(any("never_auto" in r for r in res.reasons))

    def test_provider_failure_fails_closed(self):
        with mock.patch.object(s1gate, "ask", side_effect=s1gate.ProviderError("down")):
            res = s1gate.evaluate(_rubric(), "state")
        self.assertEqual(res.verdict, s1gate.BLOCK)
        self.assertTrue(res.enforced)
        self.assertIn("failing closed", res.reasons[0])

    def test_state_is_hashed_not_stored_raw_in_result(self):
        res = self._run({"bad": {"type": "noul", "noul": 0.0}})
        self.assertEqual(len(res.state_sha256), 64)


class TestRubricPacks(unittest.TestCase):
    def test_every_shipped_rubric_loads_and_rules_parse(self):
        names = s1gate.list_rubrics()
        self.assertGreaterEqual(len(names), 13)
        probe = {}
        for name in names:
            rb = s1gate.load_rubric(name)
            for rule in rb.rules:
                m = s1gate._RULE_RE.match(rule["when"])
                self.assertIsNotNone(m, "unparseable rule in %s: %r" % (name, rule["when"]))
                qname = m.group(1)
                self.assertIn(qname, rb.questions,
                              "rule in %s references unknown question %r" % (name, qname))
                self.assertIn(rule["verdict"], (s1gate.BLOCK, s1gate.ESCALATE, s1gate.PASS))
                self.assertTrue(rule.get("reason"), "rule without a reason in %s" % name)
            probe[name] = rb
        # Lane C must be hard-gated regardless of anything else.
        self.assertTrue(probe["nil.jacob"].never_auto)
        # Nothing ships pre-certified.
        self.assertFalse(any(rb.calibrated for rb in probe.values()),
                         "a rubric shipped as calibrated without a measured operating point")

    def test_score_rules_reference_valid_levels(self):
        for name in s1gate.list_rubrics():
            rb = s1gate.load_rubric(name)
            for rule in rb.rules:
                m = s1gate._RULE_RE.match(rule["when"])
                qname, attr = m.group(1), m.group(2)
                q = rb.questions[qname]
                if attr == "score":
                    self.assertEqual(q["type"], "score",
                                     "%s: .score used on a %s question" % (name, q["type"]))
                    top = len(q["criteria"]) - 1
                    thr = float(m.group(4))
                    self.assertLessEqual(thr, top,
                                         "%s: threshold %s above max level %s" % (name, thr, top))
                if attr == "noul":
                    self.assertEqual(q["type"], "noul", "%s: .noul on a %s" % (name, q["type"]))
                if attr.startswith("p."):
                    self.assertIn(q["type"], ("choice", "score"))
                    if q["type"] == "choice":
                        self.assertIn(attr[2:], q["criteria"])
                if attr == "choice":
                    self.assertEqual(q["type"], "choice")
                    val = m.group(4).strip("\"'")
                    self.assertIn(val, q["criteria"],
                                  "%s: rule names option %r not in criteria" % (name, val))


class TestCalibration(unittest.TestCase):
    def test_sweep_counts_confusion_matrix(self):
        pairs = [(0.9, "bad"), (0.8, "bad"), (0.2, "good"), (0.1, "good")]
        pts = sweep(pairs, steps=11, direction="above")
        perfect = [p for p in pts if p.tp == 2 and p.fp == 0]
        self.assertTrue(perfect, "a perfectly separable set should yield a clean threshold")
        self.assertEqual(perfect[0].false_block_rate, 0.0)
        self.assertEqual(perfect[0].recall, 1.0)

    def test_false_block_ceiling_is_respected(self):
        pts = [
            Point(0.3, tp=10, fp=8, tn=2, fn=0),    # catches everything, blocks 80% of good work
            Point(0.7, tp=6, fp=0, tn=10, fn=4),    # clean
        ]
        chosen = choose_operating_point(pts, max_false_block_rate=0.05, min_recall=0.5)
        self.assertIsNotNone(chosen)
        self.assertEqual(chosen.threshold, 0.7)

    def test_no_qualifying_threshold_returns_none(self):
        pts = [Point(0.5, tp=5, fp=9, tn=1, fn=5)]
        self.assertIsNone(choose_operating_point(pts, max_false_block_rate=0.05, min_recall=0.5))

    def test_refuses_to_certify_on_thin_data(self):
        from rig_capabilities.s1gate_calibrate import calibrate_rubric
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "d.db"
            log = s1gate.DecisionLog(db)
            res = s1gate.GateResult(rubric="code.diff", verdict="PASS", enforced=False,
                                    reasons=[], answers={"weakened_test": {"type": "noul", "noul": 0.1}},
                                    model="t", latency_ms=1, advisory=True, state_sha256="x")
            for _ in range(3):
                log.label(log.record(res), "good")
            log.close()
            out = calibrate_rubric("code.diff", ("weakened_test", "noul"), db_path=db)
        self.assertFalse(out["certified"])
        self.assertIn("need >=", out["reason"])


class TestDecisionLog(unittest.TestCase):
    def test_record_and_label_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            log = s1gate.DecisionLog(Path(td) / "d.db")
            res = s1gate.GateResult(rubric="r", verdict="BLOCK", enforced=True, reasons=["x"],
                                    answers={"q": {"type": "noul", "noul": 0.9}}, model="m",
                                    latency_ms=5, state_sha256="abc")
            did = log.record(res, subject="s")
            log.label(did, "bad")
            rows = log.labelled("r")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["label"], "bad")
            self.assertEqual(json.loads(rows[0]["answers_json"])["q"]["noul"], 0.9)
            self.assertEqual(log.counts("r"), {"BLOCK": 1})
            log.close()


if __name__ == "__main__":
    unittest.main()
