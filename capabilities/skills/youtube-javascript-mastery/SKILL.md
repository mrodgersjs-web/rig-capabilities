---
name: youtube-javascript-mastery
description: "JavaScript Mastery (@javascriptmastery) corpus skill: 54 transcribed build-along courses (React/Next/React Native/GSAP), its stack shares, its build order, 12 typed App Studio lessons and grep commands to mine the local transcripts. Load before quoting or mining this channel."
tags: [rig, app-studio, youtube-corpus, javascript-mastery, react, nextjs, react-native]
metadata:
  parent: app-studio
  tier: corpus
  channel: javascript-mastery
  handle: "@javascriptmastery"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/javascript-mastery
outcome: "Channel-scoped evidence for App Studio stages web-frontend, mobile, backend-data, verify-qa and ship-release, with every quoted claim bound to a video id and a relative transcript position."
activation: "Load when a build touches React/Next.js/React Native UI, conditional rendering, deployment rewrites, signup error shapes, or when you need a JSM video cited as evidence."
instruction: "Mine the local corpus with grep, verify every quote against the transcript before citing it, route which-lesson-applies judgments through rig-s1gate before any frontier model, and fail closed on any claim you cannot bind to a transcript position."
applies_when:
  env: "local corpus at .context/app-creators/javascript-mastery"
  runtime: "Next.js App Router, React 18/19, React Native / Expo"
  deps: "transcripts/<video_id>.txt and _cards/javascript-mastery.json"
  params: "quotes max 25 words verbatim"
  budget: "one grep per claim"
  scale: "channel scope only"
permissions:
  - fs.read
  - bash
flow:
  - Read _cards/javascript-mastery.json for stats, stack shares and the build order.
  - grep the transcripts to confirm the exact wording before quoting anything.
  - Attach youtube:<video_id>@pos<0.xx> plus the verbatim quote to each claim.
  - Route lesson-selection judgments through rig-s1gate (doctrine.surface) before acting.
  - Fail closed when a claim cannot be verified in the corpus.
done_when:
  - "file:capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-javascript-mastery/references/lessons.jsonl:CH-JSM-"
  - "file:capabilities/skills/youtube-javascript-mastery/references/stage-map.json"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/youtube-javascript-mastery/SKILL.md"
out_of_scope:
  - treating this channel's opinion as RIG doctrine
  - copying its branding, mascots or course scaffolding
  - any claim without a transcript position
---

Start here when: a build touches React/Next.js/React Native UI, an SPA deploy rewrite, or a signup or error-state design and you want JSM evidence behind the rule.

JEV FIRST, binding on every javascript-mastery mining, quoting and App Studio lesson-application step: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this skill's verdicts go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the lesson does not apply, and an uncalibrated ESCALATE is a held decision. Fail closed: a claim this corpus cannot bind to `youtube:<video_id>@pos<0.xx>` plus a <=25-word verbatim quote a grep reproduces is dropped, never paraphrased into plausible prose.

## Load surface

Always loaded at the start of every task that mines this channel's corpus or applies its typed lessons to an App Studio build: the `app-studio` meta-skill routes stage work here and its conductor loads this skill from its routes table before the stage's first action. It is a task-start surface, not a deep reference an agent must already know about. The typed judgment "which of these lessons applies to this build" runs through JEV before any frontier model call, and DEFERRED is the only answer when the classifier is down.


## @javascriptmastery - digest

- **what it builds**: long build-along mega-courses, each stacking 3-4 complete apps in one video. 49 of 54 transcribed videos are build videos (build share 0.91), 2,227,967 words across 2019-2026.
- **episode shape**: 250-720 minute courses, chaptered per project ("1st Project", "2nd Project" ...), each project running from setup to deployment in the same sitting.
- **stack it favours** (share of transcribed videos): React 52 (96.3%), Next.js 43 (79.6%), Tailwind 40 (74.1%), TypeScript 39 (72.2%), OpenAI 30 (55.6%), React Native 28 (51.9%), Redux 19 (35.2%), GSAP 19 (35.2%), Express 18 (33.3%), MongoDB 16 (29.6%), Three.js 16 (29.6%), Postgres 15 (27.8%), Stripe 15 (27.8%), Gemini 15 (27.8%).
- **typical build order** (marker windows seen_in, median position 0-1): setup 92 @0.25, realtime 10 @0.31, api 27 @0.38, ui 82 @0.40, auth 45 @0.47, data 52 @0.52, media 22 @0.54, ai 26 @0.59, payments 8 @0.82, testing 4 @0.83, deploy 34 @1.00.
  Note the shape: **UI and auth come before the data layer**, and payments/testing land in the last fifth. App Studio's own order is stricter; JSM's order is what a solo tutorial builder does.
