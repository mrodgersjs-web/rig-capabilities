---
name: youtube-sonny-sangha
description: "Sonny Sangha (@SonnySangha): 137-video app-build corpus (45 transcribed, 1.94M words) of multi-app Next.js and React Native crash courses plus AI-agent builds. Load before mining its transcripts for App Studio lessons or quoting it as evidence."
tags: [rig, app-studio, youtube-corpus, nextjs, react-native, ai-agents, mobile]
metadata:
  parent: app-studio
  tier: corpus-surface
  handle: "@SonnySangha"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/sonny-sangha
outcome: "Typed, evidence-backed build rules from the Sonny Sangha corpus, each bound to a transcript position and a verbatim quote, ready to fire as App Studio gates."
activation: "Load when a build touches Next.js full-stack, React Native/Expo, Clerk auth, Stripe billing, or AI-agent features, or before quoting Sonny Sangha as evidence for an App Studio decision."
instruction: "Mine the local corpus for concrete build rules; route every typed judgment (which lesson applies to a build) to JEV via rig-s1gate BEFORE any frontier model call, and fail closed when the classifier is down or a claim is not grep-verified in the corpus."
applies_when:
  env: "local corpus at metadata.corpus_root; no network access needed"
  runtime: "bash + python3 over .context/app-creators/sonny-sangha and its card"
  deps: "card .context/app-creators/_cards/sonny-sangha.json; references/lessons.jsonl"
  params: "quotes are <= 25 words verbatim from the transcript named in the evidence id"
  budget: "one grep pass per lesson candidate"
  scale: "one channel; App Studio stages only"
permissions:
  - fs.read
  - bash
flow:
  - Read the channel card for stats, stack shares, build order, and scored gotcha windows.
  - Grep the local transcripts for the failure phrase and confirm the exact quote and its position.
  - Write the rule as a typed lesson with its trigger, mandated check, and evidence id.
  - Run the lesson validator and the JEV surface gate before calling the file usable.
  - Feed the lesson to the App Studio stage named in references/stage-map.json.
done_when:
  - "grep:capabilities/skills/youtube-sonny-sangha/SKILL.md:## Top videos"
  - "file:capabilities/skills/youtube-sonny-sangha/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-sonny-sangha/SKILL.md:Start here when:"
out_of_scope:
  - publishing or redistributing this corpus (transcripts are copyrighted and stay local)
  - treating a corpus-derived lesson as a passed gate without a run receipt
  - pasting transcript passages longer than 25 words into any output
  - inventing stack shares, counts, or dates not present in the card
---

Start here when: a build decision touches Next.js full-stack, Expo/React Native, Clerk/Stripe, or an AI agent and you want a corpus-tested rule instead of a guess.

JEV FIRST, binding on every mining and lesson-application step on this channel: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this surface's typed judgments go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that a lesson does not advance, and an advisory PASS is not permission to send, push, deploy or publish.

## Load surface

Always loaded at the start of any task that mines this corpus or applies its lessons: `app-studio` routes the matching stage here, and this surface is opened before the first mining command or lesson check. It is a task-start surface, not a deep reference an agent must already know about.

## What this surface is

### Sonny Sangha - digest

