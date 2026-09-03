"""A1 PYTHON_ONLY — frozen shared contract surface (IQRSQPI).

This module owns the canonical Pydantic models that flow through all 7 A1
steps and are imported (read-only) by A2/A3/A4. Per the RIG Lattice doctrine:

    "A1 owns the frozen shared contract surface.
     A2/A3/A4 import shared types from A1."

Pydantic is used when available (validation + JSON schema). When the runtime
has no pydantic installed (externally-managed envs, minimal sandboxes), a
stdlib dataclass fallback provides the SAME field surface and a `.model_dump()`
method so the archetype stays runnable with zero third-party deps.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

try:  # pragma: no cover - exercised by environment, not unit test
    from pydantic import BaseModel, Field

    _PYDANTIC = True
except Exception:  # pragma: no cover
    _PYDANTIC = False

    import dataclasses

    def Field(default=None, *, default_factory=None):  # type: ignore[misc]
        if default_factory is not None:
            return dataclasses.field(default_factory=default_factory)
        return dataclasses.field(default=default)

    class _Meta(type):
        def __new__(mcs, name, bases, ns):
            cls = super().__new__(mcs, name, bases, ns)
            if name == "BaseModel":
                return cls
            return dataclasses.dataclass(cls)

    class BaseModel(metaclass=_Meta):  # type: ignore[no-redef]
        def model_dump(self) -> dict:
            return dataclasses.asdict(self)

        @classmethod
        def model_validate(cls, data: dict):
            fields = {f.name for f in dataclasses.fields(cls)}
            return cls(**{k: v for k, v in data.items() if k in fields})


PYDANTIC_AVAILABLE = _PYDANTIC


class IntentKey(str, Enum):
    """Deterministic intent keys. Studio-specific keys are appended from
    intent_maps/*.yaml at build time. UNKNOWN is the escalation signal."""

    UNKNOWN = "unknown"
    LEAD_SCORE = "lead_score"
    STATUS_LOOKUP = "status_lookup"
    INVENTORY_CHECK = "inventory_check"
    SEND_FOLLOWUP = "send_followup"


class InboundPayload(BaseModel):
    source: str
    raw: dict[str, Any] = Field(default_factory=dict)


class Source(BaseModel):
    uri: str
    kind: str  # 'sql' | 'http' | 'mcp'


class StructuredQuery(BaseModel):
    intent: IntentKey
    sources: list[Source] = Field(default_factory=list)
    params: dict[str, Any] = Field(default_factory=dict)


class ResearchPack(BaseModel):
    rows: list[dict] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    shim_slot: dict = Field(default_factory=dict)


class Draft(BaseModel):
    body: str
    personalization: str
    sources: list[Source] = Field(default_factory=list)


class QualityResult(BaseModel):
    passed: bool
    gates_passed: list[str] = Field(default_factory=list)
    reason: Optional[str] = None


class ProofPacket(BaseModel):
    artifact_hash: str
    sources: list[str] = Field(default_factory=list)
    gates: list[str] = Field(default_factory=list)
    timestamp: str = ""  # ISO-8601 UTC; "" means "fill at emit time"
    signer: str = "a1_python_only"


class Action(BaseModel):
    kind: str  # 'smtp' | 'slack' | 'stripe' | 'noop'
    payload: dict = Field(default_factory=dict)
    requires_approval: bool = False


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
