"""Day-1 acceptance tests for core math primitives per DOCTRINE.md §8.

Anchor cases mandated: σ = −10, 0, +3, +5, +10, +30.

Run:
    cd capabilities/skills/rig-lattice-system
    python3 tests/run_all.py
"""
from __future__ import annotations
import sys
from pathlib import Path


from rig_lattice.core.robust_mad_z import robust_mad_z, mad, NORMALITY_CONSTANT
from rig_lattice.core.sigma import sigma_score, patent_examiner_trigger, anchor_label
from rig_lattice.core.escalation import escalation_cost
from rig_lattice.core.bdf import bdf, bdf_blocked, bdf_explain
from rig_lattice.core.thresholds import THRESHOLDS, detonation_gate, BLOCK, PASS, has_banned_phrase
from rig_lattice.core.rig_l import rig_l_composite, rig_l_label
from rig_lattice.core.base import DeviationEngine, EngineResult
from rig_lattice.core.registry import (
    ENGINE_REGISTRY, resolve_engine, resolve_by_codename, resolve_by_slug,
    list_engines_by_layer, physics_engines, engine_count_by_layer,
)


# ── 1. Robust-MAD-Z primitive ──────────────────────────────────────────────

def test_robust_mad_z_returns_zero_for_median_value():
    baseline = [10, 11, 12, 13, 14, 15]
    # median = 12.5; scoring 12.5 should give 0σ
    assert abs(robust_mad_z(12.5, baseline)) < 0.01

def test_robust_mad_z_normality_constant():
    assert NORMALITY_CONSTANT == 0.6745

def test_mad_is_median_absolute_deviation():
    # Manually computed: median([1,2,3,4,5]) = 3; deviations = [2,1,0,1,2]; median = 1
    assert abs(mad([1, 2, 3, 4, 5]) - 1.0) < 0.01

def test_mad_floor_prevents_div_by_zero():
    # All-identical baseline would give MAD=0 → divide-by-zero
    z = robust_mad_z(10.0, [5, 5, 5, 5, 5])
    # Should be very high (large numerator / floor) but not crash
    assert z != 0
    assert isinstance(z, float)

def test_robust_mad_z_outlier_robust():
    # Adding one extreme outlier should NOT change the median or MAD much
    z1 = robust_mad_z(10, [4, 5, 6, 5, 4])
    z2 = robust_mad_z(10, [4, 5, 6, 5, 4, 1000])  # add outlier
    # Robust estimator: deltas should stay close
    assert abs(z1 - z2) < 1.0


# ── 2. Sigma primitive ─────────────────────────────────────────────────────

def test_sigma_score_weights():
    # 0.3·structural + 0.7·behavior
    assert abs(sigma_score(10, 0) - 3.0) < 0.001
    assert abs(sigma_score(0, 10) - 7.0) < 0.001
    assert abs(sigma_score(10, 10) - 10.0) < 0.001

def test_patent_examiner_trigger_at_5_sigma():
    assert patent_examiner_trigger(5.0) is True
    assert patent_examiner_trigger(4.99) is False
    assert patent_examiner_trigger(10) is True


# ── 3. Anchor cases for escalation cost ───────────────────────────────────

def test_escalation_anchor_sigma_neg10():
    # |n|=10, in low band → 2^10 = 1024
    assert escalation_cost(-10) == 1024

def test_escalation_anchor_sigma_0():
    # |n|=0 → 2^0 = 1
    assert escalation_cost(0) == 1

def test_escalation_anchor_sigma_3():
    # |n|=3 → 2^3 = 8
    assert escalation_cost(3) == 8

def test_escalation_anchor_sigma_5():
    # |n|=5 → 2^5 = 32
    assert escalation_cost(5) == 32

def test_escalation_anchor_sigma_10():
    # boundary: |n|=10 → 2^10 = 1024
    assert escalation_cost(10) == 1024

