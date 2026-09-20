"""Offline tests for the ULTRA routing contracts.

These assert ROUTING OUTCOMES, not "it ran". Every Jev answer here is a
fixture: nothing in this file proves semantic calibration or live-provider
behaviour, only that a verdict goes to the right place and that the absence of
a verdict never looks like progress.
"""
from __future__ import annotations

import unittest
from unittest import mock

from rig_capabilities import s1gate, ultra_gates as ug, ultra_plan as up


def noul(p):
    return {"type": "noul", "noul": p}


def score(v, conf=0.8, levels=None):
    probs = {str(i): (v if i == int(v) else 0.0) for i in range(len(levels or [0, 1, 2, 3]))}
    return {"type": "score", "score": v, "confidence": conf, "probabilities": probs}


def choice(c, conf=0.8):
    return {"type": "choice", "choice": c, "confidence": conf, "probabilities": {c: conf}}


class FakeResult:
    def __init__(self, verdict, advisory=True, enforced=False, answers=None, reasons=None, error=None):
        self.verdict, self.advisory, self.enforced = verdict, advisory, enforced
        self.answers = answers or {}
        self.reasons = reasons or []
        self.error = error
        self.decision_id = 123


def fake_evaluator(verdict, answers=None, advisory=True, enforced=False, reasons=None, error=None):
    def _e(rb, state, **kw):
        return FakeResult(verdict, advisory, enforced, answers, reasons, error)
    return _e


GOOD_FACTS = {
    "plan.dq_before_build": {
        "alternatives": [{"name": n, "mechanism": "m" + str(i)} for i, n in
                         enumerate(["boring", "inverted", "cross-domain", "buy-not-build", "wait"])],
        "reference_class": "governed AI studios, first 12 months to first revenue",
        "base_rate": 0.28, "base_rate_source": "measured 2026-09", "n_in_class": 41, "intent": "x"},
    "questioning.card_before_ask": {"card_options": ["a", "b"], "card_recommendation": "a",
                                    "question_text": "which buyer?"},
    "research.citation_before_cite": {"citation_url": "https://x.dev/a", "citation_fetched_at": "2026-09-18",
                                      "citation_live": True, "claim_text": "3-13%", "source_text": "3-13% ..."},
    "forecast.forecast_before_average": {"forecast_text": "p=0.6 because ...", "forecast_count": 5,
                                         "forecast_family_count": 3},
    "execution.slice_before_integrate": {"diff_text": "diff", "claims_text": "claims", "lease_holder": "w1",
                                         "writer_family": "a", "verifier_family": "b"},
    "execution.tripwire_before_next_wave": {"tripwire_text": "CAC > 3x", "fresh_evidence_text": "CAC 1.2x"},
    "proof.gate_before_register": {"done_test_text": "runs", "done_test_cmds": ["cmd: true"],
                                   "planted_failure_receipt": "receipt-1"},
    "proof.seal_before_forecast_resolve": {"chain_verified": True, "planted_failure_receipt": "r",
                                           "artifact_text": "bytes"},
    "learning.variant_before_adopt": {"variant_text": "v", "live_text": "l", "score_before": 0.6,
                                      "score_after": 0.8, "holdout_split_id": "h3"},
    "outward.gate_d": {"approval_quote": "approve the repost", "action_text": "repost", "target": "li/123",
                       "human_approved_this_action": True},
}


