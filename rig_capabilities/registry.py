"""Workstation-repository registry status.

Reads ~/Developer/rig-intelligence/registry/workstation-repositories.json
(the single source of truth for every repo on this workstation) and reports
the live state of each entry: visibility, expected_origin vs local origin,
last-push timestamp, drift, and the operator note.

Designed so an agent can answer "where is repo X? did the last push land?"
without scraping git/network on every call. Falls back to "registry not
found" gracefully — this file is informative, never load-bearing for
rig-capabilities itself.
"""
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_REGISTRY = Path.home() / "Developer" / "rig-intelligence" / "registry" / \
                   "workstation-repositories.json"


def _gh(repo: str, subpath: str) -> dict | None:
    """Call `gh api repos/{repo}/{subpath}` and return parsed JSON, or None.

    Returns None when (a) the subprocess fails/times out, (b) the body is not
    JSON, or (c) GitHub returned a non-2xx envelope ({"message":...,"status":"404"}).
    A trailing slash on the repo root causes a 404 — pass subpath="" for the
    repo metadata call.
    """
    try:
        url = f"repos/{repo}" + (f"/{subpath}" if subpath else "")
        out = subprocess.run(
            ["gh", "api", url],
            capture_output=True, text=True, timeout=30, check=True,
        )
        d = json.loads(out.stdout)
        if isinstance(d, dict) and d.get("message") and "documentation_url" in d:
            return None
        return d
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            json.JSONDecodeError):
        return None


def _local_origin(local_path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(local_path), "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10, check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return ""


def _git_head_ts(local_path: Path) -> str | None:
    """Author timestamp of HEAD in ISO 8601, or None."""
    try:
        out = subprocess.run(
            ["git", "-C", str(local_path), "log", "-1", "--format=%cI"],
            capture_output=True, text=True, timeout=10, check=True,
        )
        ts = out.stdout.strip()
        return ts or None
    except (subprocess.CalledProcessError, subprocess.TimeoutExceededError):
        return None


def load_registry(path: Path | str | None = None) -> list[dict]:
    p = Path(path or DEFAULT_REGISTRY)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text()).get("repositories", [])
    except json.JSONDecodeError:
        return []


def status_one(entry: dict, *, fetch: bool = False) -> dict:
    """Build a one-row status dict for a registry entry.

    `fetch=True` queries GitHub + git for live data; `fetch=False` returns
    the static fields only (cheap, no subprocess)."""
    rec: dict = {
        "id": entry.get("id"),
        "github": entry.get("github"),
        "expected_origin": entry.get("expected_origin"),
        "disposition": entry.get("disposition"),
        "write_enabled": bool(entry.get("write_enabled")),
        "write_mode": entry.get("write_mode"),
        "needs_operator_decision": entry.get("needs_operator_decision"),
        "reason": entry.get("reason"),
        "live": False,
    }
    if not fetch:
        return rec
    repo = entry.get("github")
    if not repo:
        rec["live_error"] = "no github slug"
        return rec

    meta = _gh(repo, "")
    if meta:
        rec["live"] = True
        rec["visibility"] = meta.get("visibility")
        rec["default_branch"] = meta.get("default_branch")
        rec["pushed_at"] = meta.get("pushed_at")
        rec["archived"] = bool(meta.get("archived"))
        rec["disabled"] = bool(meta.get("disabled"))
        rec["private"] = bool(meta.get("private"))

    lp = entry.get("local_path")
    if lp:
        local = Path(lp).expanduser()
        rec["local_path"] = str(local)
        rec["local_exists"] = local.exists()
        if local.exists():
            rec["local_origin"] = _local_origin(local)
            rec["local_head_at"] = _git_head_ts(local)
            exp = (entry.get("expected_origin") or "").rstrip("/")
            rec["origin_matches_expected"] = (
                rec.get("local_origin", "").rstrip("/") == exp
                if exp else None
            )
    return rec


def status(repo_filter: str | None = None, *,
           path: Path | str | None = None, fetch: bool = False) -> dict:
    """Build a status report for one id (or all entries).

    Returns: {"fetched": bool, "registry_path": str, "entries": [status_one, ...]}
    """
    entries = load_registry(path)
    if repo_filter:
        entries = [e for e in entries if e.get("id") == repo_filter
                   or e.get("github") == repo_filter
                   or repo_filter in (e.get("github") or "")]
    rows = [status_one(e, fetch=fetch) for e in entries]
    rp = str(Path(path or DEFAULT_REGISTRY))
    return {"fetched": fetch, "registry_path": rp,
            "registry_exists": Path(rp).exists(),
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "count": len(rows), "entries": rows}
