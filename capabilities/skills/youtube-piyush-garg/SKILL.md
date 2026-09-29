---
name: youtube-piyush-garg
description: "Piyush Garg (@piyushgargdev): 549-video corpus, PARTIAL coverage (4 transcribed, 36K words) of AI-agent, MCP and Docker builds plus tooling tutorials. Load before mining its transcripts for App Studio AI-features lessons or quoting it as evidence."
tags: [rig, app-studio, youtube-corpus, ai-agents, mcp, docker, nextjs, partial-corpus]
metadata:
  parent: app-studio
  tier: corpus-surface
  handle: "@piyushgargdev"
  corpus_root: /Users/rig128gb/Developer/rig-capabilities/.context/app-creators/piyush-garg
outcome: "Typed, evidence-backed build rules from the Piyush Garg corpus, each bound to a transcript position and a verbatim quote, staged as candidates while the scrape resumes."
activation: "Load for AI-agent integrations, MCP wiring, model gateways, or debugging a silent AI endpoint, or before quoting Piyush Garg as evidence."
instruction: "Mine the local corpus for concrete build rules; route every typed judgment (which lesson applies to a build) to JEV via rig-s1gate BEFORE any frontier model call, and fail closed when the classifier is down or a claim is not grep-verified in the corpus. Lessons are APPEND-only: add new ones as transcripts arrive."
applies_when:
  env: "local corpus at metadata.corpus_root; no network access needed"
  runtime: "bash + python3 over .context/app-creators/piyush-garg and its card"
  deps: "card .context/app-creators/_cards/piyush-garg.json; references/lessons.jsonl"
  params: "quotes are <= 25 words verbatim from the transcript named in the evidence id"
  budget: "one grep pass per lesson candidate"
  scale: "one channel; PARTIAL coverage, App Studio ai-features and verify-qa stages"
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
  - "grep:capabilities/skills/youtube-piyush-garg/SKILL.md:## Top videos"
  - "file:capabilities/skills/youtube-piyush-garg/references/lessons.jsonl"
  - "grep:capabilities/skills/youtube-piyush-garg/SKILL.md:Start here when:"
out_of_scope:
  - publishing or redistributing this corpus (transcripts are copyrighted and stay local)
  - treating a corpus-derived lesson as a passed gate without a run receipt
  - pasting transcript passages longer than 25 words into any output
  - claiming channel-wide statistics from 4 of 549 videos
---

Start here when: an AI feature is wired to a model gateway or an MCP server and returns nothing, and you need the check that names the real cause.

JEV FIRST, binding on every mining and lesson-application step on this channel: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; this surface's typed judgments go to `rig-s1gate check doctrine.surface` and `app.stage-gate`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that a lesson does not advance, and an advisory PASS is not permission to send, push, deploy or publish.

## Load surface

Always loaded at the start of any task that mines this corpus or applies its lessons: `app-studio` routes the matching stage here, and this surface is opened before the first mining command or lesson check. It is a task-start surface, not a deep reference an agent must already know about.

## What this surface is

### Piyush Garg - digest (PARTIAL: 4 of 549 transcribed)

