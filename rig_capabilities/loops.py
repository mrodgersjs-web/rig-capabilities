"""rig-loop engine — Loop-Skill Contract v11.

A doctrine becomes a *loop-skill*: a skill directory carrying `loop.yaml`
(stages, deterministic gates, closing loop, kill switch, outward policy),
a `SKILL.md` narrative, and planted-failure `tests/cases.json`. This module
is the A1 (code-decides) runtime every harness hook calls:

  activate -> stage gates -> closing loop -> seal (ProofPacket) -> close

Hooks (`rig-loop hook <event>`) read one JSON payload on stdin — Claude Code /
Codex hook schema, or the normalized payload the pi extension and Hermes
handler send — and answer allow / deny / inject / block. With no active run
every hook is a silent no-op, so wiring the hooks globally costs nothing
until a loop-skill is in use.

Stdlib only. PyYAML is used when present (loop.yaml), otherwise loop.json.
State root: ~/.rig/state/loops (override: RIG_LOOP_STATE, used by tests).
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ENGINE_VERSION = "11.0.0"
SCHEMA = "rig.loop-skill.v11"
MARKER = "RIG_LOOP_MANAGED"
REPO = Path(__file__).resolve().parent.parent
HOME = Path.home()
CLI = REPO / "bin" / "rig-loop"
# Only `pass` completes a stage. A parked stage stays unmet after `resume` (a park is
# an honest pause, never a skip).
STAGE_OK = ("pass",)

HARNESSES = ("claude", "codex", "hermes", "omp", "prime-agent")
SKILL_ROOTS = {
    "canonical": REPO / "capabilities" / "skills",
    "claude": HOME / ".claude" / "skills",
    "codex": HOME / ".codex" / "skills",
    "hermes": HOME / ".hermes" / "skills",
    "omp": HOME / ".omp" / "agent" / "skills",
    "prime-agent": HOME / ".prime" / "agent" / "skills",
}
# Per-harness hook registration surface (json manifests, pi extensions, hermes hook dir).
HOOK_CONFIG = {
    "claude": HOME / ".claude" / "settings.json",
    "codex": HOME / ".codex" / "hooks.json",
    "hermes": HOME / ".hermes" / "hooks" / "rig-loop-gate",
    "omp": HOME / ".omp" / "agent" / "extensions" / "rig-loop-hooks.ts",
    "prime-agent": HOME / ".prime" / "agent" / "extensions" / "rig-loop-hooks.ts",
}
OMP_CONFIG = HOME / ".omp" / "agent" / "config.yml"
PROOF_DIR = HOME / ".rig" / "proof"
# `rig-loop wire --apply` links the CLI here. Module-level so tests can redirect it.
RIG_LOOP_LINK = HOME / ".rig" / "bin" / "rig-loop"

WRITE_TOOLS = {"write", "edit", "multiedit", "notebookedit", "apply_patch", "multi_edit",
               "str_replace_editor", "create_file"}
SHELL_TOOLS = {"bash", "shell", "run_command", "exec", "terminal", "execute_command"}

# Plan/spec/scratch locations always writable while a loop is active, regardless of stage.
DEFAULT_PLAN_GLOBS = [
    "*/docs/plans/*", "*/docs/superpowers/*", "*/.claude/plans/*", "*/plans/*",
    "/tmp/*", "/private/tmp/*", "*/HANDOFF.md", "*/BACKLOG.md", "*/INITIAL.md",
    "*/.rig/state/*", "*/scratchpad/*", "*.plan.md",
]
# Outward / irreversible shell patterns. Blocked unless the run carries a Gate-D approval.
# Pattern-based (best effort, not a sandbox): git/gh global options such as `-C dir`,
# `-c k=v`, `--git-dir=…` are tolerated between the binary and the subcommand.
_GIT_OPTS = (r"(?:\s+(?:-[Cc]|--git-dir|--work-tree|--namespace|--exec-path|--config-env)\s+\S+"
             r"|\s+--?[\w-]+(?:=\S+)?)*")
_GH_OPTS = r"(?:\s+(?:-R|--repo|--hostname)\s+\S+|\s+--?[\w-]+(?:=\S+)?)*"
DEFAULT_OUTWARD_PATTERNS = [
    rf"\bgit{_GIT_OPTS}\s+push\b",
    rf"\bgh{_GH_OPTS}\s+(pr\s+merge|release\s+create|repo\s+create|repo\s+delete)\b",
    r"\bvercel\b[^|;&]*(--prod|\bdeploy\b)",
    r"\bnpm\s+publish\b", r"\bdocker\s+push\b", r"\bkubectl\s+apply\b", r"\bterraform\s+apply\b",
    r"\bcurl\b(?![^|;&]*(localhost|127\.0\.0\.1))[^|;&]*-X\s*(POST|PUT|DELETE|PATCH)\b",
    r"\b(resend|instantly|sendgrid|twilio|postiz|mailgun)\b[^|;&]*\b(send|publish|post|blast)\b",
    r"\bstripe\b[^|;&]*\b(charge|payment|refund)\b",
    r"\baws\s+\S+\s+(deploy|create-|delete-|put-)\w*",
    r"\bgcloud\s+\S+\s+(deploy|create|delete)\b",
    r"\blaunchctl\s+(load|unload|bootstrap|bootout)\b",
]


# --------------------------------------------------------------------------- utils
def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def state_root() -> Path:
    p = Path(os.environ.get("RIG_LOOP_STATE") or (HOME / ".rig" / "state" / "loops")).expanduser()
    p.mkdir(parents=True, exist_ok=True)
    (p / "runs").mkdir(exist_ok=True)
    return p


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _load_yaml_or_json(text: str) -> dict:
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    except ImportError:
        pass
    return json.loads(text)


def _run_cmd(cmd: str, cwd: str | None, timeout: int = 60) -> dict:
    t0 = time.time()
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd or None, capture_output=True, text=True,
                           timeout=timeout)
        return {"cmd": cmd, "exit": r.returncode, "stdout": r.stdout[-2000:],
                "stderr": r.stderr[-2000:], "secs": round(time.time() - t0, 2)}
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "exit": 124, "stdout": "", "stderr": "timeout", "secs": timeout}
    except Exception as exc:  # noqa: BLE001
        return {"cmd": cmd, "exit": 127, "stdout": "", "stderr": str(exc), "secs": 0}


# --------------------------------------------------------------------------- specs
class SpecError(ValueError):
    pass


def find_spec_path(loop_id: str, roots: dict | None = None) -> Path | None:
    roots = roots or SKILL_ROOTS
    for root in roots.values():
        d = Path(root) / loop_id
        for name in ("loop.yaml", "loop.json"):
            p = d / name
            if p.exists():
                return p
    return None


def load_spec(loop_id_or_path: str) -> dict:
    p = Path(loop_id_or_path)
    if not p.exists() or p.is_dir():
        if p.is_dir():
            for name in ("loop.yaml", "loop.json"):
                if (p / name).exists():
                    p = p / name
                    break
        else:
            found = find_spec_path(loop_id_or_path)
            if not found:
                raise SpecError(f"no loop.yaml for '{loop_id_or_path}' in any skill root")
            p = found
    text = p.read_text()
    try:
        spec = _load_yaml_or_json(text)
    except Exception as exc:  # noqa: BLE001
        sib = p.with_suffix(".json")
        if sib.exists():
            spec = json.loads(sib.read_text())
        else:
            raise SpecError(f"cannot parse {p}: {exc} (no PyYAML? run: rig-loop compile {p.parent.name})")
    spec["_path"] = str(p)
    spec["_dir"] = str(p.parent)
    errs = validate_spec(spec)
    if errs:
        raise SpecError(f"{p}: " + "; ".join(errs))
    return spec


def validate_spec(spec: dict) -> list[str]:
    errs: list[str] = []
    if spec.get("schema") != SCHEMA:
        errs.append(f"schema must be {SCHEMA}")
    if not spec.get("id"):
        errs.append("id required")
    stages = spec.get("stages") or []
    if not stages:
        errs.append("at least one stage required")
    seen: set[str] = set()
    for st in stages:
        sid = st.get("id")
        if not sid:
            errs.append("stage without id")
            continue
        if sid in seen:
            errs.append(f"duplicate stage {sid}")
        seen.add(sid)
        for g in st.get("gate") or []:
            if g.get("type") not in GATE_TYPES:
                errs.append(f"stage {sid}: unknown gate type {g.get('type')}")
    cl = spec.get("closing_loop") or {}
    if cl and cl.get("to") and cl["to"] not in seen:
        errs.append("closing_loop.to must name a stage")
    ks = spec.get("kill_switch") or {}
    if not ks.get("max_iterations"):
        errs.append("kill_switch.max_iterations required (every loop needs a kill switch)")
    return errs


def list_specs(roots: dict | None = None) -> list[dict]:
    roots = roots or {"canonical": SKILL_ROOTS["canonical"]}
    out = []
    for label, root in roots.items():
        root = Path(root)
        if not root.is_dir():
            continue
        for d in sorted(root.iterdir()):
            for name in ("loop.yaml", "loop.json"):
                p = d / name
                if p.exists():
                    try:
                        s = load_spec(str(p))
                        out.append({"id": s["id"], "name": s.get("name"), "version": s.get("version"),
                                    "root": label, "path": str(p), "stages": [x["id"] for x in s["stages"]]})
                    except Exception as exc:  # noqa: BLE001
                        out.append({"id": d.name, "root": label, "path": str(p), "error": str(exc)})
                    break
    return out


# --------------------------------------------------------------------------- runs
def _run_dir(run_id: str) -> Path:
    return state_root() / "runs" / run_id


def _new_run_id(loop_id: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    salt = hashlib.sha1(f"{loop_id}{ts}{os.getpid()}{time.time()}".encode()).hexdigest()[:6]
    return f"{loop_id}-{ts}-{salt}"


def save_run(run: dict) -> None:
    run["updated_at"] = utc_now()
    _atomic_write(_run_dir(run["run_id"]) / "run.json", json.dumps(run, indent=2, sort_keys=True))


def load_run(run_id: str) -> dict | None:
    p = _run_dir(run_id) / "run.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:  # noqa: BLE001
        return None


def log_event(run: dict, kind: str, **data) -> None:
    rec = {"ts": utc_now(), "kind": kind, **data}
    d = _run_dir(run["run_id"])
    d.mkdir(parents=True, exist_ok=True)
    with open(d / "events.jsonl", "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    run["events"] = int(run.get("events", 0)) + 1


def _active_path() -> Path:
    return state_root() / "active.json"


def _read_active() -> dict:
    p = _active_path()
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:  # noqa: BLE001
            pass
    return {"by_cwd": {}, "latest": None}


def _write_active(a: dict) -> None:
    _atomic_write(_active_path(), json.dumps(a, indent=2, sort_keys=True))


def set_active(run: dict) -> None:
    a = _read_active()
    a["by_cwd"][run["cwd"]] = run["run_id"]
    a["latest"] = run["run_id"]
    _write_active(a)


def clear_active(run: dict) -> None:
    a = _read_active()
    for k, v in list(a["by_cwd"].items()):
        if v == run["run_id"]:
            del a["by_cwd"][k]
    if a.get("latest") == run["run_id"]:
        a["latest"] = next(iter(a["by_cwd"].values()), None)
    _write_active(a)


def _owns_cwd(run: dict, cwd: str | None) -> bool:
    if cwd is None:
        return True
    try:
        c = Path(cwd).resolve()
        return c == Path(run["cwd"]) or Path(run["cwd"]) in c.parents
    except Exception:  # noqa: BLE001
        return False


def find_active(cwd: str | None = None, run_id: str | None = None) -> dict | None:
    """Active run for this cwd (or nearest parent), else the latest active run.
    An explicit run_id still has to own the cwd — a hook can never be pointed at
    another directory's run."""
    if run_id:
        r = load_run(run_id)
        return r if r and r.get("status") == "active" and _owns_cwd(r, cwd) else None
    a = _read_active()
    if cwd:
        c = str(Path(cwd).resolve())
        while True:
            rid = a["by_cwd"].get(c)
            if rid:
                r = load_run(rid)
                if r and r.get("status") == "active":
                    return r
            parent = str(Path(c).parent)
            if parent == c:
                break
            c = parent
    # Fallback to the latest run ONLY when the caller gave no cwd — a hook firing in an
    # unrelated directory must never attach to someone else's run.
    if cwd is None and a.get("latest"):
        r = load_run(a["latest"])
        if r and r.get("status") == "active":
            return r
    return None


