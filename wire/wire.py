#!/usr/bin/env python3
"""Wire the rig-capabilities MCP server into all five coding harnesses.

Harnesses: Claude Code, Codex, OMP, Hermes, Prime Agent — same target map and
managed-marker discipline as jake-pai-mcp/wire/wire.py.
Dry-run by default. --apply writes backups (<file>.bak-<ts> before first edit
per run). --verify re-reads every config and reports the live wiring.

Idempotent: JSON entries are replaced only when they differ; text blocks are
rewritten between RIG MANAGED markers. Re-running after `git pull` (or a repo
move) re-points every harness at this checkout.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SERVER = REPO / "server.py"
NAME = "rig-capabilities"
HOME = Path.home()

MARK_BEGIN = "<!-- BEGIN RIG CAPABILITIES MCP (managed) -->"
MARK_END = "<!-- END RIG CAPABILITIES MCP (managed) -->"
YAML_BEGIN = "  # BEGIN RIG CAPABILITIES MANAGED"
YAML_END = "  # END RIG CAPABILITIES MANAGED"


def _pick_python() -> str:
    """Stable interpreter: uv minor-symlink > Apple CLT python3 >= 3.9 > current."""
    candidates = [
        Path.home() / ".local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3",
        Path("/usr/bin/python3"),
    ]
    probe = "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"
    for c in candidates:
        if c.exists() and subprocess.run([str(c), "-c", probe]).returncode == 0:
            return str(c)
    return sys.executable or "/usr/bin/python3"


PY = _pick_python()
MD_BLOCK = f"""{MARK_BEGIN}

## Rig Capabilities (MCP server: `rig-capabilities`)

- **Before authoring ANY new skill, agent, hook, harness, loop, or command** (or recommending an install), call `capabilities_search` — it indexes this repo plus every installed harness root (~/.claude, ~/.codex, ~/.hermes, ~/.agents).
- **Canonicalize, then distribute:** new or vendored assets go into `~/Developer/rig-capabilities/capabilities/<kind>/` via `capability_add` (git-versioned), then reach a harness via `capability_install`. Canonical entries shadow same-named installs elsewhere — one owner per name.
- **Goal loops & the 56 goal harnesses**: your harness has a local copy under its `harnesses/` root (`~/.claude/harnesses`, `~/.codex/harnesses`, `~/.omp/harnesses`, `~/.prime/agent/harnesses`, `~/.hermes/jake/goal-harnesses`); compiled engine specs live in `~/Developer/rig-capabilities/out/harness-goalspecs/`. Pick one with `capabilities_route("goal harness <outcome>")`.
- **`/skill-upgrades`**: run the quality→pack→apply→verify upgrade flow — `capabilities_quality_report` for the weakest assets, then `capabilities_context_pack` for the target, then `rig-capabilities test <id>`. Installed as a command in Claude/Codex/OMP/agents and as the `/skill-upgrades` skill in Hermes.

