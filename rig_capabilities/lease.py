"""V40: exclusive worktree leases — the F2 fix (shared-worktree collision).

Doctrine (RIG ANTI-FABRICATION HARNESS v1, Mechanism 1): "opened a new terminal
in the same worktree" becomes a hard startup failure, not silent corruption.
No lease → no work. One task, one worktree, one branch. Ceiling 16, hard cap.
Stale leases are reaped; the boot-time position assertion aborts a task that is
not where the lease says it is.

`acquire()` NEVER creates a checkout (house law: agents do not create worktrees).
It binds an existing git toplevel and refuses anything the workstation repo
guard would deny writes to, so a dispatched task can never be leased into a
surface whose writes will be denied.

State lives under `lease_dir()`, resolved at CALL time from RIG_LEASE_STATE_ROOT
(default `~/.rig/leases`) so a test or a gate can point the whole subsystem at a
throwaway root without re-importing. Every register write is atomic
(tmp + os.replace) under an flock; collisions are append-only.

Nothing here fires automatically. `record_collision()` writes
`<lease_dir>/route-state.json` ({agent_collisions, retries}); the operator (or
the dispatch wrapper) hands that file to
`/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac route --state <path>` so
the existing `tac.agent-collision` rule fires. Bare `tac` is coreutils.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Import-time default, kept for the frozen contract's name. Authoritative
# resolution is lease_dir(), which re-reads the env on every call.
LEASE_DIR = Path(os.environ.get("RIG_LEASE_STATE_ROOT",
                               Path.home() / ".rig" / "leases"))
ENV_STATE_ROOT = "RIG_LEASE_STATE_ROOT"
CEILING = 16
DEFAULT_TTL_S = 4 * 3600
LEASES_FILE = "leases.json"
LOCK_FILE = "leases.lock"
COLLISIONS_FILE = "collisions.jsonl"
ROUTE_STATE_FILE = "route-state.json"
SCENARIO_REL = "tests/fixtures/fable2031/lease-scenario.json"
CANARY_SUBDIR = "canary"
GUARD_BIN = Path(os.environ.get("RIG_REPO_GUARD",
                               str(Path.home() / ".rig" / "bin" / "rig-repo-guard")))
CANONICAL_REPO = "/Users/rig128gb/Developer/rig-capabilities"

EXIT_OK = 0
EXIT_DENIAL = 2


class LeaseError(Exception):
    """Base for every lease refusal."""

    def __init__(self, reason: str, **fields) -> None:
        super().__init__(reason)
        self.reason = reason
        self.fields = fields


class LeaseDenied(LeaseError):
    """The lease was refused. Exit 2; the task must stop, not relocate."""


# --------------------------------------------------------------- state layout

def lease_dir() -> Path:
    """The lease state root, resolved at call time (tests/gates point elsewhere)."""
    env = os.environ.get(ENV_STATE_ROOT)
    if env:
        return Path(env).expanduser()
    return Path.home() / ".rig" / "leases"


def canary_root(task_id: str) -> Path:
    """Per-task canary dir — outside every tracked worktree by construction."""
    return lease_dir() / _slug(task_id) / CANARY_SUBDIR


def route_state_path() -> Path:
    return lease_dir() / ROUTE_STATE_FILE


def collisions_path() -> Path:
    return lease_dir() / COLLISIONS_FILE


def _slug(task_id: str) -> str:
    """Filesystem-safe, collision-free-enough task id."""
    s = "".join(c if c.isalnum() or c in "-_." else "-"
                for c in str(task_id)).strip("-")
    if not s:
        s = hashlib.sha256(str(task_id).encode("utf-8")).hexdigest()[:12]
    return s[:64]


def _write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(
        f"{path.name}.tmp-{os.getpid()}-{secrets.randbelow(1 << 20)}")
    tmp.write_text(json.dumps(obj, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    os.replace(tmp, path)


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _append_line(path: Path, rec: dict) -> None:
    """One O_APPEND write. Collisions are never rewritten, never lost silently."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, (json.dumps(rec, sort_keys=True) + "\n").encode("utf-8"))
    finally:
        os.close(fd)


@contextlib.contextmanager
def _locked():
    """Serialise the read-modify-write of the lease register across processes."""
    root = lease_dir()
    root.mkdir(parents=True, exist_ok=True)
    fh = open(root / LOCK_FILE, "a+")
    try:
        fcntl.flock(fh, fcntl.LOCK_EX)
        yield root
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


