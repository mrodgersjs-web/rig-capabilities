---
id: app-sub-quota-gate
version: 2
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: enforce quotas and credits in the creation path, and make every charge and webhook idempotent in test mode with live keys at Gate-D
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: quota gate limit
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | lessons LA-08 TG-04 LA-47 LA-46 LA-07 | uncalibrated
tier: sub
parent: app-studio-backend-data
stage: backend-data
audience: builder
lessons: LA-08 TG-04 LA-47 LA-46 LA-07
jev_gate: app.prompt
jev_decision: 121937
content_sha256: b893e67c072768a58fbe47d4a17ea07c4c1556350f6dbba82fec3f03ffa73b6a
---

# Quota, credits and payments gate (App Studio sub prompt, v2)

Contract
- id: app-sub-quota-gate | version: 2 | tier: sub | parent: app-studio-backend-data | stage: backend-data | audience: builder
- inputs: {{QUOTA}}
- output: one quota or credits check in the creation path, a visible counter, a deny response the UI maps to an upgrade prompt, and idempotent charge and webhook handlers
- lessons carried (each one is an instruction to follow):
  - LA-08: Prove the gate with a limit+1 deny test and show the counter moving in the rendered UI.
  - TG-04: Enforce a quota in the one creation path per action, as a token bucket, DB counter or entitlement flag, and hit the deny path before calling it done. (TubeGuruji videos: zcYM_Gqoph4, ciXiibK7Gds, s28yOCBVgGw, rdaSPdCkoFQ)
  - LA-47: Make every charge, webhook and tool-called payment path idempotent and prove it by running it twice with the same idempotency key (exactly one charge); parse each webhook event type with its own payload shape; test store purchases on a real device or the store sandbox; live keys stay behind Gate-D.
  - LA-46: Before a deploy request, add the single-page-app catch-all rewrite to index.html and make the cookie secure flag depend on the environment; prove one deep-link refresh and one login and logout on each environment.
  - LA-07: Env-gate each paid vendor with a NAMED fallback so the app runs without the key, and list missing credentials exactly in a BLOCKED list.
- gates: library gate app.prompt on this text; output gate app.stage-gate on the backend-data record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: requests 1..limit succeed and request limit+1 is denied with the named status (one curl loop), the counter change shows on the rendered page, and two charge requests with the same idempotency key produce exactly one charge record
- stop: stop and report BLOCKED: quota undefined when the spec names no limit, and BLOCKED: live key requested whenever a live key, a real charge or a store submission is needed; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. Put the check in the one creation path for the action, not in the UI (TG-04).
2. Choose the shape: time window (token bucket), cumulative (DB counter) or tier (entitlement flag). Quota: {{QUOTA}}.
3. Deny with the contract's status and a message the UI turns into an upgrade prompt.
4. Prove it with limit+1 requests and show the counter moving on the page (LA-08).
5. Payments that buy credits take an idempotency key: replay the request with the same key and show exactly one charge (LA-47; creators CH-SSG-06).
6. Each webhook event type gets its own payload shape and handler, with its signature verified (CH-CWA-10); session cookies set secure per environment (LA-46).
7. Test-mode keys only; with no key, a named fallback grants demo credits without charging (LA-07). Store purchases are proven on a real device or the store sandbox (CH-GXD-03).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
