---
name: agentic-setup-mastra
description: "Agentic-systems-setup skill for Mastra on Mike's Mac: agents, workflows, tools, memory, and the dev playground, wired to local-first models via the AI SDK's OpenAI-compatible provider with a deterministic fake model for tests. Use when an agent must stand up Mastra end to end without paid keys, or when a Mastra run is claimed without a receipt."
tags: [rig, agentic-systems-setup, mastra, agents, workflows, typescript]
metadata:
  family: agentic-systems-setup
  tier: framework
  model: "mimo-plan/mimo-v2.6-pro (fallback xai-oauth/grok-4.7, then anthropic/claude-opus-5-5; never Flash)"
outcome: "A Mastra project whose agent generates through a deterministic fake model under vitest with receipts, whose local-first model route is documented, and whose cloud steps (Mastra Cloud signup/deploy) are named and untouched."
activation: "Load for any Mastra install, agent/workflow/tool/memory authoring, dev playground run, or Mastra claim on Mike's Mac that lacks a receipt."
instruction: "Prove installs and runs with receipts, keep model calls on local OpenAI-compatible endpoints, run the agent on a deterministic fake model in tests, and gate cloud steps with Gate-D."
applies_when:
  env: "Aside sandbox for install and unit tests; host shell when a native addon blocks storage"
  runtime: "Node 22 (verified v22.22.3), TypeScript, tsx or vitest"
  deps: "@mastra/core (verified 1.71.0), ai (verified 7.0.118) for MockLanguageModelV4"
  params: "lab dir ~/.rig/agentic-lab/mastra; playground port recorded in proof receipts when run"
  budget: "one hello-world agent plus one test run per session"
  scale: "single project; not a Mastra Cloud estate"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Verify the environment (PATH prefix, node version) and probe local model endpoints before wiring any model.
  - Install pinned versions into the lab dir with an isolated npm cache and capture exit codes.
  - Register one agent on a Mastra instance with a deterministic mock model and run generate under vitest.
  - Attempt the dev playground once; capture any native-addon error verbatim and route that step to a host shell.
  - Write proof receipts and gate the skill with rig-s1gate and the skill contract.
done_when:
  - "grep:capabilities/skills/agentic-setup-mastra/SKILL.md:fake-model"
  - "grep:capabilities/skills/agentic-setup-mastra/SKILL.md:Gate-D"
  - "grep:capabilities/skills/agentic-setup-mastra/references/proof.json:exit_code"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-mastra/SKILL.md"
out_of_scope:
  - "Mastra Cloud signup or deploy (Gate-D, never in this skill's runs)"
  - "paid API keys of any kind"
  - "hand-authoring content where an assigned generator owns it (RIG content doctrine)"
---

# agentic-setup-mastra

Start here when: a project needs Mastra agents, workflows, tools, memory, or the dev playground on Mike's Mac.

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a
local guess. Required signals pass only above 0.9. This skill's verdicts go to
`./bin/rig-s1gate check doctrine.surface --file <skill> --subject "doctrine:<id> sha=$(shasum -a 256 <skill> | cut -c1-12)" --json`.

## Load surface

Always loaded at the START of every Mastra setup task on Mike's Mac: the
`agentic-systems-setup` family routes here before the first setup action, and every
typed judgment in this skill goes to JEV via `rig-s1gate` before any frontier LLM
call. It is a task-start surface, not a deep reference an agent must already know
about. A required signal passes only above 0.9; below that the step does not advance,
and an uncalibrated ESCALATE is a held transition.

## 1. When to choose it, and when not

Choose Mastra when the deliverable is a **TypeScript agent framework**: agents with tools, memory,
structured output, guardrails, multi-agent supervision, plus workflows and a local dev playground
(Studio) for testing agents in a UI.

Do **not** choose it when:

- The ask is a durable background-job substrate (queues, retries, schedules) rather than agents —
  that is Trigger.dev or Inngest; RIG's own `tg-durable-ai-pipelines` and `tool-mastra` skills
  already cover Mastra alongside durable pipelines — read those before duplicating work here.
- The ask is a Python agent stack (that is Pydantic AI, CrewAI, LangChain Python) or a low-code
  builder (that is n8n, Dify, Flowise).

**Two nearest alternatives:** `langchain` (JS/Python agent + chain ecosystem, huge integrations) and
`crewai` (Python multi-agent crews). For durable execution of agent runs, pair with `trigger-dev` or
`inngest` instead of forcing Mastra to be the queue.

## 2. Current version and sources (fetched 2026-09-28)

