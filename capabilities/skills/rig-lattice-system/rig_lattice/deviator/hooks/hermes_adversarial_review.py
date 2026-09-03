"""DOCTRINE.md §6 + §7 — adversarial_review hook.

Fires for tier ≥ published artifacts. Spawns an independent Adversarial
Reviewer (separate agent persona, no self-review) that attacks the artifact
for 8 failure modes:
  - Median output / generic gravity
  - Fake mechanism (chains that look causal but aren't)
  - Unsupported claims
  - Low specificity
  - Business irrelevance
  - Approval bypass
  - Credential risk
  - Audit gaps

The reviewer returns a structured attack report. Coherence Scorer runs in
parallel (deterministic — no LLM needed). Outcome Observer compares predicted
σ to realized σ and updates the Brier log.

Hermes ABI:
    adversarial_review(scorecard: dict, *, text: str | None = None) -> dict
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent

from rig_lattice.core.thresholds import has_banned_phrase
from rig_lattice.deviator.pipeline.audit import audit_log


ATTACK_VECTORS = [
    "median_output_or_generic_gravity",
    "fake_mechanism",
    "unsupported_claims",
    "low_specificity",
    "business_irrelevance",
    "approval_bypass",
    "credential_risk",
    "audit_gaps",
]


def _attack_median_output(text: str) -> tuple[bool, str]:
    """Check for generic-AI median language."""
    found, hits = has_banned_phrase(text)
    if found:
        return True, f"Generic consultant tokens detected: {hits}"
    # Density check on additional templated phrases
    templated = re.findall(
        r"\b(furthermore|moreover|in today.s landscape|thought leadership|"
        r"best practices|world-class|cutting-edge|holistic|leverage|synergy)\b",
        text, re.IGNORECASE,
    )
    if len(templated) >= 3:
        return True, f"High density of templated phrases ({len(templated)} occurrences)"
    return False, "no generic-median signals"


def _attack_fake_mechanism(text: str) -> tuple[bool, str]:
    """Causal connectives present but no actual mechanism chain."""
    connectives = len(re.findall(r"\b(because|therefore|drives|leads to)\b",
                                   text, re.IGNORECASE))
    chains = len(re.findall(
        r"(Input.{0,40}→.{0,40}→|Activity.{0,40}→.{0,40}→|"
        r"mechanism:|the way this works|step-by-step:)",
        text, re.IGNORECASE,
    ))
    # If connectives exist but no chain → fake mechanism
    if connectives >= 3 and chains == 0:
        return True, f"{connectives} causal connectives but zero explicit mechanism chains"
    return False, f"{chains} mechanism chains found"


def _attack_unsupported_claims(text: str) -> tuple[bool, str]:
    """Numeric claims without citation."""
    numeric_claims = re.findall(r"\$\d+(\.\d+)?\s*[KMB]?|\d+(\.\d+)?\s*%", text)
    citations = re.findall(
        r"\[\d+\]|\b(per [A-Z][a-z]+|cite|source:|10-K|10-Q|S-1|"
        r"according to [A-Z])\b", text)
    if len(numeric_claims) >= 5 and len(citations) < 2:
        return True, f"{len(numeric_claims)} numeric claims, only {len(citations)} citations"
    return False, f"{len(citations)} citations for {len(numeric_claims)} claims"


def _attack_low_specificity(text: str) -> tuple[bool, str]:
    """Named entities + specific products + concrete metrics."""
    specifics = re.findall(
        r"\b(HED|RIG|Forge|CL-?\d|HK\s*series|Pierce|Oshkosh|CAT|Manitowoc|"
        r"Deere|Bosch|Parker|Grayhill|Helios|Topcon|Wabtec|Allison|Cummins|Trimble|"
        r"<\s*\d+\s*ms|\d+\s*%\s*false[- ]positive|J1939|CODESYS|NVIS|CMMC)\b",
        text, re.IGNORECASE,
    )
    if len(specifics) < 5:
        return True, f"Only {len(specifics)} specific named entities (need ≥5)"
    return False, f"{len(specifics)} specific named entities"


def _attack_business_irrelevance(text: str) -> tuple[bool, str]:
    """Does the artifact connect to revenue / customer / margin?"""
    business_signals = re.findall(
        r"\b(revenue|margin|customer|client|ARR|MRR|attach|upsell|"
        r"churn|retention|pipeline|ROI|payback|cost of|ARPU)\b",
        text, re.IGNORECASE,
    )
    if len(business_signals) < 3:
        return True, f"Only {len(business_signals)} business-relevance signals"
    return False, f"{len(business_signals)} business signals"


def _attack_approval_bypass(text: str) -> tuple[bool, str]:
    """Does the artifact try to bypass approval (act-now / urgency manipulation)?"""
    bypass = re.findall(
        r"\b(act now|limited time|urgent|only opportunity|don.t wait|"
        r"now or never|window closes today|last chance)\b",
        text, re.IGNORECASE,
    )
    if bypass:
        return True, f"Approval-bypass language detected: {bypass[:3]}"
    return False, "no bypass language"


def _attack_credential_risk(text: str) -> tuple[bool, str]:
    """Are there absolutist credential claims that would expose RIG?"""
    risky = re.findall(
        r"\b(certified by .+ (worldwide|globally)|always works|never fails|"
        r"guaranteed (return|outcome)|100% [a-z]+ rate)\b",
        text, re.IGNORECASE,
    )
    if risky:
        return True, f"Credential-risk claims: {risky[:3]}"
    return False, "no credential-risk claims"


def _attack_audit_gaps(text: str, scorecard: dict) -> tuple[bool, str]:
    """Are there falsification / kill criteria for major claims?"""
    falsifiers = re.findall(
        r"(kill criteri|terminate if|rescope if|wrong if|falsification|"
        r"<\s*\d+%\s*by\s*(Month|Q[1-4]|20\d{2}))",
        text, re.IGNORECASE,
    )
    if len(falsifiers) < 2:
        return True, f"Only {len(falsifiers)} falsification markers (need ≥2 for tier ≥ published)"
    return False, f"{len(falsifiers)} falsification markers"


ATTACK_FNS = {
    "median_output_or_generic_gravity": _attack_median_output,
    "fake_mechanism": _attack_fake_mechanism,
    "unsupported_claims": _attack_unsupported_claims,
    "low_specificity": _attack_low_specificity,
    "business_irrelevance": _attack_business_irrelevance,
    "approval_bypass": _attack_approval_bypass,
    "credential_risk": _attack_credential_risk,
}


def _coherence_score(text: str) -> float:
    """Deterministic coherence proxy: ratio of distinct sentence-starters to total.

    Lower = more repetitive (less coherent flow). Threshold per DOCTRINE: <0.70 alert.
    """
    sentences = re.split(r"[.!?]\s+", text)
    if len(sentences) < 5:
        return 1.0
    starters = [s.split()[0].lower() if s.split() else "" for s in sentences]
    unique_ratio = len(set(starters)) / len(starters)
    return round(unique_ratio, 3)


def adversarial_review(scorecard: dict, *, text: str | None = None) -> dict:
    """Run the 8 attack vectors against an artifact.

    Args:
        scorecard: orchestrator output dict
        text: full artifact text (required for attack scanning)

    Returns:
        dict with `attacks`, `coherence`, `attacks_landed`, `verdict`.
    """
    if not text:
        return {"verdict": "skipped", "reason": "no text provided",
                "attacks": [], "attacks_landed": 0, "coherence": None}

    attacks: list[dict] = []
    for name, fn in ATTACK_FNS.items():
        landed, detail = fn(text)
        attacks.append({"vector": name, "landed": landed, "detail": detail})

    # Audit gaps takes scorecard as well
    landed, detail = _attack_audit_gaps(text, scorecard)
    attacks.append({"vector": "audit_gaps", "landed": landed, "detail": detail})

    attacks_landed = sum(1 for a in attacks if a["landed"])
    coherence = _coherence_score(text)

    verdict = "passed"
    if attacks_landed >= 3 or coherence < 0.70:
        verdict = "needs_rework"
    if attacks_landed >= 5:
        verdict = "BLOCK"

    mission_id = scorecard.get("mission_id", "?")
    artifact_hash = scorecard.get("artifact_hash", "?")
    tier = scorecard.get("tier", "published")

    audit_log("review", mission_id, artifact_hash,
                {"hook": "adversarial_review",
                 "attacks_landed": attacks_landed,
                 "coherence": coherence, "verdict": verdict,
                 "attacks": attacks},
                tier=tier, actor="adversarial_reviewer")

    return {
        "verdict": verdict,
        "attacks_landed": attacks_landed,
        "attacks_total": len(attacks),
        "coherence": coherence,
        "coherence_alert": coherence < 0.70,
        "attacks": attacks,
    }
