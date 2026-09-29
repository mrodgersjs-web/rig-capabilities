---
name: youtube-lama-dev
description: "Lama Dev (@LamaDev) corpus skill: 53 transcribed MERN/Next.js app tutorials with the densest UI-first build order of the five channels, plus Prisma/Mongoose/Express and hydration traps, 12 typed App Studio lessons and grep commands for the local transcripts."
tags: [rig, app-studio, youtube-corpus, lama-dev, mern, nextjs, express, prisma]
metadata:
  parent: app-studio
  tier: corpus
  channel: lama-dev
  handle: "@LamaDev"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/lama-dev
outcome: "Channel-scoped evidence for App Studio stages web-frontend, backend-data and scaffold-setup, every claim bound to a video id and a relative transcript position."
activation: "Load for MERN/Express middleware, Mongoose and Prisma schema pushes, form coercion, cart/variant state, hydration with persisted stores, or when you need Lama Dev cited as evidence."
instruction: "Mine the local corpus with grep, verify every quote against the transcript before citing it, route which-lesson-applies judgments through rig-s1gate before any frontier model, and fail closed on any claim you cannot bind to a transcript position."
applies_when:
  env: "local corpus at .context/app-creators/lama-dev"
  runtime: "React 18/19, Next.js 14/15, Express 5, Mongoose, Prisma"
  deps: "transcripts/<video_id>.txt and _cards/lama-dev.json"
  params: "quotes max 25 words verbatim"
  budget: "one grep per claim"
  scale: "channel scope only"
permissions:
  - fs.read
  - bash
flow:
  - Read _cards/lama-dev.json for stats, stack shares and the build order.
  - grep the transcripts to confirm the exact wording before quoting anything.
  - Attach youtube:<video_id>@pos<0.xx> plus the verbatim quote to each claim.
  - Route lesson-selection judgments through rig-s1gate (doctrine.surface) before acting.
  - Fail closed when a claim cannot be verified in the corpus.
done_when:
  - "file:capabilities/skills/youtube-lama-dev/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-lama-dev/references/lessons.jsonl:CH-LMA-"
  - "file:capabilities/skills/youtube-lama-dev/references/stage-map.json"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/youtube-lama-dev/SKILL.md"
out_of_scope:
  - treating this channel's opinion as RIG doctrine
  - copying its course scaffolding or Discord support model
  - any claim without a transcript position
---

Start here when: the build is MERN/Express or Next.js with a hand-built UI, and you need the React hydration, middleware and schema-push traps in checkable form.

JEV FIRST, binding on every lama-dev mining, quoting and App Studio lesson-application step: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this skill's verdicts go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the lesson does not apply, and an uncalibrated ESCALATE is a held decision. Fail closed: a claim this corpus cannot bind to `youtube:<video_id>@pos<0.xx>` plus a <=25-word verbatim quote a grep reproduces is dropped, never paraphrased into plausible prose.

## Load surface

Always loaded at the start of every task that mines this channel's corpus or applies its typed lessons to an App Studio build: the `app-studio` meta-skill routes stage work here and its conductor loads this skill from its routes table before the stage's first action. It is a task-start surface, not a deep reference an agent must already know about. The typed judgment "which of these lessons applies to this build" runs through JEV before any frontier model call, and DEFERRED is the only answer when the classifier is down.


## @LamaDev - digest

- **what it builds**: one complete app per tutorial (Pinterest, blog, school management, e-commerce, Netflix, real estate, booking, Fiverr clone, social X), MERN and Next.js in roughly equal weight. 39 of 53 transcribed videos are build videos (build share 0.74), 982,470 words across 2021-2026.
- **episode shape**: 200-445 minutes, chapter-per-feature with very fine granularity (30-40 chapters per video), UI design chapters named explicitly ("Masonry Grid Design with CSS", "Responsive Top Bar Design").
- **stack it favours** (share of transcribed videos): React 47 (88.7%), Next.js 30 (56.6%), TypeScript 22 (41.5%), Express 17 (32.1%), TanStack Query 16 (30.2%), MongoDB 15 (28.3%), Tailwind 13 (24.5%), Redux 13 (24.5%), Firebase 8 (15.1%), Stripe 8 (15.1%), Prisma 7 (13.2%), Clerk 6 (11.3%).
- **typical build order** (marker windows seen_in, median position 0-1): setup 42 @0.05, ui 286 @0.33, data 122 @0.48, auth 100 @0.50, api 109 @0.53, payments 12 @0.55, ai 12 @0.61, media 48 @0.62, realtime 33 @0.75, testing 3 @0.82, deploy 18 @0.96.
  This is the most **UI-first** of the five: 286 UI marker windows at median 0.33, with the data layer and auth both landing around the midpoint. Useful for design-ux and web-frontend evidence, and a caution for backend-data ordering.