class TestPackRegistry(unittest.TestCase):
    STUDIOS = {"questioning", "research", "forecasting", "judgment", "execution", "proof", "learning"}

    def test_seven_studio_packs_registered_and_namespaced(self):
        names = s1gate.list_rubrics()
        ultra = [n for n in names if n.startswith("ultra.")]
        self.assertEqual(len(ultra), 7, ultra)
        for n in ultra:
            rb = s1gate.load_rubric(n)
            self.assertEqual(rb.lane, "build")
            self.assertFalse(rb.calibrated, "%s must ship advisory" % n)

    def test_studio_coverage(self):
        covered = {g.studio for g in ug.GATES.values()}
        self.assertTrue(self.STUDIOS <= covered, self.STUDIOS - covered)

    def test_every_gate_pack_exists(self):
        for gid, g in ug.GATES.items():
            if g.pack:
                s1gate.load_rubric(g.pack)  # raises if absent
            else:
                self.assertTrue(g.requires_human, "%s has no pack and no human authority" % gid)

    def test_question_shapes_respect_provider_limits(self):
        for name in s1gate.list_rubrics():
            if not name.startswith("ultra."):
                continue
            for q, spec in s1gate.load_rubric(name).questions.items():
                t = spec["type"]
                if t == "noul":
                    self.assertNotIn("criteria", spec, "%s.%s: noul takes no criteria" % (name, q))
                if t == "score":
                    self.assertLessEqual(len(spec["criteria"]), 11, "%s.%s exceeds 11 levels" % (name, q))
                if t == "choice":
                    self.assertIsInstance(spec["criteria"], dict, "%s.%s: choice criteria must be slug -> description" % (name, q))
                    self.assertLessEqual(len(spec["criteria"]), 255, name + "." + q)
                    for slug in spec["criteria"]:
                        self.assertRegex(slug, r"^[\w.-]+$", "%s.%s: %r is not a rule-addressable slug" % (name, q, slug))

    def test_rules_parse_and_are_answerable(self):
        """A rule whose left-hand side cannot resolve is a dead gate, not a gate."""
        for name in s1gate.list_rubrics():
            if not name.startswith("ultra."):
                continue
            rb = s1gate.load_rubric(name)
            answers = {}
            for q, spec in rb.questions.items():
                if spec["type"] == "noul":
                    answers[q] = noul(0.5)
                elif spec["type"] == "score":
                    answers[q] = {"type": "score", "score": 2.0, "confidence": 0.9,
                                  "probabilities": {str(i): 0.25 for i in range(len(spec["criteria"]))}}
                else:
                    opts = list(spec["criteria"])
                    answers[q] = {"type": "choice", "choice": opts[0], "confidence": 0.9,
                                  "probabilities": {o: 1.0 / len(opts) for o in opts}}
            for rule in rb.rules:
                got, note = s1gate.eval_condition(answers, rule["when"])
                self.assertIsNotNone(got, "%s: rule %r -> %s" % (name, rule["when"], note))


