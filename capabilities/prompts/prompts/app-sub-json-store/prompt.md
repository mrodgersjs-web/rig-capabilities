---
id: app-sub-json-store
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: a JSON-file store with atomic writes that boots from an empty folder
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: json file store
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-backend-data
stage: backend-data
audience: builder
lessons: LA-24 TG-20
jev_gate: app.prompt
jev_decision: 119536
content_sha256: 18fe5bf4d59e4eee5b6284fe9457cd470df8aeb7000558c539c4f6fadc5c729a
---

# JSON file store (App Studio sub prompt, v1)

Contract
- id: app-sub-json-store | version: 1 | tier: sub | parent: app-studio-backend-data | stage: backend-data | audience: builder
- inputs: {{DATA_DIR}}, {{CONTRACT}}
- output: one store module that every API route uses
- lessons carried (each one is an instruction to follow):
  - LA-24: Read the persisted record back through a different path before claiming an endpoint stored it.
  - TG-20: Make writes idempotent: React StrictMode runs effects twice in development and duplicated rows follow. (TubeGuruji videos: zlZ_7VTfxUs)
- gates: library gate app.prompt on this text; output gate app.stage-gate on the backend-data record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: after `rm -rf {{DATA_DIR}}` the production server boots, and each POST in the contract is followed by a GET whose body shows the stored fields
- stop: report BLOCKED: <path> when {{DATA_DIR}} cannot be written inside the workspace; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. Keep all data under {{DATA_DIR}}; create it on first write so an empty checkout boots (the verifier deletes it first).
2. Write atomically: write a temp file in the same folder, then rename it over the target.
3. Read the file on every request; no module-level cache across requests.
4. Use crypto.randomUUID() for ids; keep amounts as the numbers the contract names.
5. Guard creates against double submission (TG-20).
6. Prove each write by reading it back through a GET (LA-24).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
