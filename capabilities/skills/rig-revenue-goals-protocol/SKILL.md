---
name: "rig-revenue-goals-protocol"
description: "Write a goal spec an independent evaluator can audit — Goal, Output, Acceptance, Limits, Stop-and-verify — and run the worker/evaluator loop until it passes. Use when the trigger is 'spec this task', 'done criteria', 'goal protocol', or 'how do we verify this deliverable'."
---

# GOALS protocol (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. "The evaluator can only audit what you specify" (CLAIM:
SY8krFc58DE). The corpus's own done-test + verifier pair.

## Step 1. Write the five components

1. **Goal** — one sentence, action verb, deliverable on one line.
2. **Output** — file name, format, schema. Unspecified output cannot be audited.
3. **Acceptance** — numbered, each yes/no/number decidable. "Fuzzy words fail the test" (CLAIM:
   SY8krFc58DE).
4. **Limits** — forbidden actions (the rig-revenue-meta risk register goes here verbatim), caps,
   budgets.
5. **Stop-and-verify** — the evidence each acceptance criterion requires, listed before work
   starts.

## Step 2. Three prompt tests before dispatch

- Stranger test: could a stranger know what done looks like? Follow-up questions = weak criteria.
- Spreadsheet test: every acceptance criterion is a yes/no column.
- Runway test: the worst-case misread is caught by the Limits within minutes.

## Step 3. Worker → independent evaluator loop

1. Worker produces against the spec.
2. A separate evaluator (no memory of the worker's reasoning) audits every criterion against the
   Stop-and-verify evidence. Self-approval is not an evaluation.
3. Failures bounce back with the criterion that failed. Loop max 3, then escalate to the human.

## done_when

- file:capabilities/skills/rig-revenue-goals-protocol/SKILL.md
- grep:capabilities/skills/rig-revenue-goals-protocol/SKILL.md:^## Step 2. Three prompt tests
- grep:capabilities/skills/rig-revenue-goals-protocol/SKILL.md:Fuzzy words fail the test
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-goals-protocol/SKILL.md

## Provenance (videoIds)

86bRah0t_Ko, SY8krFc58DE, _5Nne2mrXIo (95%-confidence interview), uczx7l95Wj8.
