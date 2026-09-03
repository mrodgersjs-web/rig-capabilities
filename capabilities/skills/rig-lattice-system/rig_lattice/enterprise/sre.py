"""Enterprise SRE — SLIs/SLOs, error budgets, circuit breaker, retry with backoff, alerting.

Per the LinkedIn Studio template SRE & Reliability subsystem.
"""
from __future__ import annotations
import random
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


# ── SLIs / SLOs ───────────────────────────────────────────────────────────
@dataclass(frozen=True)
class SLO:
    name: str
    objective: float       # e.g. 0.99 = 99% availability
    window_seconds: int    # measurement window
    description: str = ""


# Canonical RIG Deviator SLOs
SLOS = {
    "audit_availability":      SLO("audit_availability", 0.99, 86_400, "Audit endpoint returns within 5s"),
    "audit_latency_p95":       SLO("audit_latency_p95", 5.0, 3_600, "p95 audit latency < 5s"),
    "engine_pass_rate_floor":  SLO("engine_pass_rate_floor", 0.50, 86_400, "≥50% engines emit non-error result"),
    "physics_gate_uptime":     SLO("physics_gate_uptime", 0.999, 604_800, "Physics gates always available"),
    "baseline_freshness":      SLO("baseline_freshness", 0.95, 604_800, "Baselines refreshed weekly"),
    "des2_amplifier_uptime":   SLO("des2_amplifier_uptime", 0.99, 86_400, "DES² amplifier intact"),
}


@dataclass
class SLITracker:
    """Tracks success/total counts in a rolling window for one SLI."""
    slo: SLO
    successes: int = 0
    total: int = 0

    def record(self, ok: bool) -> None:
        self.total += 1
        if ok:
            self.successes += 1

    @property
    def availability(self) -> float:
        return self.successes / self.total if self.total else 1.0

    @property
    def error_budget_burned(self) -> float:
        """Fraction of error budget consumed. 0.0=fresh, 1.0=fully burned."""
        allowed_errors = (1.0 - self.slo.objective) * self.total
        actual_errors = self.total - self.successes
        if allowed_errors <= 0:
            return 0.0 if actual_errors == 0 else 1.0
        return min(1.0, actual_errors / allowed_errors)

    @property
    def status(self) -> str:
        if self.availability >= self.slo.objective:
            return "HEALTHY"
        if self.error_budget_burned < 1.0:
            return "BURNING"
        return "EXHAUSTED"


_TRACKERS: dict[str, SLITracker] = {}


def record_sli(name: str, ok: bool) -> None:
    if name not in _TRACKERS:
        if name not in SLOS:
            return
        _TRACKERS[name] = SLITracker(slo=SLOS[name])
    _TRACKERS[name].record(ok)


def sli_status() -> dict:
    return {
        name: {
            "objective": t.slo.objective,
            "availability": round(t.availability, 4),
            "total": t.total,
            "error_budget_burned": round(t.error_budget_burned, 3),
            "status": t.status,
        }
        for name, t in _TRACKERS.items()
    }


# ── Circuit Breaker ──────────────────────────────────────────────────────
class CircuitState(str, Enum):
    CLOSED = "closed"        # requests flow through normally
    OPEN = "open"            # requests blocked, fast-fail
    HALF_OPEN = "half_open"  # one probe request allowed


@dataclass
class CircuitBreaker:
    name: str
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 30.0
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    opened_at: float = 0.0

    def call(self, fn: Callable[[], Any]) -> tuple[bool, Any, str]:
        """Execute `fn` with circuit-breaker protection.

        Returns (ok, value, reason).
        """
        # Check if we should transition OPEN → HALF_OPEN
        if self.state == CircuitState.OPEN:
            if time.time() - self.opened_at >= self.timeout_seconds:
                self.state = CircuitState.HALF_OPEN
                self.consecutive_successes = 0
            else:
                return False, None, f"circuit {self.name} OPEN (cooldown active)"

        # Execute
        try:
            value = fn()
            self._record_success()
            return True, value, ""
        except Exception as e:
            self._record_failure()
            return False, None, f"{type(e).__name__}: {e}"

    def _record_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.consecutive_failures = 0
        elif self.state == CircuitState.CLOSED:
            self.consecutive_failures = 0

    def _record_failure(self) -> None:
        self.consecutive_failures += 1
        if self.state == CircuitState.HALF_OPEN:
            # Probe failed → re-open
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
            self.consecutive_successes = 0
        elif self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.opened_at = time.time()


_BREAKERS: dict[str, CircuitBreaker] = {}


def get_breaker(name: str, **kwargs) -> CircuitBreaker:
    if name not in _BREAKERS:
        _BREAKERS[name] = CircuitBreaker(name=name, **kwargs)
    return _BREAKERS[name]


# ── Retry with exponential backoff + jitter ──────────────────────────────
def retry_with_backoff(fn: Callable[[], Any],
                        max_attempts: int = 3,
                        base_delay: float = 0.5,
                        max_delay: float = 30.0,
                        jitter: float = 0.1) -> tuple[bool, Any, list[str]]:
    """Retry `fn` with exponential backoff and jitter.

    Returns (ok, final_value, [error_messages]).
    """
    errors = []
    for attempt in range(1, max_attempts + 1):
        try:
            return True, fn(), errors
        except Exception as e:
            errors.append(f"attempt {attempt}: {type(e).__name__}: {e}")
            if attempt == max_attempts:
                break
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            jittered = delay * (1 + random.uniform(-jitter, jitter))
            time.sleep(jittered)
    return False, None, errors


# ── Alerting ────────────────────────────────────────────────────────────
class AlertSeverity(str, Enum):
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


@dataclass
class Alert:
    name: str
    severity: AlertSeverity
    message: str
    timestamp: float = field(default_factory=time.time)


_ALERTS: deque[Alert] = deque(maxlen=256)


def alert(name: str, severity: AlertSeverity, message: str,
            dispatch: bool = True) -> Alert:
    """Create an alert. When dispatch=True (default), routes to the
    notification system based on severity.

    AlertSeverity.CRITICAL always dispatches to all configured channels.
    AlertSeverity.WARN dispatches to Slack only.
    AlertSeverity.INFO is local-log only (zero outbound traffic).
    """
    a = Alert(name=name, severity=severity, message=message)
    _ALERTS.append(a)
    if dispatch:
        try:
            from rig_lattice.enterprise.notify import dispatch_alert
            dispatch_alert(a)
        except Exception:
            # Never let notification failure break alert recording
            pass
    return a


def recent_alerts(severity: AlertSeverity | None = None,
                    limit: int = 20) -> list[Alert]:
    if severity is None:
        return list(_ALERTS)[-limit:]
    return [a for a in _ALERTS if a.severity == severity][-limit:]


def check_slo_alerts() -> list[Alert]:
    """Scan tracker state, emit alerts when error budget burns high."""
    new_alerts = []
    for name, t in _TRACKERS.items():
        burned = t.error_budget_burned
        if burned >= 0.90:
            a = alert(f"slo_budget_exhausted_{name}", AlertSeverity.CRITICAL,
                      f"SLO {name}: {burned:.1%} error budget burned")
            new_alerts.append(a)
        elif burned >= 0.50:
            a = alert(f"slo_budget_burning_{name}", AlertSeverity.WARN,
                      f"SLO {name}: {burned:.1%} error budget burned")
            new_alerts.append(a)
    return new_alerts
