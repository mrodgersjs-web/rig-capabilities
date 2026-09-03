"""Enterprise Observability — OpenTelemetry-style metrics, Prometheus exposition,
structured JSON logging, health checks.

Per the LinkedIn Studio template Observability subsystem.
"""
from __future__ import annotations
import json
import time
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from rig_lattice._paths import AUDITS_DIR

ROOT = Path(__file__).parent.parent
LOG_PATH = AUDITS_DIR / "observability.jsonl"


# ── Structured JSON logger ────────────────────────────────────────────────
_LOG_LOCK = threading.Lock()


def log_event(event: str, level: str = "info", **fields: Any) -> dict:
    """Emit a structured JSON log line. Append-only."""
    record = {
        "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "event": event,
        **fields,
    }
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _LOG_LOCK:
        with LOG_PATH.open("a") as f:
            f.write(json.dumps(record, default=str) + "\n")
    return record


# ── In-process metric counters / gauges / histograms ──────────────────────
_METRICS_LOCK = threading.Lock()
_COUNTERS: dict[str, float] = defaultdict(float)
_GAUGES: dict[str, float] = {}
_HISTOGRAMS: dict[str, list[float]] = defaultdict(list)


def counter_inc(name: str, value: float = 1.0, **labels: str) -> None:
    key = _label_key(name, labels)
    with _METRICS_LOCK:
        _COUNTERS[key] += value


def gauge_set(name: str, value: float, **labels: str) -> None:
    key = _label_key(name, labels)
    with _METRICS_LOCK:
        _GAUGES[key] = value


def histogram_observe(name: str, value: float, **labels: str) -> None:
    key = _label_key(name, labels)
    with _METRICS_LOCK:
        # Keep last 1024 samples to bound memory
        h = _HISTOGRAMS[key]
        h.append(value)
        if len(h) > 1024:
            h.pop(0)


def _label_key(name: str, labels: dict[str, str]) -> str:
    if not labels:
        return name
    parts = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return f"{name}{{{parts}}}"


def metric_snapshot() -> dict:
    """Return a snapshot of all metrics for /metrics endpoint use."""
    with _METRICS_LOCK:
        return {
            "counters": dict(_COUNTERS),
            "gauges": dict(_GAUGES),
            "histograms": {k: _summarize(v) for k, v in _HISTOGRAMS.items()},
        }


