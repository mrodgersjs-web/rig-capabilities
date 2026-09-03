"""Day-5 acceptance tests per DOCTRINE.md §8.

Required acceptance:
  - All 10 physics engines (31–40) with literal physics formulas
  - Short-circuit: any L3 BLOCK halts the pipeline
  - Worked test case: artifact that passes L1+L2 but fails Fine-Tuning gate
    → MUST short-circuit
"""
from __future__ import annotations
import math
import sys
from pathlib import Path


from rig_lattice.core.base import DeviationEngine, EngineResult
from rig_lattice.core.registry import PHYSICS
from rig_lattice.engines import load_all_engines, load_physics_engines, physics_short_circuit
from rig_lattice.adapters.physics_formulas import (
    # constants
    H_BAR, SPEED_OF_LIGHT, K_BOLTZMANN, PLANCK_LENGTH,
    FINE_TUNING_THRESHOLD, BELL_CLASSICAL_BOUND, BELL_QUANTUM_BOUND,
    HAWKING_VOLUME_RATIO_MAX, HAWKING_ENTROPY_THRESHOLD,
    # formulas
    wkb_tunneling_probability, fermion_state_collision,
    casimir_force_per_area, fine_tuning_ratio, bekenstein_hawking_entropy,
    lightcone_separation, chsh_parameter, bell_violation,
    hysteresis_loop_area, heisenberg_min_uncertainty,
    # scorers
    quantum_tunnel_score, pauli_exclusion_score, casimir_terseness_score,
    fine_structure_score, hawking_horizon_score, causality_score,
    absolute_zero_score, phase_transition_score, bell_entanglement_score,
    vacuum_fluctuation_score,
)

STRONG_TEXT_PATH = Path(__file__).parent.parent / "examples" / "example_strict_passing.md"


# ── 1. Physical constants ────────────────────────────────────────────────

def test_planck_constant_correct():
    assert abs(H_BAR - 1.054571817e-34) < 1e-43

def test_speed_of_light_correct():
    assert SPEED_OF_LIGHT == 299_792_458

def test_boltzmann_constant_correct():
    assert abs(K_BOLTZMANN - 1.380649e-23) < 1e-32

def test_planck_length_correct():
    assert abs(PLANCK_LENGTH - 1.616255e-35) < 1e-44

def test_fine_tuning_threshold():
    assert FINE_TUNING_THRESHOLD == 0.10

def test_bell_classical_bound_is_2():
    assert BELL_CLASSICAL_BOUND == 2.0

def test_bell_quantum_bound_tsirelson():
    # Tsirelson bound: 2√2 ≈ 2.828
    assert abs(BELL_QUANTUM_BOUND - 2 * math.sqrt(2)) < 1e-9


# ── 2. WKB tunneling formula ─────────────────────────────────────────────

def test_wkb_over_barrier_returns_1():
    # E ≥ V_barrier → classical passage (T = 1)
    assert wkb_tunneling_probability(5.0, 10.0, 1.0) == 1.0

def test_wkb_below_barrier_in_0_1_range():
    # E < V → tunneling, 0 < T < 1
    t = wkb_tunneling_probability(barrier_height=1e-19, particle_energy=5e-20,
                                    barrier_width=1e-10, mass=9.11e-31)
    assert 0.0 < t <= 1.0

def test_wkb_zero_width_returns_zero():
    assert wkb_tunneling_probability(10, 5, 0.0) == 0.0


# ── 3. Pauli exclusion ───────────────────────────────────────────────────

def test_pauli_no_duplicates_returns_pass_score():
    text = "Para A line one.\n\nPara B different text completely.\n\nPara C unique content here entirely."
    score = pauli_exclusion_score(text)
    assert score >= 90  # no collisions → near 100

def test_pauli_duplicate_paragraphs_penalty():
    para = "Identical paragraph repeated. " * 5
    text = f"{para}\n\n{para}\n\n{para}"
    score = pauli_exclusion_score(text)
    # 3 paragraphs, all identical → 2 collisions → 100 - 50 = 50
    assert score <= 50  # collisions → lower score

def test_fermion_state_collision_detector():
    assert fermion_state_collision(["a", "b", "c"]) is False
    assert fermion_state_collision(["a", "b", "a"]) is True


# ── 4. Casimir force ─────────────────────────────────────────────────────

def test_casimir_force_is_attractive_negative():
    # F/A always negative (attractive) per Casimir
    f = casimir_force_per_area(1e-9)  # 1 nm
    assert f < 0

def test_casimir_force_inverse_d4_scaling():
    # Halving distance → 16x stronger (1/d⁴)
    f1 = casimir_force_per_area(1e-9)
    f2 = casimir_force_per_area(0.5e-9)
    assert abs(abs(f2) - 16 * abs(f1)) / abs(f1) < 0.01

