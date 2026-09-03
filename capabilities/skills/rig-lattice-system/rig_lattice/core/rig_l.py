"""DOCTRINE.md §2.5 — RIG-L composite headline number.

| RIG-L | Meaning |
| --- | --- |
| < 3.0   | Block. Generic, shallow, unsafe, fake-understanding, non-compounding |
| 3.0–3.9 | Pass. Proprietary edge exists. Needs strengthening                     |
| 4.0–4.9 | Category rupture. Strong enough to publish, ship, test aggressively    |
| 5.0–7.9 | RIG signature. Distinctive, believable, mechanistic, memorable          |
| 8.0–9.9 | Frontier artifact. Hard to copy, high residue, creates new behavior     |
| 10+     | Doctrine artifact. Creates a new frame, vocabulary, category, OS pattern |
"""
from __future__ import annotations
from typing import Sequence


def rig_l_composite(layer_sigmas: dict[str, list[float]],
                     hard_blocks: int = 0) -> float:
    """Compute the composite RIG-L from per-layer σ pulls.

    Per DOCTRINE.md doctrine: take the top-6 |σ| pulls (the strongest deviation
    signal across layers), average them, and apply a risk penalty proportional
    to the count of physics-layer hard-blocks.

    Args:
        layer_sigmas: {layer_name: [σ_values]}
        hard_blocks: count of L3 physics short-circuits.

    Returns:
        Composite RIG-L score. Negative if predominantly negative pulls;
        positive if predominantly positive. Capped by risk penalty.
    """
    all_sigmas = []
    for sigmas in layer_sigmas.values():
        all_sigmas.extend(sigmas)
    if not all_sigmas:
        return 0.0

    # Top-6 |σ| pulls — preserve sign in the average
    top_pulls = sorted(all_sigmas, key=lambda s: -abs(s))[:6]
    mean_pull = sum(top_pulls) / len(top_pulls)

    # Risk penalty: each hard-block subtracts 30% of the composite
    risk_penalty = min(0.9, hard_blocks * 0.3)
    composite = mean_pull * (1 - risk_penalty)

    return round(composite, 2)


def rig_l_label(rig_l: float) -> str:
    """Return the RIG-L band label per DOCTRINE.md §2.5."""
    if rig_l < 3.0:
        return "block"
    if rig_l < 4.0:
        return "pass_needs_strengthening"
    if rig_l < 5.0:
        return "category_rupture"
    if rig_l < 8.0:
        return "rig_signature"
    if rig_l < 10.0:
        return "frontier_artifact"
    return "doctrine_artifact"


def rig_l_description(rig_l: float) -> str:
    """Return the prose description for an RIG-L value."""
    if rig_l < 3.0:
        return "Block. Generic, shallow, unsafe, fake-understanding, or non-compounding."
    if rig_l < 4.0:
        return "Pass. Proprietary edge exists. Needs strengthening."
    if rig_l < 5.0:
        return "Category rupture. Strong enough to publish, ship, test aggressively."
    if rig_l < 8.0:
        return "RIG signature. Distinctive, believable, mechanistic, memorable."
    if rig_l < 10.0:
        return "Frontier artifact. Hard to copy, high residue, creates new behavior."
    return "Doctrine artifact. Creates a new frame, vocabulary, category, or OS pattern."
