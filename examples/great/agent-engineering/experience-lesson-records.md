---
name: great-experience-lesson-records
lane: agent-engineering
source: canonical-curated
exemplar_of: experience-lesson-records
description: Reference exemplar — the lessons validator GREEN on a matching run that carries the mandated-check receipt and GREEN on a retired lesson deliberately skipped, RED (exit 2) on each of the five planted failures (missing field, empty evidence, uncompilable regex, unknown status, matched-but-no-receipt)
---

# experience-lesson-records — reference

Canonical asset `experience-lesson-records` (skill). Path:
`capabilities/skills/experience-lesson-records`.

> A lesson is a typed, evidence-bearing rule that FIRES as a gate on condition
> match. At run close the reflection step distills the trajectory into a record
> — `trigger`, `match`, `mandated_check`, `evidence`, `status` — stored under a
> retrieval key. On a later task whose text matches the trigger, the mandated
> check becomes a receipt the run must carry. `validate_lessons.py` enforces
> every clause; the planted fixtures are permanent regression cases.

## What good looks like

The load-bearing seed from the source's own done-test — a return-type lesson
that must fire, not merely be remembered:

```json
{"lesson_id":"L-return-type","trigger":"public return-type change","match":"substring","mandated_check":"enumerate downstream callers before editing","evidence":["run-2026-08-19/gamma:r7","run-2026-08-19/attempt:a2"],"status":"active"}
```

A run that matches it and pays for it — the receipt is the difference between
recall and application:

```json
{"kind":"task","text":"apply a public return-type change to parse()"}
{"kind":"receipt","check":"enumerate downstream callers before editing","detail":"found 4 callers via lsp references"}
{"kind":"close","outcome":"submitted"}
```

`validate_lessons.py lessons_valid.jsonl --run run_valid.jsonl` → **exit 0**.

## The nine done-test forms

| fixture | run | exit | why |
|---------|-----|------|-----|
| `lessons_valid.jsonl` | `run_valid.jsonl` | 0 | matched lesson, receipt present |
| `lessons_valid.jsonl` | `run_retired_skipped.jsonl` | 0 | retired lesson skipped — sanctioned, not a hole |
| `lessons_missing_field.jsonl` | — | 2 | a lesson missing `evidence` cannot be enforced |
| `lessons_evidence_empty.jsonl` | — | 2 | an evidence-less lesson is a guess |
| `lessons_bad_regex.jsonl` | — | 2 | a trigger that will not compile is dead the day it is written |
| `lessons_unknown_status.jsonl` | — | 2 | `status:"maybe"` is not a state the gate understands |
| `lessons_valid.jsonl` | `run_missing_receipt.jsonl` | 2 | the lesson fired and the gate was not satisfied |

The five exit-2 fixtures are the regression suite: each is the failure the gate
exists to catch, kept so a future edit that stops the gate biting turns a green
red immediately.

## Why it is not a diary

The RIG delta: `~/.hermes/jake/improvements.log` appends free-text with no
condition key and no retrieval path, so a lesson is re-read by a human or never
applied. Here the trigger is a match key and the mandated check is a receipt the
run must produce — the lesson fires rather than being recalled.

Provenance: video `lNlMXsUQggc`; arXiv:2608.27969 (openJiuwen); OSS
`openJiuwen-ai/jiuwenswarm`.
