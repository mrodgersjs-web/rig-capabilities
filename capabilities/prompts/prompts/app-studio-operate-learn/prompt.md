---
id: app-studio-operate-learn
version: 1
status: draft
updated: 2026-09-28
task: App Studio operate-learn stage prompt: record the failures hit during the build as lesson candidates with exact evidence
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: lessons from this build operate and learn stage
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: main
parent: app-studio-meta
stage: operate-learn
audience: builder
lessons: LA-26 LA-28 LA-34
jev_gate: app.prompt
jev_decision: 119517
content_sha256: db809a458c14a88ead34911f9c356b756ed523ff1745773c5f4d59e899d89eca
---

# Stage 11: operate-learn (App Studio main prompt, v1)

Contract
- id: app-studio-operate-learn | version: 1 | tier: main (stage) | parent: app-studio-meta | stage: operate-learn | audience: builder
- inputs: the build log, stage records, {{FIRED_LESSONS}}
- output: a Lessons observed section in DONE.md (app-sub-lesson-candidates) and the record .app-studio/stages/operate-learn.md
- lessons carried (each one is an instruction to follow):
  - LA-26: Keep watcher routines read-only (they never build) and delete them at mission close so they do not become silently dead routines.
  - LA-28: Write each new failure into this ledger as a typed lesson and patch the owning sub-skill in the same session; memory-only lessons do not count.
  - LA-34: Compare each run's duration and evidence with the work it claims; a multi-phase build that completes in seconds, or evidence hashed from placeholder strings, is a stub and not a result.
- gates: library gate app.prompt on this text; output gate app.stage-gate plus mission.completion (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: every failure hit during the build has a candidate row with the exact error text and the command that proved the fix, or the section says none observed
- stop: report BLOCKED: build log missing when the log cannot be read; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-lesson-candidates

Question this stage answers: did the mission's lessons reach the ledger and the owning skills?

1. List each failure you hit as a lesson candidate (app-sub-lesson-candidates). The lesson filer turns them into ledger entries (LA-28).
2. Name each fired lesson's receipt or `not applicable: <reason>` in the stage record.
3. Delete any watcher you started; watchers never build (LA-26).
4. Compare the time spent with the work claimed before closing (LA-34).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
