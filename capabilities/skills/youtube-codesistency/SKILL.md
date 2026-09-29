---
name: youtube-codesistency
description: "Codesistency (@Codesistency) corpus skill: 7 transcribed mobile + full-stack bootcamp builds (React Native/Expo, Next.js, Clerk, Neon, Stripe) in a thin but high-coverage corpus, with 5 typed App Studio lessons and grep commands for the local transcripts."
tags: [rig, app-studio, youtube-corpus, codesistency, react-native, expo, nextjs]
metadata:
  parent: app-studio
  tier: corpus
  channel: codesistency
  handle: "@Codesistency"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/codesistency
outcome: "Channel-scoped evidence for App Studio stages verify-qa, backend-data, scaffold-setup and web-frontend, every claim bound to a video id and a relative transcript position."
activation: "Load for bootcamp-scale mobile + web builds, error-monitoring and AI-code-review stack choices, Vite env handling, Express error-handler shape, or when you need Codesistency cited as evidence."
instruction: "Mine the local corpus with grep, verify every quote against the transcript before citing it, route which-lesson-applies judgments through rig-s1gate before any frontier model, and fail closed on any claim you cannot bind to a transcript position."
applies_when:
  env: "local corpus at .context/app-creators/codesistency"
  runtime: "Expo / React Native, Next.js, Vite, Express"
  deps: "transcripts/<video_id>.txt and _cards/codesistency.json"
  params: "quotes max 25 words verbatim; thin corpus (7 transcripts) - claims stay narrow"
  budget: "one grep per claim"
  scale: "channel scope only"
permissions:
  - fs.read
  - bash
flow:
  - Read _cards/codesistency.json for stats, stack shares and the build order.
  - grep the transcripts to confirm the exact wording before quoting anything.
  - Attach youtube:<video_id>@pos<0.xx> plus the verbatim quote to each claim.
  - Route lesson-selection judgments through rig-s1gate (doctrine.surface) before acting.
  - Fail closed when a claim cannot be verified in the corpus.
done_when:
  - "file:capabilities/skills/youtube-codesistency/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-codesistency/references/lessons.jsonl:CH-CDS-"
  - "file:capabilities/skills/youtube-codesistency/references/stage-map.json"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/youtube-codesistency/SKILL.md"
out_of_scope:
  - generalising from 7 transcripts to a whole channel's doctrine
  - treating this channel's opinion as RIG doctrine
  - any claim without a transcript position
---

Start here when: you need the bootcamp-style mobile-plus-web stack decisions (monitoring, AI code review, env handling) or a thin-corpus second opinion on a config trap.

JEV FIRST, binding on every codesistency mining, quoting and App Studio lesson-application step: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this skill's verdicts go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the lesson does not apply, and an uncalibrated ESCALATE is a held decision. Fail closed: a claim this corpus cannot bind to `youtube:<video_id>@pos<0.xx>` plus a <=25-word verbatim quote a grep reproduces is dropped, never paraphrased into plausible prose.

## Load surface

Always loaded at the start of every task that mines this channel's corpus or applies its typed lessons to an App Studio build: the `app-studio` meta-skill routes stage work here and its conductor loads this skill from its routes table before the stage's first action. It is a task-start surface, not a deep reference an agent must already know about. The typed judgment "which of these lessons applies to this build" runs through JEV before any frontier model call, and DEFERRED is the only answer when the classifier is down.


## @Codesistency - digest

