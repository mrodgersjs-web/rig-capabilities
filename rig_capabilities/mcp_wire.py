"""Wire the rig-capabilities MCP server into the harnesses that lack it.

Four harnesses read four different config dialects. This module writes one entry,
in each dialect, from one spec:

    command = <the python that boots server.py>
    args    = [<repo>/server.py]

Shapes are copied from live configs and vendor docs, not invented:
  cursor    ~/.cursor/mcp.json            mcpServers.<name>.{command,args}   (JSON)
  gemini    ~/.gemini/settings.json       mcpServers.<name>.{command,args}   (JSON)
  opencode  ~/.config/opencode/opencode.json  mcp.<name>.{command[],type,enabled}
  goose     ~/.config/goose/config.yaml   extensions.<name>.{type,name,enabled,cmd,args}

Like `model_route`, every projection is a PURE text -> text function so the whole
behaviour is testable without touching a real config: `plan()` returns diffs and
changes nothing, and `apply()` refuses to run without a Gate-D approval that names
each target it is allowed to write. A `check` on a wired target is `already_wired`,
so the command is idempotent by construction rather than by luck.

Stdlib only. RIG_MCP_WIRE_TARGETS=<dir> redirects every target into one directory
(name -> <dir>/<name>) for tests, exactly as RIG_ROUTE_TARGETS does for model_route.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SERVER = REPO / "server.py"
PYTHON = os.environ.get("RIG_MCP_PYTHON") or \
    "/Users/rig128gb/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3"
ENTRY_NAME = "rig-capabilities"
GATE_D_ACTION = "mcp-wire"
ENGINE_VERSION = "1.0.0"

# Configs that already carry the server (proof that the entry works, and the source
# of the launch spec above). Never written here.
ALREADY_WIRED = ("claude:~/.claude.json", "codex:~/.codex/config.toml",
                 "hermes:~/.hermes/config.yaml", "omp:~/.omp/agent/mcp.json")


class WireGateError(Exception):
    """Refusal to write. Always raised before any byte is touched."""


def targets_root() -> Path | None:
    raw = (os.environ.get("RIG_MCP_WIRE_TARGETS") or "").strip()
    return Path(raw).expanduser() if raw else None


def _target(name: str, live: Path) -> Path:
    root = targets_root()
    return (root / name) if root else live


def proof_root() -> Path:
    raw = (os.environ.get("RIG_PROOF_ROOT") or "").strip()
    return Path(raw).expanduser() if raw else (Path.home() / ".rig" / "proof")


def gate_d_path(run_id: str) -> Path:
    return proof_root() / f"gate-d-{run_id}.json"


def targets() -> list[tuple[str, Path]]:
    return [("cursor", _target("cursor", Path.home() / ".cursor" / "mcp.json")),
            ("gemini", _target("gemini", Path.home() / ".gemini" / "settings.json")),
            ("opencode", _target("opencode",
                                 Path.home() / ".config" / "opencode" / "opencode.json")),
            ("goose", _target("goose", Path.home() / ".config" / "goose" / "config.yaml"))]


DIALECT = {"cursor": "json", "gemini": "json", "opencode": "json-mcp", "goose": "yaml"}
CONTAINER = {"cursor": "mcpServers", "gemini": "mcpServers",
             "opencode": "mcp", "goose": "extensions"}


# --------------------------------------------------------------------------
# entry bodies, in each dialect's own key order
# --------------------------------------------------------------------------
def entry_json(target: str, indent: int) -> list[str]:
    pad = " " * indent
    keys = [("command", f'"{PYTHON}"'),
            ("args", f'["{SERVER}"]')]
    if target == "opencode":
        keys = [("command", f'["{PYTHON}", "{SERVER}"]'),
                ("type", '"local"'), ("enabled", "true")]
    body = [f'{pad}  "{k}": {v}' for k, v in keys]
    for i in range(len(body) - 1):        # every key but the last needs a separator
        body[i] += ","
    return [f'{pad}"{ENTRY_NAME}": {{'] + body + [f"{pad}}}"]


def entry_yaml(indent: int) -> list[str]:
    """goose stdio extension, in the field order of the vendor config-files doc."""
    pad = " " * indent
    return [f"{pad}{ENTRY_NAME}:",
            f"{pad}  type: stdio",
            f"{pad}  name: {ENTRY_NAME}",
            f"{pad}  enabled: true",
            f"{pad}  cmd: {PYTHON}",
            f'{pad}  args: ["{SERVER}"]',
            f"{pad}  env_keys: []",
            f"{pad}  envs: {{}}",
            f"{pad}  timeout: 300"]


def entry_lines(target: str, indent: int) -> list[str]:
    return entry_yaml(indent) if DIALECT[target] == "yaml" else entry_json(target, indent)


# --------------------------------------------------------------------------
# locating the container and its children, in both dialects
# --------------------------------------------------------------------------
def _open_line(lines: list[str], key: str, yaml_dialect: bool) -> int:
    """Index of the line that opens `key`'s mapping, or -1.

    JSON reads `  "mcpServers": {`; YAML reads `extensions:` at column zero. A YAML
    key with an inline map (`extensions: {}`) counts as openable only when the braces
    are not already closed on that line, which for these four files they never are.
    """
    json_pat = f'"{key}":'
    yaml_pat = f"{key}:"
    for i, raw in enumerate(lines):
        s = raw.strip()
        if yaml_dialect:
            if s == yaml_pat or s.startswith(yaml_pat + " "):
                return i
        elif s.startswith(json_pat) and (s.rstrip().endswith("{")
                                         or s.rstrip().endswith("{}")):
            # `"mcpServers": {}` is an empty-but-present container: openable, and the
            # code path that inserts no trailing comma is exactly this one.
            return i
    return -1


def _child_indent(lines: list[str], open_idx: int) -> int:
    """Indent of the container's first existing child, or open-line indent + 2.

    Matching the file's own child indent is what keeps a one-line insertion from
    landing as a sibling of the container instead of a member of it.
    """
    for raw in lines[open_idx + 1:]:
        if raw.strip():
            return len(raw) - len(raw.lstrip(" "))
    return (len(lines[open_idx]) - len(lines[open_idx].lstrip(" "))) + 2


def has_entry(target: str, text: str) -> bool:
    """Is ENTRY_NAME already a direct child of the container?"""
    lines = text.splitlines()
    is_yaml = DIALECT[target] == "yaml"
    oi = _open_line(lines, CONTAINER[target], is_yaml)
    if oi < 0:
        return False
    ci = _child_indent(lines, oi)
    own = len(lines[oi]) - len(lines[oi].lstrip(" "))
    prefixed = (f"{ENTRY_NAME}:", f'"{ENTRY_NAME}":')
    for raw in lines[oi + 1:]:
        if not raw.strip():
            continue
        ind = len(raw) - len(raw.lstrip(" "))
        if raw.strip().startswith(prefixed) and ind == ci:
            return True
        if ind <= own and not raw.strip().startswith((",", "]", "}")):
            return False          # container closed before our key appeared
    return False


def project(target: str, text: str) -> tuple[str, list[dict]]:
    """Return (new_text, actions). Pure: never touches the filesystem."""
    if target not in DIALECT:
        raise WireGateError(f"unknown_target:{target}")
    is_yaml = DIALECT[target] == "yaml"
    lines = text.splitlines()
    key = CONTAINER[target]
    oi = _open_line(lines, key, is_yaml)
    if oi < 0:
        return text, [{"target": target, "action": "container_missing",
                       "detail": f'no "{key}" container found; refusing to guess where '
                                 "to create one"}]
    if has_entry(target, text):
        return text, [{"target": target, "action": "already_wired"}]
    own = len(lines[oi]) - len(lines[oi].lstrip(" "))
    head = lines[oi].rstrip()
    inline_empty = head.endswith("{}")
    if inline_empty:
        # `"mcpServers": {}` opens AND closes on this line. Inserting after it would
        # land the entry outside the braces — a sibling of the container, silently
        # unread by the harness. So the line is rewritten to stay open and its own
        # closer is re-emitted after the entry, at the container's indent.
        ci = own + 2
        body = entry_lines(target, ci)
        out = (lines[:oi] + [head[:-1]] + body + [" " * own + "}"] + lines[oi + 1:])
        return "\n".join(out) + ("\n" if text.endswith("\n") else ""), \
            [{"target": target, "action": "wire", "entry": ENTRY_NAME, "indent": ci,
              "container_line": oi + 1, "container_nonempty": False,
              "container_reopened": True, "trailing_comma": False}]
    ci = _child_indent(lines, oi)
    body = entry_lines(target, ci)
    # A comma after the block is needed only when a real sibling follows the open line;
    # `"mcpServers": {}` was handled above, so a closer here is the container's last
    # child line and putting a comma on our block would be invalid JSON.
    nonempty = False
    for raw in lines[oi + 1:]:
        if raw.strip():
            nonempty = raw.strip() not in ("}", "},")
            break
    comma = (not is_yaml) and nonempty
    if comma:
        body[-1] = body[-1] + ","
    out = lines[:oi + 1] + body + lines[oi + 1:]
    return "\n".join(out) + ("\n" if text.endswith("\n") else ""), \
        [{"target": target, "action": "wire", "entry": ENTRY_NAME, "indent": ci,
          "container_line": oi + 1, "container_nonempty": nonempty,
          "trailing_comma": comma}]


# --------------------------------------------------------------------------
# plan / apply / verify
# --------------------------------------------------------------------------
def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp-rig-wire")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _backup(path: Path) -> Path:
    """Copy the pre-write config into the repo's gitignored .context, not next to it."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = REPO / ".context" / "mcp-wire-backups"
    d.mkdir(parents=True, exist_ok=True)
    dest = d / f"{path.parent.name}-{path.name}-{stamp}"
    shutil.copy2(path, dest)
    return dest


