"""Estate ledger builder — mechanical discovery of the scheduling estate.

Scans the live estate surfaces and emits one ledger record per job with a
framework verdict derived from source-proven evidence:

- launchd: ~/Library/LaunchAgents plists. The plist itself is evidence —
  WatchPaths/Sockets/WatchDevices prove resident_service; StartCalendarInterval/
  StartInterval without those prove a periodic script (default verdict).
- hermes: ~/.hermes/cron/jobs.json. Only enabled, non-retired jobs are estate;
  everything else is summarized, not listed.
- kestra / temporal / orca: recorded with their reachability status. When the
  surface is not reachable, its counts carry source='user_table_2026-09-09'
  and status 'declared_unreachable' — never silently classified.

Honest evidence classes only (per doctrine): source-proven, declared-only,
needs_review. Nothing is upgraded into a proven class without source evidence.

Usage: python3 estate_ledger.py [--write]  (default: emit JSON to stdout)
"""

from __future__ import annotations

import json
import plistlib
import sys
from datetime import datetime, timezone
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tool_selection import ToolSelectionBlock, select_framework  # noqa: E402

USER_TABLE_SOURCE = "user_table_2026-09-09"
VENDOR_PREFIXES = (
    "com.apple.",
    "com.microsoft.",
    "com.google.",
    "com.adobe.",
    "com.github.",
    "com.jetbrains.",
    "com.docker.",
    "com.slack.",
    "com.discord.",
    "com.spotify.",
    "com.zoom.",
    "org.mozilla.",
    "net.java.",
    "io.docker.",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _launchd_jobs() -> tuple[list[dict], dict]:
    records: list[dict] = []
    stats = {"plists": 0, "vendor_skipped": 0, "resident": 0, "periodic": 0, "needs_review": 0, "unreadable": 0}
    label_pids = _label_pids()
    listener_pids = _listener_pids()
    corroboration = {label: listener for label, pid in label_pids.items()
                     if (listener := listener_pids.get(pid))}
    agents_dir = Path.home() / "Library" / "LaunchAgents"
    for plist_path in sorted(agents_dir.glob("*.plist")):
        stats["plists"] += 1
        label = plist_path.stem
        if label.startswith(VENDOR_PREFIXES):
            stats["vendor_skipped"] += 1
            continue
        try:
            plist = plistlib.loads(plist_path.read_bytes())
        except Exception:
            stats["unreadable"] += 1
            records.append(_record(label, "launchd", str(plist_path), "needs_review", None, "review",
                                   "plist unreadable"))
            continue
        records.append(_classify_launchd(label, plist_path, plist, stats, corroboration))
    return records, stats


def _plist_facts(plist: dict) -> dict:
    """Pure extraction of classification-relevant plist fields."""
    watch = plist.get("WatchPaths")
    devices = plist.get("WatchDevices") or plist.get("DeviceAttach")
    keepalive = plist.get("KeepAlive")
    return {
        "watched_paths": list(watch) if watch else [],
        "sockets": bool(plist.get("Sockets")),
        "devices": bool(devices),
        "keepalive_unconditional": keepalive is True,
        "keepalive_conditional": isinstance(keepalive, dict),
        "calendar": bool(plist.get("StartCalendarInterval")),
        "interval": bool(plist.get("StartInterval")),
    }


def _listener_pids(out: str | None = None) -> dict[int, str]:
    """pid -> listening socket description, from lsof (OS corroboration).
    Pass `out` to exercise the parser against captured output."""
    if out is None:
        try:
            out = subprocess.run(
                ["lsof", "-nP", "-iTCP", "-sTCP:LISTEN", "-F", "pn"],
                capture_output=True, text=True, timeout=15,
            ).stdout
        except Exception:
            return {}
    listeners: dict[int, str] = {}
    pid = None
    for line in out.splitlines():
        tag, val = line[:1], line[1:]
        if tag == "p":
            pid = int(val) if val.isdigit() else None
        elif tag == "n" and pid is not None:
            listeners.setdefault(pid, val)
    return listeners


def _label_pids(out: str | None = None) -> dict[str, int]:
    """launchd label -> running pid, from `launchctl list` (PID, Status, Label).
    Pass `out` to exercise the parser against captured output."""
    if out is None:
        try:
            out = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=15).stdout
        except Exception:
            return {}
    pids: dict[str, int] = {}
    for line in out.splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].isdigit() and int(parts[0]) > 0:
            pids[parts[2]] = int(parts[0])
    return pids


