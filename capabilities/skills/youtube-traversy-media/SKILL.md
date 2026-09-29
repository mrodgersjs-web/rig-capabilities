---
name: youtube-traversy-media
description: "Traversy Media (@TraversyMedia): 1032-video corpus (51 transcribed, 678K words) of framework crash courses and full-stack builds across React, Django, Laravel, PHP, Vue, WebRTC and Postgres. Load before mining its transcripts for App Studio lessons or quoting it as evidence."
tags: [rig, app-studio, youtube-corpus, react, django, laravel, postgres, full-stack]
metadata:
  parent: app-studio
  tier: corpus-surface
  handle: "@TraversyMedia"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/traversy-media
outcome: "Typed, evidence-backed build rules from the Traversy Media corpus, each bound to a transcript position and a verbatim quote, ready to fire as App Studio gates."
activation: "Load when a build touches form handling, auth, Postgres/Prisma, error monitoring, realtime, or when a cross-framework rule is needed, or before quoting Traversy Media as evidence."
instruction: "Mine the local corpus for concrete build rules; route every typed judgment (which lesson applies to a build) to JEV via rig-s1gate BEFORE any frontier model call, and fail closed when the classifier is down or a claim is not grep-verified in the corpus."
applies_when:
  env: "local corpus at metadata.corpus_root; no network access needed"
  runtime: "bash + python3 over .context/app-creators/traversy-media and its card"
  deps: "card .context/app-creators/_cards/traversy-media.json; references/lessons.jsonl"
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
  - "grep:capabilities/skills/youtube-traversy-media/SKILL.md:## Top videos"
  - "file:capabilities/skills/youtube-traversy-media/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-traversy-media/SKILL.md:Start here when:"
out_of_scope:
  - publishing or redistributing this corpus (transcripts are copyrighted and stay local)
  - treating a corpus-derived lesson as a passed gate without a run receipt
  - pasting transcript passages longer than 25 words into any output
  - inventing stack shares, counts, or dates not present in the card
---

Start here when: a build touches forms, auth, a relational database, error monitoring, or realtime and you want a rule proven across four server frameworks, not one.

JEV FIRST, binding on every mining and lesson-application step on this channel: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this surface's typed judgments go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that a lesson does not advance, and an advisory PASS is not permission to send, push, deploy or publish.

## Load surface

Always loaded at the start of any task that mines this corpus or applies its lessons: `app-studio` routes the matching stage here, and this surface is opened before the first mining command or lesson check. It is a task-start surface, not a deep reference an agent must already know about.

## What this surface is

### Traversy Media - digest

- **What the channel builds**: framework crash courses and complete small apps across the whole web stack. 24 of 51 transcribed videos are build videos (build_share 0.47), 2020-2026, 678,356 words. Unlike the other Y-B channels it is genuinely polyglot: Python/Django, PHP/Laravel, Vue, React, Astro, vanilla JS.
- **Episode shape**: 3-7 hour single-framework courses with 20-40 chapters ("Python Django 7 Hour Course", "Laravel From Scratch", "Web RTC Full Course"), 2-4 hour project builds ("Create A Booking App From Scratch", "NextJS + Postgres and Error Monitoring"), and 5-20 minute opinion/tooling clips ("Cursor Crash Course", "Figma Oversimplified", "Git & GitHub Crash Course").
- **Stack it favours (card, videos / share / years)**: react 27 / 0.53 / 2021-2026, postgres 16 / 0.31 / 2022-2026, tailwind 15 / 0.29, typescript 15 / 0.29, openai 15 / 0.29 / 2025-2026, anthropic 14 / 0.27 / 2025-2026, nextjs 12 / 0.24, express 11 / 0.22, neon 9 / 0.18, prisma 8 / 0.16, docker 8 / 0.16, aws 7 / 0.14.
- **Typical build order (card, median position, seen_in)**: payments 0.14 (1) -> setup 0.23 (51) -> data 0.40 (49) -> api 0.44 (24) -> ui 0.47 (66) -> ai 0.59 (24) -> media 0.68 (32) -> realtime 0.69 (14) -> auth 0.71 (33) -> testing 0.77 (4) -> deploy 1.0 (13). Note auth lands late (0.71) and testing is barely present (seen_in 4): the corpus is a source for data/API/UI order rules and for its own testing gap, not for an auth-first model.
- **Mine it for**: cross-framework form and CSRF rules (Laravel, Django, PHP), server/client double execution in shared loader code, error observability at both API and client, lint-warning builds, realtime join/leave handling, empty-state guards, and the "errors were being suppressed" post-mortem of vibe coding.
- **What NOT to copy**: framework-first course pacing where the app is an excuse for the framework; the late-auth ordering; the near-absent automated testing (seen_in 4 of 51); live "restart your computer and see" debugging.

## Top videos (signal-sorted, from the card; 51 of 1032 transcribed)

