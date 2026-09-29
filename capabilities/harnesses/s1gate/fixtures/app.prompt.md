# app-sub-json-store (App Studio sub-prompt, v1)

Contract
- id: app-sub-json-store | version: 1 | tier: sub | parent: app-studio-backend-data | stage: backend-data | audience: builder
- inputs: {{DATA_DIR}} (default .data/), {{CONTRACT}}
- output: a store module used by every API route, plus a backend-data stage record whose Evidence block shows each write read back
- lessons carried: LA-24 (read the persisted record back through a different path), TG-20 (duplicate effects must not double-write)
- gates: library app.prompt; output app.stage-gate on .app-studio/stages/backend-data.md (required nouls above 0.9; DEFERRED when the classifier is down)
- done_when: `rm -rf .data && npm run build` exits 0, the server boots from an empty store, and each POST in the contract is followed by a GET that returns the stored fields
- stop: if the store cannot be written inside the workspace, stop and report BLOCKED: <path and error>; no deploys, pushes or paid APIs (Gate-D)

1. Keep all data under {{DATA_DIR}}; create it on first write so an empty checkout boots.
2. Write atomically: write a temp file in the same folder, then rename it over the target.
3. Read the file on every request; never cache it in module scope across requests.
4. Make create requests idempotent where the client may retry (TG-20).
5. Prove persistence (LA-24): `curl -s -X POST ...` then `curl -s .../:id`; paste both status codes and body excerpts into the Evidence block with the exact commands.