- **what it builds**: very long bootcamp bundles and single big apps - a 1372-minute "build 4 full stack projects" bootcamp, a 960-minute React Native e-commerce app, a 720-minute Claude Code mobile bootcamp, an OnlyFans-style Next.js/Stripe platform, a React Native chat app, and a Next.js social app. 6 of 7 transcribed videos are build videos (build share 0.86), 1,008,146 words across 2024-2026.
- **episode shape**: chapter-per-phase with explicit numbered parts ("0 - Course Introduction", "1 - AI Trip Planner App"), and - unusually - a "Deployment and Backend Config" phase before the app UI is written.
- **stack it favours** (share of transcribed videos; n=7 so treat shares as directional): React 7 (100%), Tailwind 7 (100%), TypeScript 7 (100%), React Native 6 (85.7%), MongoDB 6 (85.7%), Clerk 5 (71.4%), Postgres 5 (71.4%), Stripe 5 (71.4%), TanStack Query 5 (71.4%), Express 5 (71.4%), Next.js 4 (57.1%), Expo 4 (57.1%).
- **typical build order** (marker windows seen_in, median position 0-1): ui 7 @0.14, setup 13 @0.28, data 7 @0.29, api 8 @0.31, ai 1 @0.33, auth 9 @0.36, deploy 4 @0.70, media 6 @0.72, payments 4 @0.79, realtime 6 @0.79, testing 1 @1.00.
  UI markers land first (0.14) and deployment lands at 0.70 - **before** payments and realtime. This is a bootcamp ordering, not a production ordering.
- **what to mine it for**: the standing tooling choice (Sentry for error monitoring plus an AI code reviewer before the first deploy), boot-fail-loud env validation, Vite vs Node env access, Express error-handler arity, and TanStack Query invalidation semantics.
- **what NOT to copy**: its ordering (UI first, testing last at median 1.00), and any frequency claim - with 7 transcripts, "always" here means "in these 7 builds".

## Top videos

| id | published | min | title |
|---|---|---|---|
| MDZC8VDZnV8 | 2024-09-29 | 1372 | FREE Coding Bootcamp - Build 4 Full Stack Projects in 23 Hours |
| m1f5qkFDZnk | 2025-12-29 | 960 | Build a Full Stack E-Commerce Mobile App with React Native |
| OcqWu_kasck | 2026-09-15 | 720 | CLAUDE CODE BOOTCAMP: Build 3 Real Mobile Apps |
| mduqkHlJujA | 2024-09-29 | 692 | Build an OnlyFans with Next.js, Stripe and React |
| ufo46oWej3g | 2026-01-29 | 600 | The Ultimate React Native Chat App in 2026 |
| vUYopHWOURg | 2025-09-29 | 262 | Next.js Tutorial 2025 - Build a Full Stack Social App |

## Mining the corpus

```bash
C=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/codesistency
ls "$C/transcripts" | wc -l                      # 7 files
grep -n -i -o -E '.{0,200}Sentry for error monitoring.{0,200}' "$C/transcripts/OcqWu_kasck.txt"
grep -n -i -o -E '.{0,200}import meta.{0,200}' "$C/transcripts/ufo46oWej3g.txt"
grep -n -i -o -E '.{0,200}global middleware.{0,200}' "$C/transcripts/q3HE1dFiJBI.txt"
```
Card: `/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/codesistency.json`

7 of 47 videos transcribed on 2026-09-28; scrape resuming.

## Typed lessons

`references/lessons.jsonl` holds 5 typed lessons `CH-CDS-01..05` in the App Studio ledger format,
each evidence entry `youtube:<video_id>@pos<0.xx>` plus a <=25-word quote grep-verified against that
transcript. `references/stage-map.json` maps each lesson to an App Studio stage.

## How App Studio uses it

| stage | what Codesistency feeds |
|---|---|
| verify-qa | monitoring + AI code review before first deploy (CH-CDS-01) |
| backend-data | fail-loud DB env validation (CH-CDS-02), Express error-handler arity (CH-CDS-04) |
| scaffold-setup | import.meta.env in Vite (CH-CDS-03) |
| web-frontend | invalidateQueries return value is not a success signal (CH-CDS-05) |

Bench candidate: `references/bench-candidates.json` (BENCH-CDS-01 social feed with posts, likes and
notifications), scoped to one ~50-minute builder run.