| video id | published | minutes | transcribed words | title | url |
|---|---|---|---|---|---|
| `PtQiiknWUcI` | 2022-09-29 | 430 | 84,563 | Python Django 7 Hour Course | https://www.youtube.com/watch?v=PtQiiknWUcI |
| `ISv22NNL-aE` | 2021-09-29 | 388 | 77,485 | 6 Hour Vue.js & Firebase Project - FireBlogs | https://www.youtube.com/watch?v=ISv22NNL-aE |
| `QsH8FL0952k` | 2022-09-29 | 275 | 61,671 | Web RTC Full Course & More | https://www.youtube.com/watch?v=QsH8FL0952k |
| `2eebptXfEvw` | 2021-09-29 | 387 | 59,709 | PHP For Absolute Beginners | 6.5 Hour Course | https://www.youtube.com/watch?v=2eebptXfEvw |
| `MYyJ4PuL4pY` | 2022-09-29 | 258 | 41,526 | Laravel From Scratch | 4+ Hour Course | https://www.youtube.com/watch?v=MYyJ4PuL4pY |
| `l9zh0pqEHyc` | 2025-09-29 | 252 | 36,943 | Create A Booking App From Scratch | React, Next.js, Appwrite, Tailwind | https://www.youtube.com/watch?v=l9zh0pqEHyc |
| `e-hGCPaRZYk` | 2025-10-29 | 220 | 35,010 | Ambient Sound Mixer - JavaScript OOP Project - 3.5+ Hours | https://www.youtube.com/watch?v=e-hGCPaRZYk |
| `NKiTlo_dgb8` | 2025-09-29 | 203 | 30,859 | NextJS + Postgres and Error Monitoring  - Full Stack Support Ticketing System | https://www.youtube.com/watch?v=NKiTlo_dgb8 |
| `bCpFbERgj7s` | 2025-09-29 | 183 | 28,089 | React Native Crash Course+ | Build a Mobile App In 3 Hours | https://www.youtube.com/watch?v=bCpFbERgj7s |
| `VR3p7almo_c` | 2025-09-29 | 166 | 25,178 | Build & Deploy An AI-Powered Chat App | Vue, Node, TypeScript,  Open AI, Stream & Neon Dat | https://www.youtube.com/watch?v=VR3p7almo_c |
| `XCifkDC0yXA` | 2026-04-29 | 98 | 16,964 | React Native Crash Course 2026 - Build a Complete Mobile App | https://www.youtube.com/watch?v=XCifkDC0yXA |
| `Oi9z5gfIHJs` | 2022-09-29 | 95 | 15,354 | Astro Crash Course | https://www.youtube.com/watch?v=Oi9z5gfIHJs |
| `C2GpeepcmYs` | 2026-06-29 | 63 | 11,512 | Claude Code Crash Course For Developers | https://www.youtube.com/watch?v=C2GpeepcmYs |
| `vA5TTz6BXhY` | 2025-09-29 | 49 | 8,932 | Git & GitHub Crash Course 2025 | https://www.youtube.com/watch?v=vA5TTz6BXhY |
| `5zR1ZE5aqho` | 2025-09-29 | 52 | 8,897 | Cursor Crash Course & AI Coding For Beginners | https://www.youtube.com/watch?v=5zR1ZE5aqho |

## Mining the local corpus

```bash
CORPUS=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/traversy-media
CARD=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/traversy-media.json
ls "$CORPUS/transcripts" | wc -l                      # transcribed count
grep -n -i -o -E '.{0,200}csrf.{0,200}' "$CORPUS/transcripts/MYyJ4PuL4pY.txt"
grep -n -i -o -E '.{0,200}executed server-side.{0,200}' "$CORPUS/transcripts/jcBzuuZvLCE.txt"
python3 -c "import json;d=json.load(open('$CARD'));print(d['build_order']);print([g['video'] for g in d['gotchas'][:10]])"
python3 capabilities/skills/app-studio/scripts/mine_creator_corpus.py .context/app-creators/traversy-media
```

Evidence id format in `references/lessons.jsonl`: `youtube:<video_id>@pos<0.xx>` (fractional character offset into the transcript) plus `quote: <=25 words verbatim`.

## How App Studio uses it

`references/stage-map.json` routes each lesson to a stage. This channel concentrates on **web-frontend** (double execution, realtime, empty states), **backend-data** (CSRF + named inputs, server-side required fields), **verify-qa** (no suppressed errors), **ship-release** (lint-warning builds, branch discipline) and **operate-learn** (error context at both ends, session replay). It is the strongest Y-B source for the form/CSRF/validation family and for cross-framework rules, because its rules survive Django, Laravel and React.

Typed judgment routing: "does TRV-02 apply to this form?" is a JEV judgment. Run `./bin/rig-s1gate check <rubric> --file <artifact> --subject "doctrine:youtube-traversy-media" --json` and DEFER if it errors.

## Coverage

51 of 1032 videos transcribed on 2026-09-28; scrape resuming. Coverage is 0.05 of the channel and biased to its longest courses (678K words in 51 files), so the per-framework tail (Bun, Astro, OOP, CSS) is thin. Absent topics are unmeasured, not absent.
