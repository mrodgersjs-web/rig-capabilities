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
        # A shipped `calibrated: true` is only honest when the rule signals it
        # claims carry measured operating points whose hashes verify.
        # (Was: nothing ships calibrated -- pre per-rule era; 2026-09-20.)
        for name, rb in probe.items():
            if not rb.calibrated:
                continue
            entries = (rb.calibration or {}).get("rules") or {}
            self.assertTrue(entries, "%s: calibrated flag with no per-rule entries" % name)
            for r in rb.rules:
                sig = s1gate._rule_signal(r)
                if sig not in entries:
                    continue  # unmeasured rule: advisory, allowed to coexist
                e = entries[sig]
                for field in ("threshold", "train", "holdout", "combined",
                              "labeled_set_sha256", "rule_sha256", "rubric_sha256"):
                    self.assertIn(field, e, "%s: %s certified without %s" % (name, sig, field))
                self.assertTrue(rb.rule_enforces(r, model=e.get("model") or None),
                                "%s: %s hash binding does not verify" % (name, sig))

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

    def test_work_criteria_map_covers_every_rubric_and_rejects_unknown(self):
        root = Path(s1gate.RUBRIC_DIR).parent
        raw = json.loads((root / "work-criteria.json").read_text(encoding="utf-8"))
        self.assertIs(raw["fail_closed"], True)
        self.assertIs(raw["advisory_until_calibrated"], True)
        self.assertEqual(raw["min_noul"], 0.9)
        self.assertEqual(raw["min_confidence"], 0.9)
        self.assertIn("rig-s1gate check", raw["command"])
        kinds = raw["kinds"]
        self.assertNotIn("not-a-kind", kinds)
        names = s1gate.list_rubrics()
        self.assertGreaterEqual(len(names), 71)
        for name in names:
            self.assertEqual(kinds.get(name), name,
                             "shipped rubric %s is not an identity key" % name)
        for kind, target in kinds.items():
            rb = s1gate.load_rubric(target)
            self.assertEqual(rb.name, target, "kind %s points at %s" % (kind, target))
        # The five gap packs are new and unmeasured. They must not enforce.
        for name in ("routine.run", "youtube.scrape", "board.card", "fusion.check", "form.field"):
            self.assertIn(name, names)
            self.assertFalse(s1gate.load_rubric(name).calibrated, "%s must stay advisory" % name)

    def test_owned_packs_reject_noul_at_or_below_090(self):
        # Above 0.9 means 0.90 fails and 0.91 passes.
        owned = (
            "doctrine.surface", "routine.run", "youtube.scrape",
            "board.card", "fusion.check", "form.field",
        )
        for name in owned:
            rb = s1gate.load_rubric(name)
            self.assertGreaterEqual(rb.confidence_floor, 0.90, name)
            noul_rules = [r for r in rb.rules if ".noul <=" in r["when"]]
            self.assertTrue(noul_rules, "%s has no 0.90 noul rule" % name)
            for rule in noul_rules:
                self.assertIn("<= 0.90", rule["when"], rule["when"])
                qname = rule["when"].split(".noul")[0].strip()
                under = {qname: {"type": "noul", "noul": 0.90}}
                above = {qname: {"type": "noul", "noul": 0.91}}
                fail, _ = s1gate.eval_condition(under, rule["when"])
                clear, _ = s1gate.eval_condition(above, rule["when"])
                self.assertIs(fail, True, "%s let 0.90 pass: %s" % (name, rule["when"]))
                self.assertIs(clear, False, "%s blocked 0.91: %s" % (name, rule["when"]))


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
            for i in range(3):
                log.label(log.record(res, subject="code.diff:thin%d@x" % i), "good")
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

    def test_record_refuses_an_empty_subject(self):
        # An unattributable row poisons every aggregate on the table: the
        # logger must refuse it loudly, never default it to NULL or "".
        with tempfile.TemporaryDirectory() as td:
            log = s1gate.DecisionLog(Path(td) / "d.db")
            res = s1gate.GateResult(rubric="r", verdict="PASS", enforced=False,
                                    reasons=["x"], answers={}, model="m",
                                    latency_ms=5, state_sha256="abc")
            for bad in (None, "", "   "):
                with self.assertRaises(ValueError, msg=repr(bad)):
                    log.record(res, subject=bad)
            self.assertEqual(log.counts(), {}, "refused rows must not be written")
            log.close()

    def test_errored_rows_are_quarantined_out_of_the_scoring_path(self):
        with tempfile.TemporaryDirectory() as td:
            log = s1gate.DecisionLog(Path(td) / "d.db")
            base = dict(rubric="r", enforced=True, reasons=["x"],
                        answers={"q": {"type": "noul", "noul": 0.9}}, model="m",
                        latency_ms=5, state_sha256="abc")
            ok = log.record(s1gate.GateResult(verdict="BLOCK", **base), subject="s")
            err = log.record(s1gate.GateResult(verdict="BLOCK", error="TimeoutError: timed out",
                                               **base), subject="e")
            log.label(ok, "good")
            log.label(err, "good")
            self.assertEqual(log.counts("r"), {"BLOCK": 1},
                             "an errored row is a provider failure, not a judgment")
            self.assertEqual([r["id"] for r in log.labelled("r")], [ok])
            row = log.get(err)
            self.assertEqual(row["excluded"], 1)
            self.assertIn("TimeoutError", row["exclusion_reason"])
            # reversible: the flag can be cleared without deleting the row
            log._conn.execute("UPDATE decisions SET excluded=0 WHERE id=?", (err,))
            log._conn.commit()
            self.assertEqual(log.counts("r"), {"BLOCK": 2})
            log.close()


