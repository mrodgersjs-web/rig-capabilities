#!/usr/bin/env python3
"""Read-only D85 build/estate status feed. Emits one JSON object per line."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "contract": ROOT / "D85_AGENT_PROCESS_CONTRACT.json",
    "delivery": ROOT / "v2" / "DELIVERY_STATUS.json",
    "launchagents": ROOT / "estate" / "launchagents-live-2026-09-09.json",
    "hermes": ROOT / "estate" / "hermes-jobs-live-2026-09-09.json",
    "surfaces": ROOT / "estate" / "agent-surface-bindings-live-2026-09-09.json",
    "collaboration": ROOT / "review" / "collaboration-role-verification.json",
    "job_preflight": ROOT / "estate" / "job-workflow-preflight-2026-09-09.json",
    "coverage": ROOT / "estate" / "implemented-missing-coverage-2026-09-09.json",
    "estate_review": ROOT / "v3" / "automation-estate-review.content.json",
    "worksheet": ROOT / "estate" / "decision-worksheet-latest.csv",
}


def _load(name: str, path: Path, errors: list[dict[str, str]]) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
        if not isinstance(value, dict):
            raise ValueError("root must be an object")
        return value
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        errors.append({"source": name, "path": str(path), "error": f"{type(exc).__name__}: {exc}"})
        return {}


def _hash(path: Path) -> str | None:
    try:
        return "sha256:" + hashlib.new("sha256", path.read_bytes()).hexdigest()
    except OSError:
        return None


def _read_worksheet(path: Path, errors: list[dict[str, str]]) -> dict[str, tuple[str, str]]:
    """CSV join map {id: (verdict, primary_action)}; an unreadable worksheet is
    a named absence (worksheet_unreadable), never dropped rows downstream."""
    if not path.is_file():
        errors.append({"source": "worksheet", "path": str(path), "error": "worksheet_unreadable: missing"})
        return {}
    try:
        with path.open(newline="") as handle:
            return {
                row["id"]: (row.get("verdict", ""), row.get("primary_action", ""))
                for row in csv.DictReader(handle)
                if row.get("id")
            }
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        errors.append({"source": "worksheet", "path": str(path), "error": f"worksheet_unreadable: {type(exc).__name__}: {exc}"})
        return {}


def snapshot() -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    data = {name: _load(name, path, errors) for name, path in SOURCES.items() if name != "worksheet"}
    contract = data["contract"]
    delivery = data["delivery"]
    launch = data["launchagents"]
    hermes = data["hermes"]
    surfaces = data["surfaces"]
    collaboration = data["collaboration"]
    preflight = data["job_preflight"]
    coverage = data["coverage"]
    estate = data["estate_review"]
    gaps: list[str] = []
    if delivery.get("overall") != "PASS":
        gaps.append("Archify authoritative suite is BLOCK")
    if (surfaces.get("summary") or {}).get("wired_count") != 4:
        gaps.append("D85 is not wired on all four agent surfaces")
    if not (launch.get("summary") or {}).get("record_inventory_complete"):
        gaps.append("LaunchAgent record inventory is incomplete")
    if not launch.get("inventory_complete"):
        gaps.append("LaunchAgent path inventory is incomplete")
    if not (delivery.get("implementation_status") or {}).get("global_d85_wiring") == "WIRED":
        gaps.append("D85 compiler and global hook enforcement are not implemented")
    if collaboration.get("verdict") != "PASS":
        gaps.append("Required collaboration roles are incomplete")
    if preflight.get("operational_completion_verdict") != "PASS":
        gaps.append("Job workflow is not operationally proven end to end")
    if (coverage.get("operation_inventory_slice") or {}).get("status") != "IMPLEMENTED":
        gaps.append("Operation inventory is a Python-only prerequisite; classification and D85 scoring remain blocked")
    if not (estate.get("counts") or {}).get("live"):
        gaps.append("Automation estate review packet has no live job rows")
    return {
        "schema_version": "rig.lattice.status-feed.v1",
        "observed_at": datetime.now(timezone(timedelta(0))).isoformat().replace("+00:00", "Z"),
        "status": "DEGRADED" if errors else ("BLOCK" if gaps else "PASS"),
        "startup": {
            "gate": (contract.get("current") or {}).get("startup_hard_stop"),
            "packet_id": (contract.get("current") or {}).get("startup_packet_id"),
            "nonblocking_degradation": (contract.get("current") or {}).get("startup_nonblocking_degradation"),
        },
        "archify": {
            "overall": delivery.get("overall"),
            "delivered": [row.get("name") for row in delivery.get("delivered", [])],
            "blocked": [row.get("name") for row in delivery.get("blocked", [])],
        },
        "agent_surfaces": surfaces.get("summary"),
        "launchagents": launch.get("summary"),
        "hermes_jobs": hermes.get("summary"),
        "collaboration": {
            "verdict": collaboration.get("verdict"),
            "passing_required_roles": collaboration.get("passing_required_roles"),
            "required_role_count": collaboration.get("required_role_count"),
        },
        "job_workflow": {
            "preflight": preflight.get("status"),
            "operational_completion": preflight.get("operational_completion_verdict"),
            "browser_execution_tested": preflight.get("browser_execution_tested"),
            "model_inference_tested": preflight.get("model_inference_tested"),
        },
        "d85_coverage": {
            "checkpoints": coverage.get("d85_checkpoint_summary"),
            "operation_inventory": coverage.get("operation_inventory_slice"),
        },
        "automation_estate": {
            "captured_at": estate.get("captured_at"),
            "counts": estate.get("counts"),
            "inventory_complete": estate.get("inventory_complete"),
            "kestra_mcp_parity": ((estate.get("mcp") or {}).get("kestra_parity") or {}).get("status"),
            "authority_errors": {name: a.get("error") for name, a in (estate.get("authorities") or {}).items() if a.get("error")},
        },
        "estate_jobs": _estate_jobs(estate, _read_worksheet(SOURCES["worksheet"], errors)),
        "gaps": gaps,
        "source_hashes": {name: _hash(path) for name, path in SOURCES.items()},
        "errors": errors,
    }


def _estate_jobs(estate: dict[str, Any], worksheet: dict[str, tuple[str, str]]) -> list[dict[str, Any]]:
    """Per-job operating-state view: packet row fields (P4.5/P4.6) joined with
    worksheet verdicts. Unknown cells always name their cause literal."""
    out: list[dict[str, Any]] = []
    for job in list(estate.get("jobs") or []) + list(estate.get("proposals") or []):
        verdict, primary = worksheet.get(job.get("id") or "", ("unknown", "worksheet_row_absent"))
        out.append(
            {
                "id": job.get("id"),
                "operating_state": job.get("operating_state") or "unknown:field_absent",
                "blocking_conditions": job.get("blocking_conditions") or [],
                "verdict": verdict or "unknown",
                "primary_action": primary or "worksheet_row_absent",
            }
        )
    return out


def self_check(value: dict[str, Any]) -> None:
    assert value["schema_version"] == "rig.lattice.status-feed.v1"
    assert value["startup"]["gate"] in {"PASS", "FAIL", "BLOCK", None}
    assert isinstance(value["gaps"], list)
    assert (value.get("automation_estate") or {}).get("counts", {}).get("live", 0) > 0, "estate summary missing or empty"
    assert all(
        j["operating_state"] in {"proposed", "retired", "blocked", "running", "enabled", "last_success", "ready"}
        or j["operating_state"].startswith("unknown:")
        for j in value["estate_jobs"]
    ), "operating_state outside the closed set"
    assert all(j["verdict"] in {"pass", "fail", "unknown"} for j in value["estate_jobs"]), "verdict outside the closed set"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="emit a fresh JSON line repeatedly")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval must be positive")
    if args.self_check:
        self_check(snapshot())
        print("STATUS FEED SELF-CHECK PASS")
        return 0
    while True:
        print(json.dumps(snapshot(), sort_keys=True), flush=True)
        if not args.watch:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
