---
name: youtube-josh-tried-coding
description: "Josh tried coding (@joshtriedcoding): 250-video corpus, PARTIAL coverage (5 transcribed, 620K words) of 10-hour single-app full-stack courses on Next.js, tRPC, Prisma, Stripe, shadcn. Load before mining its transcripts for App Studio lessons or quoting it as evidence."
tags: [rig, app-studio, youtube-corpus, nextjs, trpc, prisma, stripe, partial-corpus]
metadata:
  parent: app-studio
  tier: corpus-surface
  handle: "@joshtriedcoding"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/josh-tried-coding
outcome: "Typed, evidence-backed build rules from the Josh tried coding corpus, each bound to a transcript position and a verbatim quote, staged as candidates while the scrape resumes."
activation: "Load when a build touches a Next.js + tRPC/Prisma/Stripe stack, a hydration mismatch, package-manager choice, or auth typing, or before quoting Josh tried coding as evidence."
instruction: "Mine the local corpus for concrete build rules; route every typed judgment (which lesson applies to a build) to JEV via rig-s1gate BEFORE any frontier model call, and fail closed when the classifier is down or a claim is not grep-verified in the corpus. Lessons are APPEND-only: add new ones as transcripts arrive."
applies_when:
  env: "local corpus at metadata.corpus_root; no network access needed"
  runtime: "bash + python3 over .context/app-creators/josh-tried-coding and its card"
  deps: "card .context/app-creators/_cards/josh-tried-coding.json; references/lessons.jsonl"
  params: "quotes are <= 25 words verbatim from the transcript named in the evidence id"
  budget: "one grep pass per lesson candidate"
  scale: "one channel; PARTIAL coverage, App Studio stages only"
permissions:
  - fs.read
  - bash
flow:
  - Read the channel card for stats, stack shares, build order, and scored gotcha windows.
  - Grep the local transcripts for the failure phrase and confirm the exact quote and its position.
  - Append the rule as a typed lesson with its trigger, mandated check, and evidence id (never overwrite existing rows).
  - Run the lesson validator and the JEV surface gate before calling the file usable.
  - Regenerate the card after new transcripts land, then re-mine for gaps.
done_when:
  - "grep:capabilities/skills/youtube-josh-tried-coding/SKILL.md:## Top videos"
  - "file:capabilities/skills/youtube-josh-tried-coding/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-josh-tried-coding/SKILL.md:Start here when:"
out_of_scope:
  - publishing or redistributing this corpus (transcripts are copyrighted and stay local)
  - treating a corpus-derived lesson as a passed gate without a run receipt
  - pasting transcript passages longer than 25 words into any output
  - claiming channel-wide statistics from 5 of 250 videos
---

Start here when: a build is a Next.js + tRPC + Prisma + Stripe product and you want the traps that showed up in five complete 10-hour builds, not a happy-path tutorial.

JEV FIRST, binding on every mining and lesson-application step on this channel: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this surface's typed judgments go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that a lesson does not advance, and an advisory PASS is not permission to send, push, deploy or publish.

## Load surface

Always loaded at the start of any task that mines this corpus or applies its lessons: `app-studio` routes the matching stage here, and this surface is opened before the first mining command or lesson check. It is a task-start surface, not a deep reference an agent must already know about.

## What this surface is

### Josh tried coding - digest (PARTIAL: 5 of 250 transcribed)

- **What the channel builds**: one app per course, end to end. All 5 transcribed videos are build videos (build_share 1.0), 2023-2025, 620,466 words across 5 transcripts (each 10-12 hours): e-commerce shop, digital marketplace, two SaaS platforms, Reddit clone.
- **Episode shape**: "Build a Complete X | Full Course" with 20-40 chapters; monolithic single-sitting builds that move UI -> auth -> data -> payments -> deploy.
- **Stack it favours (card, videos / share of the 5 transcribed / years)**: nextjs 5 / 1.0, react 5 / 1.0, tailwind 5 / 1.0, shadcn 5 / 1.0, typescript 5 / 1.0, aws 5 / 1.0, tanstack-query 5 / 1.0, zod 5 / 1.0, prisma 4 / 0.8, postgres 4 / 0.8, stripe 4 / 0.8, trpc 4 / 0.8, react-hook-form 4 / 0.8, neon 3 / 0.6.
- **Typical build order (card, median position, seen_in)**: ui 0.18 (18) -> auth 0.29 (13) -> data 0.32 (8) -> setup 0.40 (10) -> media 0.44 (10) -> realtime 0.59 (1) -> api 0.64 (9) -> payments 0.78 (14) -> deploy 0.93 (6) -> testing 1.0 (1). UI first, payments late, testing essentially absent (seen_in 1).
- **Mine it for**: the mistakes inside long builds (hydration mismatches, package-manager breakage, auth type imports, Stripe key loading, Vercel image bandwidth, form actions silently swallowing submits, dependency version drift in Zod/resolver APIs).
- **What NOT to copy**: the "we'll fix it later" treatment of hydration warnings; mixing pnpm with yarn/npm in one project; following tutorial code without pinning the dependency versions it was written against; the absence of automated testing.

