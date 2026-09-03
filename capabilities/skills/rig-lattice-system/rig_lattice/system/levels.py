"""The 7 levels of the RIG Deviator System.

Each Level is a named, ordered stage in the canonical pipeline. Level → BMS
archetype dispatch happens in archetypes.py. The orchestrator runs L1 → L7
in order, with L1 short-circuiting the chain on hard failures.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Level(str, Enum):
    L1_CAPTURE = "L1_CAPTURE"
    L2_PROCESS = "L2_PROCESS"
    L3_CREATE = "L3_CREATE"
    L4_DISTRIBUTE = "L4_DISTRIBUTE"
    L5_ENGAGE = "L5_ENGAGE"
    L6_CONVERT = "L6_CONVERT"
    L7_AUTONOMIZE = "L7_AUTONOMIZE"


L1_CAPTURE = Level.L1_CAPTURE
L2_PROCESS = Level.L2_PROCESS
L3_CREATE = Level.L3_CREATE
L4_DISTRIBUTE = Level.L4_DISTRIBUTE
L5_ENGAGE = Level.L5_ENGAGE
L6_CONVERT = Level.L6_CONVERT
L7_AUTONOMIZE = Level.L7_AUTONOMIZE


LEVELS = (
    L1_CAPTURE,
    L2_PROCESS,
    L3_CREATE,
    L4_DISTRIBUTE,
    L5_ENGAGE,
    L6_CONVERT,
    L7_AUTONOMIZE,
)


@dataclass(frozen=True)
class LevelSpec:
    level: Level
    purpose: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]


LEVEL_SPECS = {
    L1_CAPTURE: LevelSpec(
        level=L1_CAPTURE,
        purpose="Pull artifact from any source. Normalize to text + hash.",
        inputs=("file_path | url | stdin",),
        outputs=("text", "content_hash", "source_meta"),
    ),
    L2_PROCESS: LevelSpec(
        level=L2_PROCESS,
        purpose="Audit through 40 engines + DES² 5-amplifier inner loop.",
        inputs=("text",),
        outputs=("audit", "des2", "engines_scored"),
    ),
    L3_CREATE: LevelSpec(
        level=L3_CREATE,
        purpose="Generate +20σ variants per weak engine.",
        inputs=("text", "audit"),
        outputs=("variants[]", "weakest_engines[]"),
    ),
    L4_DISTRIBUTE: LevelSpec(
        level=L4_DISTRIBUTE,
        purpose="Render HTML + markdown reports + JSON receipts.",
        inputs=("audit", "des2", "variants"),
        outputs=("html_path", "md_path", "receipt_path"),
    ),
    L5_ENGAGE: LevelSpec(
        level=L5_ENGAGE,
        purpose="Surface failed gates, deliver actionable next-step copy.",
        inputs=("audit", "des2"),
        outputs=("blockers[]", "next_actions[]", "fix_suggestions[]"),
    ),
    L6_CONVERT: LevelSpec(
        level=L6_CONVERT,
        purpose="Apply patch overlays. Produce strict-passing artifact.",
        inputs=("text", "audit", "fix_suggestions"),
        outputs=("patched_text", "final_text", "final_audit"),
    ),
    L7_AUTONOMIZE: LevelSpec(
        level=L7_AUTONOMIZE,
        purpose="Daemon-driven continuous audit + Brier outcome observation.",
        inputs=("final_text", "final_audit", "predicted_madz"),
        outputs=("daemon_status", "outcome_records[]", "weight_updates[]"),
    ),
}


def spec_for(level: Level) -> LevelSpec:
    return LEVEL_SPECS[level]
