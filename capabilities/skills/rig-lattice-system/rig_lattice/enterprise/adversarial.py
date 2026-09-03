"""Day 7 — Adversarial Reviewer + Coherence Scorer + Outcome Observer.

Per DOCTRINE.md §7 — independence is non-negotiable. Reviewer never
self-reviews; runs as separate persona with disjoint context.

Three components:
  1. Adversarial Reviewer — attacks every artifact across 8 vectors
  2. Coherence Scorer — measures internal coherence across paragraphs
  3. Outcome Observer — compares predicted σ to realized σ, feeds Brier deltas
"""
from __future__ import annotations
import hashlib
import re
import statistics
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent


# ── 1. Adversarial Reviewer ─────────────────────────────────────────────
@dataclass(frozen=True)
class AttackVector:
    name: str
    description: str


ATTACK_VECTORS = (
    AttackVector("median_output_generic_gravity",
                 "Banned consultant tokens / unmistakable AI median language"),
    AttackVector("fake_mechanism",
                 "Causal-sounding chains that aren't actually causal"),
    AttackVector("unsupported_claims",
                 "Claims without sources at tier ≥ client"),
    AttackVector("low_specificity",
                 "Lacks specific named entities, dates, dollar amounts"),
    AttackVector("business_irrelevance",
                 "No business signal (revenue / cost / time / risk)"),
    AttackVector("approval_bypass",
                 "Language designed to bypass governance / approval gates"),
    AttackVector("credential_risk",
                 "Implicit credential claims that could expose the firm"),
    AttackVector("audit_gaps",
                 "No falsification calendar / kill criteria / accountability"),
)


@dataclass
class AdversarialAttack:
    vector: str
    landed: bool             # True if attack found a weakness (artifact loses)
    detail: str
    evidence_quote: str = ""


@dataclass
class AdversarialReview:
    review_id: str
    reviewer_persona: str       # ALWAYS != author persona
    artifact_hash: str
    attacks: list[AdversarialAttack] = field(default_factory=list)
    verdict: str = "pending"    # pass | needs_rework | reject
    coherence: float = 1.0
    timestamp_utc: str = ""

    @property
    def attacks_landed(self) -> int:
        return sum(1 for a in self.attacks if a.landed)

    @property
    def attacks_total(self) -> int:
        return len(self.attacks)

    def to_dict(self) -> dict:
        return {
            "review_id": self.review_id,
            "reviewer_persona": self.reviewer_persona,
            "artifact_hash": self.artifact_hash,
            "verdict": self.verdict,
            "attacks_landed": self.attacks_landed,
            "attacks_total": self.attacks_total,
            "coherence": round(self.coherence, 3),
            "attacks": [{"vector": a.vector, "landed": a.landed, "detail": a.detail}
                          for a in self.attacks],
            "timestamp_utc": self.timestamp_utc,
        }


class IndependentReviewerError(Exception):
    """Raised when a reviewer attempts to review its own author persona."""


def adversarial_review(
    text: str,
    author_persona: str,
    reviewer_persona: str | None = None,
) -> AdversarialReview:
    """Run 8 attack vectors against `text`. Reviewer persona MUST differ from author.

    Args:
        text: artifact under review
        author_persona: who created it (e.g. "claude-sonnet", "human-mike")
        reviewer_persona: who's reviewing (default: adversarial-reviewer-v1)

    Returns:
        AdversarialReview with per-attack verdicts.

    Raises:
        IndependentReviewerError if reviewer_persona == author_persona
    """
    rp = reviewer_persona or "adversarial-reviewer-v1"
    if rp == author_persona:
        raise IndependentReviewerError(
            f"reviewer persona {rp!r} == author {author_persona!r}: "
            "independence violated"
        )

    review = AdversarialReview(
        review_id=f"adv-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}",
        reviewer_persona=rp,
        artifact_hash=hashlib.sha256(text.encode("utf-8")).hexdigest()[:24],
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )

    # 1. Median output / generic gravity
    generic_hits = re.findall(
        r"\b(unlock|transform|seamless|leverage|synergy|holistic|"
        r"world-class|cutting-edge|thought leadership|best practices)\b",
        text, re.IGNORECASE,
    )
    review.attacks.append(AdversarialAttack(
        vector="median_output_or_generic_gravity",
        landed=len(generic_hits) > 0,
        detail=f"Generic tokens detected: {generic_hits[:3]}" if generic_hits else "no generic tokens",
    ))

    # 2. Fake mechanism — causal connectives without verbs
    causal_count = len(re.findall(
        r"\b(because|leads to|drives|causes|via|through|enables|forces)\b",
        text, re.IGNORECASE,
    ))
    review.attacks.append(AdversarialAttack(
        vector="fake_mechanism",
        landed=causal_count == 0,
        detail=f"{causal_count} causal connectives found",
    ))

    # 3. Unsupported claims
    citations = len(re.findall(r"\[\d+\]|\bper\s+[A-Z]|Research and Markets|Helios", text))
    claims = len(re.findall(r"\$\d|\d+%|\d+ (year|month|day)", text))
    review.attacks.append(AdversarialAttack(
        vector="unsupported_claims",
        landed=(claims >= 5 and citations < 1),
        detail=f"{citations} citations for {claims} claims",
    ))

    # 4. Low specificity — named entities count
    named = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b", text)
    review.attacks.append(AdversarialAttack(
        vector="low_specificity",
        landed=len(named) < 5,
        detail=f"{len(named)} multi-word named entities",
    ))

    # 5. Business irrelevance
    biz_signals = len(re.findall(
        r"\$\d|\bROI\b|\brevenue\b|\bmargin\b|\bcost\b|\bcustomer\b|\bclient\b|\brisk\b",
        text, re.IGNORECASE,
    ))
    review.attacks.append(AdversarialAttack(
        vector="business_irrelevance",
        landed=biz_signals < 3,
        detail=f"{biz_signals} business signals",
    ))

    # 6. Approval bypass
    bypass = re.findall(
        r"(skip review|bypass approval|no need for|expedite|fast-track without)",
        text, re.IGNORECASE,
    )
    review.attacks.append(AdversarialAttack(
        vector="approval_bypass",
        landed=len(bypass) > 0,
        detail=f"bypass phrases: {bypass}" if bypass else "no bypass language",
    ))

    # 7. Credential risk
    cred = re.findall(
        r"\b(we are certified in|we guarantee compliance|HIPAA-compliant|SOC2 certified|"
        r"GDPR compliant|FERPA approved)\b",
        text, re.IGNORECASE,
    )
    review.attacks.append(AdversarialAttack(
        vector="credential_risk",
        landed=len(cred) > 0,
        detail=f"credential claims: {cred}" if cred else "no credential-risk claims",
    ))

    # 8. Audit gaps
    falsifiers = len(re.findall(
        r"(kill criteri|terminate if|rescope if|wrong if|falsification|by Month \d)",
        text, re.IGNORECASE,
    ))
    review.attacks.append(AdversarialAttack(
        vector="audit_gaps",
        landed=falsifiers < 1,
        detail=f"{falsifiers} falsification markers",
    ))

    # Coherence scoring (sub-component 2)
    review.coherence = coherence_score(text)

    # Verdict
    landed = review.attacks_landed
    if landed == 0:
        review.verdict = "pass"
    elif landed <= 2:
        review.verdict = "needs_rework"
    else:
        review.verdict = "reject"
    return review


