#!/usr/bin/env python3
"""List the Traject lessons whose trigger fires on a task text.

Usage: fire_lessons.py "<the task text>"
Prints, one per line, the lesson id and the mandated check this run owes a receipt for.
Exit 0 always; exit 1 on usage error. Stdlib only. Reads only references/lessons.jsonl.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LEDGER = Path(__file__).resolve().parent.parent / "references" / "lessons.jsonl"


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1 or not argv[0].strip():
        print("usage: fire_lessons.py \"<the task text>\"", file=sys.stderr)
        return 1
    text = argv[0]
    fired = 0
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") != "active":
            continue
        trig, kind = row.get("trigger", ""), row.get("match")
        if kind == "substring":
            hit = trig in text
        else:
            try:
                hit = re.search(trig, text) is not None
            except re.error:
                hit = False
        if hit:
            fired += 1
            print(f"{row['lesson_id']}\t{row['mandated_check']}")
    print(f"# {fired} lesson(s) fire on this task; each owes one receipt in run.jsonl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
