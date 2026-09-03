"""Day-4 acceptance tests per DOCTRINE.md §8.

Required acceptance:
  - All 10 nature engines implemented with bio-inspired formulas
  - Reef-diversity / starvation-floor / replacement-probability boundary tests
  - Process gates wired into orchestrator
"""
from __future__ import annotations
import sys
from pathlib import Path


from rig_lattice.core.base import DeviationEngine, EngineResult
from rig_lattice.core.registry import NATURE
from rig_lattice.engines.nature import load_nature_engines
from rig_lattice.engines import load_all_engines
from rig_lattice.adapters.bio_formulas import (
    pheromone_reinforcement_score, physarum_path_concentration,
    diversity_score, levy_jump_score, firefly_attractiveness_score,
    chemotaxis_gradient_score, whale_spiral_annealing,
    cuckoo_parasitism_score, coral_reef_score,
    coral_reef_substrate_coverage, reef_diversity_check,
    reef_replacement_probability, starvation_floor_ok,
    levy_step_prob, whale_spiral_step, cuckoo_replacement_count,
    REEF_SUBSTRATES, REEF_DIVERSITY_FLOOR, REEF_REPLACEMENT_PROB_MAX,
    REEF_STARVATION_FLOOR, EVAPORATION_RHO, LEVY_BETA, CUCKOO_ABANDON_PROBABILITY,
)

STRONG_TEXT_PATH = Path(__file__).parent.parent / "examples" / "example_strict_passing.md"


# ── 1. Bio-formula constants ──────────────────────────────────────────────

def test_evaporation_rho_in_range():
    assert 0 < EVAPORATION_RHO < 1

def test_levy_beta_in_canonical_range():
    # Yang/Deb: 1 < β ≤ 3 for heavy-tail Lévy
    assert 1 < LEVY_BETA <= 3

def test_cuckoo_abandon_probability_in_range():
    # Standard CSO: 0.1 ≤ p_a ≤ 0.5
    assert 0.1 <= CUCKOO_ABANDON_PROBABILITY <= 0.5

def test_reef_substrates_are_5():
    assert len(REEF_SUBSTRATES) == 5
    assert set(REEF_SUBSTRATES) == {"broadcast", "brood", "bud", "fragment", "deprecate"}


# ── 2. Boundary: Reef diversity floor ─────────────────────────────────────

def test_reef_diversity_below_floor_fails():
    coverage = {s: False for s in REEF_SUBSTRATES}
    coverage["broadcast"] = True  # only 1/5 = 20% < 40% floor
    ok, msg = reef_diversity_check(coverage)
    assert ok is False
    assert "below floor" in msg

def test_reef_diversity_at_floor_passes():
    coverage = {s: False for s in REEF_SUBSTRATES}
    coverage["broadcast"] = True
    coverage["brood"] = True  # 2/5 = 40% AT floor
    ok, msg = reef_diversity_check(coverage)
    assert ok is True

def test_reef_diversity_above_floor_passes():
    coverage = {s: True for s in REEF_SUBSTRATES}  # 100%
    ok, msg = reef_diversity_check(coverage)
    assert ok is True


# ── 3. Boundary: Reef replacement probability cap ─────────────────────────

def test_reef_replacement_starts_low():
    p = reef_replacement_probability(generation=0, max_gens=100)
    assert 0.04 <= p <= 0.06  # starts near 0.05

def test_reef_replacement_caps_at_max():
    p = reef_replacement_probability(generation=999, max_gens=100)
    assert p <= REEF_REPLACEMENT_PROB_MAX
    assert p == REEF_REPLACEMENT_PROB_MAX

def test_reef_replacement_monotonic_with_generation():
    p0 = reef_replacement_probability(0, 100)
    p50 = reef_replacement_probability(50, 100)
    p100 = reef_replacement_probability(100, 100)
    assert p0 < p50 < p100 or p100 == REEF_REPLACEMENT_PROB_MAX


# ── 4. Boundary: Starvation floor ─────────────────────────────────────────

def test_starvation_floor_above_passes():
    # All substrates at 20% — well above 5% floor
    ok, msg = starvation_floor_ok([0.20] * 5)
    assert ok is True

def test_starvation_floor_at_threshold_passes():
    # Exactly at floor — counts as pass (inclusive)
    ok, msg = starvation_floor_ok([REEF_STARVATION_FLOOR] * 5)
    assert ok is True

def test_starvation_floor_below_fails():
    # One substrate below floor
    ok, msg = starvation_floor_ok([0.20, 0.20, 0.001, 0.20, 0.20])
    assert ok is False
    assert "below floor" in msg

def test_starvation_floor_empty_input_fails():
    ok, msg = starvation_floor_ok([])
    assert ok is False


# ── 5. Bio-formula math primitives ────────────────────────────────────────

