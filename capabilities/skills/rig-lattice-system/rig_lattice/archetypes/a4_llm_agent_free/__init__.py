"""A4 LLM_AGENT_FREE archetype (STUB).

BMS band < 0.25 (lowest determinism / highest reasoning). Hierarchical crew
with contrarian sourcing, multiple frames, red-team review, and Brier-style
evaluation. Strategy outputs must include mechanisms AND falsifiers.

A4 doctrine:
  - Hierarchical crew is defined.
  - Contrarian sourcing exists.
  - Multiple frames supported.
  - Red-team review runs.
  - Brier-style evaluation runs.
  - Human approval is MANDATORY (no automatic integration).
  - Audit trail must be post-mortem ready.

Imports the frozen shared contract from A1; never redefines it.
"""
from __future__ import annotations

try:
    from ..a1_python_only._types import (
        Action,
        Draft,
        InboundPayload,
        IntentKey,
        ProofPacket,
        QualityResult,
        ResearchPack,
        Source,
        StructuredQuery,
    )
except ImportError:
    from a1_python_only._types import (
        Action,
        Draft,
        InboundPayload,
        IntentKey,
        ProofPacket,
        QualityResult,
        ResearchPack,
        Source,
        StructuredQuery,
    )

__all__ = [
    "Action",
    "Draft",
    "InboundPayload",
    "IntentKey",
    "ProofPacket",
    "QualityResult",
    "ResearchPack",
    "Source",
    "StructuredQuery",
    "STEP_INTERFACE",
    "ACCEPTANCE",
]

ARCHETYPE_ID = "A4_LLM_AGENT_FREE"
BMS_MODE = "LLM_AGENT_FREE"
APPROVAL_MANDATORY = True

ACCEPTANCE = (
    "hierarchical_crew",
    "contrarian_sourcing",
    "multiple_frames",
    "mechanisms_and_falsifiers",
    "red_team_review",
    "brier_evaluation",
    "human_approval_mandatory",
    "postmortem_ready_audit",
)

STEP_INTERFACE = {
    "a4_1_intent": "run(input_payload: dict) -> IntentPacket",
    "a4_2_question": "run(state) -> StructuredQuery  # multi-frame decomposition",
    "a4_3_research": "run(state) -> ResearchPack  # contrarian sourcing",
    "a4_4_solution": "run(state) -> Draft  # mechanisms + falsifiers",
    "a4_5_quality": "run(state) -> QualityResult  # red-team + Brier",
    "a4_6_proof": "run(state) -> ProofPacket  # post-mortem ready",
    "a4_7_integrate": "run(packet, approval, action) -> ExecutionResult  # human approval mandatory",
}


def not_implemented(step: str):
    raise NotImplementedError(
        f"A4 LLM_AGENT_FREE step '{step}' is a stub. See README.md. "
        f"Contract: {STEP_INTERFACE.get(step, 'run(state) -> packet')}"
    )