def detect_harness() -> str:
    """Best-effort builder family from the environment (used for GEV independence)."""
    env = os.environ
    if env.get("RIG_AGENT"):
        return env["RIG_AGENT"].lower()
    if env.get("CLAUDECODE") or env.get("CLAUDE_SESSION_ID") or env.get("CLAUDE_CODE_ENTRYPOINT"):
        return "claude"
    if env.get("CODEX_SANDBOX") or env.get("CODEX_HOME") or env.get("CODEX_THREAD_ID"):
        return "codex"
    if env.get("HERMES_HOME") or env.get("HERMES_SESSION_ID"):
        return "hermes"
    if env.get("PRIME_AGENT_HOME") or env.get("PRIME_AGENT_DIR"):
        return "prime-agent"
    if env.get("OMP_HOME") or env.get("OMP_AGENT_DIR") or env.get("PI_AGENT_DIR"):
        return "omp"
    return "unknown"


def activate(loop_id: str, cwd: str | None = None, intent: str = "", mode: str = "auto",
             harness: str = "", session_id: str = "", if_inactive: bool = False,
             parent_run_id: str | None = None) -> dict:
    spec = load_spec(loop_id)
    cwd = str(Path(cwd or os.getcwd()).resolve())
    if if_inactive:
        cur = find_active(cwd)
        if cur and cur["loop_id"] == loop_id:
            return cur
    modes = spec.get("modes") or {"auto": {}}
    if mode not in modes:
        raise SpecError(f"mode '{mode}' not in {sorted(modes)}")
    parent = None
    if parent_run_id:
        parent = load_run(parent_run_id)
        if not parent or parent.get("status") != "active":
            raise SpecError(f"parent run {parent_run_id} is not active")
        mx = int((parent.get("kill_switch") or {}).get("max_children", 12))
        if len(parent.get("children") or []) >= mx:
            raise SpecError(f"parent run already has {mx} children (kill switch max_children)")
    run_id = _new_run_id(spec["id"])
    d = _run_dir(run_id)
    (d / "artifacts").mkdir(parents=True, exist_ok=True)
    ks = spec.get("kill_switch") or {}
    run = {
        "schema": "rig.loop-run.v11",
        "run_id": run_id, "loop_id": spec["id"], "loop_version": spec.get("version"),
        "spec_path": spec["_path"], "mode": mode, "mode_opts": modes.get(mode) or {},
        "cwd": cwd, "harness": (harness or detect_harness()), "session_id": session_id, "intent": intent,
        "started_at": utc_now(), "updated_at": utc_now(), "status": "active",
        "stage_status": {}, "stage_artifacts": {}, "stage_score": {}, "stage_notes": {},
        "history": [], "counters": {}, "checks": [], "planted": [], "files_written": [],
        "drift": [], "iteration": 1, "stop_blocks": 0, "events": 0, "tool_calls": 0,
        "qr_passes": [], "verifications": [], "children": [], "parent_run_id": parent_run_id,
        "predicted": None,
        "gate_d": {"requested": None, "approved": False, "by": None, "at": None, "phrase": None},
        "proof": None, "kill_switch": {"max_iterations": int(ks.get("max_iterations", 3)),
                                        "max_wall_minutes": int(ks.get("max_wall_minutes", 240)),
                                        "max_stop_blocks": int(ks.get("max_stop_blocks", 2)),
                                        "max_tool_calls": int(ks.get("max_tool_calls", 800)),
                                        "max_children": int(ks.get("max_children", 12))},
        "coordinate": spec.get("coordinate"), "packet": spec.get("packet"),
    }
    save_run(run)
    log_event(run, "activate", loop=spec["id"], mode=mode, harness=run["harness"], intent=intent,
              parent=parent_run_id)
    save_run(run)
    if parent:
        parent.setdefault("children", []).append(run_id)
        log_event(parent, "child_start", child=run_id, intent=intent)
        save_run(parent)
    set_active(run)
    return run


def _restore_parent(run: dict) -> None:
    """When a child run leaves the active state, the parent becomes active for the cwd again."""
    pid = run.get("parent_run_id")
    if not pid:
        return
    parent = load_run(pid)
    if parent and parent.get("status") == "active":
        log_event(parent, "child_end", child=run["run_id"], status=run.get("status"))
        save_run(parent)
        set_active(parent)


def artifacts_dir(run: dict) -> Path:
    return _run_dir(run["run_id"]) / "artifacts"


def stage_by_id(spec: dict, sid: str) -> dict | None:
    for st in spec["stages"]:
        if st["id"] == sid:
            return st
    return None


def current_stage(run: dict, spec: dict) -> dict | None:
    for st in spec["stages"]:
        if run["stage_status"].get(st["id"]) not in STAGE_OK:
            return st
    return None


def progress(run: dict, spec: dict) -> tuple[int, int]:
    done = sum(1 for st in spec["stages"] if run["stage_status"].get(st["id"]) in STAGE_OK)
    return done, len(spec["stages"])