if __name__ == "__main__":
    unittest.main()


class TestImproveAndRank(unittest.TestCase):
    """The loop is exercised with a stub provider and a stub rewriter, so the
    assertions are about the loop's contract, not about any model."""

    def _provider(self, script):
        # script: list of answer dicts returned in order of evaluate() calls
        calls = iter(script)
        return mock.patch.object(s1gate, "ask", side_effect=lambda *a, **k: {"model": "t", "answers": next(calls)})

    def test_improve_stops_when_cleared_and_returns_best(self):
        from rig_capabilities.s1gate_improve import improve
        rb = _rubric(calibrated=False)
        script = [{"bad": {"type": "noul", "noul": 0.9}}, {"bad": {"type": "noul", "noul": 0.1}}]
        seen = []
        def rw(draft, ctx, findings, rubric):
            seen.append(findings); return draft + " [fixed]"
        with self._provider(script):
            res = improve(rb, "draft", rewriter=rw, max_iterations=3)
        self.assertTrue(res.cleared)
        self.assertEqual(res.iterations, 1)
        self.assertEqual(res.best, "draft [fixed]")
        self.assertEqual([t["verdict"] for t in res.trajectory], [s1gate.ESCALATE, s1gate.PASS])
        # 2026-09-20: per-rule enforcement records the VERDICT ACTUALLY ENFORCED.
        # An uncalibrated BLOCK is annotated as ESCALATE everywhere, not just in
        # the verdict field -- a rewriter must never be shown a BLOCK that cannot fire.
        self.assertTrue(seen and seen[0][0].startswith("ESCALATE:"), "rewriter must receive the findings")

    def test_improve_never_returns_a_worse_version(self):
        from rig_capabilities.s1gate_improve import improve
        rb = _rubric(calibrated=False, rules=[
            {"when": "bad.noul >= 0.60", "verdict": "ESCALATE", "reason": "b"},
            {"when": "bad.noul >= 0.90", "verdict": "ESCALATE", "reason": "worse"},
        ])
        script = [{"bad": {"type": "noul", "noul": 0.7}},   # 1 finding
                  {"bad": {"type": "noul", "noul": 0.95}},  # 2 findings: worse
                  {"bad": {"type": "noul", "noul": 0.95}}]
        with self._provider(script):
            res = improve(rb, "v0", rewriter=lambda d, c, f, r: d + "+", max_iterations=2)
        self.assertFalse(res.cleared)
        self.assertEqual(res.best, "v0")
        self.assertIn("budget", res.stopped_because)

    def test_improve_stops_on_unchanged_rewrite(self):
        from rig_capabilities.s1gate_improve import improve
        rb = _rubric(calibrated=False)
        with self._provider([{"bad": {"type": "noul", "noul": 0.9}}] * 3):
            res = improve(rb, "same", rewriter=lambda d, c, f, r: d, max_iterations=3)
        self.assertEqual(res.iterations, 1)
        self.assertIn("unchanged", res.stopped_because)

    def test_improve_on_never_auto_still_escalates(self):
        from rig_capabilities.s1gate_improve import improve
        rb = _rubric(calibrated=False, never_auto=True)
        with self._provider([{"bad": {"type": "noul", "noul": 0.0}}]):
            res = improve(rb, "clean", rewriter=lambda d, c, f, r: d, max_iterations=1)
        self.assertEqual(res.best_verdict, s1gate.ESCALATE)
        self.assertIn("never_auto", res.stopped_because)

    def test_rank_orders_best_first(self):
        from rig_capabilities.s1gate_improve import rank
        rb = _rubric(calibrated=False, rules=[
            {"when": "bad.noul >= 0.30", "verdict": "ESCALATE", "reason": "a"},
            {"when": "bad.noul >= 0.60", "verdict": "ESCALATE", "reason": "b"},
        ])
        script = [{"bad": {"type": "noul", "noul": 0.9}},
                  {"bad": {"type": "noul", "noul": 0.1}},
                  {"bad": {"type": "noul", "noul": 0.4}}]
        with self._provider(script):
            rows = rank(rb, ["worst", "best", "middle"])
        self.assertEqual([r["text"] for r in rows], ["best", "middle", "worst"])
        self.assertEqual([r["tripped"] for r in rows], [0, 1, 2])


