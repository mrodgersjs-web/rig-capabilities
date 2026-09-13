"""Instruction-surface renderer: one policy source, four managed runtimes.

The build standard lives in `capabilities/data/rig-build-standard/policy.md`. Each
runtime's instruction surface (the four paths in the D85 authority's
`surfaces.json` — never a path literal here) carries exactly one managed block,
delimited by markers that name the policy's sha256. Rules this module enforces:

* the managed block is the ONLY thing this module writes in a target; every other
  byte of that file is preserved verbatim, so hand-written surface content is safe;
* a block whose sha differs from current policy is DRIFT, reported by `check` with
  exit 2 — never silently repaired;
* nothing reaches a target without Gate-D: `stage` writes the candidate, the diff and
  the exact action file; `install` consumes a signed approval through
  `d85_gates.arm_gate_d`, so an approval row this module wrote itself would not verify.
* `receipts` reports installed / configured / loaded / exercised / enforced as five
  separate states. An unobservable state is UNVERIFIED, never inferred from the
  neighbouring one.

Usage: python3 rig_capabilities/surfaces_render.py selftest
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POLICY = REPO / "capabilities/data/rig-build-standard/policy.md"
SURFACES = REPO / "capabilities/skills/rig-determinism-85/authority/surfaces.json"
STAGE_DIR = REPO / "runs/agentic-stack-buildout/gate-d/surfaces"
D85_SKILL = REPO / "capabilities/skills/rig-determinism-85"
GATE_D_PROCESS = "build_standard_chain_v1"
ACTION_DIR = STAGE_DIR / "actions"
# Gate-D seams the tests move; production leaves both None so the live authority and
# its signed <authority>/gate_d store are used.
AUTHORITY = None
GATE_ROOT = None
OPEN_ = "<!-- RIG_BUILD_STANDARD:v1:sha256:"
CLOSE = "<!-- /RIG_BUILD_STANDARD:v1 -->"
RUNTIMES = ("claude_code", "hermes", "omp", "prime_agent")


class SurfaceError(ValueError):
    pass


def policy_sha() -> str:
    return hashlib.sha256(policy_body().encode()).hexdigest()


def policy_body() -> str:
    try:
        text = POLICY.read_text(encoding="utf-8")
    except OSError as exc:
        raise SurfaceError(f"policy source unreadable: {exc}") from exc
    match = re.search(r"<\!-- BODY -->\n(.*?)\n<!-- /BODY -->", text, re.S)
    if not match or not match.group(1).strip():
        raise SurfaceError("policy.md must contain a non-empty <!-- BODY --> section")
    return match.group(1)


def block(sha: str | None = None) -> str:
    sha = sha or policy_sha()
    return f"{OPEN_}{sha} -->\n{policy_body()}\n{CLOSE}"


def surfaces() -> dict[str, Path]:
    try:
        cfg = json.loads(SURFACES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SurfaceError(f"surfaces.json unreadable: {exc}") from exc
    got = cfg.get("surfaces") if isinstance(cfg, dict) else None
    if not isinstance(got, dict) or set(got) != set(RUNTIMES):
        raise SurfaceError(f"surfaces.json must define exactly {sorted(RUNTIMES)}")
    return {name: Path(raw).expanduser() for name, raw in got.items()}


def splice(current: str, managed: str) -> str:
    """Replace the managed block, or append it. Everything outside stays verbatim."""
    open_re = re.escape(OPEN_) + r"[0-9a-f]{64} -->"
    pattern = re.compile(open_re + r"\n.*?\n" + re.escape(CLOSE), re.S)
    if pattern.search(current):
        return pattern.sub(lambda _m: managed, current, count=1)
    sep = "" if not current or current.endswith("\n\n") else ("\n" if current.endswith("\n") else "\n\n")
    return current + sep + managed + "\n"


def status() -> list[dict]:
    sha = policy_sha()
    managed = block(sha)
    rows = []
    for name, path in sorted(surfaces().items()):
        row = {"surface": name, "path": str(path), "policy_sha256": sha}
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            rows.append({**row, "status": "MISSING", "detail": type(exc).__name__})
            continue
        if managed in text:
            rows.append({**row, "status": "WIRED", "preserved_bytes": len(text) - len(managed)})
        elif re.search(re.escape(OPEN_) + r"[0-9a-f]{64} -->", text):
            stale = re.search(re.escape(OPEN_) + r"([0-9a-f]{64}) -->", text).group(1)
            rows.append({**row, "status": "DRIFT", "detail": f"block sha {stale} != policy {sha}"})
        else:
            rows.append({**row, "status": "UNWIRED", "detail": "no managed block present"})
    return rows


def action_for(name: str) -> dict:
    """The exact action a signed approval must bind: one surface, one policy hash."""
    return {"kind": "wiring:instruction-surface", "surface": name,
            "policy_sha256": policy_sha()}


def action_label(action: dict) -> str:
    return (f"wiring:instruction-surface:{action['surface']}"
            f"@sha256:{action['policy_sha256']}")


def _approval(action: dict, approval_id: str | None) -> dict:
    """Gate-D, and only Gate-D: HMAC-signed approvals.jsonl row + D85 eligibility of
    the registered process, consumed once by an O_EXCL marker. This module never
    mints; `approval_id` is accepted for CLI compatibility and deliberately ignored,
    because the authority is the signature, not a caller-supplied label."""
    if str(D85_SKILL) not in sys.path:
        sys.path.insert(0, str(D85_SKILL))
    import d85_gates  # noqa: PLC0415 — the D85 authority is a skill-root module
    try:
        verdict = d85_gates.gate_d(AUTHORITY or d85_gates.AUTHORITY_REGISTRY,
                                   GATE_D_PROCESS, action, test_gate_root=GATE_ROOT)
    except Exception as exc:  # noqa: BLE001 — any refusal is a refusal
        return {"ok": False, "reason": f"{type(exc).__name__}: {exc}"}
    return {"ok": True, "approval": verdict}


def _atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".tmp-{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def stage(name: str | None = None) -> list[dict]:
    """Write candidates + diffs + pending Gate-D requests. Never touches a target."""
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    wanted = [name] if name else list(RUNTIMES)
    out = []
    for surface in wanted:
        path = surfaces()[surface]
        try:
            current = path.read_text(encoding="utf-8")
        except OSError:
            current = ""
        rendered = splice(current, block())
        cand = STAGE_DIR / f"{surface}.candidate.md"
        _atomic(cand, rendered)
        diff = "".join(difflib.unified_diff(
            current.splitlines(keepends=True), rendered.splitlines(keepends=True),
            fromfile=str(path), tofile=cand.name))
        diff_path = STAGE_DIR / f"{surface}.diff"
        _atomic(diff_path, diff or "(no change — already current)\n")
        action = action_for(surface)
        ACTION_DIR.mkdir(parents=True, exist_ok=True)
        act_file = ACTION_DIR / f"{surface}.action.json"
        act_file.write_text(json.dumps(action, indent=1, sort_keys=True) + "\n",
                            encoding="utf-8")
        req = STAGE_DIR / f"{surface}.gate-d-request.json"
        req.write_text(json.dumps({
            "schema": "rig.build-standard.gate-d-request.v1", "surface": surface,
            "target": str(path), "action": action, "action_label": action_label(action),
            "action_file": str(act_file), "process_id": GATE_D_PROCESS,
            "candidate": str(cand), "diff": str(diff_path),
            "bytes_added": len(rendered) - len(current),
            "status": "PENDING_MIKE_TYPED_APPROVAL",
            "mint_command": (
                f"python3 -c \"import sys; sys.path.insert(0,'{D85_SKILL}'); "
                f"import d85_gates as g, json, pathlib; "
                f"a=json.loads(pathlib.Path('{act_file}').read_text()); "
                f"p=pathlib.Path('{D85_SKILL}/authority/gate_d'); "
                f"v=g.score_realized(g.AUTHORITY_REGISTRY, '{GATE_D_PROCESS}'); "
                f"print(g.mint_approval(p, process_id='{GATE_D_PROCESS}', "
                f"inventory_sha256=v['inventory_sha256'], classification_sha256=v['classification_sha256'], "
                f"realized_sha256=g._canonical_hash(v), action=a, approver='mike', "
                f"lifetime_seconds=900))\""),
        }, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        out.append({"surface": surface, "candidate": str(cand), "request": str(req),
                    "action": action_label(action), "bytes_added": len(rendered) - len(current)})
    return out


def install(name: str, approval_id: str | None) -> dict:
    path = surfaces()[name]
    action = action_for(name)
    gate = _approval(action, approval_id)
    if not gate["ok"]:
        raise SurfaceError(f"GATE-D BLOCKED ({name}): {gate['reason']} — the approved "
                           f"action must be exactly: {action_label(action)}")
    try:
        current = path.read_text(encoding="utf-8")
    except OSError:
        current = ""
    before = hashlib.sha256(current.encode()).hexdigest()
    rendered = splice(current, block())
    if rendered == current:
        return {"surface": name, "status": "ALREADY_CURRENT", "sha256": before}
    backup = STAGE_DIR / f"{name}.pre-install-{before[:12]}.md"
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    backup.write_text(current, encoding="utf-8")
    _atomic(path, rendered)
    after = path.read_text(encoding="utf-8")
    if block() not in after:
        _atomic(path, current)
        raise SurfaceError(f"{name}: post-write containment failed; restored {before[:12]}")
    outside = splice(current, "")
    if outside and outside.strip() not in after:
        _atomic(path, current)
        raise SurfaceError(f"{name}: unrelated surface content lost; restored {before[:12]}")
    return {"surface": name, "status": "WIRED", "sha_before": before,
            "sha_after": hashlib.sha256(after.encode()).hexdigest(),
            "policy_sha256": policy_sha(), "backup": str(backup),
            "gate_d": gate["approval"]}


def receipts() -> list[dict]:
    """Five separate states per runtime. Never collapse them; never infer."""
    from rig_capabilities.catalog import Repo  # noqa: PLC0415
    cat = Repo(REPO)
    sha = policy_sha()
    rows = []
    for name, path in sorted(surfaces().items()):
        harness = {"claude_code": "claude", "hermes": "hermes", "omp": "omp",
                   "prime_agent": "prime-agent"}[name]
        skill_roots, agent_roots = cat.install_roots("skill"), cat.install_roots("agent")
        row = {
            "surface": name, "path": str(path), "policy_sha256": sha,
            "configured": harness in skill_roots and harness in agent_roots,
            "skill_installed": _has(skill_roots.get(harness), "rig-build-standard", "SKILL.md"),
            "agent_installed": _has(agent_roots.get(harness), "rig-stackwright", "rig-stackwright.md",
                                    "rig-stackwright.toml"),
            "surface_wired": next((r["status"] for r in status() if r["surface"] == name), "UNKNOWN"),
            "loaded": "UNVERIFIED", "exercised": "UNVERIFIED", "enforced": "UNVERIFIED",
        }
        row["status"] = ("READY_TO_LOAD" if row["skill_installed"] and row["agent_installed"]
                         and row["surface_wired"] == "WIRED" else "PARTIAL")
        rows.append(row)
    return rows


def _has(root: str | None, name: str, *candidates: str) -> bool:
    """Installed = the bytes are on disk. Two shapes exist because Catalog.install
    copies by src.name: a directory asset (<root>/<name>/SKILL.md) and a flat file
    (<root>/<name>.md). A flat candidate only counts when it is named after the
    asset, so a stray <root>/SKILL.md cannot make an agent look installed."""
    if not root:
        return False
    base = Path(root).expanduser()
    for cand in candidates:
        if (base / name / cand).is_file() or (cand.startswith(name) and (base / cand).is_file()):
            return True
    return (base / name).is_file()


def selftest() -> int:
    import tempfile
    sha = policy_sha()
    assert re.fullmatch(r"[0-9a-f]{64}", sha), sha
    assert "rig-build-standard" in policy_body()
    with tempfile.TemporaryDirectory() as td:
        original = splice("", block())
        assert block() in original
        # idempotent: splicing again changes nothing
        assert splice(original, block()) == original
        # unrelated content preserved byte-exact, block replaced once
        hand = "# My hand-written stuff\n\nkeep me\n\n" + original + "\ntrailer\n"
        assert splice(hand, block()) == hand
        drifted = hand.replace(sha, "0" * 64)
        row = re.search(re.escape(OPEN_) + r"([0-9a-f]{64}) -->", drifted)
        assert row and row.group(1) == "0" * 64
        # fresh install into an empty file leaves only the block
        empty = splice("", block())
        assert empty.strip().startswith(OPEN_) and empty.strip().endswith(CLOSE)
        # authorization cannot be self-issued: no signed row -> refusal
        assert _approval({"kind": "wiring:instruction-surface", "surface": "omp",
                          "policy_sha256": sha}, "self-issued")["ok"] is False
    print("surfaces-render selftest OK")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    if argv[0] == "selftest":
        return selftest()
    import argparse
    ap = argparse.ArgumentParser(prog="surfaces_render", exit_on_error=False)
    ap.add_argument("verb", choices=["check", "render", "stage", "install", "receipts", "policy"])
    ap.add_argument("--surface", choices=list(RUNTIMES))
    ap.add_argument("--approval")
    ap.add_argument("--out")
    try:
        args = ap.parse_args(argv)
    except Exception as exc:  # noqa: BLE001
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2
    try:
        if args.verb == "policy":
            print(block())
            return 0
        if args.verb == "check":
            rows = status()
            print(json.dumps(rows, indent=1, sort_keys=True))
            return 0 if all(r["status"] == "WIRED" for r in rows) else 2
        if args.verb == "render":
            if not args.surface:
                raise SurfaceError("render needs --surface")
            current = surfaces()[args.surface]
            text = current.read_text(encoding="utf-8") if current.is_file() else ""
            rendered = splice(text, block())
            if args.out:
                _atomic(Path(args.out), rendered)
                print(json.dumps({"surface": args.surface, "out": args.out,
                                  "policy_sha256": policy_sha()}, sort_keys=True))
            else:
                print(rendered)
            return 0
        if args.verb == "stage":
            print(json.dumps(stage(args.surface), indent=1, sort_keys=True))
            return 0
        if args.verb == "install":
            if not args.surface:
                raise SurfaceError("install needs --surface")
            print(json.dumps(install(args.surface, args.approval), indent=1, sort_keys=True))
            return 0
        print(json.dumps(receipts(), indent=1, sort_keys=True))
        return 0
    except SurfaceError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
