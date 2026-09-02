#!/usr/bin/env python3
"""Enforce the experience-lesson-record contract mechanically.

A lesson is a typed, evidence-bearing rule distilled at run close: "when THIS
condition recurs, THIS check is mandatory, and here is the run that earned the
lesson". The failure mode this closes is the reflective-journal that reads as
learning and changes nothing — a lesson with no trigger you can match, no check
you can enforce, or no evidence it was ever paid for.

Two files:

  lessons.jsonl  — the ledger. One JSON object per line, each a lesson with the
                   six required fields below.
  run.jsonl      — one agent run. `task` row states the task; `receipt` rows
                   record checks that were actually performed; `close` row ends
                   the run.

The check: for every ACTIVE lesson whose `trigger` matches the run's task, the
run MUST carry a receipt naming that lesson's `mandated_check`. A RETIRED lesson
is skipped (that is the whole point of retiring one), so an honest retirement is
GREEN, never a silent hole.

Exit codes (the honesty contract):
  0  every lesson well-formed AND every active-matching lesson has its receipt
  1  usage / file-not-found (a refusal to judge, not a verdict)
  2  a contract violation: a malformed lesson, an uncompilable trigger, an
     evidence-less lesson, an unknown status, or a matched active lesson whose
     mandated check has no receipt in the run

Stdlib only. Reads only the paths it is given. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED = ("lesson_id", "trigger", "match", "mandated_check", "evidence", "status")
STATUSES = {"active", "retired"}
MATCH_KINDS = {"substring", "regex"}


def _nonempty_str(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _load_jsonl(path: Path, origin: str, violations: list):
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            violations.append((f"{origin}:{lineno}", f"bad_json: {e}"))
            continue
        if not isinstance(obj, dict):
            violations.append((f"{origin}:{lineno}", "row_not_object"))
            continue
        rows.append((lineno, obj))
    return rows


def check_lessons(rows, origin, violations):
    """Validate lesson shape; return {lesson_id: lesson} for well-formed rows."""
    lessons = {}
    for lineno, row in rows:
        where = f"{origin}:{lineno}"
        missing = [f for f in REQUIRED if f not in row]
        if missing:
            violations.append((where, f"missing_fields: {','.join(missing)}"))
            continue
        lid = row["lesson_id"]
        if not _nonempty_str(lid):
            violations.append((where, "lesson_id_empty"))
            continue
        if lid in lessons:
            violations.append((where, f"duplicate_lesson_id: {lid}"))
        if not _nonempty_str(row["trigger"]):
            violations.append((where, f"{lid}: trigger_empty"))
        if row["match"] not in MATCH_KINDS:
            violations.append((where, f"{lid}: match_kind {row['match']!r} not in {sorted(MATCH_KINDS)}"))
        elif row["match"] == "regex":
            try:
                re.compile(row["trigger"])
            except re.error as e:
                violations.append((where, f"{lid}: trigger_not_a_regex: {e}"))
        if not _nonempty_str(row["mandated_check"]):
            violations.append((where, f"{lid}: mandated_check_empty"))
        ev = row["evidence"]
        # A lesson with no evidence is a guess. This is the load-bearing clause:
        # a lesson must cite at least one run/row-id that earned it.
        if not (isinstance(ev, list) and ev and all(_nonempty_str(x) for x in ev)):
            violations.append((where, f"{lid}: evidence_must_be_nonempty_string_list"))
        if row["status"] not in STATUSES:
            violations.append((where, f"{lid}: unknown_status {row['status']!r}"))
        lessons[lid] = row
    return lessons


def _matches(lesson, task_text: str) -> bool:
    if lesson["match"] == "substring":
        return lesson["trigger"] in task_text
    try:
        return re.search(lesson["trigger"], task_text) is not None
    except re.error:
        return False        # already reported as a violation


def check_run(lessons, run_rows, origin, violations):
    """A matched active lesson must have a receipt for its mandated check."""
    task_text = None
    receipts = set()
    closed = False
    for lineno, row in run_rows:
        where = f"{origin}:{lineno}"
        kind = row.get("kind")
        if kind == "task":
            if not _nonempty_str(row.get("text")):
                violations.append((where, "task_text_missing"))
            task_text = row.get("text") or ""
        elif kind == "receipt":
            chk = row.get("check")
            if not _nonempty_str(chk):
                violations.append((where, "receipt_check_missing"))
            else:
                receipts.add(chk)
        elif kind == "close":
            closed = True
        else:
            violations.append((where, f"unknown_run_kind: {kind!r}"))
    if task_text is None:
        violations.append((origin, "run_has_no_task_row"))
        return
    if not closed:
        violations.append((origin, "run_never_closed"))
    for lid, lesson in lessons.items():
        if lesson["status"] != "active":
            continue                       # retired lessons are intentionally skipped
        if lesson["match"] not in MATCH_KINDS or not _nonempty_str(lesson["trigger"]):
            continue                       # malformed lesson already reported
        if _matches(lesson, task_text) and lesson["mandated_check"] not in receipts:
            violations.append(
                (origin, f"{lid}: task matched trigger but no receipt for "
                         f"mandated check {lesson['mandated_check']!r}"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="validate experience-lesson records")
    ap.add_argument("lessons", help="lessons.jsonl ledger")
    ap.add_argument("--run", help="a run.jsonl to check against the ledger")
    args = ap.parse_args(argv)

    lp = Path(args.lessons)
    if not lp.is_file():
        print(f"lessons file not found: {lp}", file=sys.stderr)
        return 1

    violations: list = []
    lesson_rows = _load_jsonl(lp, lp.name, violations)
    lessons = check_lessons(lesson_rows, lp.name, violations)

    if args.run:
        rp = Path(args.run)
        if not rp.is_file():
            print(f"run file not found: {rp}", file=sys.stderr)
            return 1
        run_rows = _load_jsonl(rp, rp.name, violations)
        check_run(lessons, run_rows, rp.name, violations)

    if violations:
        for where, msg in violations:
            print(f"VIOLATION {where}: {msg}")
        print(f"\nlessons: {len(violations)} violation(s); "
              f"{len(lessons)} well-formed lesson(s)")
        return 2
    print(f"OK {lp.name}: {len(lessons)} lesson(s)"
          + (f" checked against {Path(args.run).name}" if args.run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
