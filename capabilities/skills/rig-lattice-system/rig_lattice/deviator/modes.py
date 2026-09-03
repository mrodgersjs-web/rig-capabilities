"""Three-mode review depth per DOCTRINE.md §6.2.

  Quick     — 3 engines (Gravity Escape, Reality Anchor, Memory Residue)
              for small edits, low-risk internal artifacts (BMS A1)
  Standard  — 10 engines (Cognitive 01–10) for briefs, specs, normal
              missions (BMS A2/A3)
  Doctrine  — All 40 engines for production releases, doctrine changes,
              agent promotion, civilization artifacts (BMS A4)
"""
from __future__ import annotations

QUICK_ENGINES = [
    "gravity_escape",
    "reality_anchor",
    "memory_residue",
]

STANDARD_ENGINES = [
    "gravity_escape",
    "reality_anchor",
    "feynman_xray",
    "mechanism_furnace",
    "rupture",
    "frame_collision",
    "voltage",
    "darwinian_selection",   # evolutionary memory flywheel analog
    "memory_residue",
    "temporal_horizon_integrity",
]

# Doctrine = None → run all 40 engines from criteria/

MODE_REGISTRY = {
    "quick":    QUICK_ENGINES,
    "standard": STANDARD_ENGINES,
    "doctrine": None,
}


def resolve_engines(mode: str) -> list[str] | None:
    """Return the list of engine slugs to run for this mode (None = all 40)."""
    if mode not in MODE_REGISTRY:
        raise ValueError(f"unknown mode {mode!r}; choose from {list(MODE_REGISTRY)}")
    return MODE_REGISTRY[mode]


def tier_to_mode(tier: str) -> str:
    """Map artifact tier → review mode per DOCTRINE.md §1.6."""
    return {
        "internal_note":     "quick",
        "internal_artifact": "quick",
        "client":            "standard",
        "published":         "standard",
        "doctrine":          "doctrine",
        "civilization":      "doctrine",
    }.get(tier, "standard")
