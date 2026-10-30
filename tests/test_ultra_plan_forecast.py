"""Offline tests for the plan-quality and forecast-swarm mechanics.

No model calls. These assert structure: what a plan must contain, and what a
crowd must look like before its average means anything.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest

from rig_capabilities import ultra_forecast as uf
from rig_capabilities import ultra_plan as up


def alts(n, mechanism="m"):
    return [{"name": "%s-%d" % (mechanism, i), "mechanism": mechanism + str(i)} for i in range(n)]


class TestDiverge(unittest.TestCase):
    def test_five_distinct_mechanisms_pass(self):
        self.assertTrue(up.diverge(alts(5))["ok"])

    def test_one_alternative_is_refused_with_the_number_named(self):
        got = up.diverge([{"name": "the only idea", "mechanism": "retainer"}])
        self.assertFalse(got["ok"])
        self.assertIn("need 5", got["why"])

    def test_five_rebrandings_of_one_mechanism_collapse(self):
        got = up.diverge([{"name": "tier %d" % i, "mechanism": "monthly retainer"} for i in range(5)])
        self.assertFalse(got["ok"])
        self.assertEqual(got["distinct_mechanisms"], 1)
        self.assertIn("collapsed", got["why"])

    def test_mechanism_matching_is_normalised_not_literal(self):
        got = up.diverge([{"name": "a", "mechanism": "  Retainer  "}, {"name": "b", "mechanism": "retainer"},
                          {"name": "c", "mechanism": "x"}, {"name": "d", "mechanism": "y"},
                          {"name": "e", "mechanism": "z"}, {"name": "f", "mechanism": "w"}])
        self.assertTrue(got["ok"], got["why"])
        self.assertIn("retainer", got["collapsed"])

    def test_alternative_without_a_mechanism_is_malformed_not_counted(self):
        got = up.diverge([{"name": "no mechanism here"}] + alts(6))
        self.assertFalse(got["ok"])
        self.assertEqual(got["malformed"], [0])

    def test_non_list_input_is_refused(self):
        self.assertFalse(up.diverge("five good ideas")["ok"])

    def test_minimum_is_overridable_and_reported(self):
        got = up.diverge(alts(3), minimum=3)
        self.assertTrue(got["ok"])
        self.assertEqual(got["minimum"], 3)


class TestOutsideView(unittest.TestCase):
    def test_no_reference_class_is_an_inside_guess(self):
        self.assertFalse(up.outside_view({"base_rate": 0.4})["ok"])
        self.assertIn("inside-view", up.outside_view({"reference_class": "fine"} )["why"])

    def test_class_without_a_rate_is_refused(self):
        got = up.outside_view({"reference_class": "governed AI studios, first 12 months"})
        self.assertFalse(got["ok"])
        self.assertIn("no base rate", got["why"])

    def test_unsourced_rate_is_refused(self):
        got = up.outside_view({"reference_class": "governed AI studios, first 12 months", "base_rate": 0.4})
        self.assertFalse(got["ok"])
        self.assertIn("no source", got["why"])

    def test_filler_source_is_refused_but_not_a_real_citation_that_mentions_it(self):
        base = {"reference_class": "governed AI studios, first 12 months", "base_rate": 0.4,
                "n_in_class": 30}
        for filler in ("vibes", "Vibes.", "guess", "tbd", "me"):
            self.assertFalse(up.outside_view(dict(base, base_rate_source=filler))["ok"], filler)
        self.assertTrue(up.outside_view(dict(base, base_rate_source="https://x/survey (not vibes-based)"))["ok"])

    def test_rate_must_be_a_probability(self):
        base = {"reference_class": "governed AI studios, first 12 months", "base_rate_source": "https://x"}
        self.assertFalse(up.outside_view(dict(base, base_rate=1.4))["ok"])
        self.assertFalse(up.outside_view(dict(base, base_rate="optimistic"))["ok"])

    def test_uncounted_or_thin_class_is_refused(self):
        base = {"reference_class": "the two studios I know", "base_rate": 0.5, "base_rate_source": "https://x"}
        self.assertIn("n_in_class", up.outside_view(dict(base))["why"])
        self.assertFalse(up.outside_view(dict(base, n_in_class=2))["ok"])
        self.assertFalse(up.outside_view(dict(base, n_in_class="some"))["ok"])

    def test_good_outside_view_reports_what_it_used(self):
        got = up.outside_view({"reference_class": "governed AI studios, first 12 months",
                               "base_rate": 0.28, "base_rate_source": "measured 2026-09", "n_in_class": 41})
        self.assertTrue(got["ok"])
        self.assertEqual(got["base_rate"], 0.28)
        self.assertIn("0.280", got["why"])


class TestSwarmLedger(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.led = uf.Ledger(os.path.join(self.dir, "forecasts.jsonl"))

    def _add(self, name, family, p, **kw):
        kw.setdefault("reasons_for", "evidence supports it")
        kw.setdefault("reasons_against", "evidence against it")
        return self.led.add("r1", "ULTRA ships by 2026-10-31", name, family, p, **kw)

    def test_bare_number_is_rejected(self):
        with self.assertRaises(uf.UltraForecastError) as cm:
            self._add("A", "blackwell", 0.6, reasons_for="")
        self.assertIn("considerations", str(cm.exception))

    def test_probability_out_of_range_is_rejected(self):
        for bad in (1.4, -0.1):
            with self.assertRaises(uf.UltraForecastError):
                self._add("A", "blackwell", bad)

    def test_forecaster_sharing_the_author_family_is_rejected(self):
        with self.assertRaises(uf.UltraForecastError) as cm:
            self._add("A", "blackwell", 0.6, author="me", author_family="blackwell")
        self.assertIn("weight family", str(cm.exception))
        # a different family from the same person is still an independent voice
        self.assertTrue(self._add("A", "qwen", 0.6, author="me", author_family="blackwell"))

    def test_ids_are_stable_per_forecaster_and_distinct_across_them(self):
        a = self._add("A", "blackwell", 0.6)
        b = self._add("B", "qwen", 0.6)
        self.assertNotEqual(a["id"], b["id"])
        self.assertEqual(a["id"], self._add("A", "blackwell", 0.6)["id"])

    def test_trimmed_mean_drops_the_extremes(self):
        for i, p in enumerate([0.44, 0.58, 0.62, 0.66, 0.71]):
            self._add("F%d" % i, "fam%d" % (i % 3), p, low_correlation=(i == 0))
        got = uf.aggregate(self.led.all())
        self.assertAlmostEqual(got["value"], 0.62, places=3)
        self.assertEqual(got["n"], 5)
        self.assertTrue(got["diverse"], got["refusals"])

    def test_small_or_single_family_swarm_refuses_to_look_authoritative(self):
        self._add("A", "blackwell", 0.6)
        self._add("B", "blackwell", 0.7)
        got = uf.aggregate(self.led.all())
        self.assertFalse(got["diverse"])
        self.assertEqual(len(got["refusals"]), 2)

    def test_two_families_are_refused_the_contract_demands_three(self):
        for i, (fam, p) in enumerate([("qwen", 0.40), ("qwen", 0.50), ("gpt", 0.55),
                                      ("gpt", 0.60), ("gpt", 0.65)]):
            self._add("F%d" % i, fam, p)
        got = uf.aggregate(self.led.all())
        self.assertFalse(got["diverse"], got)
        self.assertTrue(any("3" in r for r in got["refusals"]),
                        "the refusal must name the demanded family count: %s" % got["refusals"])

    def test_asymmetric_swarm_aggregates_by_symmetric_trim(self):
        """All-high swarm with one extreme low: trim=1 drops ONE from each end
        symmetrically -- the loud low goes, one high goes, and the fixture pins
        the number so an 'asymmetric clamp' cannot sneak in unnoticed."""
        for i, (fam, p) in enumerate([("qwen", 0.90), ("gpt", 0.91), ("gemini", 0.92),
                                      ("llama", 0.93), ("mistral", 0.05)]):
            self._add("F%d" % i, fam, p)
        got = uf.aggregate(self.led.all())
        self.assertAlmostEqual(got["value"], 0.910, places=3, msg=got)
        self.assertEqual(got["trimmed"], 1)

    def test_author_number_can_be_excluded_from_its_own_swarm(self):
        """Trimming usually already absorbs a lone outlier, so the numbers here
        are chosen to prove the exclusion actually runs, not that trimming works."""
        self._add("AUTHOR", "blackwell", 0.75, author="me")
        for i, (fam, p) in enumerate([("qwen", 0.40), ("gpt", 0.45), ("gemini", 0.50),
                                      ("llama", 0.55), ("mistral", 0.60)]):
            self._add("F%d" % i, fam, p, author="someone-else")
        with_author = uf.aggregate(self.led.all(), drop_author=False)
        self.assertAlmostEqual(with_author["value"], 0.525, places=3)
        without = uf.aggregate(self.led.all(), author="me")
        self.assertAlmostEqual(without["value"], 0.5, places=3)
        self.assertEqual(without["n"], 5)
        self.assertGreater(with_author["value"], without["value"])

    def test_nothing_is_claimed_registered_until_a_transport_says_so(self):
        rec = self._add("A", "blackwell", 0.6, horizon="P1M", trigger_event="start",
                        target_event="done", evidence_refs=["run:r1/intent.md"], cohort_id="ultra-r1")
        self.assertFalse(rec["registered"])
        self.assertEqual(len(self.led.pending()), 1)
        payload = uf.register_payload(rec)
        self.assertEqual(sorted(payload), sorted(
            ["resolver_id", "horizon", "probability", "cohort_id", "proposition",
             "trigger_event", "target_event", "evidence_refs"]))
        self.assertEqual(payload["probability"], "0.6000")
        self.assertEqual(len(self.led.pending()), 1, "building a payload is not sending it")
        self.led.mark_registered(rec["id"], True)
        self.assertEqual(len(self.led.pending()), 0)
        self.assertTrue(self.led.get(rec["id"])["registered"])

    def test_incomplete_record_cannot_be_registered(self):
        rec = self._add("A", "blackwell", 0.6)
        with self.assertRaises(uf.UltraForecastError) as cm:
            uf.register_payload(rec)
        for field in ("horizon", "trigger_event", "target_event", "evidence_refs"):
            self.assertIn(field, str(cm.exception))

    def test_registration_failure_is_recorded_not_swallowed(self):
        rec = self._add("A", "blackwell", 0.6, horizon="P1M", trigger_event="s", target_event="t",
                        evidence_refs=["x"])
        self.led.mark_registered(rec["id"], False, error="pg down")
        got = self.led.get(rec["id"])
        self.assertFalse(got["registered"])
        self.assertEqual(got["transport_error"], "pg down")

    def test_brier_matches_hand_arithmetic(self):
        # perfect 0.0; a flat 0.5 coin flip scores 0.25; a confident miss scores 1.0
        self.assertEqual(uf.brier([(1.0, 1), (0.0, 0)])["brier"], 0.0)
        self.assertEqual(uf.brier([(0.5, 1), (0.5, 0)])["brier"], 0.25)
        self.assertEqual(uf.brier([(0.9, 0)])["brier"], 0.81)
        self.assertIsNone(uf.brier([])["brier"])

    def test_brier_rejects_garbage_pairs(self):
        with self.assertRaises(uf.UltraForecastError):
            uf.brier([(0.5, 2)])
        with self.assertRaises(uf.UltraForecastError):
            uf.brier([(1.5, 1)])

    def test_weights_are_withheld_on_thin_evidence_not_invented(self):
        for i, p in enumerate([0.6, 0.4, 0.7]):
            rec = self._add("F%d" % i, "blackwell", p)
            self.led.resolve(rec["id"], 1 if i == 0 else 0)
        got = uf.weights(self.led.all())
        self.assertTrue(got["uniform"])
        self.assertIsNone(got["weights"])
        self.assertIn("weight withheld", got["thin"]["blackwell"])

    def test_weights_reward_the_better_family_once_n_resolves(self):
        for i in range(4):
            r = self._add("good%d" % i, "goodfam", 0.8)
            self.led.resolve(r["id"], 1)
        for i in range(4):
            r = self._add("bad%d" % i, "badfam", 0.8)
            self.led.resolve(r["id"], 0)
        got = uf.weights(self.led.all())
        self.assertFalse(got["uniform"])
        self.assertGreater(got["weights"]["goodfam"], got["weights"]["badfam"])
        self.assertAlmostEqual(got["scored"]["goodfam"]["brier"], 0.04, places=3)
        self.assertAlmostEqual(got["scored"]["badfam"]["brier"], 0.64, places=3)

    def test_outcomes_are_written_once(self):
        rec = self._add("A", "blackwell", 0.6)
        self.led.resolve(rec["id"], 1)
        with self.assertRaises(uf.UltraForecastError):
            self.led.resolve(rec["id"], 0)

    def test_a_torn_line_is_skipped_and_reported_by_count(self):
        rec = self._add("A", "blackwell", 0.6)
        with open(self.led.path, "a") as fh:
            fh.write("{ this is not json\n")
        self.assertEqual(len(self.led.all()), 1)
        self.assertEqual(self.led.get(rec["id"])["id"], rec["id"])

    def test_resolve_survives_a_reload(self):
        rec = self._add("A", "blackwell", 0.6)
        self.led.resolve(rec["id"], 1)
        again = uf.Ledger(self.led.path)
        self.assertEqual(again.get(rec["id"])["outcome"], 1)
        self.assertEqual(json.loads(again.path.read_text().splitlines()[0])["outcome"], 1)


class TestEnsembleHygieneAndPlants(unittest.TestCase):
    """Conductor D-20261001-083903-8fab: capping + calibration must go RED on
    planted failures, not just green on the happy path. Each mutant below is a
    planted defect; the test asserts the check detects it.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.led = uf.Ledger(os.path.join(self.dir, "forecasts.jsonl"))

    def _add(self, name, family, p, **kw):
        kw.setdefault("reasons_for", "evidence supports it")
        kw.setdefault("reasons_against", "evidence against it")
        return self.led.add("r1", "ULTRA ships", name, family, p, **kw)

    def _crowd(self, probs=(0.44, 0.58, 0.62, 0.66, 0.71), low_at=0):
        for i, p in enumerate(probs):
            self._add("F%d" % i, "fam%d" % (i % 5), p, low_correlation=(i == low_at))
        return self.led.all()

    def test_planted_overconfident_stream_is_capped(self):
        got = uf.aggregate(self._crowd((0.99, 0.99, 0.99, 0.99, 0.99)))
        self.assertGreater(got["capped_count"], 0, "0.99 voices must be winsorized")
        self.assertLessEqual(got["value"], 0.98 + 1e-9)
        self.assertTrue(uf.verify_aggregate(got)["ok"])

    def test_planted_uncapped_mutant_goes_red(self):
        recs = self._crowd((0.99, 0.99, 0.99, 0.99, 0.99))
        mutant = uf.aggregate(recs, cap_bounds=None)      # planted defect: no cap
        verdict = uf.verify_aggregate(mutant)
        self.assertFalse(verdict["ok"])
        self.assertTrue(any("capping skipped" in r for r in verdict["reasons"]))
        good = uf.aggregate(recs)
        self.assertNotEqual(mutant["value"], good["value"],
                            "the mutant must actually change the number, else the red proves nothing")

    def test_planted_missing_caveat_goes_red(self):
        got = uf.aggregate(self._crowd())
        del got["correlation_caveat"]                        # planted defect
        verdict = uf.verify_aggregate(got)
        self.assertFalse(verdict["ok"])
        self.assertTrue(any("caveat missing" in r for r in verdict["reasons"]))

    def test_swarm_without_low_correlation_member_is_refused(self):
        for i, p in enumerate((0.44, 0.58, 0.62, 0.66, 0.71)):
            self._add("F%d" % i, "fam%d" % (i % 5), p)   # nobody flagged
        got = uf.aggregate(self.led.all())
        self.assertFalse(got["diverse"])
        self.assertTrue(any("low-correlation" in r for r in got["refusals"]), got["refusals"])

    def test_planted_forged_diversity_goes_red(self):
        got = uf.aggregate(self._crowd())
        got["low_correlation_members"] = 0                 # planted defect: forged flag
        verdict = uf.verify_aggregate(got)
        self.assertFalse(verdict["ok"])
        self.assertTrue(any("slot empty" in r for r in verdict["reasons"]))

    def _resolved(self, n, outcome_fn):
        out = []
        for i in range(n):
            rec = self._add("R%d" % i, "fam%d" % (i % 5), 0.2 + 0.6 * ((i * 7) % 10) / 10.0,
                            low_correlation=(i == 0))
            self.led.resolve(rec["id"], outcome_fn(i))
            out.append(self.led.get(rec["id"]))
        return out

    def test_platt_withheld_on_thin_history(self):
        resolved = self._resolved(15, lambda i: i % 2)
        fit = uf.platt_fit(resolved)
        self.assertIsNone(fit["fit"])
        self.assertIn("worse than none", fit["why"])
        with self.assertRaises(uf.UltraForecastError):
            uf.calibrate(0.7, fit)      # a withheld calibrator never passes numbers through

    def test_platt_withheld_on_single_class_history(self):
        resolved = self._resolved(25, lambda i: 1)          # every outcome is 1
        fit = uf.platt_fit(resolved)
        self.assertIsNone(fit["fit"])
        self.assertIn("single-class", fit["why"])

    def test_platt_fits_and_refits_on_cadence(self):
        resolved = self._resolved(40, lambda i: i % 2)
        fit = uf.platt_fit(resolved)
        self.assertIsNotNone(fit["fit"])
        self.assertEqual(fit["fit_n"], 40)
        self.assertEqual(fit["fitted_on"], "resolved ledger (probability, outcome) pairs")
        self.assertFalse(uf.platt_stale(fit, 40))
        self.assertFalse(uf.platt_stale(fit, 89))
        self.assertTrue(uf.platt_stale(fit, 90), ">=50 newly resolved must demand a refit")
        self.assertTrue(uf.platt_stale({"fit": None}, 10000),
                        "a withheld calibrator is always stale")

    def test_platt_shrinks_an_overconfident_history(self):
        over = [{"probability": 0.9, "outcome": i % 2} for i in range(40)]
        fit = uf.platt_fit(over)
        self.assertIsNotNone(fit["fit"])
        self.assertLess(uf.calibrate(0.9, fit), 0.9, "an overconfident history must shrink high numbers")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
