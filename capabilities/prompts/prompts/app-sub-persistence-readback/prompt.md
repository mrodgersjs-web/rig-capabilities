---
id: app-sub-persistence-readback
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: check each persisted record through a second path and show background work runs with a forced-due fixture
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: persistence readback check
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-verifier
stage: verify-qa
audience: verifier
lessons: LA-05 LA-24
jev_gate: app.prompt
jev_decision: 119542
content_sha256: 9c983173004bf3d7a608e9e2b9de1e7b21d7339c3082a09471ae7d1cb8c53df0
---

# Persistence read-back (App Studio sub prompt, v1)

Contract
- id: app-sub-persistence-readback | version: 1 | tier: sub | parent: app-studio-verifier | stage: verify-qa | audience: verifier
- inputs: the acceptance rows with created ids
- output: read-back rows: write request, read path, fields compared, verdict
- lessons carried (each one is an instruction to follow):
  - LA-05: Sweep every consumer of the transformed keys in the same change and prove background endpoints with a forced-due fixture, because a clean exit with zero work is what a broken join looks like.
  - LA-24: Read the persisted record back through a different path before claiming an endpoint stored it.
- gates: library gate app.prompt on this text; output gate app.stage-gate on the verify-qa record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: every write has a read-back row through a path other than the write response
- stop: report BLOCKED: <record> when no read path exists for a write; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. For each write, read the record back through another path: a GET, a list endpoint, or the store file (LA-24).
2. Compare the fields the contract names, not just the status.
3. For scheduled or background work, create a forced-due fixture and confirm the job did real work; a clean exit with zero work is a broken join (LA-05).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