class TestAnswerCache(unittest.TestCase):
    """The deterministic answer cache: answers may be reused, verdicts never are."""

    def _log(self, td):
        return s1gate.DecisionLog(Path(td) / "d.db")

    def test_second_identical_call_is_served_from_cache(self):
        body = {"model": "jev-test", "answers": {"bad": {"type": "noul", "noul": 0.01}}}
        with tempfile.TemporaryDirectory() as td:
            log = self._log(td)
            with mock.patch.object(s1gate, "ask", return_value=body) as ask_mock:
                r1 = s1gate.evaluate(_rubric(), "same state", subject="t:1", log=log)
                r2 = s1gate.evaluate(_rubric(), "same state", subject="t:2", log=log)
            self.assertEqual(ask_mock.call_count, 1, "second identical call must not hit the provider")
            self.assertFalse(r1.cache_hit)
            self.assertTrue(r2.cache_hit)
            self.assertEqual(r1.answers, r2.answers)
            self.assertEqual(r2.verdict, s1gate.PASS)
            log.close()

    def test_verdict_is_recomputed_against_current_rules_not_cached(self):
        """Cache the answers noul=0.70 under a 0.60 threshold (BLOCK, calibrated),
        then re-judge the SAME state under a rubric whose threshold rose to 0.99:
        the verdict must flip to PASS without a provider call. If the verdict had
        been cached, hardening a rule could never take effect on cached states."""
        body = {"model": "jev-test", "answers": {"bad": {"type": "noul", "noul": 0.70}}}
        strict = _rubric(rules=[{"when": "bad.noul >= 0.99", "verdict": "BLOCK", "reason": "bad"}])
        with tempfile.TemporaryDirectory() as td:
            log = self._log(td)
            with mock.patch.object(s1gate, "ask", return_value=body) as ask_mock:
                r1 = s1gate.evaluate(_rubric(), "state", subject="t:1", log=log)
                r2 = s1gate.evaluate(strict, "state", subject="t:2", log=log)
            self.assertEqual(r1.verdict, s1gate.BLOCK)
            self.assertEqual(r2.verdict, s1gate.PASS)
            self.assertTrue(r2.cache_hit)
            self.assertEqual(ask_mock.call_count, 1)
            log.close()

    def test_changed_questions_are_a_cache_miss(self):
        body = {"model": "jev-test", "answers": {"bad": {"type": "noul", "noul": 0.01}}}
        other_q = _rubric(questions={"bad": {"type": "noul", "instructions": "DIFFERENT"}})
        with tempfile.TemporaryDirectory() as td:
            log = self._log(td)
            with mock.patch.object(s1gate, "ask", return_value=body) as ask_mock:
                s1gate.evaluate(_rubric(), "state", subject="t:1", log=log)
                r2 = s1gate.evaluate(other_q, "state", subject="t:2", log=log)
            self.assertEqual(ask_mock.call_count, 2,
                             "an edited question set must not reuse old answers")
            self.assertFalse(r2.cache_hit)
            log.close()

    def test_expired_entry_is_a_miss_and_is_pruned(self):
        body = {"model": "jev-test", "answers": {"bad": {"type": "noul", "noul": 0.01}}}
        with tempfile.TemporaryDirectory() as td:
            log = self._log(td)
            with mock.patch.object(s1gate, "ask", return_value=body):
                s1gate.evaluate(_rubric(), "state", subject="t:1", log=log)
            import time as _t
            stale = _t.time() - (s1gate.CACHE_TTL_DAYS + 1) * 86400
            log._conn.execute("UPDATE answer_cache SET created_ts=?", (stale,))
            log._conn.commit()
            with mock.patch.object(s1gate, "ask", return_value=body) as ask_mock:
                r2 = s1gate.evaluate(_rubric(), "state", subject="t:2", log=log)
            self.assertFalse(r2.cache_hit)
            self.assertEqual(ask_mock.call_count, 1)
            log.close()

    def test_provider_failure_is_never_cached(self):
        body = {"model": "jev-test", "answers": {"bad": {"type": "noul", "noul": 0.01}}}
        with tempfile.TemporaryDirectory() as td:
            log = self._log(td)
            with mock.patch.object(s1gate, "ask",
                                   side_effect=[s1gate.ProviderError("down"), body]) as ask_mock:
                r1 = s1gate.evaluate(_rubric(), "state", subject="t:1", log=log)
                self.assertEqual(log.cache_stats()["rubrics"], [],
                                 "a failed call must not seed the cache")
                r2 = s1gate.evaluate(_rubric(), "state", subject="t:2", log=log)
            self.assertEqual(r1.verdict, s1gate.BLOCK)
            self.assertEqual(ask_mock.call_count, 2)
            self.assertFalse(r2.cache_hit)
            log.close()

    def test_cache_disabled_by_env_flag(self):
        body = {"model": "jev-test", "answers": {"bad": {"type": "noul", "noul": 0.01}}}
        with tempfile.TemporaryDirectory() as td:
            log = self._log(td)
            with mock.patch.object(s1gate, "CACHE_ENABLED", False), \
                    mock.patch.object(s1gate, "ask", return_value=body) as ask_mock:
                s1gate.evaluate(_rubric(), "state", subject="t:1", log=log)
                r2 = s1gate.evaluate(_rubric(), "state", subject="t:2", log=log)
            self.assertEqual(ask_mock.call_count, 2)
            self.assertFalse(r2.cache_hit)
            self.assertEqual(log.cache_stats()["rubrics"], [])
            log.close()

    def test_cache_stats_counts_hits(self):
        body = {"model": "jev-test", "answers": {"bad": {"type": "noul", "noul": 0.01}}}
        with tempfile.TemporaryDirectory() as td:
            log = self._log(td)
            with mock.patch.object(s1gate, "ask", return_value=body):
                for i in range(3):
                    s1gate.evaluate(_rubric(), "state", subject="t:%d" % i, log=log)
            st = log.cache_stats("t")
            self.assertEqual(st["rubrics"][0]["entries"], 1)
            self.assertEqual(st["rubrics"][0]["hits"], 2)
            self.assertEqual(st["logged_cache_hits"], 2)
            log.close()


