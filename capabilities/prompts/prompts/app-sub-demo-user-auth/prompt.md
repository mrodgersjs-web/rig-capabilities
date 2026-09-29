---
id: app-sub-demo-user-auth
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: a seeded demo user as a named auth stub with ownership checks on every mutation
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: demo user auth stub
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-backend-data
stage: backend-data
audience: builder
lessons: LA-07 TG-16
jev_gate: app.prompt
jev_decision: 119528
content_sha256: 812b51e9e9565618fb9f137949a9ad4751acd73f4e0cfba0cc2ec4c5ccfdd442
---

# Demo-user auth stub (App Studio sub prompt, v1)

Contract
- id: app-sub-demo-user-auth | version: 1 | tier: sub | parent: app-studio-backend-data | stage: backend-data | audience: builder
- inputs: {{OUT_OF_SCOPE}}
- output: a demo-user module and ownership checks in each mutating route
- lessons carried (each one is an instruction to follow):
  - LA-07: Env-gate each paid vendor with a NAMED fallback so the app runs without the key, and list missing credentials exactly in a BLOCKED list.
  - TG-16: Gate every mutation on record ownership, not only on being signed in. (TubeGuruji videos: P6dha4Sq8gQ)
- gates: library gate app.prompt on this text; output gate app.stage-gate on the backend-data record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: every record carries ownerId, and a mutation on a record with another ownerId returns 403 or 404, shown by one curl
- stop: report BLOCKED: auth scope unclear when the task names real sign-in without a stub; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. One constant demo user (id, name, email) marked `named stub for the real auth provider` in code and in stack.md (LA-07).
2. Every record stores ownerId; every read filters by it.
3. Every mutation checks ownership, not just presence of a user (TG-16).
4. Show the demo user's name in the dashboard so the stub is visible.

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
