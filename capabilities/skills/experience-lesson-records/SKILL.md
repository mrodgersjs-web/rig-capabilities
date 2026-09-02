---
name: experience-lesson-records
description: >-
  Use when a harness keeps re-learning the same failure. At run close a
  reflection step distills the trajectory into a TYPED lesson record — trigger
  condition, mandated check, evidence (the run/rows that earned it), status —
  stored under a retrieval key. On a later task whose text matches the trigger,
  the lesson FIRES: its mandated check becomes a gate requirement the run must
  carry a receipt for, rather than a prose recollection a human might re-read.
  A lesson with no matchable trigger, no enforceable check, or no evidence is
  refused; a retired lesson is skipped, never a silent hole. validate_lessons.py
  enforces every clause: exit 2 on a malformed lesson, an uncompilable trigger,
  an evidence-less lesson, an unknown status, or a matched active lesson whose
  mandated check has no receipt in the run.
allowed-tools: Bash Read Write
owner: rig-intelligence
domain: Agent memory / across-task retention
status: Draft
outcome: >-
  agent-engineering: a distilled lesson fires as a gate on condition match
  instead of decaying into a diary — the same failure is not re-learned, because
  the reflection step produces an enforceable record, not prose
done_when:
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/experience-lesson-records/fixtures/lessons_valid.jsonl --run capabilities/skills/experience-lesson-records/fixtures/run_valid.jsonl; test $? -eq 0
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/experience-lesson-records/fixtures/lessons_valid.jsonl --run capabilities/skills/experience-lesson-records/fixtures/run_retired_skipped.jsonl; test $? -eq 0
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/experience-lesson-records/fixtures/lessons_missing_field.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/experience-lesson-records/fixtures/lessons_evidence_empty.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/experience-lesson-records/fixtures/lessons_bad_regex.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/experience-lesson-records/fixtures/lessons_unknown_status.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/experience-lesson-records/fixtures/lessons_valid.jsonl --run capabilities/skills/experience-lesson-records/fixtures/run_missing_receipt.jsonl; rc=$?; test $rc -eq 2
  - file:capabilities/skills/experience-lesson-records/validate_lessons.py
great_example: examples/great/agent-engineering/experience-lesson-records.md
quality_floor: 0.6
---

# experience-lesson-records

THE LAW: **a lesson is a typed, evidence-bearing rule that FIRES as a gate on
condition match — not a prose recollection.** The reflection step at run close
either produces a record with a matchable trigger, an enforceable check, and the
run that earned it, or it produced a diary. A diary reads as learning and
changes nothing: the same gate fails a fourth time.

The source names the object and the two clocks the store runs on:

> "beyond static harnesses for long-horizon coding agents" (arXiv:2608.27969,
> openJiuwen) — the harness must *retain across tasks*, not only adapt within
> one. The lesson is the retained unit. (video lNlMXsUQggc; OSS
> openJiuwen-ai/jiuwenswarm)

The RIG delta this closes: today every harness's `self_improvement` block
appends free-text to `~/.hermes/jake/improvements.log` (`pattern_cadence: 5`,
"same gate fails 3+ times ⇒ propose a revision") with no schema, no condition
key, no retrieval path. The lesson is re-read by a human or never applied. This
skill makes the lesson a condition-keyed record with a gate.

## The record: one JSONL line, six required fields

`lessons.jsonl` — one lesson per line. All six fields required; any missing
field is exit 2, because a lesson you cannot match or cannot enforce is not a
lighter lesson, it is decoration.

| field | meaning |
|-------|---------|
| `lesson_id` | globally unique; a duplicate id is a violation |
| `trigger` | the condition text matched against a task |
| `match` | `substring` \| `regex`; a `regex` trigger that will not compile is exit 2 (a trigger that cannot match is dead the day it is written) |
| `mandated_check` | the check that becomes a gate requirement when the trigger fires |
| `evidence` | **non-empty** list of run/row-ids that earned the lesson — the load-bearing clause: a lesson with no evidence is a guess, and a guess is exit 2 |
| `status` | `active` \| `retired`; unknown status is exit 2 |

## Firing: the run must carry a receipt

`run.jsonl` — one run: a `task` row (the task text), zero or more `receipt`
rows (checks actually performed, each naming a `check`), and a `close` row.

For every **active** lesson whose `trigger` matches the task text, the run MUST
contain a receipt whose `check` equals the lesson's `mandated_check`. A match
with no receipt is exit 2 — the lesson fired and the gate was not satisfied.
This is the difference between "the lesson was recalled" and "the lesson was
applied": recall is free, a receipt is evidence.

A **retired** lesson is skipped even when its trigger matches — retiring a
lesson is the sanctioned way to stop it firing (risk: a lesson whose condition
key has drifted becomes dead weight; prune on an age-vs-retrieval rule). An
honest retirement is GREEN, not a hole.

## Done-tests (the planted failures are permanent regression cases)

`validate_lessons.py` is exercised by eight `done_when` forms: two GREEN
(a matching run with its receipt; a retired lesson skipped) and five RED at
exit 2 — a field-missing lesson, an empty-evidence lesson, an uncompilable
regex trigger, an unknown status, and a matched active lesson with no receipt.
Each RED fixture is kept so the gate cannot silently stop biting.

## Provenance

Source video `lNlMXsUQggc`; paper arXiv:2608.27969 (*openJiuwen: Beyond Static
Harnesses for Long-Horizon Coding Agents*); implementation
`openJiuwen-ai/jiuwenswarm`. No creator text is reproduced; the mechanism is
re-derived as an enforceable record.