- **what to mine it for**: conditional-rendering failure modes, error-state design, install/dependency traps, SPA hosting rewrites, signup endpoint behaviour, React Native platform-API traps, and recent AI-agent-driven debugging practice (its 2025-2026 videos run Claude/Devon against a live app).
- **what NOT to copy**: its "3 apps in one video" course scaffolding, its 12-hour runtime (App Studio caps a builder run at ~50 minutes), and its habit of shipping without tests (testing markers appear in only 4 windows at median position 0.83).

## Top videos

| id | published | min | title |
|---|---|---|---|
| XxXyfkrP298 | 2023-09-29 | 720 | Modern React Web Development Full Course - 12 Hours, 4 Real Industry Web Applications |
| DwbwuYYiBTk | 2024-09-29 | 719 | Build and Deploy 3 Modern Apps and Get Hired as Full Stack Developer |
| 8vIDZO_w7lY | 2025-09-29 | 692 | Build 3 Complete Full-Stack Web Apps and Launch Your Developer Career |
| BTfcnxXevm0 | 2025-09-29 | 628 | Build and Deploy 3 Full-Stack React Native Apps That'll Get You Hired |
| 41lfYQhUzRs | 2025-09-29 | 591 | Build and Deploy 3 Animated Websites with GSAP & Three.js |
| RbxHZwFtRT4 | 2024-09-29 | 596 | Build and Deploy 3 Modern UI/UX Websites and Get Hired |
| ATdaYQw0ptk | 2025-12-29 | 585 | Creative Frontend Course: Master GSAP, Three.js & React in 10 Hours |
| F627pKNUCVQ | 2023-09-29 | 584 | Build and Deploy 4 Modern React Apps and Get Hired |
| ek7hmv5PVV8 | 2026-01-29 | 473 | Full Stack Engineering Course: Full Stack PERN Admin Dashboard |
| dyFVwXROzZk | 2023-09-29 | 496 | Build and Deploy 3 Modern React API Applications in 8 Hours |
| VsUzmlZfYNg | 2022-09-29 | 448 | Build and Deploy a Full Stack MERN Social Media App |
| 6a3Dz8gwjdg | 2024-09-29 | 338 | Build and Deploy a React Admin Dashboard With Real time Data |
| xZ1ba-RLrjo | 2025-09-29 | 336 | Build and Deploy a Full Stack React Admin Dashboard |
| H5FAxTBuNM8 | 2025-09-29 | 300 | DevOps from Zero to Hero: Build and Deploy a Production API |
| gu4pafNCXng | 2025-09-29 | 257 | Build and Deploy a Real-Time Stock Market App with Alerts, Charts & AI Insights |

## Mining the corpus

```bash
C=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/javascript-mastery
ls "$C/transcripts" | wc -l                      # 54 files
grep -n -i -o -E '.{0,200}conditional rendering.{0,200}' "$C/transcripts/8vIDZO_w7lY.txt"
grep -n -i -o -E '.{0,200}legacy.peer.deps.{0,200}' "$C/transcripts/41lfYQhUzRs.txt"
grep -n -i -o -E '.{0,200}window.{0,40}React Native.{0,200}' "$C/transcripts/4nVoLX2taFg.txt"
```
Card (stats, stack shares, build order, marker-scored gotcha windows):
`/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/javascript-mastery.json`

54 of 183 videos transcribed on 2026-09-28; scrape resuming.

## Typed lessons

`references/lessons.jsonl` holds 12 typed lessons `CH-JSM-01..12` in the App Studio ledger format
(lesson_id, trigger, match, mandated_check, evidence, status). Each evidence entry is
`youtube:<video_id>@pos<0.xx>` plus a <=25-word quote grep-verified against that transcript.
`references/stage-map.json` maps each lesson to an App Studio stage.

## How App Studio uses it

| stage | what JSM feeds |
|---|---|
| web-frontend | conditional rendering that must not blank a screen (CH-JSM-06), hook return contracts (CH-JSM-07), in-page error packaging (CH-JSM-08) |
| backend-data | env-var timing (CH-JSM-03), validation-then-destructure order (CH-JSM-04) |
| mobile | web globals banned in React Native (CH-JSM-01) |
| verify-qa | signup user-enumeration (CH-JSM-10) |
| ship-release | SPA catch-all rewrite (CH-JSM-05) |
| ai-features | prompting an agent with symptoms it can actually see (CH-JSM-09) |
| scaffold-setup | dependency mismatch handling (CH-JSM-02), invisible characters in pasted code (CH-JSM-11) |
| operate-learn | error monitoring before release (CH-JSM-12) |

Bench candidates from this channel: `references/bench-candidates.json` (BENCH-JSM-01 trending movies,
BENCH-JSM-02 admin dashboard), each scoped to one ~50-minute builder run.
