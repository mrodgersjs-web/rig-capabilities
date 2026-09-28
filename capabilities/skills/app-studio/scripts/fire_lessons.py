#!/usr/bin/env python3
"""Which App Studio lessons fire for a task, and which checks the run now owes.

Reads the typed ledger (default ../references/lessons.jsonl, schema owned by
experience-lesson-records) and matches each ACTIVE lesson's trigger against the task
text. Every fired lesson names a mandated check: the run must carry a receipt for it,
and validate_lessons.py --run enforces that at close.

Usage:
  fire_lessons.py "<task text>" [--ledger PATH] [--json] [--receipts]
    --receipts  print receipt rows (kind=receipt) to paste into a run.jsonl once each
                check has actually been performed - never before.
Exit 0 always on a readable ledger (zero fired lessons is a legal answer);
exit 1 on a missing or malformed ledger. Stdlib only. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT = Path(__file__).resolve().parent.parent / "references" / "lessons.jsonl"


def fired(task: str, ledger: Path) -> list[dict]:
    out = []
    for n, line in enumerate(ledger.read_text().splitlines(), 1):
        if not line.strip():
            continue
        les = json.loads(line)
        if les.get("status") != "active":
            continue
        trig = les["trigger"]
        hit = re.search(trig, task) if les.get("match") == "regex" else trig.lower() in task.lower()
        if hit:
            out.append(les)
    return out


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--ledger", type=Path, default=DEFAULT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--receipts", action="store_true")
    a = ap.parse_args(argv)
    try:
        hits = fired(a.task, a.ledger)
    except (OSError, ValueError, KeyError, re.error) as e:
        print(f"ledger unreadable: {e}", file=sys.stderr)
        return 1
    if a.json:
        print(json.dumps([{k: h[k] for k in ("lesson_id", "mandated_check")} for h in hits], indent=1))
    elif a.receipts:
        for h in hits:
            print(json.dumps({"kind": "receipt", "check": h["mandated_check"], "detail": "<what you ran and saw>"}))
    else:
        print(f"{len(hits)} lesson(s) fire for this task")
        for h in hits:
            print(f"- {h['lesson_id']}: {h['mandated_check']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
