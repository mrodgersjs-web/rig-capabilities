---
name: youtube-notjust-dev
description: "NotJust Dev (@notjustdev) corpus skill: 10 transcribed React Native / Expo production courses (Clerk, Supabase, Expo Router) with App Store submission coverage, 5 typed App Studio lessons and grep commands for the local transcripts."
tags: [rig, app-studio, youtube-corpus, notjust-dev, react-native, expo, supabase]
metadata:
  parent: app-studio
  tier: corpus
  channel: notjust-dev
  handle: "@notjustdev"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/notjust-dev
outcome: "Channel-scoped evidence for App Studio stages mobile, ship-release and backend-data, every claim bound to a video id and a relative transcript position."
activation: "Load for Expo / React Native build work, keyboard and safe-area handling, native rebuild rules, FlatList data guards, or App Store submission steps."
instruction: "Mine the local corpus with grep, verify every quote against the transcript before citing it, route which-lesson-applies judgments through rig-s1gate before any frontier model, and fail closed on any claim you cannot bind to a transcript position."
applies_when:
  env: "local corpus at .context/app-creators/notjust-dev"
  runtime: "Expo, Expo Router, React Native CLI, Supabase"
  deps: "transcripts/<video_id>.txt and _cards/notjust-dev.json"
  params: "quotes max 25 words verbatim; thin corpus (10 transcripts) - claims stay narrow"
  budget: "one grep per claim"
  scale: "channel scope only"
permissions:
  - fs.read
  - bash
flow:
  - Read _cards/notjust-dev.json for stats, stack shares and the build order.
  - grep the transcripts to confirm the exact wording before quoting anything.
  - Attach youtube:<video_id>@pos<0.xx> plus the verbatim quote to each claim.
  - Route lesson-selection judgments through rig-s1gate (doctrine.surface) before acting.
  - Fail closed when a claim cannot be verified in the corpus.
done_when:
  - "file:capabilities/skills/youtube-notjust-dev/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-notjust-dev/references/lessons.jsonl:CH-NJD-"
  - "file:capabilities/skills/youtube-notjust-dev/references/stage-map.json"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/youtube-notjust-dev/SKILL.md"
out_of_scope:
  - generalising from 10 transcripts to a whole channel's doctrine
  - treating this channel's opinion as RIG doctrine
  - any claim without a transcript position
---

Start here when: the build is a React Native / Expo mobile app and you need the keyboard, native-rebuild, list-guard and App Store submission traps in checkable form.

JEV FIRST, binding on every notjust-dev mining, quoting and App Studio lesson-application step: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this skill's verdicts go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the lesson does not apply, and an uncalibrated ESCALATE is a held decision. Fail closed: a claim this corpus cannot bind to `youtube:<video_id>@pos<0.xx>` plus a <=25-word verbatim quote a grep reproduces is dropped, never paraphrased into plausible prose.

## Load surface

Always loaded at the start of every task that mines this channel's corpus or applies its typed lessons to an App Studio build: the `app-studio` meta-skill routes stage work here and its conductor loads this skill from its routes table before the stage's first action. It is a task-start surface, not a deep reference an agent must already know about. The typed judgment "which of these lessons applies to this build" runs through JEV before any frontier model call, and DEFERRED is the only answer when the classifier is down.


## @notjustdev - digest

