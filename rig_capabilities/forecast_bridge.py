"""Prediction studio bridge — connect ultra_forecast.register_payload to Memory OS.

Usage:
    from rig_capabilities.forecast_bridge import register_and_settle
    result = register_and_settle(record)

The `record` must carry: horizon, proposition, trigger_event, target_event,
evidence_refs, probability, cohort_id (optional), run (optional).

This module calls `register_payload()` to build the Memory OS argument set,
then invokes `memory_issue_forecast` through the local CLI bridge. It does NOT
call Memory OS MCP directly (that's the caller's job if they want MCP).

The settle cycle: register -> resolve -> brier -> weights is handled by
Memory OS's own forecast_settle / forecast_report operations. This bridge
only handles the register step.
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Dict, Optional

from .ultra_forecast import register_payload, UltraForecastError


def register_and_settle(
    rec: Dict[str, Any],
    *,
    cli: str = "/Users/rig128gb/bin/rig-memory-os",
    timeout: int = 30,
) -> Dict[str, Any]:
    """Register a forecast with Memory OS and return the result.

    Raises UltraForecastError on missing fields (from register_payload).
    Returns Memory OS response dict on success.
    """
    payload = register_payload(rec)
    cmd = [cli, "call", "memory.issue_forecast", "--input", json.dumps(payload)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return {"ok": False, "error": "rig-memory-os CLI not found", "cli": cli}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "timeout": timeout}
    if proc.returncode != 0:
        return {"ok": False, "returncode": proc.returncode, "stderr": proc.stderr[:500]}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": True, "raw": proc.stdout[:500]}


def register_batch(
    records: list[Dict[str, Any]], **kwargs
) -> list[Dict[str, Any]]:
    """Register multiple forecasts sequentially."""
    return [register_and_settle(r, **kwargs) for r in records]


if __name__ == "__main__":
    # Smoke test: register a dummy forecast
    test_rec = {
        "horizon": "7d",
        "proposition": "W04 JEV lane completes all9 contract items by 2026-09-28",
        "trigger_event": "r04 + r05 evidenced",
        "target_event": "r06-r08 evidenced + GLM verified",
        "evidence_refs": ["w04-r04-receipt.json", "w04-r05-receipt.json"],
        "probability": 0.72,
        "cohort_id": "w04-jev-lane",
        "run": "2026-09-21-eve",
    }
    try:
        result = register_and_settle(test_rec)
        print(json.dumps(result, indent=2))
    except UltraForecastError as e:
        print(f"EXPECTED (no live Memory OS): {e}", file=sys.stderr)
        # Still prove register_payload works
        from .ultra_forecast import register_payload
        p = register_payload(test_rec)
        print(json.dumps(p, indent=2))
        print("register_payload OK (Memory OS CLI not exercised)")
