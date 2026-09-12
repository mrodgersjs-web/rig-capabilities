"""s8 — seal-readiness assembly: build the commit-gate manifest from live
state and report each receipt's status WITHOUT consuming anything.

The manifest shape is commit_gate's (d85 / joint / gate-d / verdict). This
module never approves, never arms, never consumes: it answers "what is
still open before the SHA can be sealed?" and points at the exact owner of
each open item (certifier re-cert, trial rows, Gate-D human approval,
cross-family verdict). A missing artifact or unavailable authority is
reported as OPEN/REFUSED, never as a pass.

Usage:
  python3 -m rig_capabilities.seal_readiness assemble --sha SHA ...
  python3 -m rig_capabilities.seal_readiness report   --sha SHA ...
  python3 rig_capabilities/seal_readiness.py        # selftest
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
try:
    from rig_capabilities import commit_gate
except ImportError:  # direct `python3 rig_capabilities/seal_readiness.py`
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from rig_capabilities import commit_gate


def assemble(*, sha_build: str, cert: str, trials: str, cells: list[str],
             process_id: str, action_file: str, verdict_artifact: str) -> dict:
    """The commit_gate manifest, assembled in code so the shape cannot drift."""
    return {
        "d85": {"build": sha_build, "cert": cert},
        "joint": {"trials": trials, "cells": list(cells)},
        "gate-d": {"process_id": process_id, "action_file": action_file},
        "verdict": {"artifact": verdict_artifact},
    }


def readiness(repo: Path, sha: str, manifest: dict) -> dict:
    """Per-receipt status. Non-consuming: verify paths only, never arm."""
    out: dict = {"sha": sha, "receipts": {}, "blockers": []}

    def run(kind, fn):
        try:
            errs = fn()
        except Exception as e:  # unavailable authority counts as REFUSED
            errs = [f"{type(e).__name__}: {e}"]
        out["receipts"][kind] = "PASS" if not errs else "REFUSED"
        if errs:
            out["blockers"].append({kind: errs})

    anchor = commit_gate._anchor_errors(repo, None)
    out["anchor"] = ("SEALED" if not anchor
                     else "; ".join(anchor) or "UNSEALED")
    if anchor:
        # nothing under d85 can pass while the anchor is unsealed; report it
        # once as the named blocker instead of four identical refusals
        out["receipts"]["d85"] = "BLOCKED_BY_ANCHOR"
        out["blockers"].append({"d85": anchor})
    else:
        run("d85", lambda: commit_gate._verify_d85(
            repo, manifest["d85"], sha))
    run("joint", lambda: commit_gate.verify_joint(
        repo, manifest["joint"], sha))
    run("gate-d", lambda: commit_gate._verify_gate_d(
        repo, manifest["gate-d"], sha))
    run("verdict", lambda: commit_gate.verify_verdict(
        repo, manifest["verdict"], sha))
    out["ready"] = all(v == "PASS" for v in out["receipts"].values())
    return out


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="seal_readiness")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("assemble", "report"):
        p = sub.add_parser(name)
        p.add_argument("--repo", default=".")
        p.add_argument("--sha", required=True)
        p.add_argument("--build", required=True)
        p.add_argument("--cert", required=True)
        p.add_argument("--trials", required=True)
        p.add_argument("--cells", required=True, help="comma-separated")
        p.add_argument("--process-id", required=True)
        p.add_argument("--action-file", required=True)
        p.add_argument("--verdict-artifact", required=True)
    a = ap.parse_args(argv)
    manifest = assemble(
        sha_build=a.build, cert=a.cert, trials=a.trials,
        cells=a.cells.split(","), process_id=a.process_id,
        action_file=a.action_file, verdict_artifact=a.verdict_artifact)
    if a.cmd == "assemble":
        print(json.dumps(manifest, indent=2, sort_keys=True))
        return 0
    print(json.dumps(readiness(Path(a.repo).resolve(), a.sha, manifest),
                     indent=2, sort_keys=True))
    return 0


def selftest() -> int:
    import subprocess
    import tempfile
    errs = []
    with tempfile.TemporaryDirectory() as td:
        repo = Path(td)
        (repo / "rig_capabilities").mkdir()
        (repo / ".git").mkdir()
        m = assemble(sha_build="b.json", cert="c.json", trials="t.jsonl",
                     cells=["C01"], process_id="P", action_file="a.json",
                     verdict_artifact="v.json")
        want = {"d85": {"build": "b.json", "cert": "c.json"},
                "joint": {"trials": "t.jsonl", "cells": ["C01"]},
                "gate-d": {"process_id": "P", "action_file": "a.json"},
                "verdict": {"artifact": "v.json"}}
        if m != want:
            errs.append(f"assemble shape drift: {m}")
        # readiness on an empty repo: NOTHING passes, NOTHING is consumed,
        # and the unsealed anchor is the named d85 blocker
        r = readiness(repo, "0" * 40, m)
        if r["ready"]:
            errs.append("empty repo reported ready")
        if r["receipts"]["d85"] != "BLOCKED_BY_ANCHOR":
            errs.append(f"anchor not named for d85: {r['receipts']['d85']}")
        for k in ("joint", "gate-d", "verdict"):
            if r["receipts"][k] != "REFUSED":
                errs.append(f"{k} not refused on empty repo")
        # report CLI runs the same path and exits 0 with JSON
        proc = subprocess.run(
            [sys.executable, "-m", "rig_capabilities.seal_readiness",
             "report", "--repo", td, "--sha", "0" * 40,
             "--build", "b.json", "--cert", "c.json", "--trials", "t.jsonl",
             "--cells", "C01", "--process-id", "P",
             "--action-file", "a.json", "--verdict-artifact", "v.json"],
            capture_output=True, text=True, timeout=60)
        try:
            got = json.loads(proc.stdout)
        except json.JSONDecodeError:
            errs.append(f"CLI not json: {proc.stdout[:80]}{proc.stderr[:120]}")
            got = {}
        if proc.returncode != 0 or got.get("ready") is not False:
            errs.append(f"CLI wrong: rc={proc.returncode} ready={got.get('ready')}")
        # no consumption: no approval markers or consumed files anywhere
        if any(p.is_file() for p in repo.rglob("*") if p.parent != repo / ".git"):
            leftovers = [str(p.relative_to(repo)) for p in repo.rglob("*")
                         if p.is_file() and ".git" not in p.parts]
            if leftovers:
                errs.append(f"readiness wrote state: {leftovers}")
    print(json.dumps({"ok": not errs, "errors": errs}))
    return 0 if not errs else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("assemble", "report"):
        sys.exit(main())
    sys.exit(selftest())