class TestRouterOffline(unittest.TestCase):
    def test_offline_is_not_a_cleared_gate(self):
        for gid, facts in GOOD_FACTS.items():
            got = ug.route(gid, "state", facts)
            self.assertEqual(got["route"], ug.Route.OFFLINE_CODE_ONLY, gid)
            self.assertFalse(got["cleared"], gid)
            self.assertFalse(got["advance"], gid)

    def test_unknown_gate_blocks_and_asks_for_a_human(self):
        got = ug.route("nope.not_real", "x", {})
        self.assertEqual(got["route"], ug.Route.BLOCKED_UNKNOWN)
        self.assertFalse(got["advance"])
        self.assertTrue(got["human_required"])

    def test_missing_required_facts_never_advance(self):
        got = ug.route("research.citation_before_cite", "state", {}, live=False)
        self.assertEqual(got["route"], ug.Route.REWORK)
        self.assertTrue(got["jev_skipped"])
        self.assertIn("missing required facts", " ".join(got["reasons"]))

    def test_five_headings_over_one_mechanism_is_not_divergence(self):
        got = ug.route("plan.dq_before_build", "state", {
            "alternatives": [{"name": "price " + str(i), "mechanism": "retainer"} for i in range(5)],
            "reference_class": "governed AI studios, first 12 months", "base_rate": 0.3,
            "base_rate_source": "measured", "n_in_class": 41}, live=True,
            evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got["route"], ug.Route.REWORK)
        self.assertIn("need 5", " ".join(got["reasons"]))

    def test_an_estimate_without_a_reference_class_is_refused(self):
        got = ug.route("plan.dq_before_build", "state", {
            "alternatives": [{"name": n, "mechanism": "m" + str(i)} for i, n in enumerate("abcde")],
            "reference_class": "we think it will go fine", "base_rate": 0.7,
            "base_rate_source": "vibes"}, live=True, evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got["route"], ug.Route.REWORK)

    def test_a_thin_reference_class_is_refused(self):
        base = {"alternatives": [{"name": n, "mechanism": "m" + str(i)} for i, n in enumerate("abcde")],
                "reference_class": "the two studios I know personally", "base_rate": 0.5,
                "base_rate_source": "conversation with 2 founders"}
        for n, expect_refused in ((2, True), (4, True), (5, False), (41, False)):
            got = ug.route("plan.dq_before_build", "state", dict(base, n_in_class=n),
                           live=True, evaluator=fake_evaluator(s1gate.PASS))
            self.assertEqual(got["route"] == ug.Route.REWORK, expect_refused, "n_in_class=%d" % n)

    def test_a_real_source_containing_a_filler_word_still_counts(self):
        base = {"alternatives": [{"name": n, "mechanism": "m" + str(i)} for i, n in enumerate("abcde")],
                "reference_class": "governed AI studios, first 12 months", "base_rate": 0.3,
                "base_rate_source": "https://example.com/me-study-2026 (their own vibes-adjacent survey)",
                "n_in_class": 30}
        self.assertTrue(up.outside_view(base)["ok"])

    def test_a_base_rate_with_no_source_is_refused(self):
        got = ug.route("plan.dq_before_build", "state", {
            "alternatives": [{"name": n, "mechanism": "m" + str(i)} for i, n in enumerate("abcde")],
            "reference_class": "governed AI studios, first 12 months", "base_rate": 0.3},
            live=True, evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got["route"], ug.Route.REWORK)
        self.assertIn("missing required facts", " ".join(got["reasons"]))

    def test_code_check_failure_short_circuits_before_jev(self):
        called = []

        def spy(*a, **k):
            called.append(1)
            return FakeResult(s1gate.PASS)

        got = ug.route("proof.gate_before_register", "state",
                       {"done_test_text": "file exists", "done_test_cmds": ["test -f x"],
                        "planted_failure_receipt": "r"}, live=True, evaluator=spy)
        self.assertEqual(got["route"], ug.Route.REWORK)
        self.assertEqual(called, [], "Jev was called after a deterministic failure")
        self.assertTrue(any("no runnable assertion" in c["note"] for c in got["code_checks"]))

    def test_undecidable_code_check_escalates_not_passes(self):
        got = ug.route("research.citation_before_cite", "state",
                       {"citation_url": "https://x.dev/a", "citation_fetched_at": "2026-09-18",
                        "claim_text": "c", "source_text": "s"}, live=True,
                       evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got["route"], ug.Route.ESCALATE_REVIEW)
        self.assertTrue(got["jev_skipped"])

    def test_named_but_never_run_assertion_no_longer_passes(self):
        """A cmd: string whose command FAILS at execution time is not a done-test.
        Before this check executed, any string starting with 'cmd:' cleared it."""
        got = ug.route("proof.gate_before_register", "state",
                       {"done_test_text": "x", "done_test_cmds": ["cmd: exit 3"],
                        "planted_failure_receipt": "r"}, live=True,
                       evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got["route"], ug.Route.REWORK)
        self.assertTrue(any("exited 3" in c["note"] for c in got["code_checks"]))

    def test_executing_assertion_advances(self):
        got = ug.route("proof.gate_before_register", "state",
                       {"done_test_text": "x", "done_test_cmds": ["cmd: true"],
                        "planted_failure_receipt": "r"}, live=True,
                       evaluator=fake_evaluator(s1gate.PASS, {"done_test_is_vacuous": noul(0.05)}))
        self.assertTrue(got["cleared"])
        self.assertTrue(any("EXECUTED" in c["note"] for c in got["code_checks"]))

    def test_timeout_is_a_failure_not_an_absolution(self):
        got = ug.route("proof.gate_before_register", "state",
                       {"done_test_text": "x", "done_test_cmds": ["cmd: sleep 5"],
                        "done_test_timeout": 1, "planted_failure_receipt": "r"}, live=True,
                       evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got["route"], ug.Route.REWORK)
        self.assertTrue(any("TIMEOUT" in c["note"] for c in got["code_checks"]))


