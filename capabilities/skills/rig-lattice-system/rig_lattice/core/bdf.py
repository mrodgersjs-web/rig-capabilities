"""DOCTRINE.md §2.4 — BDF (Build / Defend / Falsify) composite.

    BDF = intent · |MADZ| · craft · restraint

Four positive multipliers. If any factor → 0, the artifact is blocked
regardless of headline score.
"""
from __future__ import annotations

# Any factor below this threshold collapses BDF to zero and blocks the artifact
ZERO_FLOOR = 0.01


def bdf(intent: float, madz: float, craft: float, restraint: float) -> float:
    """Compute the Build/Defend/Falsify composite.

    intent:    Why was this built? (0–1, did the author commit to the bet?)
    madz:      The Robust-MAD-Z score (signed; |·| is taken)
    craft:     How well executed? (0–1, structural rigor)
    restraint: How well-bounded? (0–1, scope discipline)

    If any of {intent, craft, restraint} falls below ZERO_FLOOR, returns 0.0
    — the artifact is blocked regardless of headline score.
    """
    if intent < ZERO_FLOOR or craft < ZERO_FLOOR or restraint < ZERO_FLOOR:
        return 0.0
    return intent * abs(madz) * craft * restraint


def bdf_blocked(intent: float, craft: float, restraint: float) -> bool:
    """True if any BDF factor falls below the zero floor."""
    return intent < ZERO_FLOOR or craft < ZERO_FLOOR or restraint < ZERO_FLOOR


def bdf_explain(intent: float, madz: float,
                  craft: float, restraint: float) -> dict:
    """Diagnostic dict explaining the BDF composite components."""
    blocked = bdf_blocked(intent, craft, restraint)
    return {
        "intent": intent,
        "madz_abs": abs(madz),
        "craft": craft,
        "restraint": restraint,
        "bdf": bdf(intent, madz, craft, restraint),
        "blocked": blocked,
        "weakest": min(
            ("intent", intent),
            ("craft", craft),
            ("restraint", restraint),
            key=lambda kv: kv[1],
        )[0] if blocked else None,
    }
