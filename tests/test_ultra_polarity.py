"""Polarity regression for ultra.judgment.genuinely_different (UltraPlan V2 W04).

The prompt is POSITIVELY framed -- "these two alternatives differ in mechanism" --
so a HIGH noul means genuine divergence and must NOT escalate. The pre-fix rule
(`noul >= 0.85 -> ESCALATE`) punished exactly the good case, and its reason text
("may be cosmetic variants") contradicted its own trigger condition.
"""
from __future__ import annotations

import unittest
from unittest import mock

from rig_capabilities import s1gate


def judgment_answers(gd_noul: float):
    rb = s1gate.load_rubric("ultra.judgment")
    out = {}
    for q, spec in rb.questions.items():
        if q == "genuinely_different":
            out[q] = {"type": "noul", "noul": gd_noul}
        elif spec["type"] == "noul":
            out[q] = {"type": "noul", "noul": 0.95}          # every other positive prompt: healthy
        elif spec["type"] == "score":
            mx = len(spec["criteria"]) - 1
            out[q] = {"type": "score", "score": float(mx - 1), "confidence": 0.9,
                      "probabilities": {str(mx - 1): 0.9}}
        else:
            out[q] = {"type": "choice", "choice": list(spec["criteria"])[0], "confidence": 0.9,
                      "probabilities": {}}
    return out


class TestGenuinelyDifferentPolarity(unittest.TestCase):
    def test_high_noul_genuine_divergence_does_not_escalate(self):
        rb = s1gate.load_rubric("ultra.judgment")
        with mock.patch.object(s1gate, "ask",
                               return_value={"model": "t", "answers": judgment_answers(0.95)}):
            res = s1gate.evaluate(rb, "five options, five mechanisms")
        self.assertNotIn("genuinely_different", " ".join(res.reasons or []),
                         "a genuinely-diverse set must not trip the diversity rule")

    def test_low_noul_cosmetic_set_escalaets(self):
        rb = s1gate.load_rubric("ultra.judgment")
        with mock.patch.object(s1gate, "ask",
                               return_value={"model": "t", "answers": judgment_answers(0.05)}):
            res = s1gate.evaluate(rb, "one option in five fonts")
        self.assertIn("genuinely_different", " ".join(res.reasons or []))
        self.assertEqual(res.verdict, s1gate.ESCALATE)  # advisory pack: BLOCK downgrades, never silence

    def test_boundary_at_threshold_fires(self):
        rb = s1gate.load_rubric("ultra.judgment")
        with mock.patch.object(s1gate, "ask",
                               return_value={"model": "t", "answers": judgment_answers(0.50)}):
            res = s1gate.evaluate(rb, "boundary")
        self.assertIn("genuinely_different", " ".join(res.reasons or []),
                      "the rule is <=, so exactly 0.50 fires")

    def test_rule_direction_matches_prompt_polarity(self):
        """Structural guard: for a positively-framed prompt the rule must be <=,
        never >=. (Negative-framed prompts keep >=; this test only owns this rule.)"""
        rb = s1gate.load_rubric("ultra.judgment")
        rule = next(r for r in rb.rules if r["when"].startswith("genuinely_different"))
        self.assertIn("<=", rule["when"])
        self.assertTrue(rule.get("reason", "").strip(), "an escalated verdict must explain itself")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
