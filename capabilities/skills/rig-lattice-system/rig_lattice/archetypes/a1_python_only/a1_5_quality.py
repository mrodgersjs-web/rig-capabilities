"""A1.5 — Quality (PYTHON_ONLY).

Does: run deterministic gates over a Draft. At this BMS band the only
model-touch would be an optional "slop judge" (Promptfoo); the structural
gates below are pure Python and run first. If any hard gate fails, the
QualityResult.passed is False and the run layer stops the cell.

Gates implemented (all deterministic):
  G1 non_empty_body      — the artifact body is present
  G2 source_per_claim    — at least one source backs the draft
  G3 shim_within_limit   — personalization shim <= 60 words
"""
from __future__ import annotations

from ._types import Draft, QualityResult
from .a1_4_solution import SHIM_WORD_LIMIT

HARD_GATES = ("non_empty_body", "source_per_claim", "shim_within_limit")


def evaluate(draft: Draft) -> QualityResult:
    passed: list[str] = []

    if draft.body and draft.body.strip():
        passed.append("non_empty_body")
    else:
        return QualityResult(passed=False, gates_passed=passed, reason="empty body")

    if draft.sources:
        passed.append("source_per_claim")
    else:
        return QualityResult(
            passed=False, gates_passed=passed, reason="no source backs the draft"
        )

    if len((draft.personalization or "").split()) <= SHIM_WORD_LIMIT:
        passed.append("shim_within_limit")
    else:
        return QualityResult(
            passed=False,
            gates_passed=passed,
            reason=f"shim exceeds {SHIM_WORD_LIMIT} words",
        )

    return QualityResult(passed=True, gates_passed=passed, reason=None)


def run(draft: Draft) -> QualityResult:
    return evaluate(draft)
