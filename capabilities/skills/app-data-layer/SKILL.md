---
name: app-data-layer
description: "App Studio sub-skill, stage 5 (backend-data): schema as the source of truth, auth deny paths, quota and credits gates proven with limit+1, background jobs proven with forced-due fixtures, key transforms swept across every consumer, and persistence read back through a second path. Use for any database, auth, payments, webhook, or background-job slice in a web or mobile app."
tags: [rig, app-studio, sub-skill, backend, database, auth, quotas, jobs]
metadata:
  parent: app-studio
  tier: sub
  stage: backend-data
  extends: "tg-saas-skeleton, tg-auth-wiring, auth-implementation-patterns, database-migrations, prisma-patterns, supabase-postgres-best-practices, stripe-integration, tg-quota-gates, tg-durable-ai-pipelines"
outcome: "A backend slice whose schema, deny paths, gates, and jobs each carry an executed proof: migration applied, signed-out redirect, limit+1 deny, forced-due job run, and a read-back of persisted rows."
activation: "Load for any schema, migration, auth, credits, quota, payments, webhook, or background-job work, or when an endpoint returns a clean empty result that looks suspicious."
instruction: "Keep the schema file authoritative, prove every gate at limit+1, prove every job with a forced-due fixture, sweep all consumers when a key shape changes, read persisted records back through a second path, and gate the slice."
applies_when:
  env: "local PGlite service or Postgres for build and test; Neon or Supabase in production"
  runtime: "Next.js route handlers or server actions; Supabase edge functions; Flutter clients"
  deps: "Drizzle or Prisma schema; auth vendor (Clerk, Supabase auth, NextAuth)"
  params: "quota numbers are product decisions (corpus range 1 per day to 15 per 24h)"
  budget: "one slice per gate or table"
  scale: "single app; not multi-tenant enterprise isolation"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Apply the schema from the committed schema file and read the tables back.
  - Prove auth deny paths and every quota or credits gate at limit plus one.
  - Prove each background job with a forced-due fixture instead of a clean exit.
  - Sweep every consumer in the same change when a key shape or transform changes.
  - Read persisted records back through a different path and gate the slice.
done_when:
  - "grep:capabilities/skills/app-data-layer/SKILL.md:LA-05"
  - "grep:capabilities/skills/app-data-layer/SKILL.md:forced-due"
  - "grep:capabilities/skills/app-data-layer/SKILL.md:limit.1 deny"
  - "cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py"
out_of_scope:
  - disabling row-level security to move faster (one corpus video does; RIG does not carry it)
  - production data changes without Mike's approval
  - payment plan purchases (Gate-D)
---

# app-data-layer

JEV FIRST, binding on every backend-data step: an agent whose only context is this excerpt
sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call; this stage's verdicts go to `rig-s1gate check app.stage-gate` and `api.backend`. When the classifier is
unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9;
below that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

Always loaded at the start of every backend-data task: the `app-studio` meta-skill routes
stage 5 here and `app-studio-conductor` loads it from its routes table before the
stage's first action. It is a task-start surface, not a deep reference an agent
must already know about.

Sub-skill of `app-studio`, stage 5 of 11. Main skills it extends: `tg-saas-skeleton`,
`tg-auth-wiring`, `auth-implementation-patterns`, `database-migrations`, `prisma-patterns`,
`supabase-postgres-best-practices`, `stripe-integration`, `tg-quota-gates`,
`tg-durable-ai-pipelines`. Sub-process: `tg-auth-schema-wiring`, `tg-background-jobs`.

## Procedure

1. **Schema is the source of truth.** Commit the schema file and its SQL migration; state
   which database runs where. When a runtime layer deviates (Grokbot used a thin SQL
   client over the PGlite service instead of drizzle's proxy), write the deviation in the
   README and keep the schema file authoritative.
2. **Drizzle pg-proxy contract (LA-06).** The remote callback returns `{ rows: [...] }` and
   rows are array-mode in field order; object-keyed rows silently map to `[{}]`. Prove it
   with a standalone query before wiring it into Next.
3. **Auth deny paths.** Signed-out requests to protected routes redirect; the middleware
   public-route list includes `/` (a deployed corpus app demanded login on its landing
   page because it did not).
4. **Gates at limit+1 (LA-08).** Every quota, credits, or plan gate gets a deny test at
   limit+1 and a visible counter: Grokbot credits went 5 to 4 in the rendered sidebar and
   agent #4 on the free plan returned 402.
5. **Jobs are proven with a forced-due fixture (LA-05).** No long AI job inside a request
   handler. Backdate `next_run_at`, call the tick, expect `{"ran":1}`. A clean exit with
   `{"ran":0}` is what a broken join looks like: after a snake-to-camel layer shipped, the
   tick still read `r.agent_id` and silently ran nothing.
6. **Sweep consumers on any key-shape change (LA-05).** Rename, transform, or normalize
   keys and every reader moves in the same change.
7. **Read back persistence (LA-24).** An endpoint's `status: ok` is a claim. Read the row
   through a different path; the TransformFit chat endpoint returned ok while persisting
   only `{message, timestamp}` and dropping screen and run.
8. **Test data (LA-18).** Know whether the build points at production before automated
   sign-ups; clean up and poll deletion.

## Evidence

memory/episodic/2026-09-26.md#L11, #L124, #L128; memory/projects/transformfit-qa.md#L16;
tubeguruji-doctrine laws 4, 5, and 8.