def test_escalation_anchor_sigma_20():
    # |n|=20 → 1024 · 3^10 = 1024 · 59049 = 60,466,176
    assert escalation_cost(20) == 1024 * (3 ** 10)

def test_escalation_anchor_sigma_30():
    # |n|=30 → 1024 · 3^10 · 5^10 ≈ 5.9 × 10^14
    expected = 1024 * (3 ** 10) * (5 ** 10)
    assert escalation_cost(30) == expected

def test_escalation_negative_and_positive_equal():
    assert escalation_cost(-15) == escalation_cost(15)
    assert escalation_cost(-25) == escalation_cost(25)


# ── 4. BDF composite ──────────────────────────────────────────────────────

def test_bdf_full_pass():
    # All factors = 1 → BDF = |madz|
    assert abs(bdf(1.0, 5.0, 1.0, 1.0) - 5.0) < 0.001

def test_bdf_zero_floor_blocks_artifact():
    # intent below floor → BDF = 0 regardless of headline
    assert bdf(0.001, 10.0, 1.0, 1.0) == 0.0
    assert bdf(1.0, 10.0, 0.0, 1.0) == 0.0
    assert bdf(1.0, 10.0, 1.0, 0.0) == 0.0

def test_bdf_uses_absolute_madz():
    # |MADZ| means negative σ contributes positively to BDF
    assert bdf(1.0, -5.0, 1.0, 1.0) == bdf(1.0, 5.0, 1.0, 1.0)

def test_bdf_blocked_predicate():
    assert bdf_blocked(0.001, 1.0, 1.0) is True
    assert bdf_blocked(1.0, 1.0, 1.0) is False

def test_bdf_explain_identifies_weakest():
    out = bdf_explain(0.001, 5.0, 1.0, 1.0)
    assert out["blocked"] is True
    assert out["weakest"] == "intent"


# ── 5. Thresholds + detonation_gate ───────────────────────────────────────

def test_thresholds_has_all_six_tiers():
    expected = {"internal_note", "internal_artifact", "client",
                 "published", "doctrine", "civilization"}
    assert expected == set(THRESHOLDS.keys())

def test_detonation_gate_blocks_below_min_sigma():
    v = detonation_gate(2.0, tier="published")  # published requires +5
    assert v.status == "BLOCK"

def test_detonation_gate_passes_at_min():
    v = detonation_gate(5.0, tier="published", patent_verdict="novel")
    assert v.status == "PASS"

def test_detonation_gate_requires_patent_at_doctrine():
    # doctrine tier requires Patent Examiner = "novel"
    v_fail = detonation_gate(9.0, tier="doctrine", patent_verdict="not_required")
    v_pass = detonation_gate(9.0, tier="doctrine", patent_verdict="novel")
    assert v_fail.status == "BLOCK"
    assert v_pass.status == "PASS"

def test_banned_phrase_detection():
    found, hits = has_banned_phrase("We unlock seamless transformation.")
    assert found is True
    assert "unlock" in hits

def test_banned_phrase_clean_text():
    found, hits = has_banned_phrase("HED Forge ships predictive diagnostics at 30ms p99.")
    assert found is False


# ── 6. RIG-L composite + labels ───────────────────────────────────────────

def test_rig_l_composite_basic():
    # Mean of top-6: [10, 8, 7, 5, 4, 3] → mean = 6.166
    layer = {"cognitive": [10, 8, 7, 5, 4, 3, 2, 1]}
    rl = rig_l_composite(layer)
    assert 6.0 < rl < 7.0

def test_rig_l_hard_block_penalty():
    layer = {"cognitive": [10, 8, 7, 5, 4, 3]}
    # 1 hard-block = 30% penalty
    rl_clean = rig_l_composite(layer, hard_blocks=0)
    rl_blocked = rig_l_composite(layer, hard_blocks=1)
    assert abs(rl_blocked - rl_clean * 0.7) < 0.01

