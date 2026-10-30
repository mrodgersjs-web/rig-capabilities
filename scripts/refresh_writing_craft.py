#!/usr/bin/env python3
"""Corpus freshness job (v15.5): resume the writing-craft scrape, then rebuild
baselines. Idempotent — scrape script skips manifest entries it already has.
Exit 2 + named BLOCKED reason when nothing can advance (YouTube IP block)."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd: list[str]) -> dict:
    r = subprocess.run([sys.executable] + cmd, capture_output=True, text=True, timeout=1800)
    return {"cmd": " ".join(cmd), "exit": r.returncode, "tail": (r.stdout or r.stderr).strip().splitlines()[-3:]}


def main() -> int:
    steps = [run([str(HERE / "scrape_writing_craft.py")]), run([str(HERE / "comms_baselines.py")])]
    report = {"steps": steps}
    print(json.dumps(report, indent=2))
    return 0 if any(s["exit"] == 0 for s in steps) else 2


if __name__ == "__main__":
    raise SystemExit(main())