- **what to mine it for**: hydration mismatches (nested buttons, theme-dependent render, persisted zustand), Express middleware `next()` semantics, Prisma/Mongoose schema push discipline, form type coercion, cart line identity, caching defaults, and React fragments under `<Link>`.
- **what NOT to copy**: its UI-before-data order (App Studio builds the schema first), its light touch on tests (3 testing windows at median 0.82), and its own disclaimer that these are tutorials, not production apps.

## Top videos

| id | published | min | title |
|---|---|---|---|
| O9YnPuKC4w4 | 2025-09-29 | 445 | Full-Stack E-Commerce App with Microservices Architecture (Monorepo) |
| x4LhjMk-mkA | 2025-09-29 | 398 | React Node.js MongoDB Full-Stack Pinterest App Tutorial |
| Pfy3q6PbbRA | 2025-09-29 | 373 | React Node.js Blog App Full Tutorial (Infinite Scroll, User Roles, Filters) |
| 6sfiAyKy8Jo | 2024-09-29 | 373 | Next.js Full-Stack School Management App (Role Based Dashboard) |
| I0BOUiFe9WY | 2024-09-29 | 360 | Next.js E-Commerce App Full Tutorial with the Best Headless Solution |
| o080tU3sd0k | 2024-09-29 | 354 | Full-Stack Social Media App with React 19 & Next.js 15 & MySQL |
| tsNswx0nRKM | 2021-09-29 | 305 | React Node.js Netflix App: MERN Stack + JWT Full Tutorial |
| eJ3YysWaP_A | 2024-09-29 | 300 | React Node.js Real Estate App (MERN, Real-time Chat) |
| csUM7yfiaMw | 2023-09-29 | 268 | React Node.js Fiverr App (MERN Freelance Service App) |
| rNSzejRkHcg | 2025-09-29 | 262 | Next.js 15 MySQL Social X App w Real-Time Notifications |
| vCOSTG10Y4o | 2024-09-29 | 295 | Next.js 14 Complete Course 2024 |
| DpYE5zPDRVQ | 2023-09-29 | 245 | Full-Stack Blog App Tutorial (Next.js MongoDB) |
| 6dvYioHX328 | 2025-09-29 | 240 | Next.js E-Commerce App & Admin Panel UI Design Tutorial |
| k3Vfj-e1Ma4 | 2022-09-29 | 229 | React Node.js Booking App (MERN Reservation App) |
| CCF-xV3RSSs | 2022-09-29 | 207 | React Node.js Video Sharing App (Redux, JWT, Cookies) |

## Mining the corpus

```bash
C=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/lama-dev
ls "$C/transcripts" | wc -l                      # 53 files
grep -n -i -o -E '.{0,200}hydration.{0,200}' "$C/transcripts/SjsQdfvxjL8.txt"
grep -n -i -o -E '.{0,200}prisma DB and push.{0,200}' "$C/transcripts/eJ3YysWaP_A.txt"
grep -n -i -o -E '.{0,200}skip hydration.{0,200}' "$C/transcripts/aYzT06aQkGI.txt"
```
Card: `/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/lama-dev.json`

53 of 108 videos transcribed on 2026-09-28; scrape resuming.

## Typed lessons

`references/lessons.jsonl` holds 12 typed lessons `CH-LMA-01..12` in the App Studio ledger format,
each evidence entry `youtube:<video_id>@pos<0.xx>` plus a <=25-word quote grep-verified against that
transcript. `references/stage-map.json` maps each lesson to an App Studio stage.

## How App Studio uses it

| stage | what Lama Dev feeds |
|---|---|
| web-frontend | nested-button hydration (CH-LMA-01), suppressHydrationWarning (CH-LMA-02), persisted-store skipHydration (CH-LMA-03), cart line identity (CH-LMA-10), Link fragments (CH-LMA-11) |
| backend-data | prisma db push (CH-LMA-04), Express next() (CH-LMA-05), revalidatePath client cache (CH-LMA-06), form type coercion (CH-LMA-07), response.ok checks (CH-LMA-09), fetch caching defaults (CH-LMA-12) |
| scaffold-setup | stale .git before git init (CH-LMA-08) |
| design-ux | its 286 UI marker windows are the best local source for component-level layout evidence |

Bench candidates: `references/bench-candidates.json` (BENCH-LMA-01 multi-author blog,
BENCH-LMA-02 real-estate listings with chat), each scoped to one ~50-minute builder run.