def wall_minutes(run: dict) -> float:
    try:
        t0 = datetime.strptime(run["started_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t0).total_seconds() / 60.0
    except Exception:  # noqa: BLE001
        return 0.0


# --------------------------------------------------------------------------- gates
def _resolve_artifact(run: dict, st: dict, path: str | None) -> Path:
    override = run["stage_artifacts"].get(st["id"])
    raw = override or path or st.get("artifact") or ""
    p = Path(os.path.expanduser(raw))
    if not p.is_absolute():
        p = artifacts_dir(run) / p
    return p


def _gate_file_exists(run, spec, st, g):
    p = _resolve_artifact(run, st, g.get("path"))
    return p.exists() and p.stat().st_size > 0, f"artifact {p}" + ("" if p.exists() else " missing")


def _gate_file_contains(run, spec, st, g):
    p = _resolve_artifact(run, st, g.get("path"))
    if not p.exists():
        return False, f"{p} missing"
    text = p.read_text(errors="replace")
    missing = [pat for pat in g.get("patterns", []) if not re.search(pat, text, re.M)]
    return (not missing), ("all patterns present" if not missing else f"missing in {p.name}: {missing}")


def _gate_regex(run, spec, st, g):
    p = _resolve_artifact(run, st, g.get("path"))
    if not p.exists():
        return False, f"{p} missing"
    ok = re.search(g["pattern"], p.read_text(errors="replace"), re.M) is not None
    return ok, (f"{p.name} matches /{g['pattern']}/" if ok else f"{p.name} lacks /{g['pattern']}/ — {g.get('hint','')}")


def _gate_regex_absent(run, spec, st, g):
    p = _resolve_artifact(run, st, g.get("path"))
    if not p.exists():
        return False, f"{p} missing"
    m = re.search(g["pattern"], p.read_text(errors="replace"), re.M)
    return m is None, ("clean" if m is None else f"{p.name} still contains /{g['pattern']}/: {m.group(0)!r} — {g.get('hint','')}")


def _gate_no_unanswered_blocking(run, spec, st, g):
    p = _resolve_artifact(run, st, g.get("path"))
    if not p.exists():
        return False, f"{p} missing"
    open_q = []
    for line in p.read_text(errors="replace").splitlines():
        if re.match(r"^\s*[-*]\s*\[BLOCKING\]", line, re.I) and not re.search(r"(ANSWER:|→|->)\s*\S", line):
            open_q.append(line.strip()[:120])
    run["counters"]["blocking_open"] = len(open_q)
    return (not open_q), ("no open BLOCKING questions" if not open_q else f"{len(open_q)} open BLOCKING: {open_q[:3]}")


def _gate_min_counter(run, spec, st, g):
    v = int(run["counters"].get(g["counter"], 0))
    return v >= int(g["min"]), f"{g['counter']}={v} (min {g['min']})"


def _gate_checks_green(run, spec, st, g):
    if len(run["checks"]) < int(g.get("min", 1)):
        return False, f"{len(run['checks'])} checks registered (min {g.get('min',1)}); add with: rig-loop check add \"<cmd>\""
    results = run_checks(run)
    red = [r for r in results if r["exit"] != 0]
    return (not red), ("all checks green" if not red else f"red: {[r['cmd'] for r in red]}")


def _children(run: dict) -> list[dict]:
    return [c for c in (load_run(cid) for cid in (run.get("children") or [])) if c]


def all_planted(run: dict) -> list[dict]:
    """A parent's evidence includes what its slice runs proved."""
    out = list(run["planted"])
    for c in _children(run):
        out.extend(c.get("planted") or [])
    return out


def all_files_written(run: dict) -> list[str]:
    out = list(run["files_written"])
    for c in _children(run):
        out.extend(f for f in (c.get("files_written") or []) if f not in out)
    return out


def _gate_planted_failure(run, spec, st, g):
    good = [p for p in all_planted(run) if p.get("red_ok") and p.get("green_ok")]
    return len(good) >= int(g.get("min", 1)), f"{len(good)} planted failures proven RED→GREEN (min {g.get('min',1)}, slices included)"


def proof_binding_ok(run: dict) -> tuple[bool, str]:
    """The sealed packet must still exist, hash-match, belong to this iteration, and every
    artifact it recorded must be byte-identical now. Anything else is a stale proof."""
    pr = run.get("proof") or {}
    if not pr.get("path"):
        return False, "not sealed — run: rig-loop seal"
    p = Path(pr["path"])
    if not p.exists():
        return False, f"ProofPacket missing: {p}"
    if pr.get("hash") != sha256_file(p):
        return False, f"ProofPacket altered since seal: {p}"
    if pr.get("iteration") != run.get("iteration"):
        return False, f"ProofPacket is from iteration {pr.get('iteration')} (now {run.get('iteration')}) — re-seal"
    try:
        packet = json.loads(p.read_text())
    except Exception as exc:  # noqa: BLE001
        return False, f"ProofPacket unreadable: {exc}"
    for sid, a in (packet.get("artifacts") or {}).items():
        ap = Path(a["path"])
        if not ap.exists():
            return False, f"artifact for stage {sid} deleted since seal: {ap}"
        if sha256_file(ap) != a["sha256"]:
            return False, f"artifact for stage {sid} changed since seal: {ap} — re-seal"
    return True, "ProofPacket sealed and bound " + str(p)


def _gate_sealed(run, spec, st, g):
    return proof_binding_ok(run)


def _gate_gate_d(run, spec, st, g):
    gd = run["gate_d"]
    return bool(gd.get("approved")), ("Gate-D approved by " + str(gd.get("by")) if gd.get("approved") else "Gate-D not approved — outward action needs Mike's typed APPROVE <run_id>")


def _gate_gate_d_requested(run, spec, st, g):
    gd = run["gate_d"]
    return bool(gd.get("requested")), ("Gate-D requested: " + str(gd.get("requested"))[:80] if gd.get("requested")
                                        else "no Gate-D request on record — rig-loop gate-d request --action \"<what>\"")


def _gate_cmd(run, spec, st, g):
    r = _run_cmd(g["command"], g.get("cwd") or run["cwd"], int(g.get("timeout", 60)))
    return r["exit"] == 0, f"`{g['command']}` exit {r['exit']} {r['stderr'][-160:].strip()}"


def _gate_stage_passed(run, spec, st, g):
    return run["stage_status"].get(g["stage"]) == "pass", f"stage {g['stage']} is {run['stage_status'].get(g['stage'],'unset')}"


def _gate_drift_within(run, spec, st, g):
    n = len(run["drift"])
    return n <= int(g.get("max", 10)), f"scope drift {n} file(s) outside declared spec (max {g.get('max',10)})"


def _gate_files_written_min(run, spec, st, g):
    n = len(all_files_written(run))
    return n >= int(g.get("min", 1)), f"{n} files written this run incl. slices (min {g.get('min',1)})"


def _gate_qr_dry(run, spec, st, g):
    passes = run.get("qr_passes") or []
    mn = int(g.get("min", 2))
    if len(passes) < mn:
        return False, f"{len(passes)} Q⇄R passes recorded (min {mn}); record each with: rig-loop qr pass --new-unknowns N"
    last = int(passes[-1].get("new_unknowns", 1))
    return last == 0, (f"dry after {len(passes)} passes" if last == 0
                       else f"last Q⇄R pass still surfaced {last} new load-bearing unknown(s) — not dry")


def _gate_children_done(run, spec, st, g):
    ids = run.get("children") or []
    mn = int(g.get("min", 1))
    kids = [(cid, (load_run(cid) or {}).get("status", "missing")) for cid in ids]
    if len(kids) < mn:
        return False, f"{len(kids)} slice run(s) (min {mn}); open one with: rig-loop slice start \"<name>\""
    open_ = [f"{cid}={s}" for cid, s in kids if s != "done"]
    return (not open_), ("all slices done: " + ", ".join(cid for cid, _ in kids) if not open_
                          else f"slices not done: {open_}")


def _gate_independent_verdict(run, spec, st, g):
    accept = [v.upper() for v in (g.get("accept") or ["PERFECT", "VERIFIED", "PARTIAL"])]
    builder = (run.get("harness") or "unknown").lower()
    good = [v for v in (run.get("verifications") or [])
            if v.get("verdict", "").upper() in accept and v.get("family", "").lower() != builder]
    mn = int(g.get("min", 1))
    if len(good) >= mn:
        return True, f"independent verdict {good[-1]['verdict']} from {good[-1]['family']} (builder {builder})"
    seen = [f"{v.get('family')}:{v.get('verdict')}" for v in run.get("verifications") or []]
    return False, (f"no accepted verdict from a family other than the builder ({builder}); seen {seen or 'none'}. "
                   f"Run: rig-loop verify --family <codex|claude|hermes|omp|prime-agent>")


_CONF_RX = re.compile(r"^##\s*CONFIDENCE[^\n]*\n\s*(0(?:\.\d+)?|1(?:\.0+)?)\s*$", re.M)


def _gate_confidence_declared(run, spec, st, g):
    p = _resolve_artifact(run, st, g.get("path"))
    if not p.exists():
        return False, f"{p} missing"
    m = _CONF_RX.search(p.read_text(errors="replace"))
    if not m:
        return False, "declare `## CONFIDENCE` followed by a probability 0–1 that the DONE-TEST will pass first time"
    run["predicted"] = float(m.group(1))
    return True, f"predicted confidence {run['predicted']}"


_DONE_TEST_RX = re.compile(r"^\s*[-*]\s*(cmd|file|grep|mcp):(\S.*)$", re.M)


def register_done_tests(run: dict, spec: dict, st: dict) -> list[str]:
    """Turn `- cmd:/file:/grep:` DONE-TEST lines of the stage artifact into checks tagged
    done_test, so Intent is executed at Quality/Proof instead of merely syntax-checked."""
    p = _resolve_artifact(run, st, None)
    if not p.exists():
        return []
    added = []
    existing = {c["cmd"] for c in run["checks"]}
    for form, arg in _DONE_TEST_RX.findall(p.read_text(errors="replace")):
        arg = arg.strip()
        if form == "cmd":
            cmd = arg
        elif form == "file":
            cmd = f"test -s {arg}"
        elif form == "grep":
            path, _, rx = arg.partition(":")
            cmd = f"grep -Eq '{rx}' {path}"
        else:
            continue
        if cmd in existing:
            continue
        run["checks"].append({"cmd": cmd, "cwd": run["cwd"], "added": utc_now(), "last": None, "done_test": True})
        run.setdefault("done_tests", []).append(cmd)
        added.append(cmd)
    if added:
        log_event(run, "done_tests_registered", count=len(added))
    return added


GATE_TYPES = {
    "file_exists": _gate_file_exists, "file_contains": _gate_file_contains, "regex": _gate_regex,
    "regex_absent": _gate_regex_absent, "no_unanswered_blocking": _gate_no_unanswered_blocking,
    "min_counter": _gate_min_counter, "checks_green": _gate_checks_green,
    "planted_failure": _gate_planted_failure, "sealed": _gate_sealed, "gate_d_approved": _gate_gate_d,
    "gate_d_requested": _gate_gate_d_requested,
    "cmd": _gate_cmd, "stage_passed": _gate_stage_passed, "drift_within": _gate_drift_within,
    "files_written_min": _gate_files_written_min, "qr_dry": _gate_qr_dry,
    "children_done": _gate_children_done, "independent_verdict": _gate_independent_verdict,
    "confidence_declared": _gate_confidence_declared,
}


def evaluate_gate(run: dict, spec: dict, st: dict) -> tuple[bool, list[dict]]:
    results = []
    ok_all = True
    for g in st.get("gate") or []:
        fn = GATE_TYPES[g["type"]]
        try:
            ok, detail = fn(run, spec, st, g)
        except Exception as exc:  # noqa: BLE001 — fail closed
            ok, detail = False, f"gate error: {exc}"
        results.append({"type": g["type"], "ok": bool(ok), "detail": detail, "tier": g.get("failure_tier", "halt")})
        if not ok and g.get("failure_tier", "halt") != "degrade":
            ok_all = False
    return ok_all, results


def can_enter(run: dict, spec: dict, st: dict) -> tuple[bool, str]:
    idx = [s["id"] for s in spec["stages"]].index(st["id"])
    for prior in spec["stages"][:idx]:
        if run["stage_status"].get(prior["id"]) not in STAGE_OK:
            return False, f"prior stage {prior['id']} is {run['stage_status'].get(prior['id'], 'unset')}"
    for req in st.get("requires") or []:
        if run["stage_status"].get(req) != "pass":
            return False, f"requires stage {req} pass"
    return True, ""


def mark_stage(run: dict, spec: dict, sid: str, status: str, artifact: str | None = None,
               score: int | None = None, note: str = "", force: bool = False) -> dict:
    st = stage_by_id(spec, sid)
    if not st:
        raise SpecError(f"unknown stage {sid}; valid: {[s['id'] for s in spec['stages']]}")
    if status not in ("pass", "fail", "park"):
        raise SpecError("status must be pass|fail|park")
    if run["status"] != "active":
        raise SpecError(f"run is {run['status']}; resume first")
    ok, why = can_enter(run, spec, st)
    if not ok:
        raise SpecError(f"cannot mark {sid}: {why}")
    if artifact:
        run["stage_artifacts"][sid] = str(Path(artifact).expanduser().resolve())
    gate_results: list[dict] = []
    degraded: list[dict] = []
    if status == "pass":
        ids = [s["id"] for s in spec["stages"]]
        # once P has passed, every later stage re-verifies the proof binding
        if "P" in ids and ids.index(sid) > ids.index("P") and run["stage_status"].get("P") == "pass":
            bound, why = proof_binding_ok(run)
            if not bound and not force:
                run["stage_status"].pop("P", None)
                log_event(run, "proof_stale", stage=sid, detail=why)
                save_run(run)
                raise SpecError(f"cannot mark {sid}: {why} — P reopened; re-seal then `rig-loop stage P pass`")
        gate_ok, gate_results = evaluate_gate(run, spec, st)
        if not gate_ok and not force:
            red = [r for r in gate_results if not r["ok"] and r["tier"] != "degrade"]
            log_event(run, "gate_red", stage=sid, results=gate_results)
            save_run(run)
            raise SpecError(f"stage {sid} gate RED — refusing pass: " +
                            " | ".join(f"{r['type']}: {r['detail']}" for r in red))
        degraded = [r for r in gate_results if not r["ok"] and r["tier"] == "degrade"]
        if degraded:
            note = (note + " " if note else "") + "[DEGRADED: " + "; ".join(f"{r['type']}: {r['detail']}" for r in degraded) + "]"
            log_event(run, "gate_degraded", stage=sid, results=degraded)
        if force:
            note = (note + " " if note else "") + "[FORCED — recorded as forced pass]"
        if st.get("register_done_tests"):
            added = register_done_tests(run, spec, st)
            if added:
                note = (note + " " if note else "") + f"[done-tests registered: {len(added)}]"
    run["stage_status"][sid] = status
    if score is not None:
        run["stage_score"][sid] = int(score)
    if note:
        run["stage_notes"][sid] = note
    run["history"].append({"ts": utc_now(), "stage": sid, "status": status, "iteration": run["iteration"],
                           "forced": bool(force and status == "pass"), "degraded": degraded, "gate": gate_results})
    log_event(run, "stage", stage=sid, status=status, forced=bool(force))
    if status == "fail":
        _apply_closing_loop(run, spec, sid)
    elif status == "park":
        run["status"] = "parked"
        run["park_reason"] = note or "parked"
        clear_active(run)
        _restore_parent(run)
    elif current_stage(run, spec) is None:
        run["status"] = "done"
        log_event(run, "done")
        clear_active(run)
        _restore_parent(run)
    save_run(run)
    return run


def _apply_closing_loop(run: dict, spec: dict, failed: str) -> None:
    cl = spec.get("closing_loop") or {}
    if failed in (cl.get("from") or []):
        run["iteration"] += 1
        mx = run["kill_switch"]["max_iterations"]
        if run["iteration"] > mx:
            run["status"] = "escalated"
            run["park_reason"] = f"closing loop exhausted ({mx} iterations) at {failed} — escalate to Mike"
            log_event(run, "escalate", stage=failed, iterations=run["iteration"] - 1)
            clear_active(run)
            _restore_parent(run)
            return
        to = cl.get("to")
        ids = [s["id"] for s in spec["stages"]]
        for sid in ids[ids.index(to):]:
            run["stage_status"].pop(sid, None)
        # evidence is per iteration: a new iteration must re-prove its planted failures and
        # re-seal; registered checks stay but their last results are discarded
        run["planted"] = []
        run["proof"] = None
        for c in run["checks"]:
            c["last"] = None
        run["iteration_started_at"] = utc_now()
        log_event(run, "closing_loop", from_stage=failed, to=to, iteration=run["iteration"])
    else:
        run["stage_status"].pop(failed, None)


# --------------------------------------------------------------------------- checks / plant / gate-d / seal
def add_check(run: dict, cmd: str, cwd: str | None = None) -> dict:
    run["checks"].append({"cmd": cmd, "cwd": cwd or run["cwd"], "added": utc_now(), "last": None})
    log_event(run, "check_add", cmd=cmd)
    save_run(run)
    return run


def run_checks(run: dict) -> list[dict]:
    results = []
    for c in run["checks"]:
        r = _run_cmd(c["cmd"], c.get("cwd"), 300)
        c["last"] = {"exit": r["exit"], "at": utc_now(), "tail": (r["stdout"] + r["stderr"])[-300:]}
        results.append(r)
    log_event(run, "checks_run", green=sum(1 for r in results if r["exit"] == 0), total=len(results))
    save_run(run)
    return results


def plant(run: dict, name: str, red_cmd: str, green_cmd: str, cwd: str | None = None) -> dict:
    """Non-vacuity: red_cmd must FAIL (the gate goes red on a planted defect); green_cmd must PASS."""
    red = _run_cmd(red_cmd, cwd or run["cwd"], 300)
    green = _run_cmd(green_cmd, cwd or run["cwd"], 300)
    rec = {"name": name, "red_cmd": red_cmd, "red_exit": red["exit"], "red_ok": red["exit"] != 0,
           "green_cmd": green_cmd, "green_exit": green["exit"], "green_ok": green["exit"] == 0, "at": utc_now()}
    run["planted"].append(rec)
    log_event(run, "plant", **{k: v for k, v in rec.items() if k != "at"})
    save_run(run)
    return rec


def gate_d_request(run: dict, action: str) -> dict:
    run["gate_d"].update({"requested": action, "requested_at": utc_now()})
    log_event(run, "gate_d_request", action=action)
    save_run(run)
    return run["gate_d"]


def gate_d_approve(run: dict, phrase: str, by: str = "mike") -> dict:
    expected = f"APPROVE {run['run_id']}"
    if phrase.strip() != expected:
        raise SpecError(f"Gate-D phrase mismatch; expected exactly: {expected}")
    if not run["gate_d"].get("requested"):
        raise SpecError("no Gate-D request on record — run: rig-loop gate-d request --action \"<what>\"")
    run["gate_d"].update({"approved": True, "by": by, "at": utc_now(), "phrase": phrase.strip()})
    log_event(run, "gate_d_approve", by=by)
    save_run(run)
    return run["gate_d"]


def seal(run: dict, spec: dict, signer: str = "rig-loop") -> dict:
    """ProofPacket: hash-bound record of the run. Requires every stage before P (or all
    stages if no P) to be pass; refuses on red checks."""
    ids = [s["id"] for s in spec["stages"]]
    p_idx = ids.index("P") if "P" in ids else len(ids)
    unmet = [sid for sid in ids[:p_idx] if run["stage_status"].get(sid) != "pass"]
    if unmet:
        raise SpecError(f"cannot seal: stages not passed: {unmet}")
    check_results = run_checks(run) if run["checks"] else []
    red = [r["cmd"] for r in check_results if r["exit"] != 0]
    if red:
        raise SpecError(f"cannot seal: red checks {red}")
    arts = {}
    for st in spec["stages"]:
        if st["id"] == "P" or (st.get("artifact") or "").endswith("proof.json"):
            continue  # the packet cannot bind its own copy
        p = _resolve_artifact(run, st, None)
        if p.exists() and p.is_file():
            arts[st["id"]] = {"path": str(p), "sha256": sha256_file(p)}
    packet = {
        "schema_version": "rig.proofpacket.v1", "proof_id": f"loop-{run['run_id']}",
        "created_at": utc_now(), "signer": signer, "packet_type": run.get("packet") or "LoopRunPacket",
        "loop_id": run["loop_id"], "loop_version": run.get("loop_version"), "run_id": run["run_id"],
        "coordinate": run.get("coordinate"), "intent": run.get("intent"), "cwd": run["cwd"],
        "harness": run.get("harness"), "mode": run["mode"], "iteration": run["iteration"],
        "stages": {sid: run["stage_status"].get(sid) for sid in ids},
        "stage_scores": run["stage_score"], "artifacts": arts,
        "checks": [{"cmd": r["cmd"], "exit": r["exit"]} for r in check_results],
        "planted_failures": run["planted"], "files_written": run["files_written"],
        "scope_drift": run["drift"], "gate_d": run["gate_d"], "events": run["events"],
        "history": run["history"], "verdict": "GO",
        "verifications": run.get("verifications") or [], "children": slice_list(run),
        "qr_passes": run.get("qr_passes") or [], "predicted": run.get("predicted"),
        "calibration": record_calibration(run), "tool_calls": run.get("tool_calls", 0),
    }
    body = json.dumps(packet, indent=2, sort_keys=True)
    packet["proof_hash"] = hashlib.sha256(body.encode()).hexdigest()
    proof_dir = Path(os.environ.get("RIG_LOOP_PROOF_DIR") or PROOF_DIR)
    proof_dir.mkdir(parents=True, exist_ok=True)
    out = proof_dir / f"loop-{run['run_id']}.json"
    _atomic_write(out, json.dumps(packet, indent=2, sort_keys=True))
    # keep a copy beside the stage artifacts so the P stage artifact resolves
    _atomic_write(artifacts_dir(run) / "proof.json", json.dumps(packet, indent=2, sort_keys=True))
    run["proof"] = {"path": str(out), "hash": sha256_file(out), "proof_hash": packet["proof_hash"],
                    "iteration": run["iteration"]}
    log_event(run, "seal", path=str(out))
    save_run(run)
    return packet


def park(run: dict, reason: str) -> dict:
    run["status"] = "parked"
    run["park_reason"] = reason
    log_event(run, "park", reason=reason)
    save_run(run)
    clear_active(run)
    _restore_parent(run)
    return run


def resume(run_id: str) -> dict:
    run = load_run(run_id)
    if not run:
        raise SpecError(f"no run {run_id}")
    if run["status"] == "done":
        raise SpecError("run is done")
    run["status"] = "active"
    run.pop("park_reason", None)
    log_event(run, "resume")
    save_run(run)
    set_active(run)
    return run


def close(run: dict, reason: str = "closed") -> dict:
    run["status"] = "closed"
    run["close_reason"] = reason
    log_event(run, "close", reason=reason)
    save_run(run)
    clear_active(run)
    _restore_parent(run)
    return run


# --------------------------------------------------------------------------- v20: Q⇄R, slices, verify, handoff, calibration
def qr_pass(run: dict, new_unknowns: int, note: str = "") -> dict:
    rec = {"n": len(run.get("qr_passes") or []) + 1, "at": utc_now(), "new_unknowns": int(new_unknowns), "note": note}
    run.setdefault("qr_passes", []).append(rec)
    run["counters"]["qr_passes"] = rec["n"]
    log_event(run, "qr_pass", **{k: v for k, v in rec.items() if k != "at"})
    save_run(run)
    return rec


def slice_start(parent: dict, name: str, loop_id: str = "iqrsqpi-v20-slice") -> dict:
    return activate(loop_id, cwd=parent["cwd"], intent=name, mode="auto", harness=parent.get("harness", ""),
                    parent_run_id=parent["run_id"])


def slice_list(parent: dict) -> list[dict]:
    out = []
    for cid in parent.get("children") or []:
        c = load_run(cid) or {}
        out.append({"run_id": cid, "intent": c.get("intent"), "status": c.get("status", "missing"),
                    "stages": c.get("stage_status", {})})
    return out


VERIFIER_FAMILIES = {
    "claude": ["claude", "-p", "--output-format", "text", "--max-turns", "12", "{prompt}"],
    "codex": ["codex", "exec", "--sandbox", "workspace-write", "--cd", "{cwd}", "{prompt}"],
    "hermes": ["hermes", "chat", "-q", "{prompt}", "--oneshot"],
    "omp": ["omp", "-p", "--no-session", "{prompt}"],
    "prime-agent": ["prime-agent", "-p", "{prompt}"],
}
_VERDICT_RX = re.compile(r"VERDICT:\s*(PERFECT|VERIFIED|PARTIAL|FEEDBACK|FAILED)\b", re.I)


def build_verifier_prompt(run: dict, spec: dict) -> str:
    arts = []
    for st in spec["stages"]:
        p = _resolve_artifact(run, st, None)
        if p.exists() and p.is_file() and p.suffix == ".md":
            arts.append(f"\n### {st['id']} {st.get('name','')} — {p}\n" + p.read_text(errors="replace")[:6000])
    checks = "\n".join(f"- `{c['cmd']}`" + (" (done-test)" if c.get("done_test") else "") for c in run["checks"]) or "- none"
    files = "\n".join(f"- {f}" for f in run["files_written"][:60]) or "- none recorded"
    return (
        f"You are an INDEPENDENT VERIFIER for a RIG loop run. You are a different model family from the builder "
        f"({run.get('harness')}); you have the artifacts and the tree, never the builder's reasoning. Do NOT modify tracked files.\n"
        f"Run id: {run['run_id']} · loop: {run['loop_id']} · cwd: {run['cwd']}\nIntent: {run.get('intent')}\n\n"
        f"Registered checks (run each yourself, report exit codes verbatim):\n{checks}\n\nFiles the builder wrote:\n{files}\n\n"
        f"Artifacts:{''.join(arts)}\n\n"
        "Verify against the contract in the artifacts: does the code/work satisfy the DONE-TEST and the Acceptance criteria? "
        "Probe adversarially for a way the checks could be green while the intent is unmet. "
        "Output exactly: a line `VERDICT: PERFECT|VERIFIED|PARTIAL|FEEDBACK|FAILED`, then `GAPS:` bullets with file:line evidence "
        "(or `- none`), then `EVIDENCE:` with the command outputs you ran. Be specific; do not pad."
    )


def verify(run: dict, spec: dict, family: str, cmd_override: str | None = None, timeout: int = 900) -> dict:
    """Dispatch a headless verifier of another family, parse its VERDICT, record it on the run."""
    family = family.lower()
    if family == (run.get("harness") or "").lower():
        raise SpecError(f"verifier family '{family}' equals the builder family — GEV separation requires a different family")
    prompt = build_verifier_prompt(run, spec)
    d = _run_dir(run["run_id"])
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    prompt_path = d / f"verify-{family}-{ts}.prompt.md"
    out_path = d / f"verify-{family}-{ts}.md"
    _atomic_write(prompt_path, prompt)
    t0 = time.time()
    override = cmd_override or os.environ.get("RIG_LOOP_VERIFIER_CMD")
    try:
        if override:
            cmd = override.replace("{prompt_file}", str(prompt_path)).replace("{cwd}", run["cwd"])
            r = subprocess.run(cmd, shell=True, cwd=run["cwd"], capture_output=True, text=True, timeout=timeout,
                               stdin=subprocess.DEVNULL)
        else:
            if family not in VERIFIER_FAMILIES:
                raise SpecError(f"unknown verifier family {family}; options: {sorted(VERIFIER_FAMILIES)}")
            argv = [a.replace("{prompt}", prompt).replace("{cwd}", run["cwd"]) for a in VERIFIER_FAMILIES[family]]
            r = subprocess.run(argv, cwd=run["cwd"], capture_output=True, text=True, timeout=timeout,
                               stdin=subprocess.DEVNULL)
        output, exit_code = (r.stdout or "") + ("\n[stderr]\n" + r.stderr if r.stderr else ""), r.returncode
    except subprocess.TimeoutExpired:
        output, exit_code = f"[timeout after {timeout}s]", 124
    except FileNotFoundError as exc:
        output, exit_code = f"[verifier binary not found: {exc}]", 127
    _atomic_write(out_path, output)
    m = _VERDICT_RX.search(output)
    verdict = m.group(1).upper() if m else "NO_VERDICT"
    gaps = []
    gm = re.search(r"GAPS:\s*\n((?:[ \t]*[-*].*\n?)+)", output)
    if gm:
        gaps = [ln.strip().lstrip("-* ").strip() for ln in gm.group(1).splitlines() if ln.strip()][:12]
    rec = {"family": family, "verdict": verdict, "exit": exit_code, "at": utc_now(), "secs": round(time.time() - t0, 1),
           "output": str(out_path), "prompt": str(prompt_path), "gaps": gaps, "iteration": run["iteration"]}
    run.setdefault("verifications", []).append(rec)
    log_event(run, "verify", family=family, verdict=verdict, exit=exit_code)
    save_run(run)
    return rec


def render_handoff(run: dict, spec: dict) -> str:
    st = current_stage(run, spec)
    done, total = progress(run, spec)
    kids = slice_list(run)
    lines = [
        "# Session Handoff", "",
        f"**Date**: {utc_now()[:10]}", f"**Project**: {run['cwd']}",
        f"**Session Goal**: {run.get('intent') or '(no intent recorded)'}",
        f"**Loop**: {run['loop_id']} run `{run['run_id']}` · mode {run['mode']} · iteration {run['iteration']} · status {run['status']}",
        f"**Status**: {'COMPLETE' if run['status'] == 'done' else 'PARTIAL' if done else 'NOT STARTED'} — {done}/{total} stages", "",
        "## Completed",
    ]
    for s in spec["stages"]:
        if run["stage_status"].get(s["id"]) == "pass":
            art = run["stage_artifacts"].get(s["id"]) or str(_resolve_artifact(run, s, None))
            lines.append(f"- [x] {s['id']} {s.get('name','')} — artifact: {art}")
    lines += ["", "## In Progress"]
    if st:
        ok, results = evaluate_gate(run, spec, st)
        red = [f"{r['type']}: {r['detail']}" for r in results if not r["ok"]]
        lines.append(f"- [ ] {st['id']} {st.get('name','')} — artifact: {_resolve_artifact(run, st, None)}")
        lines.append(f"  - Next step: {'`rig-loop stage ' + st['id'] + ' pass`' if ok else 'clear: ' + '; '.join(red)}")
    lines += ["", "## Not Started"]
    for s in spec["stages"]:
        if run["stage_status"].get(s["id"]) != "pass" and (not st or s["id"] != st["id"]):
            lines.append(f"- [ ] {s['id']} {s.get('name','')}")
    if kids:
        lines += ["", "## Slices"] + [f"- {k['run_id']} — {k['intent']} — {k['status']}" for k in kids]
    lines += ["", "## Decisions Made", "| Decision | Rationale | Reversible? |", "|----------|-----------|-------------|"]
    for sid, note in (run.get("stage_notes") or {}).items():
        lines.append(f"| {sid}: {note[:80]} | recorded in run history | yes |")
    if run["gate_d"].get("requested"):
        lines.append(f"| Gate-D: {run['gate_d']['requested'][:80]} | approved={run['gate_d'].get('approved')} | n/a |")
    lines += ["", "## Context for Next Session",
              f"- Key insight: resume with `rig-loop resume {run['run_id']}` (state: {_run_dir(run['run_id'])})",
              f"- Files to read first: {', '.join(run['stage_artifacts'].values()) or str(artifacts_dir(run))}",
              f"- Tests to run first: {', '.join(c['cmd'] for c in run['checks']) or '(none registered)'}",
              f"- Risk: {run.get('park_reason') or ('scope drift ' + str(len(run['drift'])) + ' file(s)' if run['drift'] else 'none recorded')}",
              "", "## Build Health",
              f"- Files modified this session: {len(run['files_written'])}",
              f"- Tests passing: {'yes' if run['checks'] and all((c.get('last') or {}).get('exit') == 0 for c in run['checks']) else 'unknown — run rig-loop check run'}",
              "- Verifications: " + (", ".join(v["family"] + "=" + v["verdict"] for v in (run.get("verifications") or [])) or "none"),
              f"- Context health at close: {'GREEN' if run['tool_calls'] < run['kill_switch']['max_tool_calls'] // 2 else 'YELLOW'}", ""]
    return "\n".join(lines)


def handoff(run: dict, spec: dict, to: str | None = None) -> Path:
    text = render_handoff(run, spec)
    out = artifacts_dir(run) / "handoff.md"
    _atomic_write(out, text)
    if to:
        _atomic_write(Path(os.path.expanduser(to)), text)
    log_event(run, "handoff", path=str(out), copy=to)
    save_run(run)
    return out


def calibration_path() -> Path:
    return state_root() / "calibration.jsonl"


def record_calibration(run: dict) -> dict | None:
    if run.get("predicted") is None:
        return None
    dts = [c for c in run["checks"] if c.get("done_test")]
    if not dts:
        return None
    actual = 1.0 if all((c.get("last") or {}).get("exit") == 0 for c in dts) else 0.0
    rec = {"at": utc_now(), "loop": run["loop_id"], "run": run["run_id"], "predicted": run["predicted"],
           "actual": actual, "brier": round((run["predicted"] - actual) ** 2, 4), "done_tests": len(dts)}
    with open(calibration_path(), "a") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    run["calibration"] = rec
    return rec


def calibration_summary(loop_id: str | None = None) -> dict:
    p = calibration_path()
    rows = []
    if p.exists():
        for ln in p.read_text().splitlines():
            try:
                r = json.loads(ln)
                if not loop_id or r.get("loop") == loop_id:
                    rows.append(r)
            except Exception:  # noqa: BLE001
                continue
    n = len(rows)
    return {"runs": n, "mean_brier": round(sum(r["brier"] for r in rows) / n, 4) if n else None,
            "hit_rate": round(sum(r["actual"] for r in rows) / n, 3) if n else None,
            "mean_predicted": round(sum(r["predicted"] for r in rows) / n, 3) if n else None, "recent": rows[-5:]}


# --------------------------------------------------------------------------- hook policy
def _norm_tool(name: str) -> str:
    n = (name or "").strip()
    low = n.lower().replace("-", "_")
    if low in WRITE_TOOLS:
        return "Write"
    if low in SHELL_TOOLS:
        return "Bash"
    return n


_PATCH_FILE_RX = re.compile(r"^\*\*\*\s+(?:Add|Update|Delete|Move to)\s+File:\s*(.+?)\s*$", re.M)


def _write_paths(inp: dict, payload: dict) -> list[str]:
    """Every file a write-class tool call touches: single path fields, MultiEdit-style
    `edits[]`, `files[]`, and apply_patch envelopes (`*** Update File: …`)."""
    paths: list[str] = []
    for k in ("file_path", "path", "filePath", "notebook_path", "target"):
        v = inp.get(k) or payload.get(k)
        if isinstance(v, str) and v:
            paths.append(v)
    for k in ("edits", "files", "changes"):
        for item in inp.get(k) or []:
            if isinstance(item, dict):
                v = item.get("file_path") or item.get("path") or item.get("filePath")
                if isinstance(v, str) and v:
                    paths.append(v)
            elif isinstance(item, str):
                paths.append(item)
    for k in ("patch", "diff", "input"):
        v = inp.get(k)
        if isinstance(v, str) and "*** " in v:
            paths.extend(_PATCH_FILE_RX.findall(v))
    out: list[str] = []
    for p in paths:
        if p not in out:
            out.append(p)
    return out


def normalize_payload(payload: dict) -> dict:
    inp = payload.get("tool_input") or payload.get("input") or payload.get("args") or {}
    if not isinstance(inp, dict):
        inp = {}
    paths = _write_paths(inp, payload)
    return {
        "tool": _norm_tool(payload.get("tool_name") or payload.get("tool") or payload.get("toolName") or ""),
        "raw_tool": payload.get("tool_name") or payload.get("tool") or payload.get("toolName") or "",
        "input": inp,
        "paths": paths,
        "path": paths[0] if paths else "",
        "command": inp.get("command") or inp.get("cmd") or payload.get("command") or "",
        "cwd": payload.get("cwd") or os.getcwd(),
        "session_id": payload.get("session_id") or "",
        "prompt": payload.get("prompt") or payload.get("message") or "",
        "stop_hook_active": bool(payload.get("stop_hook_active")),
        "tool_use_id": payload.get("tool_use_id") or payload.get("toolCallId") or "",
    }


def _glob_any(path: str, globs: list[str]) -> bool:
    p = str(path)
    for g in globs:
        gg = os.path.expanduser(g)
        if fnmatch.fnmatch(p, gg) or fnmatch.fnmatch(p, gg.rstrip("*") + "*"):
            return True
    return False


def _declared_globs(run: dict, spec: dict) -> list[str]:
    st = stage_by_id(spec, "S") or {}
    p = _resolve_artifact(run, st, None) if st else None
    if not p or not p.exists():
        return []
    text = p.read_text(errors="replace")
    m = re.search(r"^##\s*Files.*?$([\s\S]*?)(?=^##\s|\Z)", text, re.M)
    if not m:
        return []
    globs = []
    for line in m.group(1).splitlines():
        line = line.strip().lstrip("-*").strip().strip("`")
        if line and not line.startswith("#"):
            globs.append(line.split()[0])
    return globs


def banner(run: dict, spec: dict) -> str:
    st = current_stage(run, spec)
    done, total = progress(run, spec)
    gd = "approved" if run["gate_d"].get("approved") else "not approved"
    if st is None:
        nxt = "all stages complete — close with: rig-loop close"
    else:
        gates = "; ".join(f"{g['type']}" + (f"({g.get('path','')})" if g.get("path") else "") for g in st.get("gate") or []) or "none"
        nxt = f"stage {st['id']} {st.get('name','')} ({done+1}/{total}) — artifact: {_resolve_artifact(run, st, None)} — gates: {gates}"
    parent = f" · child of {run['parent_run_id']}" if run.get("parent_run_id") else ""
    lines = [f"[rig-loop] {spec.get('name', run['loop_id'])} · run {run['run_id']}{parent} · mode {run['mode']} · iteration {run['iteration']}/{run['kill_switch']['max_iterations']} · gate-d {gd} · tool-calls {run.get('tool_calls', 0)}/{run['kill_switch'].get('max_tool_calls', 800)}",
             f"[rig-loop] NOW: {nxt}",
             f"[rig-loop] advance with: rig-loop stage {st['id'] if st else '<id>'} pass [--artifact PATH]  · status: rig-loop status  · park: rig-loop park --reason \"...\""]
    if run["drift"]:
        lines.append(f"[rig-loop] scope drift: {len(run['drift'])} file(s) outside spec ## Files")
    if run["mode_opts"].get("stop_after_stage"):
        lines.append("[rig-loop] WALK mode: stop after each stage pass and wait for Mike's confirmation.")
    return "\n".join(lines)


def hook_session_start(run: dict | None, spec: dict | None, p: dict) -> dict:
    if not run:
        return {"action": "allow"}
    return {"action": "inject", "text": "[rig-loop] RESUMED active loop run\n" + banner(run, spec)}


def hook_prompt(run: dict | None, spec: dict | None, p: dict) -> dict:
    if not run:
        return {"action": "allow"}
    ks = run["kill_switch"]
    if wall_minutes(run) > ks["max_wall_minutes"]:
        park(run, f"kill switch: wall clock > {ks['max_wall_minutes']} min")
        return {"action": "inject", "text": f"[rig-loop] KILL SWITCH — run {run['run_id']} parked after {ks['max_wall_minutes']} min. Re-plan or `rig-loop resume {run['run_id']}` with a reason."}
    log_event(run, "prompt", chars=len(p.get("prompt", "")))
    save_run(run)
    return {"action": "inject", "text": banner(run, spec)}


def hook_pre_tool(run: dict | None, spec: dict | None, p: dict, skill: str | None = None) -> dict:
    if not run and skill:
        try:
            run = activate(skill, cwd=p["cwd"], harness="auto", if_inactive=True)
            spec = load_spec(skill)
        except Exception as exc:  # noqa: BLE001
            return {"action": "allow", "note": f"auto-activate failed: {exc}"}
    if not run:
        return {"action": "allow"}
    st = current_stage(run, spec)
    tool = p["tool"]
    # ---- kill switch: tool-call budget
    run["tool_calls"] = int(run.get("tool_calls", 0)) + 1
    mx = int(run["kill_switch"].get("max_tool_calls", 800))
    if run["tool_calls"] > mx:
        park(run, f"kill switch: tool-call budget {mx} exceeded at stage {st['id'] if st else 'complete'}")
        return {"action": "deny", "reason": (
            f"[rig-loop {run['loop_id']}] KILL SWITCH — {mx} tool calls reached; run {run['run_id']} parked. "
            f"Write a handoff (`rig-loop resume {run['run_id']} && rig-loop handoff`) and re-plan with Mike.")}
    # ---- shell: outward / irreversible actions need Gate-D
    if tool == "Bash" and p["command"]:
        pol = spec.get("outward_policy") or {}
        pats = pol.get("patterns") or DEFAULT_OUTWARD_PATTERNS
        hit = next((pat for pat in pats if re.search(pat, p["command"], re.I)), None)
        if hit and pol.get("require_gate_d", True) and not run["gate_d"].get("approved"):
            log_event(run, "deny", tool=tool, reason="outward-without-gate-d", cmd=p["command"][:300])
            save_run(run)
            return {"action": "deny", "reason": (
                f"[rig-loop {run['loop_id']}] OUTWARD ACTION BLOCKED (matched /{hit}/). Gate-D not approved for run {run['run_id']}. "
                f"Stage now: {st['id'] if st else 'complete'}. Request with `rig-loop gate-d request --action \"...\"`, then Mike types "
                f"`rig-loop gate-d approve --phrase \"APPROVE {run['run_id']}\"`. Stage everything dormant until then.")}
        # shell redirect / in-place edits count as writes for artifacts_only stages
        if st and (st.get("write_policy") or {}).get("mode") == "artifacts_only":
            allow_globs = DEFAULT_PLAN_GLOBS + ((st.get("write_policy") or {}).get("extra_allow") or []) + [str(artifacts_dir(run)) + "/*"]
            targets = re.findall(r"(?<![0-9&<])>>?\s*([^\s;&|<>]+)", p["command"])
            targets += re.findall(r"\b(?:tee|sed\s+-i(?:\s+'')?)\s+(?:-a\s+)?([^\s;&|<>]+)", p["command"])
            bad = [t for t in targets if t not in ("/dev/null",) and not t.startswith("&")
                   and not _glob_any(str(Path(os.path.expanduser(t.strip("'\"")))), allow_globs)
                   and not _glob_any(str(Path(p["cwd"]) / t.strip("'\"")), allow_globs)]
            if bad:
                log_event(run, "deny", tool=tool, reason="shell-write-before-stage", stage=st["id"], targets=bad[:5])
                save_run(run)
                return {"action": "deny", "reason": (
                    f"[rig-loop {run['loop_id']}] SHELL WRITE BLOCKED at stage {st['id']} {st.get('name','')}: {bad[:3]}. "
                    f"{(st.get('write_policy') or {}).get('deny_message') or 'Only plan/spec artifacts may be written until this stage passes.'} "
                    f"Artifact: {_resolve_artifact(run, st, None)} then `rig-loop stage {st['id']} pass`.")}
        log_event(run, "tool", tool=tool, cmd=p["command"][:200])
        save_run(run)
        return {"action": "allow"}
    # ---- writes: stage write policy (every path the call touches; fail closed when unknown)
    if tool == "Write":
        if not st:
            return {"action": "allow"}
        pol = st.get("write_policy") or {"mode": "open"}
        mode = pol.get("mode", "open")
        allow_globs = DEFAULT_PLAN_GLOBS + (pol.get("extra_allow") or []) + [str(artifacts_dir(run)) + "/*"]
        if not p["paths"] and mode == "artifacts_only":
            log_event(run, "deny", tool=tool, reason="write-unknown-target", stage=st["id"], raw_tool=p["raw_tool"])
            save_run(run)
            return {"action": "deny", "reason": (
                f"[rig-loop {run['loop_id']}] WRITE BLOCKED at stage {st['id']} {st.get('name','')}: tool "
                f"{p['raw_tool'] or 'write'} did not declare a target path, so it cannot be checked (fail-closed). "
                f"Use a single-file write to the stage artifact ({_resolve_artifact(run, st, None)}).")}
        for raw in p["paths"]:
            path = str(Path(os.path.expanduser(raw)))
            if not Path(path).is_absolute():
                path = str(Path(p["cwd"]) / path)
            if mode == "artifacts_only" and not _glob_any(path, allow_globs):
                log_event(run, "deny", tool=tool, reason="write-before-stage", stage=st["id"], path=path)
                save_run(run)
                return {"action": "deny", "reason": (
                    f"[rig-loop {run['loop_id']}] WRITE BLOCKED at stage {st['id']} {st.get('name','')}: {path}. "
                    f"{pol.get('deny_message') or 'Only plan/spec artifacts may be written until this stage passes.'} "
                    f"Write the stage artifact ({_resolve_artifact(run, st, None)}) then run `rig-loop stage {st['id']} pass`.")}
            if mode == "declared":
                globs = _declared_globs(run, spec)
                if globs and not _glob_any(path, globs + allow_globs):
                    if path not in run["drift"]:
                        run["drift"].append(path)
                        log_event(run, "drift", path=path, stage=st["id"])
            if path not in run["files_written"]:
                run["files_written"].append(path)
            log_event(run, "tool", tool=tool, path=path, stage=st["id"])
        save_run(run)
    return {"action": "allow"}


def hook_stop(run: dict | None, spec: dict | None, p: dict) -> dict:
    if not run or run["status"] != "active":
        return {"action": "allow"}
    st = current_stage(run, spec)
    if st is None:
        return {"action": "inject", "text": f"[rig-loop] run {run['run_id']} complete; close with `rig-loop close`."}
    last = run["history"][-1] if run["history"] else None
    if run["mode_opts"].get("stop_after_stage") and last and last.get("status") == "pass":
        return {"action": "inject", "text": f"[rig-loop] WALK: stage {last['stage']} passed. Waiting for Mike to confirm before {st['id']}."}
    if p.get("stop_hook_active") or run["stop_blocks"] >= run["kill_switch"]["max_stop_blocks"]:
        return {"action": "inject", "text": (
            f"[rig-loop] stop allowed after {run['stop_blocks']} block(s) — loop {run['loop_id']} is NOT done: stage {st['id']} unmet. "
            f"Say so plainly in the final message, or `rig-loop park --reason \"...\"`.")}
    run["stop_blocks"] += 1
    log_event(run, "stop_block", stage=st["id"], n=run["stop_blocks"])
    save_run(run)
    ok, results = evaluate_gate(run, spec, st)
    red = "; ".join(f"{r['type']}: {r['detail']}" for r in results if not r["ok"]) or "artifact not produced"
    return {"action": "block", "reason": (
        f"[rig-loop {run['loop_id']}] NOT DONE — stage {st['id']} {st.get('name','')} has not passed ({red}). "
        f"Either finish the stage (`rig-loop stage {st['id']} pass`) or park honestly (`rig-loop park --reason \"...\"`). "
        f"Stop-block {run['stop_blocks']}/{run['kill_switch']['max_stop_blocks']}.")}


def hook_post_tool(run: dict | None, spec: dict | None, p: dict) -> dict:
    return {"action": "allow"}


HOOKS = {"session-start": hook_session_start, "prompt": hook_prompt, "pre-tool": hook_pre_tool,
         "post-tool": hook_post_tool, "stop": hook_stop}


def dispatch_hook(event: str, payload: dict, skill: str | None = None, run_id: str | None = None) -> dict:
    if event not in HOOKS:
        raise SpecError(f"unknown hook event {event}; valid: {sorted(HOOKS)}")
    p = normalize_payload(payload)
    run = find_active(p["cwd"], run_id)
    spec = load_spec(run["loop_id"]) if run else None
    if event == "pre-tool":
        return hook_pre_tool(run, spec, p, skill=skill)
    return HOOKS[event](run, spec, p)


def render_hook(event: str, result: dict, fmt: str) -> tuple[str, str, int]:
    """Return (stdout, stderr, exit_code) for a harness format."""
    action = result.get("action", "allow")
    if fmt == "pi":
        out = {"block": action in ("deny", "block"), "reason": result.get("reason", ""),
               "inject": result.get("text", "")}
        return json.dumps(out), "", 0
    if fmt == "text":
        return json.dumps(result, indent=2), "", 0
    # claude / codex (Claude-compatible hook schema)
    if action == "deny":
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                      "permissionDecisionReason": result["reason"]}}
        return json.dumps(out), result["reason"], 2
    if action == "block":
        return "", result["reason"], 2
    if action == "inject":
        return result.get("text", ""), "", 0
    return "", "", 0


