"""A2 HYBRID tests.

Runs under pytest if installed, and also standalone:

    python3 platform/archetypes/a2_hybrid/tests/test_a2.py

Covers the schema-bounded LLM chain end-to-end with NO API key (offline mock),
the strict-schema validator (accept + reject), the schema_failed stop path,
the confidence-collapse escalation to A3, the UNKNOWN-intent escalation,
deterministic SHA-256 proof that binds to the EXACT model bytes + tamper
detection, the contract-frozen guarantee (A2 imports A1's types, never
redefines them), and conditional approval at A2.7.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Standalone execution: the top dir is named "platform" (collides with the
# stdlib module), so add archetypes/ and import packages by their own names.
_HERE = Path(__file__).resolve()
_ARCHETYPES_DIR = _HERE.parents[2]  # .../platform/archetypes
if str(_ARCHETYPES_DIR) not in sys.path:
    sys.path.insert(0, str(_ARCHETYPES_DIR))

from a2_hybrid import proof as a2_proof  # noqa: E402
from a2_hybrid.contract import (  # noqa: E402
    Action,
    A2Schema,
    CONFIDENCE_FLOOR,
    Draft,
    InboundPayload,
    LLMResponse,
    PipelineInput,
    QualityResult,
    Source,
)
from a2_hybrid.run import (  # noqa: E402
    ESCALATION_TARGET,
    A2Pipeline,
    OfflineMockLLM,
    parse_llm,
    validate_schema,
)


def _pipeline(**kw) -> A2Pipeline:
    from a1_python_only.a1_3_research import DeterministicFetcher

    fetcher = DeterministicFetcher(
        {"sql://crm/leads": [{"name": "Acme Corp", "score": 87}]}
    )
    return A2Pipeline(fetcher=fetcher, **kw)


def _lead_pin(action=None) -> PipelineInput:
    return PipelineInput(
        payload=InboundPayload(source="form", raw={"text": "score this lead"}),
        context={"lead_id": 1},
        action=action,
    )


def test_runs_offline_with_no_api_key():
    # Default client is OfflineMockLLM => no key, no network.
    out = _pipeline().run(_lead_pin(action=Action(kind="noop")))
    assert out.status == "completed"
    assert out.model == "offline-mock"
    assert out.schema_valid is True


def test_full_hybrid_chain_completes_with_proof():
    out = _pipeline().run(_lead_pin(action=Action(kind="noop", requires_approval=False)))
    assert out.status == "completed"
    assert out.proof is not None
    assert len(out.proof.artifact_hash) == 64  # SHA-256 hex
    # The schema gate is recorded in the proof — proves output was bounded.
    assert "schema_valid" in out.proof.gates
    assert "source_per_claim" in out.proof.gates
    assert out.proof.sources == ["sql://crm/leads"]
    assert out.confidence >= CONFIDENCE_FLOOR
    assert out.integration_status == "executed"


def test_strict_validator_accepts_well_formed():
    obj = {"headline": "Acme Corp", "personalization": "hi", "confidence": 0.9}
    v = validate_schema(obj)
    assert isinstance(v, A2Schema)
    assert v.headline == "Acme Corp"
    assert v.confidence == 0.9


def test_strict_validator_rejects_bad_shapes():
    # missing key
    assert validate_schema({"headline": "x", "confidence": 0.9}) is None
    # wrong type
    assert validate_schema(
        {"headline": "x", "personalization": "y", "confidence": "high"}
    ) is None
    # out of range
    assert validate_schema(
        {"headline": "x", "personalization": "y", "confidence": 1.7}
    ) is None
    # empty headline
    assert validate_schema(
        {"headline": "  ", "personalization": "y", "confidence": 0.9}
    ) is None
    # not a dict (raw prose leaked through)
    assert validate_schema("just prose") is None


def test_schema_failure_stops_before_proof():
    # An LLM that ignores the schema must NOT produce a shipped artifact.
    pipe = _pipeline(llm=OfflineMockLLM(force_invalid=True))
    out = pipe.run(_lead_pin(action=Action(kind="noop")))
    assert out.status == "schema_failed"
    assert out.schema_valid is False
    assert out.proof is None


def test_confidence_collapse_escalates_to_a3():
    # Pin confidence below the floor => escalate, do not ship.
    pipe = _pipeline(llm=OfflineMockLLM(confidence=CONFIDENCE_FLOOR - 0.1))
    out = pipe.run(_lead_pin(action=Action(kind="noop")))
    assert out.status == "escalate"
    assert out.escalation_target == ESCALATION_TARGET
    assert out.schema_valid is True  # schema was fine; trust was not
    assert out.proof is None


def test_unknown_intent_escalates():
    pin = PipelineInput(
        payload=InboundPayload(source="form", raw={"text": "noise noise noise"})
    )
    out = _pipeline().run(pin)
    assert out.status == "escalate"
    assert out.escalation_target == ESCALATION_TARGET


def test_parse_llm_handles_raw_json_and_garbage():
    # parsed dict preferred
    r = LLMResponse(raw_text="{}", parsed={"a": 1})
    assert parse_llm(r) == {"a": 1}
    # falls back to raw_text JSON
    r2 = LLMResponse(raw_text='{"b": 2}', parsed={})
    assert parse_llm(r2) == {"b": 2}
    # non-JSON garbage => None (not an exception)
    r3 = LLMResponse(raw_text="not json at all", parsed={})
    assert parse_llm(r3) is None


def test_proof_is_deterministic_and_binds_model_bytes():
    draft = Draft(
        body="Summary based on 1 sourced record(s): Acme Corp",
        personalization="Tailored.",
        sources=[Source(uri="sql://crm/leads", kind="sql")],
    )
    quality = QualityResult(
        passed=True,
        gates_passed=["schema_valid", "non_empty_body", "source_per_claim"],
    )
    llm = LLMResponse(raw_text='{"headline":"Acme Corp"}', parsed={}, model="offline-mock")
    p1 = a2_proof.run(draft, quality, llm)
    p2 = a2_proof.run(draft, quality, llm)
    assert p1.artifact_hash == p2.artifact_hash  # deterministic
    assert a2_proof.verify(p1, draft, quality, llm) is True
    # Tamper the MODEL output -> verification must fail (A2's extra binding).
    tampered = LLMResponse(raw_text='{"headline":"Evil Corp"}', parsed={}, model="offline-mock")
    assert a2_proof.verify(p1, draft, quality, tampered) is False
    assert p1.signer == "a2_hybrid"


def test_contract_is_imported_from_a1_not_redefined():
    # The frozen guarantee: A2's Draft IS A1's Draft object, not a copy.
    import a1_python_only._types as a1types
    import a2_hybrid.contract as a2c

    assert a2c.Draft is a1types.Draft
    assert a2c.ProofPacket is a1types.ProofPacket
    assert a2c.Source is a1types.Source


def test_approval_blocks_when_flagged_and_no_approver():
    pin = _lead_pin(
        action=Action(kind="stripe", payload={"amt": 100}, requires_approval=True)
    )
    with tempfile.TemporaryDirectory() as d:
        audit = Path(d) / "audit.jsonl"
        pipe = _pipeline(audit_path=audit)
        out = pipe.run(pin)
        assert out.status == "completed"
        assert out.integration_status == "blocked"  # conservative default approver
        assert audit.exists() and audit.read_text().strip()


def test_approval_executes_when_approver_grants():
    pin = _lead_pin(
        action=Action(kind="slack", payload={"msg": "hi"}, requires_approval=True)
    )
    pipe = _pipeline(approver=lambda packet, action: True)
    out = pipe.run(pin)
    assert out.integration_status == "executed"


# ---- standalone runner (no pytest required) --------------------------------
def _run_all() -> int:
    tests = [
        v for k, v in sorted(globals().items())
        if k.startswith("test_") and callable(v)
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