- `@mastra/core` **1.71.0** — verified: `npm view @mastra/core version` printed `1.71.0`; installed
  `node_modules/@mastra/core/package.json` read `"version": "1.71.0"`.
- `ai` (Vercel AI SDK) **7.0.118** — verified from `node_modules/ai/package.json`; its `ai/test`
  entry exports `MockLanguageModelV4` (read from the installed `dist/test/index.d.ts`).
- Official docs fetched today: https://mastra.ai/docs/agents/overview (Agent class, `model` as
  `'provider/model-name'` via the model router or an AI SDK model instance, `Mastra` instance
  registration, `getAgentById`, `.generate()`/`.stream()`, Studio, tools, memory, human-in-the-loop,
  guardrails, supervisor/multi-agent patterns).

## 3. Environment route and prerequisites

- **Aside sandbox:** install and vitest run here. Use the PATH prefix:
  `export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"` (node v22.22.3, npm 10.9.8).
- **Native-addon hazard (observed as a standing sandbox fact):** Mastra's default storage
  (libsql) and anything similar are `.node` addons and are **blocked in the Aside sandbox**. If
  `mastra dev` or memory/storage initialization fails on a native binding, capture the exact error
  text and run that step from a host shell (Orca terminal); pure model calls and workflows without
  storage stay in the sandbox.
- **npm cache hazard (observed here, 2026-09-28):** sibling workers collide in the shared npm cache;
  use `npm_config_cache="$HOME/.rig/agentic-lab/.npm-cache-a4"` and serialize installs.

## 4. Install (exact commands)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/mastra && cd ~/.rig/agentic-lab/mastra
npm init -y
npm_config_cache="$HOME/.rig/agentic-lab/.npm-cache-a4" \
  npm i @mastra/core@1.71.0 ai@7.0.118 typescript tsx vitest
```

(For the full project scaffold, `npm create mastra@latest` exists per docs; hand-rolling the minimal
instance as above is faster and dependency-lighter for lab proof.)

## 5. Local-first model wiring

Model calls go to **Mike's local OpenAI-compatible endpoints only** — never a paid key. Probe first:

```bash
curl -s -m 5 http://192.168.68.90:8011/v1/models
curl -s -m 5 http://192.168.68.90:8111/v1/models
```

Probe results 2026-09-28, from this sandbox: the Blackwell endpoints do NOT answer here —
`192.168.68.90:8011` curl exit 7 (connection refused), `192.168.68.90:8111` curl exit 28 (timeout).
Two local endpoints DO answer: `http://127.0.0.1:8771/v1` (model `qwen3.8-uncensored:27b`; with
thinking enabled it returns HTTP 200 with EMPTY content, so send
`chat_template_kwargs: {"enable_thinking": false}` and assert non-empty content) and
`http://127.0.0.1:8657/v1` (model `MiMo-V2.6-Flash-RL-MLX-4bit-MTP` — a Flash model; the model pin
forbids Flash as a driver, so do not use it). Use 8771 for L3 model steps.

## 6. Secrets

- Keychain item names only, never values: `com.rig.env.LOCAL_LLM_API_KEY` if a local endpoint ever
  needs a bearer token (local endpoints are usually keyless — verify before adding one).
- `.env.example` placeholders only. Mastra reads env from the project's environment; no credential
  store is created here. Never print, paste, or store raw keys.

## 7. Hello-world (run here)

`src/mastra/index.ts` — one agent on a Mastra instance, deterministic mock model:

```typescript
import { Mastra } from "@mastra/core";
import { Agent } from "@mastra/core/agent";
import { MockLanguageModelV4 } from "ai/test";

export const fakeModel = new MockLanguageModelV4({
  doGenerate: async () => ({
    content: [{ type: "text", text: "fake-model:HELLO FROM MASTRA" }],
    finishReason: "stop" as const,
    usage: { inputTokens: 1, outputTokens: 4, totalTokens: 5 },
    warnings: [],
  }),
});

export const helloAgent = new Agent({
  id: "hello-agent",
  name: "Hello Agent",
  instructions: "Reply with the fixed greeting and nothing else.",
  model: fakeModel,
});

export const mastra = new Mastra({ agents: { helloAgent } });
```

Test: `mastra.getAgentById("hello-agent")` resolves and `agent.generate("say hello")` returns text
containing `fake-model:HELLO FROM MASTRA`. Command: `npx vitest run --reporter=basic`. Receipts in
`references/proof.json`.

## 8. Durable and production features (docs-sourced, L0)

