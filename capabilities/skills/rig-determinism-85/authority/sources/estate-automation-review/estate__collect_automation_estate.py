#!/usr/bin/env python3
"""Deterministic automation-estate collector.

Inventories every scheduler authority (launchd, Hermes, Orca, Temporal, Kestra,
Prefect), applies estate/job-standard.v1.json (20 keep/migrate/kill criteria +
canonical framework precedence), and emits
v3/automation-estate-review.content.json plus the embedded packet inside
v3/automation-estate-review.html. Stdlib-only, read-only against every
authority except `docker exec kestra-postgres psql` (SELECT-only statements).

Missing evidence stays null with status UNKNOWN; unknown is never zero.
"""
from __future__ import annotations

import argparse
import importlib.util
import hashlib
import json
import os
import plistlib
import re
import sqlite3
import base64
import shutil
import subprocess
import sys
from urllib.error import URLError
from urllib.request import Request as urllib_request_Request, urlopen
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STANDARD_PATH = ROOT / "estate" / "job-standard.v1.json"
sys.path.insert(0, str(ROOT))  # estate.* source imports resolve from any cwd
from estate.lattice_wire_adapter import route_intent_fn  # noqa: E402
from estate.normalized_centerytics import deterministic_step  # noqa: E402


def _err(text: str) -> None:
    """stderr write helper: attribute call site, never a stream handed as data."""
    sys.stderr.write(text + "\n")

HOME = Path.home()
LAUNCH_AGENTS_DIR = HOME / "Library" / "LaunchAgents"
HERMES_JOBS = HOME / ".hermes" / "cron" / "jobs.json"
PREFECT_API = "http://127.0.0.1:4200/api/deployments"
KESTRA_CONTAINER = "kestra-postgres"
KESTRA_NAMESPACE = "main.rig"
DISPOSITIONS = {"KEEP", "MIGRATE", "RETIRE", "INVESTIGATE", "PROPOSED"}
ANSWER_STATUSES = {"ANSWERED", "UNKNOWN"}
RECENCY_DAYS = 7

LATTICE = {
    "coordinate": "L3-D1-A2",
    "bms": {
        "confidence": 0.68,
        "mode": "A2",
        "budget_usd": 0,
        "failure_cost": 0.35,
        "reversibility": 0.5,
        "mechanism_clarity": 0.9,
        "level": "L3",
        "note": "Effects-rubric recompute (00b): append-only evidence writes are irreversible-by-copy, so reversibility stays 0.5 and the mode is A2 — no A1 claim, no D85 certification, no promotion; collection/scoring remain deterministic and unresolved evidence is UNKNOWN, never model-filled.",
    },
}

CHECKLIST_PATH = ROOT / "estate" / "job-checklist.v1.json"
ESTATE_SOURCES = {"launchd", "hermes", "orca", "temporal", "kestra", "prefect", "proposal"}
DECIDED = {"KEEP", "MIGRATE", "RETIRE", "PROPOSED"}


def lattice_route(job: dict[str, Any]) -> dict[str, Any]:
    """Deterministic keyword routing (rig_lattice, no model) at neutral BMS priors."""
    if route_intent_fn() is None:
        return {"coordinate": None, "mode": None, "error": "rig_lattice package not importable"}
    parts = (job.get("name"), job.get("source"), job.get("trigger_kind"),
             (job.get("command") or job.get("body_path") or "")[:160])
    text = " ".join(str(v) for v in parts if v)
    try:
        r = route_intent_fn()(text, domain=str(job.get("source") or ""), failure_cost=0.5, reversibility=0.5, mechanism_clarity=0.5)
    except Exception as exc:
        return {"coordinate": None, "mode": None, "error": f"{type(exc).__name__}: {exc}"}
    return {"coordinate": r.primary_coordinate, "cell": r.cell_id, "mode": r.mode, "level": r.level,
            "diamond": r.diamond, "bms_confidence": r.bms_score, "budget_usd": r.budget_usd,
            "approval_required": r.approval_required, "archetype": r.archetype, "rationale": r.rationale}


def _goal_has_mechanism(job: dict[str, Any]) -> bool:
    gi = job.get("goal_impact") or {}
    return any((v.get("mechanism") if isinstance(v, dict) else v) for v in gi.values())


def _checklist_pred(item: dict[str, Any], job: dict[str, Any], threshold: float) -> str:
    mode = item["mode"]
    field = item.get("field")
    if mode == "never_collected":
        return "UNKNOWN"
    if mode == "non_null":
        return "PASS" if job.get(field) else "FAIL"
    if mode == "observed_execution":
        if job.get("source") == "proposal":
            return "UNKNOWN"
        if job.get("source") not in item.get("capable", []):
            return "UNKNOWN"
        return "PASS" if job.get(field) else "FAIL"
    if mode == "authority":
        return "PASS" if job.get("source") in ESTATE_SOURCES else "FAIL"
    if mode == "lifecycle":
        if job.get("source") == "launchd":
            ok = all(isinstance(job.get(k), bool) for k in ("installed", "enabled", "loaded"))
        else:
            ok = job.get("lifecycle") is not None
        return "PASS" if ok else "FAIL"
    if mode == "target":
        return "PASS" if any(job.get(k) for k in ("command", "body_path", "model", "workdir")) else "FAIL"
    if mode == "consumer":
        return "PASS" if (job.get("consumer") or _goal_has_mechanism(job)) else "FAIL"
    if mode == "goal_mechanism":
        return "PASS" if _goal_has_mechanism(job) else "FAIL"
    if mode == "done_test":
        if job.get("source") == "proposal":
            return "PASS" if job.get("done_test") else "FAIL"
        return "UNKNOWN" if "done_test" not in job else ("PASS" if job.get("done_test") else "FAIL")
    if mode == "field_present":
        return "PASS" if field in job else "FAIL"
    if mode == "lattice_coordinate":
        return "PASS" if (job.get("lattice") or {}).get("coordinate") else "FAIL"
    if mode == "lattice_mode":
        return "PASS" if (job.get("lattice") or {}).get("mode") else "FAIL"
    if mode == "coverage_ge":
        if "score" not in job:
            return "UNKNOWN"
        return "PASS" if job["score"]["coverage"] >= threshold else "FAIL"
    if mode == "disposition_decided":
        return "PASS" if job.get("disposition") in DECIDED else "FAIL"
    if mode == "attached_verdict":
        if job.get("source") == "proposal" and item.get("contract_field") == "done_test":
            return "PASS" if job.get("done_test") else "FAIL"
        attached = job.get(field)
        if not isinstance(attached, dict):
            return "UNKNOWN"
        return attached.get("verdict", "UNKNOWN")
    raise SystemExit(f"unknown checklist mode: {item['mode']}")


def checklist_job(job: dict[str, Any], spec: dict[str, Any]) -> dict[str, str]:
    threshold = spec.get("coverage_threshold", 0.85)
    return {item["id"]: _checklist_pred(item, job, threshold) for item in spec["items"]}


def load_checklist_spec() -> dict[str, Any]:
    spec = json.loads(CHECKLIST_PATH.read_text())
    if spec.get("schema") != "rig.automation-job-checklist.v2":
        raise SystemExit("unknown job-checklist schema")
    return spec