def test_levy_step_prob_heavy_tail():
    # Larger step → smaller probability (heavy-tail)
    p_small = levy_step_prob(2.0)
    p_large = levy_step_prob(100.0)
    assert p_small > p_large

def test_levy_step_prob_zero_returns_zero():
    assert levy_step_prob(0.0) == 0.0
    assert levy_step_prob(-1.0) == 0.0

def test_whale_spiral_step_returns_tuple():
    a, exp_cos = whale_spiral_step(t=50, total_iter=100)
    assert isinstance(a, float)
    assert isinstance(exp_cos, float)

def test_whale_spiral_a_decreases():
    # 'a' linearly decreases from 2 to 0
    a_early = whale_spiral_step(0, 100)[0]
    a_late = whale_spiral_step(99, 100)[0]
    assert a_early > a_late

def test_cuckoo_replacement_count_at_least_one():
    # Even a 1-population case returns ≥1 replacement
    assert cuckoo_replacement_count(1) >= 1
    assert cuckoo_replacement_count(100) == int(100 * CUCKOO_ABANDON_PROBABILITY)


# ── 6. Bio-formula scoring functions ──────────────────────────────────────

def test_pheromone_score_balanced_text():
    text = "We invest in primary path. We abandon secondary. We double down on third. We prune weak ones."
    score = pheromone_reinforcement_score(text)
    assert score > 0  # has both reinforcement and evaporation

def test_pheromone_score_one_sided_text():
    text = "Just keep going forever. Never stop. Always push."
    score = pheromone_reinforcement_score(text)
    assert score < 50  # no evaporation signals → low balance

def test_levy_jump_score_higher_with_more_domains():
    sparse = "We build software."
    dense = "Like Bloomberg, iOS, and Stripe. Network effects like Tesla, Topcon."
    assert levy_jump_score(dense) > levy_jump_score(sparse)

def test_coral_reef_score_full_coverage():
    text = ("broadcast Forge Edge mass-distribute. brood internal. "
            "bud spin-off. fragment second-line. deprecate legacy.")
    score = coral_reef_score(text)
    assert score >= 80  # ≥4 of 5 substrates

def test_coral_reef_score_no_coverage():
    text = "Standard project plan with no synthesis modes."
    score = coral_reef_score(text)
    assert score == 0.0

def test_diversity_score_with_alternatives():
    text = "Option A is X. Alternative 1 is Y. Scenario 2 is Z."
    assert diversity_score(text) >= 50

def test_chemotaxis_gradient_score_with_steps():
    text = "Month 1 audit. Month 2 launch. Month 3 ship. Month 4 sign. Month 5 train. Month 6 deploy."
    assert chemotaxis_gradient_score(text) >= 50

def test_whale_spiral_annealing_three_phases():
    text = "Phase 1 Foundation. Then Phase 2 Activation. Finally Phase 3 Scale."
    assert whale_spiral_annealing(text) > 0


# ── 7. 10 nature engines load + score ─────────────────────────────────────

def test_load_nature_engines_returns_10():
    engines = load_nature_engines()
    assert len(engines) == 10

def test_each_nature_engine_is_deviation_engine():
    for e in load_nature_engines():
        assert isinstance(e, DeviationEngine)
        assert e.layer == "nature"
        assert e.target == "process"
        assert e.is_gate is False  # nature engines score, don't gate

def test_each_nature_engine_has_unique_id():
    ids = [e.id for e in load_nature_engines()]
    assert sorted(ids) == list(range(21, 31))

def test_each_nature_engine_scores_text():
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    for e in load_nature_engines():
        result = e.score(text)
        assert isinstance(result, EngineResult)
        assert -20.0 <= result.madz <= 20.0  # nature layer clamp

def test_strong_text_passes_majority_of_nature():
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    engines = load_nature_engines()
    passes = sum(1 for e in engines if e.score(text).status == "PASS")
    assert passes >= 7  # ≥7/10 of nature engines


# ── 8. Total engine count after Day 4 ─────────────────────────────────────

def test_load_all_engines_includes_nature():
    """Nature engines (10) are part of load_all_engines()."""
    engines = load_all_engines()
    nature = [e for e in engines if e.layer == "nature"]
    assert len(nature) == 10
    assert "nature" in {e.layer for e in engines}


# ── Manual runner ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [(n, fn) for n, fn in globals().items()
              if n.startswith("test_") and callable(fn)]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}  →  {e}")
            failed.append(name)
        except Exception as e:
            print(f"  ⚠ {name}  →  {type(e).__name__}: {e}")
            failed.append(name)
    print()
    print(f"  RESULT: {passed}/{len(tests)} passed")
    if failed:
        print(f"  FAILED: {failed}")
        sys.exit(1)
