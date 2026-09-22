"""packages/procedure-compiler/src/compiler.py — Procedure Compiler.

Compiles lessons into step-by-step procedures derived from testable_procedure claims.
Each step retains claim IDs and timestamps for provenance.
Claims are filtered by each lesson's referenced claim_ids.

Lessons without testable_procedure claims are tracked as rejections.
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional


def _filter_claims_for_lesson(lesson: dict, all_claims: list) -> list:
    """Filter claims to only those referenced by this lesson."""
    lesson_claim_ids = set()
    for ref in lesson.get("source_refs", []):
        for claim_id in ref.get("claim_ids", []):
            lesson_claim_ids.add(claim_id)

    if not lesson_claim_ids:
        return []

    return [c for c in all_claims if c.get("claim_id") in lesson_claim_ids]


def compile_procedure(lesson: dict, claims: list) -> dict:
    """Compile a procedure from a lesson and its source claims.

    Derives typed steps from testable_procedure claims.
    Raises ValueError if lesson lacks actionable evidence.
    """
    # Filter claims to only those referenced by this lesson
    lesson_claims = _filter_claims_for_lesson(lesson, claims)

    # Filter for testable procedure claims
    procedure_claims = [c for c in lesson_claims if c.get("epistemic_type") == "testable_procedure"]

    if not procedure_claims:
        raise ValueError(f"Lesson {lesson['lesson_id']} lacks testable_procedure claims for procedure compilation")

    # Derive steps from procedure claims
    steps = []
    for i, claim in enumerate(procedure_claims):
        steps.append({
            "step_number": i + 1,
            "action": claim["text"],
            "expected_outcome": f"Claim {claim['claim_id']} executed successfully",
            "claim_id": claim["claim_id"],
            "video_id": claim["video_id"],
            "timestamp": claim["start_time"],
        })

    # Compute procedure ID
    procedure_id = hashlib.sha256(
        json.dumps({
            "lesson_id": lesson["lesson_id"],
            "steps": [s["action"] for s in steps]
        }, sort_keys=True).encode()
    ).hexdigest()[:16]

    # Build procedure payload
    procedure_payload = {
        "procedure_id": procedure_id,
        "name": f"{lesson['name']} Procedure",
        "steps": steps,
        "conditions": lesson.get("conditions", []),
        "counterexamples": lesson.get("counterexamples", []),
        "source_refs": lesson["source_refs"],
        "compiler_version": "1.0.0",
        "confidence": lesson["confidence"],
        "status": "draft",
        "created_at": "2026-09-15T00:00:00Z",
    }

    # Compute content hash
    procedure_payload["content_hash"] = hashlib.sha256(
        json.dumps(procedure_payload, sort_keys=True).encode()
    ).hexdigest()

    return procedure_payload


def compile_procedures(lessons: list, claims: list) -> list:
    """Compile procedures for all lessons.

    Fails the batch with structured errors if any lesson cannot be compiled.
    """
    procedures = []
    errors = []

    for lesson in lessons:
        try:
            procedure = compile_procedure(lesson, claims)
            procedures.append(procedure)
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise ValueError(f"Failed to compile procedures for {len(errors)} lessons: {'; '.join(errors)}")

    return procedures


def compile_procedures_with_rejections(lessons: list, claims: list) -> dict:
    """Compile procedures with explicit compiled and rejected collections."""
    procedures = []
    rejections = []

    for lesson in lessons:
        try:
            procedure = compile_procedure(lesson, claims)
            procedures.append(procedure)
        except ValueError as exc:
            rejections.append({
                "lesson_id": lesson["lesson_id"],
                "lesson_name": lesson["name"],
                "reason": "no_testable_procedure",
                "detail": str(exc),
            })
    return {"compiled": procedures, "rejected": rejections}