def enrich_rows(rows: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    totals = {"PASS": 0, "FAIL": 0, "UNKNOWN": 0}
    per_platform: dict[str, dict[str, int]] = {}
    all_pass = lattice_assigned = 0
    bucket = {"PASS": "observed", "FAIL": "capable_but_missing", "UNKNOWN": "untestable"}
    exec_counts = {"c08": {"observed": 0, "capable_but_missing": 0, "untestable": 0},
                   "c09": {"observed": 0, "capable_but_missing": 0, "untestable": 0}}
    for job in rows:
        job["lattice"] = lattice_route(job)
        lattice_assigned += bool(job["lattice"].get("coordinate"))
        ck = job["checklist"] = checklist_job(job, spec)
        counts = {s: sum(1 for v in ck.values() if v == s) for s in ("PASS", "FAIL", "UNKNOWN")}
        all_pass += counts["PASS"] == len(spec["items"])
        for st in totals:
            totals[st] += counts[st]
            per_platform.setdefault(str(job.get("source")), {"PASS": 0, "FAIL": 0, "UNKNOWN": 0})[st] += counts[st]
        for item_id, key in (("C08", "c08"), ("C09", "c09")):
            exec_counts[key][bucket[ck.get(item_id, "UNKNOWN")]] += 1
    cells = sum(totals.values())
    return {
        "spec": {"path": str(CHECKLIST_PATH), "sha256": sha256_bytes(CHECKLIST_PATH.read_bytes()),
                 "version": spec["version"], "items_count": len(spec["items"]), "item_ids": [i["id"] for i in spec["items"]], "items": spec["items"]},
        "rows": len(rows), "cells": cells, "totals": dict(sorted(totals.items())),
        "pass_rate": round(totals["PASS"] / cells, 4) if cells else 0.0,
        "rows_all_pass": all_pass, "lattice_assigned": lattice_assigned,
        "execution_observed": exec_counts,
        "validation_semantics": spec.get("validation_semantics"),
        "d85_separation": "pass_rate is checklist validation coverage, NOT D85 admission (rig-determinism-85 score four ratios >= 0.85 + bound checklist artifact); d85_classification on rows is a body-class annotation only — D85 NOT_EVALUATED for estate rows.",
        "by_platform": {k: dict(sorted(v.items())) for k, v in sorted(per_platform.items())},
        "coverage_threshold": spec.get("coverage_threshold", 0.85),
        "intake_rule": spec["intake_rule"],
    }


def now_iso() -> str:
    return datetime.now(timezone(timedelta(0))).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.new("sha256", data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def run_cli(argv: list[str], timeout: int = 45) -> tuple[int, str, str]:
    exe = shutil.which(argv[0]) or argv[0]
    try:
        proc = subprocess.run([exe, *argv[1:]], capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", f"{type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# Authority collectors. Each returns (rows, meta) where every row is a raw
# per-source observation; normalization happens in normalize_* below.
# ---------------------------------------------------------------------------

def collect_launchd() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meta: dict[str, Any] = {"captured_at": now_iso(), "error": None}
    loaded: dict[str, dict[str, Any]] = {}
    rc, out, err = run_cli(["launchctl", "list"], timeout=30)
    loaded_known = False
    if rc == 0:
        try:
            lines = out.splitlines()
            if not lines or lines[0].split() != ["PID", "Status", "Label"]:
                raise ValueError("unexpected listing header")
            for line in lines[1:]:
                if not line.strip():
                    continue
                pid, status, label = line.split(None, 2)
                loaded[label] = {"pid": None if pid == "-" else int(pid),
                                 "last_exit_status": int(status)}
            loaded_known = True
        except ValueError as exc:
            loaded.clear()
            meta["error"] = f"launchctl list unparseable: {exc}"
    else:
        meta["error"] = f"launchctl list failed rc={rc}: {err.strip()[:200]}"
    disabled: dict[str, bool] = {}
    rc, out, err = run_cli(["launchctl", "print-disabled", f"gui/{os.getuid()}"], timeout=30)
    disabled_known = rc == 0 and "disabled services = {" in out and out.rstrip().endswith("}")
    if disabled_known:
        for line in out.splitlines():
            if "=>" not in line:
                continue
            match = re.fullmatch(r'\s*"([^"]+)"\s*=>\s*(true|false|enabled|disabled)\s*', line)
            if not match:
                disabled_known = False
                break
            disabled[match[1]] = match[2] in {"true", "disabled"}
    if not disabled_known:
        meta["disabled_error"] = f"launchctl print-disabled failed or unparseable rc={rc}: {err.strip()[:200]}"
        meta["error"] = "; ".join(filter(None, [meta["error"], meta["disabled_error"]]))
    meta["launchctl_entries"] = len(loaded)
    # P4.4: `launchctl lastexit` does not exist on this macOS (P0 shard 03
    # recorded rc=1 usage-dumps). One probe decides; unavailable means NO
    # per-label fan-out and NO fabricated codes — the honestly-collected
    # launchctl-list Status column (last_exit_status) is what rows keep.
    LAUNCHD_EXIT_FLAGS = {62: "unit-missed", 183: "restarting"}  # map unverified at seal time
    sample_label = next(iter(loaded), "")
    probe_rc, probe_out, probe_err = run_cli(
        ["launchctl", "lastexit", f"gui/{os.getuid()}/{sample_label}"], timeout=10
    )
    if probe_rc == 0 and "Usage: launchctl" not in probe_out + probe_err:
        meta["lastexit"] = {"state": "available", "sample_rc": probe_rc}
    else:
        meta["lastexit"] = {
            "state": "launchd-lastexit-unavailable",
            "cause": f"rc={probe_rc}: {(probe_out or probe_err).strip()[:120]}",
        }
    rows: list[dict[str, Any]] = []
    parse_errors = 0
    if not LAUNCH_AGENTS_DIR.is_dir():
        meta["error"] = (meta["error"] or "") + f" missing dir {LAUNCH_AGENTS_DIR}"
        return rows, meta
    for plist_path in sorted(LAUNCH_AGENTS_DIR.glob("*.plist")):
        row: dict[str, Any] = {"plist_path": str(plist_path), "parse_ok": True, "loaded": None, "enabled": None, "pid": None, "last_exit_status": None}
        try:
            plist = plistlib.loads(plist_path.read_bytes())
        except Exception as exc:  # noqa: BLE001 - a malformed plist is a data point, not a crash
            row["parse_ok"] = False
            row["parse_error"] = f"{type(exc).__name__}: {exc}"
            parse_errors += 1
            rows.append(row)
            continue
        label = str(plist.get("Label") or plist_path.stem)
        row["loaded"] = False if loaded_known else None
        row["enabled"] = not disabled.get(label, bool(plist.get("Disabled"))) if disabled_known else None
        row.update(
            {
                "label": label,
                "program": plist.get("Program"),
                "arguments": [str(a) for a in (plist.get("ProgramArguments") or [])],
                "working_dir": plist.get("WorkingDirectory"),
                "run_at_load": bool(plist.get("RunAtLoad")),
                "keep_alive": plist.get("KeepAlive"),
                "start_calendar": plist.get("StartCalendarInterval"),
                "start_interval": plist.get("StartInterval"),
                "watch_paths": plist.get("WatchPaths"),
                "watch_system_files": plist.get("WatchSystemFiles"),
                "sockets": plist.get("Sockets"),
                "network_events": plist.get("NetworkEvents"),
                "start_on_mount": plist.get("StartOnMount"),
                "throttle_interval": plist.get("ThrottleInterval"),
                "env_vars": {str(k): str(v) for k, v in (plist.get("EnvironmentVariables") or {}).items()},
            }
        )
        held = [
            key
            for key in ("watch_paths", "watch_system_files", "sockets", "network_events")
            if row.get(key)
        ]
        if isinstance(row.get("start_interval"), (int, float)) and 0 < float(row["start_interval"]) < 1:
            held.append("sub_second_start_interval")
        row["held_resources"] = held
        hit = loaded.get(label)
        if hit is not None:
            row["loaded"] = True
            row["pid"] = hit["pid"]
            row["last_exit_status"] = hit["last_exit_status"]
            if meta["lastexit"]["state"] == "available":
                code_rc, code_out, _ = run_cli(
                    ["launchctl", "lastexit", f"gui/{os.getuid()}/{label}"], timeout=10
                )
                if code_rc == 0:
                    try:
                        row["last_exit_code"] = int(code_out.strip())
                        row["last_exit_flag"] = LAUNCHD_EXIT_FLAGS.get(row["last_exit_code"])
                    except ValueError:
                        row["last_exit_code"] = None
        rows.append(row)
    meta["plist_count"] = len(rows)
    meta["parse_errors"] = parse_errors
    meta["raw_sha256"] = sha256_text(json.dumps([r.get("label", r["plist_path"]) for r in rows], sort_keys=True))
    return rows, meta


def collect_hermes_executions() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """P4.3 read-only execution evidence per Hermes job. Root store
    ~/.hermes/cron/executions.db plus per-profile */cron/executions.db. Every
    connection is URI mode=ro with PRAGMA query_only=ON (the plan's double
    guard). Missing per-profile ledger => that store's rows carry
    {"state": "no_exec_ledger"} — unknown coverage, never a zero claim."""
    meta: dict[str, Any] = {"captured_at": now_iso(), "error": None, "stores": {}}
    evidence: dict[str, dict[str, Any]] = {}
    stores: list[tuple[str, Path]] = [("", HERMES_JOBS.parent / "executions.db")]
    profiles_root = HERMES_JOBS.parent.parent / "profiles"
    if profiles_root.is_dir():
        stores += sorted(
            (path.parent.parent.name, path)
            for path in profiles_root.glob("*/cron/executions.db")
        )
    for profile, db_path in stores:
        key = profile or "(root)"
        if not db_path.is_file():
            meta["stores"][key] = {"state": "no_exec_ledger", "path": str(db_path)}
            continue
        store_meta: dict[str, Any] = {"state": "ok", "path": str(db_path)}
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.execute("PRAGMA query_only=ON")
            tables = {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('executions','cron_incidents')"
                )
            }
            store_meta["tables"] = sorted(tables)
            if "executions" not in tables:
                store_meta["state"] = "no_exec_ledger"
                conn.close()
                meta["stores"][key] = store_meta
                continue
            job_ids = conn.execute("SELECT DISTINCT job_id FROM executions").fetchall()
            store_meta["executions_count"] = conn.execute("SELECT COUNT(*) FROM executions").fetchone()[0]
            for (job_id,) in job_ids:
                last = conn.execute(
                    "SELECT status, started_at, finished_at FROM executions WHERE job_id=? "
                    "ORDER BY claimed_at DESC, id DESC LIMIT 1",
                    (job_id,),
                ).fetchone()
                prefix = f"{profile}/" if profile else ""
                entry: dict[str, Any] = {"state": "ok"}
                if last is not None:
                    status, started_at, finished_at = last
                    entry["last_run"] = started_at or finished_at
                    entry["finished_at"] = finished_at
                    if status in ("completed", "failed"):
                        entry["last_status"] = status
                    else:
                        entry["exec_ledger_state"] = status or "unknown"
                if "cron_incidents" in tables:
                    types = conn.execute(
                        "SELECT DISTINCT failure_type FROM cron_incidents WHERE job_id=? AND state != 'closed'",
                        (job_id,),
                    ).fetchall()
                    entry["open_incident_types"] = sorted(row[0] for row in types if row[0])
                evidence[f"{prefix}{job_id}"] = entry
            if "cron_incidents" not in tables:
                store_meta["incidents"] = "no_incident_ledger"
            conn.close()
        except sqlite3.Error as exc:
            store_meta["state"] = "error"
            store_meta["error"] = f"{type(exc).__name__}: {exc}"
        meta["stores"][key] = store_meta
    return evidence, meta


def collect_hermes() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meta: dict[str, Any] = {"captured_at": now_iso(), "error": None, "path": str(HERMES_JOBS), "stores": []}
    jobs: list[dict[str, Any]] = []
    paths = [HERMES_JOBS, *sorted((HERMES_JOBS.parent.parent / "profiles").glob("*/cron/jobs.json"))]
    errors = []
    for path in paths:
        store: dict[str, Any] = {"path": str(path), "error": None}
        meta["stores"].append(store)
        try:
            raw = path.read_bytes()
            doc = json.loads(raw)
            rows = doc.get("jobs") if isinstance(doc, dict) else doc
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise ValueError("jobs.json root has no valid jobs array")
        except (OSError, ValueError) as exc:
            store["error"] = f"{type(exc).__name__}: {exc}"
            errors.append(f"{path}: {store['error']}")
            continue
        store["raw_sha256"] = sha256_bytes(raw)
        store["job_count"] = len(rows)
        profile = "" if path == HERMES_JOBS else path.parent.parent.name
        jobs.extend(dict(row, _hermes_profile=profile, _hermes_source_path=str(path)) for row in rows)
    meta["error"] = "; ".join(errors) or None
    meta["raw_sha256"] = sha256_text(json.dumps(meta["stores"], sort_keys=True))
    meta["job_count"] = len(jobs)
    return jobs, meta


def collect_orca() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meta: dict[str, Any] = {"captured_at": now_iso(), "error": None}
    rc, out, err = run_cli(["orca", "automations", "list", "--json"], timeout=60)
    if rc != 0:
        meta["error"] = f"orca automations list rc={rc}: {(err or out).strip()[:200]}"
        return [], meta
    try:
        doc = json.loads(out)
    except json.JSONDecodeError as exc:
        meta["error"] = f"orca output unparseable: {exc}"
        return [], meta
    if doc.get("ok") is not True:
        meta["error"] = f"orca reported not-ok: {str(doc.get('error'))[:200]}"
        return [], meta
    meta["raw_sha256"] = sha256_text(out)
    autos = (doc.get("result") or {}).get("automations") or []
    meta["automation_count"] = len(autos)
    return autos, meta


def collect_temporal() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meta: dict[str, Any] = {"captured_at": now_iso(), "error": None}
    rc, out, err = run_cli(["temporal", "schedule", "list", "--namespace", "default", "--output", "json"], timeout=60)
    if rc != 0:
        meta["error"] = f"temporal schedule list rc={rc}: {(err or out).strip()[:200]}"
        return [], meta
    try:
        parsed = json.loads(out)
    except json.JSONDecodeError as exc:
        meta["error"] = f"temporal output unparseable: {exc}"
        return [], meta
    meta["raw_sha256"] = sha256_text(out)
    schedules = parsed if isinstance(parsed, list) else [parsed]
    meta["schedule_count"] = len(schedules)
    return schedules, meta


# P4.1: union-wide — the sealed main.rig filter is a false-zero today (P0
# discovered 10 rig.* namespaces + tutorial, NO main.rig). Rows carry namespace.
KESTRA_LATEST_SQL = (
    "select json_agg(t) from (select namespace, id, revision, updated, value->>'sourceCode' as source_code "
    "from (select namespace, id, revision, updated, value, row_number() over "
    "(partition by tenant_id, namespace, id order by revision desc) rn from flows "
    "where deleted=false) f where rn=1) t"
)
KESTRA_NAMESPACES_SQL = "select json_agg(distinct namespace) from flows where deleted=false"


def collect_kestra(mcp_ids_path: Path | None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    meta: dict[str, Any] = {"captured_at": now_iso(), "error": None, "authority": f"docker exec {KESTRA_CONTAINER} psql (SELECT-only)"}
    rc, out, err = run_cli(["docker", "exec", KESTRA_CONTAINER, "psql", "-U", "kestra", "-d", "kestra", "-tAc", KESTRA_LATEST_SQL], timeout=30)
    if rc != 0:
        meta["error"] = f"kestra postgres query rc={rc}: {err.strip()[:200]}"
        meta["mcp_parity"] = {"status": "UNVERIFIED", "reason": "Postgres authority unavailable; MCP comparison skipped"}
        return [], meta
    try:
        rows = json.loads(out.strip() or "[]")
    except json.JSONDecodeError as exc:
        meta["error"] = f"kestra query output unparseable: {exc}"
        return [], meta
    meta["raw_sha256"] = sha256_text(out.strip())
    meta["flow_count"] = len(rows)
    rc2, out2, _ = run_cli(["docker", "exec", KESTRA_CONTAINER, "psql", "-U", "kestra", "-d", "kestra", "-tAc", KESTRA_NAMESPACES_SQL], timeout=15)
    if rc2 == 0:
        try:
            meta["namespaces"] = json.loads(out2.strip() or "[]")
        except json.JSONDecodeError:
            meta["namespaces"] = None
    # P4.1 REST execution evidence: stdlib urllib basic auth from env only
    # (never guessed). Unreachable => authority-down with the cause named and a
    # per-namespace literal; affected rows are tagged kestra-unverified.
    rest_meta: dict[str, Any] = {"namespaces": {}}
    env_missing = [key for key in ("KESTRA_URL", "KESTRA_USER", "KESTRA_PASS") if not os.getenv(key)]
    namespaces = meta.get("namespaces") if isinstance(meta.get("namespaces"), list) else []
    if env_missing:
        rest_meta["state"] = "authority-down"
        rest_meta["cause"] = "env_missing:" + ",".join(env_missing)
        rest_meta["namespaces"] = {ns: "authority-down" for ns in namespaces}
    else:
        base = str(os.getenv("KESTRA_URL")).rstrip("/")
        token = base64.b64encode(
            f"{os.getenv('KESTRA_USER')}:{os.getenv('KESTRA_PASS')}".encode()
        ).decode()

        def _kestra_get(path: str) -> Any:
            request = urllib_request_Request(
                base + path, headers={"Authorization": f"Basic {token}", "Accept": "application/json"}
            )
            with urlopen(request, timeout=8) as resp:  # noqa: S310 - env-pinned endpoint
                return json.loads(resp.read())

        try:
            flows_evidence: dict[str, dict[str, Any]] = {}
            for ns in namespaces:
                flows_doc = _kestra_get(f"/api/main/flows?namespace={ns}")
                for flow in flows_doc if isinstance(flows_doc, list) else []:
                    flow_id = str(flow.get("id"))
                    key = f"{ns}/{flow_id}"
                    cron = next(
                        (
                            trigger.get("cron")
                            for trigger in (flow.get("triggers") or [])
                            if "Schedule" in str(trigger.get("type"))
                        ),
                        None,
                    )
                    entry: dict[str, Any] = {
                        "enabled": not bool(flow.get("disabled", False)),
                        "trigger_expr": cron,
                    }
                    try:
                        execs = _kestra_get(
                            f"/api/main/executions?namespace={ns}&flows={flow_id}&size=1&sort=updated&sortOrder=DESC"
                        )
                        latest = (execs or [{}])[0] if isinstance(execs, list) else {}
                        current = str((latest.get("state") or {}).get("current") or "")
                        if current in ("SUCCESS", "FAILED", "WARNING"):
                            entry["last_result"] = current
                            entry["last_run"] = (latest.get("state") or {}).get("currentDate")
                    except (URLError, OSError, TimeoutError):
                        entry["exec_state"] = "unverified"
                    flows_evidence[key] = entry
                rest_meta["namespaces"][ns] = "ok"
            rest_meta["state"] = "reachable"
            rest_meta["flows"] = flows_evidence
        except (URLError, OSError, TimeoutError) as exc:
            rest_meta["state"] = "authority-down"
            rest_meta["cause"] = f"{type(exc).__name__}: {exc}"
            rest_meta["namespaces"] = {ns: "authority-down" for ns in namespaces}
    meta["rest"] = rest_meta

    pg_ids = sorted(str(r.get("id")) for r in rows)
    if mcp_ids_path and mcp_ids_path.is_file():
        mcp_ids = sorted(line.strip() for line in mcp_ids_path.read_text().splitlines() if line.strip())
        meta["mcp_parity"] = {
            "status": "MATCH" if mcp_ids == pg_ids else "MISMATCH",
            "mcp_count": len(mcp_ids),
            "postgres_count": len(pg_ids),
            "only_in_mcp": sorted(set(mcp_ids) - set(pg_ids)),
            "only_in_postgres": sorted(set(pg_ids) - set(mcp_ids)),
            "method": "stdio JSON-RPC tools/call of list_flows_in_namespace against the registered ghcr.io/kestra-io/mcp-server-python container after the KESTRA_BASE_URL registration repair (2026-09-10); mounted in-session tool reloads at next harness session",
        }
    else:
        meta["mcp_parity"] = {"status": "MCP_UNVERIFIED", "reason": "no MCP id evidence supplied via --kestra-mcp-ids"}
    return rows, meta


def collect_prefect() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    # P4.2 closed result set; the cause literal is exact, and no failed branch
    # may emit deployment_count (absence needs a named cause, never zero)
    meta: dict[str, Any] = {
        "captured_at": now_iso(),
        "error": None,
        "endpoint": PREFECT_API,
        "state": None,
        "note": "absence needs a named cause, never zero",
    }
    try:
        with urlopen(PREFECT_API, timeout=4) as resp:  # noqa: S310 - fixed local endpoint
            body = resp.read()
        try:
            doc = json.loads(body)
            metas = doc.get("deployments") if isinstance(doc, dict) else doc
            meta["deployment_count"] = len(metas or [])
            meta["raw_sha256"] = sha256_bytes(body)
            meta["state"] = "reachable"
            return metas or [], meta
        except json.JSONDecodeError as exc:
            meta["error"] = f"prefect response unparseable: {exc}"
            meta["state"] = "unreachable"
    except ConnectionRefusedError as exc:
        meta["error"] = f"prefect API refused: {type(exc).__name__}: {exc}"
        meta["state"] = "refused"
        meta["cause"] = f"{type(exc).__name__}: {exc}"
    except (URLError, OSError, TimeoutError) as exc:
        meta["error"] = f"prefect API unreachable: {type(exc).__name__}: {exc}"
        meta["state"] = "unreachable"
        meta["cause"] = f"{type(exc).__name__}: {exc}"
    return [], meta


# ---------------------------------------------------------------------------
# Normalization into one job-row shape
# ---------------------------------------------------------------------------

def _answer(score: float | None, evidence: str) -> dict[str, Any]:
    if score is None:
        return {"score": None, "status": "UNKNOWN", "evidence": evidence}
    return {"score": score, "status": "ANSWERED", "evidence": evidence}


def _map_match(job: dict[str, Any], standard: dict[str, Any]) -> dict[str, Any] | None:
    """Exact human-decision bindings win over every curated prefix/name match."""
    entries = standard.get("consumer_map", [])
    for entry in entries:
        # A human decision binds one exact stable id; never a prefix, never outranked.
        if entry.get("match_id") is not None and job["id"] == entry["match_id"]:
            return entry
    for entry in entries:
        if entry.get("match_id") is not None:
            continue
        source, _, name = str(entry.get("match", "")).partition(":")
        if job["source"] != source:
            continue
        if job["native_id"] == name or job["name"] == name or job["name"].startswith(name):
            return entry
    return None


def _recent_iso(values: list[str], days: int) -> str | None:
    cutoff = datetime.now(timezone(timedelta(0))) - timedelta(days=days)
    best: datetime | None = None
    for value in values:
        try:
            stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            continue
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone(timedelta(0)))
        if stamp >= cutoff and (best is None or stamp > best):
            best = stamp
    return best.isoformat(timespec="seconds").replace("+00:00", "Z") if best else None


def normalize_launchd(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in raw_rows:
        label = row.get("label") or Path(row["plist_path"]).stem
        args = row.get("arguments") or []
        command = " ".join([str(row.get("program") or (args[0] if args else "")), *[str(a) for a in (args[1:] if args else [])]]).strip()
        schedule_bits: list[str] = []
        if row.get("start_calendar"):
            schedule_bits.append("StartCalendarInterval")
        if row.get("start_interval"):
            schedule_bits.append(f"StartInterval={row['start_interval']}")
        out.append(
            {
                "source": "launchd",
                "native_id": label,
                "name": label,
                "lifecycle": "installed",
                "installed": True,
                "enabled": row.get("enabled"),
                "loaded": row.get("loaded"),
                "running": bool(row.get("pid")) if row.get("loaded") is not None else None,
                "pid": row.get("pid"),
                "last_exit_status": row.get("last_exit_status"),
                "trigger_kind": "launchd-keys",
                "trigger_expr": "+".join(schedule_bits) or ("WatchPaths" if row.get("watch_paths") else ("KeepAlive" if row.get("keep_alive") else ("RunAtLoad" if row.get("run_at_load") else ""))),
                "command": command or None,
                "body_path": (args[0] if args else None) or row.get("program"),
                "parse_ok": bool(row.get("parse_ok", True)),
                "parse_error": row.get("parse_error"),
                "keep_alive": bool(row.get("keep_alive")),
                "periodic": bool(row.get("start_calendar") or row.get("start_interval")),
                "run_at_load": bool(row.get("run_at_load")),
                "held_resources": row.get("held_resources") or [],
                "env_vars": row.get("env_vars") or {},
                "last_run": None,
                "last_result": None,
                "owner": None,
                "prompt_sha256": None,
                "source_refs": [row["plist_path"], "launchctl list", f"launchctl print-disabled gui/{os.getuid()}"],
                "deterministic_step": row.get("deterministic_step"),
                "evidence": row.get("evidence"),
            }
        )
    return out


def normalize_hermes(raw_jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for job in raw_jobs:
        schedule = job.get("schedule") or {}
        expr = schedule.get("display") or schedule.get("expr") or job.get("schedule_display") if isinstance(schedule, dict) else str(job.get("schedule_display") or "")
        state = str(job.get("state") or "")
        disposition = str(job.get("disposition") or "")
        script = job.get("script")
        out.append(
            {
                "source": "hermes",
                "native_id": (str(job["_hermes_profile"]) + "/" if job.get("_hermes_profile") else "") + str(job.get("id")),
                "name": str(job.get("name") or job.get("id")),
                "lifecycle": "retired" if state == "retired" or disposition == "dead" else ("completed" if state == "completed" else ("paused" if state == "paused" else state or "unknown")),
                "installed": True,
                "enabled": bool(job.get("enabled")),
                "loaded": None,
                "running": None,
                "archived": state in {"retired", "completed"} or disposition == "dead",
                "trigger_kind": (schedule.get("kind") if isinstance(schedule, dict) else None) or ("cron" if expr else None),
                "trigger_expr": expr or None,
                "command": str(script) if script else None,
                "body_path": str(script) if script else None,
                "last_run": str(job.get("last_run_at") or "") or None,
                "last_result": str(job.get("last_status") or "") or None,
                "owner": None,
                "deliver": str(job.get("deliver") or "") or None,
                "no_agent": job.get("no_agent"),
                "model": str(job.get("model") or "") or None,
                "workdir": str(job.get("workdir") or "") or None,
                "paused_reason": str(job.get("paused_reason") or "") or None,
                "retired_at": str(job.get("retired_at") or "") or None,
                "hermes_disposition": disposition or None,
                "prompt_sha256": sha256_text(str(job.get("prompt") or "")) if job.get("prompt") else None,
                "source_refs": [str(job.get("_hermes_source_path") or HERMES_JOBS)],
            }
        )
    return out


def normalize_orca(raw_autos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for auto in raw_autos:
        last_run_ms = auto.get("lastRunAt")
        next_run_ms = auto.get("nextRunAt")
        run_ctx = auto.get("runContext") or {}
        out.append(
            {
                "source": "orca",
                "native_id": str(auto.get("id")),
                "name": str(auto.get("name") or auto.get("id")),
                "lifecycle": "enabled" if auto.get("enabled") else "disabled",
                "installed": True,
                "enabled": bool(auto.get("enabled")),
                "loaded": None,
                "running": None,
                "trigger_kind": "rrule",
                "trigger_expr": str(auto.get("rrule") or "") or None,
                "timezone": str(auto.get("timezone") or "") or None,
                "scheduler_owner": str(auto.get("schedulerOwner") or "") or None,
                "command": None,
                "body_path": str(run_ctx.get("path") or "") or None,
                "agent_id": str(auto.get("agentId") or "") or None,
                "last_run": datetime.fromtimestamp(last_run_ms / 1000, tz=timezone(timedelta(0))).isoformat(timespec="seconds").replace("+00:00", "Z") if last_run_ms else None,
                "next_run": datetime.fromtimestamp(next_run_ms / 1000, tz=timezone(timedelta(0))).isoformat(timespec="seconds").replace("+00:00", "Z") if next_run_ms else None,
                "last_result": None,
                "owner": None,
                "missed_run_policy": str(auto.get("missedRunPolicy") or "") or None,
                "prompt_sha256": sha256_text(str(auto.get("prompt") or "")) if auto.get("prompt") else None,
                "source_refs": ["orca automations list --json"],
            }
        )
    return out


def normalize_temporal(raw_scheds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for sched in raw_scheds:
        info = sched.get("info") or {}
        actions = info.get("recentActions") or []
        paused = bool((info.get("pauseInfo") or {}).get("paused")) if info.get("pauseInfo") else False
        action_times = [str(a.get("actualTime") or "") for a in actions if a.get("actualTime")]
        last_result = None
        for action in reversed(actions):
            status = action.get("startWorkflowStatus")
            if status:
                last_result = status
                break
        cal = (info.get("spec") or {}).get("structuredCalendar")
        out.append(
            {
                "source": "temporal",
                "native_id": str(sched.get("scheduleId") or sched.get("id")),
                "name": str(sched.get("scheduleId") or sched.get("id")),
                "lifecycle": "paused" if paused else "active",
                "installed": True,
                "enabled": not paused,
                "loaded": None,
                "running": None,
                "trigger_kind": "structuredCalendar",
                "trigger_expr": f"structuredCalendar x {len(cal) if cal else 0} + tz:{(info.get('spec') or {}).get('timezoneName')}" if cal else None,
                "command": None,
                "workflow_type": str((info.get("workflowType") or {}).get("name") or "") or None,
                "task_queue": str((info.get("action") or {}).get("startWorkflow", {}).get("queue") or "") or None,
                "notes": str(info.get("notes") or "") or None,
                "body_path": None,
                "last_run": _recent_iso(action_times, RECENCY_DAYS) or (action_times[-1] if action_times else None),
                "last_result": last_result,
                "owner": None,
                "recent_action_count": len(actions),
                "prompt_sha256": None,
                "source_refs": ["temporal schedule list --namespace default --output json"],
            }
        )
    return out


TRIGGER_RE = re.compile(r"^\s*triggers:\s*$", re.MULTILINE)


def normalize_kestra(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in raw_rows:
        source_code = str(row.get("source_code") or "")
        has_triggers = bool(TRIGGER_RE.search(source_code))
        out.append(
            {
                "source": "kestra",
                "native_id": f"{row.get('namespace')}/{row.get('id')}" if row.get("namespace") else str(row.get("id")),
                "name": str(row.get("id")),
                "lifecycle": "definition",
                "installed": True,
                "enabled": None,
                "loaded": None,
                "running": None,
                "trigger_kind": "flow-triggers" if has_triggers else None,
                "trigger_expr": "triggers: block in source" if has_triggers else None,
                "namespace": str(row.get("namespace") or "") or None,
                "command": None,
                "body_path": None,
                "revision": row.get("revision"),
                "definition_updated": str(row.get("updated") or "") or None,
                "has_triggers": has_triggers,
                "deterministic_markers": bool(re.search(r"^\s*(script|queries|tasks):\s*$", source_code, re.MULTILINE)),
                "last_run": None,
                "last_result": None,
                "owner": None,
                "prompt_sha256": sha256_text(source_code) if source_code else None,
                "source_refs": [f"docker exec {KESTRA_CONTAINER} psql latest-revision SELECT (namespace {KESTRA_NAMESPACE})"],
            }
        )
    return out


def normalize_prefect(raw_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for dep in raw_rows:
        out.append(
            {
                "source": "prefect",
                "native_id": str(dep.get("id") or dep.get("name")),
                "name": str(dep.get("name") or dep.get("id")),
                "lifecycle": "deployment",
                "installed": True,
                "enabled": bool(dep.get("is_active", True)),
                "loaded": None,
                "running": None,
                "trigger_kind": "prefect-schedule" if dep.get("schedules") or dep.get("schedules_") else None,
                "trigger_expr": None,
                "command": None,
                "body_path": None,
                "last_run": None,
                "last_result": None,
                "owner": None,
                "prompt_sha256": None,
                "source_refs": [PREFECT_API],
            }
        )
    return out


# ---------------------------------------------------------------------------
# Scoring, classification, routing (pure functions)
# ---------------------------------------------------------------------------

def classify_job(job: dict[str, Any], standard: dict[str, Any]) -> str:
    if job["source"] == "hermes" and job.get("no_agent") is True:
        return "CODE" if job.get("body_path") else "UNKNOWN"
    if job["source"] == "hermes" and job.get("no_agent") is False:
        return "MODEL"
    if job["source"] == "orca":
        return "MODEL"
    if job["source"] == "kestra":
        return "CODE" if job.get("deterministic_markers") else "UNKNOWN"
    if job["source"] == "launchd":
        return "CODE" if job.get("parse_ok") and job.get("body_path") else "UNKNOWN"
    return "UNKNOWN"


def _vendor_managed(job: dict[str, Any], standard: dict[str, Any]) -> str | None:
    constraint = standard.get("platform_constraints", {}).get("vendor_managed", {})
    prefixes = constraint.get("label_prefixes", [])
    for prefix in prefixes:
        if job["name"].startswith(prefix):
            return f"label prefix {prefix}"
    body = job.get("body_path") or ""
    for prefix in constraint.get("path_prefixes", []):
        if body.startswith(prefix):
            return f"executable path prefix {prefix}"
    return None


def score_job(job: dict[str, Any], standard: dict[str, Any]) -> dict[str, Any]:
    answers: dict[str, dict[str, Any]] = {}
    match = _map_match(job, standard)
    vendor = _vendor_managed(job, standard)
    revenue = bool(match and match.get("revenue_bearing"))
    goal_keys = set((match or {}).get("goal_keys") or [])
    path_evidence = " ".join(filter(None, [job.get("command"), job.get("body_path"), job.get("workdir")]))
    revenue_artifact_hit = None
    if path_evidence.strip():
        revenue_artifact_hit = any(token in path_evidence for token in standard.get("revenue_artifact_paths", []))

    answers["Q01"] = (
        _answer(1.0, f"consumer_map: {match['consumer']}") if match
        else (_answer(1.0, f"vendor installer owner contract: {vendor}") if vendor
              else (_answer(0.0, "hermes authority state retired/dead — archived, no live consumer") if job["lifecycle"] in {"retired", "completed"} or job.get("hermes_disposition") == "dead"
                    else _answer(None, "no consumer evidence on any authority")))
    )
    answers["Q02"] = (
        _answer(1.0, f"mechanism cited: {match['mechanism']} [evidence: {match['evidence']}]") if match and goal_keys
        else (_answer(0.0, "curated map names no goal mechanism for this job") if match else _answer(None, "no curated mechanism for this job")))
    answers["Q03"] = (
        (lambda res: _answer(1.0 if str(res or "").lower() in {"ok", "completed", "workflow_execution_status_completed"} else 0.0, f"last observed result: {res}"))(job.get("last_result"))
        if revenue and job.get("last_result")
        else (_answer(None, "revenue job without observed execution result") if revenue else _answer(None, "not revenue-bearing; question scoped to revenue jobs")))
    answers["Q04"] = (
        _answer(1.0, "command/body path matches revenue artifact allowlist") if revenue_artifact_hit
        else (_answer(0.0, "path evidence exists and matches no revenue artifact") if path_evidence.strip() else _answer(None, "no path evidence on this authority")))
    answers["Q05"] = (
        _answer(0.0, f"duplicate effect target {job.get('duplicate_group')}") if job.get("duplicate_group")
        else _answer(1.0, "effect target unique across every scheduler authority"))

    answers["Q06"] = (
        _answer(1.0, f"goal keys {sorted(goal_keys)} cite the ladder") if goal_keys & {"rig_destination", "paid_deals", "qualified_calls", "offer_paths"}
        else (_answer(0.0, "curated map cites no ladder goal") if match else _answer(None, "no curated goal mapping")))
    answers["Q07"] = _answer(1.0, "consumer_map goal_key fitness") if "fitness" in goal_keys else _answer(None, "no fitness mechanism evidence")
    answers["Q08"] = _answer(1.0, "consumer_map goal_key james_affirmation") if "james_affirmation" in goal_keys else _answer(None, "no James-affirmation mechanism evidence")
    answers["Q09"] = _answer(1.0, "consumer_map goal_key learning") if "learning" in goal_keys else _answer(None, "no learning-floor mechanism evidence")
    answers["Q10"] = (
        _answer(1.0, f"named verifier: {match.get('verifier')}") if match and match.get("verifier")
        else (_answer(0.5, f"delivered to human channel '{job.get('deliver')}', readback unproven") if job.get("deliver") in {"telegram", "origin", "all"}
              else _answer(None, "output delivery not evidenced")))

    answers["Q11"] = (
        _answer(1.0, f"owner named via consumer_map: {match['consumer']}") if match
        else (_answer(0.5, f"vendor-owned via installer contract: {vendor}") if vendor
              else (_answer(0.5, f"scheduler owner is a platform service: {job.get('scheduler_owner')}") if job.get("scheduler_owner") else _answer(None, "no maintainer named on the authority"))))
    trigger_present = bool(job.get("trigger_expr"))
    if job["source"] == "launchd" and not trigger_present:
        answers["Q12"] = _answer(0.0, "no StartCalendarInterval/StartInterval/WatchPaths/Sockets; RunAtLoad only" if job.get("run_at_load") else "no schedule or trigger keys on the plist")
    elif trigger_present:
        answers["Q12"] = _answer(1.0, f"trigger configured: {job.get('trigger_kind')} {job.get('trigger_expr')}")
    else:
        answers["Q12"] = _answer(None, "authority returned no trigger field for this row")

    recent = _recent_iso([v for v in [job.get("last_run")] if v], RECENCY_DAYS)
    if job.get("last_run"):
        answers["Q13"] = _answer(1.0 if recent else 0.0, f"last recorded execution {job['last_run']} ({'within' if recent else 'outside'} {RECENCY_DAYS}-day window)")
    else:
        answers["Q13"] = _answer(None, "authority does not expose execution timestamps for this row")

    if job["source"] == "launchd":
        code = job.get("last_exit_status")
        answers["Q14"] = (
            _answer(None, "launchctl does not expose an exit status for this row")
            if code is None
            else _answer(1.0 if code == 0 else 0.0, f"launchctl last exit status {code}")
        )
    else:
        last_result = job.get("last_result")
        if last_result is None:
            answers["Q14"] = _answer(None, "no execution-result field on this authority")
        else:
            answers["Q14"] = _answer(1.0 if str(last_result).lower() in {"ok", "completed", "workflow_execution_status_completed"} else 0.0, f"last result {last_result}")

    if job["source"] == "launchd":
        answers["Q15"] = _answer(1.0 if job.get("parse_ok") else 0.0, "plist parses and label joined against launchctl list" if job.get("parse_ok") else job.get("parse_error", "plist parse failure"))
    elif job["source"] == "hermes":
        coherent = (job["lifecycle"] != "retired") == (job.get("retired_at") is None)
        answers["Q15"] = _answer(1.0 if coherent else 0.0, f"state/disposition coherence ({job.get('hermes_disposition')}, retired_at {job.get('retired_at')})")
    else:
        answers["Q15"] = _answer(1.0, "authority listing fetched complete; latest revision only")

    fit = job.get("_platform_fit") or {}
    answers["Q16"] = fit.get("q16", _answer(None, "routing evidence absent"))
    answers["Q17"] = fit.get("q17", _answer(None, "trigger-shape fit not assessable"))
    if job["source"] == "launchd":
        if job.get("held_resources"):
            answers["Q18"] = _answer(1.0, f"held resource keys {job['held_resources']}")
        elif job.get("keep_alive"):
            answers["Q18"] = _answer(0.0, "KeepAlive asserted with no socket/watched-dir/hardware/sub-second resource")
        else:
            answers["Q18"] = _answer(None, "no resident claim on this plist")
    else:
        answers["Q18"] = _answer(None, "not a launchd row")

    d85 = job.get("d85_class")
    answers["Q19"] = (
        _answer(1.0, "executable body path evidenced (CODE)") if d85 == "CODE"
        else (_answer(0.5, "agent-loop body (MODEL); deterministic alternative not recorded") if d85 == "MODEL"
              else _answer(None, "body class not inspectable from the authority")))

    if job["lifecycle"] in {"retired", "completed"} or job.get("hermes_disposition") == "dead":
        answers["Q20"] = _answer(0.0, f"authority lifecycle state {job['lifecycle']}")
    elif job["source"] == "launchd":
        answers["Q20"] = (
            _answer(None, "launchctl loaded state was not observed")
            if job.get("loaded") is None
            else _answer(1.0 if job["loaded"] else 0.5, "loaded in launchctl domain" if job["loaded"] else "installed, not currently loaded")
        )
    elif job["source"] == "hermes":
        answers["Q20"] = _answer(1.0 if job.get("hermes_disposition") == "active" else 0.5, f"hermes disposition {job.get('hermes_disposition')}")
    elif job.get("enabled") is None:
        answers["Q20"] = _answer(None, "authority does not expose enable/disable state for this row")
    else:
        answers["Q20"] = _answer(1.0 if job["enabled"] else 0.5, f"enabled={job['enabled']}" + (f", pause reason: {job.get('paused_reason')}" if job.get("paused_reason") else ""))

    criteria = {c["id"]: c for c in standard["criteria"]}
    totals = {"points_earned": 0.0, "points_possible": float(sum(c["weight"] for c in standard["criteria"])), "points_answered_possible": 0.0}
    answered = 0
    category_scores: dict[str, dict[str, float]] = {}
    for qid, ans in answers.items():
        crit = criteria[qid]
        cat = category_scores.setdefault(crit["category"], {"earned": 0.0, "possible_answered": 0.0, "answered": 0})
        if ans["status"] == "ANSWERED":
            answered += 1
            points = float(ans["score"]) * crit["weight"]
            totals["points_earned"] += points
            totals["points_answered_possible"] += crit["weight"]
            cat["earned"] += points
            cat["possible_answered"] += crit["weight"]
    totals["coverage"] = round(answered / len(standard["criteria"]), 3)
    for cat in category_scores.values():
        cat["answered"] = round(cat["answered"], 0)
    return {"answers": answers, "totals": totals, "category_scores": category_scores, "consumer_match": match, "vendor_managed": vendor}


def route_job(job: dict[str, Any], standard: dict[str, Any]) -> dict[str, Any]:
    source = job["source"]
    if source == "kestra":
        return {"recommended_platform": "Kestra", "reason": "scheduled run-to-completion work already on the canonical default", "blockers": []}
    if source == "launchd":
        if job.get("held_resources"):
            return {"recommended_platform": "launchd", "reason": f"evidenced held resource {job['held_resources']}", "blockers": []}
        vendor = _vendor_managed(job, standard)
        if vendor:
            return {"recommended_platform": "launchd", "reason": f"vendor-managed installer surface ({vendor}); migration is a vendor-contract decision", "blockers": []}
        if job.get("periodic"):
            return {"recommended_platform": "Kestra", "reason": "periodic run-to-completion without a held resource selects the Kestra default", "blockers": ["confirm current owner and last-exec semantics before moving a vendor-adjacent helper"]}
        return {"recommended_platform": None, "reason": "manual/one-off launchd surface (RunAtLoad or agent-only); not a scheduling recommendation", "blockers": []}
    if source == "temporal":
        return {"recommended_platform": None, "reason": "Temporal retention requires five named elements (consumer, failure mode, <=60s start-latency SLA, catch-up policy, deployment evidence); SLA and catch-up policy are not recorded on this authority", "blockers": ["document start-latency SLA and catch-up policy, or move the schedule to Kestra"]}
    if source == "hermes":
        if job.get("no_agent") is True and job.get("body_path"):
            return {"recommended_platform": "Kestra", "reason": "deterministic script job; Kestra owns ordinary schedules with the rejected-duplicate caveat", "blockers": ["preserve Hermes delivery semantics (deliver channel) or re-host them in the Kestra flow"]}
        return {"recommended_platform": None, "reason": "agent-loop cron host; Orca selection requires the rejected deterministic alternative and falsifiable reason, which is not recorded", "blockers": ["record agent_reasoning justification, then keep on an agent coordinator or rewrite deterministically onto Kestra"]}
    if source == "orca":
        return {"recommended_platform": "Orca", "reason": "judgment work on the judgment coordinator matches the precedence shape", "blockers": [] if job.get("enabled") else ["disabled authority state: confirm retire-vs-keep intent"]}
    if source == "prefect":
        return {"recommended_platform": None, "reason": "authority unreachable; no invented recommendation", "blockers": ["prefect authority down"]}
    return {"recommended_platform": None, "reason": "unknown source", "blockers": []}


def disposition_for(job: dict[str, Any], route: dict[str, Any], scored: dict[str, Any], standard: dict[str, Any]) -> tuple[str, list[str]]:
    answers = scored["answers"]
    blockers = list(route.get("blockers") or [])
    retired_state = job["lifecycle"] in {"retired", "completed"} or job.get("hermes_disposition") == "dead" or (job["source"] == "orca" and job.get("enabled") is False)
    coverage = scored["totals"]["coverage"]
    if retired_state:
        return "RETIRE", blockers + [f"authority state {job.get('hermes_disposition') or job['lifecycle']} — retired rows default to retire and never count as current schedules"]
    if route["recommended_platform"] and route["recommended_platform"] != job["source"] and job["source"] != "launchd" or (job["source"] == "launchd" and route["recommended_platform"] == "Kestra"):
        return "MIGRATE", blockers
    no_consumer = answers["Q01"]["status"] == "ANSWERED" and answers["Q01"]["score"] == 0
    if no_consumer and coverage >= standard["thresholds"]["retire_min_coverage"]:
        return "RETIRE", blockers + ["explicit lack of consumer with coverage >= threshold"]
    has_evidence = answers["Q13"]["status"] == "ANSWERED" and answers["Q13"]["score"] == 1 or scored["consumer_match"] is not None or scored["vendor_managed"] is not None
    if has_evidence and (answers["Q14"]["score"] is None or answers["Q14"]["score"] == 1):
        return "KEEP", blockers
    if answers["Q14"]["score"] == 0:
        return "INVESTIGATE", blockers + ["last observed execution failed"]
    return "INVESTIGATE", blockers + ["insufficient recent-run or consumer evidence for KEEP"]


def duplicate_pass(jobs: list[dict[str, Any]], standard: dict[str, Any]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {}
    for group in standard.get("effect_groups", []):
        members = [j["id"] for j in jobs if any(_map_match_id_match(j, m) for m in group["members"])]
        if len(members) > 1:
            groups[group["id"]] = members
            for j in jobs:
                if j["id"] in members:
                    j["duplicate_blockers"] = group["blockers"]
                    j["scheduler_of_record_candidate"] = group["scheduler_of_record_candidate"]
    mechanical: dict[str, list[str]] = {}
    for j in jobs:
        # P4.6: any row with a command participates in the mechanical
        # identical-command group (cross-scheduler), not launchd alone
        if j.get("command") and j.get("trigger_expr"):
            key = sha256_text(" ".join(str(j["command"]).split()) + "|" + str(j["trigger_expr"]) + "|" + json.dumps(j.get("env_vars") or {}, sort_keys=True))[7:23]
            mechanical.setdefault(key, []).append(j["id"])
    for key, members in mechanical.items():
        if len(members) > 1:
            groups[f"effect:identical-command-{key[:8]}"] = members
    for members in groups.values():
        for j in jobs:
            if j["id"] in members:
                j["duplicate_group"] = next(gid for gid, ms in groups.items() if j["id"] in ms)
    return [{"id": gid, "members": members} for gid, members in sorted(groups.items())]


CLASSIFICATIONS_DIR = ROOT / "estate" / "classifications"
JOB_CONTRACTS_DIR = ROOT / "estate" / "job-contracts"
OPERATING_STATES = ("proposed", "retired", "blocked", "running", "enabled", "last_success", "ready")
RETIREMENT_KINDS = ("owner_out", "duplicate_of", "unapproved", "outward_ungranted", "failed_fresh")
KESTRA_OWNERSHIP_CLASSES = ("independent", "legacy", "dup/legacy", "retired_dup")


def load_classifications(path: Path) -> dict[str, Any]:
    """Read-only owner-approval records (kestra_ownership.json +
    retirement_decisions.jsonl). Missing files mean no records — rows fall to
    defaults; never an error, never a second registry."""
    records: dict[str, Any] = {"ownership": {}, "retirements": {}}
    ownership_path = path / "kestra_ownership.json"
    if ownership_path.is_file():
        try:
            doc = json.loads(ownership_path.read_text())
            if isinstance(doc, dict):
                records["ownership"] = doc
        except (OSError, json.JSONDecodeError):
            records["ownership"] = {}
    retirements_path = path / "retirement_decisions.jsonl"
    if retirements_path.is_file():
        for line in retirements_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict) and record.get("job_id"):
                records["retirements"][record["job_id"]] = record
    return records


def _retire_binding(job: dict[str, Any]) -> str:
    source = job["source"]
    native = job["native_id"]
    if source == "launchd":
        return f"launchctl bootout gui/{os.getuid()}/{native} (+ {job.get('body_path') or 'plist'})"
    if source == "hermes":
        return f"hermes cron retire {native}"
    if source == "temporal":
        return f"temporal schedule pause {native}"
    if source == "orca":
        return f"orca automation disable {native} (confirm)"
    if source == "kestra":
        return f"kestra flow disable {native} (confirm)"
    return f"retire {source}:{native}"


def cross_scheduler_owners(
    jobs: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    classifications: dict[str, Any],
) -> list[str]:
    """One duplicate_group, exactly one scheduler_of_record. Kestra wins by
    migration convention; otherwise the owner record names it; otherwise the
    cause is owner_unresolved:<group>. Returns closed cause literals."""
    causes: list[str] = []
    by_id = {j["id"]: j for j in jobs}
    ownership = classifications.get("ownership") or {}
    retirements = classifications.get("retirements") or {}
    for group in groups:
        members = [by_id[mid] for mid in group["members"] if mid in by_id]
        live = [j for j in members if not j.get("archived")]
        if not members:
            continue
        kestra_members = [j for j in live if j["source"] == "kestra"]
        owner = None
        if kestra_members:
            owner = kestra_members[0]
        else:
            # the standard's curated candidate is its declared owner for the
            # group; owner-approval records outrank it; else unresolved
            # only owner-claiming classes count; retired_dup/dup/legacy are
            # records OF duplication, never claims of ownership
            claims = [
                j for j in members
                if (ownership.get(j["id"]) or {}).get("classification") in ("independent", "legacy")
            ]
            if len(claims) == 1:
                owner = claims[0]
            elif len(claims) > 1:
                for j in claims:
                    causes.append(f"multi_owner:{j['id']}")
            if owner is None:
                candidates = [j for j in members if j.get("scheduler_of_record_candidate") == j["id"]]
                if len(candidates) == 1:
                    owner = candidates[0]
        if owner is None:
            causes.append(f"owner_unresolved:{group['id']}")
        for j in members:
            is_owner = owner is not None and j["id"] == owner["id"]
            j["scheduler_of_record"] = owner["id"] if is_owner else None
            j["kestra_ownership"] = (ownership.get(j["id"]) or {}).get("classification")
            retirement = retirements.get(j["id"])
            if retirement:
                j["retire_reason"] = retirement.get("kind")
            migrate = []
            if owner is not None and not is_owner and j in live:
                migrate.append(
                    {
                        "from": j["id"],
                        "to": owner["id"],
                        "retire_binding": _retire_binding(j),
                    }
                )
            j["should_migrate"] = migrate
            if is_owner:
                j["owner_migration"] = [
                    {
                        "from": other["id"],
                        "to": owner["id"],
                        "retire_binding": _retire_binding(other),
                    }
                    for other in live
                    if other["id"] != owner["id"]
                ]
        for j in members:
            record = ownership.get(j["id"]) or {}
            j["classified_by"] = record.get("computed_by") or "collector:default"
            j["classified_at"] = record.get("at")
            if j["id"] in ownership and record.get("lid") is None:
                # an unsealed owner record is a pending Gate-D, deterministically
                j["gate_d_pending_lid"] = "unsealed"
    return causes


def _within_recency(iso_value: Any, capture_iso: str, days: int = RECENCY_DAYS) -> bool:
    if not iso_value:
        return False
    try:
        stamp = datetime.fromisoformat(str(iso_value).replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone(timedelta(0)))
        cutoff = datetime.now(timezone(timedelta(0))) - timedelta(days=days)
        return stamp >= cutoff
    except (ValueError, TypeError):
        return False


def operating_state_for(job: dict[str, Any], ctx: dict[str, Any]) -> tuple[str, list[str]]:
    """P4.5 closed-set row state, recomputed deterministically per capture.
    Nothing accumulates across runs; every blocking condition is a closed
    literal from the plan's set (+ retire_unverified per its prose)."""
    if job["source"] == "proposal":
        return "proposed", []
    conditions: list[str] = []
    rest = (ctx.get("authorities") or {}).get("kestra_rest") or {}
    prefect_meta = (ctx.get("authorities") or {}).get("prefect") or {}
    if rest.get("state") == "authority-down" and (job["source"] == "kestra" or str(job.get("scheduler_of_record") or "").startswith("kestra:")):
        conditions.append("kestra_authority_down")
    if prefect_meta.get("state") not in (None, "reachable") and job["source"] == "prefect":
        conditions.append("prefect_authority_down")
    if job.get("exec_ledger_state") == "no_exec_ledger":
        conditions.append("hermes_no_exec_ledger")
    ownership_class = job.get("kestra_ownership")
    if ownership_class and ownership_class.startswith("dup") and job.get("scheduler_of_record") and not str(job["scheduler_of_record"]).startswith("kestra:"):
        conditions.append("owner_reconcile_disputed")
    if job.get("gate_d_pending_lid"):
        conditions.append(f"gate_d_pending:{job['gate_d_pending_lid']}")
    for failure_type in job.get("observed_failure_modes") or []:
        conditions.append(f"open_cron_incident:{failure_type}")
    contract_ids = ctx.get("contract_ids") or set()
    if job["id"] not in contract_ids:
        conditions.append("contract_missing")
    if job.get("should_migrate") and job.get("duplicate_group") and job.get("scheduler_of_record") is None:
        conditions.append("migration_in_flight")
    if conditions:
        return "blocked", sorted(conditions)
    if job.get("disposition") == "RETIRE":
        off_verified = False
        source = job["source"]
        if source == "launchd":
            off_verified = job.get("enabled") is False and job.get("loaded") is False
        elif source == "hermes":
            off_verified = job.get("lifecycle") in ("retired", "completed") or job.get("hermes_disposition") == "dead"
        elif source == "orca":
            off_verified = job.get("enabled") is False
        elif source == "temporal":
            off_verified = job.get("lifecycle") == "paused"
        elif source == "kestra":
            off_verified = job.get("enabled") is False
        if off_verified:
            return "retired", []
        return "blocked", ["retire_unverified"]
    capture_iso = ctx.get("capture_iso") or ""
    source = job["source"]
    success_recent = False
    success_past = False
    if source == "hermes" and job.get("last_result") == "completed" and job.get("enabled"):
        success_recent = _within_recency(job.get("last_run"), capture_iso)
        success_past = bool(job.get("last_run")) and not success_recent
    elif source == "kestra" and job.get("last_result") == "SUCCESS" and job.get("enabled"):
        success_recent = _within_recency(job.get("last_run"), capture_iso)
        success_past = bool(job.get("last_run")) and not success_recent
    elif source == "temporal" and str(job.get("last_result") or "") == "workflow_execution_status_completed" and job.get("lifecycle") != "paused":
        success_recent = _within_recency(job.get("last_run"), capture_iso)
        success_past = bool(job.get("last_run")) and not success_recent
    if success_recent:
        return "running", []
    if source == "launchd" and job.get("pid") and job.get("held_resources"):
        return "running", []
    if success_past:
        return "last_success", []
    active = bool(
        job.get("enabled")
        or (source == "launchd" and job.get("loaded"))
        or (source == "hermes" and job.get("lifecycle") not in ("retired", "completed", "dead"))
        or (source == "temporal" and job.get("lifecycle") not in ("paused",))
        or (source == "kestra")
    )
    if active:
        return "enabled", []
    return "ready", []


CONTRACT_REQUIRED_KEYS = {
    "contract_id", "job_id", "source", "native_id", "owner_control", "operations", "failure_mode",
    "done_test", "freshness", "retention", "policy_sha256", "sealed_at", "lid", "seal_source",
}
CONTRACT_OWNER_SET = {"code", "model", "effect"}


def _contract_for(job_id: str, contracts_dir: Path) -> dict[str, Any]:
    """Load + structurally validate one job contract (stdlib-only shape checks;
    the jsonschema gate already lives in test_contract_checks)."""
    path = contracts_dir / f"{job_id}.json"
    if not path.is_file():
        return {"state": "missing", "contract_id": None, "lid": None}
    try:
        doc = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return {"state": "invalid", "contract_id": None, "lid": None, "cause": f"{type(exc).__name__}: {exc}"}
    if not isinstance(doc, dict) or set(doc) != CONTRACT_REQUIRED_KEYS:
        return {"state": "invalid", "contract_id": doc.get("contract_id") if isinstance(doc, dict) else None, "lid": None, "cause": "required key set mismatch"}
    operations = doc.get("operations")
    if (
        not isinstance(operations, list)
        or not operations
        or any(
            not isinstance(op, dict) or op.get("owner") not in CONTRACT_OWNER_SET or not op.get("mechanism")
            for op in operations
        )
    ):
        return {"state": "invalid", "contract_id": doc.get("contract_id"), "lid": None, "cause": "operations must be non-empty with closed owners + mechanism"}
    state = "sealed" if doc.get("lid") else "unsealed"
    return {
        "state": state,
        "contract_id": doc.get("contract_id"),
        "lid": doc.get("lid"),
        "failure_mode": doc.get("failure_mode"),
        "done_test": doc.get("done_test"),
        "operations": operations,
        "freshness": doc.get("freshness"),
        "retention": doc.get("retention"),
    }


_DURATION_PART = re.compile(r"(\d+)([DWMY])")


def _freshness_window_days(freshness: Any) -> int:
    """ISO-8601 duration → days (dep-free; M=30d, Y=365d — the duration only
    ever widens the verification window, ceiling noted)."""
    if not isinstance(freshness, str) or not freshness.startswith("P"):
        return RECENCY_DAYS
    days = 0
    for amount, unit in _DURATION_PART.findall(freshness):
        days += int(amount) * {"D": 1, "W": 7, "M": 30, "Y": 365}[unit]
    return max(RECENCY_DAYS, days or RECENCY_DAYS)


def _selector_evidence_for(job: dict[str, Any]) -> dict[str, Any]:
    step = job.get("deterministic_step")
    if isinstance(step, dict) and step.get("steps"):
        return {"deterministic_step": step}
    cadence = job.get("trigger_expr") or ("interval" if job.get("periodic") else None)
    if cadence:
        # honest claim shape; absent policies stay absent (selector blocks on
        # missing fields -> UNKNOWN, never fabricated policy text)
        return {"ordinary_schedule": {"cadence": str(cadence)}}
    return {}


def attach_gate_facts(
    jobs: list[dict[str, Any]],
    ctx: dict[str, Any],
) -> None:
    """P5 attach pass: one closed verdict object per contracted gate on each
    row. Absence is UNKNOWN with a named cause, never FAIL, never zero."""
    contracts_dir = ctx.get("contracts_dir") or JOB_CONTRACTS_DIR
    capture_iso = ctx.get("capture_iso") or now_iso()
    selector = ctx.get("selector")
    by_group: dict[str, list[dict[str, Any]]] = {}
    for job in jobs:
        if job.get("duplicate_group"):
            by_group.setdefault(job["duplicate_group"], []).append(job)
    for job in jobs:
        contract = _contract_for(job["id"], contracts_dir)
        job["contract"] = contract
        job["contract_id"] = contract.get("contract_id")
        job["contract_sealed"] = contract.get("state") == "sealed"

        # C19: exactly one live scheduler holds the job, off-states verified
        group_id = job.get("duplicate_group")
        if not group_id:
            job["record_owner_check"] = {"verdict": "PASS", "cause": "no_duplicate_group"}
        else:
            siblings = by_group.get(group_id, [])
            candidate = next((s["id"] for s in siblings if s.get("scheduler_of_record") == s["id"]), None)
            unverified = [
                s["id"] for s in siblings
                if s["id"] != job["id"] and s.get("operating_state") not in ("retired", "proposed")
            ]
            if unverified:
                job["record_owner_check"] = {"verdict": "UNKNOWN", "cause": f"off_state_unverified:{unverified[0]}", "group": group_id, "candidate": candidate}
            elif candidate and job["id"] != candidate:
                job["record_owner_check"] = {"verdict": "FAIL", "cause": f"held_by:{candidate}", "group": group_id, "candidate": candidate}
            elif candidate and job["id"] == candidate:
                job["record_owner_check"] = {"verdict": "PASS", "cause": "single_live_owner", "group": group_id, "candidate": candidate}
            else:
                job["record_owner_check"] = {"verdict": "UNKNOWN", "cause": f"owner_unresolved:{group_id}", "group": group_id, "candidate": None}

        # C20: migration binding recorded (owner + rollback)
        if job.get("owner_migration") or any(job.get("should_migrate") or []):
            job["migration_binding"] = {"verdict": "PASS", "cause": "binding_recorded"}
        elif group_id and job.get("scheduler_of_record") is None and job.get("duplicate_group"):
            job["migration_binding"] = {"verdict": "UNKNOWN", "cause": "migration_binding_absent"}
        else:
            job["migration_binding"] = {"verdict": "UNKNOWN", "cause": "migration_binding_absent"}

        # C21: renewal evidence per owner scheduler
        source = job["source"]
        if source == "kestra":
            if job.get("enabled") and job.get("last_result") == "SUCCESS":
                job["renewal_evidence"] = {"verdict": "PASS", "cause": "schedule_enabled_green_run"}
            else:
                job["renewal_evidence"] = {"verdict": "UNKNOWN", "cause": "no_renewal_clause"}
        elif source == "launchd":
            if (job.get("keep_alive") or job.get("start_interval")) and job.get("last_exit_status") == 0:
                job["renewal_evidence"] = {"verdict": "PASS", "cause": "keepalive_green_last_end"}
            elif job.get("keep_alive") or job.get("start_interval"):
                job["renewal_evidence"] = {"verdict": "UNKNOWN", "cause": "lastexit_unavailable"}
            else:
                job["renewal_evidence"] = {"verdict": "UNKNOWN", "cause": "no_renewal_clause"}
        elif source == "temporal":
            if job.get("catch_up_policy") and job.get("deployment_evidence"):
                job["renewal_evidence"] = {"verdict": "PASS", "cause": "catchup_and_deployment"}
            else:
                job["renewal_evidence"] = {"verdict": "UNKNOWN", "cause": "no_renewal_clause"}
        else:
            job["renewal_evidence"] = {"verdict": "UNKNOWN", "cause": "no_renewal_clause"}

        # C22: verified run within max(7d, freshness) with output ref
        window_days = _freshness_window_days(contract.get("freshness"))
        verified_at = None
        store_cause = None
        if source == "kestra" and job.get("last_result") == "SUCCESS" and job.get("last_run"):
            verified_at = job["last_run"]
        elif source == "hermes" and job.get("last_result") == "completed" and job.get("last_run"):
            verified_at = job["last_run"]
        elif source == "temporal" and str(job.get("last_result") or "") == "workflow_execution_status_completed" and job.get("last_run"):
            verified_at = job["last_run"]
        elif job.get("state") in ("kestra-unverified", "prefect-unverified"):
            store_cause = job["state"]
        elif job.get("exec_ledger_state") == "no_exec_ledger":
            store_cause = "hermes_no_exec_ledger"
        if verified_at and _within_recency(verified_at, capture_iso, days=window_days):
            job["execution_verified"] = {"verdict": "PASS", "cause": "verified_within_window", "window_days": window_days}
        elif store_cause:
            job["execution_verified"] = {"verdict": "UNKNOWN", "cause": store_cause, "window_days": window_days}
        elif verified_at:
            job["execution_verified"] = {"verdict": "UNKNOWN", "cause": "past_window", "window_days": window_days}
        else:
            job["execution_verified"] = {"verdict": "UNKNOWN", "cause": "no_execution_history", "window_days": window_days}

        # C23: trigger-owner selection evidenced (or default_used via Kestra)
        if selector is None:
            job["owner_evidence"] = {"verdict": "UNKNOWN", "cause": "tool_selection_absent"}
        else:
            evidence = _selector_evidence_for(job)
            try:
                verdict = selector.__call__(evidence)
                if verdict.get("framework") == "kestra" and verdict.get("default_used"):
                    job["owner_evidence"] = {"verdict": "PASS", "cause": "default_used_kestra"}
                elif verdict.get("framework") in ("plain_python", "kestra", "temporal", "launchd", "orca_pydantic", "langgraph"):
                    job["owner_evidence"] = {"verdict": "PASS", "cause": f"evidenced:{verdict['framework']}"}
                else:
                    job["owner_evidence"] = {"verdict": "UNKNOWN", "cause": "tool_selection_absent"}
            except Exception as exc:
                detail = str(exc)
                missing = detail.split(":", 1)[0]
                job["owner_evidence"] = {"verdict": "UNKNOWN", "cause": "tool_selection_absent", "missing_property": missing}


def _map_match_id_match(job: dict[str, Any], match_ref: str) -> bool:
    source, _, name = match_ref.partition(":")
    return job["source"] == source and (job["native_id"] == name or job["name"] == name or job["name"].startswith(name))


def goal_impact_for(job: dict[str, Any]) -> dict[str, Any]:
    match = job.get("_consumer_match") or {}
    impact: dict[str, Any] = {}
    for key in match.get("goal_keys") or []:
        impact[key] = {"value": 1, "mechanism": match.get("mechanism"), "consumer": match.get("consumer"), "evidence": match.get("evidence")}
    return impact


D85_SKILL = Path("/Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-determinism-85")
GATE_D_CONSUMED_DIR = D85_SKILL / "authority" / "gate_d" / "consumed"
DECISION_SCHEMA = "rig.estate.human-decision.v1"
IMPORT_ACTION_SCHEMA = "rig.estate.decision-import.v1"
ESTATE_PROCESS_ID = "estate-automation-review"
DECISION_REQUIRED = ("id", "process_id", "gate_d_run_id", "action_sha256", "action", "consumed_marker")
DECISION_BIND_FIELDS = ("id", "owner", "consumer", "mechanism", "goal_keys")


_D85_MODULE: Any = None


_TOOL_SELECTION_MODULE: Any = None


def _tool_selection():
    """The canonical two-owner selector, loaded read-only from the authority
    skill. A load failure is an absent tool (C23 -> tool_selection_absent),
    never a fabricated verdict."""
    global _TOOL_SELECTION_MODULE
    if _TOOL_SELECTION_MODULE is None:
        path = D85_SKILL / "tool_selection.py"
        spec = importlib.util.spec_from_file_location("rig_tool_selection_for_estate", path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:  # noqa: BLE001 - absent tool stays absent
            sys.modules.pop(spec.name, None)
            return None
        _TOOL_SELECTION_MODULE = module
    return getattr(_TOOL_SELECTION_MODULE, "select_framework", None)


def _canonical_hash():
    """The authority's own action hasher, loaded read-only. Never a local re-implementation."""
    global _D85_MODULE
    if _D85_MODULE is None:
        path = D85_SKILL / "d85.py"
        spec = importlib.util.spec_from_file_location("rig_d85_for_estate", path)
        if spec is None or spec.loader is None:
            raise SystemExit(f"NO CANONICAL HASH: cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        # d85 defines dataclasses, which resolve their owning module through sys.modules
        # at class-creation time; exec without registering first fails inside the import.
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 - an unloadable authority is a refusal, never a pass
            sys.modules.pop(spec.name, None)
            raise SystemExit(f"NO CANONICAL HASH: {path} failed to load: {exc}")
        _D85_MODULE = module
    hasher = getattr(_D85_MODULE, "_canonical_hash", None)
    if not callable(hasher):
        raise SystemExit("NO CANONICAL HASH: d85._canonical_hash is gone; refusing to judge action bytes locally")
    return hasher


def verify_decision(record: dict[str, Any], consumed_dir: Path = GATE_D_CONSUMED_DIR) -> None:
    """Bind a ledger record to the exact action a human armed. Strictly read-only.

    The collector never calls `gate-d`: gate_d() creates its consumed marker with O_EXCL,
    so a re-run would spend authority as a side effect of reading, and gate_d() also drops
    expired approvals before it inspects that marker — a replay would reject valid history
    once the approval TTL passes. Both errors are avoided by checking canonical state
    instead of re-judging it.

    These are necessary conditions, not approval proof: the action bytes on disk must
    re-hash (with the authority's own hasher) to the recorded action_sha256, the armed
    decision must equal the ledger row, and the consumed marker must carry this exact run
    id + action hash under authority/gate_d/consumed/. None of them is sufficient: that
    directory is not a D85 protected root and marker contents are unsigned, so the same
    local actor who wrote the ledger could name a marker. The sufficient proof is the HMAC
    over approvals.jsonl, which only the canonical authority can check. Until it exposes a
    read-only receipt operation, every record is refused and the overlay stays dormant.
    """
    missing = [f for f in DECISION_REQUIRED if record.get(f) in (None, "")]
    if missing:
        raise SystemExit(f"DECISION UNBOUND: {record.get('id')} missing {missing}")
    if not isinstance(record.get("goal_keys"), list):
        raise SystemExit(f"DECISION UNBOUND: {record.get('id')} goal_keys must be a list")
    action_path = Path(record["action"])
    if not action_path.is_file():
        raise SystemExit(f"DECISION ACTION MISSING: {action_path}")
    try:
        action = json.loads(action_path.read_text())
    except json.JSONDecodeError as exc:
        raise SystemExit(f"DECISION ACTION UNPARSEABLE: {action_path}: {exc}")
    if action.get("schema") != IMPORT_ACTION_SCHEMA or action.get("process_id") != record["process_id"]:
        raise SystemExit(f"DECISION ACTION MISMATCH: {action_path} is not an import action for {record['process_id']}")
    if _canonical_hash()(action) != record["action_sha256"]:
        raise SystemExit(f"DECISION ACTION HASH MISMATCH: {action_path} does not hash to "
                         f"{record['action_sha256']} — the armed bytes were replaced")
    armed = [d for d in action.get("decisions", []) if d.get("id") == record.get("id")]
    if len(armed) != 1 or any(armed[0].get(f) != record.get(f) for f in DECISION_BIND_FIELDS):
        raise SystemExit(f"DECISION CONTENT MISMATCH: {record.get('id')} is not what {action_path} armed")
    marker = Path(record["consumed_marker"])
    expected = f"{record['gate_d_run_id'][7:23]}.{record['action_sha256'][7:23]}"
    if marker.name != expected or marker.parent != consumed_dir:
        raise SystemExit(f"DECISION MARKER MISMATCH: {marker} does not bind run "
                         f"{record['gate_d_run_id']} / action {record['action_sha256']} at {consumed_dir}")
    if not marker.is_file():
        raise SystemExit(f"DECISION UNSPENT: {marker} does not exist — the canonical verifier "
                         "never consumed this approval, so it is not an applied decision")
    # Dormant by construction, with no auto-activation. A future activation is a reviewed
    # code change in this function: call a canonical read-only receipt operation in the D85
    # authority, check the verdict it returns for this run_id + action_sha256, and only then
    # return. Probing for the symbol's existence would be a bypass — an uncalled verifier
    # proves nothing.
    raise SystemExit(
        f"NO RECEIPT VERIFIER: no read-only Gate-D receipt check exists, so nothing can prove "
        f"the HMAC behind {record['gate_d_run_id']}. authority/gate_d/consumed/ is not a D85 "
        "protected root and marker contents are unsigned, so binding plus marker existence is "
        "necessary but not sufficient. Estate decision overlays stay dormant.")


def load_decisions(path: Path, consumed_dir: Path = GATE_D_CONSUMED_DIR) -> list[dict[str, Any]]:
    """Read the ledger. Structural defects are named before per-record Gate-D binding."""
    if not path.is_file():
        raise SystemExit(f"DECISIONS MISSING: {path} does not exist")
    parsed: list[tuple[int, dict[str, Any]]] = []
    seen: set[str] = set()
    for lineno, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"DECISIONS LINE {lineno}: unparseable JSON in {path}: {exc}")
        if record.get("schema") != DECISION_SCHEMA:
            raise SystemExit(f"DECISIONS LINE {lineno}: unknown schema {record.get('schema')!r}")
        if record.get("id") in seen:
            raise SystemExit(f"DECISIONS LINE {lineno}: duplicate decision for {record['id']}")
        seen.add(str(record.get("id")))
        parsed.append((lineno, record))
    if not parsed:
        raise SystemExit(f"DECISIONS EMPTY: {path} holds no records")
    for lineno, record in parsed:
        verify_decision(record, consumed_dir)
    return [record for _, record in parsed]


def apply_decisions(jobs: list[dict[str, Any]], standard: dict[str, Any],
                    records: list[dict[str, Any]],
                    consumed_dir: Path = GATE_D_CONSUMED_DIR) -> None:
    """Owner lands on the row; consumer/mechanism enter the same consumer_map curated entries use.

    Verification lives inside this boundary, not in front of it: a library caller that assembles
    plain dicts must not be able to move C06/C07/C10, Q11, or goal impact without a bound record.
    Every record is verified before anything mutates, so one unacceptable record cannot leave a
    half-applied overlay.
    """
    for record in records:
        if record.get("process_id") != ESTATE_PROCESS_ID:
            raise SystemExit(f"DECISION PROCESS MISMATCH: {record.get('id')} is armed for "
                             f"{record.get('process_id')!r}, not {ESTATE_PROCESS_ID!r}")
        verify_decision(record, consumed_dir)
    by_id = {job["id"]: job for job in jobs}
    for record in records:
        ident = record.get("id")
        job = by_id.get(ident)
        if job is None:
            raise SystemExit(f"DECISION UNKNOWN ROW: {ident} is not in this snapshot")
        if record.get("owner"):
            job["owner"] = record["owner"]
            job["owner_evidence"] = f"human decision, gate-D {record['gate_d_run_id']}"
        if record.get("consumer"):
            standard.setdefault("consumer_map", []).append({
                "match_id": ident,
                "consumer": record["consumer"],
                "mechanism": record.get("mechanism"),
                "goal_keys": record.get("goal_keys") or [],
                "evidence": f"human decision, gate-D {record['gate_d_run_id']}",
            })


# ---------------------------------------------------------------------------
# Snapshot assembly
# ---------------------------------------------------------------------------

def snapshot(standard: dict[str, Any], mcp_ids_path: Path | None,
             decisions_path: Path | None = None) -> dict[str, Any]:
    launch_raw, launch_meta = collect_launchd()
    hermes_raw, hermes_meta = collect_hermes()
    orca_raw, orca_meta = collect_orca()
    temporal_raw, temporal_meta = collect_temporal()
    kestra_raw, kestra_meta = collect_kestra(mcp_ids_path)
    prefect_raw, prefect_meta = collect_prefect()

    jobs: list[dict[str, Any]] = []
    jobs.extend(normalize_launchd(launch_raw))
    jobs.extend(normalize_hermes(hermes_raw))
    jobs.extend(normalize_orca(orca_raw))
    jobs.extend(normalize_temporal(temporal_raw))
    jobs.extend(normalize_kestra(kestra_raw))
    jobs.extend(normalize_prefect(prefect_raw))

    # P4.1: join REST evidence onto kestra rows; authority-down tags every row
    rest = kestra_meta.get("rest") or {}
    rest_flows = rest.get("flows") or {}
    for job in jobs:
        if job["source"] != "kestra":
            continue
        entry = rest_flows.get(job["native_id"])
        if entry:
            job["enabled"] = entry.get("enabled")
            if entry.get("trigger_expr"):
                job["trigger_expr"] = entry["trigger_expr"]
                job["trigger_kind"] = "cron"
            if entry.get("last_result"):
                job["last_result"] = entry["last_result"]
            if entry.get("last_run"):
                job["last_run"] = entry["last_run"]
        elif rest.get("state") == "authority-down":
            job["state"] = "kestra-unverified"

    # P4.3: join read-only execution evidence onto hermes rows (ledger wins for
    # last_run; terminal statuses only for last_result; unknown stays unknown)
    hermes_exec, hermes_exec_meta = collect_hermes_executions()
    for job in jobs:
        if job["source"] != "hermes":
            continue
        native = job["native_id"]
        profile = native.rpartition("/")[0] if "/" in native else ""
        entry = hermes_exec.get(native)
        if entry:
            if entry.get("last_run"):
                job["last_run"] = entry["last_run"]
            if entry.get("last_status"):
                job["last_result"] = entry["last_status"]
            if entry.get("exec_ledger_state"):
                job["exec_ledger_state"] = entry["exec_ledger_state"]
            if entry.get("open_incident_types"):
                job["observed_failure_modes"] = entry["open_incident_types"]
        else:
            store_state = (hermes_exec_meta["stores"].get(profile or "(root)") or {}).get("state")
            if store_state and store_state != "ok":
                job["exec_ledger_state"] = store_state

    for job in jobs:
        job["id"] = f"{job['source']}:{job['native_id']}"
    groups = duplicate_pass(jobs, standard)

    # P4.6: owner-approval records + one scheduler of record per duplicate group
    classifications = load_classifications(CLASSIFICATIONS_DIR)
    owner_causes = cross_scheduler_owners(jobs, groups, classifications)

    human: dict[str, Any] | None = None
    if decisions_path:
        # The ledger path, not a caller-assembled list, is what reaches the scoring boundary.
        records = load_decisions(decisions_path)
        apply_decisions(jobs, standard, records)
        human = {"records": len(records),
                 "gate_d_run_ids": sorted({d["gate_d_run_id"] for d in records})}

    contract_ids = {
        path.stem
        for path in JOB_CONTRACTS_DIR.glob("*.json")
        if path.suffix == ".json"
    } if JOB_CONTRACTS_DIR.is_dir() else set()
    state_ctx = {
        "authorities": {"kestra_rest": kestra_meta.get("rest"), "prefect": prefect_meta},
        "exec": hermes_exec,
        "contract_ids": contract_ids,
        "capture_iso": now_iso(),
    }
    for job in jobs:
        job["d85_class"] = classify_job(job, standard)
        route = route_job(job, standard)
        try:
            job["deterministic_step"] = deterministic_step(job)
        except ValueError as exc:
            job["deterministic_step"] = None
            job["deterministic_step_unknown"] = f"deterministic_step_malformed: {exc}"
        fit_q16 = (
            _answer(1.0, route["reason"]) if route["recommended_platform"] == job["source"]
            else (_answer(0.0, route["reason"]) if route["recommended_platform"] else _answer(None, route["reason"]))
        )
        if job["source"] == "launchd":
            fit_q17 = _answer(0.0, "periodic run-to-completion on launchd selects Kestra") if (job.get("periodic") and not job.get("held_resources") and not _vendor_managed(job, standard)) else (_answer(1.0, "resident/vendored surface on its native platform") if (job.get("held_resources") or _vendor_managed(job, standard)) else _answer(None, "manual surface; shape not comparable"))
        elif job["source"] == "kestra":
            fit_q17 = _answer(1.0, "scheduled deterministic flow on the canonical default") if job.get("has_triggers") else _answer(None, "trigger presence not derivable from source")
        elif job["source"] == "temporal":
            fit_q17 = _answer(1.0, "schedule is native Temporal shape; selection evidence is the separate five-element test")
        elif job["source"] == "hermes":
            fit_q17 = _answer(0.5, "cron runner hosting agent-loop jobs; judgment platform per precedence") if job.get("no_agent") is False else _answer(1.0, "cron runner hosting a deterministic script")
        elif job["source"] == "orca":
            fit_q17 = _answer(1.0, "judgment job on the judgment coordinator")
        else:
            fit_q17 = _answer(None, "authority unreachable")
        job["_platform_fit"] = {"q16": fit_q16, "q17": fit_q17}
        scored = score_job(job, standard)
        job["_consumer_match"] = scored["consumer_match"]
        job["answers"] = scored["answers"]
        job["score"] = {"earned": round(scored["totals"]["points_earned"], 2), "possible": scored["totals"]["points_possible"], "answered_possible": scored["totals"]["points_answered_possible"], "coverage": scored["totals"]["coverage"]}
        job["category_scores"] = scored["category_scores"]
        job["goal_impact"] = goal_impact_for(job)
        job["d85_classification"] = job["d85_class"]
        job["current_platform"] = job["source"]
        job["recommended_platform"] = route["recommended_platform"]
        job["recommendation_reason"] = route["reason"]
        disposition, blockers = disposition_for(job, route, scored, standard)
        if job.get("duplicate_group") and job.get("scheduler_of_record_candidate") and job["id"] != job["scheduler_of_record_candidate"]:
            disposition = "MIGRATE"
            blockers = blockers + [f"duplicate effect target {job['duplicate_group']}; scheduler-of-record candidate {job['scheduler_of_record_candidate']}"]
        job["disposition"] = disposition
        job["blockers"] = blockers
        job["confidence"] = round(0.2 + 0.8 * scored["totals"]["coverage"], 3)
        job["duplicate_group"] = job.get("duplicate_group")
        job["vendor_managed"] = scored["vendor_managed"]
        job.pop("_platform_fit", None)
        job.pop("_consumer_match", None)
        job["operating_state"], job["blocking_conditions"] = operating_state_for(job, state_ctx)
        job["evidence"] = {
            "command_sha256": sha256_text(job["command"]) if job.get("command") else None,
            "prompt_sha256": job.get("prompt_sha256"),
            "sources": job["source_refs"],
        }

    jobs.sort(key=lambda j: j["id"])
    live_jobs = [j for j in jobs if not j.get("archived")]
    archived_jobs = [j for j in jobs if j.get("archived")]
    # the closing bar is per-group: exactly one scheduler of record per
    # duplicate group (non-owner members carry should_migrate instead)
    inventory_causes = sorted(set(owner_causes))

    unknown_count = sum(1 for j in jobs for ans in j["answers"].values() if ans["status"] == "UNKNOWN")
    authority_errors = {name: meta["error"] for name, meta in {
        "launchd": launch_meta, "hermes": hermes_meta, "orca": orca_meta, "temporal": temporal_meta, "kestra": kestra_meta, "prefect": prefect_meta,
    }.items() if meta.get("error")}
    mcp_parity = kestra_meta.get("mcp_parity", {"status": "UNVERIFIED"})

    blocking_conditions = [
        "Prefect authority unreachable: no deployment count claimed.",
        "Kestra collection is definition-level: executions/last results not collected.",
        "launchd exposes no last-execution timestamp: recency answers stay UNKNOWN for launchd rows.",
        "No current registry proves this list covers every scheduler technology in the estate.",
    ]
    if authority_errors:
        blocking_conditions.append(f"authority errors: {sorted(authority_errors)}")
    if mcp_parity.get("status") != "MATCH":
        blocking_conditions.append(f"Kestra MCP parity is {mcp_parity.get('status')}")

    goal_evidence = {}
    for path_str in standard.get("goal_evidence_sources", []):
        path = Path(path_str)
        goal_evidence[path_str] = {"sha256": sha256_bytes(path.read_bytes()) if path.is_file() else None, "error": None if path.is_file() else "unreadable"}

    proposals = []
    for seed in standard.get("proposal_seeds", []):
        proposals.append({
            "id": seed["id"], "source": "proposal", "name": seed["name"], "disposition": "PROPOSED",
            "consumer": seed["consumer"], "mechanism": seed["mechanism"], "done_test": seed["done_test"],
            "goal_keys": seed["goal_keys"], "recommended_platform": seed["suggested_platform"],
            "operating_state": "proposed", "blocking_conditions": [], "contract_id": None,
        })

    def by_platform(row_list: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for job in row_list:
            counts[job["source"]] = counts.get(job["source"], 0) + 1
        return dict(sorted(counts.items()))

    def by_disposition(row_list: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for job in row_list:
            counts[job["disposition"]] = counts.get(job["disposition"], 0) + 1
        return dict(sorted(counts.items()))

    attach_gate_facts(
        jobs,
        {
            "contracts_dir": JOB_CONTRACTS_DIR,
            "capture_iso": now_iso(),
            "selector": _tool_selection(),
        },
    )
    checklist = enrich_rows(jobs + proposals, load_checklist_spec())
    packet = {
        "schema": "rig.automation-estate-review.v2",
        "claim_scope": "Evidence-bounded snapshot of every reachable scheduler authority. UNKNOWN means unobserved, never zero. Read-only review: no start/stop/delete/migrate action is taken or possible from the page.",
        "captured_at": now_iso(),
        "inventory_complete": not inventory_causes,
        "inventory_causes": inventory_causes,
        "blocking_conditions": blocking_conditions,
        "authorities": {
            "launchd": launch_meta, "hermes": hermes_meta, "orca": orca_meta,
            "temporal": temporal_meta, "kestra": kestra_meta, "prefect": prefect_meta,
        },
        "counts": {
            "live": len(live_jobs),
            "archived": len(archived_jobs),
            "proposed": len(proposals),
            "live_by_platform": by_platform(live_jobs),
            "archived_by_platform": by_platform(archived_jobs),
            "live_by_disposition": by_disposition(live_jobs),
            "unknown_answers": unknown_count,
        },
        "goal_evidence": goal_evidence,
        "mcp": {"kestra_parity": mcp_parity},
        "lattice": LATTICE,
        "checklist": checklist,
        "human_decisions": human,
        "standard": {"path": str(STANDARD_PATH), "sha256": sha256_bytes(STANDARD_PATH.read_bytes()), "version": standard.get("version"), "criteria_count": len(standard["criteria"])},
        "criteria": standard["criteria"],
        "categories": standard["categories"],
        "owner_table": standard["owner_table"],
        "routing_sentence": standard["routing_sentence"],
        "disposition_rules": standard["disposition_rules"],
        "duplicate_groups": groups,
        "jobs": jobs,
        "proposals": proposals,
    }
    return packet


# ---------------------------------------------------------------------------
# Output writing + self-check
# ---------------------------------------------------------------------------

DATA_START = "<!--ESTATE-DATA-START-->"
DATA_END = "<!--ESTATE-DATA-END-->"


def embed_in_html(html: str, packet_json: str) -> str:
    escaped = packet_json.replace("</", "<\\/")
    pattern = re.compile(re.escape(DATA_START) + r".*?" + re.escape(DATA_END), re.DOTALL)
    replacement = DATA_START + '<script type="application/json" id="estate-data">' + escaped + "</script>" + DATA_END
    if not pattern.search(html):
        raise SystemExit("HTML output lacks ESTATE-DATA markers")
    html = pattern.sub(lambda _m: replacement, html, count=1)
    html = re.sub(r'<meta name="estate-packet-sha256" content="[^"]*"',
                  '<meta name="estate-packet-sha256" content="' + packet_json_hash(packet_json) + '"', html, count=1)
    return html


def packet_json_hash(packet_json: str) -> str:
    return sha256_bytes(packet_json.encode("utf-8"))


def build_packet_json(packet: dict[str, Any]) -> str:
    return json.dumps(packet, indent=1, ensure_ascii=True, sort_keys=False)


# Fields that legitimately move between two captures of an unchanged estate. `captured_at` is when
# the collector ran; `raw_sha256` is a hash over the raw inventory including that timestamp;
# `last_run` (and the evidence sentence that quotes it) is a fact about a job that actually ran,
# and `next_run` is the next firing computed from the clock. None is a scoring decision.
# classified_at is capture-stamped by contract; last_result is a fact about a
# job that ran (same volatility class as last_run). operating_state and
# scheduler_of_record differences are the real drift and must NOT settle.
VOLATILE_KEYS = ("captured_at", "raw_sha256", "last_run", "next_run", "classified_at", "last_result")
TIMED_EVIDENCE = re.compile(r"(last recorded execution )\d{4}-\d\d-\d\dT[\d:]+Z")


def _settle(obj: Any, path: str = "", dropped: list | None = None):
    """Copy a packet with time-dependent fields replaced by a marker, collecting what was dropped.

    Only values that differ between the two sides are reported, so an operator sees the real drift
    (a job that ran) and not thirty identical timestamp substitutions.
    """
    dropped = [] if dropped is None else dropped
    if isinstance(obj, dict):
        out = {}
        for key, value in obj.items():
            if key in VOLATILE_KEYS:
                dropped.append(f"{path}.{key}")
                out[key] = "<volatile>"
            else:
                out[key] = _settle(value, f"{path}.{key}", dropped)
        return out
    if isinstance(obj, list):
        return [_settle(v, f"{path}[{i}]", dropped) for i, v in enumerate(obj)]
    if isinstance(obj, str):
        return TIMED_EVIDENCE.sub(r"\1<volatile>", obj)
    return obj


def _volatile_diff(sealed: Any, fresh: Any, path: str = "") -> list[str]:
    """Names the volatile values that actually changed, so the ignoring above is auditable."""
    found: list[str] = []
    if isinstance(sealed, dict) and isinstance(fresh, dict):
        for key in set(sealed) | set(fresh):
            if key in VOLATILE_KEYS and sealed.get(key) != fresh.get(key):
                found.append(f"{path}.{key}: {sealed.get(key)} -> {fresh.get(key)}")
            elif key in sealed and key in fresh:
                found += _volatile_diff(sealed[key], fresh[key], f"{path}.{key}")
    elif isinstance(sealed, list) and isinstance(fresh, list) and len(sealed) == len(fresh):
        for i, (a, b) in enumerate(zip(sealed, fresh)):
            found += _volatile_diff(a, b, f"{path}[{i}]")
    elif isinstance(sealed, str) and isinstance(fresh, str) and sealed != fresh \
            and TIMED_EVIDENCE.sub(r"\1<t>", sealed) == TIMED_EVIDENCE.sub(r"\1<t>", fresh):
        found.append(f"{path}: {sealed} -> {fresh}")
    return found


def self_check(packet: dict[str, Any], content_path: Path, html_path: Path | None,
               packet_json: str, settle_volatile: bool = False) -> list[str]:
    failures: list[str] = []

    def check(ok: bool, label: str) -> None:
        if not ok:
            failures.append(label)

    check(packet["schema"] == "rig.automation-estate-review.v2", "schema")
    check(packet["standard"]["criteria_count"] == 20 and len(packet["criteria"]) == 20, "criteria_count != 20")
    ids = [j["id"] for j in packet["jobs"]]
    check(len(ids) == len(set(ids)), "duplicate stable job IDs")
    enum_ok = all(
        j["disposition"] in DISPOSITIONS and ans["status"] in ANSWER_STATUSES and (ans["score"] is None or ans["score"] in {0, 0.5, 1})
        for j in packet["jobs"] for ans in j["answers"].values()
    )
    check(enum_ok, "enum violation in dispositions/answers")
    check(all(j["disposition"] != "PROPOSED" for j in packet["jobs"]), "a PROPOSED row leaked into live jobs")
    check(all(p["disposition"] == "PROPOSED" for p in packet["proposals"]), "proposal disposition drift")
    check(packet["counts"]["live"] + packet["counts"]["archived"] == len(packet["jobs"]), "live+archived must equal rendered job rows")
    check(packet["counts"]["archived"] == sum(1 for j in packet["jobs"] if j.get("archived")), "archived total mismatch")
    check(packet["counts"]["proposed"] == len(packet["proposals"]), "proposal invariant")
    check(0 <= packet["counts"]["unknown_answers"], "unknown count")
    file_bytes = content_path.read_bytes()
    external_hash = sha256_bytes(file_bytes)
    written_json = file_bytes.decode("utf-8")
    if settle_volatile:
        # Nothing was written, so byte equality with the sealed file is impossible: the capture
        # timestamp moves every run, and `last_run` moves whenever a job actually ran. Compare the
        # scored content with those fields settled, and let the caller report exactly what moved.
        check(json.dumps(_settle(json.loads(written_json)), sort_keys=True)
              == json.dumps(_settle(packet), sort_keys=True),
              "scored estate differs from the sealed packet beyond capture time and job runs")
    else:
        check(written_json == packet_json, "written packet differs from computed packet")
    if html_path is not None and html_path.exists():
        html_text = html_path.read_text()
        embedded_meta = re.search(r'<meta name="estate-packet-sha256" content="([^"]+)"', html_text)
        check(bool(embedded_meta) and embedded_meta.group(1) == external_hash, "embedded meta hash differs from external packet")
        embedded_block = re.search(re.escape(DATA_START) + r'.*?<script type="application/json" id="estate-data">(.*?)</script>' + re.escape(DATA_END), html_text, re.DOTALL)
        if not embedded_block:
            failures.append("embedded packet block missing")
        else:
            embedded_obj = json.loads(embedded_block.group(1))
            check(json.dumps(embedded_obj, sort_keys=False) == json.dumps(json.loads(written_json), sort_keys=False), "embedded packet differs from external packet")
    cl = packet.get("checklist") or {}
    check(cl.get("rows") == len(packet["jobs"]) + len(packet["proposals"]), "checklist summary rows mismatch")
    if cl.get("spec", {}).get("item_ids"):
        want_ids = cl["spec"]["item_ids"]
        rec = {"PASS": 0, "FAIL": 0, "UNKNOWN": 0}
        allp = lat = 0
        rexec = {"c08": {"observed": 0, "capable_but_missing": 0, "untestable": 0},
                 "c09": {"observed": 0, "capable_but_missing": 0, "untestable": 0}}
        ebucket = {"PASS": "observed", "FAIL": "capable_but_missing", "UNKNOWN": "untestable"}
        drift = False
        for j in list(packet["jobs"]) + list(packet["proposals"]):
            ck = j.get("checklist") or {}
            if sorted(ck.keys()) != sorted(want_ids):
                drift = True
                break
            for st in ck.values():
                rec[st] += 1
            allp += sum(1 for v in ck.values() if v == "PASS") == len(want_ids)
            lat += bool((j.get("lattice") or {}).get("coordinate"))
            for item_id, key in (("C08", "c08"), ("C09", "c09")):
                rexec[key][ebucket.get(ck.get(item_id, "UNKNOWN"), "untestable")] += 1
        check(not drift, "checklist item drift: a row lacks the full checklist")
        check(rec == cl["totals"] and allp == cl["rows_all_pass"] and lat == cl["lattice_assigned"],
              "checklist summary cannot be recomputed from rows")
        check(lat == cl.get("rows"), "lattice routing incomplete: rows without a coordinate")
        check(rexec == cl.get("execution_observed"), "execution_observed cannot be recomputed from rows")
    check(all(0.0 <= j["score"]["coverage"] <= 1.0 for j in packet["jobs"]), "coverage bounds")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect the automation estate into a scored review packet")
    parser.add_argument("--output", type=Path, default=ROOT / "v3" / "automation-estate-review.content.json")
    parser.add_argument("--html", type=Path, default=None, help="opt-in page update; --output must be that page's .content.json companion")
    parser.add_argument("--kestra-mcp-ids", type=Path, default=None, help="file of flow ids from the kestra MCP list_flows_in_namespace(main.rig) for parity")
    parser.add_argument("--decisions", type=Path, default=None,
                        help="human-decision ledger (JSONL) already armed by the canonical Gate-D verifier")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="score, hash, and self-check against what is already on disk; write "
                             "nothing. The packet and the sealed page are compared, never rewritten.")
    args = parser.parse_args()
    if args.html is not None:
        if not args.html.is_file() or args.output.resolve() != args.html.resolve().with_suffix(".content.json"):
            parser.error("--html requires an existing page and its exact .content.json companion as --output")
    html_path = args.html
    if html_path is None and args.dry_run and args.output.resolve() == (ROOT / "v3" / "automation-estate-review.content.json").resolve():
        html_path = ROOT / "v3" / "automation-estate-review.html"
    if args.dry_run and html_path is not None and not html_path.is_file():
        _err(f"DRY RUN: {html_path} does not exist; canonical page comparison cannot run")
        return 1

    standard = json.loads(STANDARD_PATH.read_text())
    packet = snapshot(standard, args.kestra_mcp_ids, args.decisions)
    packet_json = build_packet_json(packet)
    if args.dry_run:
        # Dry-run always compares computed state with the selected packet and, for the
        # canonical packet, its existing HTML. Verification must not be opt-in.
        if not args.output.exists():
            _err(f"DRY RUN: {args.output} does not exist; nothing to compare against")
            return 1
        file_hash = sha256_bytes(args.output.read_bytes())
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(packet_json + "\n")
        file_hash = sha256_bytes(args.output.read_bytes())
        if html_path is not None:
            html = html_path.read_text()
            payload = json.dumps(packet, indent=1, ensure_ascii=True) + "\n"
            html_path.write_text(embed_in_html(html, payload))

    if args.self_check or args.dry_run:
        failures = self_check(packet, args.output, html_path if html_path is not None and html_path.exists() else None,
                              packet_json + "\n", settle_volatile=args.dry_run)
        if failures:
            for failure in failures:
                _err(f"SELF-CHECK FAIL: {failure}")
            return 1
        print("AUTOMATION ESTATE SELF-CHECK PASS")
        if args.dry_run:
            moved = _volatile_diff(json.loads(args.output.read_text()), packet)
            print(f"volatile drift={len(moved)}" + (f" (showing 6): {moved[:6]}" if moved else ""))
        print(f"20 criteria; jobs live={packet['counts']['live']} archived={packet['counts']['archived']} proposed={packet['counts']['proposed']}")
        print(f"live_by_disposition={packet['counts']['live_by_disposition']}")
        print(f"checklist rows={packet['checklist']['rows']} pass_rate={packet['checklist']['pass_rate']:.1%} all_pass={packet['checklist']['rows_all_pass']} lattice={packet['checklist']['lattice_assigned']}/{packet['checklist']['rows']} totals={packet['checklist']['totals']}")
        print(f"packet {file_hash}")
        print(f"mcp_parity={packet['mcp']['kestra_parity']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