def test_rig_l_label_bands():
    assert rig_l_label(2.0) == "block"
    assert rig_l_label(3.5) == "pass_needs_strengthening"
    assert rig_l_label(4.5) == "category_rupture"
    assert rig_l_label(7.0) == "rig_signature"
    assert rig_l_label(9.0) == "frontier_artifact"
    assert rig_l_label(15.0) == "doctrine_artifact"


# ── 7. DeviationEngine base class ─────────────────────────────────────────

def test_deviation_engine_pass():
    eng = DeviationEngine(
        id=1, name="TestEngine", layer="cognitive", target="output",
        raw_fn=lambda artifact: 100.0,
        baseline_fn=lambda: [50.0, 51.0, 52.0, 53.0, 54.0],
        threshold=3.0,
    )
    result = eng.score("any")
    assert isinstance(result, EngineResult)
    assert result.engine == "TestEngine"
    assert result.status == "PASS"
    assert result.madz > 3.0  # well above baseline

def test_deviation_engine_block():
    eng = DeviationEngine(
        id=2, name="TestEngine", layer="cognitive", target="output",
        raw_fn=lambda artifact: 51.0,  # at median → 0σ
        baseline_fn=lambda: [50.0, 51.0, 52.0, 53.0, 54.0],
        threshold=3.0,
    )
    result = eng.score("any")
    assert result.status == "BLOCK"

def test_deviation_engine_hard_block_predicate():
    def banned(artifact):
        return "banned" in artifact

    eng = DeviationEngine(
        id=3, name="TestEngine", layer="physics", target="state",
        raw_fn=lambda artifact: 100.0,
        baseline_fn=lambda: [50.0, 51.0, 52.0, 53.0, 54.0],
        hard_blocks=(banned,),
        is_gate=True,
    )
    result = eng.score("this artifact contains banned content")
    assert result.status == "HARD_BLOCK"

def test_deviation_engine_to_dict():
    eng = DeviationEngine(
        id=4, name="TestEngine", layer="cognitive", target="output",
        raw_fn=lambda artifact: 100.0,
        baseline_fn=lambda: [50.0, 51.0, 52.0],
    )
    d = eng.score("x").to_dict()
    assert d["engine"] == "TestEngine"
    assert d["status"] == "PASS"
    assert "madz" in d


# ── 8. 40-engine registry ─────────────────────────────────────────────────

def test_registry_has_exactly_40_engines():
    assert len(ENGINE_REGISTRY) == 40

def test_registry_engine_count_by_layer():
    counts = engine_count_by_layer()
    assert counts["cognitive"] == 20
    assert counts["nature"] == 10
    assert counts["physics"] == 10

def test_registry_resolve_by_id():
    e = resolve_engine("cognitive", 1)
    assert e.name == "GravityEscape"

def test_registry_resolve_by_codename():
    e = resolve_by_codename("MechanismFurnace")
    assert e.id == 4

def test_registry_resolve_by_slug():
    e = resolve_by_slug("reality_anchor")
    assert e.name == "RealityAnchor"

def test_registry_physics_engines_are_gates():
    for e in physics_engines():
        assert e.is_gate is True
        assert e.layer == "physics"
    assert len(physics_engines()) == 10

def test_registry_no_duplicate_ids():
    ids = [e.id for e in ENGINE_REGISTRY]
    assert len(ids) == len(set(ids))

def test_registry_no_duplicate_codenames():
    names = [e.name for e in ENGINE_REGISTRY]
    assert len(names) == len(set(names))

def test_registry_no_duplicate_slugs():
    slugs = [e.slug for e in ENGINE_REGISTRY]
    assert len(slugs) == len(set(slugs))

def test_registry_ids_are_1_to_40():
    ids = sorted([e.id for e in ENGINE_REGISTRY])
    assert ids == list(range(1, 41))


# ── Manual runner for environments without pytest ─────────────────────────
if __name__ == "__main__":
    import inspect
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
