---
name: tg-durable-ai-pipelines
description: >
  Sub-skill of tubeguruji-doctrine: durable background workflows for multi-step
  AI generation per the TubeGuruji corpus — Inngest step.run chains, Trigger.dev
  agentic workflows, n8n inside a real app — with the production wiring (signing
  keys, Vercel sync, dev-vs-prod data) that the corpus got wrong on camera first.
tags: [rig, doctrine, inngest, triggerdev, workflows, tubeguruji]
metadata:
  source: "corpus — -h1O73T0jmo, 31-Qfr2Pc5Q, 6niOEjus2Vg (Inngest chains), kxM_oEMn3IM, rcEUVADmH2g (Trigger.dev), b_4Z_QpEd2Q (n8n in-app), ciXiibK7Gds, YwcyE1XlUZU, YbUJpaOlUbk, lHFlpc5auDY (Inngest via Vercel integration), VSrcC0y0umc (Inngest framing)"
  extracted: "2026-09-25"
  parent: tubeguruji-doctrine
  subs: [tg-ai-media-pipeline]
outcome: "Multi-step AI jobs run as durable workflows with per-step progress, surviving serverless timeouts, with production event/signing keys verified by an executed sync — not assumed."
activation: "Load when a generation flow has 2+ steps, needs longer than a serverless request, needs retries/resume, or must show per-step progress."
instruction: >
  Move every multi-step generation out of the request path into a durable workflow.
  Each step gets its own step boundary so failures resume instead of restarting.
  A pipeline is not done when it runs locally — it is done when the production
  Inngest/Trigger dashboard shows the function synced and an end-to-end run has
  completed there.
applies_when:
  env: "Next.js app deployed on Vercel (or self-hosted n8n); vendor dashboard account"
  runtime: "Node 18+; vendor SDK (inngest, trigger.dev) or n8n instance"
  deps: "Inngest / Trigger.dev / n8n; provider APIs called inside steps"
  params: "step granularity = one provider call or DB write per step; progress events per step"
  budget: "wiring is hours; free tiers carry dev; production keys are free"
  scale: "tens of concurrent jobs on free tiers; not a high-throughput queue replacement"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - List the generation steps; one step = one provider call or DB write (fetch series data → generate script → TTS → captions → images → save, 31-Qfr2Pc5Q).
  - Wrap the chain in the workflow engine of choice (Inngest step.run / Trigger.dev tasks / n8n workflow triggered by app events, b_4Z_QpEd2Q).
  - Emit per-step progress the UI can render as a progress bar (ciXiibK7Gds, kxM_oEMn3IM).
  - Wire production: connect the Inngest Vercel integration so signing/event keys inject into env, then REDEPLOY and hit "sync app" in the Inngest dashboard (lHFlpc5auDY, -h1O73T0jmo); for Trigger.dev use the Vercel project connect that auto-syncs the secret key (rcEUVADmH2g, kxM_oEMn3IM).
  - Remember the corpus rule: "whenever you update any Inngest signing key you have to redeploy your application" (6niOEjus2Vg).
  - Run one job end-to-end in PRODUCTION and record it in the vendor dashboard.
done_when:
  - "grep:capabilities/skills/tg-durable-ai-pipelines/SKILL.md:step.run"
  - "grep:capabilities/skills/tg-durable-ai-pipelines/SKILL.md:sync app"
  - "grep:data/corpora/how-to/manifest.jsonl:31-Qfr2Pc5Q"
great_example: examples/great/code-engineering/great-tg-media-pipeline.md
out_of_scope:
  - cron scheduling strategy, multi-tenant queue architecture
  - media-step specifics (tg-ai-media-pipeline)
  - paid tier upgrades without Gate-D
quality_floor: "A pipeline proven only on localhost is RED. Production sync + one completed production run is the evidence bar."
---

# Durable AI Pipelines

## Why the corpus moved off request-path

The framing the corpus teaches (VSrcC0y0umc): durable event-driven workflows
"replace traditional queue, state management and scheduling" so that no provider
API call is missed when a chain fans out across multiple AI services — and so a
5-step media job survives the serverless timeout that would kill it inside one
API route.

## The canonical chain (appears in three separate builds)

`fetch source data → generate script → TTS voice → generate captions → generate
images → animate/compose → save` (-h1O73T0jmo, 31-Qfr2Pc5Q, 6niOEjus2Vg). This is
the reusable skeleton for any AI media app; the steps are vendor-swappable.

## Engine selection (corpus usage, not benchmarks)

| Engine | Corpus use | Production wiring gotcha |
|---|---|---|
| Inngest | step.run chains for media generation, daily-task agents | Vercel integration injects signing/event keys → must redeploy → "sync app" in Inngest dashboard before scheduled/generation tasks work (-h1O73T0jmo, lHFlpc5auDY); key rotation forces redeploy (6niOEjus2Vg) |
| Trigger.dev | long-running agentic workflows with step progress (avatar studio: generation, voice cloning, captions) | Vercel project connect auto-syncs the trigger secret key; one-time env pull (rcEUVADmH2g, kxM_oEMn3IM) |
| n8n | automation triggered by app events (resume submit → AI question generation), running local AND self-hosted on Hostinger for production | framed explicitly as "n8n inside a real web application", not standalone automation (b_4Z_QpEd2Q) |

## Dev-vs-prod data trap

Convex/Inngest production environments start EMPTY after deploy — the corpus has to
explain the empty prod dashboard as expected, twice (fh1s6UbzJ7k, hCSX5zSb3b4), and
Convex needs the dev→production deployment URL swapped in env (UgLN9O930vE,
b_4Z_QpEd2Q production deployment key). Empty production data is not a bug; unfixed
env pointing at dev is.

## Progress UX contract

Every corpus pipeline renders per-step progress (progress bar per step, ciXiibK7Gds;
step-by-step bar, kxM_oEMn3IM; Inngest step progress, 6niOEjus2Vg). A silent pipeline
reads as a hang to users — emit progress per step as part of the step, not as an
afterthought.