- **What the channel builds**: short, dense AI/agent and tooling builds. 2 of 4 transcribed videos are build videos (build_share 0.5), 2024-2026, 36,017 words total (the smallest Y-B corpus): text-to-image with Flux, an agentic memory system design, an MCP/OpenAI Agent SDK build, and a Git/GitHub tutorial.
- **Episode shape**: 18-40 minute single-concept builds ("Build Text To Image AI using Flux Model", "MCP - Model Context Protocol | OpenAI Agent SDK with Typescript") and one 111-minute tooling course. All are caption-transcribed; `RDxQEzXN8AU` (Git/GitHub) carries machine-translated captions (mixed-language, stutter artifacts) and is deliberately used for no lesson here.
- **Stack it favours (card, videos / share of the 4 transcribed / years)**: openai 3 / 0.75, gemini 3 / 0.75, anthropic 3 / 0.75, docker 3 / 0.75, nextjs 2 / 0.5, typescript 1 / 0.25, postgres 1 / 0.25, stripe 1 / 0.25, ai-sdk 1 / 0.25, langchain 1 / 0.25, inngest 1 / 0.25, railway 1 / 0.25.
- **Typical build order (card, median position, seen_in; n=1 build so treat as a single sample)**: ai 0.02 -> data 0.03 -> api 0.09 -> auth 0.10 -> setup 0.20 -> media 0.21 -> payments 0.22 -> testing 0.26 -> ui 0.84. Unusual: the AI/model layer is decided first and the UI is the last fifth of the video.
- **Mine it for**: the debugging order for silent AI endpoints (network payload first, API keys second, code third), MCP transport choice (hosted remote-tool invocation vs streamable HTTP), and how an agent's own scoped key is proven present before a run.
- **What NOT to copy**: building the UI last with no intermediate verification; treating "it runs on localhost:3000" as proof a feature works; relying on a model gateway whose key presence is never checked in its own dashboard.

## Top videos (transcribed set, 4 of 549; the corpus is thin and the table is short by design)

| video id | published | minutes | title | url |
|---|---|---|---|---|
| `2zdWI2SYB9I` | 2026-07-29 | 27 | AI Agentic Memory System Design | https://www.youtube.com/watch?v=2zdWI2SYB9I |
| `3qjb6RL3nJo` | 2025-11-29 | 18 | MCP - Model Context Protocol | OpenAI Agent SDK with Typescript | https://www.youtube.com/watch?v=3qjb6RL3nJo |
| `pb_jYgSqGh0` | 2025-09-29 | 22 | Build Text To Image AI using Flux Model | https://www.youtube.com/watch?v=pb_jYgSqGh0 |
| `RDxQEzXN8AU` | 2024-09-29 | 111 | Complete Git and GitHub Tutorial for Beginners | https://www.youtube.com/watch?v=RDxQEzXN8AU |

## Mining the local corpus

```bash
CORPUS=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/piyush-garg
CARD=/Users/rig128gb/Developer/rig-capabilities/.context/app-creators/_cards/piyush-garg.json
ls "$CORPUS/transcripts" | wc -l                      # 4 today, grows as the scrape resumes
grep -n -i -o -E '.{0,200}network tab.{0,200}' "$CORPUS/transcripts/pb_jYgSqGh0.txt"
grep -n -i -o -E '.{0,200}streamable.{0,200}' "$CORPUS/transcripts/3qjb6RL3nJo.txt"
# regenerate the card after new transcripts land, then re-mine and APPEND lessons:
python3 capabilities/skills/app-studio/scripts/mine_creator_corpus.py .context/app-creators/piyush-garg
```

Evidence id format in `references/lessons.jsonl`: `youtube:<video_id>@pos<0.xx>` (fractional character offset into the transcript) plus `quote: <=25 words verbatim`.

## How App Studio uses it

`references/stage-map.json` routes its lessons to **verify-qa** (PYG-01 network-tab-first for empty AI responses, PYG-02 drive one real request) and **ai-features** (PYG-03 record the MCP transport, PYG-04 scoped key proven before an agent run). These are the Y-B corpus's only MCP transport lessons, so the ai-features stage leans on this thin file more than its size suggests; that is a reason to re-mine it as the scrape resumes, not to over-trust it.

Typed judgment routing: "does PYG-01 apply to this blank response?" is a JEV judgment. Run `./bin/rig-s1gate check <rubric> --file <artifact> --subject "doctrine:youtube-piyush-garg" --json` and DEFER if it errors.

## Coverage

4 of 549 videos transcribed on 2026-09-28; scrape resuming. Coverage is PARTIAL (0.007) and YouTube throttled the scrape, so every number above describes the 4 transcribed videos only. The card and this skill are regenerated from `.context/app-creators/piyush-garg` as transcripts arrive; lessons are appended, never rewritten.
