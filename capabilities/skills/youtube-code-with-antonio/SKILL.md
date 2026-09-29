---
name: youtube-code-with-antonio
description: "Code With Antonio (@codeWithAntonio) corpus skill: 39 transcribed 10-12 hour full-stack clone builds (Next.js + TypeScript + Clerk + Prisma/Drizzle + tRPC), its stack shares, its auth-first build order, 12 typed App Studio lessons and grep commands for the local transcripts."
tags: [rig, app-studio, youtube-corpus, code-with-antonio, nextjs, typescript, prisma, clerk]
metadata:
  parent: app-studio
  tier: corpus
  channel: code-with-antonio
  handle: "@codeWithAntonio"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/code-with-antonio
outcome: "Channel-scoped evidence for App Studio stages backend-data, web-frontend, verify-qa and ship-release, every claim bound to a video id and a relative transcript position."
activation: "Load for Next.js App Router work, Prisma/Drizzle schema and singleton setup, Clerk auth, server actions, tRPC/prefetch hydration, Stripe webhooks, or when you need Antonio cited as evidence."
instruction: "Mine the local corpus with grep, verify every quote against the transcript before citing it, route which-lesson-applies judgments through rig-s1gate before any frontier model, and fail closed on any claim you cannot bind to a transcript position."
applies_when:
  env: "local corpus at .context/app-creators/code-with-antonio"
  runtime: "Next.js 13-16 App Router, TypeScript, Turborepo"
  deps: "transcripts/<video_id>.txt and _cards/code-with-antonio.json"
  params: "quotes max 25 words verbatim"
  budget: "one grep per claim"
  scale: "channel scope only"
permissions:
  - fs.read
  - bash
flow:
  - Read _cards/code-with-antonio.json for stats, stack shares and the build order.
  - grep the transcripts to confirm the exact wording before quoting anything.
  - Attach youtube:<video_id>@pos<0.xx> plus the verbatim quote to each claim.
  - Route lesson-selection judgments through rig-s1gate (doctrine.surface) before acting.
  - Fail closed when a claim cannot be verified in the corpus.
done_when:
  - "file:capabilities/skills/youtube-code-with-antonio/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-code-with-antonio/references/lessons.jsonl:CH-CWA-"
  - "file:capabilities/skills/youtube-code-with-antonio/references/stage-map.json"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/youtube-code-with-antonio/SKILL.md"
out_of_scope:
  - treating this channel's opinion as RIG doctrine
  - copying its clone-app branding or course scaffolding
  - any claim without a transcript position
---

Start here when: a build is a Next.js + TypeScript SaaS or clone with Clerk/Prisma/tRPC/Stripe and you want the config traps that bite at 10 hours in, cited to a video.

JEV FIRST, binding on every code-with-antonio mining, quoting and App Studio lesson-application step: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this skill's verdicts go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the lesson does not apply, and an uncalibrated ESCALATE is a held decision. Fail closed: a claim this corpus cannot bind to `youtube:<video_id>@pos<0.xx>` plus a <=25-word verbatim quote a grep reproduces is dropped, never paraphrased into plausible prose.

## Load surface

Always loaded at the start of every task that mines this channel's corpus or applies its typed lessons to an App Studio build: the `app-studio` meta-skill routes stage work here and its conductor loads this skill from its routes table before the stage's first action. It is a task-start surface, not a deep reference an agent must already know about. The typed judgment "which of these lessons applies to this build" runs through JEV before any frontier model call, and DEFERRED is the only answer when the classifier is down.


## @codeWithAntonio - digest

- **what it builds**: single 640-720 minute full-stack clone or SaaS builds, one product per video (Discord, Trello, YouTube, Cursor, e-commerce + CMS, Duolingo, N8N/Zapier, voice SaaS). 37 of 39 transcribed videos are build videos (build share 0.95) and the corpus is the densest of the five channels at 3,210,416 words across 2023-2026.
- **episode shape**: chapter-per-feature, roughly 12-25 chapters, always opening "Intro & Demo" then "Environment setup" and always closing "Deployment". Backend chapters are interleaved with UI, not deferred.
- **stack it favours** (share of transcribed videos): React 38 (97.4%), Next.js 37 (94.9%), TypeScript 36 (92.3%), Tailwind 34 (87.2%), Clerk 29 (74.4%), Zod 27 (69.2%), shadcn/ui 25 (64.1%), Prisma 22 (56.4%), react-hook-form 20 (51.3%), TanStack Query 19 (48.7%), Postgres 18 (46.2%), Stripe 18 (46.2%).
- **typical build order** (marker windows seen_in, median position 0-1): setup 83 @0.15, auth 52 @0.22, data 33 @0.26, api 34 @0.39, ui 105 @0.42, ai 36 @0.52, media 32 @0.59, realtime 20 @0.72, payments 21 @0.85, deploy 28 @1.00.
  This is the **auth-and-schema-first** order: authentication at 0.22 and the data layer at 0.26 both land before the UI mass at 0.42. It is the closest of the five channels to App Studio's own backend-before-frontend discipline.