def _summarize(samples: list[float]) -> dict:
    if not samples:
        return {"count": 0, "sum": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0}
    sorted_s = sorted(samples)
    n = len(sorted_s)
    return {
        "count": n,
        "sum": sum(sorted_s),
        "min": sorted_s[0],
        "max": sorted_s[-1],
        "p50": sorted_s[n // 2],
        "p95": sorted_s[min(int(n * 0.95), n - 1)],
        "p99": sorted_s[min(int(n * 0.99), n - 1)],
    }


def prometheus_exposition() -> str:
    """Render metrics in Prometheus text exposition format."""
    lines = []
    snap = metric_snapshot()
    for key, val in snap["counters"].items():
        lines.append(f"# TYPE {key.split('{')[0]} counter")
        lines.append(f"{key} {val}")
    for key, val in snap["gauges"].items():
        lines.append(f"# TYPE {key.split('{')[0]} gauge")
        lines.append(f"{key} {val}")
    for key, summary in snap["histograms"].items():
        base = key.split("{")[0]
        lines.append(f"# TYPE {base} histogram")
        for stat, val in summary.items():
            lines.append(f"{base}_{stat} {val}")
    return "\n".join(lines) + "\n"


# ── Health checks (9 per LinkedIn Studio template) ────────────────────────
@dataclass
class HealthCheck:
    name: str
    ok: bool
    detail: str = ""
    elapsed_ms: float = 0.0


def run_health_checks() -> list[HealthCheck]:
    """Run all 9 enterprise health checks and return results."""
    checks = []

    # 1. Criteria packs load
    t0 = time.time()
    try:
        from rig_lattice.deviator.auditor import _load_yaml, CRITERIA_DIR
        packs = list(CRITERIA_DIR.glob("*.yaml"))
        ok = len(packs) >= 40
        checks.append(HealthCheck("criteria_packs_load", ok,
                                    f"found {len(packs)} packs (need ≥40)",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("criteria_packs_load", False, str(e),
                                    (time.time() - t0) * 1000))

    # 2. 40-engine registry intact
    t0 = time.time()
    try:
        from rig_lattice.core.registry import ENGINE_REGISTRY
        ok = len(ENGINE_REGISTRY) == 40
        checks.append(HealthCheck("engine_registry_intact", ok,
                                    f"{len(ENGINE_REGISTRY)}/40 engines",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("engine_registry_intact", False, str(e),
                                    (time.time() - t0) * 1000))

    # 3. Math primitives importable
    t0 = time.time()
    try:
        from rig_lattice.core import robust_mad_z, bdf, escalation_cost
        _ = robust_mad_z(10, [1, 2, 3])
        checks.append(HealthCheck("math_primitives", True, "all importable",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("math_primitives", False, str(e),
                                    (time.time() - t0) * 1000))

    # 4. Audit log writable
    t0 = time.time()
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        test_file = LOG_PATH.parent / ".health_test"
        test_file.write_text("ok")
        test_file.unlink()
        checks.append(HealthCheck("audit_log_writable", True, "",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("audit_log_writable", False, str(e),
                                    (time.time() - t0) * 1000))

    # 5. DES² inner-loop available
    t0 = time.time()
    try:
        from rig_lattice.deviator.des2_innerloop import AMP_PRODUCT_MAX
        ok = abs(AMP_PRODUCT_MAX - 6.552) < 0.001
        checks.append(HealthCheck("des2_amplifier_intact", ok,
                                    f"AMP_PRODUCT_MAX={AMP_PRODUCT_MAX:.4f}",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("des2_amplifier_intact", False, str(e),
                                    (time.time() - t0) * 1000))

    # 6. All 3 engine layers loadable
    t0 = time.time()
    try:
        from rig_lattice.engines import load_all_engines
        engines = load_all_engines()
        ok = len(engines) == 40
        checks.append(HealthCheck("all_engines_loadable", ok,
                                    f"{len(engines)}/40 loaded",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("all_engines_loadable", False, str(e),
                                    (time.time() - t0) * 1000))

    # 7. Brier log accessible
    t0 = time.time()
    try:
        from rig_lattice.deviator.des2_innerloop import BRIER_LOG
        BRIER_LOG.parent.mkdir(parents=True, exist_ok=True)
        checks.append(HealthCheck("brier_log_accessible", True,
                                    f"path={BRIER_LOG}",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("brier_log_accessible", False, str(e),
                                    (time.time() - t0) * 1000))

    # 8. Baselines populated (40 engines × 10 samples)
    t0 = time.time()
    try:
        from rig_lattice.adapters.baselines import BASELINE_TYPES
        ok = len(BASELINE_TYPES) == 10
        checks.append(HealthCheck("baselines_populated", ok,
                                    f"{len(BASELINE_TYPES)} baseline types (need 10)",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("baselines_populated", False, str(e),
                                    (time.time() - t0) * 1000))

    # 9. IQRSQPI lattice resolves
    t0 = time.time()
    try:
        from rig_lattice.enterprise.iqrsqpi import all_cells, TOTAL_CELLS
        ok = len(all_cells()) == TOTAL_CELLS == 588
        checks.append(HealthCheck("iqrsqpi_lattice_resolves", ok,
                                    f"{TOTAL_CELLS}=588 cells (7×3×4×7)",
                                    (time.time() - t0) * 1000))
    except Exception as e:
        checks.append(HealthCheck("iqrsqpi_lattice_resolves", False, str(e),
                                    (time.time() - t0) * 1000))

    return checks


def health_summary() -> dict:
    checks = run_health_checks()
    return {
        "ok": all(c.ok for c in checks),
        "total": len(checks),
        "passed": sum(1 for c in checks if c.ok),
        "failed": [c.name for c in checks if not c.ok],
        "checks": [{"name": c.name, "ok": c.ok, "detail": c.detail,
                     "elapsed_ms": round(c.elapsed_ms, 2)} for c in checks],
    }
