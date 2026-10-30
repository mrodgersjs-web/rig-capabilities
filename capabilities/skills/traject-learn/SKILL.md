---
name: traject-learn
description: "Traject OS sub-skill, stage 11 (learn): close the run, promote typed lessons to the ledger and their sub-skills, and run the Sunday funnel review against the JOB-SYSTEM-v2 lanes. Gated by JEV mission.completion and atomic.claim. Lessons reach the ledger and the owning sub-skill in the same session. DEFER when the classifier is down."
tags: [rig, traject-os, sub-skill, learn, lessons, review]
metadata:
  parent: traject-os
  tier: sub
  stage: learn
  extends: "aside-job-learning, resume-screening-stack"
outcome: "A closed run whose run.jsonl validates, whose new failures became typed lessons in the ledger AND whose owning sub-skills were patched the same session, and a Sunday funnel review mapping outcomes to the JOB-SYSTEM-v2 lanes and KPIs."
activation: "Load at run close and at the Sunday funnel review (traject-weekly-learn-loop)."
instruction: "Write typed lessons (trigger, mandated check, evidence) for every new failure, append them to the ledger and patch the owning sub-skill in the same session, validate run.jsonl with validate_lessons.py, and run the Sunday review against the JOB-SYSTEM-v2 lanes (A/B/C/E/D) and KPIs (K0 signed offer ≥$180K base). Never invent an outcome metric."
applies_when:
  env: "the lessons ledger (references/lessons.jsonl); <project>/.traject/run.jsonl; JOB-SYSTEM-v2.md"
  runtime: "experience-lesson-records validator; the daily/weekly loops"
  deps: "a completed or held run; aside-job-learning"
  params: "run id, task text, failures observed"
  budget: "one close per run; one review per Sunday"
  scale: "one run.jsonl per run"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Distill each new failure into a typed lesson (trigger, mandated check, evidence).
  - Append to the ledger AND patch the owning sub-skill in the same session.
  - Validate run.jsonl with validate_lessons.py (must exit 0).
  - On Sunday, review the funnel against JOB-SYSTEM-v2 lanes and KPIs.
done_when:
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/traject-os/references/lessons.jsonl"
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/mission.completion.json"
out_of_scope:
  - inventing outcome metrics or business results that were not observed
  - filing lessons in memory only without patching the owning sub-skill
---

# traject-learn

JEV FIRST: the close verdict goes to `rig-s1gate check mission.completion` and each new
lesson to `atomic.claim` BEFORE any frontier call. Classifier down: DEFER, never guess.
Required signals above 0.9.

Sub-skill of `traject-os`, stage 11. Main skills: `aside-job-learning`,
`resume-screening-stack`. Agent: `traject-proof-curator` / `traject-debrief-clerk`.
Harness: `traject-proof-publish-session`. Loop: `traject-weekly-learn-loop`.

## Procedure

1. **Typed lessons**: for each new failure, write a lesson with `trigger` (matchable substring or
   regex), `mandated_check` (the enforceable check), and `evidence` (the run/row that earned it).
   Append to `references/lessons.jsonl` and patch the owning sub-skill in the **same session**.
   A lesson with no matchable trigger, no enforceable check, or no evidence is refused.
2. **Validate the run**: `validate_lessons.py <ledger> --run <run.jsonl>` must exit 0 — every
   active lesson whose trigger fired has a receipt.
3. **Sunday funnel review** (`traject-weekly-learn-loop`): map outcomes to JOB-SYSTEM-v2 lanes —
   A Apply (K3 100 receipt-backed/wk), B Direct (K1 3+ conversations/wk, K4 50 warm touches/wk),
   C Convert (K2 advance 30%, K5 human asks <24h), E Market, D Learn — and the north star
   K0 = signed offer ≥$180K base (target $250K). Report outcomes as observed, never invented.
4. **Carry forward** debrief ownership gaps and NONE rows into the next room's story bank.

## Lessons that fire here

- Every lesson in the ledger fires here at close; run
  `python3 capabilities/skills/traject-os/scripts/fire_lessons.py "<task text>"` for the list.
