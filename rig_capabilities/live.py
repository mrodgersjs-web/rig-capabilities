"""Live-state layer: bind index entries to RUNTIME evidence.

Doctrine (audit finding #4, 2026-08-30): "exists on disk" never proves
"is running". The index says an asset is present; this module says whether
it is actually wired — a hook registered in settings.json, a skill installed
into a live harness root, a CLI on PATH, a service port actually bound by
the process that is supposed to own it.

Stdlib only. Every probe degrades to an honest unknown, never a fabricated
green: unknown-state == {"live": False, "state": "unknown"}.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import socket
import subprocess
import urllib.request
from pathlib import Path

HARNESS_LABELS = {"claude": "claude-skills", "codex": "codex-skills",
                  "hermes": "hermes-skills", "agents": "agents-skills"}

# named infra services bound by rig-capabilities doctrine. `ports` are the
# truth surface; `finger` is an HTTP path whose status proves identity, and
# `owner_regex` is what lsof's process column must look like.
SERVICES = [
    {"id": "temporal", "ports": [7233], "owner_regex": r"temporal",
     "finger": None},
    {"id": "prefect", "ports": [4200], "owner_regex": r"python|prefect",
     "finger": ("http://127.0.0.1:4200/api/version", r"[0-9]")},
    {"id": "langfuse", "ports": [3000], "owner_regex": r"langfuse",
     "finger": ("http://127.0.0.1:3000/api/public/health", r"[Oo][Kk]|status")},
    {"id": "kestra", "ports": [8080], "owner_regex": r"java|kestra",
     "finger": None},
]

_CLAUDE_SETTINGS = Path(os.path.expanduser("~/.claude/settings.json"))
_CLAUDE_ROOT = Path(os.path.expanduser("~/.claude"))


def _clamp_state(present: bool, wired: bool) -> dict:
    if not present:
        return {"live": False, "state": "absent"}
    if wired:
        return {"live": True, "state": "wired"}
    return {"live": False, "state": "dormant"}


# -- hook registration ------------------------------------------------------

def _claude_hook_commands() -> str:
    """Concatenated command strings of every registered Claude hook."""
    try:
        d = json.loads(_CLAUDE_SETTINGS.read_text())
    except (OSError, ValueError):
        return ""
    out: list[str] = []
    for ev in (d.get("hooks") or {}).values():
        for grp in ev or []:
            for h in grp.get("hooks") or []:
                out.append(str(h.get("command", "")))
    return "\n".join(out)


def hook_live(asset: dict, commands_blob: str) -> dict:
    stem = asset["id"]
    name = re.sub(r"\.(sh|py|ts|js|mjs)$", "", stem)
    wired = bool(name) and name in commands_blob
    return _clamp_state(True, wired)


def installed_in(asset: dict, roots: dict) -> dict:
    """Location-loaded kinds are 'wired' when a copy sits in a live harness
    install root. Check the roots directly — the index shadow-drops external
    duplicates of canonical ids, so it cannot answer this question."""
    kind = asset["kind"]
    found = []
    for harness, base in (roots.get(kind) or {}).items():
        if not base:
            continue
        b = Path(os.path.expanduser(base))
        stem = re.sub(r"\.(md|ya?ml|sh|py|toml|json)$", "", asset["id"])
        if kind == "skill":
            hit = (b / stem / "SKILL.md").exists()
        else:
            hit = any((b / asset["id"]).exists() for _ in [0]) or any(
                (b / f"{stem}{ext}").exists() for ext in (".md", ".yaml", ".yml",
                                                          ".sh", ".py", ".toml", ".json"))
        if hit:
            found.append(harness)
    return _clamp_state(True, bool(found)) | {"roots": sorted(found)}


# -- CLI presence -----------------------------------------------------------

def cli_live(asset: dict) -> dict:
    name = re.sub(r"\.(md|sh|py)$", "", asset["id"])
    found = shutil.which(name)
    return _clamp_state(True, bool(found)) | {"path": found}


# -- services ---------------------------------------------------------------

def _port_open(port: int, timeout: float = 0.4) -> bool:
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout)
        s.close()
        return True
    except OSError:
        return False


def _http_finger(url: str, rx: str, timeout: float = 1.2):
    try:
        body = urllib.request.urlopen(url, timeout=timeout).read(400).decode("replace", "replace")
    except Exception as exc:  # noqa: BLE001 — any failure is a non-match
        return {"ok": False, "detail": f"{type(exc).__name__}"}
    return {"ok": bool(re.search(rx, body)), "detail": body[:80]}


def _port_owner(port: int) -> str:
    try:
        out = subprocess.run(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN"],
                             capture_output=True, text=True, timeout=2)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    lines = out.stdout.splitlines()
    return lines[1].split()[0].lower() if len(lines) > 1 else ""


def service_state(svc: dict) -> dict:
    bound = [p for p in svc["ports"] if _port_open(p)]
    if not bound:
        return {"id": svc["id"], "live": False, "state": "down", "port": svc["ports"]}
    owner = _port_owner(bound[0])
    matches = bool(re.search(svc["owner_regex"], owner))
    finger = None
    if svc["finger"]:
        url, rx = svc["finger"]
        finger = _http_finger(url, rx)
    # identity holds if EITHER the owning process looks right OR an HTTP
    # fingerprint confirms it — a down/unreachable endpoint must not mark a
    # correctly-owned service "hijacked".
    identity = matches or (finger["ok"] if finger else False)
    state = "wired" if identity else "hijacked"  # port open but NOT this service
    return {"id": svc["id"], "live": bool(identity), "state": state,
            "port": bound, "owner": owner or "unknown",
            "identity_match": identity, "finger": finger}

# -- aggregate --------------------------------------------------------------

def live_status(repo, id: str | None = None, services: bool = True) -> dict:
    doc = repo.load_index()
    assets = doc["assets"]
    roots = repo.config().get("install_roots", {})
    commands_blob = _claude_hook_commands()
    targets = [a for a in assets if a["source"] == "canonical"
               and (id is None or a["id"] == id)]
    if id is not None and not targets:
        m = repo.resolve(id)
        targets = m[:1]
    rows = []
    for a in targets:
        kind = a["kind"]
        if kind == "hook":
            st = hook_live(a, commands_blob)
        elif kind == "command":
            st = cli_live(a)
        else:
            st = installed_in(a, roots)
        rows.append({"id": a["id"], "kind": kind, **st})
    out = {"generated_at": doc.get("generated_at"),
           "canonical_probed": len(rows), "assets": rows}
    if services:
        out["services"] = [service_state(s) for s in SERVICES]
    if id is not None and rows:
        out["summary"] = rows[0]
    return out
