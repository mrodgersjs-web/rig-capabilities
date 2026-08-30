"""v3 — drift detection + auto-refresh.

The index is stale when any configured root (canonical capabilities/ or an
external_roots path) has a newer mtime than `.last_seen.json`. Pack and
search call `auto_refresh` so unattended agents don't serve a yesterday
index. Rebuild is skipped when nothing drifted.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_WALK_CAP = 8000
_SLACK = 1.0  # seconds; filesystem mtime granularity


def _tree_mtime(path: Path) -> float:
    if not path.exists():
        return 0.0
    try:
        newest = path.stat().st_mtime
    except OSError:
        return 0.0
    n = 0
    try:
        for f in path.rglob("*"):
            n += 1
            if n > _WALK_CAP:
                break
            try:
                m = f.stat().st_mtime
            except OSError:
                continue
            if m > newest:
                newest = m
    except OSError:
        pass
    return newest


def _roots(repo) -> list[dict]:
    rows = [{"label": "canonical", "path": str(repo.cap_root)}]
    for r in repo.config().get("external_roots") or []:
        p = r.get("path")
        if not p:
            continue
        rows.append({"label": r["label"], "path": os.path.expanduser(p)})
    return rows


def drift_report(repo) -> dict:
    last_p = Path(repo.root) / ".last_seen.json"
    last = {}
    if last_p.exists():
        try:
            last = json.loads(last_p.read_text())
        except json.JSONDecodeError:
            last = {}
    roots = []
    drifted = []
    for r in _roots(repo):
        p = Path(r["path"])
        mt = _tree_mtime(p)
        prev = float((last.get(r["label"]) or {}).get("mtime") or 0)
        d = bool(p.exists()) and mt > prev + _SLACK
        roots.append({"label": r["label"], "path": str(p), "exists": p.exists(),
                      "mtime": mt, "last_seen": prev, "drifted": d})
        if d:
            drifted.append(r["label"])
    idx = Path(repo.root) / ".index.json"
    return {
        "stale": bool(drifted) or not idx.exists(),
        "drifted": drifted,
        "roots": roots,
        "index_exists": idx.exists(),
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def mark_seen(repo, report: dict | None = None) -> None:
    report = report or drift_report(repo)
    payload = {r["label"]: {"mtime": r["mtime"]} for r in report["roots"]}
    payload["_checked_at"] = report.get("checked_at")
    p = Path(repo.root) / ".last_seen.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=1))
    tmp.replace(p)


def auto_refresh(repo) -> dict:
    """Rebuild the index iff drift_report says stale. Returns the report + flag."""
    rep = drift_report(repo)
    if not rep["stale"]:
        return {"refreshed": False, **rep}
    repo.build_index()
    mark_seen(repo, drift_report(repo))
    return {"refreshed": True, **rep}
