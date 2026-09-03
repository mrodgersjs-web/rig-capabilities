"""DOCTRINE.md §2.6 + §4 — 6-tier THRESHOLDS dict + detonation_gate.

Audience-graded gates. Each tier maps to a minimum σ, whether Patent Examiner
review is required, whether Doctrine Council review is required, and the
review cost band.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

# ── Verdicts ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Verdict:
    status: Literal["PASS", "BLOCK"]
    reason: str = ""

    def __bool__(self) -> bool:
        return self.status == "PASS"


PASS = Verdict("PASS", "passed all gates")


def BLOCK(reason: str) -> Verdict:
    return Verdict("BLOCK", reason)


# ── 6-tier threshold map (DOCTRINE.md §1.6) ───────────────────────────────
THRESHOLDS = {
    "internal_note": {
        "minSigma": 1,
        "requiresPatentExaminer": False,
        "requiresDoctrineCouncil": False,
        "costBand": "$0",
    },
    "internal_artifact": {
        "minSigma": 3,
        "requiresPatentExaminer": False,
        "requiresDoctrineCouncil": False,
        "costBand": "$0.01",
    },
    "client": {
        "minSigma": 3,
        "requiresPatentExaminer": "conditional",
        "requiresDoctrineCouncil": False,
        "costBand": "$0.05",
    },
    "published": {
        "minSigma": 5,
        "requiresPatentExaminer": True,
        "requiresDoctrineCouncil": False,
        "costBand": "$1",
    },
    "doctrine": {
        "minSigma": 8,
        "requiresPatentExaminer": True,
        "requiresDoctrineCouncil": True,
        "costBand": "$10",
    },
    "civilization": {
        "minSigma": 10,
        "requiresPatentExaminer": True,
        "requiresDoctrineCouncil": True,
        "costBand": "$50",
    },
}


# ── Reference detonation_gate (DOCTRINE.md §4.1) ──────────────────────────
def detonation_gate(robust_mad_z: float,
                     patent_verdict: str = "not_required",
                     tier: str = "client") -> Verdict:
    """Decide whether an artifact can ship at the given tier.

    Args:
        robust_mad_z: The artifact's RIG-L or headline RobustMADZ.
        patent_verdict: One of {"novel", "derivative", "not_required"}.
                         Must be "novel" for tiers requiring Patent Examiner.
        tier: One of THRESHOLDS keys.

    Returns:
        Verdict — PASS if all gates clear, BLOCK with reason otherwise.
    """
    if tier not in THRESHOLDS:
        return BLOCK(f"Unknown tier: {tier}")
    t = THRESHOLDS[tier]

    if abs(robust_mad_z) < t["minSigma"]:
        return BLOCK(f"Below {t['minSigma']}σ for tier {tier} "
                      f"(got {robust_mad_z:+.2f}σ).")

    requires_pe = t.get("requiresPatentExaminer")
    if requires_pe is True and patent_verdict != "novel":
        return BLOCK("Patent Examiner verdict required: must be 'novel'.")
    if requires_pe == "conditional" and patent_verdict not in ("novel", "not_required"):
        return BLOCK(f"Conditional Patent Examiner review failed: {patent_verdict}.")

    # Doctrine Council enforcement is downstream (timing-based) — encoded here
    # as a marker that callers must verify out-of-band.
    if t.get("requiresDoctrineCouncil"):
        # Caller must inject a council_verdict; if missing, this is documentation
        pass

    return PASS


# ── Hard-block list (DOCTRINE.md §4.2) ────────────────────────────────────
BANNED_PHRASES = (
    "unlock", "transform", "seamless", "scale effortlessly",
    "Get Started", "Learn More", "Book a Demo",
)


def has_banned_phrase(text: str) -> tuple[bool, list[str]]:
    """Return (found, list_of_violators) for hard-block phrase scan."""
    text_lower = text.lower()
    hits = [p for p in BANNED_PHRASES if p.lower() in text_lower]
    return (bool(hits), hits)
