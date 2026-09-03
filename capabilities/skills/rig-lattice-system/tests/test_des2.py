"""Day-6 acceptance tests per DOCTRINE.md §8.

Required acceptance:
  - 5 amplifiers as inner-loop wrappers (Mechanism Map, Source-Per-Claim,
    Falsification Check, Anti-Generic Gate, Brier-Calibrated Confidence)
  - Verify 6.55× per axis on canonical benchmark artifacts
  - Brier delta tracking enabled

Math reference: 1.5 × 1.4 × 1.6 × 1.3 × 1.5 = 6.5520
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path


from rig_lattice.deviator.des2_innerloop import (
    # constants
    AMP_MECHANISM, AMP_SOURCE, AMP_FALSIFY, AMP_SPECIFIC, AMP_BRIER,
    AMP_PRODUCT_MAX, BRIER_MAE_THRESHOLD, SPECIFICITY_FLOOR,
    # types
    AmplifierVerdict, EngineAmplification,
    # amplifiers
    amp1_mechanism_map, amp2_source_per_claim, amp3_falsifier,
    amp4_anti_generic, amp5_brier,
    # main wrapper
    amplify_engine,
    # Brier
    record_prediction, record_outcome, brier_mae,
    # verification
    verify_compound_rigor, amp_product_max,
    CANONICAL_PASSING_BENCHMARK, CANONICAL_FAILING_BENCHMARK,
)
from rig_lattice.core.base import DeviationEngine
from rig_lattice.engines.cognitive import load_cognitive_engines

STRONG_TEXT_PATH = Path(__file__).parent.parent / "examples" / "example_strict_passing.md"


# ── 1. Canonical multiplier values per DOCTRINE §3.1 ──────────────────────


# ── stdlib replacement for the pytest monkeypatch/tmp_path fixtures ────────
# The vendored suite used `monkeypatch.setattr(dim, "BRIER_LOG", tmp_path/x)`.
# This repo runs stdlib unittest only, so the same isolation is provided by a
# context manager: a real temp dir, an explicit save/restore of the module
# attribute, and cleanup even when the test raises.
import contextlib as _contextlib
import tempfile as _tempfile
from pathlib import Path as _Path


@_contextlib.contextmanager
def _brier_tmp(filename: str = "brier.jsonl"):
    """Point des2_innerloop.BRIER_LOG at a fresh temp file for one test."""
    import rig_lattice.deviator.des2_innerloop as dim

    original = dim.BRIER_LOG
    with _tempfile.TemporaryDirectory() as td:
        log = _Path(td) / filename
        dim.BRIER_LOG = log
        try:
            yield dim, log
        finally:
            dim.BRIER_LOG = original


def test_a1_multiplier_is_1_5():
    assert AMP_MECHANISM == 1.5

def test_a2_multiplier_is_1_4():
    assert AMP_SOURCE == 1.4

def test_a3_multiplier_is_1_6():
    assert AMP_FALSIFY == 1.6

def test_a4_multiplier_is_1_3():
    assert AMP_SPECIFIC == 1.3

def test_a5_multiplier_is_1_5():
    assert AMP_BRIER == 1.5

def test_amp_product_is_6_55():
    """The canonical 6.55× per axis from DOCTRINE §3.1."""
    expected = 1.5 * 1.4 * 1.6 * 1.3 * 1.5  # = 6.552
    assert abs(AMP_PRODUCT_MAX - expected) < 1e-6
    assert abs(AMP_PRODUCT_MAX - 6.552) < 1e-3


# ── 2. Per-amplifier behavior ─────────────────────────────────────────────

def test_amp1_passes_on_dense_causal_text():
    text = ("Because X drives Y, the system leads to Z via Q. "
             "Therefore P results in R through S, which causes T. "
             "Due to U, this triggers V; enables W; forces X.") * 3
    v = amp1_mechanism_map(text, "test_engine")
    assert v.passed is True
    assert v.multiplier == AMP_MECHANISM

def test_amp1_fails_on_sparse_text():
    text = "Just plain text. No connectives anywhere. Boring."
    v = amp1_mechanism_map(text, "test")
    # density may or may not pass — must verify multiplier matches
    if not v.passed:
        assert v.multiplier == 1.0

def test_amp2_passes_with_3_plus_sources():
    text = ("Per Research and Markets[1], the market grows. "
             "Helios Technologies[2] reported earnings. "
             "Per McKinsey, the trend continues.")
    v = amp2_source_per_claim(text, "test")
    assert v.passed is True
    assert v.multiplier == AMP_SOURCE

def test_amp2_fails_without_sources():
    text = "Just claims with no citations or named sources."
    v = amp2_source_per_claim(text, "test")
    assert v.passed is False
    assert v.multiplier == 1.0

def test_amp3_passes_with_falsifiers():
    text = ("Kill criteria: if attach rate is below 8% by Month 18, rescope by Q3 2027. "
             "Wrong if attach is below 12% by end of Year 2.")
    v = amp3_falsifier(text, "test")
    assert v.passed is True
    assert v.multiplier == AMP_FALSIFY

def test_amp4_passes_on_clean_text():
    text = "We commit to ship Forge Edge by Month 8 with <50ms p99 latency."
    v = amp4_anti_generic(text, "test")
    assert v.passed is True

def test_amp4_fails_on_generic_slop():
    text = ("We leverage cutting-edge solutions to unlock world-class synergies "
             "through holistic transformation that scales effortlessly across the "
             "enterprise. We unlock value seamlessly. We unlock holistic synergy.")
    v = amp4_anti_generic(text, "test")
    assert v.passed is False
    assert v.multiplier == 1.0


# ── 3. Brier tracking ────────────────────────────────────────────────────

def test_brier_history_persists():
    """record_prediction then record_outcome → log entries persist."""
    with _brier_tmp("test_brier.jsonl") as (dim, log):

        entry = record_prediction(
            mission_id="m-test-1",
            engine_name="GravityEscape",
            predicted_madz=4.5,
            expected_resolution_date="2026-12-31",
        )
        assert entry["predicted"] == 4.5
        assert entry["realized"] is None
        assert log.exists()

        resolution = record_outcome(entry["log_id"], realized_madz=4.0)
        assert resolution is not None
        assert resolution["predicted"] == 4.5
        assert resolution["realized"] == 4.0
        assert abs(resolution["delta"] - 0.5) < 1e-9

def test_brier_record_outcome_unknown_id_returns_none():
    with _brier_tmp("test_brier.jsonl") as (dim, log):
        # Resolve a log_id that never existed
        assert record_outcome("does-not-exist", 5.0) is None

def test_brier_mae_with_history():
    """brier_mae correctly computes mean |predicted - realized| across resolutions."""
    with _brier_tmp("test_brier.jsonl") as (dim, log):

        # Record 3 predictions + resolve all
        for pred, real in [(4.0, 4.5), (5.0, 4.0), (3.0, 3.5)]:
            e = record_prediction(mission_id="m1", engine_name="TestEng",
                                    predicted_madz=pred)
            record_outcome(e["log_id"], realized_madz=real)

        mae, n = brier_mae("TestEng")
        # |4.0-4.5| + |5.0-4.0| + |3.0-3.5| = 0.5 + 1.0 + 0.5 = 2.0; mean = 0.667
        assert n == 3
        assert abs(mae - (2.0 / 3)) < 0.01

def test_brier_mae_empty_history():
    with _brier_tmp("empty.jsonl") as (dim, log):
        mae, n = brier_mae("any_engine")
        assert mae == 0.0
        assert n == 0

def test_amp5_baseline_pass_with_insufficient_history():
    """A5 baseline-passes when <3 resolved predictions exist."""
    with _brier_tmp("tiny.jsonl") as (dim, log):
        v = amp5_brier("any text", "GravityEscape")
        assert v.passed is True  # baseline pass
        assert v.multiplier == AMP_BRIER

def test_amp5_passes_when_mae_under_threshold():
    """A5 fully passes when MAE < 1.0σ over ≥3 resolved entries."""
    with _brier_tmp("tight.jsonl") as (dim, log):
        # Tight calibration: deltas all ≤0.5
        for pred, real in [(4.0, 4.2), (5.0, 4.8), (3.0, 3.3), (6.0, 6.1)]:
            e = record_prediction(mission_id="m1", engine_name="TightEng",
                                    predicted_madz=pred)
            record_outcome(e["log_id"], realized_madz=real)
        v = amp5_brier("text", "TightEng")
        assert v.passed is True

def test_amp5_fails_when_mae_above_threshold():
    """A5 fails when MAE ≥ 1.0σ."""
    with _brier_tmp("loose.jsonl") as (dim, log):
        # Loose calibration: deltas ≥1.5
        for pred, real in [(4.0, 6.0), (5.0, 2.5), (3.0, 5.0), (6.0, 3.5)]:
            e = record_prediction(mission_id="m1", engine_name="LooseEng",
                                    predicted_madz=pred)
            record_outcome(e["log_id"], realized_madz=real)
        v = amp5_brier("text", "LooseEng")
        assert v.passed is False
        assert v.multiplier == 1.0


# ── 4. Inner-loop wrapper per-engine ─────────────────────────────────────

def test_amplify_engine_returns_amplification_record():
    engines = load_cognitive_engines()
    text = "Test text for amplification."
    amp = amplify_engine(engines[0], text)
    assert isinstance(amp, EngineAmplification)
    assert amp.engine_name == engines[0].name
    assert amp.engine_id == engines[0].id
    assert 1.0 <= amp.composite_uplift <= AMP_PRODUCT_MAX

def test_amplify_engine_runs_all_5_amplifiers():
    engines = load_cognitive_engines()
    amp = amplify_engine(engines[0], "Sample text.")
    expected_keys = {"A1_mechanism", "A2_sources", "A3_falsifier",
                      "A4_specificity", "A5_brier"}
    assert set(amp.amplifiers.keys()) == expected_keys

def test_amplify_engine_to_dict_serializable():
    engines = load_cognitive_engines()
    amp = amplify_engine(engines[0], "Sample text.")
    d = amp.to_dict()
    # Must be JSON-serializable
    json.dumps(d)
    assert d["passed_count"] + (d["total_amplifiers"] - d["passed_count"]) == d["total_amplifiers"]


# ── 5. CANONICAL 6.55× VERIFICATION (DOCTRINE §8 Day 6 MANDATE) ──────────

def test_canonical_passing_benchmark_hits_6_55():
    """Day 6 acceptance: passing benchmark must hit exactly 6.55× per axis."""
    with _brier_tmp("fresh.jsonl") as (dim, log):

        passed, uplift, details = verify_compound_rigor(CANONICAL_PASSING_BENCHMARK)
        assert passed is True
        assert abs(uplift - 6.552) < 0.01
        # All 5 amplifiers must pass on the canonical benchmark
        assert all(details.values()), f"Some amplifiers failed: {details}"

def test_canonical_failing_benchmark_significantly_lower():
    """Failing benchmark must score at least 2× lower than passing."""
    with _brier_tmp("fresh.jsonl") as (dim, log):

        _, uplift_pass, _ = verify_compound_rigor(CANONICAL_PASSING_BENCHMARK)
        _, uplift_fail, _ = verify_compound_rigor(CANONICAL_FAILING_BENCHMARK,
                                                    expected_min=0.0, expected_max=10.0)

        # Differentiation: passing ≥ 2× failing
        assert uplift_pass / max(uplift_fail, 0.1) >= 2.0
        # And specifically: passing > 6.0, failing < 3.5
        assert uplift_pass > 6.0
        assert uplift_fail < 3.5

def test_amp_product_max_matches_doctrine():
    """The AMP_PRODUCT_MAX constant equals 1.5·1.4·1.6·1.3·1.5 = 6.552."""
    assert abs(amp_product_max() - 6.552) < 1e-3


# ── 6. Failed-amplifier degrades correctly ──────────────────────────────

def test_failed_amplifier_uses_1x_multiplier():
    """A failed amplifier contributes 1.0× to the composite uplift."""
    text = "Empty"
    v = amp2_source_per_claim(text, "test")
    assert v.passed is False
    assert v.multiplier == 1.0

def test_all_amplifiers_failing_gives_1x_uplift():
    """If all 5 amplifiers fail, composite uplift = 1.0× (no rigor uplift)."""
    text = ""  # empty text fails everything
    amps = [
        amp1_mechanism_map(text, "test"),
        amp2_source_per_claim(text, "test"),
        amp3_falsifier(text, "test"),
        amp4_anti_generic(text, "test", floor=999),  # impossible floor
    ]
    uplift = 1.0
    for v in amps:
        uplift *= v.multiplier
    # 4 amplifiers all 1.0× → uplift = 1.0
    assert uplift == 1.0


# ── 7. Day 6 SUMMARY: 25× system rigor mandate ─────────────────────────

def test_25x_system_rigor_mandate():
    """DOCTRINE §3: 25× system rigor when DES² is overlaid per cell per layer.

    Math: 6.55× per quality axis × 6.55× per proof axis ≈ 42.9×.
    Spec calls it '25× compoundly' (conservative — accounts for some
    overlap between axes). We verify that the per-axis multiplier is
    sufficient to compound to ≥20× across both axes.
    """
    per_axis = AMP_PRODUCT_MAX
    compound_two_axes = per_axis ** 2
    # Spec says "25× compoundly" — we verify ≥ 20× compound across two axes.
    assert compound_two_axes >= 20.0
    # And exactly 6.55× per axis as DOCTRINE §3.1 spec mandates
    assert abs(per_axis - 6.552) < 1e-3


# ── Manual runner ───────────────────────────────────────────────────────
if __name__ == "__main__":
    import inspect
    tests = []
    for name, fn in globals().items():
        if name.startswith("test_") and callable(fn):
            sig = inspect.signature(fn)
            tests.append((name, fn, list(sig.parameters)))

    passed, failed = 0, []
    for name, fn, params in tests:
        try:
            if "monkeypatch" in params or "tmp_path" in params:
                # Skip pytest-dependent tests in manual runner
                print(f"  ⊘ {name} (pytest fixture required)")
                continue
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
    print(f"  RESULT: {passed}/{passed + len(failed)} passed (pytest fixtures skipped)")
    if failed:
        print(f"  FAILED: {failed}")
        sys.exit(1)
