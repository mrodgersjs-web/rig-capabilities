"""packages/evaluator-suite/src/evaluator.py — Evaluator Suite.

Performs proper JSON Schema validation (Draft 2020-12) and runs golden tests.
"""
from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Optional

import jsonschema
from jsonschema import Draft202012Validator, FormatChecker

SCHEMAS_DIR = Path("schemas")


def load_schema(name: str) -> dict:
    """Load a JSON schema by name."""
    path = SCHEMAS_DIR / f"{name}.json"
    return json.loads(path.read_text())


def validate_schema(schema: dict) -> bool:
    """Validate that a schema itself is well-formed."""
    try:
        Draft202012Validator.check_schema(schema)
        return True
    except jsonschema.SchemaError:
        return False


def validate_artifact(artifact: dict, schema_name: str) -> dict:
    """Validate an artifact against its JSON schema (Draft 2020-12)."""
    schema = load_schema(schema_name)

    # Validate schema itself
    if not validate_schema(schema):
        return {"valid": False, "errors": [f"Schema {schema_name} is not well-formed"]}

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = list(validator.iter_errors(artifact))

    error_messages = []
    for error in errors:
        path = ".".join(str(p) for p in error.path) or "(root)"
        error_messages.append(f"{path}: {error.message}")

    return {"valid": len(errors) == 0, "errors": error_messages}


def verify_content_hash(artifact: dict) -> bool:
    """Verify the artifact's content_hash is correct."""
    stored_hash = artifact.get("content_hash", "")
    if not stored_hash:
        return False

    payload = {k: v for k, v in artifact.items() if k != "content_hash"}
    computed_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()

    return computed_hash == stored_hash


def run_golden_validation(artifact: dict, schema_name: str) -> dict:
    """Run golden validation on an artifact (schema + hash)."""
    validation = validate_artifact(artifact, schema_name)
    hash_ok = verify_content_hash(artifact)

    result = {
        "artifact_id": artifact.get("lesson_id") or artifact.get("skill_id") or "unknown",
        "schema": schema_name,
        "schema_valid": validation["valid"],
        "schema_errors": validation["errors"],
        "content_hash_valid": hash_ok,
        "status": "pass" if (validation["valid"] and hash_ok) else "fail",
    }
    return result


def evaluate_all(artifacts_dir: Path, schema_name: str) -> list:
    """Evaluate all artifacts in a directory."""
    results = []
    for path in sorted(artifacts_dir.glob("*.json")):
        artifact = json.loads(path.read_text())
        result = run_golden_validation(artifact, schema_name)
        result["path"] = str(path)
        results.append(result)
    return results
