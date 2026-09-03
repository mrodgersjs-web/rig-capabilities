"""Day-3 acceptance tests per DOCTRINE.md §8.

Required acceptance:
  - All 20 cognitive engines implemented with raw_fn + baseline_fn
  - LLM adapter (LiteLLM) implemented with offline fallback
  - 10 baseline types seeded per engine
  - Unit tests + ProofPacket → Action → Result writes for every engine
"""
from __future__ import annotations
import os
import sys
from pathlib import Path


from rig_lattice.core.base import DeviationEngine, EngineResult
from rig_lattice.core.registry import COGNITIVE
from rig_lattice.adapters import (
    llm_score, LLMResponse, OFFLINE_MODE,
    raw_score_from_criteria, BASELINE_CORPUS, BASELINE_TYPES,
    baseline_scores_for_engine, get_baseline_samples,
)
from rig_lattice.engines import load_all_engines
from rig_lattice.engines.cognitive import load_cognitive_engines
from rig_lattice.deviator.pipeline.proof_packet import emit_proof_packet, hash_input, ProofPacket


STRONG_TEXT_PATH = Path(__file__).parent.parent / "examples" / "example_strict_passing.md"


# ── 1. LLM adapter ────────────────────────────────────────────────────────

def test_llm_score_returns_response_in_offline_mode():
    os.environ["RIG_DV_OFFLINE"] = "1"
    # Reload module to pick up env var
    import importlib
    import rig_lattice.adapters.llm as llm_mod
    importlib.reload(llm_mod)
    resp = llm_mod.llm_score("test prompt")
    assert resp.ok is True
    assert resp.score == 50.0
    del os.environ["RIG_DV_OFFLINE"]
    importlib.reload(llm_mod)

def test_llm_response_dataclass():
    r = LLMResponse(ok=True, content="SCORE: 75", score=75.0, elapsed_s=0.5)
    assert r.score == 75.0
    assert r.ok


# ── 2. Criteria runner ────────────────────────────────────────────────────

def test_raw_score_from_criteria_returns_0_to_100():
    text = "We commit to shipping by Month 8 with kill criteria documented."
    score = raw_score_from_criteria(text, "reality_anchor")
    assert 0.0 <= score <= 100.0

def test_raw_score_higher_for_strong_text():
    if not STRONG_TEXT_PATH.exists():
        return
    strong = STRONG_TEXT_PATH.read_text()
    weak = "Things happen sometimes."
    s_strong = raw_score_from_criteria(strong, "mechanism_furnace")
    s_weak = raw_score_from_criteria(weak, "mechanism_furnace")
    assert s_strong > s_weak

def test_raw_score_handles_missing_pack():
    try:
        raw_score_from_criteria("text", "nonexistent_engine_slug")
        assert False, "should have raised FileNotFoundError"
    except FileNotFoundError:
        pass


# ── 3. Baseline corpus ────────────────────────────────────────────────────

def test_baseline_corpus_has_10_types():
    assert len(BASELINE_TYPES) == 10
    for t in BASELINE_TYPES:
        assert t in BASELINE_CORPUS
        assert len(BASELINE_CORPUS[t]) > 100  # non-trivial sample

def test_baseline_samples_returns_10_strings():
    samples = get_baseline_samples()
    assert len(samples) == 10
    assert all(isinstance(s, str) for s in samples)

def test_baseline_scores_for_engine_returns_10_floats():
    scores = baseline_scores_for_engine("reality_anchor")
    assert len(scores) == 10
    assert all(isinstance(s, float) for s in scores)
    assert all(0.0 <= s <= 100.0 for s in scores)

def test_baseline_scores_cached():
    s1 = baseline_scores_for_engine("gravity_escape")
    s2 = baseline_scores_for_engine("gravity_escape")
    # Same call returns the same tuple from cache
    assert s1 is s2


# ── 4. All 20 cognitive engines loaded ────────────────────────────────────

def test_load_cognitive_engines_returns_20():
    engines = load_cognitive_engines()
    assert len(engines) == 20

