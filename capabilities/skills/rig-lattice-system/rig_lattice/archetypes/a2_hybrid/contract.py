"""A2 HYBRID — contract surface (schema-bounded LLM rung).

A2 is the rung above A1: A1 is frozen, NO-LLM, deterministic; A2 adds a real
LLM call but ONLY behind a strict output schema and a validator chain:

    LLM output -> parser -> SchemaValidator -> Draft -> gate

A2 NEVER redefines the frozen A1 contract. It imports A1's Pydantic/dataclass
models read-only and adds three A2-specific envelopes:

  * LLMRequest   — the temperature-0, schema-constrained call the runtime makes
  * LLMResponse  — the raw text + parsed dict the (mock or real) LLM returned
  * A2Schema     — the strict output schema the LLM is constrained to
  * PipelineInput / PipelineOutput — top-level A2 in/out (mirrors A1's, plus
    confidence + the schema-validation trace that A1 has no equivalent for)

Runs with NO API key: the default LLM client is a deterministic offline mock
that emits schema-valid JSON, so the whole chain is reproducible and testable
with zero network and zero secrets.
"""
from __future__ import annotations

from typing import Any, Optional

# Import the FROZEN A1 contract — never redefine these.
try:  # package-root import (archetypes/ on sys.path)
    from a1_python_only._types import (  # noqa: F401
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
except ImportError:  # relative import (monorepo-package style)
    from ..a1_python_only._types import (  # noqa: F401
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


# Confidence below this floor at A2.4 means the schema-bounded LLM could not
# produce a trustworthy draft -> escalate to A3 (don't fail, don't ship).
CONFIDENCE_FLOOR = 0.55


class A2Schema(BaseModel):
    """The STRICT output schema the LLM is constrained to at temperature 0.

    The schema-constrained call must return exactly these fields. Anything
    else (extra prose, missing keys, wrong types) is rejected by the
    validator and the cell escalates rather than shipping unvalidated text.
    """

    headline: str
    personalization: str
    confidence: float


class LLMRequest(BaseModel):
    """A temperature-0, schema-constrained LLM call. `schema_keys` is the
    allowed output surface; `temperature` is pinned to 0.0 for determinism."""

    prompt: str
    schema_keys: list[str] = Field(
        default_factory=lambda: ["headline", "personalization", "confidence"]
    )
    temperature: float = 0.0
    max_tokens: int = 256


class LLMResponse(BaseModel):
    """What the (mock or real) LLM returned: the raw text AND the parsed dict.
    The raw text is retained so the ProofPacket can bind the artifact to the
    exact bytes the model produced (source-per-claim, model edition)."""

    raw_text: str
    parsed: dict[str, Any] = Field(default_factory=dict)
    model: str = "offline-mock"


class PipelineInput(BaseModel):
    """Top-level A2 input. Same shape as A1's so a cell can be promoted A1->A2
    without changing its caller, plus nothing extra is required."""

    payload: InboundPayload
    context: dict[str, Any] = Field(default_factory=dict)
    action: Optional[Action] = None


class PipelineOutput(BaseModel):
    """Top-level A2 output. Adds `confidence` and `schema_valid` over A1 because
    those are the two facts a hybrid rung must surface that a no-LLM rung cannot:
        status:
          'completed'        — LLM drafted, schema validated, gated, proof emitted
          'escalate'         — UNKNOWN intent OR confidence < floor -> A3
          'schema_failed'    — LLM output did not satisfy the strict schema
          'quality_failed'   — a hard gate failed before proof
    """

    status: str
    intent: str
    confidence: float = 0.0
    schema_valid: bool = False
    proof: Optional[ProofPacket] = None
    quality: Optional[QualityResult] = None
    integration_status: Optional[str] = None
    escalation_target: Optional[str] = None
    model: str = "offline-mock"


__all__ = [
    "PYDANTIC_AVAILABLE",
    "Action",
    "A2Schema",
    "CONFIDENCE_FLOOR",
    "Draft",
    "InboundPayload",
    "IntentKey",
    "LLMRequest",
    "LLMResponse",
    "PipelineInput",
    "PipelineOutput",
    "ProofPacket",
    "QualityResult",
    "ResearchPack",
    "Source",
    "StructuredQuery",
    "utcnow_iso",
]