- **What the channel builds**: long-form "build N apps in M hours" crash courses (Next.js 13/15, React Native/Expo) plus one-off AI-agent and SaaS builds. 21 of 45 transcribed videos are build videos (build_share 0.47), 2017-2026, 1,939,899 words in the transcribed set.
- **Episode shape**: two formats. (1) 12-40 hour multi-app courses with per-app chapters ("AI Notion Clone | Build 1 of 12", "Disney+ Clone | Build 8 of 12"); (2) 25-45 minute single-feature builds ("How to Add API Keys to ANY AI App in Minutes", "Rate Limiting, Bot Protection").
- **Stack it favours (card, videos / share of transcribed set / years)**: nextjs 29 / 0.64 / 2022-2026, anthropic 21 / 0.47 / 2025-2026, clerk 18 / 0.40 / 2025-2026, openai 18 / 0.40 / 2023-2026, react 17 / 0.38 / 2021-2026, stripe 12 / 0.27 / 2022-2026, typescript 11 / 0.24, react-native 9 / 0.20, expo 7 / 0.16, convex 7 / 0.16 / 2025-2026. Recent tail is AI-heavy: anthropic, ai-sdk, inngest, zod, arcjet, playwright.
- **Typical build order (card, median position in the transcript, seen_in)**: setup 0.31 (40) -> auth 0.35 (48) -> data 0.35 (27) -> realtime 0.37 (26) -> ai 0.40 (63) -> ui 0.44 (98) -> api 0.50 (58) -> testing 0.50 (28) -> media 0.52 (15) -> payments 0.74 (24) -> deploy 0.76 (24). Auth and AI come early; payments and deploy are the last quarter of the video.
- **Mine it for**: failure-and-fix windows (the card scores them; e.g. Expo cache/env reload, SSR-client mismatch, idempotent charge tool calls, deprecated model ids, cached responses leaking user data), the "pillar" framing of production AI agents (speed/memory/freshness/compounding), and defensive upload handling.
- **What NOT to copy**: the 12-apps-in-37-hours pacing (it produces breadth, not verified slices); sponsored product as the default architecture (Redis context engine, Sanity, Replit Agent); "I fixed it and then I broke it" live-debugging as a build process; deprecated model ids (Claude 3.5 Sonic) baked into demos.

## Top videos (signal-sorted, from the card; 45 of 137 transcribed)

