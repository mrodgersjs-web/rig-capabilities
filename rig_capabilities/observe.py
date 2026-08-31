"""Observability: local traces always; Langfuse when configured.

Every pack/rate decision writes `.context/traces.jsonl`. If
LANGFUSE_HOST + LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY are set, the
same event is POSTed to Langfuse `/api/public/ingestion`. Missing config
or a failed POST is recorded in `.context/langfuse-last-error.json` and
`status()` reports `langfuse: false` — never pretended live.

This host had no Langfuse container at build time; local JSONL is the
source of truth until keys exist.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _ctx(repo) -> Path:
    d = Path(repo.root) / ".context"
    d.mkdir(exist_ok=True)
    return d


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def config_from_env(repo=None) -> dict:
    user = {}
    if repo is not None:
        try:
            user = (repo.config() or {}).get("observe") or {}
        except Exception:
            user = {}
    host = (os.environ.get("LANGFUSE_HOST")
            or os.environ.get("LANGFUSE_BASEURL")
            or user.get("langfuse_host") or "").rstrip("/")
    public = os.environ.get("LANGFUSE_PUBLIC_KEY") or user.get("public_key") or ""
    secret = os.environ.get("LANGFUSE_SECRET_KEY") or user.get("secret_key") or ""
    return {"host": host, "public_key": public, "secret_key": secret,
            "configured": bool(host and public and secret)}


def _persist_error(repo, error: str) -> None:
    rec = {"ts": _now(), "error": error}
    (_ctx(repo) / "langfuse-last-error.json").write_text(json.dumps(rec, indent=1))


def _post_langfuse(cfg: dict, event: dict) -> tuple[bool, str]:
    url = cfg["host"] + "/api/public/ingestion"
    token = base64.b64encode(f"{cfg['public_key']}:{cfg['secret_key']}".encode()).decode()
    body = json.dumps({
        "batch": [{
            "id": str(uuid.uuid4()),
            "type": "trace-create",
            "timestamp": event["ts"],
            "body": {
                "id": event["id"],
                "name": event["name"],
                "input": event.get("input"),
                "output": event.get("output"),
                "metadata": event.get("metadata") or {},
            },
        }]
    }).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Authorization": f"Basic {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "rig-capabilities-observe/5"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            r.read()
        return True, ""
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"{type(exc).__name__}: {exc}"


def trace(repo, name: str, *, input=None, output=None, metadata=None) -> dict:
    event = {
        "id": str(uuid.uuid4()),
        "ts": _now(),
        "name": name,
        "input": input,
        "output": output,
        "metadata": metadata or {},
    }
    with (_ctx(repo) / "traces.jsonl").open("a") as f:
        f.write(json.dumps(event) + "\n")
    cfg = config_from_env(repo)
    if cfg["configured"]:
        ok, err = _post_langfuse(cfg, event)
        event["langfuse"] = ok
        if not ok:
            _persist_error(repo, err)
            event["langfuse_error"] = err
    else:
        event["langfuse"] = False
    return event


def status(repo) -> dict:
    cfg = config_from_env(repo)
    traces = _ctx(repo) / "traces.jsonl"
    n = 0
    if traces.exists():
        n = sum(1 for line in traces.read_text().splitlines() if line.strip())
    err = None
    ep = _ctx(repo) / "langfuse-last-error.json"
    if ep.exists():
        try:
            err = json.loads(ep.read_text())
        except json.JSONDecodeError:
            err = {"error": "unreadable"}
    reachable = False
    if cfg["configured"]:
        try:
            req = urllib.request.Request(
                cfg["host"] + "/api/public/health",
                headers={"User-Agent": "rig-capabilities-observe/5"})
            with urllib.request.urlopen(req, timeout=3) as r:
                reachable = r.status < 500
        except (urllib.error.URLError, TimeoutError, OSError):
            reachable = False
    return {
        "langfuse_configured": cfg["configured"],
        "langfuse_host": cfg["host"] or None,
        "langfuse_reachable": reachable,
        "local_traces": n,
        "last_error": err,
    }
