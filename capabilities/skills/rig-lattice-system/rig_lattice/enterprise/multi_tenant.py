"""Enterprise Multi-Tenant — token bucket rate limiter, RIG-cap-aware, quota tracking.

Per the LinkedIn Studio template Multi-Tenant subsystem.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class TokenBucket:
    """Classic token-bucket rate limiter.

    capacity:   max tokens the bucket holds
    refill_rate: tokens added per second
    """
    capacity: float
    refill_rate: float
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)
    _lock: Lock = field(default_factory=Lock)

    def __post_init__(self):
        if self.tokens == 0.0:
            self.tokens = self.capacity

    def consume(self, n: float = 1.0) -> tuple[bool, float]:
        """Try to consume `n` tokens. Returns (allowed, wait_seconds_if_blocked)."""
        with self._lock:
            self._refill()
            if self.tokens >= n:
                self.tokens -= n
                return True, 0.0
            deficit = n - self.tokens
            wait = deficit / self.refill_rate if self.refill_rate > 0 else float("inf")
            return False, wait

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now


# ── Per-tenant buckets ──────────────────────────────────────────────────
@dataclass
class Tenant:
    tenant_id: str
    name: str = ""
    audits_per_hour: int = 1000
    llm_calls_per_hour: int = 200
    monthly_quota_audits: int = 100_000

    def __post_init__(self):
        self.audit_bucket = TokenBucket(
            capacity=self.audits_per_hour,
            refill_rate=self.audits_per_hour / 3600,
        )
        self.llm_bucket = TokenBucket(
            capacity=self.llm_calls_per_hour,
            refill_rate=self.llm_calls_per_hour / 3600,
        )
        self.month_audit_count: int = 0
        self.month_started: float = time.time()


_TENANTS: dict[str, Tenant] = {}


def register_tenant(tenant_id: str, **kwargs) -> Tenant:
    t = Tenant(tenant_id=tenant_id, **kwargs)
    _TENANTS[tenant_id] = t
    return t


def get_tenant(tenant_id: str) -> Tenant | None:
    return _TENANTS.get(tenant_id)


def consume_audit(tenant_id: str) -> tuple[bool, str]:
    """Consume one audit token. Returns (allowed, reason)."""
    t = _TENANTS.get(tenant_id)
    if not t:
        return False, f"unknown tenant {tenant_id}"

    # Monthly quota
    _check_month_rollover(t)
    if t.month_audit_count >= t.monthly_quota_audits:
        return False, f"monthly quota exhausted ({t.month_audit_count}/{t.monthly_quota_audits})"

    ok, wait = t.audit_bucket.consume(1.0)
    if not ok:
        return False, f"rate limited; wait {wait:.1f}s"

    t.month_audit_count += 1
    return True, ""


def consume_llm_call(tenant_id: str, cost_units: float = 1.0) -> tuple[bool, str]:
    """Consume `cost_units` LLM tokens (default 1 per call; can scale by cost)."""
    t = _TENANTS.get(tenant_id)
    if not t:
        return False, f"unknown tenant {tenant_id}"
    ok, wait = t.llm_bucket.consume(cost_units)
    if not ok:
        return False, f"LLM rate limited; wait {wait:.1f}s"
    return True, ""


def _check_month_rollover(t: Tenant) -> None:
    """Reset monthly counter after 30 days."""
    if time.time() - t.month_started >= 30 * 86_400:
        t.month_audit_count = 0
        t.month_started = time.time()


def quota_status(tenant_id: str) -> dict:
    t = _TENANTS.get(tenant_id)
    if not t:
        return {"error": "unknown tenant"}
    _check_month_rollover(t)
    return {
        "tenant_id": t.tenant_id,
        "name": t.name,
        "audit_bucket_tokens": round(t.audit_bucket.tokens, 2),
        "audit_bucket_capacity": t.audit_bucket.capacity,
        "llm_bucket_tokens": round(t.llm_bucket.tokens, 2),
        "llm_bucket_capacity": t.llm_bucket.capacity,
        "monthly_audits_used": t.month_audit_count,
        "monthly_audits_quota": t.monthly_quota_audits,
        "monthly_pct_used": round(t.month_audit_count / t.monthly_quota_audits * 100, 1),
    }
