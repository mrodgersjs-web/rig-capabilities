"""A2 HYBRID archetype — RIG Lattice Mode 2 (schema-bounded LLM rung).

BMS band ~0.50-0.75. The rung between frozen A1 (no LLM in the decision path)
and approval-gated A3/A4. A2 adds a REAL LLM call but ONLY behind a strict
output schema and a validator chain:

    LLM output -> parser -> SchemaValidator -> Draft -> gate

No raw LLM output passes directly into integration. A2 imports the frozen
shared contract from A1 (never redefines it), enforces source-per-claim from
A2 up, and escalates confidence collapse to A3.

Runs with NO API key: the default LLM client is a deterministic offline mock
(OfflineMockLLM) that emits schema-valid JSON, so the chain is reproducible
and testable with zero network and zero secrets.

Public surface:
  contract  — A2 envelopes (LLMRequest/LLMResponse/A2Schema/Pipeline I/O) +
              re-exported frozen A1 models
  run       — A2Pipeline (schema-bounded orchestrator) + OfflineMockLLM +
              the parse/validate/solution/quality stages
  proof     — SHA-256 ProofPacket binding the artifact to the model bytes
"""
from __future__ import annotations

from . import contract, proof, run
from .contract import (
    PYDANTIC_AVAILABLE,
    Action,
    A2Schema,
    CONFIDENCE_FLOOR,
    Draft,
    InboundPayload,
    IntentKey,
    LLMRequest,
    LLMResponse,
    PipelineInput,
    PipelineOutput,
    ProofPacket,
    QualityResult,
    ResearchPack,
    Source,
    StructuredQuery,
)
from .run import (
    ESCALATION_TARGET,
    A2Pipeline,
    LLMClient,
    OfflineMockLLM,
    parse_llm,
    solution,
    validate_schema,
)

__all__ = [
    "PYDANTIC_AVAILABLE",
    "Action",
    "A2Pipeline",
    "A2Schema",
    "CONFIDENCE_FLOOR",
    "Draft",
    "ESCALATION_TARGET",
    "InboundPayload",
    "IntentKey",
    "LLMClient",
    "LLMRequest",
    "LLMResponse",
    "OfflineMockLLM",
    "PipelineInput",
    "PipelineOutput",
    "ProofPacket",
    "QualityResult",
    "ResearchPack",
    "Source",
    "StructuredQuery",
    "contract",
    "parse_llm",
    "proof",
    "run",
    "solution",
    "validate_schema",
]

ARCHETYPE_ID = "A2_HYBRID"
BMS_MODE = "HYBRID"
BMS_FLOOR = 0.50
BMS_CEILING = 0.75
ESCALATION_TARGET = "A3"
