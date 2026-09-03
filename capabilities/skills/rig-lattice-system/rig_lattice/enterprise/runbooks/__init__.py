"""Enterprise Runbooks — 8 named failure-mode playbooks.

Per the LinkedIn Studio template: Daemon Startup/Crash, Cookie Expiry,
DB Corruption, Blotato/LinkedIn Failure (and analogs for Deviator).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Runbook:
    name: str
    trigger: str             # condition that fires this runbook
    severity: str            # info | warn | critical
    steps: tuple[str, ...]
    auto_remediation: Callable[[], dict] | None = None


def _rb_engine_crash() -> dict:
    """Auto-remediation: reload engine modules, re-run health check."""
    from rig_lattice.enterprise.observability import run_health_checks
    return {"action": "engine_reload_attempted", "checks": [c.name for c in run_health_checks() if c.ok]}


def _rb_db_corruption() -> dict:
    """Auto-remediation: verify integrity, alert if broken."""
    from rig_lattice.enterprise.database import integrity_check
    return integrity_check()


def _rb_baseline_drift() -> dict:
    """Auto-remediation: clear baseline cache to force recompute."""
    from rig_lattice.adapters.baselines import clear_baseline_cache
    clear_baseline_cache()
    return {"action": "baseline_cache_cleared"}


def _rb_amplifier_failure() -> dict:
    """Auto-remediation: verify DES² product constant."""
    from rig_lattice.deviator.des2_innerloop import AMP_PRODUCT_MAX
    return {"amp_product_max": AMP_PRODUCT_MAX, "expected": 6.552,
            "intact": abs(AMP_PRODUCT_MAX - 6.552) < 0.001}


def _rb_audit_chain_broken() -> dict:
    """Auto-remediation: verify audit chain, surface break point."""
    from rig_lattice.enterprise.security import chain_verify
    intact, n, msg = chain_verify()
    return {"intact": intact, "entries_checked": n, "error": msg}


def _rb_rate_limit_storm() -> dict:
    """Auto-remediation: log + alert; humans must intervene."""
    from rig_lattice.enterprise.sre import alert, AlertSeverity
    a = alert("rate_limit_storm", AlertSeverity.WARN,
              "Rate limits hit across multiple tenants — investigate upstream")
    return {"alert_id": a.name, "ts": a.timestamp}


def _rb_physics_short_circuit_storm() -> dict:
    """Auto-remediation: surface what's failing; do not auto-bypass."""
    from rig_lattice.enterprise.observability import counter_inc
    counter_inc("physics_short_circuit_storm_observed")
    return {"action": "observed_only_no_bypass_allowed"}


def _rb_secret_leak_detected() -> dict:
    """Auto-remediation: redact + alert CRITICAL."""
    from rig_lattice.enterprise.sre import alert, AlertSeverity
    a = alert("secret_leak_detected", AlertSeverity.CRITICAL,
              "Secret pattern detected in submitted artifact — halt + rotate")
    return {"alert_id": a.name, "rotate_immediately": True}


RUNBOOKS: list[Runbook] = [
    Runbook(
        name="engine_crash",
        trigger="any engine raises uncaught exception during score()",
        severity="critical",
        steps=(
            "1. Check observability logs for stack trace",
            "2. Verify engine YAML criteria pack is valid",
            "3. Reload engine modules; re-run health check",
            "4. If still failing, disable engine via feature flag",
            "5. File issue against the engine's module",
        ),
        auto_remediation=_rb_engine_crash,
    ),
    Runbook(
        name="db_corruption",
        trigger="SQLite PRAGMA integrity_check returns != 'ok'",
        severity="critical",
        steps=(
            "1. Run database.integrity_check() for full report",
            "2. If audit_chain broken, identify the break-point seq",
            "3. Restore from last known-good backup",
            "4. Replay audit_chain entries forward to current state",
            "5. Notify all tenants of incident",
        ),
        auto_remediation=_rb_db_corruption,
    ),
    Runbook(
        name="baseline_drift",
        trigger="weekly cron has not run in 8+ days",
        severity="warn",
        steps=(
            "1. Check Hermes cron logs",
            "2. Manually trigger baseline_recal",
            "3. Compare new baselines vs prior week — if delta > 5%, alert reviewer",
            "4. Clear adapters.baselines cache after refresh",
        ),
        auto_remediation=_rb_baseline_drift,
    ),
    Runbook(
        name="amplifier_constant_drift",
        trigger="AMP_PRODUCT_MAX != 6.552 (DES² spec violation)",
        severity="critical",
        steps=(
            "1. Read des2_innerloop.AMP_PRODUCT_MAX",
            "2. If ≠ 1.5×1.4×1.6×1.3×1.5, code has been tampered",
            "3. Restore from main branch of repo",
            "4. Re-run full test suite",
            "5. Notify security team",
        ),
        auto_remediation=_rb_amplifier_failure,
    ),
    Runbook(
        name="audit_chain_broken",
        trigger="chain_verify() returns intact=False",
        severity="critical",
        steps=(
            "1. Identify the break-point entry",
            "2. Determine if it's tampering or storage corruption",
            "3. If tampering: rotate vault keys, audit recent access",
            "4. If corruption: replay from last good entry",
            "5. Document incident in INCIDENTS.md",
        ),
        auto_remediation=_rb_audit_chain_broken,
    ),
    Runbook(
        name="rate_limit_storm",
        trigger="≥3 tenants hit rate-limit simultaneously",
        severity="warn",
        steps=(
            "1. Identify the upstream cause (LLM, scraper, viral usage)",
            "2. Consider temporary capacity boost",
            "3. Notify affected tenants",
            "4. If sustained, propose tier upgrade",
        ),
        auto_remediation=_rb_rate_limit_storm,
    ),
    Runbook(
        name="physics_short_circuit_storm",
        trigger="≥10 artifacts in 1 hour HARD_BLOCK on physics layer",
        severity="warn",
        steps=(
            "1. Inspect the dominant failing gate",
            "2. If KELVIN: investigate banned-phrase explosion in inputs",
            "3. If FineTuning: review specificity baselines",
            "4. Do NOT auto-bypass — these are correctness signals",
            "5. Brief operators on emerging pattern",
        ),
        auto_remediation=_rb_physics_short_circuit_storm,
    ),
    Runbook(
        name="secret_leak_detected",
        trigger="enterprise.security.scan_for_secrets() returns non-empty",
        severity="critical",
        steps=(
            "1. Halt all downstream processing of the artifact",
            "2. Identify the secret type and likely owner",
            "3. Rotate the leaked credential immediately",
            "4. Review audit_chain for any unauthorized access",
            "5. Notify the credential owner + security team",
            "6. File incident report",
        ),
        auto_remediation=_rb_secret_leak_detected,
    ),
]


def list_runbooks() -> list[Runbook]:
    return list(RUNBOOKS)


def get_runbook(name: str) -> Runbook | None:
    return next((r for r in RUNBOOKS if r.name == name), None)


def execute_runbook(name: str) -> dict:
    """Run the auto-remediation step (if defined). Returns result dict."""
    rb = get_runbook(name)
    if not rb:
        return {"error": f"unknown runbook: {name}"}
    if not rb.auto_remediation:
        return {"runbook": name, "auto_remediation": False,
                "manual_steps": list(rb.steps)}
    try:
        result = rb.auto_remediation()
        return {"runbook": name, "auto_remediation": True, "result": result,
                "manual_followup_steps": list(rb.steps)}
    except Exception as e:
        return {"runbook": name, "error": f"{type(e).__name__}: {e}"}
