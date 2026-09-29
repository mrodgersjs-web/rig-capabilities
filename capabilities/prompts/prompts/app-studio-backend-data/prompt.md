---
id: app-studio-backend-data
version: 2
status: draft
updated: 2026-09-28
task: App Studio backend-data stage prompt: implement the API contract, storage, auth, quotas and jobs with executed proof per endpoint
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: api contract endpoints backend data layer for the app
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-24 TG-16 TG-20 LA-42 LA-43 LA-50 | uncalibrated
tier: main
parent: app-studio-meta
stage: backend-data
audience: builder
lessons: LA-24 TG-16 TG-20 LA-42 LA-43 LA-50
jev_gate: app.prompt
jev_decision: 121935
content_sha256: 11e3055ed656ea68d7e15693045a31a1135c2a83f1c506e67910dff72ffc571d
---

# Stage 5: backend-data (App Studio main prompt, v2)

Contract
- id: app-studio-backend-data | version: 2 | tier: main (stage) | parent: app-studio-meta | stage: backend-data | audience: builder
- inputs: {{CONTRACT}} (the API contract lines), {{STACK}} (storage and auth choices), spec.md and stack.md
- output: .app-studio/stages/backend-data.md whose Evidence block has one curl row (command, exit code, status, body excerpt) per contract line, plus the API routes themselves
- lessons carried (each one is an instruction to follow):
  - LA-24: Read the persisted record back through a different path before claiming an endpoint stored it.
  - TG-16: Gate every mutation on record ownership, not only on being signed in. (TubeGuruji videos: P6dha4Sq8gQ)
  - TG-20: Make writes idempotent: React StrictMode runs effects twice in development and duplicated rows follow. (TubeGuruji videos: zlZ_7VTfxUs)
  - LA-42: Every middleware, server action and route handler ends each path with next(), a response or a rethrow: an Express error handler declares four parameters, a server-action catch rethrows after recording, and a hung request or a swallowed redirect is reproduced with one request before the fix.
  - LA-43: Coerce form and query values (they arrive as strings) inside the schema before validating, read the parsed data only after the success check, and reject incomplete input server-side with a named error the UI shows; test one empty submit and one wrong-type submit.
  - LA-50: Name the invalidation for every cached read and prove it: after a write the next read returns the new value, and the same cached route requested as two users never returns one user's data to the other.
- gates: library gate app.prompt on this text; output gate app.stage-gate plus api.backend (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: every contract endpoint has an Evidence row with the curl command, the observed status and a body excerpt matching the contract fields, including each error status the contract names
- stop: stop and report BLOCKED: <endpoint> when the storage layer cannot persist inside the workspace; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval
- sub-prompts owned: app-sub-json-store, app-sub-demo-user-auth, app-sub-clerk-auth, app-sub-drizzle-neon, app-sub-quota-gate, app-sub-durable-job

Question this stage answers: are schema, auth, gates and jobs proven by executed checks?

1. For each contract line, implement the path, method, field names and every status code it names, then curl it against the production server and paste the command, exit code, status and body excerpt into the Evidence block. Error cases get their own rows.
2. Storage: when the stack names a JSON file, follow app-sub-json-store; when it names Postgres, follow app-sub-drizzle-neon.
3. Auth: a named demo-user stub (app-sub-demo-user-auth) unless Clerk is in scope (app-sub-clerk-auth). Every mutation checks record ownership (TG-16).
4. Quotas go in the creation path (app-sub-quota-gate) when the spec names a limit; multi-step work runs as durable steps (app-sub-durable-job).
5. Make writes idempotent where a client may repeat them (TG-20).
6. After each POST, read the record back with a GET before claiming it stored (LA-24).
7. Build in this order: storage, auth, routes, then quotas and jobs, with a production build after each.
8. Every middleware, server action and route handler ends each path with next(), a response or a rethrow; prove no request hangs with `curl -s -m 5` (LA-42; creators CH-LMA-05, CH-CDS-04).
9. Coerce string form values in the schema before validating, and test one empty and one wrong-type submit (LA-43; CH-LMA-07).
10. Name the invalidation for every cached read: a write is followed by a read that returns the new value (LA-50; CH-SSG-03).
11. Charges, credits and webhooks follow app-sub-quota-gate.

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
