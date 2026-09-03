"""DOCTRINE.md §6 + §9 — weekly cron hook.

Fires weekly. Recalibrates:
  1. Generic baselines  — refresh the 10 baseline types × 40 engines = 400 corpora
  2. Brier deltas       — compare predicted σ to realized σ over the past week
  3. Engine weights     — adjust based on Brier MAE per engine

Hermes ABI:
    weekly_recal_cron() -> dict
        # returns: {"recalibrated_engines": int, "brier_mae": float, ...}
"""
from __future__ import annotations
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent

from rig_lattice.deviator.pipeline.audit import audit_log
from rig_lattice.core.registry import ENGINE_REGISTRY
from rig_lattice._paths import AUDITS_DIR

BRIER_LOG = AUDITS_DIR / "brier_history.jsonl"
BASELINE_DIR = ROOT / "baselines"
WEIGHTS_PATH = AUDITS_DIR / "engine_weights.json"


def _read_brier_history(window_days: int = 7) -> list[dict]:
    """Return Brier entries from the last `window_days`."""
    if not BRIER_LOG.exists():
        return []
    cutoff = time.time() - window_days * 86400
    entries: list[dict] = []
    for line in BRIER_LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
            # Entries with a timestamp older than cutoff get skipped
            ts = d.get("timestamp", 0)
            if isinstance(ts, str):
                ts = time.mktime(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S"))
            if ts >= cutoff:
                entries.append(d)
        except Exception:
            continue
    return entries


def _compute_brier_mae() -> tuple[float, int]:
    """Mean absolute error of predicted_rig_l vs realized_rig_l."""
    entries = _read_brier_history()
    deltas = [abs(e["predicted_rig_l"] - e["realized_rig_l"])
              for e in entries
              if "predicted_rig_l" in e and "realized_rig_l" in e]
    if not deltas:
        return 0.0, 0
    return round(statistics.mean(deltas), 3), len(deltas)


def _recalibrate_baselines() -> int:
    """Refresh generic baselines per DOCTRINE.md §9.

    Stub: writes a marker file. Real implementation scrapes 10 baseline
    types × 40 engines via LiteLLM + web scrapers.
    """
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    marker = BASELINE_DIR / "_last_recal.txt"
    marker.write_text(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    # In Day 3 we'll wire the actual LiteLLM scraping per engine
    return len(ENGINE_REGISTRY)


def _update_engine_weights(brier_entries: list[dict]) -> dict[str, float]:
    """Adjust per-engine weights based on Brier deltas.

    Engines with higher MAE on their σ predictions get down-weighted.
    """
    per_engine: dict[str, list[float]] = {}
    for e in brier_entries:
        slug = e.get("engine_slug")
        if slug and "predicted_sigma" in e and "realized_sigma" in e:
            per_engine.setdefault(slug, []).append(
                abs(e["predicted_sigma"] - e["realized_sigma"])
            )

    weights: dict[str, float] = {}
    for slug, deltas in per_engine.items():
        mae = statistics.mean(deltas)
        # Weight = 1.0 baseline, reduced if MAE high. Floor at 0.3.
        weights[slug] = round(max(0.3, 1.0 - mae * 0.1), 3)

    if weights:
        WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        WEIGHTS_PATH.write_text(json.dumps(weights, indent=2))

    return weights


def weekly_recal_cron() -> dict:
    """Run the weekly recalibration cycle."""
    start = time.time()
    brier_entries = _read_brier_history(window_days=7)
    mae, n = _compute_brier_mae()
    weights = _update_engine_weights(brier_entries)
    recalibrated = _recalibrate_baselines()

    result = {
        "recalibrated_engines": recalibrated,
        "brier_mae": mae,
        "brier_entries": n,
        "engine_weights_updated": len(weights),
        "elapsed_s": round(time.time() - start, 2),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    audit_log("cron", "weekly-recal", "system",
                {"hook": "weekly_recal_cron", "result": result},
                tier="internal_artifact", actor="hermes.cron")

    return result


if __name__ == "__main__":
    import json as _j
    print(_j.dumps(weekly_recal_cron(), indent=2))
