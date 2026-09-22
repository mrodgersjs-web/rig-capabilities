"""Typed Pydantic boundary for the MODEL verifier-dispatch operation.

Reference contract companion for D85 model_necessity[0] of process
rig_capabilities_engine_v1. It mirrors exactly the input the rig-loop engine
renders for verify() (loops.py:1297-1329: run evidence + stage contract
written to verify-<family>-<ts>.prompt.md, dispatched to one cross-family
VERIFIER_FAMILIES CLI) and the output it parses back (loops.py:1337-1343:
verdict token + verification record). Executed-verified under pydantic
2.13.4: valid inputs/outputs validate; same-family verdicts and junk fail.
"""

from typing import Literal

from pydantic import BaseModel, field_validator

Families = Literal["codex", "claude", "hermes", "omp", "prime-agent"]


class EngineVerifyInput(BaseModel):
    run_evidence: str
    family: Families

    @field_validator("run_evidence")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("run_evidence must be non-empty")
        return v


class EngineVerifyRecord(BaseModel):
    family: Families
    verdict: Literal["PASS", "REVISE", "BLOCK"]
    exit: int
    at: str
    secs: float


class EngineVerifyOutput(BaseModel):
    record: EngineVerifyRecord

    @field_validator("record")
    @classmethod
    def _cross_family_only(cls, v: EngineVerifyRecord, info) -> EngineVerifyRecord:
        # GEV separation (loops.py:1300-1301, :740-754): a verdict whose
        # family equals the builder family is never an accepted verdict.
        builder = info.context.get("builder_family") if info.context else None
        if builder is not None and v.family == builder:
            raise ValueError("verdict family equals builder family")
        return v