Docs (fetch date above) cover: workflows with explicit steps and branching, tools and agents-as-tools,
memory across conversations, structured output, human-in-the-loop approval, guardrails, processors,
subagents/supervisors, voice, channels (Slack/Discord/Telegram), and client/server adapters. None of
the durable-execution semantics (retries, idempotency, schedules) are Mastra's core job — use
Trigger.dev/Inngest for those. Only `generate` on a mock model ran here.

## 9. Observability

Mastra offers logging/observability hooks at the instance level and Studio for inspecting tool calls
and responses (docs). Nothing observed here beyond vitest output and structured console logs; do not
claim an OTel exporter without a run proving it.

## 10. Testing (deterministic fake model + one planted failure)

- Deterministic mock: `MockLanguageModelV4` from `ai/test` (no network, no key).
- Unit tests (vitest): assert the agent resolves from the instance and that `generate` returns the
  exact mock text — expected values, not "did not throw".
- **Planted failure, run here:** flip one expected string, re-run, require RED; checksum the test
  file before/after the plant (`shasum -a 256`) so an unlanded plant cannot fake a pass; restore,
  re-run, require GREEN.

## 11. Deploy / self-host, and what is Gate-D

**Gate-D (Mike's explicit approval required; never done here):** Mastra Cloud signup or deploy, any
paid model provider key, public URL/tunnel exposure. Local use is the default: agents run in-process
and the dev playground binds locally. Anything requiring Docker is blocked in this sandbox (Colima
down, Docker owned by another worker) and would run from a host shell under Gate-D.

## 12. Teardown and upgrade

```bash
lsof -t -i :PORT | xargs kill        # stop a playground if you started one
rm -rf ~/.rig/agentic-lab/mastra ~/.rig/agentic-lab/.npm-cache-a4
```

Upgrade: `npm view @mastra/core version`, bump the pin, re-run tests and gates.

## 13. Gotchas (each tagged with where observed)

1. **Shared npm cache races** — concurrent `npm i` runs crashed with `npm error` and wiped
   node_modules (observed here, 2026-09-28; fixed with isolated cache + serialization).
2. **AI SDK major drift** — `ai` 7.x test mocks are `MockLanguageModelV3/V4` under `ai/test`; older
   snippets reference `MockLanguageModel` from `ai/test` on v4 SDKs (observed here: the installed
   `ai@7.0.118` `dist/test/index.d.ts` exports).
3. **No storage configured prints a loud warning and is not durable** — `agent.generate` ran with
   `No 'storage' configured on Mastra — falling back to an in-memory store...` (observed here,
   2026-09-28, exact warning captured in proof.json); persistent adapters (`@mastra/libsql`,
   `@mastra/pg`) are native/postinstall-bound and belong on a host shell.
4. **Docs assume hosted models** — the docs quickstart shows `model: 'openai/gpt-5.6-sol'` via the
   model router, which is a paid route; local-first means an AI SDK model instance instead (observed
   here on https://mastra.ai/docs/agents/overview, 2026-09-28).

## 14. Proof receipts (2026-09-28)

| Command | Exit | Version | Observed | Proof level |
|---|---|---|---|---|
| `npm view @mastra/core version` | 0 | 1.71.0 | `1.71.0` | L0 |
| `npm i --ignore-scripts @mastra/core@1.71.0 ai@7.0.118` | 0 | 1.71.0 | 138 pkgs to lab dir | L1 |
| `node --experimental-strip-types test/run.ts` | 0 | node 22.22.3 | `agent.generate` on MockLanguageModelV4 PASS (in-memory storage warning captured) | L2 |
| planted re-run of `test/run.ts` | 1 | node 22.22.3 | AssertionError RED; plant checksummed 8a709f54f9e6 -> 8b6474de7e2f | L2 |
| restored re-run of `test/run.ts` | 0 | node 22.22.3 | PASS again; checksum back to 8a709f54f9e6 | L2 |
| `node test/l3.mjs` (tool step calls 127.0.0.1:8771) | 0 | qwen3.8-uncensored:27b | `"Hello there Mike"` non-empty | L3 |
| planted / restored re-runs of `test/l3.mjs` | 1 / 0 | - | ASSERTION FAILED / PASS again | L3 |
| `mastra dev` playground | NOT RUN | 1.71.0 | the `mastra` CLI package was not installed in this lab run (playground needs it); storage adapters like `@mastra/libsql` are native addons blocked in this sandbox — run on a host shell | not claimed |
| docs fetch `mastra.ai/docs/agents/overview` | 0 | n/a | agent/workflow/memory surface confirmed | L0 |

L3 IS claimed (local endpoint `127.0.0.1:8771`, thinking disabled, non-empty content asserted).
L4 is NOT claimed (playground not run). L5 is Gate-D and was not done. Full receipts:
`references/proof.json`.