class TestRouterWithVerdicts(unittest.TestCase):
    def test_pass_advances(self):
        got = ug.route("research.citation_before_cite", "state", GOOD_FACTS["research.citation_before_cite"],
                       live=True, evaluator=fake_evaluator(s1gate.PASS, {"claim_supported": noul(0.95)}))
        self.assertEqual(got["route"], ug.Route.ADVANCE)
        self.assertTrue(got["cleared"])
        self.assertIn("claim_supported.noul=0.95", " ".join(got["reasons"]))

    def test_advisory_block_cannot_halt_a_quality_gate(self):
        got = ug.route("research.citation_before_cite", "state", GOOD_FACTS["research.citation_before_cite"],
                       live=True, evaluator=fake_evaluator(s1gate.BLOCK, advisory=True, enforced=False,
                                                           reasons=["claim_supported low"]))
        self.assertEqual(got["route"], ug.Route.ANNOTATE_ADVANCE)
        self.assertIn("advisory only", " ".join(got["reasons"]))

    def test_calibrated_block_sends_rework(self):
        got = ug.route("research.citation_before_cite", "state", GOOD_FACTS["research.citation_before_cite"],
                       live=True, evaluator=fake_evaluator(s1gate.BLOCK, advisory=False, enforced=True))
        self.assertEqual(got["route"], ug.Route.REWORK)

    def test_kill_switch_gate_escalates_even_while_advisory(self):
        got = ug.route("execution.tripwire_before_next_wave", "state",
                       GOOD_FACTS["execution.tripwire_before_next_wave"], live=True,
                       evaluator=fake_evaluator(s1gate.ESCALATE, advisory=True))
        self.assertEqual(got["route"], ug.Route.ESCALATE_REVIEW)
        self.assertFalse(got["advance"])

    def test_undecidable_jev_rule_never_advances_while_advisory(self):
        got = ug.route("forecast.forecast_before_average", "state",
                       GOOD_FACTS["forecast.forecast_before_average"], live=True,
                       evaluator=fake_evaluator(s1gate.ESCALATE, advisory=True,
                                                reasons=["rule 'absent.noul >= 0.5' undecidable (missing field)"]))
        self.assertEqual(got["route"], ug.Route.ESCALATE_REVIEW)

    def test_provider_error_halts_even_for_an_advisory_pack(self):
        """Real s1gate.evaluate, real fail-closed path, mocked transport."""
        with mock.patch.object(s1gate, "ask", side_effect=s1gate.ProviderError("HTTP 402: credit balance too low")):
            got = ug.route("learning.variant_before_adopt", "state", GOOD_FACTS["learning.variant_before_adopt"],
                           live=True, evaluator=s1gate.evaluate)
        self.assertEqual(got["route"], ug.Route.HALT_FAILCLOSED)
        self.assertFalse(got["advance"])
        self.assertTrue(got["enforced"], "fail-closed is enforcement, not advice")

    def test_malformed_answer_escalates(self):
        with mock.patch.object(s1gate, "ask", return_value={"model": "jev-test", "answers": {}}):
            got = ug.route("proof.gate_before_register", "state", GOOD_FACTS["proof.gate_before_register"],
                           live=True, evaluator=s1gate.evaluate)
        self.assertEqual(got["route"], ug.Route.ESCALATE_REVIEW)


class TestHumanAuthority(unittest.TestCase):
    def test_clean_pass_on_a_card_still_goes_to_the_human(self):
        got = ug.route("questioning.card_before_ask", "state", GOOD_FACTS["questioning.card_before_ask"],
                       live=True, evaluator=fake_evaluator(s1gate.PASS, {"is_decision": noul(0.99)}))
        self.assertEqual(got["route"], ug.Route.HUMAN_CARD)
        self.assertTrue(got["human_required"])
        self.assertFalse(got["advance"])

    def test_gate_d_has_no_pack_and_still_needs_a_quote(self):
        self.assertIsNone(ug.GATES["outward.gate_d"].pack)
        got = ug.route("outward.gate_d", "post the thing", {"action_text": "post", "target": "li/1"},
                       live=True, evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got["route"], ug.Route.REWORK)
        got2 = ug.route("outward.gate_d", "post the thing", GOOD_FACTS["outward.gate_d"],
                        live=True, evaluator=fake_evaluator(s1gate.PASS))
        self.assertEqual(got2["route"], ug.Route.HUMAN_CARD)
        self.assertFalse(got2["advance"], "no machine route may clear an outward action")


class TestReasonStringsAndConfidence(unittest.TestCase):
    def test_noul_reasons_never_carry_a_confidence_field(self):
        lines = ug._reason_lines({"a": noul(0.42), "b": score(2.0), "c": choice("HIGH")})
        joined = " ".join(lines)
        self.assertIn("a.noul=0.42", joined)
        self.assertNotIn("a.noul=0.42 conf", joined)
        self.assertIn("conf=0.8", joined)

    def test_bimodal_score_below_floor_escalates_via_real_engine(self):
        rb = s1gate.load_rubric("ultra.judgment")
        answers = {q: (noul(0.9) if s["type"] == "noul" else
                       {"type": "score", "score": 1.39, "confidence": 0.0,
                        "probabilities": {"0": 0.46, "4": 0.42}})
                   for q, s in rb.questions.items()}
        with mock.patch.object(s1gate, "ask", return_value={"model": "jev-test", "answers": answers}):
            res = s1gate.evaluate(rb, "state")
        self.assertEqual(res.verdict, s1gate.ESCALATE)
        self.assertTrue(any("low confidence" in r for r in res.reasons))
        got = ug.route("plan.dq_before_build", "state", GOOD_FACTS["plan.dq_before_build"], live=True,
                       evaluator=s1gate.evaluate)
        self.assertEqual(got["route"], ug.Route.ANNOTATE_ADVANCE)  # advisory: annotate, do not halt


