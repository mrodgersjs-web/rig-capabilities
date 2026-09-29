---
id: app-sub-typed-lesson
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: write one typed lesson line for the App Studio ledger that validates and fires
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: typed lesson format
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-lesson-filer
stage: operate-learn
audience: lesson-filer
lessons: LA-28 LA-30
jev_gate: app.prompt
jev_decision: 119552
content_sha256: e8d1665d98a3d31bba9b12ce82a26062acd9d7937a01ace001d1f7538aa9ea6b
---

# Typed lesson format (App Studio sub prompt, v1)

Contract
- id: app-sub-typed-lesson | version: 1 | tier: sub | parent: app-studio-lesson-filer | stage: operate-learn | audience: lesson-filer
- inputs: {{FAILURE_EVIDENCE}}, {{LEDGER}}
- output: one JSON line: lesson_id, trigger, match, mandated_check, evidence, status
- lessons carried (each one is an instruction to follow):
  - LA-28: Write each new failure into this ledger as a typed lesson and patch the owning sub-skill in the same session; memory-only lessons do not count.
  - LA-30: Write single-line quoted scalars, unanchored grep checks and agent ids with .md, reindex before test, and execute done_when directly when the CLI index is stale.
- gates: library gate app.prompt on this text; output gate app.stage-gate on the operate-learn record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: validate_lessons.py exits 0 on the ledger and fire_lessons.py lists the new lesson for a matching task sentence
- stop: stop and report BLOCKED: <path> when an evidence path does not exist or the ledger cannot be written; never file a lesson that fails validation; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

Append one line to {{LEDGER}}:
{"lesson_id": "LA-<nn>-<slug>", "trigger": "<regex that matches future task text>", "match": "regex", "mandated_check": "<imperative check>", "evidence": ["<run dir or file>", "session:<id>"], "status": "active"}
1. Compile the regex before writing; test it on one matching and one non-matching sentence.
2. The mandated check is one imperative sentence a verifier can perform.
3. Evidence paths must exist; channel-derived lessons cite video ids.
4. Keep scalars on one line (LA-30); validate and fire-test after writing (LA-28).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