# --------------------------------------------------------------------------- wiring
def _hook_cmd(event: str, fmt: str) -> str:
    return f"python3 {CLI} hook {event} --format {fmt}  # {MARKER}"


def _claude_style_entries(fmt: str) -> dict:
    tools = "Write|Edit|MultiEdit|NotebookEdit|Bash|apply_patch|shell"
    e = lambda ev, t=None: {"type": "command", "command": _hook_cmd(ev, fmt), "timeout": t or 20}  # noqa: E731
    return {
        "SessionStart": [{"matcher": "startup|resume", "hooks": [e("session-start", 10)]}],
        "UserPromptSubmit": [{"matcher": "*", "hooks": [e("prompt", 10)]}],
        "PreToolUse": [{"matcher": tools, "hooks": [e("pre-tool", 20)]}],
        "Stop": [{"matcher": "*", "hooks": [e("stop", 20)]}],
    }


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bak = path.with_name(f"{path.name}.bak-rigloop-{ts}")
    shutil.copy2(path, bak)
    return bak


def _strip_managed(hooks: dict) -> dict:
    out = {}
    for ev, arr in (hooks or {}).items():
        keep = []
        for m in arr or []:
            hs = [h for h in (m.get("hooks") or []) if MARKER not in str(h.get("command", ""))]
            if hs:
                m2 = dict(m)
                m2["hooks"] = hs
                keep.append(m2)
        if keep:
            out[ev] = keep
    return out


