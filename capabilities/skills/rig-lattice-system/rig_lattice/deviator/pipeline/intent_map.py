"""DOCTRINE.md §8 Day 2 — Intent map + fallback routing.

Maps a mission's `intent` keyword to:
  - target tier (internal_note → civilization)
  - review mode (quick / standard / doctrine)
  - default Patent Examiner expectation
  - cost cap suggestion for AI gates

Fallback: unknown intent → 'client' tier + 'standard' mode + cost cap $0.10.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class IntentBinding:
    intent: str
    tier: str
    mode: str
    patent_expected: bool
    cost_cap_usd: float
    description: str


INTENT_MAP: dict[str, IntentBinding] = {
    # ── Internal ──────────────────────────────────────────────────────────
    "note":          IntentBinding("note",          "internal_note",     "quick",    False, 0.00,
                                   "Quick capture, low signal, draft territory"),
    "scratch":       IntentBinding("scratch",       "internal_note",     "quick",    False, 0.00,
                                   "Scratch work, not retained"),
    "internal_doc":  IntentBinding("internal_doc",  "internal_artifact", "quick",    False, 0.01,
                                   "Internal team-facing doc"),
    "design_doc":    IntentBinding("design_doc",    "internal_artifact", "standard", False, 0.05,
                                   "Engineering design doc / RFC"),
    "spec":          IntentBinding("spec",          "internal_artifact", "standard", False, 0.05,
                                   "Product spec / PRD"),

    # ── Client / outbound ─────────────────────────────────────────────────
    "outreach":      IntentBinding("outreach",      "client",            "standard", False, 0.05,
                                   "Outreach copy, prospect-facing landing"),
    "client":        IntentBinding("client",        "client",            "standard", True,  0.10,
                                   "Client deliverable / proposal"),
    "proposal":      IntentBinding("proposal",      "client",            "standard", True,  0.25,
                                   "Proposal / RFP response"),
    "rfp":           IntentBinding("rfp",           "client",            "standard", True,  0.25,
                                   "RFP response (alias for proposal)"),
    "landing":       IntentBinding("landing",       "client",            "standard", False, 0.05,
                                   "Marketing landing page copy"),

    # ── Published ─────────────────────────────────────────────────────────
    "blog":          IntentBinding("blog",          "published",         "standard", True,  0.10,
                                   "Public blog post"),
    "substack":      IntentBinding("substack",      "published",         "standard", True,  0.10,
                                   "Substack publication"),
    "press":         IntentBinding("press",         "published",         "doctrine", True,  0.25,
                                   "Press release / public announcement"),
    "investor":      IntentBinding("investor",      "published",         "doctrine", True,  0.50,
                                   "Investor memo / pitch deck"),

    # ── Doctrine ──────────────────────────────────────────────────────────
    "doctrine":      IntentBinding("doctrine",      "doctrine",          "doctrine", True,  0.50,
                                   "Doctrine artifact / new framework"),
    "framework":     IntentBinding("framework",     "doctrine",          "doctrine", True,  0.50,
                                   "Framework documentation"),
    "skill":         IntentBinding("skill",         "doctrine",          "doctrine", True,  0.50,
                                   "Skill promotion candidate"),
    "agent":         IntentBinding("agent",         "doctrine",          "doctrine", True,  0.50,
                                   "Agent persona / promotion candidate"),

    # ── Civilization ──────────────────────────────────────────────────────
    "civilization":  IntentBinding("civilization",  "civilization",      "doctrine", True,  1.00,
                                   "Civilization-grade artifact"),
    "manifesto":     IntentBinding("manifesto",     "civilization",      "doctrine", True,  1.00,
                                   "Manifesto / category-creating doc"),
}


# Fallback for unknown intent strings
FALLBACK = IntentBinding(
    "unknown", "client", "standard", False, 0.10,
    "Unrecognized intent — defaulting to client/standard for safety",
)


def resolve_intent(intent: str | None) -> IntentBinding:
    """Resolve an intent keyword to a binding. Unknown → FALLBACK."""
    if not intent:
        return FALLBACK
    return INTENT_MAP.get(intent.lower(), FALLBACK)


def list_intents() -> list[str]:
    """All known intent keywords."""
    return sorted(INTENT_MAP.keys())
