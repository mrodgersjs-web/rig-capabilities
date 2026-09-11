"""Typed pydantic schemas for the fh_review MODEL operation.

Companion to authority/sources/fh_review/ (kept outside source_root so the
D85 inventory binds only the executor pair). The worker's own CODE validator
enforces this contract structurally at runtime; these classes are the typed
input/output schemas the D85 necessity record names.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Verdict = Literal["PASS", "REVISE", "BLOCK"]


class FhReviewInput(BaseModel):
    prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    stack: Literal["rig5"]
    participants_required: int = Field(default=4, ge=4)


class FhParticipantVerdict(BaseModel):
    participant: str
    verdict: Verdict


class FhReviewOutput(BaseModel):
    participants: list[FhParticipantVerdict] = Field(min_length=4)
    consensus: Verdict
    evidence: list[str] = Field(min_length=2)

    @field_validator("evidence")
    @classmethod
    def hex64(cls, v: list[str]) -> list[str]:
        for item in v:
            if len(item) != 64 or any(c not in "0123456789abcdef" for c in item):
                raise ValueError("evidence hashes must be lowercase sha256 hex")
        return v