- **what it builds**: mobile-first products with a shared web surface - an 8-hour full-stack community app, an 8-hour Expo/Supabase course, a TikTok clone, an Airbnb clone, an AI social-listening app, an AI chat app, and a step-by-step App Store publishing walkthrough. 7 of 10 transcribed videos are build videos (build share 0.70), 282,923 words across 2020-2026.
- **episode shape**: module-shaped ("Module 1: UI", "Module 2: Backend", "Module 3: Production") in the long courses, numbered screens in the app builds, and one unusually valuable **pure ops** video on App Store Connect submission.
- **stack it favours** (share of transcribed videos; n=10): React Native 9 (90%), React 8 (80%), Expo 8 (80%), Supabase 5 (50%), Expo Router 5 (50%), TypeScript 4 (40%), TanStack Query 3 (30%), Clerk 2 (20%), Firebase 2 (20%), Postgres 2 (20%), OpenAI 2 (20%), AWS 2 (20%).
- **typical build order** (marker windows seen_in, median position 0-1): ui 13 @0.14, deploy 4 @0.18, setup 11 @0.20, api 5 @0.47, auth 5 @0.51, data 14 @0.59, media 13 @0.72, testing 3 @0.76, ai 4 @0.78, payments 13 @0.84, realtime 6 @0.95.
  Deploy markers at median 0.18 are **early** - this channel provisions hosting and accounts before the feature work. Payments and realtime sit in the last sixth.
- **what to mine it for**: Expo/React Native runtime traps (keyboard + safe area, StatusBar theming, native rebuilds after config changes), FlatList data guards, production module ordering, and the App Store Connect checklist.
- **what NOT to copy**: its deploy-before-data ordering, and its thin test practice (3 testing windows at median 0.76).

## Top videos

| id | published | min | title |
|---|---|---|---|
| l9ov48v0M2M | 2025-09-29 | 518 | Build a Full Stack mobile app in just 8 Hours (React Native, Expo, Clerk, Supabase) |
| rIYzLhkG9TA | 2024-09-29 | 496 | React Native Full 8 Hours Course (Expo, Expo Router, Supabase) |
| IxfnhAHnfCM | 2025-11-29 | 313 | Let's Build TikTok with React Native & Supabase (Full Tutorial) |
| ZxkmTsEYfg8 | 2021-09-29 | 192 | Build the Airbnb app in React Native (Tutorial for beginners) |
| Q4q5nPYtmgc | 2025-09-29 | 62 | Building an AI Social Listening App with BrightData |
| CC0H9xz29JI | 2026-06-29 | 61 | Build an AI Chat app using Expo, Clerk, OpenAI, Claude Code |
| r-Z--YDrmjI | 2022-09-29 | 28 | Publish your React Native CLI app to Apple App Store (step-by-step) |

## Mining the corpus

```bash
C=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/notjust-dev
ls "$C/transcripts" | wc -l                      # 10 files
grep -n -i -o -E '.{0,200}safe area.{0,200}' "$C/transcripts/CC0H9xz29JI.txt"
grep -n -i -o -E '.{0,200}expo prebuild.{0,200}' "$C/transcripts/CC0H9xz29JI.txt"
grep -n -i -o -E '.{0,200}Expo status bar.{0,200}' "$C/transcripts/rIYzLhkG9TA.txt"
grep -n -i -o -E '.{0,200}marketing url.{0,200}' "$C/transcripts/r-Z--YDrmjI.txt"
```
Card: `/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/notjust-dev.json`

10 of 83 videos transcribed on 2026-09-28; scrape resuming.

## Typed lessons

`references/lessons.jsonl` holds 5 typed lessons `CH-NJD-01..05` in the App Studio ledger format,
each evidence entry `youtube:<video_id>@pos<0.xx>` plus a <=25-word quote grep-verified against that
transcript. `references/stage-map.json` maps each lesson to an App Studio stage.

## How App Studio uses it

| stage | what NotJust Dev feeds |
|---|---|
| mobile | keyboard + safe area (CH-NJD-01), native rebuild after config change (CH-NJD-02), FlatList nested-collection guards (CH-NJD-03), Expo StatusBar import (CH-NJD-04) |
| ship-release | App Store Connect field checklist (CH-NJD-05) |
| backend-data | nested-collection nullability before list render (CH-NJD-03) |

Bench candidate: `references/bench-candidates.json` (BENCH-NJD-01 community feed mobile app),
scoped to one ~50-minute builder run.
