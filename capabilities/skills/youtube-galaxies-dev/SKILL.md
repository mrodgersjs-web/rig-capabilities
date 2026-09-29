---
name: youtube-galaxies-dev
description: "Simon Grimm / galaxies_dev (@galaxies_dev): 654-video corpus, PARTIAL coverage (10 transcribed, 337K words) of React Native and Expo app builds. This is the Y-B mobile stage source. Load before mining its transcripts for App Studio mobile lessons or quoting it as evidence."
tags: [rig, app-studio, youtube-corpus, react-native, expo, mobile, partial-corpus]
metadata:
  parent: app-studio
  tier: corpus-surface
  handle: "@galaxies_dev"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/galaxies-dev
outcome: "Typed, evidence-backed mobile build rules from the galaxies_dev corpus, each bound to a transcript position and a verbatim quote, staged as candidates while the scrape resumes."
activation: "Load for any React Native, Expo, Expo Router, NativeWind, mobile billing or mobile observability work, or before quoting galaxies_dev as evidence. This is the mobile-stage counterpart to the notJust-style web corpus."
instruction: "Mine the local corpus for concrete mobile build rules; route every typed judgment (which lesson applies to a build) to JEV via rig-s1gate BEFORE any frontier model call, and fail closed when the classifier is down or a claim is not grep-verified in the corpus. Lessons are APPEND-only: add new ones as transcripts arrive."
applies_when:
  env: "local corpus at metadata.corpus_root; no network access needed"
  runtime: "bash + python3 over .context/app-creators/galaxies-dev and its card"
  deps: "card .context/app-creators/_cards/galaxies-dev.json; references/lessons.jsonl"
  params: "quotes are <= 25 words verbatim from the transcript named in the evidence id"
  budget: "one grep pass per lesson candidate"
  scale: "one channel; PARTIAL coverage, App Studio mobile stage only"
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
  - "grep:capabilities/skills/youtube-galaxies-dev/SKILL.md:## Top videos"
  - "file:capabilities/skills/youtube-galaxies-dev/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-galaxies-dev/SKILL.md:Start here when:"
out_of_scope:
  - publishing or redistributing this corpus (transcripts are copyrighted and stay local)
  - treating a corpus-derived lesson as a passed gate without a run receipt
  - pasting transcript passages longer than 25 words into any output
  - claiming channel-wide statistics from 10 of 654 videos
---

Start here when: the build is a mobile app (Expo/React Native) and you want the device-level traps that come after "it renders in the simulator".

JEV FIRST, binding on every mining and lesson-application step on this channel: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this surface's typed judgments go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that a lesson does not advance, and an advisory PASS is not permission to send, push, deploy or publish.

## Load surface

Always loaded at the start of any task that mines this corpus or applies its lessons: `app-studio` routes the matching stage here, and this surface is opened before the first mining command or lesson check. It is a task-start surface, not a deep reference an agent must already know about.

## What this surface is

### Simon Grimm (galaxies_dev) - digest (PARTIAL: 10 of 654 transcribed)

- **What the channel builds**: complete React Native apps with an AI layer. 6 of 10 transcribed videos are build videos (build_share 0.6), 2024-2026, 337,050 words: food delivery app, ChatGPT clone, AI caption editor, Amazon-style app with voice agents, Trello clone, plus short demos (IAP testing, drawer navigation, AI app tooling).
- **Episode shape**: 30-45 minute full-app builds ("Build a Food Delivery App with React Native (Expo Router, Maps, Reanimated, Zustand) | Wolt clone") and 13-40 minute focused pieces ("Drawer Navigation with Nested Tabs using Expo Router", "How I Test In-App Purchases While Building an App with AI").
- **Stack it favours (card, videos / share of the 10 transcribed / years)**: react-native 10 / 1.0, expo 9 / 0.9, react 8 / 0.8, expo-router 7 / 0.7, bun 7 / 0.7, typescript 6 / 0.6, openai 5 / 0.5, tailwind 4 / 0.4, clerk 4 / 0.4, nativewind 4 / 0.4, supabase 3 / 0.3, sentry 3 / 0.3, react-hook-form 3 / 0.3, drizzle 2 / 0.2.
- **Typical build order (card, median position, seen_in)**: setup 0.10 (5) -> auth 0.28 (14) -> api 0.28 (3) -> data 0.29 (9) -> testing 0.39 (1) -> ui 0.53 (8) -> ai 0.63 (6) -> media 0.70 (5) -> realtime 0.81 (5) -> payments 0.89 (4). Mobile-specific: auth gates come at 0.28, before UI; payments are last (0.89).
- **Mine it for**: the mobile layer a web corpus never covers: error monitoring as foundation work, per-environment session-replay rates, RevenueCat/IAP that fails in the simulator, missing polyfills for crypto/TextEncoder on device, Expo Router version drift, keyboard overlap on forms, explicit index routes in drawer+tab navigation.
- **What NOT to copy**: running the whole build on the "latest version" of a router whose typed routes are broken; trusting simulator results for purchases; copying documentation snippets without diffing them against installed versions; the near-absent testing (seen_in 1).