- **what to mine it for**: Prisma/Drizzle client setup, server-action error semantics, cookie flags in dev vs prod, hydration vs prefetch, webhook payload shapes, Hono/tRPC typing, monorepo build failures, and mid-build type/lint gate practice.
- **what NOT to copy**: the 12-hour single-video runtime (App Studio caps a builder run at ~50 minutes), vendor lock to one auth provider per build, and the "fix it in a later chapter" habit its own gotcha windows show (several errors surface at 0.85-0.99 of the video).

## Top videos

| id | published | min | title |
|---|---|---|---|
| e_MO-Rcz_MA | 2026-03-01 | 718 | Full Stack AI Voice SaaS: Next.js, tRPC, and Voice Cloning |
| k_D_C3ExypU | 2026-05-29 | 719 | Don't Pay for Claude Code - Build This Instead |
| ig26iRcMavQ | 2025-09-29 | 719 | Full Stack YouTube Clone: tRPC, Mux Video Processing & AI Title Generation |
| pRybm9lXW2c | 2024-09-29 | 714 | Fullstack Trello Clone: Next.js 14, Server Actions, Prisma, Stripe |
| Xf9rHPNBMyQ | 2026-01-29 | 715 | Build a Cursor Clone from Scratch (AI IDE) - Next.js 16 & Convex |
| ZbX4Ok9YX94 | 2023-09-29 | 706 | Fullstack Discord Clone: Next.js 13, React, Socket.io, Prisma |
| ArmPzvHTcfQ | 2025-09-29 | 703 | Build a YouTube Clone with Next.js 15: React, Tailwind, Drizzle, tRPC |
| ED2H_y6dmC8 | 2025-10-29 | 719 | Build and Deploy an N8N & Zapier Clone |
| CAr02YlEJUc | 2025-09-29 | 709 | Build and Deploy a B2B AI SaaS Support Platform |
| xEDCEmqyvC8 | 2025-09-29 | 699 | Build and Deploy a SaaS AI Agent Platform |
| N_uNKAus0II | 2024-09-29 | 673 | Build a Finance SaaS Platform With Nextjs, React, Honojs with CSV Upload |
| dP75Khfy4s4 | 2024-09-29 | 672 | Build a Duolingo Clone With Nextjs, React, Drizzle, Stripe |
| 6fXNWBFPfRM | 2025-09-29 | 676 | Build and Deploy a Multi-Vendor E-Commerce Marketplace |
| 5miHyP6lExg | 2023-09-29 | 641 | Full Stack E-Commerce + Dashboard & CMS: Next.js 13 App Router |
| Big_aFLmekI | 2023-09-29 | 641 | Build a Course & LMS Platform: Next 13, React, Stripe, Mux, Prisma |

## Mining the corpus

```bash
C=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/code-with-antonio
ls "$C/transcripts" | wc -l                      # 39 files
grep -n -i -o -E '.{0,200}hydration error.{0,200}' "$C/transcripts/ffJ38dBzrlY.txt"
grep -n -i -o -E '.{0,200}secure.{0,60}development.{0,200}' "$C/transcripts/dllIBXa0nlE.txt"
grep -n -i -o -E '.{0,200}provider options.{0,200}' "$C/transcripts/k_D_C3ExypU.txt"
```
Card: `/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/code-with-antonio.json`

39 of 44 videos transcribed on 2026-09-28; scrape resuming.

## Typed lessons

`references/lessons.jsonl` holds 12 typed lessons `CH-CWA-01..12` in the App Studio ledger format,
each evidence entry `youtube:<video_id>@pos<0.xx>` plus a <=25-word quote grep-verified against that
transcript. `references/stage-map.json` maps each lesson to an App Studio stage.

## How App Studio uses it

| stage | what Antonio feeds |
|---|---|
| web-frontend | hydration fixes: mounted gate (CH-CWA-01), dynamic + ssr:false (CH-CWA-02), client-only hooks (CH-CWA-08), wrong-surface imports (CH-CWA-09), prefetch/initial-state match (CH-CWA-11) |
| backend-data | Prisma singleton (CH-CWA-05), server-action re-throw (CH-CWA-04), Hono status codes (CH-CWA-07), per-event webhook shapes (CH-CWA-10) |
| ship-release | cookie `secure` flag vs localhost (CH-CWA-03) |
| ai-features | providerOptions on the model call (CH-CWA-06) |
| verify-qa | mid-build production build as a type/lint gate (CH-CWA-12) |

Bench candidates: `references/bench-candidates.json` (BENCH-CWA-01 kanban board, BENCH-CWA-02 finance
CSV import), each scoped to one ~50-minute builder run.