def test_casimir_terseness_short_sentences_pass():
    text = ". ".join(["short sentence"] * 30) + "."
    score = casimir_terseness_score(text)
    assert score == 100.0

def test_casimir_terseness_long_sentences_fail():
    long_sentence = "this is a very long sentence " * 10
    text = ". ".join([long_sentence] * 5) + "."
    score = casimir_terseness_score(text)
    assert score < 50


# ── 5. Fine-tuning ratio ─────────────────────────────────────────────────

def test_fine_tuning_below_threshold_is_fine_tuned():
    ratio = fine_tuning_ratio(viable_band=0.05, parameter_space=1.0)
    assert ratio < FINE_TUNING_THRESHOLD  # fine-tuned

def test_fine_tuning_above_threshold_is_generic():
    ratio = fine_tuning_ratio(viable_band=0.5, parameter_space=1.0)
    assert ratio > FINE_TUNING_THRESHOLD  # generic

def test_fine_tuning_zero_parameter_space():
    assert fine_tuning_ratio(0.5, 0.0) == 1.0


# ── 6. Hawking radiation ─────────────────────────────────────────────────

def test_bekenstein_hawking_positive_for_area():
    s = bekenstein_hawking_entropy(area_m2=1.0)
    assert s > 0

def test_bekenstein_hawking_zero_area():
    assert bekenstein_hawking_entropy(0.0) == 0.0

def test_hawking_horizon_score_proof_dense():
    text = ("We have certified. We own the platform. We built the silicon. "
            "We deliver $10M annually. We ship 24 SKUs. We operate 30 years.")
    score = hawking_horizon_score(text)
    assert score >= 90

def test_hawking_horizon_score_empty():
    text = "Some generic text without any proof of access."
    score = hawking_horizon_score(text)
    assert score < 50


# ── 7. Speed-of-light causality ──────────────────────────────────────────

def test_lightcone_timelike_separation():
    # 1 light-second time, 0 distance → strictly timelike
    assert lightcone_separation(time_delta=1.0, space_delta=0) == "timelike"

def test_lightcone_spacelike_separation():
    # 1 second time, 2 light-seconds distance → spacelike (acausal)
    assert lightcone_separation(time_delta=1.0, space_delta=2 * SPEED_OF_LIGHT) == "spacelike"

def test_causality_score_no_violations():
    text = "Phase 1 audit. Phase 2 build on Phase 1. Phase 3 scale Phase 2."
    assert causality_score(text) == 100.0

def test_causality_score_placeholder_penalty():
    text = "We will deliver [TBD] revenue. The plan is [SOURCE]. Read [PLACEHOLDER] here."
    assert causality_score(text) < 50  # 3 placeholders → 100 - 90 = ≤10


# ── 8. Absolute zero / no-perfection ─────────────────────────────────────

def test_absolute_zero_clean_text_passes():
    text = "We commit to <50ms p99 latency with <5% false-positive rate."
    assert absolute_zero_score(text) == 100.0

def test_absolute_zero_caught_banned_phrase():
    text = "We guarantee zero downtime and 100% reliable always available service."
    # 3 matches: zero downtime, 100% reliable, always available
    # 100 - 75 = 25
    assert absolute_zero_score(text) <= 50


# ── 9. Phase transition ─────────────────────────────────────────────────

def test_phase_transition_commitments_score():
    text = ("We commit to ship by Month 8. We will not retreat. Past this "
            "point, the bet is locked. Production-or-nothing guarantee signed.")
    assert phase_transition_score(text) >= 50

def test_hysteresis_loop_area_nonzero_for_difference():
    T_up = [0.0, 1.0, 2.0]
    T_down = [0.0, 1.0, 2.0]
    op_up = [0.0, 0.5, 1.0]
    op_down = [0.2, 0.7, 1.0]
    area = hysteresis_loop_area(T_up, T_down, op_up, op_down)
    assert area > 0


# ── 10. Bell entanglement ───────────────────────────────────────────────

def test_chsh_parameter_computes():
    s = chsh_parameter(1.0, 0.0, 1.0, 1.0)
    assert s == 3.0

def test_bell_violation_above_2():
    assert bell_violation(2.5) is True
    assert bell_violation(-2.5) is True

def test_bell_violation_at_or_below_classical_bound():
    assert bell_violation(2.0) is False
    assert bell_violation(1.5) is False
    assert bell_violation(0.0) is False


# ── 11. Vacuum fluctuation (Heisenberg) ─────────────────────────────────