class TestApiKeyEnvFileFallback(unittest.TestCase):
    """SP4 2026-10-10: non-GUI sessions (ssh, launchd) get security rc=36; fall back to a
    mode-600 env file, and refuse one that is group/other readable."""

    def _run(self, mode, body="TYPESAFE_API_KEY=file-fixture\n"):
        done = mock.Mock(stdout="", stderr="", returncode=36)
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "env"; f.write_text(body); f.chmod(mode)
            with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": "", "S1GATE_ENV_FILE": str(f)}, clear=False), \
                    mock.patch.dict("os.environ", {}, clear=False) as e, \
                    mock.patch.object(s1gate.subprocess, "run", return_value=done):
                e.pop("S1GATE_ENV_FILE_DISABLE", None)
                return s1gate._api_key()

    def test_mode_600_env_file_used_when_keychain_rc36(self):
        self.assertEqual(self._run(0o600), "file-fixture")

    def test_export_and_quotes_parsed(self):
        self.assertEqual(self._run(0o600, 'export TYPESAFE_API_KEY="file-fixture"\n'), "file-fixture")

    def test_world_readable_env_file_refused(self):
        with self.assertRaises(s1gate.ProviderError) as cm:
            self._run(0o644)
        self.assertIn("mode 600", str(cm.exception))
        self.assertNotIn("file-fixture", str(cm.exception))


