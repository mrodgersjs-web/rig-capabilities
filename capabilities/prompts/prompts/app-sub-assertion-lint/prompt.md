---
id: app-sub-assertion-lint
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: lint a test runner for assertion verbs and hardcoded pass literals before quoting its counts
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: assertion verbs lint
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-verifier
stage: verify-qa
audience: verifier
lessons: LA-20 LA-34
jev_gate: app.prompt
jev_decision: 119526
content_sha256: 8b48982034076bacafc3195c6be1c3ef58de34d32e46a7f3a5630b2b29b1687d
---

# Assertion lint on test runners (App Studio sub prompt, v1)

Contract
- id: app-sub-assertion-lint | version: 1 | tier: sub | parent: app-studio-verifier | stage: verify-qa | audience: verifier
- inputs: {{RUNNER_PATHS}}
- output: a lint row per runner: assertion verb count, hardcoded status literals, verdict
- lessons carried (each one is an instruction to follow):
  - LA-20: Grep the runner behind any PASS report for assertion verbs (expect, assert) and hardcoded status literals before quoting its counts.
  - LA-34: Compare each run's duration and evidence with the work it claims; a multi-phase build that completes in seconds, or evidence hashed from placeholder strings, is a stub and not a result.
- gates: library gate app.prompt on this text; output gate code.review (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: each runner behind a reported PASS count has a nonzero assertion count, or its counts are reported as unverified
- stop: stop and report BLOCKED: runner unreadable when a runner file cannot be read; report the counts as unverified, never PASS, when a runner has zero assertion verbs; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. Grep each runner for assertion verbs: expect(, assert, should, toBe, toEqual.
2. Grep for hardcoded status literals: `passed: true`, `status: "PASS"`, `full_scenario_executed`.
3. Zero assertions means its PASS count proves nothing (LA-20).
4. Compare run duration with scenario count; hundreds of scenarios in seconds is a stub (LA-34).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