def _wire_json_hooks(path: Path, fmt: str, apply: bool, remove: bool = False) -> dict:
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except Exception as exc:  # noqa: BLE001
            return {"harness": fmt, "path": str(path), "ok": False, "error": f"unparseable: {exc}"}
    hooks = _strip_managed(data.get("hooks") or {})
    if not remove:
        for ev, entries in _claude_style_entries(fmt).items():
            hooks.setdefault(ev, []).extend(entries)
    changed = (data.get("hooks") or {}) != hooks
    if apply and changed:
        bak = _backup(path)
        data["hooks"] = hooks
        _atomic_write(path, json.dumps(data, indent=2) + "\n")
        return {"harness": fmt, "path": str(path), "ok": True, "changed": True, "backup": str(bak) if bak else None}
    return {"harness": fmt, "path": str(path), "ok": True, "changed": changed, "applied": bool(apply and changed)}


def _pi_extension_source() -> str:
    src = REPO / "capabilities" / "hooks" / "rig-loop-hooks.ts"
    return src.read_text()


def _wire_pi(dest: Path, apply: bool, remove: bool = False) -> dict:
    if remove:
        existed = dest.exists()
        if existed and apply:
            dest.unlink()
        return {"path": str(dest), "ok": True, "changed": existed}
    text = _pi_extension_source()
    changed = (not dest.exists()) or dest.read_text() != text
    if apply and changed:
        dest.parent.mkdir(parents=True, exist_ok=True)
        _backup(dest)
        _atomic_write(dest, text)
    return {"path": str(dest), "ok": True, "changed": changed, "applied": bool(apply and changed)}


