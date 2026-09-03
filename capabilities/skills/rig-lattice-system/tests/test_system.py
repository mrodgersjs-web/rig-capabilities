"""System tests — 7 levels × 28 archetypes + orchestrator + integrations."""
from __future__ import annotations
import sys
from pathlib import Path


from rig_lattice.enterprise.iqrsqpi import BMSMode
from rig_lattice.system import (
    LEVELS, Level, L1_CAPTURE, L2_PROCESS, L3_CREATE, L4_DISTRIBUTE,
    L5_ENGAGE, L6_CONVERT, L7_AUTONOMIZE,
    ARCHETYPES, get_archetype, list_archetypes_for_level,
    run_system, run_level, SystemRun,
)
from rig_lattice.enterprise.integrations import (
    integrations_status,
    langsmith_emit, langsmith_available,
    langfuse_emit, langfuse_available,
    crewai_dispatch, crewai_available, list_crews,
    litellm_route, litellm_available,
    otel_span, otel_available,
)

STRONG = Path(__file__).parent.parent / "examples" / "example_strict_passing.md"


# ── 1. Levels ───────────────────────────────────────────────────────────

def test_seven_levels_in_canonical_order():
    assert len(LEVELS) == 7
    assert LEVELS[0] == L1_CAPTURE
    assert LEVELS[-1] == L7_AUTONOMIZE


# ── 2. Archetypes ───────────────────────────────────────────────────────

def test_28_archetypes_registered():
    assert len(ARCHETYPES) == 28

def test_each_level_has_4_archetypes():
    for level in LEVELS:
        modes = {a.id.mode for a in list_archetypes_for_level(level)}
        assert modes == {BMSMode.A1, BMSMode.A2, BMSMode.A3, BMSMode.A4}

def test_get_archetype_by_level_and_mode():
    a = get_archetype(L1_CAPTURE, BMSMode.A1)
    assert a.id.level == L1_CAPTURE
    assert a.id.mode == BMSMode.A1
    assert callable(a.fn)

def test_a4_archetypes_require_human_gate():
    for level in LEVELS:
        a = get_archetype(level, BMSMode.A4)
        assert a.requires_human_gate is True


# ── 3. L1 CAPTURE ───────────────────────────────────────────────────────

def test_l1_a1_reads_file():
    if not STRONG.exists():
        return
    result = run_level(L1_CAPTURE, {"source": str(STRONG)}, BMSMode.A1)
    assert result.ok is True
    assert result.output["word_count"] > 100

def test_l1_a1_handles_missing_file():
    result = run_level(L1_CAPTURE, {"source": "/does/not/exist.md"}, BMSMode.A1)
    assert result.ok is False

def test_l1_a1_reads_stdin():
    result = run_level(L1_CAPTURE,
                         {"source": "-", "stdin_text": "Hello world"}, BMSMode.A1)
    assert result.ok is True
    assert result.output["text"] == "Hello world"

def test_l1_a4_returns_human_instruction():
    result = run_level(L1_CAPTURE, {"source": "manual"}, BMSMode.A4)
    assert result.ok is True
    assert result.output["requires_human"] is True


# ── 4. L2 PROCESS ───────────────────────────────────────────────────────

def test_l2_a1_audits_text():
    if not STRONG.exists():
        return
    text = STRONG.read_text()
    state = {"L1_CAPTURE": {"text": text}}
    result = run_level(L2_PROCESS, state, BMSMode.A1)
    assert result.ok is True
    assert "audit" in result.output
    assert "rig_l" in result.output

def test_l2_a1_blocks_without_l1():
    result = run_level(L2_PROCESS, {}, BMSMode.A1)
    assert result.ok is False


# ── 5. L3 CREATE ────────────────────────────────────────────────────────

def test_l3_a1_produces_variants():
    if not STRONG.exists():
        return
    from rig_lattice.deviator.auditor import audit_all
    text = STRONG.read_text()
    audit = audit_all(text, llm_enabled=False)
    state = {"L1_CAPTURE": {"text": text}, "L2_PROCESS": {"audit": audit}}
    result = run_level(L3_CREATE, state, BMSMode.A1)
    assert result.ok is True
    assert len(result.output["variants"]) >= 1


# ── 6. L4 DISTRIBUTE ────────────────────────────────────────────────────