def _diff(before: str, after: str, path: str) -> str:
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile=path + ":before", tofile=path + ":after"))


def plan() -> dict:
    """Read-only: every target's state, the diff a write would cause, and JSON validity."""
    rows = []
    for name, path in targets():
        row = {"target": name, "path": str(path), "dialect": DIALECT[name],
              "exists": path.is_file()}
        if not path.is_file():
            row.update(state="missing_file", actions=["cannot_read"])
            rows.append(row)
            continue
        before = path.read_text(encoding="utf-8")
        try:
            after, actions = project(name, before)
        except WireGateError as exc:
            row.update(state=str(exc), actions=[])
            rows.append(row)
            continue
        state = actions[0]["action"] if actions else "noop"
        if state == "wire" and DIALECT[name] != "yaml":
            try:
                json.loads(after)
                row["json_valid_after"] = True
            except json.JSONDecodeError as exc:
                state = "invalid_json_refused"
                after = before
                row["json_valid_after"] = False
                row["detail"] = str(exc)
        row.update(state=state, actions=[a["action"] for a in actions],
                   sha_before=_sha(before), sha_after=_sha(after),
                   changes=before != after,
                   diff=_diff(before, after, str(path)) if before != after else "")
        rows.append(row)
    return {"schema": "rig.mcp-wire-plan.v1", "engine": ENGINE_VERSION,
            "entry": ENTRY_NAME, "launch": {"command": PYTHON, "args": [str(SERVER)]},
            "already_wired_elsewhere": list(ALREADY_WIRED),
            "targets": rows,
            "writable": [r["target"] for r in rows if r.get("changes")],
            "blocked": [{"target": r["target"], "state": r["state"]}
                        for r in rows if not r.get("changes")]}


