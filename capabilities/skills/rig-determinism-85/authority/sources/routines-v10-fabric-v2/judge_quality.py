#!/usr/bin/env python3
"""Quality judge for routine fires (routines-v10).

Samples final assistant outputs of routine fires and scores each with the
same judge the estate uses (Jev text via ~/.rig/bin/aside-jev `score`), so a
load-test cohort can be compared against a control cohort at equal quality.

Cohorts are selected by routine metadata label ("loadtest"/"client-ops") or by
explicit routine ids. Writes one JSON report per run into the fabric state dir.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

DB_PATH = os.environ.get("RIG_ROUTINE_DB", str(Path.home() / ".aside/u/0/state.db"))
STATE_DIR = Path(os.environ.get("RIG_FABRIC_STATE", str(Path.home() / ".rig/state/routine-fabric")))
JEV = str(Path.home() / ".rig/bin/aside-jev")
LEVELS = "degraded,partial,clean"
QUESTION = ("Is this routine fire's final response a clean, complete, correct "
            "fulfillment of the routine prompt it was given?")

LEVEL_VALUE = {"degraded": 0.0, "partial": 0.5, "clean": 1.0}


def sample(db_path: str, label: str | None, ids: list[str],
           n: int, since_epoch: float) -> list[dict]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    if ids:
        ph = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT s.id sid, s.routine_id rid, r.name rname, r.prompt rprompt, "
            f"t.final_assistant_message msg, s.status st, s.created_at ts "
            f"FROM sessions s JOIN routines r ON r.id = s.routine_id "
            f"LEFT JOIN session_turns t ON t.session_id = s.id "
            f"WHERE s.routine_id IN ({ph}) AND s.created_at >= ? "
            f"AND t.final_assistant_message IS NOT NULL", (*ids, int(since_epoch))).fetchall()
    else:
        rows = conn.execute(
            "SELECT s.id sid, s.routine_id rid, r.name rname, r.prompt rprompt, "
            "t.final_assistant_message msg, s.status st, s.created_at ts "
            "FROM sessions s JOIN routines r ON r.id = s.routine_id "
            "LEFT JOIN session_turns t ON t.session_id = s.id "
            "WHERE r.metadata LIKE ? AND s.created_at >= ? "
            "AND t.final_assistant_message IS NOT NULL",
            (f'%"{label}"%', int(since_epoch))).fetchall()
    conn.close()
    picked = random.sample(rows, min(n, len(rows)))
    return [dict(r) for r in picked]


def judge_one(row: dict) -> str:
    # Prompt is the rubric context; the output is what gets judged.
    state = f"ROUTINE PROMPT:\n{row['rprompt'][:4000]}\n\nROUTINE OUTPUT:\n{row['msg'][:4000]}"
    p = subprocess.run([JEV, "score", QUESTION, "--state", state, "--levels", LEVELS],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"aside-jev exit {p.returncode}: {p.stderr[:200]}")
    out = json.loads(p.stdout[p.stdout.index("{"):])
    ans = out.get("answers", {}).get("answer", {})
    if ans.get("type") != "score" or "score" not in ans:
        raise RuntimeError(f"unexpected Jev answer shape: {out}")
    level = ans["legend"][str(int(round(ans["score"])))]
    return level if level in LEVEL_VALUE else "degraded"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default=None, help="routine metadata label (e.g. loadtest)")
    ap.add_argument("--ids", default=None, help="comma-separated routine ids")
    ap.add_argument("--cohort", required=True, help="cohort name for the report")
    ap.add_argument("--sample", type=int, default=10)
    ap.add_argument("--since-epoch", type=float, default=time.time() - 86400)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    ids = args.ids.split(",") if args.ids else []
    rows = sample(DB_PATH, args.label, ids, args.sample, args.since_epoch)
    results = []
    for row in rows:
        level = judge_one(row)
        results.append({"session_id": row["sid"], "routine_id": row["rid"],
                        "routine_name": row["rname"], "status": row["st"],
                        "level": level, "value": LEVEL_VALUE[level]})
    values = [r["value"] for r in results]
    report = {
        "cohort": args.cohort,
        "judge": "aside-jev score (Jev text), levels degraded,partial,clean",
        "question": QUESTION,
        "sampled": len(results),
        "mean_value": (sum(values) / len(values)) if values else None,
        "share_clean": (sum(1 for v in values if v == 1.0) / len(values)) if values else None,
        "levels": {lv: sum(1 for r in results if r["level"] == lv) for lv in LEVEL_VALUE},
        "results": results,
    }
    out_path = Path(args.out) if args.out else STATE_DIR / f"judge-{args.cohort}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