class TestApiKeyReadPath(unittest.TestCase):
    """Credential resolution: the keychain item is referenced BY NAME, its value
    never leaves the resolver, and a `security` failure is diagnosed honestly
    (a bare "no key" masked session-scoped rc=36 failures as missing creds)."""

    def test_env_var_wins_and_no_subprocess_runs(self):
        with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": "env-fixture"}, clear=False), \
                mock.patch.object(s1gate.subprocess, "run") as run:
            self.assertEqual(s1gate._api_key(), "env-fixture")
        run.assert_not_called()

    def test_keychain_item_resolves_when_env_is_empty(self):
        done = mock.Mock(stdout="keychain-fixture\n", stderr="", returncode=0)
        with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": ""}, clear=False), \
                mock.patch.object(s1gate.subprocess, "run", return_value=done) as run:
            self.assertEqual(s1gate._api_key(), "keychain-fixture")
        argv = run.call_args[0][0]
        self.assertEqual(argv[:2], ["security", "find-generic-password"])
        self.assertIn(s1gate.KEYCHAIN_ITEM, argv)
        self.assertIn("-w", argv)

    def test_security_failure_reports_rc_and_stderr(self):
        done = mock.Mock(stdout="",
                         stderr="security: SecKeychainCopyContent: User interaction is not allowed.\n",
                         returncode=36)
        with mock.patch.dict("os.environ", {"TYPESAFE_API_KEY": "", "S1GATE_ENV_FILE_DISABLE": "1"}, clear=False), \
                mock.patch.object(s1gate.subprocess, "run", return_value=done):
            with self.assertRaises(s1gate.ProviderError) as cm:
                s1gate._api_key()
        msg = str(cm.exception)
        self.assertIn("rc=36", msg)
        self.assertIn("User interaction is not allowed", msg)
        self.assertIn(s1gate.KEYCHAIN_ITEM, msg)
