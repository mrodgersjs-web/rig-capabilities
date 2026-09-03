"""DOCTRINE.md §2.2 — Sigma score (structural + behavioral blend).

    SigmaScore = 0.3 · structural + 0.7 · behavior
    Patent Examiner trigger: SigmaScore ≥ 5σ
"""
from __future__ import annotations

STRUCTURAL_WEIGHT = 0.3
BEHAVIORAL_WEIGHT = 0.7
PATENT_EXAMINER_THRESHOLD = 5.0


def sigma_score(structural: float, behavior: float) -> float:
    """Blend a structural σ (regex/count detection) with a behavioral σ
    (downstream outcome / Brier-calibrated). Behavior dominates 70/30."""
    return STRUCTURAL_WEIGHT * structural + BEHAVIORAL_WEIGHT * behavior


def patent_examiner_trigger(sigma: float) -> bool:
    """DOCTRINE.md §1.6 — Patent Examiner review fires at σ ≥ 5."""
    return sigma >= PATENT_EXAMINER_THRESHOLD


# ── Sigma anchors (DOCTRINE.md §1.5) ───────────────────────────────────────
SIGMA_ANCHORS = {
    -10: "Extreme inverse / anti-concept; dangerous unless deliberate",
    -8: "World-class restraint OR severe under-indexing",
    -5: "Strong negative deviation, often a hard fail",
    -3: "Below acceptable; usually blocked",
    -1: "Slightly below median",
    0: "Generic median (default LLM output)",
    1: "Slightly above median",
    3: "Minimum RIG pass (escaped generic gravity)",
    5: "RIG signature artifact",
    8: "Frontier / experimental artifact",
    10: "Category creation / doctrine artifact",
    30: "Physics-layer hard-constraint limit",
}


def anchor_label(sigma: float) -> str:
    """Return the nearest anchor label for a given σ value."""
    rounded = min(SIGMA_ANCHORS.keys(), key=lambda x: abs(x - sigma))
    return SIGMA_ANCHORS[rounded]