def _wire_hermes(dest: Path, apply: bool, remove: bool = False) -> dict:
    src = REPO / "capabilities" / "hooks" / "rig-loop-gate"
    if remove:
        if dest.exists() and apply:
            shutil.rmtree(dest)
        return {"path": str(dest), "ok": True}
    changed = False
    for name in ("HOOK.yaml", "handler.py"):
        s, d = src / name, dest / name
        if not d.exists() or d.read_text() != s.read_text():
            changed = True
            if apply:
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
    return {"path": str(dest), "ok": True, "changed": changed, "applied": bool(apply and changed)}


def _wire_omp_include(skill_ids: list[str], apply: bool) -> dict:
    if not OMP_CONFIG.exists():
        return {"path": str(OMP_CONFIG), "ok": False, "error": "missing"}
    text = OMP_CONFIG.read_text()
    m = re.search(r"^(\s*)includeSkills:\s*\n", text, re.M)
    if not m:
        return {"path": str(OMP_CONFIG), "ok": True, "changed": False, "note": "no includeSkills allowlist — all skills load"}
    indent = m.group(1) + "  "
    missing = [s for s in skill_ids if not re.search(rf"^{re.escape(indent)}- {re.escape(s)}\s*$", text, re.M)]
    if not missing:
        return {"path": str(OMP_CONFIG), "ok": True, "changed": False}
    insert = "".join(f"{indent}- {s}\n" for s in missing)
    new = text[:m.end()] + insert + text[m.end():]
    if apply:
        _backup(OMP_CONFIG)
        _atomic_write(OMP_CONFIG, new)
    return {"path": str(OMP_CONFIG), "ok": True, "changed": True, "added": missing, "applied": apply}