class TestDerivedMetrics(unittest.TestCase):
    def test_coverage_counts_a_missing_class_as_missing(self):
        counts = {c: 3 for c in ug.ANGLE_CLASSES if c != "exit/kill"}
        got = ug.coverage(counts)
        self.assertEqual(got["missing"], ["exit_kill"])
        self.assertEqual(got["missing_readable"], ["exit/kill"])
        self.assertAlmostEqual(got["coverage"], 13 / 14.0, places=4)

    def test_labels_and_slugs_are_the_same_class(self):
        """A stage tagging with the pack's slug and a human writing the readable
        label must not produce two different coverage numbers."""
        by_label = ug.coverage({c: 2 for c in ug.ANGLE_CLASSES})
        by_slug = ug.coverage({c: 2 for c in ug.angle_slugs()})
        self.assertEqual(by_label["coverage"], by_slug["coverage"])
        self.assertEqual(by_label["missing"], by_slug["missing"])
        self.assertEqual(by_label["answered"], by_slug["answered"])
        self.assertEqual(by_label["coverage"], 1.0)

    def test_an_unknown_class_is_reported_not_credited(self):
        got = ug.coverage({"customer/job": 3, "vibes": 99})
        self.assertIn("vibes", got["unknown_classes"])
        self.assertLess(got["coverage"], 0.2)

    def test_a_non_numeric_count_is_refused_not_zeroed(self):
        got = ug.coverage({"customer/job": "three"})
        self.assertIsNone(got["coverage"])
        self.assertIn("not a number", got["insufficient_input"])

    def test_information_is_the_weakest_link_not_the_mean(self):
        vals = {c: 0.95 for c in ug.ANGLE_CLASSES}
        vals["legal/compliance"] = 0.20
        got = ug.information(vals)
        self.assertEqual(got["dq_information"], 0.2)
        self.assertEqual(got["worst_class"], "legal_compliance")
        self.assertEqual(got["worst_class_readable"], "legal/compliance")
        self.assertAlmostEqual(got["mean"], 0.8964, places=4)
        self.assertGreater(got["mean"] - got["dq_information"], 0.6, "the mean hides the gap")

    def test_information_refuses_to_default_high(self):
        got = ug.information({"customer/job": 0.9})
        self.assertIsNone(got["dq_information"])
        self.assertIn("insufficient_input", got)

    def test_trimmed_mean_drops_the_extremes(self):
        got = ug.trimmed_mean([0.05, 0.60, 0.62, 0.64, 0.99])
        self.assertAlmostEqual(got["value"], 0.62, places=3)
        self.assertEqual(got["trimmed"], 1)

    def test_small_swarm_warns_instead_of_silently_trimming(self):
        got = ug.trimmed_mean([0.6, 0.7])
        self.assertEqual(got["trimmed"], 0)
        self.assertIn("warning", got)
        self.assertIsNone(ug.trimmed_mean([])["value"])


class TestContractSurface(unittest.TestCase):
    def test_contract_lists_every_gate_advisory(self):
        rows = ug.contract()
        self.assertEqual(len(rows), len(ug.GATES))
        packs = [r for r in rows if r["pack"]]
        self.assertTrue(packs)
        for r in packs:
            self.assertFalse(r["pack_calibrated"], r["id"])
            self.assertTrue(r["pack_questions"], r["id"])

    def test_every_declared_check_exists(self):
        for gid, g in ug.GATES.items():
            for c in g.checks:
                self.assertIn(c, ug.CODE_CHECKS, "%s declares unknown check %s" % (gid, c))

    def test_rule_literals_address_declared_options(self):
        """A rule comparing against a typo'd slug is a gate that can never fire."""
        for name in s1gate.list_rubrics():
            if not name.startswith("ultra."):
                continue
            rb = s1gate.load_rubric(name)
            for rule in rb.rules:
                m = __import__("re").match(r"^\w+\.choice\s*(?:==|!=)\s*(.+)$", rule["when"])
                if not m:
                    continue
                qname = rule["when"].split(".", 1)[0]
                want = m.group(1).strip().strip("\"'")
                self.assertIn(want, rb.questions[qname]["criteria"],
                              "%s: %r compares to an option that does not exist" % (name, rule["when"]))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
