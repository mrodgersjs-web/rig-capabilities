---
id: app-sub-clerk-auth
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: wire Clerk with public routes, ownership checks and a demo-user fallback when keys are absent
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: clerk auth wiring
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-backend-data
stage: backend-data
audience: builder
lessons: LA-07 TG-14 TG-15 TG-16
jev_gate: app.prompt
jev_decision: 119527
content_sha256: 69cf59d2831d31354be706ad880599e31694db4cbaed7a2f0bd8ace09c87216d
---

# Clerk auth wiring (App Studio sub prompt, v1)

Contract
- id: app-sub-clerk-auth | version: 1 | tier: sub | parent: app-studio-backend-data | stage: backend-data | audience: builder
- inputs: {{STACK}}
- output: middleware with a public-route list, ClerkProvider in the root layout, protected API routes
- lessons carried (each one is an instruction to follow):
  - LA-07: Env-gate each paid vendor with a NAMED fallback so the app runs without the key, and list missing credentials exactly in a BLOCKED list.
  - TG-14: Keep / (and every public page) in the auth middleware's public-route list; a deployed landing page that demands sign-in is a shipped bug. (TubeGuruji videos: zjwj21wzs4U)
  - TG-15: Before real users: production OAuth origins and redirect URIs, the Clerk production instance, and both login and logout redirect URLs. (TubeGuruji videos: fh1s6UbzJ7k, hCSX5zSb3b4, saoW6BaNamc, zrdbOx0eGtM)
  - TG-16: Gate every mutation on record ownership, not only on being signed in. (TubeGuruji videos: P6dha4Sq8gQ)
- gates: library gate app.prompt on this text; output gate app.stage-gate on the backend-data record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: signed out, `curl -s -o /dev/null -w '%{http_code}' /` prints 200 and a protected API route prints 401; with no Clerk keys set the demo-user fallback serves the app
- stop: report BLOCKED: clerk keys for any check that needs a real Clerk session; never create a Clerk production instance from the bench; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. middleware: list / and every public page as public routes (TG-14).
2. ClerkProvider wraps the root layout; server routes read the user id from the session.
3. Gate each mutation on ownership (TG-16).
4. With the publishable and secret keys absent, fall back to the demo user and say so in stack.md (LA-07).
5. Production needs the Clerk production instance, the real domain and OAuth origins; list them in the release request (TG-15).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
