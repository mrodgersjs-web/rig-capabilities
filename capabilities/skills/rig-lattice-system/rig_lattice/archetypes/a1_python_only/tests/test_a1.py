"""A1 PYTHON_ONLY tests.

Runs under pytest if installed, and also standalone:

    python3 platform/archetypes/a1_python_only/tests/test_a1.py

Covers the full IQRSQPI chain, the UNKNOWN escalation path, hard-gate
failure, SHA-256 proof determinism + tamper detection, and conditional
approval at A1.7.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Allow standalone execution. NOTE: the top dir is named "platform", which
# collides with the stdlib `platform` module, so we do NOT add the monorepo
# root to sys.path. Instead we add the `archetypes/` dir and import the
# package by its own name `a1_python_only`.
_HERE = Path(__file__).resolve()
_ARCHETYPES_DIR = _HERE.parents[2]  # .../platform/archetypes
if str(_ARCHETYPES_DIR) not in sys.path:
    sys.path.insert(0, str(_ARCHETYPES_DIR))

from a1_python_only import (  # noqa: E402
    a1_1_intent,
    a1_5_quality,
    a1_6_proof,
)
from a1_python_only.a1_3_research import (  # noqa: E402
    DeterministicFetcher,
)
from a1_python_only.contract import (  # noqa: E402
    Action,
    Draft,
    InboundPayload,
    IntentKey,
    PipelineInput,
    QualityResult,
    Source,
)
from a1_python_only.run import (  # noqa: E402
    ESCALATION_TARGET,
    A1Pipeline,
)


def _scoring_pipeline() -> A1Pipeline:
    fetcher = DeterministicFetcher(
        {"sql://crm/leads": [{"name": "Acme Corp", "score": 87}]}
    )
    return A1Pipeline(fetcher=fetcher)


def test_intent_classification_match():
    payload = InboundPayload(source="form", raw={"text": "score this lead"})
    assert a1_1_intent.run(payload) == IntentKey.LEAD_SCORE


def test_intent_unknown_on_miss():
    payload = InboundPayload(source="form", raw={"text": "completely unrelated text"})
    assert a1_1_intent.run(payload) == IntentKey.UNKNOWN


def test_full_chain_completes_with_proof():
    pin = PipelineInput(
        payload=InboundPayload(source="form", raw={"text": "score this lead"}),
        context={"lead_id": 1},
        action=Action(kind="noop", requires_approval=False),
    )
    out = _scoring_pipeline().run(pin)
    assert out.status == "completed"
    assert out.intent == IntentKey.LEAD_SCORE.value
    assert out.proof is not None
    assert len(out.proof.artifact_hash) == 64  # SHA-256 hex
    assert "non_empty_body" in out.proof.gates
    assert "source_per_claim" in out.proof.gates
    assert out.proof.sources == ["sql://crm/leads"]
    assert out.integration_status == "executed"


def test_unknown_intent_escalates():
    pin = PipelineInput(
        payload=InboundPayload(source="form", raw={"text": "noise noise noise"}),
    )
    out = _scoring_pipeline().run(pin)
    assert out.status == "escalate"
    assert out.escalation_target == ESCALATION_TARGET


def test_quality_gate_fails_on_no_source():
    # Draft with empty sources must fail the source_per_claim hard gate.
    draft = Draft(body="something", personalization="", sources=[])
    q = a1_5_quality.run(draft)
    assert q.passed is False
    assert q.reason and "source" in q.reason


def test_proof_is_deterministic_and_tamper_evident():
    draft = Draft(
        body="Summary based on 1 sourced record(s): Acme Corp",
        personalization="",
        sources=[Source(uri="sql://crm/leads", kind="sql")],
    )
    quality = QualityResult(
        passed=True,
        gates_passed=["non_empty_body", "source_per_claim", "shim_within_limit"],
    )
    p1 = a1_6_proof.run(draft, quality)
    p2 = a1_6_proof.run(draft, quality)
    assert p1.artifact_hash == p2.artifact_hash  # deterministic
    assert a1_6_proof.verify(p1, draft, quality) is True
    # Tamper the body -> verification must fail.
    tampered = Draft(body="evil", personalization="", sources=draft.sources)
    assert a1_6_proof.verify(p1, tampered, quality) is False


def test_approval_blocks_when_flagged_and_no_approver():
    pin = PipelineInput(
        payload=InboundPayload(source="form", raw={"text": "score this lead"}),
        action=Action(kind="stripe", payload={"amt": 100}, requires_approval=True),
    )
    with tempfile.TemporaryDirectory() as d:
        audit = Path(d) / "audit.jsonl"
        pipe = A1Pipeline(
            fetcher=DeterministicFetcher(
                {"sql://crm/leads": [{"name": "Acme", "score": 50}]}
            ),
            audit_path=audit,
        )
        out = pipe.run(pin)
        assert out.status == "completed"
        assert out.integration_status == "blocked"  # conservative default approver
        assert audit.exists() and audit.read_text().strip()  # append-only audit row


def test_approval_executes_when_approver_grants():
    pin = PipelineInput(
        payload=InboundPayload(source="form", raw={"text": "score this lead"}),
        action=Action(kind="slack", payload={"msg": "hi"}, requires_approval=True),
    )
    pipe = A1Pipeline(
        fetcher=DeterministicFetcher(
            {"sql://crm/leads": [{"name": "Acme", "score": 50}]}
        ),
        approver=lambda packet, action: True,
    )
    out = pipe.run(pin)
    assert out.integration_status == "executed"


# ---- standalone runner (no pytest required) --------------------------------
def _run_all() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
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
