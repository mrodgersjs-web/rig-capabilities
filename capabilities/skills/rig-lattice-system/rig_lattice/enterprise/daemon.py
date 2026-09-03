"""Enterprise Daemon — long-running orchestration with slots.

Per the LinkedIn Studio template DAEMON subsystem (17 slots).
Our analog: 9 slots covering audit, baseline-recal, brier-resolve,
audit-chain-verify, integrity-check, alert-scan, runbook-execute,
report-emit, dashboard-refresh.
"""
from __future__ import annotations
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any


class SlotState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    OK = "ok"
    ERROR = "error"


@dataclass
class Slot:
    name: str
    handler: Callable[[], Any]
    interval_seconds: int           # how often to run
    last_run: float = 0.0
    next_run: float = 0.0
    state: SlotState = SlotState.IDLE
    last_result: Any = None
    last_error: str = ""
    run_count: int = 0
    error_count: int = 0

    def due(self, now: float | None = None) -> bool:
        return (now or time.time()) >= self.next_run


def _slot_audit_summary() -> dict:
    """Periodically snapshot in-memory metrics into observability log."""
    from rig_lattice.enterprise.observability import metric_snapshot, log_event
    snap = metric_snapshot()
    log_event("daemon_audit_summary", **{
        "counters": len(snap["counters"]),
        "gauges": len(snap["gauges"]),
        "histograms": len(snap["histograms"]),
    })
    return snap


def _slot_baseline_recal() -> dict:
    """Clear baseline cache so next audit recomputes from corpus."""
    from rig_lattice.adapters.baselines import clear_baseline_cache
    clear_baseline_cache()
    return {"action": "baseline_cache_cleared"}


def _slot_brier_resolve_check() -> dict:
    """Check for predictions whose expected_resolution date has passed."""
    from rig_lattice.deviator.des2_innerloop import _read_brier_history
    history = _read_brier_history()
    unresolved = [e for e in history if e.get("realized") is None]
    overdue = [e for e in unresolved if e.get("expected_resolution") and
                e["expected_resolution"] < time.strftime("%Y-%m-%d", time.gmtime())]
    return {"unresolved_count": len(unresolved), "overdue_count": len(overdue)}


def _slot_audit_chain_verify() -> dict:
    from rig_lattice.enterprise.security import chain_verify
    intact, n, msg = chain_verify()
    return {"intact": intact, "entries": n, "error": msg}


def _slot_db_integrity() -> dict:
    from rig_lattice.enterprise.database import integrity_check
    return integrity_check()


def _slot_alert_scan() -> dict:
    from rig_lattice.enterprise.sre import check_slo_alerts
    new = check_slo_alerts()
    return {"new_alerts": len(new), "names": [a.name for a in new]}


def _slot_approval_expiry_sweep() -> dict:
    from rig_lattice.enterprise.quality_gates import _APPROVALS, ApprovalStatus
    expired = 0
    for r in _APPROVALS.values():
        if r.is_expired():
            r.status = ApprovalStatus.EXPIRED
            expired += 1
    return {"expired_approvals": expired}


def _slot_sla_report() -> dict:
    from rig_lattice.enterprise.sla import promise_report
    return promise_report()


def _slot_health_check() -> dict:
    from rig_lattice.enterprise.observability import health_summary
    return health_summary()


# Canonical 9 slots (analog to LinkedIn Studio's 17)
DEFAULT_SLOTS: list[Slot] = [
    Slot(name="audit_summary",       handler=_slot_audit_summary,       interval_seconds=300),
    Slot(name="baseline_recal",      handler=_slot_baseline_recal,      interval_seconds=604_800),  # weekly
    Slot(name="brier_resolve_check", handler=_slot_brier_resolve_check, interval_seconds=86_400),   # daily
    Slot(name="audit_chain_verify",  handler=_slot_audit_chain_verify,  interval_seconds=3_600),    # hourly
    Slot(name="db_integrity",        handler=_slot_db_integrity,        interval_seconds=86_400),
    Slot(name="alert_scan",          handler=_slot_alert_scan,          interval_seconds=60),
    Slot(name="approval_expiry",     handler=_slot_approval_expiry_sweep, interval_seconds=900),
    Slot(name="sla_report",          handler=_slot_sla_report,          interval_seconds=3_600),
    Slot(name="health_check",        handler=_slot_health_check,        interval_seconds=300),
]


class Daemon:
    """Long-running scheduler that fires slots at their intervals."""

    def __init__(self, slots: list[Slot] | None = None):
        self.slots: list[Slot] = slots or list(DEFAULT_SLOTS)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        # Stagger initial next_run to spread load
        now = time.time()
        for i, s in enumerate(self.slots):
            s.next_run = now + (i * 5)  # 5s apart

    def tick(self) -> list[dict]:
        """Run any due slots. Returns list of executions performed."""
        now = time.time()
        executed = []
        for slot in self.slots:
            if not slot.due(now):
                continue
            slot.state = SlotState.RUNNING
            slot.last_run = now
            slot.run_count += 1
            try:
                slot.last_result = slot.handler()
                slot.state = SlotState.OK
                slot.last_error = ""
            except Exception as e:
                slot.state = SlotState.ERROR
                slot.last_error = f"{type(e).__name__}: {e}"
                slot.error_count += 1
            slot.next_run = now + slot.interval_seconds
            executed.append({
                "slot": slot.name,
                "state": slot.state.value,
                "elapsed_ms": round((time.time() - now) * 1000, 2),
                "result_keys": list(slot.last_result.keys())
                                if isinstance(slot.last_result, dict) else None,
                "error": slot.last_error,
            })
        return executed

    def run_forever(self, sleep_seconds: float = 5.0) -> None:
        """Run tick loop until stopped."""
        while not self._stop.is_set():
            self.tick()
            self._stop.wait(sleep_seconds)

    def start_background(self) -> None:
        """Launch tick loop in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self.run_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)

    def status(self) -> dict:
        return {
            "slots": [
                {
                    "name": s.name,
                    "state": s.state.value,
                    "run_count": s.run_count,
                    "error_count": s.error_count,
                    "last_run": s.last_run,
                    "next_run": s.next_run,
                    "interval_seconds": s.interval_seconds,
                    "last_error": s.last_error,
                }
                for s in self.slots
            ],
            "total_slots": len(self.slots),
            "running": sum(1 for s in self.slots if s.state == SlotState.RUNNING),
            "errored": sum(1 for s in self.slots if s.state == SlotState.ERROR),
        }
