"""The idea surface: V3.1 gates, MAP-Elites replay, and the ASR stack.

The gates are the point of the module — an idea-scoring engine that accepts
everything is worth nothing — so each of the four gates is tested by forcing
its exact threshold pair from the build card, not by hoping a sample lands
there.
"""

from __future__ import annotations

import json
import unittest

from rig_lattice.idea import asr, booster, mapelites
from rig_lattice.idea.booster import (
    ACCEPT_MAX_GENERIC_PENALTY,
    ACCEPT_THRESHOLDS,
    ANTI_RANDOMNESS_APPROPRIATENESS,
    ANTI_RANDOMNESS_NOVELTY,
    GENERIC_USEFULNESS_DEVIATION,
    GENERIC_USEFULNESS_USEFULNESS,
    THEATER_DEVIATION,
    THEATER_PROOF_DENSITY,
    BoosterScore,
    Idea,
    evaluate,
    final_verdict,
    run_gates,
    score_idea,
)


def _score_with(**overrides) -> BoosterScore:
    """A baseline score with specific dimensions forced, to test one gate."""
    base = score_idea(Idea(title="baseline", content="baseline content"))
    fields = {f: getattr(base, f) for f in base.__dataclass_fields__}
    # Start from a state that clears every gate, then break exactly one.
    fields.update(
        creativity_score=0.90,
        deviation_score=0.85,
        novelty=0.80,
        usefulness=0.80,
        quality=0.80,
        surprise=0.80,
        appropriateness=0.80,
        proof_density=0.80,
        generic_penalty=0.05,
    )
    fields.update(overrides)
    return BoosterScore(**fields)


class TestGateThresholds(unittest.TestCase):
    def test_baseline_accepts(self):
        gates = run_gates(_score_with())
        self.assertEqual(final_verdict(gates), "accept")
        self.assertEqual([g.gate for g in gates if not g.passed], [])

    def test_anti_randomness_rejects_novel_but_contextless(self):
        score = _score_with(
            novelty=ANTI_RANDOMNESS_NOVELTY + 0.05,
            appropriateness=ANTI_RANDOMNESS_APPROPRIATENESS - 0.05,
        )
        gates = run_gates(score)
        gate = next(g for g in gates if g.gate == "anti_randomness")
        self.assertFalse(gate.passed)
        self.assertEqual(gate.action, "reject")
        self.assertEqual(final_verdict(gates), "reject")

    def test_anti_randomness_passes_at_the_boundary(self):
        """Exactly at the threshold is not over it: > 0.85, not >= 0.85."""
        score = _score_with(
            novelty=ANTI_RANDOMNESS_NOVELTY,
            appropriateness=ANTI_RANDOMNESS_APPROPRIATENESS - 0.05,
        )
        gate = next(g for g in run_gates(score) if g.gate == "anti_randomness")
        self.assertTrue(gate.passed)

    def test_generic_usefulness_revises_useful_but_median(self):
        score = _score_with(
            usefulness=GENERIC_USEFULNESS_USEFULNESS + 0.05,
            deviation_score=GENERIC_USEFULNESS_DEVIATION - 0.05,
        )
        gates = run_gates(score)
        gate = next(g for g in gates if g.gate == "generic_usefulness")
        self.assertFalse(gate.passed)
        self.assertEqual(gate.action, "revise")
        self.assertEqual(final_verdict(gates), "revise")

    def test_generic_usefulness_rejects_saturated_median_with_no_receipts(self):
        score = _score_with(
            usefulness=0.0,
            deviation_score=0.0,
            generic_penalty=1.0,
            proof_density=0.0,
        )
        gates = run_gates(score)
        gate = next(g for g in gates if g.gate == "generic_usefulness")
        self.assertFalse(gate.passed)
        self.assertEqual(gate.action, "reject")
        self.assertEqual(final_verdict(gates), "reject")

    def test_theater_revises_deviation_without_proof(self):
        score = _score_with(
            deviation_score=THEATER_DEVIATION + 0.05,
            proof_density=THEATER_PROOF_DENSITY - 0.05,
        )
        gates = run_gates(score)
        gate = next(g for g in gates if g.gate == "theater")
        self.assertFalse(gate.passed)
        self.assertEqual(gate.action, "revise")
        self.assertEqual(final_verdict(gates), "revise")

    def test_final_acceptance_needs_every_threshold(self):
        for name, threshold in ACCEPT_THRESHOLDS.items():
            score = _score_with(**{name: threshold - 0.01})
            gates = run_gates(score)
            gate = next(g for g in gates if g.gate == "final_acceptance")
            self.assertFalse(gate.passed, f"{name} below threshold should fail")
            self.assertIn(name, gate.reason)

    def test_final_acceptance_caps_generic_penalty(self):
        score = _score_with(generic_penalty=ACCEPT_MAX_GENERIC_PENALTY + 0.01)
        gate = next(g for g in run_gates(score) if g.gate == "final_acceptance")
        self.assertFalse(gate.passed)
        self.assertIn("generic_penalty", gate.reason)

    def test_reject_outranks_revise(self):
        score = _score_with(
            novelty=0.95,
            appropriateness=0.10,
            deviation_score=0.95,
            proof_density=0.10,
        )
        gates = run_gates(score)
        actions = {g.action for g in gates if not g.passed}
        self.assertIn("reject", actions)
        self.assertIn("revise", actions)
        self.assertEqual(final_verdict(gates), "reject")

    def test_four_gates_always_reported(self):
        gates = run_gates(_score_with())
        self.assertEqual(
            [g.gate for g in gates],
            ["anti_randomness", "generic_usefulness", "theater",
             "final_acceptance"],
        )