## Top videos (transcribed set, 5 of 250; the corpus is thin and the table is short by design)

| video id | published | minutes | transcribed words | title | url |
|---|---|---|---|---|---|
| `SG82Aqcaaa0` | 2024-09-29 | 720 | 136,019 | Build a Complete E-Commerce Shop with Next.js 14, Tailwind, React | Full Course 2024 | https://www.youtube.com/watch?v=SG82Aqcaaa0 |
| `06g6YJ6JCJU` | 2024-09-29 | 720 | 133,453 | Build a Complete Digital Marketplace with Next.js 14, React, tRPC, Tailwind | Full Course  | https://www.youtube.com/watch?v=06g6YJ6JCJU |
| `ucX2zXAZ1I0` | 2023-09-29 | 674 | 125,114 | Build a Complete SaaS Platform with Next.js 13, React, Prisma, tRPC, Tailwind | Full Cours | https://www.youtube.com/watch?v=ucX2zXAZ1I0 |
| `vEQlN17miq8` | 2025-09-29 | 720 | 121,094 | Build a Complete SaaS With Next.js, Tailwind, React, Hono.js (2024) | https://www.youtube.com/watch?v=vEQlN17miq8 |
| `mSUKMfmLAt0` | 2023-09-29 | 586 | 104,786 | Build and Deploy a Fullstack Reddit Clone: Next.js 13, React, Tailwind, Auth, Prisma, MySQ | https://www.youtube.com/watch?v=mSUKMfmLAt0 |

## Mining the local corpus

```bash
CORPUS=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/josh-tried-coding
CARD=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/josh-tried-coding.json
ls "$CORPUS/transcripts" | wc -l                      # 5 today, grows as the scrape resumes
grep -n -i -o -E '.{0,200}hydration.{0,200}' "$CORPUS/transcripts/06g6YJ6JCJU.txt"
grep -n -i -o -E '.{0,200}api key.{0,200}' "$CORPUS/transcripts/vEQlN17miq8.txt"
# regenerate the card after new transcripts land, then re-mine and APPEND lessons:
python3 capabilities/skills/app-studio/scripts/mine_creator_corpus.py .context/app-creators/josh-tried-coding
```

Evidence id format in `references/lessons.jsonl`: `youtube:<video_id>@pos<0.xx>` (fractional character offset into the transcript) plus `quote: <=25 words verbatim`.

## How App Studio uses it

`references/stage-map.json` routes each lesson to a stage: **backend-data** (auth types, provider keys), **web-frontend** (hydration source fix), **scaffold-setup** (one package manager), **architecture-stack** (dependency version drift), **verify-qa** (submit fires a request), **ship-release** (media bandwidth cost). Because coverage is 5 of 250, treat these as candidate rules: the App Studio ledger may adopt them only after a run receipt proves the check in a real build.

Typed judgment routing: "does JTC-04 apply here?" is a JEV judgment. Run `./bin/rig-s1gate check <rubric> --file <artifact> --subject "doctrine:youtube-josh-tried-coding" --json` and DEFER if it errors.

## Coverage

5 of 250 videos transcribed on 2026-09-28; scrape resuming. Coverage is PARTIAL (0.02) and YouTube throttled the scrape, so every number above describes the 5 transcribed videos only. The card and this skill are regenerated from `.context/app-creators/josh-tried-coding` as transcripts arrive; lessons are appended, never rewritten.