def _gate_d(run_id: str, wanted: list[str]) -> dict:
    """Adjudicate the approval. Raises before anything is written.

    A config write has no budget, so the scope boundary is the target list: every
    target being written MUST be named in the approval. An approval for `cursor` does
    not buy `goose`, and a valid approval never extends to a target by silence.
    """
    if run_id is None or not str(run_id).strip():
        raise WireGateError("gate_d_required")
    path = gate_d_path(run_id)
    if not path.is_file():
        raise WireGateError(f"gate_d_missing:{path}")
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WireGateError(f"gate_d_unreadable:{exc.__class__.__name__}") from exc
    if not isinstance(rec, dict):
        raise WireGateError("gate_d_required")
    if str(rec.get("status") or "").upper() != "APPROVED":
        raise WireGateError("gate_d_not_approved")
    if str(rec.get("action") or "") != GATE_D_ACTION:
        raise WireGateError(f"gate_d_action_mismatch:{rec.get('action')}")
    allowed = [str(t) for t in (rec.get("targets") or [])]
    unknown = [t for t in wanted if t not in allowed]
    if unknown:
        raise WireGateError("gate_d_target_not_approved:" + ",".join(unknown))
    return {"run_id": str(run_id), "path": str(path), "action": GATE_D_ACTION,
            "approved_targets": allowed}


def apply(gate_d_run_id: str, targets_only: list[str] | None = None) -> dict:
    """Write only what the plan changed and the approval named. Backups first."""
    p = plan()
    wanted = targets_only or p["writable"]
    if not wanted:
        # Nothing pending is the STEADY STATE, not an error: an idempotent re-run of
        # a fully-wired fleet must say all_wired=true so callers exit 0. The
        # alternative is a permanent red signal on a healthy machine.
        return {"schema": "rig.mcp-wire-apply.v1", "written": [],
                "skipped": [b["target"] for b in p["blocked"]], "gate_d": None,
                "all_wired": all(r["state"] == "already_wired"
                                 for r in p["targets"] if r["exists"]),
                "note": "nothing to write"}
    # Authority first, capability second: an unapproved call must learn it is
    # unapproved, not that its target happens to be already wired.
    gate = _gate_d(gate_d_run_id, wanted)
    for t in wanted:
        if t not in p["writable"]:
            raise WireGateError(f"not_writable:{t}")
    by_name = {r["target"]: r for r in p["targets"]}
    written = []
    for t in wanted:
        row = by_name[t]
        path = Path(row["path"])
        after = path.read_text(encoding="utf-8")
        after, _ = project(t, after)
        bak = _backup(path)
        _atomic_write(path, after)
        verify = plan()
        state = {r["target"]: r["state"] for r in verify["targets"]}[t]
        written.append({"target": t, "path": str(path), "backup": str(bak),
                        "sha_before": row["sha_before"], "sha_after": row["sha_after"],
                        "state_after": state})
    return {"schema": "rig.mcp-wire-apply.v1", "gate_d": gate, "written": written,
            "all_wired": all(r["state"] == "already_wired"
                             for r in plan()["targets"] if r["exists"])}


def verify() -> dict:
    """Idempotency proof: a second plan must find nothing left to write."""
    p = plan()
    return {"schema": "rig.mcp-wire-verify.v1", "engine": ENGINE_VERSION,
            "wired": [r["target"] for r in p["targets"] if r["state"] == "already_wired"],
            "pending": [r["target"] for r in p["targets"] if r.get("changes")],
            "blocked": p["blocked"],
            "idempotent": not p["writable"]}
