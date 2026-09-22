"""Compile governed skills from compiled procedures."""
from __future__ import annotations

import hashlib
import json
from typing import Optional


def _bms_band(confidence: float) -> str:
    if confidence >= 0.75:
        return "A1"
    if confidence >= 0.45:
        return "A2"
    if confidence >= 0.25:
        return "A3"
    return "A4"


def compile_skill(procedure: dict, skill_name: Optional[str] = None) -> dict:
    """Compile one skill while preserving procedure provenance."""
    name = skill_name or procedure["name"].lower().replace(" procedure", "").replace(" ", "-")
    procedure_steps = [step["action"] for step in procedure["steps"]]
    confidence = float(procedure["confidence"])
    skill_id = hashlib.sha256(
        json.dumps(
            {"skill_name": name, "procedure_id": procedure["procedure_id"]},
            sort_keys=True,
        ).encode()
    ).hexdigest()[:16]

    skill = {
        "skill_id": skill_id,
        "name": name,
        "version": "1.0.0",
        "description": f"Compiled from procedure: {procedure['name']}",
        "input_schema": {
            "type": "object",
            "properties": {
                "context": {
                    "type": "string",
                    "description": "Business context for the skill",
                }
            },
            "required": ["context"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "recommendation": {
                    "type": "string",
                    "description": "Skill output recommendation",
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                },
            },
            "required": ["recommendation", "confidence"],
        },
        "procedure": procedure_steps,
        "decision_rules": [
            "When procedure conditions match, execute steps sequentially and verify each expected outcome."
        ],
        "tags": [name],
        "source_refs": [
            {
                "video_id": ref["video_id"],
                **({"channel_id": ref["channel_id"]} if ref.get("channel_id") else {}),
                "claim_ids": ref.get("claim_ids", []),
                "procedure_id": procedure["procedure_id"],
            }
            for ref in procedure["source_refs"]
        ],
        "compiler_version": "1.0.0",
        "confidence": confidence,
        "status": "draft",
        "bms_band": _bms_band(confidence),
        "created_at": "2026-09-15T00:00:00Z",
    }
    skill["content_hash"] = hashlib.sha256(
        json.dumps(skill, sort_keys=True).encode()
    ).hexdigest()
    return skill


def compile_skills(procedures: list) -> list:
    """Compile all supplied procedures into skills."""
    return [compile_skill(procedure) for procedure in procedures]