@contextlib.contextmanager
def state_root_override(path):
    """Point the whole subsystem at `path`, then restore the env exactly."""
    prev = os.environ.get(ENV_STATE_ROOT)
    os.environ[ENV_STATE_ROOT] = str(path)
    try:
        yield Path(path)
    finally:
        if prev is None:
            os.environ.pop(ENV_STATE_ROOT, None)
        else:
            os.environ[ENV_STATE_ROOT] = prev


def _registry(path=None) -> dict:
    """The lease register. `path` defaults to <lease_dir()>/leases.json."""
    src = Path(path) if path is not None else lease_dir() / LEASES_FILE
    reg = _read_json(src, {})
    if not isinstance(reg, dict) or not isinstance(reg.get("leases"), dict):
        return {"leases": {}}
    return reg


def _save_registry(reg: dict) -> None:
    _write_json(lease_dir() / LEASES_FILE, reg)


# ------------------------------------------------------------- external probes

_GUARD_CACHE: dict[str, dict] = {}


def _git_toplevel(path) -> str | None:
    """Resolved git toplevel for `path`, or None when it isn't inside a repo."""
    p = Path(str(path)).expanduser()
    if not p.exists():
        return None
    try:
        r = subprocess.run(["git", "-C", str(p), "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    top = (r.stdout or "").strip()
    return str(Path(top).resolve()) if top else None


def is_toplevel(path) -> str | None:
    """`path` resolved, when `path` IS itself a git toplevel. Else None.

    A subdir of a repo resolves to its parent toplevel, so it is not a bindable
    worktree — two tasks in two subdirs are still one shared checkout.
    """
    want = str(Path(str(path)).expanduser().resolve())
    top = _git_toplevel(want)
    return top if top == want else None


def guard_probe(path) -> dict:
    """Is `path` inside a registered writable root? Never raises, never hangs.

    The workstation guard is the authority (rig_repo_guard.py denies writes
    outside every registered writable root). An unavailable guard is
    `UNAVAILABLE` with allowed=None — it must not be read as a denial, and the
    reason is recorded on the lease so the surface stays auditable.
    """
    key = str(Path(str(path)).expanduser().resolve())
    hit = _GUARD_CACHE.get(key)
    if hit is not None:
        return dict(hit)
    out: dict
    if not GUARD_BIN.exists():
        out = {"status": "UNAVAILABLE", "allowed": None,
               "reason": f"repo guard absent at {GUARD_BIN}"}
    else:
        try:
            r = subprocess.run([str(GUARD_BIN), "check", key],
                               capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.SubprocessError) as e:
            out = {"status": "UNAVAILABLE", "allowed": None,
                   "reason": f"guard probe failed: {type(e).__name__}: {e}"}
        else:
            try:
                doc = json.loads(r.stdout or "{}")
            except json.JSONDecodeError:
                doc = {}
            if not isinstance(doc, dict) or "allowed" not in doc:
                out = {"status": "UNAVAILABLE", "allowed": None,
                       "reason": f"guard answer unparseable (exit {r.returncode})"}
            else:
                out = {"status": str(doc.get("status") or
                                     ("ALLOW" if doc.get("allowed") else "BLOCK")),
                       "allowed": bool(doc.get("allowed")),
                       "reason": str(doc.get("reason") or ""),
                       "repository": doc.get("repository")}
    _GUARD_CACHE[key] = dict(out)
    return out


# ----------------------------------------------------------------- the leases

def _live(leases: dict, now) -> dict:
    return {k: v for k, v in leases.items()
            if float(v.get("expires_at") or 0) > now}


def acquire(task_id, worktree_path, branch, ttl_s=DEFAULT_TTL_S,
            provisioner="orca") -> dict:
    """Bind an EXISTING git worktree to one task. Refuses everything else.

    Order is cheap-first: ceiling → worktree → write-surface → exclusivity.
    Never creates, clones, or branches anything (L2).
    """
    if not str(task_id).strip():
        raise LeaseDenied("task_id_required")
    if not str(branch).strip():
        raise LeaseDenied("branch_required")
    ttl = float(ttl_s)
    if ttl <= 0:
        raise LeaseDenied("ttl_must_be_positive")
    want = str(Path(str(worktree_path)).expanduser().resolve())

    with _locked() as root:
        now = time.time()
        reg = _registry(root / LEASES_FILE)
        live = _live(reg["leases"], now)

        if len(live) >= CEILING:
            raise LeaseDenied("concurrency_ceiling", ceiling=CEILING,
                              held=len(live))

        top = is_toplevel(want)
        if top is None:
            raise LeaseDenied("worktree_absent", worktree_path=want,
                              detail="not a git toplevel — acquire() never creates one")

        guard = guard_probe(top)
        if guard.get("allowed") is False:
            raise LeaseDenied("unregistered_write_surface", worktree_path=top,
                              guard=guard.get("reason", "blocked"))

        for held_id, lease in live.items():
            if lease.get("worktree_path") != top:
                continue
            if held_id == str(task_id) and lease.get("branch") == str(branch):
                out = dict(lease)
                out["reused"] = True
                out["guard"] = guard
                return out
            record_collision(str(task_id), held_id)
            raise LeaseDenied("worktree_leased", lease_held_by=held_id,
                              worktree_path=top,
                              held_branch=lease.get("branch"))

        lease = {"task_id": str(task_id), "worktree_path": top,
                 "branch": str(branch), "provisioner": str(provisioner),
                 "lease_token": f"lt-{secrets.token_urlsafe(16)}",
                 "acquired_at": round(now, 3),
                 "expires_at": round(now + ttl, 3), "ttl_s": ttl,
                 "guard": guard.get("status", "UNAVAILABLE")}
        reg["leases"][str(task_id)] = lease
        _save_registry(reg)
        return dict(lease)


def release(task_id, lease_token) -> dict:
    """Drop a lease. Only the token the lease was granted with releases it."""
    with _locked() as root:
        reg = _registry(root / LEASES_FILE)
        lease = reg["leases"].get(str(task_id))
        if lease is None:
            raise LeaseDenied("lease_unknown", task_id=str(task_id))
        if str(lease.get("lease_token")) != str(lease_token):
            raise LeaseDenied("lease_token_mismatch", task_id=str(task_id))
        gone = reg["leases"].pop(str(task_id))
        _save_registry(reg)
        return {"released": str(task_id), "worktree_path": gone.get("worktree_path"),
                "branch": gone.get("branch"),
                "held_s": round(max(0.0, time.time() - float(gone.get("acquired_at") or 0)), 3)}


def list_leases(now=None) -> list:
    """Active (unexpired) leases with holder and age — `list` output."""
    ts = time.time() if now is None else float(now)
    live = _live(_registry(lease_dir() / LEASES_FILE)["leases"], ts)
    rows = []
    for held_id, lease in live.items():
        out = dict(lease)
        out["age_s"] = round(max(0.0, ts - float(lease.get("acquired_at") or 0)), 3)
        out["remaining_s"] = round(max(0.0, float(lease.get("expires_at") or 0) - ts), 3)
        rows.append(out)
    return sorted(rows, key=lambda r: r["acquired_at"])


def expire(now=None) -> dict:
    """Reap TTL-elapsed leases: forced release, task requeue is the dispatcher's job."""
    ts = time.time() if now is None else float(now)
    with _locked() as root:
        reg = _registry(root / LEASES_FILE)
        stale = {k: v for k, v in reg["leases"].items()
                 if float(v.get("expires_at") or 0) <= ts}
        for k in stale:
            reg["leases"].pop(k)
        if stale:
            _save_registry(reg)
        rows = [{"task_id": k, "worktree_path": v.get("worktree_path"),
                 "branch": v.get("branch"),
                 "overdue_s": round(ts - float(v.get("expires_at") or 0), 3)}
                for k, v in stale.items()]
        return {"now": round(ts, 3), "expired": sorted(rows, key=lambda r: r["task_id"]),
                "count": len(stale), "active": len(reg["leases"])}


def assert_position(task_id, cwd, toplevel, branch) -> dict:
    """Boot-time position assertion. Any mismatch terminates the dispatched task."""
    leases = _live(_registry(lease_dir() / LEASES_FILE)["leases"], time.time())
    lease = leases.get(str(task_id))
    if lease is None:
        return {"ok": False, "reason": "WORKTREE_ASSERTION_FAILED",
                "mismatch": "no_active_lease", "task_id": str(task_id)}

    def _same(a, b) -> bool:
        if a is None or b is None:
            return False
        try:
            return str(Path(str(a)).expanduser().resolve()) == \
                   str(Path(str(b)).expanduser().resolve())
        except OSError:
            return str(a) == str(b)

    want = lease.get("worktree_path")
    if not _same(toplevel, want):
        mismatch = "toplevel"
    elif str(branch) != str(lease.get("branch")):
        mismatch = "branch"
    elif not _inside(cwd, want):
        mismatch = "cwd"
    else:
        return {"ok": True, "reason": "position_ok", "task_id": str(task_id),
                "worktree_path": want, "branch": lease.get("branch")}
    return {"ok": False, "reason": "WORKTREE_ASSERTION_FAILED",
            "mismatch": mismatch, "task_id": str(task_id),
            "leased_worktree": want, "leased_branch": lease.get("branch"),
            "seen": {"cwd": str(cwd), "toplevel": str(toplevel),
                     "branch": str(branch)}}


def _inside(cwd, root) -> bool:
    if cwd is None or root is None:
        return False
    try:
        c = Path(str(cwd)).expanduser().resolve()
        r = Path(str(root)).expanduser().resolve()
    except OSError:
        return False
    return c == r or r in c.parents


def record_collision(task_id, held_by) -> dict:
    """Append the collision and bump the route-state counter.

    Writes <lease_dir>/route-state.json {agent_collisions, retries}. Nothing
    consumes it automatically: the operator passes it to
    /Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac route --state <path>.
    """
    root = lease_dir()
    ts = round(time.time(), 3)
    state = _read_json(root / ROUTE_STATE_FILE, {})
    if not isinstance(state, dict):
        state = {}
    n = int(state.get("agent_collisions") or 0) + 1
    retries = list(state.get("retries") or [])
    retries.append({"at": ts, "task_id": str(task_id), "held_by": str(held_by),
                    "attempt": n})
    state = {"agent_collisions": n, "retries": retries[-50:],
             "updated_at": ts,
             "route_hint": "/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac "
                           f"route --state {root / ROUTE_STATE_FILE}"}
    _append_line(collisions_path(), {"at": ts, "task_id": str(task_id),
                                     "held_by": str(held_by), "attempt": n})
    _write_json(root / ROUTE_STATE_FILE, state)
    return state


# -------------------------------------------------------- scenario replay/gate

def _resolve_token(tok: str, repo_root, state_root) -> str:
    subs = {"@REPO_ROOT@": str(repo_root), "@CANONICAL_REPO@": CANONICAL_REPO,
            "@STATE_ROOT@": str(state_root)}
    return subs.get(tok, subs.get(tok.split("/")[0], tok))


def _resolve_worktree(spec: dict, repo_root, state_root) -> tuple[str, str]:
    """Pick the first candidate that really is a git toplevel.

    Prefer the tree under test; fall back to the canonical registered checkout so
    a copied tree (no .git) still replays against a real bindable worktree.
    """
    cands = spec.get("candidates") or [spec.get("path")]
    for cand in cands:
        if not cand:
            continue
        p = _resolve_token(str(cand), repo_root, state_root)
        top = is_toplevel(p)
        if top is not None:
            return top, str(spec.get("branch") or "")
    first = _resolve_token(str(cands[0]), repo_root, state_root)
    return first, str(spec.get("branch") or "")


def _token_ref(ref: str, results: dict) -> str:
    """`@op:1.lease_token` → the token op 1 was granted."""
    if not str(ref).startswith("@op:"):
        return str(ref)
    inner = str(ref)[4:]
    idx, _, field = inner.partition(".")
    got = results.get(idx.strip()) or {}
    return str((got.get("lease") or {}).get(field) or "")


def replay_scenario(scenario_path, repo_root=None, state_root=None) -> dict:
    """Replay an ordered lease scenario inside a throwaway state root.

    `state_root=None` → a fresh mkdtemp, removed afterwards. Either way
    RIG_LEASE_STATE_ROOT is redirected for the duration and restored exactly, so
    the real ~/.rig/leases is never touched and a copied tree replays identically.
    """
    path = Path(scenario_path)
    doc = _read_json(path, None)
    if not isinstance(doc, dict) or not isinstance(doc.get("ops"), list):
        return {"ok": False, "detail": f"scenario unreadable or ops missing: {path}",
                "results": []}
    repo_root = Path(repo_root or Path.cwd())
    ttl = float(doc.get("ttl_s") or DEFAULT_TTL_S)
    owned = state_root is None
    root = Path(state_root) if state_root is not None else Path(
        tempfile.mkdtemp(prefix="lease-gate-"))
    results, mismatches = {}, []
    try:
        with state_root_override(root):
            worktrees = doc.get("worktrees") or {}
            for op in doc["ops"]:
                i = str(op.get("i"))
                kind = str(op.get("op"))
                expect = str(op.get("expect"))
                row = {"i": i, "op": kind, "expect": expect}
                try:
                    if kind == "acquire":
                        wt = worktrees.get(str(op.get("worktree"))) or {}
                        path_, branch = _resolve_worktree(wt, repo_root, root)
                        if op.get("branch"):
                            branch = str(op.get("branch"))
                        got = acquire(op.get("task"), path_, branch,
                                      ttl_s=float(op.get("ttl_s") or ttl))
                        outcome, row["lease"] = "granted", got
                    elif kind == "release":
                        tok = _token_ref(str(op.get("lease_token") or ""), results)
                        got = release(op.get("task"), tok)
                        outcome = "released"
                    elif kind == "expire":
                        got = expire(now=time.time() + float(op.get("now_offset_s") or 0))
                        outcome = "expired" if got["count"] else "none_expired"
                    else:
                        outcome = f"unknown_op:{kind}"
                except LeaseDenied as e:
                    outcome, row["reason"] = "denied", e.reason
                    row.update({k: v for k, v in e.fields.items()
                                if k in ("lease_held_by",)})
                    row["fields"] = dict(e.fields)
                except Exception as e:  # a crash is a mismatch, never a pass
                    outcome, row["reason"] = "error", f"{type(e).__name__}: {e}"
                ok = outcome == expect
                if ok and expect == "denied":
                    if op.get("reason") and row.get("reason") != op.get("reason"):
                        ok = False
                    if op.get("lease_held_by") and \
                            row.get("lease_held_by") != op.get("lease_held_by"):
                        ok = False
                row["got"] = outcome
                row["ok"] = bool(ok)
                if not ok:
                    mismatches.append(
                        f"op{i} {kind}: expected {expect}"
                        f"{'/' + str(op.get('reason')) if op.get('reason') else ''}"
                        f" got {outcome}{'/' + str(row.get('reason')) if row.get('reason') else ''}")
                results[i] = row
    finally:
        if owned:
            shutil.rmtree(root, ignore_errors=True)
    return {"ok": not mismatches, "detail": "; ".join(mismatches) or
            f"{len(results)} ops matched", "ops": len(results),
            "results": [results[k] for k in sorted(results, key=lambda x: int(x))]}


def gate_lease_exclusivity(repo) -> tuple[bool, str]:
    """Certify gate: the committed lease scenario still replays exactly as pinned.

    Hermetic (L1): reads only <repo.root>/tests/fixtures/fable2031/lease-scenario.json
    and replays it under a throwaway state root, never ~/.rig/leases. Goes RED when
    the scenario's second acquire is flipped to `granted` — exclusivity is real or
    the gate is red, never theater.
    """
    try:
        rep = replay_scenario(Path(repo.root) / SCENARIO_REL,
                              repo_root=Path(repo.root))
        return bool(rep["ok"]), rep["detail"]
    except Exception as e:  # noqa: BLE001 — a crash IS a red gate
        return False, f"{type(e).__name__}: {e}"


# -------------------------------------------------------------------- the CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="rig-lease", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("acquire", help="bind an existing worktree to one task")
    p.add_argument("--task", required=True)
    p.add_argument("--worktree", required=True)
    p.add_argument("--branch", required=True)
    p.add_argument("--ttl-s", type=float, default=DEFAULT_TTL_S)
    p.add_argument("--provisioner", default="orca")

    p = sub.add_parser("release", help="drop a lease with its granted token")
    p.add_argument("--task", required=True)
    p.add_argument("--token", dest="lease_token", default="")

    sub.add_parser("list", help="active leases, holders, ages")

    p = sub.add_parser("expire", help="reap TTL-elapsed leases")
    p.add_argument("--now-offset-s", type=float, default=0.0)

    p = sub.add_parser("assert", help="boot-time position assertion")
    p.add_argument("--task", required=True)
    p.add_argument("--cwd", default=os.getcwd())
    p.add_argument("--toplevel", required=True)
    p.add_argument("--branch", required=True)

    a = ap.parse_args(argv)
    try:
        if a.cmd == "acquire":
            out = acquire(a.task, a.worktree, a.branch, ttl_s=a.ttl_s,
                          provisioner=a.provisioner)
        elif a.cmd == "release":
            out = release(a.task, a.lease_token)
        elif a.cmd == "list":
            out = {"state_root": str(lease_dir()), "ceiling": CEILING,
                   "leases": list_leases()}
        elif a.cmd == "expire":
            out = expire(now=time.time() + a.now_offset_s)
        else:
            out = assert_position(a.task, a.cwd, a.toplevel, a.branch)
            if not out.get("ok"):
                print(json.dumps(out, indent=1, sort_keys=True))
                return EXIT_DENIAL
    except LeaseError as e:
        print(json.dumps({"ok": False, "reason": e.reason,
                          "state_root": str(lease_dir()), **e.fields},
                         indent=1, sort_keys=True))
        return EXIT_DENIAL
    print(json.dumps(out, indent=1, sort_keys=True))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