# ── 2. Coherence Scorer ─────────────────────────────────────────────────
def coherence_score(text: str) -> float:
    """Measure cross-paragraph topic coherence on a 0-1 scale.

    Simple proxy: shared named-entity / specialty-token overlap between
    sequential paragraphs. <0.70 → alert operator (per DOCTRINE §7).
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 80]
    if len(paragraphs) < 2:
        return 1.0
    # Extract entity sets per paragraph
    entity_sets = []
    for p in paragraphs:
        ents = set(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2}\b", p))
        # Strip very common words
        ents.discard("The")
        ents.discard("This")
        ents.discard("That")
        entity_sets.append(ents)
    # Jaccard between consecutive pairs
    overlaps = []
    for a, b in zip(entity_sets, entity_sets[1:]):
        if not a and not b:
            overlaps.append(1.0)
            continue
        denom = len(a | b) or 1
        overlaps.append(len(a & b) / denom)
    return statistics.mean(overlaps) if overlaps else 1.0


COHERENCE_ALERT_THRESHOLD = 0.70


def coherence_alert(text: str) -> tuple[bool, float]:
    """Return (alert_needed, coherence)."""
    c = coherence_score(text)
    return c < COHERENCE_ALERT_THRESHOLD, c


# ── 3. Outcome Observer ─────────────────────────────────────────────────
@dataclass
class OutcomeRecord:
    log_id: str
    engine_name: str
    predicted_madz: float
    realized_madz: float
    delta: float
    timestamp_utc: str = ""


def observe_outcome(*,
                     mission_id: str,
                     engine_name: str,
                     predicted_madz: float,
                     realized_madz: float) -> OutcomeRecord:
    """Compare predicted to realized σ; feed Brier delta back to weights.

    Wraps des2_innerloop.record_outcome to keep the Brier log canonical.
    """
    from rig_lattice.deviator.des2_innerloop import record_prediction, record_outcome
    pred = record_prediction(
        mission_id=mission_id,
        engine_name=engine_name,
        predicted_madz=predicted_madz,
    )
    resolution = record_outcome(pred["log_id"], realized_madz)
    return OutcomeRecord(
        log_id=resolution["log_id"] if resolution else pred["log_id"],
        engine_name=engine_name,
        predicted_madz=predicted_madz,
        realized_madz=realized_madz,
        delta=abs(predicted_madz - realized_madz),
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    )


def engine_weight_update(engine_name: str, last_n: int = 20) -> dict:
    """Compute a recommended weight adjustment based on Brier MAE for this engine.

    If MAE < 0.5σ: tighter than threshold → increase weight 5%
    If MAE > 1.5σ: looser than threshold → decrease weight 5%
    Otherwise:    hold weight steady
    """
    from rig_lattice.deviator.des2_innerloop import brier_mae
    mae, n = brier_mae(engine_name, last_n=last_n)
    if n < 3:
        return {"engine_name": engine_name, "mae": mae, "n": n,
                "weight_delta": 0.0, "reason": "insufficient history"}
    if mae < 0.5:
        return {"engine_name": engine_name, "mae": mae, "n": n,
                "weight_delta": +0.05, "reason": "tight calibration"}
    if mae > 1.5:
        return {"engine_name": engine_name, "mae": mae, "n": n,
                "weight_delta": -0.05, "reason": "loose calibration"}
    return {"engine_name": engine_name, "mae": mae, "n": n,
            "weight_delta": 0.0, "reason": "hold"}
