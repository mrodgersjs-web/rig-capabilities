---
name: great-task-authority-over-skill-authority
lane: agent-engineering
source: canonical-curated
exemplar_of: task-authority-over-skill-authority
description: Reference exemplar — the precedence gate GREEN on a task-won conflict with a cited rule, a harness guard beating a skill, a held escalation, and two compatible directives; RED (exit 2) on each of the six planted failures (authority inversion, undetected conflict, uncited rule, executed losing step, phantom record, malformed record)
---

# task-authority-over-skill-authority — reference

Canonical asset `task-authority-over-skill-authority` (hook). Paths:
`capabilities/hooks/task-authority-over-skill-authority.sh` (seam) and
`capabilities/hooks/task-authority/check_task_authority.py` (adjudicator).

> A loaded skill is a token-by-token instruction stream competing with the
> task the operator actually gave. The precedence is fixed and applied in code
> at assembly time — **task > harness > skill** — and a contradiction is
> arithmetic: same `subject`, disjoint `require` sets, no world satisfies both.
> On a conflict the run may side with the higher authority or escalate; it may
> not obey the skill, stay silent, or skip logging the rule it applied.

## What good looks like

The load-bearing seed from the source's own done-test — the skill says skip
the suite, the task says green, and the record shows the task won and said
why:

```json
{"schema": "rig.authority.assembly.v1",
 "sources": [
   {"id": "task-ship-9042", "authority": "task", "directives": [
     {"id": "D-tests", "text": "The full test suite must be green before this ship is declared done.", "subject": "test_suite", "require": "green"}]},
   {"id": "skill-ship-fast", "authority": "skill", "directives": [
     {"id": "S-skip-nose", "text": "Velocity rule: skip the test suite before shipping and let CI catch regressions after the fact.", "subject": "test_suite", "require": "skip"}]}],
 "resolution": {"conflicts": [
   {"pair": ["D-tests", "S-skip-nose"], "decision": "task",
    "precedence_rule": "task-authority-over-skill-authority: a binding task requirement outranks any skill-body directive; the skill step is dropped, not deferred"}],
  "executed": ["D-tests"]}}
```

`task-authority-over-skill-authority.sh assembly_task_wins.json` → **exit 0**,
`{"verdict": "CLEAN", "conflicts_detected": 1, "precedence_logged": true}`.

The other three greens keep the gate honest in different directions:
`assembly_harness_wins.json` (a `guard-dangerous-commands`-style harness
directive beats a skill's `rm -rf` step — a skill may not override its own
neighbours), `assembly_escalate.json` (decision `escalate`, `executed: []` —
non-compliance with the skill without pretending the task was resolved), and
`assembly_no_conflict.json` (task allows `[pnpm, npm]`, skill requires `pnpm`
— the sets intersect, so **zero** conflicts are demanded and the skill step
runs clean; a gate that fires on everything is a gate that will be disabled).

## The eleven done-test forms

| fixture | exit | clause |
|---------|------|--------|
| `assembly_task_wins.json` | 0 | task wins, rule cited, precedence logged |
| `assembly_harness_wins.json` | 0 | harness guard outranks the skill's step |
| `assembly_no_conflict.json` | 0 | intersecting requires — no conflict demanded |
| `assembly_escalate.json` | 0 | both steps held, neither executed |
| `assembly_skill_wins.json` | 2 | `AUTHORITY_INVERSION` — the resolution sided with the skill |
| `assembly_conflict_undetected.json` | 2 | `CONFLICT_UNDETECTED` — directives contradict, no record names the pair |
| `assembly_rule_uncited.json` | 2 | `RULE_UNCITED` — task won but no rule was cited |
| `assembly_executed_losing_step.json` | 2 | `EXECUTED_LOSING_STEP` — sided with the task, the suite stayed skipped |
| `assembly_phantom_record.json` | 2 | `RESOLUTION_PHANTOM` — a "conflict" the disjointness arithmetic cannot reproduce |
| `assembly_malformed_authority.json` | 2 | `RECORD_MALFORMED` — `authority: "senior_skill"` is outside the closed ladder |

Usage and a missing record exit **1** — a refusal to judge, never conflated
with a verdict. An unparseable record exits **2**: the violation belongs to
the assembly, and the gate fails closed rather than admitting whatever context
happens to parse.

## Why the gate is code, not doctrine

The RIG delta: no precedence policy exists anywhere in the estate.
`guard-dangerous-commands.sh` / `guard-secret-write.sh` / `tac-plan-gate.sh`
gate tool calls, not instruction sources; `skill-preload-precondition-gate.sh`
decides whether a body may LOAD but once loaded its directives compete
unranked with the task; `mh-03-agent-composition-session.yaml` asks for a
prose "precedence note" only when two bound skills' *triggers* overlap. Here
the ladder is arithmetic, the resolution is a record, and the silent-compliance
leg — resolution on paper, `executed: ["S-skip-nose"]` in fact — is its own
named class.

Ceiling: the gate judges the record the harness assembled — mutated or
stripped directives defeat it, same-rank (skill-vs-skill) clashes are out of
scope, and `executed` is what the record declares. Wiring the seam is a
separate Gate-D action.

Provenance: video `TA5QzGTQU_U`; arXiv:2608.11888. No creator text is
reproduced; the mechanism is re-derived as an enforceable adjudication.
