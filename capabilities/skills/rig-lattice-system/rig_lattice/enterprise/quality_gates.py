"""Enterprise Quality Gates — banned phrases, content length, approval gate, regression tests.

Per the LinkedIn Studio template Quality Gates subsystem.
"""
from __future__ import annotations
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent

# ── Banned phrases ──────────────────────────────────────────────────────
# Composed from DOCTRINE §4.2 + LinkedIn Studio template
BANNED_PHRASES = (
    # AI/consultant slop
    "unlock", "transform", "seamless", "scale effortlessly",
    "Get Started", "Learn More", "Book a Demo",
    "leverage", "synergy", "holistic",
    "world-class", "cutting-edge", "game-changing",
    "thought leadership", "best practices",
    # Empty CTAs
    "in today's landscape", "in today's rapidly evolving",
    "we are excited to announce", "we are pleased to share",
    # Filler connectors
    "furthermore", "moreover",
)


def banned_phrase_violations(text: str) -> list[tuple[str, int]]:
    """Return [(phrase, count), ...] for any banned phrases found."""
    text_lower = text.lower()
    out = []
    for phrase in BANNED_PHRASES:
        count = text_lower.count(phrase.lower())
        if count > 0:
            out.append((phrase, count))
    return out


# ── Content length ──────────────────────────────────────────────────────
@dataclass(frozen=True)
class LengthRule:
    name: str
    min_words: int
    max_words: int
    description: str = ""


LENGTH_RULES = {
    "linkedin_post":        LengthRule("linkedin_post",    50,   220, "LinkedIn post body"),
    "executive_memo":       LengthRule("executive_memo",  500,  2_000, "Exec memo / brief"),
    "rfp_response":         LengthRule("rfp_response",  1_500,  8_000, "RFP response"),
    "proposal":             LengthRule("proposal",     1_500, 12_000, "Full client proposal"),
    "design_doc":           LengthRule("design_doc",     800,  4_000, "Engineering design doc"),
    "landing_copy":         LengthRule("landing_copy",   100,   800, "Landing-page hero + body"),
    "outreach_email":       LengthRule("outreach_email",   60,   180, "Cold outreach email"),
}


def length_check(text: str, kind: str) -> tuple[bool, str]:
    """Return (passes, reason)."""
    if kind not in LENGTH_RULES:
        return True, f"no length rule for kind={kind}"
    rule = LENGTH_RULES[kind]
    n = len(text.split())
    if n < rule.min_words:
        return False, f"too short: {n} words (need ≥{rule.min_words} for {kind})"
    if n > rule.max_words:
        return False, f"too long: {n} words (max {rule.max_words} for {kind})"
    return True, f"{n} words within [{rule.min_words}, {rule.max_words}]"


# ── Approval Gate ───────────────────────────────────────────────────────
class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    request_id: str
    artifact_hash: str
    tier: str
    requested_by: str
    reason: str = ""
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: str = ""
    approved_at: float = 0.0
    requested_at: float = field(default_factory=time.time)
    ttl_seconds: int = 24 * 3600  # 24h default

    def is_expired(self) -> bool:
        return (self.status == ApprovalStatus.PENDING
                and time.time() - self.requested_at > self.ttl_seconds)


_APPROVALS: dict[str, ApprovalRequest] = {}


def request_approval(artifact_hash: str, tier: str, requested_by: str,
                      reason: str = "", ttl_seconds: int = 24 * 3600) -> ApprovalRequest:
    req = ApprovalRequest(
        request_id=f"appr-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}",
        artifact_hash=artifact_hash,
        tier=tier,
        requested_by=requested_by,
        reason=reason,
        ttl_seconds=ttl_seconds,
    )
    _APPROVALS[req.request_id] = req
    return req


def grant_approval(request_id: str, approver: str) -> ApprovalRequest | None:
    req = _APPROVALS.get(request_id)
    if not req:
        return None
    if req.is_expired():
        req.status = ApprovalStatus.EXPIRED
        return req
    req.status = ApprovalStatus.APPROVED
    req.approved_by = approver
    req.approved_at = time.time()
    return req


def reject_approval(request_id: str, approver: str, reason: str = "") -> ApprovalRequest | None:
    req = _APPROVALS.get(request_id)
    if not req:
        return None
    req.status = ApprovalStatus.REJECTED
    req.approved_by = approver
    req.approved_at = time.time()
    if reason:
        req.reason = f"{req.reason} || rejected: {reason}".lstrip(" |")
    return req


def get_approval(request_id: str) -> ApprovalRequest | None:
    return _APPROVALS.get(request_id)


def pending_approvals(tier: str | None = None) -> list[ApprovalRequest]:
    pending = [r for r in _APPROVALS.values() if r.status == ApprovalStatus.PENDING]
    if tier:
        pending = [r for r in pending if r.tier == tier]
    # Mark expired
    for r in pending:
        if r.is_expired():
            r.status = ApprovalStatus.EXPIRED
    return [r for r in pending if not r.is_expired()]


# ── Regression Tests ────────────────────────────────────────────────────
@dataclass
class RegressionCase:
    name: str
    artifact_text: str
    expected_min_rig_l: float
    expected_max_hard_blocks: int


REGRESSION_SUITE: list[RegressionCase] = [
    RegressionCase(
        name="hed_v2_5_baseline",
        artifact_text="",  # filled in from examples/example_strict_passing.md on init
        expected_min_rig_l=0.0,
        expected_max_hard_blocks=10,
    ),
]


def load_regression_fixtures() -> None:
    """Populate REGRESSION_SUITE artifacts from disk fixtures."""
    hed = ROOT / "examples" / "example_strict_passing.md"
    if hed.exists():
        REGRESSION_SUITE[0] = RegressionCase(
            name="hed_v2_5_baseline",
            artifact_text=hed.read_text(),
            expected_min_rig_l=0.0,
            expected_max_hard_blocks=10,
        )


def run_regression() -> dict:
    """Run all regression cases. Returns per-case + overall pass/fail."""
    load_regression_fixtures()
    import sys
    from rig_lattice.deviator.auditor import audit_all

    results = []
    for case in REGRESSION_SUITE:
        if not case.artifact_text:
            results.append({"name": case.name, "ok": False, "reason": "no fixture"})
            continue
        audit = audit_all(case.artifact_text, llm_enabled=False)
        rig_l = audit.get("rig_l", 0)
        hard_blocks = audit.get("hard_blocks", 0)
        ok = (rig_l >= case.expected_min_rig_l
              and hard_blocks <= case.expected_max_hard_blocks)
        results.append({
            "name": case.name,
            "ok": ok,
            "rig_l": rig_l,
            "hard_blocks": hard_blocks,
            "expected_min_rig_l": case.expected_min_rig_l,
            "expected_max_hard_blocks": case.expected_max_hard_blocks,
        })
    return {
        "ok": all(r["ok"] for r in results),
        "total": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "cases": results,
    }
