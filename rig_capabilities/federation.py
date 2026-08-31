"""v4/v5 federation — local path + HTTP peers + per-agent workspaces.

config.json `federates`:
  {"label": "peer", "path": "/other/rig-capabilities"}
  {"label": "rig96", "url": "http://192.168.x.x:8765"}

URL peers GET `/index.json` (fallback `/public-catalog.json`). Timeout 8s.
A failed fetch is skipped and recorded in `.context/federation-last-error.json`.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_HTTP_TIMEOUT = 8


def _record_error(repo, label: str, error: str) -> None:
    d = Path(repo.root) / ".context"
    d.mkdir(exist_ok=True)
    rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "label": label, "error": error}
    (d / "federation-last-error.json").write_text(json.dumps(rec, indent=1))


def _normalize(assets: list, label: str, origin: str) -> list:
    out = []
    for a in assets:
        if not isinstance(a, dict) or not a.get("id"):
            continue
        b = dict(a)
        b["source"] = f"fed:{label}"
        b["installable"] = False
        b["federated_from"] = origin
        b.setdefault("abs_path", "")
        out.append(b)
    return out


def _from_path(fed: dict, self: Path) -> list:
    root = Path(fed["path"]).expanduser().resolve()
    if root == self:
        return []
    idx = root / ".index.json"
    if not idx.exists():
        return []
    try:
        doc = json.loads(idx.read_text())
    except (json.JSONDecodeError, OSError):
        return []
    return _normalize(doc.get("assets") or [], str(fed["label"]), str(root))


def _from_url(repo, fed: dict) -> list:
    base = str(fed["url"]).rstrip("/")
    label = str(fed["label"])
    headers = {"Accept": "application/json",
               "User-Agent": "rig-capabilities-federation/5"}
    tok = (fed.get("token") or os.environ.get("RIG_CAPABILITIES_FEDERATION_TOKEN") or "").strip()
    if tok:
        headers["Authorization"] = f"Bearer {tok}"
    last_err = ""
    for suffix in ("/index.json", "/public-catalog.json"):
        try:
            req = urllib.request.Request(base + suffix, headers=headers)
            with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
                doc = json.loads(r.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            last_err = f"{suffix}: {type(exc).__name__}: {exc}"
            continue
        assets = doc.get("assets") if isinstance(doc, dict) else None
        if isinstance(assets, list):
            return _normalize(assets, label, base)
        last_err = f"{suffix}: no assets list"
    _record_error(repo, label, last_err or "url fetch failed")
    return []


def federated_assets(repo) -> list:
    out = []
    self = Path(repo.root).resolve()
    for fed in repo.config().get("federates") or []:
        if not isinstance(fed, dict) or not fed.get("label"):
            continue
        if fed.get("path"):
            out.extend(_from_path(fed, self))
        elif fed.get("url"):
            out.extend(_from_url(repo, fed))
    return out


def workspace_dir(repo, agent: str) -> Path:
    d = Path(repo.root) / ".context" / "agents" / agent
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_pack(repo, agent: str | None, pack_id: str, intent: str) -> None:
    if not agent:
        return
    rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "pack": pack_id, "intent": intent}
    with (workspace_dir(repo, agent) / "log.jsonl").open("a") as f:
        f.write(json.dumps(rec) + "\n")
