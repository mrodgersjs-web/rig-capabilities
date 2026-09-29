---
id: app-sub-gate-d-hold
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: a complete release request that stays HELD until Mike approves
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: gate-d release request
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-ship-release
stage: ship-release
audience: builder
lessons: LA-12 TG-23
jev_gate: app.prompt
jev_decision: 119535
content_sha256: 4a08f7360cc463c22d869729276941c4a3d6792cfa6a878d811aa93972808ee9
---

# Gate-D release request (App Studio sub prompt, v1)

Contract
- id: app-sub-gate-d-hold | version: 1 | tier: sub | parent: app-studio-ship-release | stage: ship-release | audience: builder
- inputs: the verified build, {{STACK}}
- output: a Release request section in .app-studio/stages/ship-release.md with status HELD
- lessons carried (each one is an instruction to follow):
  - LA-12: Report a green preview as a render check only; functional proof that depends on the real domain waits for the Gate-D promote.
  - TG-23: A rendered page is not a working deploy: sign in, create one artifact, fire one webhook and run one job on the production URL. (TubeGuruji videos: zrdbOx0eGtM, zjwj21wzs4U)
- gates: library gate app.prompt on this text; output gate app.ship (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: the section lists target, exact commands, env var names, rollback and post-approval checks, and its status line reads HELD at Gate-D
- stop: stop at status HELD and report `HELD at Gate-D`; report BLOCKED: <field> when target, commands, env var names or rollback are unknown; never run any command in the request; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

Write a Release request with:
1. Target (host, project, domain) and why.
2. Exact commands to run after approval, in order.
3. Env var names to set (never values) and where.
4. Rollback: the command that restores the previous release.
5. Post-approval checks on the production URL: sign in, create one record, fire one webhook, run one job (TG-23). A preview is a render check only (LA-12).
6. Status: HELD at Gate-D, waiting for Mike's approval.

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
