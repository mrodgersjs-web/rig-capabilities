#!/usr/bin/env python3
"""Red/green fixture proof for the s1gate money rubrics.

Run:  python3 run_fixtures.py            -- every green fixture must PASS (gate exit 0),
                                             every red fixture must ESCALATE/BLOCK (exit 1 or 2).
      python3 run_fixtures.py --selftest -- plant one flipped expectation and prove this
                                             check reports it (the run must come back red).

Exit codes: 0 ok, 1 mismatch (or, in --selftest mode, the planted failure was NOT caught).
Gate exit 3 (usage/config error) is reported as infra-error and counts as a mismatch.
Expectations live in expected.json next to this file: {rubric: {fixture: "green"|"red"}}.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # rig-capabilities repo root (rubric discovery cwd)
GATE = Path.home() / ".rig" / "bin" / "rig-s1gate"


def load_rows() -> list[tuple[str, str, str]]:
    expected = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))
    return [(r, f, e) for r, fixtures in expected.items() for f, e in fixtures.items()]


def run(rows: list[tuple[str, str, str]]) -> int:
    mismatches = 0
    for rubric, name, want in rows:
        path = HERE / rubric / name
        proc = subprocess.run(
            [str(GATE), "check", rubric, "--file", str(path),
             "--subject", f"fixture:{rubric}/{name}", "--json"],
            capture_output=True, text=True, cwd=ROOT,
        )
        code = proc.returncode
        got = "infra-error" if code == 3 else ("green" if code == 0 else "red")
        ok = got == want
        mismatches += not ok
        try:
            out = json.loads(proc.stdout)
            verdict, decision = out.get("verdict", "?"), out.get("decision_id", "?")
        except Exception:
            verdict, decision = "?", "?"
        print(f"{rubric:14} {name:22} want={want:6} got={got:11} verdict={verdict:9} "
              f"decision={decision} {'OK' if ok else 'MISMATCH'}")
    return mismatches


def main() -> int:
    rows = load_rows()
    if "--selftest" in sys.argv:
        # Planted failure: flip the first expectation; this check must notice (red).
        flipped = list(rows)
        r, f, e = flipped[0]
        flipped[0] = (r, f, "red" if e == "green" else "green")
        mismatches = run(flipped)
        caught = mismatches >= 1
        print(f"SELFTEST (planted flip of {r}/{f}): {mismatches} mismatch(es) detected -> "
              f"{'check is live (red proven)' if caught else 'CHECK IS THEATER: planted failure not caught'}")
        return 0 if caught else 1
    mismatches = run(rows)
    print(f"RUN: {len(rows)} fixtures, {mismatches} mismatch(es)")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