class TestScoring(unittest.TestCase):
    def test_all_dimensions_in_unit_interval(self):
        for payload in (
            {"title": "", "content": ""},
            {"title": "x" * 500, "content": "y " * 800},
            {"title": "t", "content": "c", "sources": ["a"] * 50,
             "claims": ["b"] * 50, "mechanisms": ["c"] * 50},
        ):
            score = score_idea(payload)
            for field in ("novelty", "usefulness", "quality", "surprise",
                           "appropriateness", "proof_density",
                           "generic_penalty", "creativity_score",
                           "deviation_score"):
                value = getattr(score, field)
                self.assertGreaterEqual(value, 0.0, f"{field}={value}")
                self.assertLessEqual(value, 1.0, f"{field}={value}")

    def test_buzzwords_raise_the_generic_penalty(self):
        plain = score_idea({"title": "router", "content": "threshold gate"})
        buzzy = score_idea({
            "title": "AI-powered best-in-class synergy",
            "content": "end-to-end seamless world-class paradigm shift",
        })
        self.assertGreater(buzzy.generic_penalty, plain.generic_penalty)

    def test_receipts_raise_proof_density(self):
        bare = score_idea({"title": "t", "content": "c"})
        backed = score_idea({
            "title": "t", "content": "c",
            "sources": ["s1", "s2", "s3"],
            "claims": ["c1", "c2"],
            "mechanisms": ["m1", "m2", "m3"],
        })
        self.assertGreater(backed.proof_density, bare.proof_density)

    def test_corpus_overlap_lowers_novelty(self):
        text = "route the work by a deterministic threshold gate"
        alone = score_idea({"title": "t", "content": text})
        echoed = score_idea({"title": "t", "content": text, "corpus": [text]})
        self.assertLess(echoed.novelty, alone.novelty)

    def test_no_divisor_can_zero_the_score(self):
        score = score_idea({
            "title": "t", "content": "c", "cost_band": 0.0, "time_to_value": 0.0
        })
        self.assertGreaterEqual(score.cost, 0.25)
        self.assertGreaterEqual(score.time_to_value, 0.25)

    def test_proxies_are_declared(self):
        """The two offline proxies must be named in the output, not hidden."""
        score = score_idea({"title": "t", "content": "c"})
        joined = " ".join(score.proxies)
        self.assertIn("N_vendi", joined)
        self.assertIn("S_bayesian", joined)

    def test_evaluate_payload_shape(self):
        result = evaluate({"title": "t", "content": "c"})
        for key in ("verdict", "creativity_score", "dimensions", "gates",
                     "failed_gates", "acceptance"):
            self.assertIn(key, result)
        self.assertIn(result["verdict"], ("accept", "revise", "reject"))


