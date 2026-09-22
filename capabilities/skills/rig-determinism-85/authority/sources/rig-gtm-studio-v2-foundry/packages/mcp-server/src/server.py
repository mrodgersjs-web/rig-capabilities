"""packages/mcp-server/src/server.py — GTM Studio MCP Server.

Exposes compiled capabilities via MCP protocol with typed contracts,
version pinning, and promotion-gated publishing.

Publishing is fail-closed: all receipts must be verified by the released
authority/Gate-D adapter. Self-authored receipts are blocked.
"""
from __future__ import annotations

import json
import importlib.util
from pathlib import Path
from typing import Optional

CAPABILITIES_DIR = Path("capabilities")

# Allowlisted kind mapping: kind -> (directory, id_field)
KIND_MAPPING = {
    "lesson": ("lessons", "lesson_id"),
    "skill": ("skills", "skill_id"),
    "harness": ("harnesses", "harness_id"),
}


def load_gates_module():
    """Load the promotion gates module."""
    spec = importlib.util.spec_from_file_location("gates", "packages/promotion-gates/src/gates.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_evaluator_module():
    """Load the evaluator module."""
    spec = importlib.util.spec_from_file_location("evaluator", "packages/evaluator-suite/src/evaluator.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def list_capabilities(kind: Optional[str] = None) -> list:
    """List all compiled capabilities, optionally filtered by kind."""
    capabilities = []

    kinds = [kind] if kind else list(KIND_MAPPING.keys())
    for k in kinds:
        if k not in KIND_MAPPING:
            continue
        dir_name, id_field = KIND_MAPPING[k]
        for path in CAPABILITIES_DIR.glob(f"{dir_name}/*.json"):
            cap = json.loads(path.read_text())
            capabilities.append({
                "id": cap[id_field],
                "kind": k,
                "name": cap.get("name", "unknown"),
                "status": cap.get("status", "unknown"),
                "confidence": cap.get("confidence"),
                "path": str(path),
            })

    return capabilities


def get_capability(capability_id: str, kind: str = "skill") -> Optional[dict]:
    """Get a specific capability by ID."""
    if kind not in KIND_MAPPING:
        return None
    dir_name, id_field = KIND_MAPPING[kind]
    path = CAPABILITIES_DIR / dir_name / f"{capability_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def publish_capability(capability: dict, kind: str = "skill", **receipts) -> dict:
    """Validate a candidate but block publish until canonical authority is wired."""
    if kind not in KIND_MAPPING:
        return {"status": "error", "error": f"Invalid kind: {kind}"}

    _, id_field = KIND_MAPPING[kind]
    capability_id = capability.get(id_field)
    if not capability_id:
        return {"status": "error", "error": f"Missing {id_field} in capability"}

    evaluator = load_evaluator_module()
    validation = evaluator.run_golden_validation(capability, kind)
    if validation["status"] != "pass":
        return {
            "status": "blocked",
            "capability_id": capability_id,
            "reason": "schema_or_hash_validation_failed",
            "errors": validation["schema_errors"],
        }

    return {
        "status": "blocked",
        "capability_id": capability_id,
        "reason": "canonical_receipt_verifier_unavailable",
    }
