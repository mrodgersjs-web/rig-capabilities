"""Enterprise SLA Calculator — promise tracking, breach calculation, credit math.

Per the LinkedIn Studio template Runbooks + SLA Calculator subsystem.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── SLA Definitions ─────────────────────────────────────────────────────
@dataclass(frozen=True)
class SLA:
    """One Service Level Agreement promise."""
    name: str
    target_pct: float        # e.g. 99.9 = three nines
    window_seconds: int      # measurement window
    breach_credit_pct: float # service credit if breached, e.g. 10
    description: str = ""


CANONICAL_SLAS = {
    "audit_availability_99_9": SLA(
        name="audit_availability_99_9", target_pct=99.9, window_seconds=2_592_000,
        breach_credit_pct=10.0,
        description="Audit endpoint available 99.9% per month",
    ),
    "audit_latency_p99_under_10s": SLA(
        name="audit_latency_p99_under_10s", target_pct=99.0, window_seconds=2_592_000,
        breach_credit_pct=5.0,
        description="p99 audit latency under 10 s for 99% of calls",
    ),
    "engine_correctness_zero_false_positive": SLA(
        name="engine_correctness_zero_false_positive", target_pct=100.0, window_seconds=2_592_000,
        breach_credit_pct=25.0,
        description="No false-positive HARD_BLOCKs on known-strong fixtures",
    ),
    "weekly_baseline_refresh": SLA(
        name="weekly_baseline_refresh", target_pct=95.0, window_seconds=2_592_000,
        breach_credit_pct=2.0,
        description="Baselines refresh within 8 days of previous refresh ≥95% of cycles",
    ),
}


# ── SLA Tracker ─────────────────────────────────────────────────────────
@dataclass
class SLATracker:
    sla: SLA
    total: int = 0
    breaches: int = 0
    last_breach_at: float = 0.0

    def record(self, ok: bool) -> None:
        self.total += 1
        if not ok:
            self.breaches += 1
            self.last_breach_at = time.time()

    @property
    def actual_pct(self) -> float:
        if self.total == 0:
            return 100.0
        return 100.0 * (self.total - self.breaches) / self.total

    @property
    def is_in_breach(self) -> bool:
        return self.actual_pct < self.sla.target_pct

    @property
    def gap_pct(self) -> float:
        return max(0.0, self.sla.target_pct - self.actual_pct)


_TRACKERS: dict[str, SLATracker] = {}


def record_sla_event(sla_name: str, ok: bool) -> None:
    if sla_name not in CANONICAL_SLAS:
        return
    if sla_name not in _TRACKERS:
        _TRACKERS[sla_name] = SLATracker(sla=CANONICAL_SLAS[sla_name])
    _TRACKERS[sla_name].record(ok)


def get_tracker(sla_name: str) -> SLATracker | None:
    return _TRACKERS.get(sla_name)


# ── Credit math ────────────────────────────────────────────────────────
def credit_owed(sla_name: str, monthly_fee_usd: float) -> float:
    """Return USD service credit owed for a breached SLA this period."""
    t = _TRACKERS.get(sla_name)
    if not t or not t.is_in_breach:
        return 0.0
    return round(monthly_fee_usd * (t.sla.breach_credit_pct / 100.0), 2)


def total_credit_owed(monthly_fee_usd: float) -> dict[str, Any]:
    """Sum credits across all SLAs."""
    by_sla = {name: credit_owed(name, monthly_fee_usd) for name in CANONICAL_SLAS}
    return {
        "monthly_fee_usd": monthly_fee_usd,
        "credits_by_sla": by_sla,
        "total_credit_usd": round(sum(by_sla.values()), 2),
        "breaches": [name for name, t in _TRACKERS.items() if t.is_in_breach],
    }


# ── Promise Report ─────────────────────────────────────────────────────
def promise_report() -> dict:
    """Snapshot of all SLA promises + current status."""
    out = {}
    for name, sla in CANONICAL_SLAS.items():
        t = _TRACKERS.get(name)
        out[name] = {
            "target_pct": sla.target_pct,
            "actual_pct": round(t.actual_pct, 3) if t else 100.0,
            "in_breach": t.is_in_breach if t else False,
            "gap_pct": round(t.gap_pct, 3) if t else 0.0,
            "total_events": t.total if t else 0,
            "breaches": t.breaches if t else 0,
            "breach_credit_pct": sla.breach_credit_pct,
            "description": sla.description,
        }
    return out