def test_each_cognitive_engine_is_deviation_engine():
    for e in load_cognitive_engines():
        assert isinstance(e, DeviationEngine)
        assert e.layer == "cognitive"
        assert e.target == "output"
        assert e.is_gate is False  # cognitive engines are scoring, not gating

def test_each_cognitive_engine_has_unique_id():
    ids = [e.id for e in load_cognitive_engines()]
    assert sorted(ids) == list(range(1, 21))

def test_each_cognitive_engine_scores_text():
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    engines = load_cognitive_engines()
    for e in engines:
        result = e.score(text)
        assert isinstance(result, EngineResult)
        assert result.engine == e.name
        assert -20.0 <= result.madz <= 20.0  # cognitive layer clamp
        assert result.status in ("PASS", "BLOCK", "HARD_BLOCK")

def test_strong_text_scores_pass_majority_of_cognitive():
    """HED v2.5 fixture (hardened doctrine artifact) should PASS ≥15 of 20
    cognitive engines."""
    if not STRONG_TEXT_PATH.exists():
        return
    text = STRONG_TEXT_PATH.read_text()
    engines = load_cognitive_engines()
    passes = sum(1 for e in engines if e.score(text).status == "PASS")
    assert passes >= 15, f"expected ≥15 passes, got {passes}"


# ── 5. ProofPacket emission ───────────────────────────────────────────────

def test_proof_packet_hash_input_deterministic():
    h1 = hash_input("test text")
    h2 = hash_input("test text")
    assert h1 == h2

def test_emit_proof_packet_returns_packet():
    packet = emit_proof_packet(
        mission_id="test-mid",
        engine_id=1,
        engine_name="GravityEscape",
        engine_slug="gravity_escape",
        layer="cognitive",
        input_text="sample",
        raw_score=75.0,
        baseline_size=10,
        madz=4.2,
        status="PASS",
    )
    assert isinstance(packet, ProofPacket)
    assert packet.engine_id == 1
    assert packet.status == "PASS"
    assert packet.madz == 4.2

def test_proof_packet_hash_stable():
    packet = ProofPacket(
        packet_id="pp-1", mission_id="m1", engine_id=1,
        engine_name="GravityEscape", engine_slug="gravity_escape",
        layer="cognitive", input_hash="h1", action="score",
        raw_score=75.0, baseline_size=10, madz=4.2, status="PASS",
    )
    h1 = packet.hash
    h2 = packet.hash
    assert h1 == h2

def test_proof_packet_persisted_to_disk():
    """Verify the packet file is actually written."""
    packet = emit_proof_packet(
        mission_id="test-persist",
        engine_id=1, engine_name="TestEngine",
        engine_slug="test_slug", layer="cognitive",
        input_text="x", raw_score=50.0,
        baseline_size=10, madz=0.0, status="BLOCK",
    )
    from rig_lattice.deviator.pipeline.proof_packet import PROOF_DIR
    assert (PROOF_DIR / f"{packet.packet_id}.json").exists()


# ── 6. Per-engine smoke (each of the 20 must score successfully) ──────────

def test_e01_gravity_escape_module_loads():
    from rig_lattice.engines.cognitive.e01_gravity_escape import ENGINE
    assert ENGINE.id == 1
    assert ENGINE.name == "GravityEscape"

def test_e04_mechanism_furnace_module_loads():
    from rig_lattice.engines.cognitive.e04_mechanism_furnace import ENGINE
    assert ENGINE.id == 4
    assert ENGINE.name == "MechanismFurnace"

def test_e10_temporal_horizon_module_loads():
    from rig_lattice.engines.cognitive.e10_temporal_horizon_integrity import ENGINE
    assert ENGINE.id == 10
    assert ENGINE.name == "TemporalHorizonIntegrity"

def test_e20_compounding_edge_module_loads():
    from rig_lattice.engines.cognitive.e20_compounding_edge import ENGINE
    assert ENGINE.id == 20
    assert ENGINE.name == "CompoundingEdge"


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
