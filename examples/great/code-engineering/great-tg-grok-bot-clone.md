---
name: great-tg-grok-bot-clone
lane: code-engineering
exemplar_of: tg-app-studio-session.yaml
description: >-
  A complete Grok Bot agent-platform clone built from corpus video oqUyyB7ROHA:
  agents with custom instructions, objectives, skills, Composio tools, recurring
  routines on Inngest, execution history, and an E2B cloud VM desktop per agent -
  the reference run for "build me an AI agent SaaS like his".
---

# Grok Bot clone - what done looks like

## Source of truth (the corpus match)

- Video: `oqUyyB7ROHA` - "Build Full Stack AI agentic Grok Bot Clone using NextJs, React, Tailwindcss" (5h52m)
- Transcript: `data/corpora/how-to/build-craft/tubeguruji/oqUyyB7ROHA.txt`
- Finished-app screenshot (what done looks like): `data/corpora/how-to/build-craft/tubeguruji-images/oqUyyB7ROHA.jpg`
- Registry row: `data/corpora/how-to/build-craft/tubeguruji-registry.jsonl`

## The spec the transcript yields (each row cited)

| Feature | Evidence |
|---|---|
| Agent SaaS: creation, custom instruction, objective, skills, tools, recurring schedule, chat, execution history, task results, browser automation | oqUyyB7ROHA @00:40-00:55 |
| Dashboard to create/manage multiple agents; connect Gmail/Slack/GitHub/Notion | @00:53-01:08 |
| Cloud VM desktop per agent; opens a real browser; pause/reconnect; auto-inactive after 2 min | @10:09-11:06 |
| VM driven by the agent on request ("use VM desktop"), returns a summary | @11:06-12:07 |
| Scaffold via interactive CLI; shadcn/ui; Postgres (Neon) + Drizzle; Clerk; Inngest; npm | @18:07-20:44 |
| OpenAI model layer under `lib/openai` with a Zod `agent-response-schema.ts` | @03:29:13-03:30:07 |
| Composio: thousands of tools, tool list, sessions ("npm composio core") | @03:05:56-03:13:49 |
| Recurring routines: schema -> saved instruction -> scheduler runs it with timezone | @03:28:40-03:34:55 |
| Cron-style scheduled executions fired from the routine engine | @04:36:12-04:52:48 |
| E2B desktop sandbox phase: create sandbox -> hand agent the desktop -> report back | @05:07:06-05:13:36 |

## Done means (the checks)

1. `npm run build` exit 0 on the finished tree.
2. Dashboard renders with agent cards; create-agent form carries instruction,
   objective, skills, tools, schedule fields.
3. Chat with an agent returns a structured result (Zod-parsed), stored in
   execution history.
4. Tools tab lists Composio tools (env-gated: static fallback list when the key
   is absent, named in the UI).
5. Schedule tab creates a routine with cron + timezone; it fires in the
   scheduler dashboard (local dev UI acceptable for dev).
6. VM desktop panel opens the E2B sandbox (env-gated: mock viewer fallback),
   pause/reconnect controls present, 2-minute idle behavior configured.
7. Video-vs-build comparison table shows every spec row PASS or an honest
   RED/BLOCKED with the reason.

## Lessons the corpus attaches to this build

Tools change; the developer keeps building (creator's own frame @01:33-01:43).
Payments and email were explicitly skipped in-video - a faithful clone may ship
them as named stubs rather than invented features.
