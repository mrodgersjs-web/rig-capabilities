#!/usr/bin/env python3
"""γ-trace validator — stdlib only. Rigidity is the product.

Validates one JSONL trace file holding three row kinds:

  step        one gamma row per consequential step; all seven fields
              (w_t, e_t, a_t, o_t, proposal, checker_verdict, w_next) must be
              present and non-null. e_t may be [] — an empty delivery set is
              evidence, not a defect.
  attempt     the attempt's terminal outcome. Exactly one row per run_id,
              closed end_reason enum, binary reward.
  attribution one row per RED (reward==0) attempt, exactly one class. Either
              one of the four fixed component classes citing step rows of the
              same run, or the honest terminal state UNATTRIBUTED (cites must
              be empty, evidence must name what is missing). Attribution is
              never guessed.

  --genesis SKILL.md additionally requires a non-empty `source:` and a
  `gamma_provenance:` (or `gamma-provenance:`) field whose cited row ids all
  exist in the trace: a genesis skill that cannot cite the gamma rows that
  motivated it is not admissible.

Exit codes: 0 = valid (UNATTRIBUTED rows are valid but echoed loudly),
2 = any violation (every violation is printed, none swallowed),
other codes are never emitted — a broken run is never green-on-noise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

STEP_FIELDS = ("w_t", "e_t", "a_t", "o_t", "proposal", "checker_verdict", "w_next")
VERDICTS = {"accept", "reject"}
END_REASONS = {"submitted", "verified", "limit", "failed"}
# The class set is fixed by design. A fifth failure kind will be misfiled
# rather than named — see Limitations in SKILL.md.
CLASSES = (
    "skill_missing_or_wrong",          # E: wrong card fired, or none did
    "state_representation_incoherent", # W: believed state diverged from real state
    "retrieval_policy_inadequate",     # rho: right cards existed, were not delivered
    "verifier_missed",                 # C: wrong progress was accepted as done
)
UNATTRIBUTED = "UNATTRIBUTED"
KINDS = {"step", "attempt", "attribution"}


def _nonempty_str(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def check_rows(lines, origin, violations):
    """Parse + validate all rows; return (steps, step_run, attempts, attributions)."""
    steps, attempts, attributions = {}, {}, {}
    step_run, seen_t = {}, {}

    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            violations.append((f"{origin}:{lineno}", f"bad_json: {e}"))
            continue
        if not isinstance(row, dict):
            violations.append((f"{origin}:{lineno}", "row_not_object"))
            continue
        kind = row.get("kind")
        where = f"{origin}:{lineno}"
        if kind not in KINDS:
            violations.append((where, f"unknown_kind: {kind!r}"))
            continue

        if kind == "step":
            rid = row.get("row_id")
            if not _nonempty_str(rid):
                violations.append((where, "step_row_id_missing"))
                continue
            if rid in steps:
                violations.append((where, f"duplicate_row_id: {rid}"))
            run_id = row.get("run_id")
            if not _nonempty_str(run_id):
                violations.append((where, f"step {rid}: run_id_missing"))
            t = row.get("t")
            if not (isinstance(t, int) and not isinstance(t, bool) and t >= 1):
                violations.append((where, f"step {rid}: t_not_positive_int"))
            else:
                key = (run_id, t)
                if key in seen_t:
                    violations.append((where, f"step {rid}: duplicate_t {t} for run {run_id}"))
                seen_t[key] = rid
            for field in STEP_FIELDS:
                if field not in row or row[field] is None:
                    violations.append((where, f"step {rid}: field {field} missing/null"))
                    continue
                val = row[field]
                if field == "e_t":
                    if not isinstance(val, list) or not all(_nonempty_str(x) for x in val):
                        violations.append((where, f"step {rid}: e_t_not_list_of_strings"))
                elif field == "checker_verdict":
                    if val not in VERDICTS:
                        violations.append((where, f"step {rid}: checker_verdict {val!r} not in {sorted(VERDICTS)}"))
                elif not _nonempty_str(val):
                    violations.append((where, f"step {rid}: field {field} empty"))
            steps[rid] = row
            step_run[rid] = run_id

        elif kind == "attempt":
            run_id = row.get("run_id")
            if not _nonempty_str(run_id):
                violations.append((where, "attempt_run_id_missing"))
                continue
            if run_id in attempts:
                violations.append((where, f"duplicate_attempt_row for run {run_id}"))
            if not _nonempty_str(row.get("task")):
                violations.append((where, f"attempt {run_id}: task missing/empty"))
            if row.get("end_reason") not in END_REASONS:
                violations.append((where, f"attempt {run_id}: end_reason {row.get('end_reason')!r} not in closed enum {sorted(END_REASONS)}"))
            reward = row.get("reward")
            if not (reward in (0, 1) and isinstance(reward, int) and not isinstance(reward, bool)):
                violations.append((where, f"attempt {run_id}: reward must be binary int 0|1, got {reward!r}"))
            attempts[run_id] = row

        else:  # attribution
            run_id = row.get("run_id")
            if not _nonempty_str(run_id):
                violations.append((where, "attribution_run_id_missing"))
                continue
            attributions.setdefault(run_id, []).append((where, row))

    return steps, step_run, attempts, attributions


def check_relations(steps, step_run, attempts, attributions, violations):
    # every step resolves to an attempt: orphan count must be 0
    for rid, run_id in step_run.items():
        if run_id not in attempts:
            violations.append((f"step {rid}", f"orphan_step: run_id {run_id!r} has no attempt row"))

    # every RED attempt carries exactly one attribution row
    red_runs = [r for r, a in attempts.items() if a.get("reward") == 0]
    for run_id in red_runs:
        rows = attributions.get(run_id, [])
        if len(rows) == 0:
            violations.append((f"run {run_id}", "red_run_unattributed: RED attempt carries no attribution row"))
        elif len(rows) > 1:
            violations.append((f"run {run_id}", f"multiple_attribution_rows: {len(rows)} rows, exactly 1 allowed"))
    for run_id, rows in attributions.items():
        if run_id not in attempts:
            for where, _ in rows:
                violations.append((where, f"attribution_run_unknown: {run_id!r}"))
        elif attempts[run_id].get("reward") == 1:
            for where, _ in rows:
                violations.append((where, f"attribution_of_green_run: {run_id}"))

    for run_id, rows in attributions.items():
        for where, row in rows:
            classes = row.get("classes")
            if not isinstance(classes, list):
                violations.append((where, f"classes_not_list: {classes!r}"))
                continue
            if len(classes) != 1:
                violations.append((where, f"attribution_class_count: got {len(classes)} classes {classes!r}, exactly one required"))
                continue
            cls = classes[0]
            cites = row.get("cites", [])
            if not isinstance(cites, list):
                violations.append((where, f"cites_not_list: {cites!r}"))
                cites = []
            if not _nonempty_str(row.get("evidence")):
                violations.append((where, "attribution_evidence_missing: attribution must carry non-empty evidence"))
            if cls == UNATTRIBUTED:
                if cites:
                    violations.append((where, f"unattributed_with_cites: {cites!r} — UNATTRIBUTED carries no citations; cite rows or pick a class"))
                continue
            if cls not in CLASSES:
                violations.append((where, f"unknown_class: {cls!r} not in the fixed set {list(CLASSES)} or {UNATTRIBUTED}"))
                continue
            if not cites:
                violations.append((where, f"attribution_without_evidence: class {cls!r} cites no gamma rows — attribution without evidence must be recorded as {UNATTRIBUTED}, never guessed"))
                continue
            for cid in cites:
                if cid not in steps:
                    violations.append((where, f"cite_not_a_row: {cid!r} does not exist in the trace"))
                elif step_run.get(cid) != run_id:
                    violations.append((where, f"cite_cross_run: {cid!r} belongs to run {step_run.get(cid)!r}, not {run_id!r}"))


def check_genesis(path, trace_file, steps, violations):
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        violations.append((path, f"genesis_unreadable: {e}"))
        return
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        violations.append((path, "genesis_missing_frontmatter: no leading --- block"))
        return
    fields = {}
    for line in m.group(1).splitlines():
        fm = re.match(r"\A([A-Za-z0-9_-]+):\s*(.*)\Z", line)
        if fm:
            fields[fm.group(1)] = fm.group(2).strip()
    if not fields.get("source"):
        violations.append((path, "genesis_missing_source: `source:` must be non-empty"))
    prov = fields.get("gamma_provenance") or fields.get("gamma-provenance")
    if not prov:
        violations.append((path, "genesis_missing_gamma_provenance: `gamma_provenance:` must cite the gamma rows that motivated this skill"))
        return
    ids = [x.strip().strip("'\"[]") for x in prov.split(",") if x.strip().strip("'\"[]")]
    if not ids:
        violations.append((path, "genesis_empty_gamma_provenance: no row ids cited"))
        return
    for rid in ids:
        if rid not in steps:
            violations.append((path, f"genesis_provenance_dangling: {rid!r} is not a row in {trace_file}"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="validate_gamma.py", description=__doc__.splitlines()[0])
    ap.add_argument("trace", help="JSONL trace file (step / attempt / attribution rows)")
    ap.add_argument("--genesis", help="SKILL.md whose frontmatter must cite trace row ids")
    args = ap.parse_args(argv)

    violations = []
    try:
        raw = open(args.trace, encoding="utf-8").read()
    except OSError as e:
        print(f"VIOLATION {args.trace}: file_unreadable: {e}")
        return 2
    steps, step_run, attempts, attributions = check_rows(raw.splitlines(), args.trace, violations)
    check_relations(steps, step_run, attempts, attributions, violations)
    if args.genesis:
        check_genesis(args.genesis, args.trace, steps, violations)

    for where, code in violations:
        print(f"VIOLATION {where}: {code}")
    red = [r for r, a in attempts.items() if a.get("reward") == 0]
    unatt = [r for r in red
             for _, row in attributions.get(r, [])
             if isinstance(row.get("classes"), list) and row.get("classes") == [UNATTRIBUTED]]
    print(f"SUMMARY gamma_rows={len(steps)} attempts={len(attempts)} red={len(red)} "
          f"unattributed={len(unatt)} violations={len(violations)}")
    for r in unatt:
        ev = attributions[r][0][1].get("evidence", "")
        print(f"UNATTRIBUTED run {r}: {ev}  (honest gap — improvement work goes to the evidence, not to a guess)")
    return 2 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
