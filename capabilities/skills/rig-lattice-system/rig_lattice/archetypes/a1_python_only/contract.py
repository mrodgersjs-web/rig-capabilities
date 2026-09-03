"""A1 contract surface (task-named alias of ._types).

The RIG task spec asks for a `contract.py` with Pydantic in/out models; the
28-archetype layout names the same surface `_types.py`. To satisfy both without
divergence, contract.py re-exports the frozen `_types` models and adds the two
canonical pipeline-level envelopes (PipelineInput / PipelineOutput) that A1's
run.py produces and consumes.

A2/A3/A4 should import shared types from here (or from ._types) — never redefine.
"""
from __future__ import annotations

from typing import Any, Optional

from ._types import (  # noqa: F401  (re-exported on purpose)
    PYDANTIC_AVAILABLE,
    Action,
    BaseModel,
    Draft,
    Field,
    InboundPayload,
    IntentKey,
    ProofPacket,
    QualityResult,
    ResearchPack,
    Source,
    StructuredQuery,
    utcnow_iso,
)


class PipelineInput(BaseModel):
    """Top-level A1 input: an inbound payload plus optional context and an
    optional action to integrate after proof."""

    payload: InboundPayload
    context: dict[str, Any] = Field(default_factory=dict)
    action: Optional[Action] = None


class PipelineOutput(BaseModel):
    """Top-level A1 output: status, the produced proof, and a trace of which
    gates/steps were reached. status is one of:
        'completed'  — full IQRSQPI chain ran, proof emitted
        'escalate'   — intent UNKNOWN -> route to A3.1
        'quality_failed' — a hard gate failed before proof
    """

    status: str
    intent: str
    proof: Optional[ProofPacket] = None
    quality: Optional[QualityResult] = None
    integration_status: Optional[str] = None
    escalation_target: Optional[str] = None


__all__ = [
    "PYDANTIC_AVAILABLE",
    "Action",
    "Draft",
    "InboundPayload",
    "IntentKey",
    "PipelineInput",
    "PipelineOutput",
    "ProofPacket",
    "QualityResult",
    "ResearchPack",
    "Source",
    "StructuredQuery",
    "utcnow_iso",
]