def _classify_launchd(label: str, plist_path: Path, plist: dict, stats: dict,
                      corroboration: dict[str, str] | None = None) -> dict:
    f = _plist_facts(plist)
    corroboration = corroboration or {}
    plist_resource = f["watched_paths"] or f["sockets"] or f["devices"]
    scheduled = f["calendar"] or f["interval"]
    listener = corroboration.get(label)

    if plist_resource and scheduled:
        stats["needs_review"] += 1
        return _record(label, "launchd", str(plist_path), "needs_review", None, "review",
                       "plist has both a held resource and schedule triggers — contradiction, human must decide")
    if plist_resource:
        if f["sockets"]:
            kind, detail = "listening_socket", "Sockets declared in plist"
        elif f["watched_paths"]:
            kind, detail = "watched_directory", f"WatchPaths: {f['watched_paths'][:2]}"
        else:
            kind, detail = "hardware_connection", "device watch declared in plist"
        return _resident(label, plist_path, kind, detail, stats)
    if listener and not scheduled:
        return _resident(label, plist_path, "listening_socket",
                         f"OS corroboration: running process holds listener {listener}", stats)
    if scheduled:
        note = ("schedule trigger; resource not provable from plist — standard verdict is Kestra + "
                "Pydantic AI (failure-restart KeepAlive conditions are absorbed by Kestra retry policy)"
                if f["keepalive_conditional"] else
                "schedule trigger without resident markers — standard verdict is Kestra + Pydantic AI")
        stats["periodic"] += 1
        return _record(label, "launchd", str(plist_path), "periodic", {}, "move", note,
                       "kestra_pydantic")
    if f["keepalive_unconditional"]:
        stats["needs_review"] += 1
        return _record(label, "launchd", str(plist_path), "needs_review", None, "review",
                       "KeepAlive=true proves restart policy, not a held resource; no plist resource, no running listener — binary test unresolved, inspect the executable")
    stats["needs_review"] += 1
    return _record(label, "launchd", str(plist_path), "needs_review", None, "review",
                   "no schedule, no held resource, no KeepAlive lifetime — manual/oneshot semantics, human must decide")


def _resident(label: str, plist_path: Path, kind: str, detail: str, stats: dict) -> dict:
    evidence = {"resident_service": {"resource_kind": kind, "resource_detail": detail}}
    try:
        expected = select_framework(evidence)["framework"]
    except ToolSelectionBlock:
        stats["needs_review"] += 1
        return _record(label, "launchd", str(plist_path), "needs_review", evidence, "review",
                       "evidence rejected by decision table")
    stats["resident"] += 1
    return _record(label, "launchd", str(plist_path), "resident", evidence, "keep",
                   "source-proven resident service; stays on launchd", expected)


def _record(job_id, source, origin, job_class, evidence, action, note, expected=None):
    try:
        modified = Path(origin).stat().st_mtime
        modified_at = datetime.fromtimestamp(modified, timezone.utc).isoformat()
        provenance = {"path": origin, "field": "stat.st_mtime", "value": modified}
    except OSError:
        modified_at, provenance = None, None
    return {
        "job_id": job_id,
        "source": source,
        "origin": origin,
        "modified_at": modified_at,
        "modified_at_source": provenance,
        "class": job_class,
        "evidence": evidence,
        "expected_framework": expected,
        "action": action,
        "note": note,
    }


def _hermes_summary() -> tuple[list[dict], dict]:
    home = Path.home() / ".hermes"
    # Installed cron/jobs.py resolves get_hermes_home()/cron/jobs.json per profile.
    paths = [home / "cron" / "jobs.json", *sorted((home / "profiles").glob("*/cron/jobs.json"))]
    records, sources = [], []
    states: dict[str, int] = {}
    total = 0
    for path in paths:
        if not path.exists():
            sources.append({"path": str(path), "status": "missing"})
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        jobs = raw.get("jobs", []) if isinstance(raw, dict) else raw
        if not isinstance(jobs, list) or any(not isinstance(j, dict) for j in jobs):
            raise ValueError(f"Invalid Hermes job registry: {path}")
        total += len(jobs)
        sources.append({"path": str(path), "status": "scanned", "total": len(jobs)})
        profile = "root" if path.parent.parent == home else path.parent.parent.name
        for job in jobs:
            state = job.get("state") or "unknown"
            states[state] = states.get(state, 0) + 1
            if not job.get("enabled") or state in ("retired", "dead", "disposed"):
                continue
            records.append(_record(
                f"hermes:{profile}:{job['id']}", "hermes_cron", str(path),
                "needs_review", None, "review",
                "enabled Hermes job; prompt/script classification and launcher wiring require review",
            ))
    return records, {
        "status": "scanned" if any(s["status"] == "scanned" for s in sources) else "missing",
        "sources": sources, "total": total, "enabled": len(records),
        "states": dict(sorted(states.items())),
    }


def build_ledger() -> dict:
    launchd_records, launchd_stats = _launchd_jobs()
    hermes_records, hermes_summary = _hermes_summary()
    jobs = launchd_records + hermes_records
    unresolved = sorted(r["job_id"] for r in jobs if r["action"] == "review")
    return {
        "schema": "rig.d85.estate-ledger.v1",
        "generated_at": _now(),
        "surfaces": {
            "launchd": {"status": "scanned", **launchd_stats},
            "hermes_cron": hermes_summary,
            "kestra": {
                "status": "declared_unreachable",
                "declared_flows": 27,
                "source": USER_TABLE_SOURCE,
            },
            "temporal": {
                "status": "declared_unreachable",
                "declared_schedules": 4,
                "source": USER_TABLE_SOURCE,
            },
            "orca": {
                "status": "declared_unreachable",
                "declared_automations": 11,
                "source": USER_TABLE_SOURCE,
            },
        },
        "jobs": jobs,
        "unresolved": unresolved,
        "unresolved_count": len(unresolved),
    }


def main() -> int:
    ledger = build_ledger()
    if "--write" in sys.argv:
        out = Path(__file__).resolve().parent / "authority" / "standards" / "estate_ledger.v1.json"
        out.write_text(json.dumps(ledger, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        print(f"wrote {out} ({len(ledger['jobs'])} jobs, {ledger['unresolved_count']} unresolved)")
    else:
        print(json.dumps(ledger["surfaces"], indent=2))
        print(f"jobs={len(ledger['jobs'])} unresolved={ledger['unresolved_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
