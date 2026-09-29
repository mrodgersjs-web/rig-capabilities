---
id: app-sub-verify-md
version: 2
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: the .app-studio/verify.md self-verification format
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: verify.md format
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-21 LA-24 LA-41 | uncalibrated
tier: sub
parent: app-studio-verify-qa
stage: verify-qa
audience: builder
lessons: LA-21 LA-24 LA-41
jev_gate: app.prompt
jev_decision: 121880
content_sha256: 43be52396622b3b312c3759b5a1d0712f2db6dc9b1c979adc618f379779804f0
---

# verify.md format (App Studio sub prompt, v2)

Contract
- id: app-sub-verify-md | version: 2 | tier: sub | parent: app-studio-verify-qa | stage: verify-qa | audience: builder
- inputs: {{CONTRACT}} (the API and page contract lines), {{PORT_LO}} (the first port in the task's range), and the production build in the current folder
- output: .app-studio/verify.md: setup rows, one row per contract line (command, curl exit code, HTTP status, body excerpt, verdict), a read-back row per POST, a real-surface row per page, and the server stop row
- lessons carried (each one is an instruction to follow):
  - LA-21: Classify a check that could not run (missing tool, dependency or credential) as BLOCKED with the missing piece named, never as FAILED or PASS.
  - LA-24: Read the persisted record back through a different path before claiming an endpoint stored it.
  - LA-41: Verify each feature on the real surface: drive one real request in a browser with the network tab open (a real device or the store sandbox for mobile and purchases) and record the request, the response and the rendered result; code reading, a running server or a simulator run is not evidence.
- gates: library gate app.prompt on this text; output gate app.stage-gate on the verify-qa record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: verify.md has a build row with exit code, a start row with the port, and one row per contract line
- stop: report BLOCKED: <line> for a contract line you could not exercise; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

Write .app-studio/verify.md:
1. Setup rows: `rm -rf .data`, `npm run build` with its exit code, `npm run start -- -p {{PORT_LO}}`, and the curl of / with its status.
2. A table: contract line | exact curl command | curl exit code | observed HTTP status | body excerpt (under 200 characters) | PASS, FAIL or BLOCKED.
   Example row: `POST /api/items {name} -> 201` | `curl -s -X POST ... -w ' %{http_code}'` | 0 | 201 | {"id":"a1","name":"Milk"} | PASS
3. For each POST, a follow-up GET row that reads the record back (LA-24).
4. BLOCKED rows name the missing piece (LA-21).
5. The stop command for the server and `lsof -t -i :{{PORT_LO}}` printing nothing.
6. Real surface: if `ls ~/Library/Caches/ms-playwright` lists a Chromium, load each contract page in it against the production server and record the network request, the response status and the rendered text; if it lists nothing, write that row as BLOCKED: no browser. A running server or code reading is not evidence (LA-41; creators CH-SSG-12, CH-PYG-02).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
