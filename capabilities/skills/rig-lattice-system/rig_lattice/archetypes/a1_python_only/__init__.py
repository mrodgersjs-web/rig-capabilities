"""A1 PYTHON_ONLY archetype — RIG Lattice Mode 1.

Deterministic IQRSQPI chain for cells where BMS >= 0.75 (L1-L2).
No model in the decision path; the only LLM touch is the optional
<=60-word personalization shim at A1.4. Escalate (UNKNOWN), don't fail.

Public surface:
  contract  — frozen Pydantic/dataclass models (also re-exported here)
  run       — A1Pipeline orchestrating all 7 steps + gates
  proof     — SHA-256 ProofPacket helpers
  a1_1..a1_7 — individual IQRSQPI step modules, each exposing run()
"""
from __future__ import annotations

from . import (
    a1_1_intent,
    a1_2_question,
    a1_3_research,
    a1_4_solution,
    a1_5_quality,
    a1_6_proof,
    a1_7_integrate,
)
from ._types import (
    PYDANTIC_AVAILABLE,
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
    "PYDANTIC_AVAILABLE",
    "Action",
    "Draft",
    "InboundPayload",
    "IntentKey",
    "ProofPacket",
    "QualityResult",
    "ResearchPack",
    "Source",
    "StructuredQuery",
    "a1_1_intent",
    "a1_2_question",
    "a1_3_research",
    "a1_4_solution",
    "a1_5_quality",
    "a1_6_proof",
    "a1_7_integrate",
]

ARCHETYPE_ID = "A1_PYTHON_ONLY"
BMS_MODE = "PYTHON_ONLY"
BMS_FLOOR = 0.75
