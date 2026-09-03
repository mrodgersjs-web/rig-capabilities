"""A3 AGENT_BOUNDED archetype (STUB).

BMS band ~0.25-0.50. LangGraph bounded-agent mode. Required components per
the lattice card: LangGraph state object, explicit nodes/edges, tool allowlist,
cost budget, runtime budget, required mechanism map, guardrail result,
approval packet, audit row, failure/escalation path.

A3 handles ambiguous or previously-UNKNOWN intent escalated from A1.1.
Approval is MANDATORY at A3 and above. Mechanism maps required at A3+.
Stronger trail: ProofPacket -> ApprovalPacket -> Action -> Result.

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
    "REQUIRED_COMPONENTS",
]

ARCHETYPE_ID = "A3_AGENT_BOUNDED"
BMS_MODE = "AGENT_BOUNDED"
APPROVAL_MANDATORY = True

REQUIRED_COMPONENTS = (
    "langgraph_state",
    "explicit_nodes_edges",
    "tool_allowlist",
    "cost_budget",
    "runtime_budget",
    "mechanism_map",
    "guardrail_result",
    "approval_packet",
    "audit_row",
    "escalation_path",
)

STEP_INTERFACE = {
    "a3_1_intent": "run(input_payload: dict) -> IntentPacket  # handles UNKNOWN from A1",
    "a3_2_question": "run(state) -> StructuredQuery  # plan/question LangGraph node",
    "a3_3_research": "run(state) -> ResearchPack  # bounded tool calls only",
    "a3_4_solution": "run(state) -> Draft  # mechanism-mapped solution",
    "a3_5_quality": "run(state) -> QualityResult  # guardrails",
    "a3_6_proof": "run(state) -> ProofPacket  # + ApprovalPacket",
    "a3_7_integrate": "run(packet, approval, action) -> ExecutionResult  # approval mandatory",
}


def not_implemented(step: str):
    raise NotImplementedError(
        f"A3 AGENT_BOUNDED step '{step}' is a stub. See README.md. "
        f"Contract: {STEP_INTERFACE.get(step, 'run(state) -> packet')}"
    )
