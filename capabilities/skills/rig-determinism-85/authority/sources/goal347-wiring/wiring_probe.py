#!/usr/bin/env python3
"""Goal 347 wiring probe: one real call per adopted repo, non-zero on any miss.

KPI mode (--count): prints the number of candidates whose registered probe
command exits 0 (the goal's single number: wired repos with a verified real
run). Done-test mode (no flag): exits 0 only when ALL 8 candidates pass.

A candidate's probe lives in ../probes.json (written at wire time, stage B):
{"jake-pai-mcp": "omp mcp list 2>/dev/null | grep -q jake-pai", ...}. No
probe registered = red, never optimistic.
"""
import json
import subprocess
import sys
from pathlib import Path

G = Path(__file__).resolve().parent.parent
CANDIDATES = [
    "nanobrowser",
    "jake-pai-mcp",
    "rig-ai-engineering",
    "rig-marketplace",
    "rig-os-agency",
    "goals-variant-b-console",
    "mrodgersjs-web-teammate",
    "app-factory-studio",
]
PROBES = G / "probes.json"


def run_probe(cmd: str) -> bool:
    try:
        return subprocess.run(cmd, shell=True, capture_output=True,
                              timeout=300).returncode == 0
    except Exception:
        return False


def main() -> int:
    probes = json.loads(PROBES.read_text()) if PROBES.exists() else {}
    wired, misses = 0, []
    for c in CANDIDATES:
        cmd = probes.get(c)
        if not cmd:
            misses.append(f"{c}: no probe registered")
            continue
        if run_probe(cmd):
            wired += 1
        else:
            misses.append(f"{c}: probe red: {cmd}")
    if "--count" in sys.argv:
        print(wired)
        return 0
    for m in misses:
        print(m, file=sys.stderr)
    return 0 if wired == len(CANDIDATES) else 1


if __name__ == "__main__":
    sys.exit(main())
