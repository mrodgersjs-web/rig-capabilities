---
name: app-close-and-learn
description: "App Studio sub-skill, stage 11 (operate-learn): close an app mission so the next one is better - spec-versus-build comparison, a validated run record whose fired lessons all carry receipts, new failures written as typed lessons plus the owning sub-skill patched in the same session, watcher routines deleted, local surfaces curled, and a sealed ProofPacket. Closes the skill-promotion gap measured on 2026-09-26."
tags: [rig, app-studio, sub-skill, close, lessons, proofpacket, operate]
metadata:
  parent: app-studio
  tier: sub
  stage: operate-learn
  extends: "experience-lesson-records, jake-lessons-ledger, proof-loop, canary, code-error-pattern-aggregator"
outcome: "A closed mission: comparison table, run.jsonl that validates against the App Studio ledger, new lessons appended and their owning sub-skills patched, watcher routines deleted, a mission.completion JEV receipt, and a sealed ProofPacket."
activation: "Load at the end of any app mission, after a failed stage that taught something, or when Mike asks what an app build learned."
instruction: "Build the comparison table, validate the run record against the ledger, append each new failure as a typed lesson and patch its sub-skill in the same session, delete watcher routines, curl every surface claimed live, gate with mission.completion, and seal the ProofPacket."
applies_when:
  env: "the project's .app-studio folder plus rig-capabilities for ledger and skill edits"
  runtime: "any app lane"
  deps: "validate_lessons.py from experience-lesson-records; proofpacket_seal; routine_update"
  params: "mission name; routines created for the mission"
  budget: "under an hour; skipped closes cost the next mission"
  scale: "one mission"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Build the spec-versus-build comparison with a proof per row.
  - Validate the run record against the App Studio lesson ledger.
  - Append new failures as typed lessons and patch the owning sub-skill in the same session.
  - Delete mission watcher routines and curl every surface claimed live.
  - Gate the close with mission.completion and seal the ProofPacket.
done_when:
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl"
  - "grep:capabilities/skills/app-close-and-learn/SKILL.md:LA-28"
  - "grep:capabilities/skills/app-close-and-learn/SKILL.md:run.jsonl"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - lessons kept only in memory or chat (they do not count)
  - retiring a lesson without evidence that its condition changed
  - publishing the mission publicly
---

# app-close-and-learn

JEV FIRST, binding on every operate-learn step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check mission.completion` and `atomic.claim`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every operate-learn task: the `app-studio` meta-skill routes
stage 11 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 11 of 11. Main skills it extends:
`experience-lesson-records` (ledger schema and validator), `jake-lessons-ledger`,
`proof-loop`, `canary`, `code-error-pattern-aggregator`. Agent: `app-lesson-filer`.
Loop: `app-lesson-promotion-loop`.

## Procedure

1. **Comparison table.** Spec row, in build yes or no, proof (route, screenshot, command).
   Rows the source skipped stay named stubs, not silent gaps.
2. **Run record.** `.app-studio/run.jsonl` holds one `task` row, a `receipt` row per check
   actually performed, and a `close` row. Validate:
   `python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/app-studio/references/lessons.jsonl --run .app-studio/run.jsonl`.
   Exit 2 means a fired lesson has no receipt: perform the check or say why it does not
   apply, then re-validate.
3. **Promote lessons in the same session (LA-28).** On 2026-09-26 the previous day's six
   lessons had reached no skill at all (memory/episodic/2026-09-26.md#L317). For each
   new failure append a typed record (`lesson_id` LA-NN, `trigger`, `match`,
   `mandated_check`, `evidence` with run rows, `status: active`) to
   `app-studio/references/lessons.jsonl`, patch the owning sub-skill's lesson list, and
   re-run the ledger validator.
4. **Routines (LA-26).** Delete the mission's watcher routines. A "Watch Grokbot build"
   heartbeat outlived its build and sat with `nextRunAt` in the past, neither firing nor
   paused (memory/episodic/2026-09-27.md#L1187).
5. **Liveness (LA-25).** Curl every surface you report as up.
6. **Gate and seal.** `rig-s1gate check mission.completion` on the close record, then seal
   a ProofPacket binding the done-claim to commands, exit codes, and the artifact hash.
7. **Board.** Update the mission's card on the daily kanban (build stream) with the proof.