def test_l4_a1_emits_receipt():
    if not STRONG.exists():
        return
    from rig_lattice.deviator.auditor import audit_all
    text = STRONG.read_text()
    audit = audit_all(text, llm_enabled=False)
    state = {
        "source": str(STRONG),
        "L1_CAPTURE": {"text": text},
        "L2_PROCESS": {"audit": audit, "des2": {}},
        "tier": "client",
    }
    result = run_level(L4_DISTRIBUTE, state, BMSMode.A1)
    assert result.ok is True
    assert "receipt" in result.output


# ── 7. L5 ENGAGE ────────────────────────────────────────────────────────

def test_l5_a1_surfaces_blockers():
    if not STRONG.exists():
        return
    from rig_lattice.deviator.auditor import audit_all
    text = STRONG.read_text()
    audit = audit_all(text, llm_enabled=False)
    state = {"L1_CAPTURE": {"text": text}, "L2_PROCESS": {"audit": audit}}
    result = run_level(L5_ENGAGE, state, BMSMode.A1)
    assert result.ok is True
    assert "blockers" in result.output
    assert "next_actions" in result.output


# ── 8. L6 CONVERT ───────────────────────────────────────────────────────

def test_l6_a1_produces_final_text():
    if not STRONG.exists():
        return
    from rig_lattice.deviator.auditor import audit_all
    text = STRONG.read_text()
    audit = audit_all(text, llm_enabled=False)
    state = {"L1_CAPTURE": {"text": text}, "L2_PROCESS": {"audit": audit}}
    result = run_level(L6_CONVERT, state, BMSMode.A1)
    assert result.ok is True
    assert "final_text" in result.output
    assert "final_audit" in result.output


# ── 9. L7 AUTONOMIZE ────────────────────────────────────────────────────

def test_l7_a1_kicks_daemon_and_logs_prediction():
    state = {
        "mission_id": "test-l7",
        "L6_CONVERT": {"final_audit": {"rig_l": 5.5, "hard_blocks": 0}},
    }
    result = run_level(L7_AUTONOMIZE, state, BMSMode.A1)
    assert result.ok is True
    assert "prediction_logged" in result.output


# ── 10. Orchestrator end-to-end ─────────────────────────────────────────

def test_system_run_all_seven_levels_a1():
    if not STRONG.exists():
        return
    result = run_system(source=str(STRONG), confidence=0.85)
    assert result.ok is True
    assert result.bms_mode == BMSMode.A1
    assert len(result.levels) == 7
    assert all(l.ok for l in result.levels)

def test_system_run_bms_route_confidence_a3():
    if not STRONG.exists():
        return
    result = run_system(source=str(STRONG), confidence=0.30)
    assert result.bms_mode == BMSMode.A3

def test_system_run_force_a4():
    if not STRONG.exists():
        return
    result = run_system(source=str(STRONG), confidence=0.99, force_a4=True)
    assert result.bms_mode == BMSMode.A4


# ── 11. Integrations ────────────────────────────────────────────────────

def test_integrations_status_returns_dict():
    s = integrations_status()
    for k in ("langsmith", "langfuse", "crewai", "litellm", "opentelemetry"):
        assert k in s

def test_langsmith_emit_falls_back_to_local():
    result = langsmith_emit("test_event", {"foo": "bar"})
    assert "destination" in result or "sent_to" in result

def test_langfuse_emit_falls_back_to_local():
    result = langfuse_emit("test_event", {"foo": "bar"}, cost_usd=0.001)
    assert "destination" in result or "sent_to" in result

def test_crewai_has_canonical_crews():
    crews = list_crews()
    assert "outcome_observer" in crews
    assert "plus20_swarm" in crews
    assert "coral_reef_mesh" in crews
    assert "adversarial_reviewer" in crews

def test_crewai_dispatch_routes_through_handler():
    result = crewai_dispatch("plus20_swarm", {"weakest_engines": ["test"]})
    assert "crew" in result or "destination" in result

def test_litellm_route_returns_result():
    # Will fall back to offline mode → score 50
    import os
    os.environ["RIG_DV_OFFLINE"] = "1"
    result = litellm_route("test prompt", cost_cap_usd=0.0)
    assert result.ok is True
    del os.environ["RIG_DV_OFFLINE"]

def test_otel_span_context_manager():
    with otel_span("test_span", level="L1", mode="A1") as span:
        assert span.name == "test_span"
        assert "level" in span.attributes
    assert span.ended_at > 0


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
