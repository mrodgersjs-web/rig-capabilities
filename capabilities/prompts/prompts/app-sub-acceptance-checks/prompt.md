---
id: app-sub-acceptance-checks
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: author executable acceptance checks for an App Bench task that the builder never sees
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: author acceptance checks bench task acceptance
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-intake-spec
stage: intake-spec
audience: conductor
lessons: LA-08 LA-20 TG-04 BENCH-02
jev_gate: app.prompt
jev_decision: 119525
content_sha256: 983fc1bf23c3057d43c851f2165cac8dc8f43c44d8e2b14167fe29330dd9e26c
---

# Authoring hidden acceptance checks (App Studio sub prompt, v1)

Contract
- id: app-sub-acceptance-checks | version: 1 | tier: sub | parent: app-studio-intake-spec | stage: intake-spec | audience: conductor
- inputs: {{CONTRACT}}, {{FEATURES}}, the task JSON
- output: an `acceptance` array in bench/tasks/<id>.json: each check has id, stage, desc, request {method, path, body}, expect {status, json fields, json_all, text_includes, capture}
- lessons carried (each one is an instruction to follow):
  - LA-08: Prove the gate with a limit+1 deny test and show the counter moving in the rendered UI.
  - LA-20: Grep the runner behind any PASS report for assertion verbs (expect, assert) and hardcoded status literals before quoting its counts.
  - TG-04: Enforce a quota in the one creation path per action, as a token bucket, DB counter or entitlement flag, and hit the deny path before calling it done. (TubeGuruji videos: zcYM_Gqoph4, ciXiibK7Gds, s28yOCBVgGw, rdaSPdCkoFQ)
  - BENCH-02: Server-render the app name and primary content of every contract page so a raw GET without JavaScript proves the page. (evidence: a working app failed its home-page check on 2026-09-28 because the raw HTML lacked the expected text (run 6415a483, P1))
- gates: library gate app.prompt on this text; output gate app.spec on the task file (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: every contract line has at least one check, at least one must-fail check exists per mutation, and the verifier's own tests prove a wrong status, an empty list and a missing substring each fail
- stop: report BLOCKED: <line> for a contract line that cannot be checked over HTTP; stubs stay out of the file until checks exist; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

Conductor only. These checks never appear in a builder prompt, a TASK.md, or anything the builder can read.

1. One check per contract line at minimum, each tagged with the stage it grades.
2. Add must-fail cases: invalid input returns the contract's error status, limit+1 is denied by a quota (LA-08, TG-04), and a deleted record stops appearing.
3. Page checks read the raw HTML without JavaScript, so require only text the server renders (BENCH-02).
4. Chain requests with captured variables (a created id feeds the next GET).
5. Prove the checks can fail: the verifier's test suite must hold must-fail fixtures with real assertions (LA-20).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