{MARK_END}"""

_backed_up: set = set()


def backup(path: Path, apply: bool) -> None:
    if not apply or not path.exists() or path in _backed_up:
        return
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    shutil.copy2(path, path.with_name(f"{path.name}.bak-{ts}"))
    _backed_up.add(path)


def note(action: str, target: str) -> str:
    line = f"  [{action}] {target}"
    print(line)
    return line


# -- JSON mcpServers targets (claude, omp, prime) -----------------------------

def wire_json(path: Path, apply: bool, actions: list) -> None:
    label = str(path)
    if not path.exists():
        actions.append(note("skip", f"{label} — file absent"))
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        actions.append(note("FAIL", f"{label} — invalid JSON: {exc}"))
        return
    servers = data.setdefault("mcpServers", {})
    desired = {"command": PY, "args": [str(SERVER)]}
    current = servers.get(NAME)
    if current == desired:
        actions.append(note("ok", f"{label} — already wired"))
        return
    if not apply:
        actions.append(note("plan", f"{label} — set mcpServers[{NAME}]"))
        return
    backup(path, apply)
    servers[NAME] = desired
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    actions.append(note("wired", label))


# -- TOML target (codex) -------------------------------------------------------

def toml_block() -> str:
    return (f"# BEGIN RIG CAPABILITIES MANAGED\n"
            f"[mcp_servers.{NAME}]\n"
            f'command = "{PY}"\n'
            f"args = [\"{SERVER}\"]\n"
            f"# END RIG CAPABILITIES MANAGED\n")


def wire_toml(path: Path, apply: bool, actions: list) -> None:
    label = ".codex/config.toml"
    if not path.exists():
        actions.append(note("skip", f"{label} — file absent"))
        return
    text = path.read_text(encoding="utf-8")
    block = toml_block()
    pat = re.compile(r"# BEGIN RIG CAPABILITIES MANAGED\n.*?# END RIG CAPABILITIES MANAGED\n",
                     re.DOTALL)
    if pat.search(text):
        if pat.search(text).group(0) == block:
            actions.append(note("ok", f"{label} — already wired"))
            return
        if not apply:
            actions.append(note("plan", f"{label} — update managed block"))
            return
        backup(path, apply)
        text = pat.sub(block, text)
    else:
        if not apply:
            actions.append(note("plan", f"{label} — append managed block"))
            return
        backup(path, apply)
        text = text.rstrip("\n") + "\n\n" + block
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    actions.append(note("wired", label))


# -- YAML target (hermes) — managed block inside mcp_servers: ------------------

def yaml_block() -> str:
    return (f"{YAML_BEGIN}\n"
            f"  {NAME}:\n"
            f"    command: {PY}\n"
            f"    args:\n"
            f"      - {SERVER}\n"
            f"    enabled: true\n"
            f"{YAML_END}\n")


def wire_yaml(path: Path, apply: bool, actions: list) -> None:
    label = ".hermes/config.yaml"
    if not path.exists():
        actions.append(note("skip", f"{label} — file absent"))
        return
    text = path.read_text(encoding="utf-8")
    block = yaml_block()
    pat = re.compile(re.escape(YAML_BEGIN) + r"\n.*?" + re.escape(YAML_END) + r"\n",
                     re.DOTALL)
    if pat.search(text):
        if pat.search(text).group(0) == block:
            actions.append(note("ok", f"{label} — already wired"))
            return
        if not apply:
            actions.append(note("plan", f"{label} — update managed block"))
            return
        backup(path, apply)
        text = pat.sub(block, text)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
        actions.append(note("wired", label))
        return
    m = re.search(r"^mcp_servers:\s*$", text, re.MULTILINE)
    if not m:
        actions.append(note("FAIL", f"{label} — no mcp_servers: key found"))
        return
    if not apply:
        actions.append(note("plan", f"{label} — insert managed block under mcp_servers:"))
        return
    backup(path, apply)
    idx = m.end() + 1
    text = text[:idx] + block + text[idx:]
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    actions.append(note("wired", label))


# -- markdown instruction blocks -------------------------------------------------

def wire_md(path: Path, apply: bool, actions: list) -> None:
    label = str(path.relative_to(HOME)) if str(path).startswith(str(HOME)) else str(path)
    if not path.exists():
        actions.append(note("skip", f"{label} — file absent"))
        return
    text = path.read_text(encoding="utf-8")
    pat = re.compile(re.escape(MARK_BEGIN) + r".*?" + re.escape(MARK_END), re.DOTALL)
    if pat.search(text):
        if pat.search(text).group(0) == MD_BLOCK:
            actions.append(note("ok", f"{label} — block current"))
            return
        if not apply:
            actions.append(note("plan", f"{label} — refresh managed block"))
            return
        backup(path, apply)
        text = pat.sub(MD_BLOCK, text)
    else:
        if not apply:
            actions.append(note("plan", f"{label} — append managed block"))
            return
        backup(path, apply)
        text = text.rstrip("\n") + "\n\n" + MD_BLOCK + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)
    actions.append(note("wired", label))


# -- targets ---------------------------------------------------------------

def targets() -> list:
    return [
        ("claude", wire_json, HOME / ".claude.json"),
        ("claude", wire_md, HOME / ".claude" / "CLAUDE.md"),
        ("codex", wire_toml, HOME / ".codex" / "config.toml"),
        ("codex", wire_md, HOME / ".codex" / "AGENTS.md"),
        ("omp", wire_json, HOME / ".omp" / "agent" / "mcp.json"),
        ("hermes", wire_yaml, HOME / ".hermes" / "config.yaml"),
        ("prime-agent", wire_json, HOME / ".prime" / "agent" / "settings.json"),
        ("prime-agent", wire_md, HOME / ".prime" / "agent" / "AGENTS.md"),
    ]


# -- canonical commands ----------------------------------------------------

COMMAND_ROOTS = (HOME / ".claude" / "commands", HOME / ".codex" / "commands")
HOOK_ROOTS = (
    HOME / ".claude" / "hooks",
    HOME / ".codex" / "hooks",
    HOME / ".hermes" / "hooks",
    HOME / ".omp" / "hooks",
    HOME / ".prime" / "agent" / "hooks",
)


def command_sources() -> list:
    d = REPO / "capabilities" / "commands"
    return sorted(d.glob("*.md")) if d.exists() else []


def sync_commands(apply: bool, actions: list) -> None:
    for src in command_sources():
        text = src.read_text(encoding="utf-8")
        for root in COMMAND_ROOTS:
            dst = root / src.name
            label = str(dst.relative_to(HOME)) if str(dst).startswith(str(HOME)) else str(dst)
            if dst.exists() and dst.read_text(encoding="utf-8") == text:
                actions.append(note("ok", f"{label} — current"))
                continue
            if not apply:
                actions.append(note("plan", f"{label} — deliver {src.name}"))
                continue
            root.mkdir(parents=True, exist_ok=True)
            backup(dst, True)
            tmp = dst.with_suffix(".md.tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(dst)
            actions.append(note("wired", label))


def verify_commands() -> bool:
    srcs = command_sources()
    missing = [str(r / s.name) for s in srcs for r in COMMAND_ROOTS
               if not ((r / s.name).exists()
                       and (r / s.name).read_text(encoding="utf-8")
                       == s.read_text(encoding="utf-8"))]
    good = not missing
    status = "OK" if good else "MISSING"
    extra = f"  (e.g. {missing[0]})" if missing else ""
    print(f"  [{status}] commands     {len(srcs)} canonical in claude+codex{extra}")
    return good



def hook_sources() -> list:
    d = REPO / "capabilities" / "hooks"
    return sorted(d.glob("*.sh")) if d.exists() else []


def sync_hooks(apply: bool, actions: list) -> None:
    for src in hook_sources():
        text = src.read_text(encoding="utf-8")
        for root in HOOK_ROOTS:
            dst = root / src.name
            label = str(dst.relative_to(HOME)) if str(dst).startswith(str(HOME)) else str(dst)
            if dst.exists() and dst.read_text(encoding="utf-8") == text:
                actions.append(note("ok", f"{label} — current"))
                continue
            if not apply:
                actions.append(note("plan", f"{label} — deliver {src.name}"))
                continue
            root.mkdir(parents=True, exist_ok=True)
            backup(dst, True)
            tmp = dst.with_name(dst.name + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(dst)
            dst.chmod(0o755)
            actions.append(note("wired", label))


def verify_hooks() -> bool:
    srcs = hook_sources()
    missing = [str(r / s.name) for s in srcs for r in HOOK_ROOTS
               if not ((r / s.name).exists()
                       and (r / s.name).read_text(encoding="utf-8")
                       == s.read_text(encoding="utf-8"))]
    good = not missing
    status = "OK" if good else "MISSING"
    extra = f"  (e.g. {missing[0]})" if missing else ""
    print(f"  [{status}] hooks        {len(srcs)} canonical in claude+codex+hermes+omp+prime{extra}")
    return good



# -- verify -------------------------------------------------------------------

def verify() -> int:
    ok = True
    for harness, fn, path in targets():
        if fn is wire_md:
            good = path.exists() and MARK_BEGIN in path.read_text(encoding="utf-8")
        elif fn is wire_toml:
            good = path.exists() and "# BEGIN RIG CAPABILITIES MANAGED" in \
                path.read_text(encoding="utf-8")
        elif fn is wire_yaml:
            good = path.exists() and YAML_BEGIN in path.read_text(encoding="utf-8")
        else:
            good = False
            if path.exists():
                try:
                    good = path.read_text(encoding="utf-8").find(NAME) >= 0
                except OSError:
                    pass
        status = "OK" if good else "MISSING"
        print(f"  [{status}] {harness:<12} {path}")
        ok = ok and good
    cmd_ok = verify_commands()
    hook_ok = verify_hooks()
    # protocol self-test
    probe = subprocess.run(
        [PY, str(SERVER)],
        input='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n'
              '{"jsonrpc":"2.0","id":2,"method":"tools/list"}\n',
        capture_output=True, text=True, timeout=30)
    has_tools = '"capabilities_search"' in probe.stdout
    print(f"  [{'OK' if has_tools else 'FAIL'}] protocol   initialize+tools/list handshake")
    return 0 if (ok and cmd_ok and hook_ok and has_tools) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true", help="write changes")
    ap.add_argument("--verify", action="store_true", help="report live wiring")
    args = ap.parse_args()
    if args.verify:
        return verify()
    actions: list = []
    print(f"rig-capabilities wiring — {'APPLY' if args.apply else 'DRY RUN'} (server: {SERVER})")
    for harness, fn, path in targets():
        fn(path, args.apply, actions)
    sync_commands(args.apply, actions)
    sync_hooks(args.apply, actions)
    print(f"  {len([a for a in actions if 'wired' in a or 'plan' in a])} target(s) changed/planned")
    return 0


if __name__ == "__main__":
    sys.exit(main())