def _wire_symlink(apply: bool) -> dict:
    link = RIG_LOOP_LINK
    ok = link.is_symlink() and Path(os.readlink(link)) == CLI
    if not ok and apply:
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(CLI)
        ok = True
    return {"path": str(link), "ok": ok, "target": str(CLI)}


def wire(apply: bool = False, harnesses: list[str] | None = None, remove: bool = False) -> dict:
    hs = harnesses or list(HARNESSES)
    report: dict = {"apply": apply, "remove": remove, "results": {}}
    for h in hs:
        if h == "claude":
            report["results"][h] = _wire_json_hooks(HOOK_CONFIG["claude"], "claude", apply, remove)
        elif h == "codex":
            report["results"][h] = _wire_json_hooks(HOOK_CONFIG["codex"], "codex", apply, remove)
        elif h in ("omp", "prime-agent"):
            report["results"][h] = _wire_pi(HOOK_CONFIG[h], apply, remove)
        elif h == "hermes":
            report["results"][h] = _wire_hermes(HOOK_CONFIG["hermes"], apply, remove)
    if not remove:
        ids = [s["id"] for s in list_specs() if "error" not in s]
        report["results"]["omp-includeSkills"] = _wire_omp_include(ids, apply)
        report["results"]["symlink"] = _wire_symlink(apply)
    return report


def verify_wiring() -> dict:
    out = {}
    for h in HARNESSES:
        p = HOOK_CONFIG[h]
        if h in ("claude", "codex"):
            try:
                data = json.loads(p.read_text()) if p.exists() else {}
                blob = json.dumps(data.get("hooks") or {})
                events = [ev for ev, arr in (data.get("hooks") or {}).items()
                          if any(MARKER in str(hk.get("command", "")) for m in arr for hk in (m.get("hooks") or []))]
                out[h] = {"wired": MARKER in blob, "events": sorted(events), "path": str(p)}
            except Exception as exc:  # noqa: BLE001
                out[h] = {"wired": False, "error": str(exc), "path": str(p)}
        elif h in ("omp", "prime-agent"):
            out[h] = {"wired": p.exists() and MARKER in p.read_text(), "path": str(p)}
        else:
            out[h] = {"wired": (p / "HOOK.yaml").exists() and (p / "handler.py").exists(), "path": str(p),
                      "note": "Hermes gateway hooks cannot block or inject; enforcement is CLI-level"}
    return out


def doctor() -> dict:
    rep: dict = {"engine": ENGINE_VERSION, "schema": SCHEMA, "cli": str(CLI), "state_root": str(state_root())}
    try:
        import yaml  # type: ignore # noqa: F401
        rep["pyyaml"] = True
    except ImportError:
        rep["pyyaml"] = False
    rep["cli_on_path"] = shutil.which("rig-loop") is not None
    rep["wiring"] = verify_wiring()
    specs = [s for s in list_specs() if "error" not in s]
    rep["loop_skills"] = {}
    for s in specs:
        inst = {}
        for h in HARNESSES:
            root = SKILL_ROOTS[h] / s["id"]
            inst[h] = (root / "SKILL.md").exists() and ((root / "loop.yaml").exists() or (root / "loop.json").exists())
        rep["loop_skills"][s["id"]] = {"installed": inst, "stages": s["stages"], "version": s.get("version")}
    bad = [s for s in list_specs() if "error" in s]
    rep["spec_errors"] = bad
    a = _read_active()
    rep["active_runs"] = {k: v for k, v in a.get("by_cwd", {}).items()}
    rep["missing_installs"] = [f"{sid}@{h}" for sid, v in rep["loop_skills"].items()
                               for h, ok in v["installed"].items() if not ok]
    # ok means: every spec parses, every harness is wired, every loop-skill is installed everywhere
    rep["ok"] = (not bad) and all(v["wired"] for v in rep["wiring"].values()) and not rep["missing_installs"]
    return rep


# --------------------------------------------------------------------------- loop tests (non-vacuity)
def run_loop_tests(loop_id: str) -> dict:
    spec = load_spec(loop_id)
    cases_path = Path(spec["_dir"]) / "tests" / "cases.json"
    if not cases_path.exists():
        return {"loop": loop_id, "ok": False, "error": f"no tests/cases.json in {spec['_dir']}"}
    cases = json.loads(cases_path.read_text())
    results = []
    with tempfile.TemporaryDirectory(prefix="rigloop-test-") as tmp:
        old_state = os.environ.get("RIG_LOOP_STATE")
        old_proof = os.environ.get("RIG_LOOP_PROOF_DIR")
        os.environ["RIG_LOOP_STATE"] = str(Path(tmp) / "state")
        os.environ["RIG_LOOP_PROOF_DIR"] = str(Path(tmp) / "proof")
        try:
            for case in cases:
                results.append(_run_case(spec, case, Path(tmp)))
        finally:
            for k, v in (("RIG_LOOP_STATE", old_state), ("RIG_LOOP_PROOF_DIR", old_proof)):
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
    ok = all(r["ok"] for r in results)
    return {"loop": loop_id, "ok": ok, "cases": results,
            "summary": f"{sum(1 for r in results if r['ok'])}/{len(results)} cases pass"}


