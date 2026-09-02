#!/usr/bin/env python3
"""Enforce task/instruction authority over skill authority at context assembly.

A loaded skill body is, token by token, an instruction stream competing with
the task the operator actually gave. Without a precedence rule applied in code
at assembly time, a skill that happens to be in context acts as a standing
override of both the task and the model's own judgement — and the compliance
is silent: nobody logs that the skill won.

This gate adjudicates one assembly record: the sources whose directives were
put in front of the model (task / harness / skill), the directives themselves,
and what the run RESOLVED when two directives contradicted. Contradiction is
mechanical, not vibes: two directives contradict when they bind the same
`subject` and their `require` value-sets are disjoint — no world satisfies
both. When they contradict, authority order is fixed:

    task > harness > skill

A skill may not override the task, nor a harness component (a guard, a gate),
nor the files it lives beside. The run's options on a conflict are exactly
two: side with the HIGHER-authority directive, or `escalate` (hold both steps,
ask the operator). Siding with the skill is an inversion; not noticing the
conflict is a miss; resolving with no named rule is an unlogged precedence,
which is how silent compliance becomes the norm. Executing the losing skill
step anyway — the silent-compliance leg the source's own done-test seeds — is
the deepest violation: the resolution papered over, the skill ran.

Exit codes (the honesty contract):
  0  CLEAN — every detected conflict has a record, each record sides with the
     higher authority (or escalates), cites a rule, and no losing step ran
  1  usage / file-not-found — a refusal to judge, never a verdict
  2  a contract violation, one of:
       AUTHORITY_INVERSION    the resolution sided with the lower authority
       CONFLICT_UNDETECTED    directives contradict and no record names the pair
       RULE_UNCITED           a conflict record carries no precedence rule
       EXECUTED_LOSING_STEP   the run executed the losing side's directive
       RESOLUTION_PHANTOM     a record claims a conflict this gate cannot reproduce
       RECORD_MALFORMED       the assembly record is outside the closed grammar

Stdlib only. Reads ONLY the one path it is given as argv[1]. Writes nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCHEMA = "rig.authority.assembly.v1"
VERDICT_SCHEMA = "rig.authority.verdict.v1"
RANK = {"task": 3, "harness": 2, "skill": 1}
DECISIONS = {"task", "harness", "skill", "escalate"}
TOP_KEYS = {"schema", "sources", "resolution"}
SOURCE_KEYS = {"id", "authority", "directives"}
DIRECTIVE_KEYS = {"id", "text", "subject", "require"}
RESOLUTION_KEYS = {"conflicts", "executed"}
RECORD_KEYS = {"pair", "decision", "precedence_rule"}

# violation classes → exit is always 2; the class names are the product
CLASSES = ("AUTHORITY_INVERSION", "CONFLICT_UNDETECTED", "RULE_UNCITED",
           "EXECUTED_LOSING_STEP", "RESOLUTION_PHANTOM", "RECORD_MALFORMED")


def _nonempty_str(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _keyable(x):
    """Type-tagged scalar key so True and 1 stay distinct in a value-set."""
    return (type(x).__name__, x)


def _require_set(v, viol, where):
    """require: one scalar or a non-empty list of scalars -> frozenset.

    Semantics: the directive asserts the outcome lies in this set. Two
    directives on one subject can coexist iff their sets intersect.
    """
    items = v if isinstance(v, list) else [v]
    if isinstance(v, list) and not v:
        viol.append(("RECORD_MALFORMED", f"{where}: require list is empty"))
        return None
    if any(isinstance(x, (list, dict)) for x in items):
        viol.append(("RECORD_MALFORMED", f"{where}: require holds a non-scalar"))
        return None
    return frozenset(_keyable(x) for x in items)


def parse_record(obj, viol):
    """Parse the closed grammar; return (sources, resolution_ok)."""
    if not isinstance(obj, dict):
        viol.append(("RECORD_MALFORMED", "top level is not an object"))
        return [], False
    extra = set(obj) - TOP_KEYS
    if extra:
        viol.append(("RECORD_MALFORMED",
                     f"unknown top-level keys: {sorted(extra)}"))
    if obj.get("schema") != SCHEMA:
        viol.append(("RECORD_MALFORMED",
                     f"schema is {obj.get('schema')!r}, expected {SCHEMA!r}"))
    sources = []
    raw_sources = obj.get("sources")
    if not isinstance(raw_sources, list) or not raw_sources:
        viol.append(("RECORD_MALFORMED", "sources missing or empty"))
        return [], True
    seen_src = set()
    seen_dir = set()
    for i, src in enumerate(raw_sources):
        where = f"sources[{i}]"
        if not isinstance(src, dict) or set(src) != SOURCE_KEYS:
            viol.append(("RECORD_MALFORMED",
                         f"{where}: keys must be exactly {sorted(SOURCE_KEYS)}"))
            continue
        sid = src["id"]
        if not _nonempty_str(sid):
            viol.append(("RECORD_MALFORMED", f"{where}.id must be a non-empty string"))
            continue
        if sid in seen_src:
            viol.append(("RECORD_MALFORMED", f"duplicate source id {sid!r}"))
            continue
        seen_src.add(sid)
        authority = src["authority"]
        if authority not in RANK:
            viol.append(("RECORD_MALFORMED",
                         f"{where}.authority {authority!r} outside "
                         f"{sorted(RANK, key=RANK.get, reverse=True)}"))
            continue
        raw_dirs = src["directives"]
        if not isinstance(raw_dirs, list) or not raw_dirs:
            viol.append(("RECORD_MALFORMED",
                         f"{where}.directives missing or empty"))
            continue
        directives = []
        for j, d in enumerate(raw_dirs):
            dwhere = f"{where}.directives[{j}]"
            if not isinstance(d, dict) or set(d) != DIRECTIVE_KEYS:
                viol.append(("RECORD_MALFORMED",
                             f"{dwhere}: keys must be exactly {sorted(DIRECTIVE_KEYS)}"))
                continue
            did, text, subject = d["id"], d["text"], d["subject"]
            bad = False
            if not _nonempty_str(did):
                viol.append(("RECORD_MALFORMED", f"{dwhere}.id must be non-empty"))
                bad = True
            elif did in seen_dir:
                viol.append(("RECORD_MALFORMED", f"duplicate directive id {did!r}"))
                bad = True
            else:
                seen_dir.add(did)
            if not _nonempty_str(text):
                viol.append(("RECORD_MALFORMED",
                             f"{dwhere}.text must be non-empty — an untexted directive "
                             f"cannot be named in a resolution"))
                bad = True
            if not _nonempty_str(subject):
                viol.append(("RECORD_MALFORMED", f"{dwhere}.subject must be non-empty"))
                bad = True
            req = _require_set(d["require"], viol, dwhere)
            if req is None:
                bad = True
            if not bad:
                directives.append({"id": did, "text": text, "subject": subject,
                                   "require": req})
        sources.append({"id": sid, "authority": authority,
                        "directives": directives})
    return sources, True


def detect_conflicts(sources):
    """Directive pairs across DIFFERENT ranks, same subject, disjoint requires.

    Same-rank pairs (skill vs skill) are out of scope for THIS gate: the
    precedence it encodes is task > harness > skill, and a peer clash has no
    named winner here. Same-source pairs are the author's own inconsistency,
    not an assembly conflict.
    """
    flat = [(src, d) for src in sources for d in src["directives"]]
    found = []
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            (sa, da), (sb, db) = flat[i], flat[j]
            if sa is sb or RANK[sa["authority"]] == RANK[sb["authority"]]:
                continue
            if da["subject"] != db["subject"]:
                continue
            if da["require"] & db["require"]:
                continue  # a world satisfies both: compatible, not a conflict
            hi, lo = ((sa, da), (sb, db)) if RANK[sa["authority"]] > RANK[sb["authority"]] \
                else ((sb, db), (sa, da))
            found.append({"pair": tuple(sorted((da["id"], db["id"]))),
                          "winner": hi[1]["id"], "winner_authority": hi[0]["authority"],
                          "loser": lo[1]["id"], "subject": da["subject"]})
    return found


def adjudicate(sources, conflicts, obj, viol):
    """Every detected conflict needs a rule-cited record siding with the
    higher authority (or an escalation), and the losing step must not run."""
    by_id = {d["id"]: (src, d) for src in sources for d in src["directives"]}
    resolution = obj.get("resolution")
    if not isinstance(resolution, dict) or not set(resolution) <= RESOLUTION_KEYS \
            or "conflicts" not in resolution or "executed" not in resolution:
        viol.append(("RECORD_MALFORMED",
                     "resolution must be an object with exactly 'conflicts' and 'executed'"))
        return False
    raw_records = resolution["conflicts"]
    executed = resolution["executed"]
    if not isinstance(raw_records, list):
        viol.append(("RECORD_MALFORMED", "resolution.conflicts must be a list"))
        return False
    if not isinstance(executed, list) or any(not _nonempty_str(e) for e in executed) \
            or len(set(executed)) != len(executed):
        viol.append(("RECORD_MALFORMED",
                     "resolution.executed must be a list of unique directive ids"))
        return False
    unknown = sorted(set(executed) - set(by_id))
    if unknown:
        viol.append(("RECORD_MALFORMED",
                     f"resolution.executed names unknown directives: {unknown}"))
        return False

    records = {}
    for i, rec in enumerate(raw_records):
        where = f"resolution.conflicts[{i}]"
        if not isinstance(rec, dict) or set(rec) != RECORD_KEYS:
            viol.append(("RECORD_MALFORMED",
                         f"{where}: keys must be exactly {sorted(RECORD_KEYS)}"))
            continue
        pair = rec["pair"]
        if not (isinstance(pair, list) and len(pair) == 2
                and all(_nonempty_str(p) for p in pair) and len(set(pair)) == 2):
            viol.append(("RECORD_MALFORMED",
                         f"{where}.pair must name exactly two directive ids"))
            continue
        if any(p not in by_id for p in pair):
            viol.append(("RECORD_MALFORMED",
                         f"{where}.pair names unknown directives: {sorted(pair)}"))
            continue
        if rec["decision"] not in DECISIONS:
            viol.append(("RECORD_MALFORMED",
                         f"{where}.decision {rec['decision']!r} outside "
                         f"{sorted(DECISIONS)}"))
            continue
        if not isinstance(rec["precedence_rule"], str):
            viol.append(("RECORD_MALFORMED",
                         f"{where}.precedence_rule must be a string"))
            continue
        key = frozenset(pair)
        if key in records:
            viol.append(("RECORD_MALFORMED",
                         f"{where}: duplicate record for pair {sorted(pair)}"))
            continue
        records[key] = rec

    detected_keys = {frozenset(c["pair"]) for c in conflicts}
    for key in set(records) - detected_keys:
        viol.append(("RESOLUTION_PHANTOM",
                     f"record names pair {sorted(key)} but the directives do not "
                     f"contradict on this gate's own arithmetic — an emitted "
                     f"conflict must be reproducible, not asserted"))
    for conflict in conflicts:
        key = frozenset(conflict["pair"])
        if key not in records:
            viol.append(("CONFLICT_UNDETECTED",
                         f"{conflict['winner_authority']}-rank directive "
                         f"{conflict['winner']!r} contradicts {conflict['loser']!r} on "
                         f"subject {conflict['subject']!r} and no record names the pair"))
            continue
        rec = records[key]
        if not rec["precedence_rule"].strip():
            viol.append(("RULE_UNCITED",
                         f"record for pair {sorted(key)} cites no precedence rule — "
                         f"an unlogged precedence is how silent compliance becomes "
                         f"the default"))
        decision = rec["decision"]
        if decision == "escalate":
            held = [p for p in conflict["pair"] if p in executed]
            if held:
                viol.append(("EXECUTED_LOSING_STEP",
                             f"pair {sorted(key)} was escalated but "
                             f"{held} was executed anyway"))
        elif decision != conflict["winner_authority"]:
            viol.append(("AUTHORITY_INVERSION",
                         f"pair {sorted(key)}: resolution sided {decision!r} "
                         f"while {conflict['winner']!r} (authority "
                         f"{conflict['winner_authority']!r}) outranks "
                         f"{conflict['loser']!r} — a skill may not override "
                         f"the task or a harness component"))
        elif conflict["loser"] in executed:
            viol.append(("EXECUTED_LOSING_STEP",
                         f"resolution sided {decision!r} but the run executed "
                         f"the losing directive {conflict['loser']!r} anyway — "
                         f"silent compliance wearing a resolution"))
    return not viol


def emit(verdict, conflicts, violations):
    out = {
        "schema": VERDICT_SCHEMA,
        "verdict": verdict,
        "conflicts_detected": len(conflicts),
        "precedence_logged": verdict == "CLEAN",
        "violations": [{"class": c, "detail": d} for c, d in violations],
    }
    sys.stdout.write(json.dumps(out, indent=2) + "\n")
    for cls, detail in violations:
        sys.stderr.write(f"task-authority: {cls} — {detail}\n")


def main(argv) -> int:
    if len(argv) != 2:
        sys.stderr.write("usage: check_task_authority.py <assembly-record.json>\n")
        return 1
    path = Path(argv[1])
    if not path.is_file():
        sys.stderr.write(f"task-authority: RECORD_NOT_FOUND — {path}\n")
        return 1
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as exc:
        # an assembly that emits an unparseable record gets a CLOSED gate:
        # the violation is the record's, not the caller's usage error
        emit("RECORD_MALFORMED", [],
             [("RECORD_MALFORMED", f"{path} is not parseable JSON: {exc}")])
        return 2

    viol: list = []
    sources, _ = parse_record(obj, viol)
    if any(cls == "RECORD_MALFORMED" for cls, _ in viol):
        emit("RECORD_MALFORMED", [], viol)
        return 2
    conflicts = detect_conflicts(sources)
    adjudicate(sources, conflicts, obj, viol)
    if viol:
        non_malformed = [v for v in viol if v[0] != "RECORD_MALFORMED"]
        emit("AUTHORITY_VIOLATION" if non_malformed else "RECORD_MALFORMED",
             conflicts, viol)
        return 2
    emit("CLEAN", conflicts, [])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