class TestMapElites(unittest.TestCase):
    CANDIDATES = [
        {"title": "Cache the routing table",
         "content": "Memoize the gate lookup because recomputing costs 4ms.",
         "mechanisms": ["lru_cache"], "time_to_value": 0.1},
        {"title": "Seal a proof packet per run",
         "content": "Bind commands, exit codes and a sha256 to every run.",
         "mechanisms": ["sha256", "exit codes", "jsonl"], "time_to_value": 0.3},
        {"title": "Replatform the router",
         "content": "Irreversible migration for throughput.",
         "mechanisms": ["rewrite"], "time_to_value": 0.9},
    ]

    def test_seed_required(self):
        with self.assertRaises(TypeError):
            mapelites.mapelites_grid(self.CANDIDATES)  # type: ignore[call-arg]

    def test_non_int_seed_rejected(self):
        with self.assertRaises(ValueError):
            mapelites.mapelites_grid(self.CANDIDATES, seed="7")  # type: ignore[arg-type]

    def test_same_seed_replays_identically(self):
        first = mapelites.mapelites_grid(self.CANDIDATES, seed=7)
        second = mapelites.mapelites_grid(self.CANDIDATES, seed=7)
        self.assertEqual(json.dumps(first, sort_keys=True),
                          json.dumps(second, sort_keys=True))

    def test_grid_never_exceeds_25_niches(self):
        grid = mapelites.mapelites_grid(self.CANDIDATES, seed=1,
                                         mutations_per_candidate=8)
        self.assertLessEqual(len(grid), mapelites.N_NICHES)
        self.assertEqual(mapelites.N_NICHES, 25)

    def test_elite_per_niche_is_the_highest_scorer(self):
        grid = mapelites.mapelites_grid(self.CANDIDATES, seed=3)
        for niche, elite in grid.items():
            self.assertEqual(elite["niche"], niche)
            self.assertGreaterEqual(elite["creativity_score"], 0.0)

    def test_operators_include_scamper_and_synectics(self):
        operators = mapelites.mutation_operators()
        joined = " ".join(operators).lower()
        self.assertIn("substitute", joined)   # SCAMPER
        self.assertIn("analog", joined)       # Synectics
        self.assertGreaterEqual(len(operators), 7 + 4 + 1)

    def test_coverage_report(self):
        grid = mapelites.mapelites_grid(self.CANDIDATES, seed=5)
        coverage = mapelites.grid_coverage(grid)
        self.assertEqual(coverage["niches_total"], 25)
        self.assertEqual(coverage["niches_filled"], len(grid))


class TestAdversarialSurvivalRate(unittest.TestCase):
    def test_stack_is_25_questions(self):
        self.assertEqual(len(asr.QUESTIONS), 25)

    def test_four_groups_present(self):
        self.assertEqual(
            set(asr.groups()),
            {"pre_ideation", "during_ideation", "post_ideation",
             "hostile_skeptic"},
        )

    def test_manual_questions_excluded_from_denominator(self):
        result = asr.run_stack({"title": "t", "content": "c"})
        self.assertEqual(result["total_questions"], 25)
        self.assertEqual(result["scored"], 25 - result["manual"])
        self.assertGreater(result["manual"], 0)
        self.assertIn("not counted as survived", result["note"])

    def test_manual_questions_never_counted_as_passed(self):
        result = asr.run_stack({"title": "t", "content": "c"})
        for row in result["questions"]:
            if row["manual"]:
                self.assertIsNone(row["passed"])
                self.assertFalse(row["counted"])

    def test_rate_is_a_fraction_of_scored_questions(self):
        result = asr.run_stack({"title": "t", "content": "c"})
        self.assertAlmostEqual(
            result["asr"], result["survived"] / result["scored"], places=4
        )

    def test_receipted_idea_survives_more_than_a_bare_one(self):
        bare = asr.adversarial_survival_rate({"title": "t", "content": "c"})
        strong = asr.adversarial_survival_rate({
            "title": "Deterministic router beats the model-guessed one",
            "content": (
                "Unlike the conventional flow, route by a threshold gate "
                "because a model in the decision path is not reproducible; "
                "measured against a p95 baseline of 12ms behind a feature "
                "flag, so rollback is cheap. However it costs one lookup."
            ),
            "context": "RIG coding agents on enterprise client refactors",
            "sources": ["registry.py", "build card"],
            "claims": ["cuts rework 40% versus baseline"],
            "mechanisms": ["threshold gate", "lookup table", "recorded escalation"],
            "corpus": ["generic competitor copy"],
        })
        self.assertGreater(strong, bare)


if __name__ == "__main__":
    unittest.main()