def _run_case(spec: dict, case: dict, tmp: Path) -> dict:
    cwd = tmp / re.sub(r"[^a-z0-9]+", "-", case["name"].lower())[:40]
    cwd.mkdir(parents=True, exist_ok=True)
    run = None
    steps_out = []
    ok = True

    def sub(s: str) -> str:
        cur = load_run(run["run_id"]) if run else None
        proof_path = ((cur or {}).get("proof") or {}).get("path", "") if cur else ""
        return (s.replace("<cwd>", str(cwd)).replace("<artifacts>", str(artifacts_dir(run)) if run else "")
                 .replace("<run_id>", run["run_id"] if run else "").replace("<proof>", proof_path))

    for i, step in enumerate(case.get("steps", [])):
        expect = step.get("expect") or {}
        got: dict = {}
        try:
            if "activate" in step:
                a = step["activate"] or {}
                run_cwd = sub(a["cwd"]) if a.get("cwd") else str(cwd)
                Path(run_cwd).mkdir(parents=True, exist_ok=True)
                run = activate(spec["id"], cwd=run_cwd, intent=a.get("intent", "test"), mode=a.get("mode", "auto"), harness="test")
                got = {"run": run["run_id"], "ok": True}
            elif "write" in step:
                w = step["write"]
                p = Path(sub(w["path"]))
                if not p.is_absolute():
                    p = (artifacts_dir(run) if run else cwd) / p
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(sub(w.get("content", "")))
                got = {"ok": True, "path": str(p)}
            elif "hook" in step:
                h = dict(step["hook"])
                ev = h.pop("event")
                payload = json.loads(sub(json.dumps(h)))
                payload.setdefault("cwd", run["cwd"] if run else str(cwd))
                res = dispatch_hook(ev, payload, skill=h.get("skill"))
                got = {"ok": True, "action": res.get("action"), "reason": res.get("reason", "")}
                if run:
                    run = load_run(run["run_id"]) or run
            elif "stage" in step:
                s = step["stage"]
                try:
                    cur_run = load_run(run["run_id"])
                    run = mark_stage(cur_run, load_spec(cur_run["loop_id"]), s["id"], s.get("status", "pass"),
                                     artifact=sub(s["artifact"]) if s.get("artifact") else None,
                                     note=s.get("note", ""), force=bool(s.get("force")))
                    got = {"ok": True, "status": run["stage_status"].get(s["id"]), "run_status": run["status"], "iteration": run["iteration"]}
                except SpecError as exc:
                    got = {"ok": False, "refused": str(exc)}
            elif "counter" in step:
                run = load_run(run["run_id"])
                run["counters"][step["counter"]["name"]] = int(step["counter"].get("value", 1))
                save_run(run)
                got = {"ok": True}
            elif "check_add" in step:
                run = add_check(load_run(run["run_id"]), sub(step["check_add"]), str(cwd))
                got = {"ok": True}
            elif "plant" in step:
                pl = step["plant"]
                rec = plant(load_run(run["run_id"]), pl["name"], sub(pl["red"]), sub(pl["green"]), str(cwd))
                got = {"ok": True, "red_ok": rec["red_ok"], "green_ok": rec["green_ok"]}
            elif "gate_d" in step:
                g = step["gate_d"]
                run = load_run(run["run_id"])
                if g.get("request"):
                    gate_d_request(run, g["request"])
                    got = {"ok": True}
                if g.get("approve") is not None:
                    try:
                        gate_d_approve(run, sub(g["approve"]))
                        got = {"ok": True, "approved": True}
                    except SpecError as exc:
                        got = {"ok": False, "refused": str(exc)[:200]}
            elif "seal" in step:
                try:
                    seal(load_run(run["run_id"]), spec, signer="rig-loop-test")
                    got = {"ok": True}
                except SpecError as exc:
                    got = {"ok": False, "refused": str(exc)[:200]}
            elif "park" in step:
                run = park(load_run(run["run_id"]), step["park"])
                got = {"ok": True, "run_status": run["status"]}
            elif "resume" in step:
                run = resume(run["run_id"])
                got = {"ok": True, "run_status": run["status"]}
            elif "qr" in step:
                rec = qr_pass(load_run(run["run_id"]), int(step["qr"].get("new_unknowns", 0)))
                got = {"ok": True, "n": rec["n"]}
            elif "slice" in step:
                sl = step["slice"]
                if sl.get("start"):
                    try:
                        run = slice_start(load_run(run["run_id"]), sl["start"], sl.get("loop", "iqrsqpi-v20-slice"))
                        got = {"ok": True, "run": run["run_id"], "child": True}
                    except SpecError as exc:
                        got = {"ok": False, "refused": str(exc)}
                elif sl.get("parent"):
                    run = load_run(run["parent_run_id"])
                    got = {"ok": True, "run": run["run_id"]}
            elif "verify" in step:
                v = step["verify"]
                mock = v.get("mock")
                override = f"printf 'VERDICT: {mock}\\nGAPS:\\n- none\\n'" if mock else v.get("cmd")
                try:
                    cur_run = load_run(run["run_id"])
                    rec = verify(cur_run, load_spec(cur_run["loop_id"]), v.get("family", "codex"), cmd_override=override, timeout=60)
                    got = {"ok": True, "verdict": rec["verdict"], "family": rec["family"]}
                except SpecError as exc:
                    got = {"ok": False, "refused": str(exc)}
            elif "handoff" in step:
                cur_run = load_run(run["run_id"])
                p = handoff(cur_run, load_spec(cur_run["loop_id"]))
                got = {"ok": p.exists(), "path": str(p)}
            elif "sh" in step:
                r = _run_cmd(sub(step["sh"]), str(cwd), 60)
                got = {"ok": r["exit"] == 0, "exit": r["exit"], "tail": (r["stdout"] + r["stderr"])[-160:]}
            elif "set" in step:
                run = load_run(run["run_id"])
                run[step["set"]["field"]] = step["set"]["value"]
                save_run(run)
                got = {"ok": True}
            elif "assert" in step:
                run = load_run(run["run_id"])
                a = step["assert"]
                val = run.get(a["field"])
                got = {"ok": True, "value": val if not isinstance(val, (list, dict)) else None,
                       "len": len(val) if isinstance(val, (list, dict)) else None,
                       "active": (find_active(str(cwd)) or {}).get("run_id")}
            else:
                got = {"ok": False, "error": f"unknown step {list(step)}"}
        except Exception as exc:  # noqa: BLE001
            got = {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:300]}
        step_ok = True
        for k, v in expect.items():
            if k == "ok":
                step_ok &= (got.get("ok") is v)
            elif k == "reason_contains":
                step_ok &= (v in got.get("reason", "") or v in got.get("refused", ""))
            elif k == "active_is":
                active = (find_active(str(cwd)) or {}).get("run_id")
                cur = load_run(run["run_id"]) if run else None
                want = {"self": (cur or {}).get("run_id"), "parent": (cur or {}).get("parent_run_id"), "none": None}[v]
                step_ok &= (active == want)
                got["active"] = active
            else:
                step_ok &= (got.get(k) == v)
        if expect and not step_ok:
            ok = False
        shown = {k: (v[:220] if isinstance(v, str) else v) for k, v in got.items()}
        steps_out.append({"i": i, "step": next(iter(step)), "got": shown, "expect": expect, "ok": step_ok or not expect})
    return {"name": case["name"], "ok": ok, "steps": steps_out}


# --------------------------------------------------------------------------- scaffold + compile
def compile_spec(loop_id: str) -> Path:
    spec = load_spec(loop_id)
    clean = {k: v for k, v in spec.items() if not k.startswith("_")}
    out = Path(spec["_dir"]) / "loop.json"
    _atomic_write(out, json.dumps(clean, indent=2, sort_keys=True) + "\n")
    return out


SCAFFOLD_SKILL = """---
name: {id}
description: "RIG doctrine as a loop-skill — {name}. {summary}"
version: 11.0.0
outcome: "agent-engineering: {name} enforced as a gated loop with hooks"
done_when:
  - "cmd:python3 bin/rig-loop test {id}"
  - "file:capabilities/skills/{id}/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.7
metadata:
  loop_skill: v11
  doctrine_source: "{source}"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill {id}"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# {name} — loop-skill (v11 contract)

Source doctrine: `{source}`

## Step 0 — activate (every harness)

```bash
rig-loop activate {id} --intent "<one sentence>"
```

## Stages

(fill from the doctrine; one artifact + one deterministic gate per stage)

## Closing loop / kill switch

See loop.yaml. Escalate to Mike when the closing loop is exhausted.
"""

SCAFFOLD_LOOP = {
    "schema": SCHEMA, "id": "", "name": "", "version": "11.0.0", "doctrine_source": [],
    "coordinate": {"level": 3, "diamond": "D2", "bms_mode": "A1", "step": "I1"},
    "family": "governance", "packet": "LoopRunPacket",
    "modes": {"auto": {}, "walk": {"stop_after_stage": True}},
    "kill_switch": {"max_iterations": 3, "max_wall_minutes": 240, "max_stop_blocks": 2},
    "outward_policy": {"require_gate_d": True},
    "stages": [
        {"id": "I1", "name": "Intent", "artifact": "intent.md",
         "gate": [{"type": "file_contains", "path": "intent.md", "patterns": ["^## GOAL", "^## DONE-TEST"]}],
         "write_policy": {"mode": "artifacts_only"}},
        {"id": "P", "name": "Proof", "artifact": "proof.json", "gate": [{"type": "sealed"}]},
    ],
    "closing_loop": {"from": ["P"], "to": "I1", "max_iterations": 3, "on_exhaust": "park"},
}


def scaffold(loop_id: str, name: str, source: str = "", summary: str = "") -> Path:
    d = SKILL_ROOTS["canonical"] / loop_id
    if d.exists():
        raise SpecError(f"{d} exists")
    (d / "tests").mkdir(parents=True)
    (d / "SKILL.md").write_text(SCAFFOLD_SKILL.format(id=loop_id, name=name, source=source, summary=summary))
    spec = dict(SCAFFOLD_LOOP)
    spec.update({"id": loop_id, "name": name, "doctrine_source": [source] if source else []})
    try:
        import yaml  # type: ignore
        (d / "loop.yaml").write_text(yaml.safe_dump(spec, sort_keys=False))
    except ImportError:
        (d / "loop.yaml").write_text(json.dumps(spec, indent=2))
    (d / "tests" / "cases.json").write_text(json.dumps([
        {"name": "refuses pass without artifact", "steps": [
            {"activate": {}},
            {"stage": {"id": "I1", "status": "pass"}, "expect": {"ok": False}}]},
        {"name": "passes with artifact", "steps": [
            {"activate": {}},
            {"write": {"path": "intent.md", "content": "## GOAL\nx\n## DONE-TEST\n- cmd:true\n"}},
            {"stage": {"id": "I1", "status": "pass"}, "expect": {"ok": True}}]},
    ], indent=2))
    return d
