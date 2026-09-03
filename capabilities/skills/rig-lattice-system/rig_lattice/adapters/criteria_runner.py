"""DOCTRINE.md §5 — Convert YAML criteria pack → raw_fn for a DeviationEngine.

Reuses the existing v3 strict criteria packs at criteria/<slug>.yaml. Each
pack has 5-10 yes/no questions with detection modes (regex, count_min,
ratio_min, absent, proximity, llm_judge). This adapter:

  1. Loads the YAML pack
  2. Runs every question's detection function
  3. Returns a weighted raw score (sum of passing weights, on a 0-100 scale)

The raw score gets fed to Robust-MAD-Z against the baseline_fn corpus to
produce the σ deviation for the engine.
"""
from __future__ import annotations
import re
from typing import Any

# Reuse the v3 auditor's detection logic — battle-tested — and its
# JSON-first criteria loader, which is what keeps this path stdlib-only.
# PyYAML is a compile-time dependency of scripts/compile_criteria.py, never a
# runtime one: the packs are read from criteria/<slug>.json.
from rig_lattice.deviator.auditor import (
    _detect_regex, _detect_absent, _detect_proximity,
    _detect_count, CRITERIA_DIR, _load_criteria,
)


def score_one_question(text: str, q: dict) -> tuple[bool, float, str]:
    """Run a single criterion question. Returns (passed, weight, evidence)."""
    mode = q.get("mode", "regex")
    weight = float(q.get("weight", 1.0))

    if mode == "regex":
        passed, ev = _detect_regex(
            text, q["pattern"],
            min_count=q.get("min_count", 1),
            max_count=q.get("max_count"),
            flags=q.get("flags", "i"),
        )
    elif mode == "absent":
        passed, ev = _detect_absent(text, q["patterns"], flags=q.get("flags", "i"))
    elif mode == "proximity":
        passed, ev = _detect_proximity(
            text, q["anchor"], q["target"],
            window_chars=q.get("window_chars", 800),
            flags=q.get("flags", "i"),
        )
    elif mode == "count_min":
        matches = re.findall(q["pattern"], text, re.IGNORECASE)
        threshold = int(q.get("threshold", 1))
        passed = len(matches) >= threshold
        ev = f"{len(matches)} matches (need ≥{threshold})"
    elif mode == "ratio_min":
        matches = re.findall(q["pattern"], text, re.IGNORECASE)
        words = max(len(text.split()), 1)
        density = len(matches) / words * 1000
        threshold = float(q.get("threshold", 1.0))
        passed = density >= threshold
        ev = f"density {density:.1f}/kw (need ≥{threshold})"
    else:
        passed, ev = False, f"unknown mode {mode}"

    return passed, weight, ev


def raw_score_from_criteria(text: str, criteria_pack: dict | str) -> float:
    """Compute a 0-100 raw score from a criteria pack on this text.

    Args:
        text: the artifact to score
        criteria_pack: either a parsed dict OR a slug to load from criteria/<slug>.json

    Returns:
        Raw score on 0-100 scale (% of criteria-weight passed).
    """
    if isinstance(criteria_pack, str):
        criteria_pack = _load_criteria(criteria_pack)

    questions = criteria_pack.get("questions", [])
    if not questions:
        return 50.0  # no criteria → neutral

    total_weight = sum(float(q.get("weight", 1.0)) for q in questions)
    earned = 0.0
    for q in questions:
        try:
            passed, weight, _ = score_one_question(text, q)
            if passed:
                earned += weight
        except Exception:
            # Bad pattern in YAML → fail closed
            pass

    return round((earned / total_weight) * 100, 2) if total_weight > 0 else 50.0


def detailed_score(text: str, criteria_pack: dict | str) -> dict:
    """Same as raw_score_from_criteria but returns per-question detail.

    Used by ProofPacket emission and debug paths.
    """
    if isinstance(criteria_pack, str):
        criteria_pack = _load_criteria(criteria_pack)

    questions = criteria_pack.get("questions", [])
    results = []
    earned = 0.0
    total_weight = 0.0

    for q in questions:
        try:
            passed, weight, ev = score_one_question(text, q)
        except Exception as e:
            passed, weight, ev = False, float(q.get("weight", 1.0)), f"error: {e}"

        total_weight += weight
        if passed:
            earned += weight

        results.append({
            "id": q["id"],
            "question": q["question"],
            "mode": q.get("mode", "regex"),
            "passed": passed,
            "weight": weight,
            "evidence": ev[:200] if ev else "",
            "required": bool(q.get("required", False)),
        })

    raw_score = round((earned / total_weight) * 100, 2) if total_weight > 0 else 50.0
    failed_required = [r["id"] for r in results if r["required"] and not r["passed"]]

    return {
        "slug": criteria_pack.get("slug"),
        "codename": criteria_pack.get("codename"),
        "raw_score": raw_score,
        "earned": round(earned, 2),
        "total_weight": round(total_weight, 2),
        "questions_total": len(questions),
        "questions_passed": sum(1 for r in results if r["passed"]),
        "failed_required": failed_required,
        "questions": results,
    }