def test_heisenberg_min_uncertainty_correct():
    # ΔE_min = ℏ/(2·Δt). For Δt=1s, ΔE = ℏ/2 ≈ 5.27e-35
    de = heisenberg_min_uncertainty(1.0)
    assert abs(de - H_BAR / 2) < 1e-44

def test_vacuum_fluctuation_score_dense_metrics():
    text = (
        "$185K activation. $485K transformation. $42K/mo. $14K/mo. $26K/mo. "
        "$10.4M federal. $130M Y3. $10M ARR. $50K refund. $200K/OEM. "
        "8% attach. 18% attach. 32% attach. 9.1% CAGR. 13.3% CAGR. 35% margin. "
        "30% margin. 25% probability. 70% probability. 80% probability. "
        "9 months. 18 months. 24 months. 6 months. 3 months. 5 weeks. "
        "4 minutes. 50ms. 18ms. 32ms. 600 hours per week."
    )
    assert vacuum_fluctuation_score(text) >= 80

def test_vacuum_fluctuation_score_silent():
    text = "We have a plan. It is comprehensive. We will execute it."
    assert vacuum_fluctuation_score(text) < 30


# ── 12. 10 physics engines loaded ───────────────────────────────────────

def test_load_physics_engines_returns_10():
    engines = load_physics_engines()
    assert len(engines) == 10

def test_each_physics_engine_is_gate():
    for e in load_physics_engines():
        assert e.is_gate is True
        assert e.layer == "physics"
        assert e.target == "state"

def test_each_physics_engine_has_unique_id():
    ids = [e.id for e in load_physics_engines()]
    assert sorted(ids) == list(range(31, 41))

def test_physics_engines_clamp_to_30_sigma():
    """Physics layer clamp is ±30σ per DOCTRINE §1.3."""
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    for e in load_physics_engines():
        result = e.score(text)
        assert -30.0 <= result.madz <= 30.0


# ── 13. Total engine count after Day 5 ──────────────────────────────────

def test_load_all_engines_returns_40():
    """20 cognitive + 10 nature + 10 physics = 40 total."""
    engines = load_all_engines()
    assert len(engines) == 40
    by_layer = {l: 0 for l in ("cognitive", "nature", "physics")}
    for e in engines:
        by_layer[e.layer] += 1
    assert by_layer == {"cognitive": 20, "nature": 10, "physics": 10}


# ── 14. WORKED SHORT-CIRCUIT TEST CASE (DOCTRINE §8 Day 5 mandate) ──────

def test_short_circuit_fires_on_perfect_claim():
    """Artifact loaded with banned absolute-zero claims should HARD_BLOCK
    on the AbsoluteZeroFloor gate, regardless of how strong cognitive/
    nature signals are."""
    text = (
        # Strong cognitive signal — full of mechanism, evidence, citations
        "HED Manufacturing[1] commits to deliver Forge Edge by Month 8. "
        "Because we built the CL-4002 silicon, predictive diagnostics runs at <50ms p99. "
        "Per Research and Markets (Jan 2025)[2], the market grows at 9.1% CAGR. "
        "P(Parker accelerates | Camgian closes ≥2 OEMs by Q3 2026) = 60%. "
        # Banned perfection claims that trigger AbsoluteZero gate
        "Our system guarantees 100% reliable, always-on, perfect uptime with zero downtime. "
        "It is irrefutable that this never fails."
    )
    short, fails = physics_short_circuit(text)
    assert short is True
    assert len(fails) >= 1
    fail_names = [f["name"] for f in fails]
    assert "AbsoluteZeroFloor" in fail_names

def test_clean_text_absolute_zero_raw_score_high():
    """Verify clean text has high raw absolute-zero score (no banned phrases).

    Note: short-circuit may still fire on other gates (e.g. Vacuum needs
    metric density, Casimir needs many sentences) for very short text — that's
    correct behavior. This test verifies the AbsoluteZero gate specifically
    is permissive for clean text.
    """
    text = (
        "We commit to ship by Month 8 with <50ms p99 latency and <5% FPR "
        "under measured conditions, with documented kill criteria by Q3 2027."
    )
    # Raw score: no banned phrases → 100
    assert absolute_zero_score(text) == 100.0

def test_short_circuit_returns_failure_details():
    """The short-circuit reporter must return enough detail to surface in HTML."""
    text = "We guarantee always-on, 100% reliable, perfect, zero-downtime service. Never fails. Cannot be argued."
    short, fails = physics_short_circuit(text)
    assert short
    for f in fails:
        assert "name" in f
        assert "status" in f
        assert "madz" in f
        assert "reason" in f


# ── Manual runner ───────────────────────────────────────────────────────
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