## Top videos (transcribed set, 10 of 654; coverage is thin so this is the whole transcribed corpus)

| video id | published | minutes | title | url |
|---|---|---|---|---|
| `XaMUNPzwFwo` | 2026-01-29 | 21 | How I Test In-App Purchases While Building an App with AI | https://www.youtube.com/watch?v=XaMUNPzwFwo |
| `aYftPYZJsy8` | 2025-11-29 | 480 | Build a Food Delivery App with React Native (Expo Router, Maps, Reanimated, Zustand) | Wolt Clone | https://www.youtube.com/watch?v=aYftPYZJsy8 |
| `53ssD7QkVUI` | 2025-10-29 | 21 | React Native Apps You NEED To See! | https://www.youtube.com/watch?v=53ssD7QkVUI |
| `A3NyYsNxMGM` | 2025-09-29 | 18 | Drawer Navigation with Nested Tabs using Expo Router | https://www.youtube.com/watch?v=A3NyYsNxMGM |
| `1P9dZZcRcao` | 2025-09-29 | 385 | Build the Amazon App with React Native & AI Voice Agents (Vapi, NativeWind, TanStack, Expo) | https://www.youtube.com/watch?v=1P9dZZcRcao |
| `Snw0b-PMhsU` | 2025-09-29 | 405 | Build Your Own AI Caption Editor with React Native (Convex, ElevenLabs, NativeWind, Expo) | https://www.youtube.com/watch?v=Snw0b-PMhsU |
| `W9bbVJwCyqo` | 2025-09-29 | 38 | React Native AI Apps can't get easier (Expo & Vercel AI SDK) | https://www.youtube.com/watch?v=W9bbVJwCyqo |
| `I_o17M30m5I` | 2025-09-29 | 13 | Tailwind is going Mobile | https://www.youtube.com/watch?v=I_o17M30m5I |
| `GZdTP3EQ7ug` | 2024-09-29 | 381 | Build a Trello Clone with React Native (Supabase, Expo Router, Push, Clerk, Drag & Drop) | https://www.youtube.com/watch?v=GZdTP3EQ7ug |
| `8ztx68SUOQo` | 2024-09-29 | 409 | Build a ChatGPT Clone with React Native (Expo, SQLite, RevenueCat, Clerk, OpenAI) | https://www.youtube.com/watch?v=8ztx68SUOQo |

## Mining the local corpus

```bash
CORPUS=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/galaxies-dev
CARD=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/galaxies-dev.json
ls "$CORPUS/transcripts" | wc -l                      # 10 today, grows as the scrape resumes
grep -n -i -o -E '.{0,200}polyfill.{0,200}' "$CORPUS/transcripts/W9bbVJwCyqo.txt"
grep -n -i -o -E '.{0,200}simulator.{0,200}' "$CORPUS/transcripts/XaMUNPzwFwo.txt"
python3 -c "import json;d=json.load(open('$CARD'));print(d['stack']);print(d['build_order'])"
# regenerate the card after new transcripts land, then re-mine and APPEND lessons:
python3 capabilities/skills/app-studio/scripts/mine_creator_corpus.py .context/app-creators/galaxies-dev
```

Evidence id format in `references/lessons.jsonl`: `youtube:<video_id>@pos<0.xx>` (fractional character offset into the transcript) plus `quote: <=25 words verbatim`.

## How App Studio uses it

`references/stage-map.json` routes almost every lesson to the **mobile** stage (GXD-01 error monitoring, GXD-02 replay rates, GXD-03 IAP on device, GXD-04 polyfills, GXD-06 router drift, GXD-07 keyboard, GXD-08 index route), plus **scaffold-setup** (GXD-05 docs snippets). This channel and notJust-style content are the two corpus sources App Studio's mobile stage draws on; where they disagree, prefer the one whose evidence id matches the platform in hand (Expo here).

Typed judgment routing: "does GXD-03 apply to this paywall?" is a JEV judgment. Run `./bin/rig-s1gate check <rubric> --file <artifact> --subject "doctrine:youtube-galaxies-dev" --json` and DEFER if it errors.

## Coverage

10 of 654 videos transcribed on 2026-09-28; scrape resuming. Coverage is PARTIAL (0.02) and YouTube throttled the scrape, so every number above describes the 10 transcribed videos only. The card and this skill are regenerated from `.context/app-creators/galaxies-dev` as transcripts arrive; lessons are appended, never rewritten.
