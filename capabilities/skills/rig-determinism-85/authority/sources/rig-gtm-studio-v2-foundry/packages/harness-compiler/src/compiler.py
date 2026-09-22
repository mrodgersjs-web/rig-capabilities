"""packages/harness-compiler/src/compiler.py — Harness Compiler.

Compiles skills into governed harnesses following the H=(E,T,C,S,L,V) contract:
- E: Evidence (allowed corpus, citations, freshness, reliability)
- T: Tools (explicit allowlist and side-effect boundaries)
- C: Constraints (ICP, offer, legal, brand, price, prohibited claims)
- S: State (typed inputs, workflow state, memory scope)
- L: Loop (IQRSQPI stages, stage thresholds, retry limits, escalation)
- V: Verifier (independent acceptance tests and sole termination authority)
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional


def compile_harness(skill: dict, harness_name: Optional[str] = None) -> dict:
    """Compile a harness from a skill following the H=(E,T,C,S,L,V) contract."""
    if not harness_name:
        harness_name = f"{skill['name']}-harness"

    # E: Evidence
    evidence = {
        "allowed_corpus": [ref["video_id"] for ref in skill["source_refs"]],
        "citation_required": True,
        "freshness_days": 365,
        "reliability_threshold": 0.7,
    }

    # T: Tools
    tools = {
        "allowlist": ["json_schema_validate", "hash_verify"],
        "side_effect_boundaries": {
            "can_read": ["capabilities/lessons", "capabilities/skills"],
            "can_write": [],
            "can_network": False,
        },
    }

    # C: Constraints
    constraints = {
        "icp": "B2B service businesses",
        "offer_scope": skill["description"],
        "legal": ["fair_use", "attribution"],
        "brand": "RIG",
        "prohibited_claims": ["guaranteed results", "no risk"],
    }

    # S: State
    state = {
        "input_schema": skill["input_schema"],
        "output_schema": skill["output_schema"],
        "workflow_state": "initialized",
        "memory_scope": "session",
    }

    # L: Loop
    loop = {
        "stages": ["intake", "question", "research", "synthesize", "quantify", "produce", "iterate"],
        "stage_thresholds": 0.8,
        "retry_limits": 3,
        "escalation": "verifier",
    }

    # V: Verifier
    verifier = {
        "acceptance_tests": [
            {"test_id": "input-schema", "type": "schema_validation", "target": "input"},
            {"test_id": "output-schema", "type": "schema_validation", "target": "output"},
            {"test_id": "provenance", "type": "hash_verification", "target": "source_refs"},
        ],
        "termination_authority": "verifier",
        "independent": True,
        "verifier_id": "rig-gtm-verifier-v1",
    }

    # Gates (required by harness schema)
    gates = [
        {"gate_id": "input-validation", "name": "Input Schema Validation", "check": "validate_against_schema(input, skill.input_schema)", "severity": "block"},
        {"gate_id": "output-validation", "name": "Output Schema Validation", "check": "validate_against_schema(output, skill.output_schema)", "severity": "block"},
        {"gate_id": "provenance-check", "name": "Source Provenance Verification", "check": "verify_source_refs(skill.source_refs)", "severity": "error"},
    ]

    # Compute harness ID
    harness_id = hashlib.sha256(
        json.dumps({"harness_name": harness_name, "skill_id": skill["skill_id"]}, sort_keys=True).encode()
    ).hexdigest()[:16]

    # Build harness payload
    harness_payload = {
        "harness_id": harness_id,
        "name": harness_name,
        "version": "1.0.0",
        "skill_id": skill["skill_id"],
        "E": evidence,
        "T": tools,
        "C": constraints,
        "S": state,
        "L": loop,
        "V": verifier,
        "gates": gates,
        "source_refs": [
            {
                "video_id": ref["video_id"],
                "channel_id": ref["channel_id"],
                "skill_ids": [skill["skill_id"]]
            }
            for ref in skill["source_refs"]
        ],
        "compiler_version": "1.0.0",
        "confidence": skill["confidence"],
        "status": "draft",
        "created_at": "2026-09-15T00:00:00Z",
    }

    # Compute content hash
    harness_payload["content_hash"] = hashlib.sha256(
        json.dumps(harness_payload, sort_keys=True).encode()
    ).hexdigest()

    return harness_payload


def compile_harnesses(skills: list) -> list:
    """Compile harnesses for all skills."""
    harnesses = []
    for skill in skills:
        harness = compile_harness(skill)
        harnesses.append(harness)
    return harnesses
