"""normalized_centerytics — deterministic-step evidence normalization (P2 R5).

The two-owner standard requires every model-step candidacy to carry an explicit
deterministic_step record in the canonical selector shape {steps, model_countermeasures}
— the plain-Python steps that were possible with their mechanisms, plus the
countermeasures bounding any later model step. Rejection rationale lives in
agent_reasoning.alternative_rejected_because, not here. Pure data normalization —
no imports beyond typing, no effects. Evidence is owner-authored and must be
exact; malformed records raise ValueError, never model-filled defaults.
"""
from __future__ import annotations

from typing import Any

CLOSED_STEP_KEYS = {"steps", "model_countermeasures"}


def deterministic_step(job: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize a job's deterministic-step evidence into the canonical selector
    shape {steps: [{step, mechanism}], model_countermeasures: [string]}; None
    when the job carries no deterministic evidence at all. Every mandated field
    must be present and non-empty — this record justifies model ownership, so
    incomplete evidence is a ValueError, never a seemingly valid closed record."""
    record = job.get("deterministic_step")
    if record is None:
        evidence = job.get("evidence")
        record = evidence.get("deterministic_step") if isinstance(evidence, dict) else None
    if record is None:
        return None
    if not isinstance(record, dict):
        raise ValueError(
            f"deterministic_step: record must be the closed object, got {type(record).__name__}"
        )
    unknown = set(record) - CLOSED_STEP_KEYS
    if unknown:
        raise ValueError(f"deterministic_step: unknown properties {sorted(unknown)}")
    steps = record.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("deterministic_step: steps must be a non-empty list of {step, mechanism}")
    normalized_steps: list[dict[str, str]] = []
    for index, item in enumerate(steps):
        if not isinstance(item, dict) or set(item) != {"step", "mechanism"}:
            raise ValueError(f"deterministic_step: steps[{index}] must contain exactly step and mechanism")
        step = item.get("step")
        mechanism = item.get("mechanism")
        if not isinstance(step, str) or not step.strip():
            raise ValueError(f"deterministic_step: steps[{index}].step must be a non-empty string")
        if not isinstance(mechanism, str) or not mechanism.strip():
            raise ValueError(f"deterministic_step: steps[{index}].mechanism must be a non-empty string")
        normalized_steps.append({"step": step.strip(), "mechanism": mechanism.strip()})
    countermeasures = record.get("model_countermeasures")
    if not isinstance(countermeasures, list) or any(
        not isinstance(entry, str) or not entry.strip() for entry in countermeasures
    ):
        raise ValueError("deterministic_step: model_countermeasures must be a list of non-empty strings")
    return {
        "steps": normalized_steps,
        "model_countermeasures": [entry.strip() for entry in countermeasures],
    }
