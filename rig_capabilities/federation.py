"""v4 — local instance federation + per-agent workspaces.

Federation is path-based and honest: `config.json` `federates: [{label, path}]`
points at other rig-capabilities roots on this machine. Their `.index.json`
is merged read-only with `source = fed:<label>`. No network. A missing peer
index is skipped, not invented.

Workspaces: `.context/agents/<id>/log.jsonl` records every pack that agent
requested, so live queries can slice by requester.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def federated_assets(repo) -> list:
    out = []
    self = Path(repo.root).resolve()
    for fed in repo.config().get("federates") or []:
        if not isinstance(fed, dict) or not fed.get("label") or not fed.get("path"):
            continue
        root = Path(fed["path"]).expanduser().resolve()
        if root == self:
            continue
        idx = root / ".index.json"
        if not idx.exists():
            continue
        try:
            doc = json.loads(idx.read_text())
        except (json.JSONDecodeError, OSError):
            continue
        label = str(fed["label"])
        for a in doc.get("assets") or []:
            if not isinstance(a, dict) or not a.get("id"):
                continue
            b = dict(a)
            b["source"] = f"fed:{label}"
            b["installable"] = False
            b["federated_from"] = str(root)
            out.append(b)
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
