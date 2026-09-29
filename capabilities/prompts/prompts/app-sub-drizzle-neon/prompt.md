---
id: app-sub-drizzle-neon
version: 1
status: draft
updated: 2026-09-28
task: App Studio sub-prompt: Drizzle ORM over Neon or PGlite with the pg-proxy row contract proven before wiring
category: app-studio
domain: app-studio
model_target: unspecified
score: null
license: first-party
source: first-party: capabilities/prompts/composition/app-studio.md
triggers: drizzle neon postgres pg proxy drizzle
compose: when-shipping-code/app-studio capabilities/prompts/composition/app-studio.md
provenance: first-party: capabilities/prompts/composition/app-studio.md | TubeGuruji doctrine + 11 tg-* skills (video ids inline), App Studio LA ledger, App Bench runs 2026-09-28 | uncalibrated
tier: sub
parent: app-studio-backend-data
stage: backend-data
audience: builder
lessons: LA-01 LA-06 TG-19
jev_gate: app.prompt
jev_decision: 119531
content_sha256: 1975978177e94bf23f657244c43c81d8b2a6d49d7094c1aee108a179cd4628b5
---

# Drizzle with Neon or PGlite (App Studio sub prompt, v1)

Contract
- id: app-sub-drizzle-neon | version: 1 | tier: sub | parent: app-studio-backend-data | stage: backend-data | audience: builder
- inputs: {{STACK}}
- output: schema, migrations and a db module; a standalone query script whose output proves the proxy contract
- lessons carried (each one is an instruction to follow):
  - LA-01: Confirm the toolchain avoids native .node binaries in the Aside sandbox: next --webpack, Tailwind v3, npm i --ignore-scripts, PGlite as a standalone service.
  - LA-06: Return {rows} with array-mode rows from a pg-proxy callback, verified by a standalone query before wiring it into Next.
  - TG-19: Expect production data stores and job dashboards to start empty; swap dev deployment URLs and keys for production ones. (TubeGuruji videos: fh1s6UbzJ7k, UgLN9O930vE, b_4Z_QpEd2Q)
- gates: library gate app.prompt on this text; output gate app.stage-gate on the backend-data record (a required noul passes only above 0.9; DEFERRED when the classifier is down, never a guessed verdict)
- done_when: `node scripts/db-check.mjs` inserts and selects one row and exits 0 before any route uses the db module
- stop: report BLOCKED: database url when neither a Neon URL nor a local PGlite service is available; deploy, git push, publish, purchase, emails to real people and paid API calls stay held for Mike's Gate-D approval

1. In the sandbox run PGlite as a standalone service, not inside the Next process (LA-01).
2. A pg-proxy callback returns {rows} with array-mode rows; prove it with a standalone query script before wiring it into Next (LA-06).
3. Generate migrations with drizzle-kit and apply them; commit the SQL files.
4. Production starts empty; list the production connection string by env var name only (TG-19).

Evidence rule: a step counts as done only when its record shows the exact command, the exit code, and the observed output (status code, body excerpt, file hash or screenshot path). A plan, a stub, a description of the code or a green preview is not evidence.
