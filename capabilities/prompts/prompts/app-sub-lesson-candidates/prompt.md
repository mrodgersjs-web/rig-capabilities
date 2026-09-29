---
id: app-sub-lesson-candidates
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: record each failure hit during the build as a lesson candidate with exact evidence
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: lesson candidates section
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-operate-learn
stage: operate-learn
audience: builder
lessons: LA-28
jev_gate: app.prompt
jev_decision: 119537
content_sha256: 6c2b02cd4fdbb3e4a24cadbd0de1a3bc44758896fbebb2ad3da54e583299dc28
---

# Lesson candidates in DONE.md (App Studio sub prompt, v1)

Contract
- id: app-sub-lesson-candidates | version: 1 | tier: sub | parent: app-studio-operate-learn | stage: operate-learn | audience: builder
- inputs: the build log and stage records
- output: a Lessons observed section in DONE.md
- lessons carried (each one is an instruction to follow):
  - LA-28: Write each new failure into this ledger as a typed lesson and patch the owning sub-skill in the same session; memory-only lessons do not count.
- gates: library gate app.prompt on this text; output gate mission.completion on the close record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: each failure hit during the build has a row, or the section reads none observed
- stop: report BLOCKED: build log missing when the log is unreadable; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

Add `## Lessons observed` to DONE.md. One row per failure you hit:
symptom | exact error text | fix | command that proved the fix | lesson id it matches, or new.
The lesson filer turns new rows into typed ledger lessons (LA-28). Write `none observed` when nothing failed.

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
