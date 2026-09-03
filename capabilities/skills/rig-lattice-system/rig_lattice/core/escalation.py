"""DOCTRINE.md §2.3 — Escalation ladder.

Cost-of-review scales with σ. The ladder enforces that civilization-tier
artifacts cost orders of magnitude more to validate than internal notes.

    for |n| ≤ 10:           cost = 2^|n|
    for 10 < |n| ≤ 20:      cost = 1024 · 3^(n−10)
    for 20 < |n| ≤ 30:      cost = 1024 · 3^10 · 5^(n−20)
"""
from __future__ import annotations

# Boundary values memoized for clarity
THRESHOLD_LOW = 10
THRESHOLD_MID = 20
THRESHOLD_HIGH = 30

BASE_LOW = 2          # 2^|n|
BASE_MID = 3          # 1024 · 3^(n−10)
BASE_HIGH = 5         # 1024 · 3^10 · 5^(n−20)

CONSTANT_1024 = 2 ** THRESHOLD_LOW    # 1024 — exactly the boundary value
CONSTANT_3_10 = BASE_MID ** THRESHOLD_LOW  # 59049 — the σ=20 anchor cost


def escalation_cost(sigma: float) -> int:
    """Compute the review cost for an artifact at this σ.

    The function uses |σ| because both extreme negative and extreme positive
    deviations carry the same review burden (dangerous either way).
    """
    n = abs(sigma)
    if n <= THRESHOLD_LOW:
        return int(BASE_LOW ** n)
    if n <= THRESHOLD_MID:
        return int(CONSTANT_1024 * (BASE_MID ** (n - THRESHOLD_LOW)))
    # Cap at σ=30 (physics-layer hard limit)
    n_capped = min(n, THRESHOLD_HIGH)
    return int(CONSTANT_1024 * CONSTANT_3_10 *
                (BASE_HIGH ** (n_capped - THRESHOLD_MID)))


def cost_band(sigma: float) -> str:
    """Return the cost band label for an artifact at this σ."""
    n = abs(sigma)
    if n <= THRESHOLD_LOW:
        return "low (2^|n|)"
    if n <= THRESHOLD_MID:
        return "mid (1024·3^(n−10))"
    return "high (1024·3^10·5^(n−20))"
