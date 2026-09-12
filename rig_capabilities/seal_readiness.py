"""s8 — seal-readiness assembly: build the commit-gate manifest from live
state and report the gate's OWN verdict WITHOUT consuming anything.

The manifest shape is commit_gate's (d85 / joint / gate-d / verdict) and
readiness() delegates to the PUBLIC commit_gate.check(): same code path,
same anchor short-circuit, no seams, no second opinion that could diverge
from the authoritative gate. This module never approves, never arms,
never consumes — it answers "what is still open before the SHA can be
sealed?" and refuses to paraphrase the gate.

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
    """The authoritative gate verdict, verbatim. Non-consuming by construction:
    commit_gate.check() is the documented non-consuming entrypoint."""
    v = commit_gate.check(repo, sha, manifest)
    return {"sha": sha, "ready": bool(v["admitted"]), "gate_verdict": v}


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
        m = assemble(sha_build="b.json", cert="c.json", trials="t.jsonl",
                     cells=["C01"], process_id="P", action_file="a.json",
                     verdict_artifact="v.json")
        want = {"d85": {"build": "b.json", "cert": "c.json"},
                "joint": {"trials": "t.jsonl", "cells": ["C01"]},
                "gate-d": {"process_id": "P", "action_file": "a.json"},
                "verdict": {"artifact": "v.json"}}
        if m != want:
            errs.append(f"assemble shape drift: {m}")
        # readiness IS the gate's verdict: same object, not a paraphrase
        gate = commit_gate.check(repo, "0" * 40, m)
        r = readiness(repo, "0" * 40, m)
        if r["gate_verdict"] != gate or r["ready"] != gate["admitted"]:
            errs.append("readiness diverged from commit_gate.check")
        if r["ready"] or not gate["refusals"]:
            errs.append(f"empty repo not refused: {r}")
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
        # no consumption: readiness must not write anything into the repo
        leftovers = [str(p.relative_to(repo)) for p in repo.rglob("*")
                     if p.is_file()]
        if leftovers:
            errs.append(f"readiness wrote state: {leftovers}")
    print(json.dumps({"ok": not errs, "errors": errs}))
    return 0 if not errs else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("assemble", "report"):
        sys.exit(main())
    sys.exit(selftest())