| video id | published | minutes | transcribed words | title | url |
|---|---|---|---|---|---|
| `cso7-4oAPNQ` | 2025-09-29 | 2251 | 484,030 | Next.js 15 Full-Stack Course For Beginners (12 Apps in 37 Hours | 2025) | https://www.youtube.com/watch?v=cso7-4oAPNQ |
| `7DVdVGm7Ht8` | 2023-09-29 | 1147 | 247,952 | The Ultimate NEXT.JS 13 Crash Course for Beginners - Build 6 Apps in 18 Hours! | https://www.youtube.com/watch?v=7DVdVGm7Ht8 |
| `6fNy0iD3hsk` | 2022-09-29 | 1051 | 226,286 | NEXT.JS Crash Course for Beginners - Build 6 Apps in 17 Hours (SSR, Auth, Full-Stack + Mor | https://www.youtube.com/watch?v=6fNy0iD3hsk |
| `-2yUgcBqgSM` | 2025-09-29 | 1189 | 225,933 | Learn AI Agents by Building 4 Full-Stack Apps in 19 Hours! (Next.js 15 Beginner Crash Cour | https://www.youtube.com/watch?v=-2yUgcBqgSM |
| `AkEnidfZnCU` | 2022-09-29 | 853 | 184,369 | React Native Crash Course for Beginners - Build 4 Apps in 14 Hours (Redux, Tailwind + More | https://www.youtube.com/watch?v=AkEnidfZnCU |
| `5ckSvrxiRI8` | 2025-09-29 | 861 | 172,565 | React Native Crash Course 2.0 for Beginners - Build 4 Apps in 14 Hours (Expo, Tailwind, Pa | https://www.youtube.com/watch?v=5ckSvrxiRI8 |
| `1KPG3LiE4jU` | 2024-09-29 | 763 | 163,381 | The Ultimate AI Next.js 13 Crash Course for Beginners - Build 4 Apps in 12 Hours! (2025) | https://www.youtube.com/watch?v=1KPG3LiE4jU |
| `Dl8ad3aSFoE` | 2026-03-29 | 43 | 10,393 | How to Build a SaaS in 2026 | Masterclass (B2B, Multi Tenant, Next.js, Roles / Permissions | https://www.youtube.com/watch?v=Dl8ad3aSFoE |
| `ilIC8Z3L8w8` | 2026-07-29 | 36 | 8,405 | The EASIEST & CHEAPEST way to send messages with your app (SMS/WhatsApp/RCS) | https://www.youtube.com/watch?v=ilIC8Z3L8w8 |
| `X9gqHaPn48w` | 2026-08-29 | 27 | 8,185 | Finally we have AI Coding for ENTERPRISE Users! (Full Tutorial with Security & Governance) | https://www.youtube.com/watch?v=X9gqHaPn48w |
| `rbMpF8N5XJI` | 2025-09-29 | 34 | 7,910 | Here's why your Next.js 15 app is at risk & HOW to FIX it! (Rate Limiting, Bot Protection  | https://www.youtube.com/watch?v=rbMpF8N5XJI |
| `JSYOZvtkAx4` | 2026-07-29 | 31 | 7,321 | I Built an AI Voice Agent That Actually Works (AI Receptionist Full Beginner Tutorial) | https://www.youtube.com/watch?v=JSYOZvtkAx4 |
| `r2vIvUm6I4A` | 2026-04-29 | 32 | 7,137 | This AI Can Plan, Design and Build an Entire App at the Same Time! (Replit Agent 4 Tutoria | https://www.youtube.com/watch?v=r2vIvUm6I4A |
| `mwn2y3UZTL4` | 2026-08-29 | 26 | 6,400 | I built a real-time AI Character that talks back & takes actions (Video AI Agent Tutorial  | https://www.youtube.com/watch?v=mwn2y3UZTL4 |
| `lOeDlzgjwmI` | 2026-04-29 | 27 | 6,309 | How to Add API Keys to ANY AI App in Minutes! (Scopes, Auth & Permissions) | https://www.youtube.com/watch?v=lOeDlzgjwmI |

## Mining the local corpus

```bash
CORPUS=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/sonny-sangha
CARD=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/sonny-sangha.json
ls "$CORPUS/transcripts" | wc -l                      # transcribed count
grep -n -i -o -E '.{0,200}idempotent.{0,200}' "$CORPUS/transcripts/OZLdtusYmzw.txt"
grep -n -i -o -E '.{0,200}hydration.{0,200}' "$CORPUS/transcripts/7DVdVGm7Ht8.txt"
python3 -c "import json;d=json.load(open('$CARD'));print(d['stack']);print(d['build_order'])"
# regenerate this card after new transcripts land:
python3 capabilities/skills/app-studio/scripts/mine_creator_corpus.py .context/app-creators/sonny-sangha
```

Evidence id format in `references/lessons.jsonl`: `youtube:<video_id>@pos<0.xx>` (fractional character offset into the transcript) plus `quote: <=25 words verbatim`.

## How App Studio uses it

`references/stage-map.json` routes each lesson to a stage. This channel concentrates on **web-frontend** (SSR/client mismatch, console warnings), **backend-data** (cache invalidation, cached user data, upload validation, idempotent charges), **ai-features** (agent memory, latency budget, model ids), plus one lesson each for **mobile** (env cache), **architecture-stack** (vendor type drift), **verify-qa** (verify in a real browser), and **scaffold-setup** (inspect before running third-party code). Bench candidates in `references/bench-candidates.json` are sized for one 50-minute builder run.

Typed judgment routing: when a builder or agent asks "does SSG-06 apply here?", that is a JEV judgment. Run `./bin/rig-s1gate check <rubric> --file <artifact> --subject "doctrine:youtube-sonny-sangha" --json` and DEFER if it errors.

## Coverage

45 of 137 videos transcribed on 2026-09-28; scrape resuming. Coverage is good but not complete: 45 of 137 is 0.33 of the channel, biased toward the long crash courses (the transcribed set carries 1.94M words). Treat absent topics as unmeasured, not absent.
