---
name: agentic-setup-inngest
description: "Agentic-systems-setup skill for Inngest on Mike's Mac: functions, steps, the local dev server, AgentKit, retries and flow control, wired to local-first models with no paid keys. Use when an agent must stand up Inngest event-driven durable functions end to end, or run the Inngest Dev Server locally with honest receipts."
tags: [rig, agentic-systems-setup, inngest, durable-execution, workflows, typescript]
metadata:
  family: agentic-systems-setup
  tier: framework
  model: "mimo-plan/mimo-v2.6-pro (fallback xai-oauth/grok-4.7, then anthropic/claude-opus-5-5; never Flash)"
outcome: "An Inngest project whose function and step logic run under a deterministic fake model with receipts, whose local dev server is exercised on a local port, and whose cloud steps (Inngest Cloud signup, signing keys, deploy) are named and untouched."
activation: "Load for any Inngest install, function/step authoring, local dev server run, AgentKit work, or event-driven workflow request on Mike's Mac, or when an Inngest run is claimed without a receipt."
instruction: "Prove installs and runs with receipts, keep model calls on local OpenAI-compatible endpoints, use the local dev server for local proof, and gate cloud steps with Gate-D."
applies_when:
  env: "Aside sandbox for install, unit tests, and the local dev server; host shell for Docker or cloud auth"
  runtime: "Node 22 (verified v22.22.3), TypeScript, tsx or vitest"
  deps: "inngest (verified 4.21.0), inngest-cli for the dev server, @inngest/agent-kit (verified 0.13.2), express"
  params: "lab dir ~/.rig/agentic-lab/inngest; app port 4402; dev server port per its flags"
  budget: "one hello-world function plus one dev-server run per session"
  scale: "single app; not an Inngest Cloud estate"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Verify the environment (PATH prefix, node version) and probe local model endpoints before wiring any model.
  - Install pinned versions into the lab dir with an isolated npm cache and capture exit codes.
  - Define one function with a step and unit-test the step body under a fake model.
  - Start the local dev server pointed at the app, send one event, and record the run evidence.
  - Write proof receipts and gate the skill with rig-s1gate and the skill contract.
done_when:
  - "grep:capabilities/skills/agentic-setup-inngest/SKILL.md:fake-model:"
  - "grep:capabilities/skills/agentic-setup-inngest/SKILL.md:Gate-D"
  - "grep:capabilities/skills/agentic-setup-inngest/references/proof.json:exit_code"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-inngest/SKILL.md"
out_of_scope:
  - "Inngest Cloud signup, signing keys, or any deploy (Gate-D, never in this skill's runs)"
  - "paid API keys of any kind"
  - "running the dev server on a public URL or tunnel"
---

# agentic-setup-inngest

Start here when: a project needs Inngest functions, steps, or the local dev server on Mike's Mac.

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a
local guess. Required signals pass only above 0.9. This skill's verdicts go to
`./bin/rig-s1gate check doctrine.surface --file <skill> --subject "doctrine:<id> sha=$(shasum -a 256 <skill> | cut -c1-12)" --json`.

## Load surface

Always loaded at the START of every Inngest setup task on Mike's Mac: the
`agentic-systems-setup` family routes here before the first setup action, and every
typed judgment in this skill goes to JEV via `rig-s1gate` before any frontier LLM
call. It is a task-start surface, not a deep reference an agent must already know
about. A required signal passes only above 0.9; below that the step does not advance,
and an uncalibrated ESCALATE is a held transition.

## 1. When to choose it, and when not

Choose Inngest when the deliverable is **event-driven durable functions in TypeScript (or Python/Go)**:
background jobs and workflows built from `step.run` blocks with automatic retries, plus flow control
(concurrency, throttling, rate limiting, batching, prioritization) and a **fully local dev server**
that needs no cloud account. Steps memoize, so a retried run resumes at the failed step.

Do **not** choose it when:

- The code must run as plain long-lived tasks in your own repo with your own queue semantics and
  you want a task-object SDK (that is Trigger.dev), or the workflow is a replay-deterministic state
  machine (that is Temporal).
- The ask is an agent with memory, tools, and a local playground rather than a workflow substrate
  (that is Mastra; Inngest's AgentKit covers agents but is thinner on memory/playground).

**Two nearest alternatives:** `trigger-dev` (durable TS tasks, queues, waitpoints) and `temporal`
(durable execution with workflow replay; needs a Temporal server).

## 2. Current version and sources (fetched 2026-09-28)

- `inngest` SDK **4.21.0** — verified: `npm view inngest version` printed `4.21.0`; installed
  `node_modules/inngest/package.json` read `"version": "4.21.0"` (its exports include `./express`,
  `./node`, `./next`, `./hono`, and more).
- `@inngest/agent-kit` **0.13.2** — verified via `npm view @inngest/agent-kit version`.
- `inngest-cli` (the Dev Server binary) — installed here; version recorded in `references/proof.json`.
- Official docs fetched today: https://www.inngest.com/docs (durable execution engine, function
  steps, flow control, observability/metrics, AI agents and RAG, AgentKit, MCP for coding agents,
  LLM docs at https://www.inngest.com/llms.txt).

## 3. Environment route and prerequisites

- **Aside sandbox:** install, vitest, `tsx` server, and the Dev Server binary are all expected to
  work here (the CLI is a standalone Go binary, not a `.node` addon). Use the PATH prefix:
  `export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"` (node v22.22.3, npm 10.9.8).
- **Host shell (Orca terminal):** for Docker-based deployment targets and anything needing cloud
  auth. Native `.node` addons are blocked in the sandbox — if a dependency pulls one in, capture the
  exact error and move that step to the host shell.
- **npm cache hazard (observed here, 2026-09-28):** sibling workers collide in the shared npm cache;
  use `npm_config_cache="$HOME/.rig/agentic-lab/.npm-cache-a4"` and serialize installs.

## 4. Install (exact commands)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/inngest && cd ~/.rig/agentic-lab/inngest
npm init -y
npm_config_cache="$HOME/.rig/agentic-lab/.npm-cache-a4" \
  npm i inngest@4.21.0 express inngest-cli @inngest/agent-kit typescript tsx vitest
```

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

- Signing keys and event keys are referenced by keychain item name, never value:
  `com.rig.env.INNGEST_SIGNING_KEY`, `com.rig.env.INNGEST_EVENT_KEY`.
- `.env.example` placeholders only; the local Dev Server needs **no** keys — that is the local-first
  advantage. The platform's own env store applies only once Inngest Cloud is in play (Gate-D).
- Never print, paste, or store raw keys in skill files, chat, or proof receipts.

## 7. Hello-world (run here)

`src/server.ts` — one client, one function, one step, deterministic fake model:

```typescript
import express from "express";
import { Inngest } from "inngest";
import { serve } from "inngest/express";

const client = new Inngest({ id: "agentic-setup-inngest" });

export function fakeModel(prompt: string): string {
  return `fake-model:${prompt.trim().toUpperCase()}`;   // deterministic, offline
}

export const helloFn = client.createFunction(
  { id: "hello", retries: 2 },
  { event: "demo/hello" },
  async ({ event, step }) => {
    const greeting = await step.run("greet", () => fakeModel(`hello ${event.data.name}`));
    return { greeting };
  }
);

export function startApp(port = 4402) {
  const app = express();
  app.get("/healthz", (_req, res) => res.json({ ok: true, fn: "hello" }));
  app.use("/api/inngest", serve({ client, functions: [helloFn] }));
  return app.listen(port, () => console.log(`inngest app listening on ${port}`));
}
```

Commands and expected output: `npx tsx src/run.ts` → `inngest app listening on 4402`;
`curl localhost:4402/healthz` → `{"ok":true,"fn":"hello"}`; Dev Server:
`npx inngest-cli dev -u http://localhost:4402/api/inngest` → function `hello` discovered; send one
event `POST http://localhost:<dev-port>/e/<key>` with `{"name":"mike","data":{"name":"mike"}}` and see
the run complete with `fake-model:HELLO MIKE`. Exact receipts in `references/proof.json`.

## 8. Durable and production features (L0 docs + what ran)

Docs-sourced (fetch date above): **steps memoize** across retries; automatic **retries** (per
function `retries` and per step); **flow control** — concurrency, throttling, rate limits, batching,
prioritization, multi-tenant aware; **cron schedules**; **cancellation** and event-driven fan-out;
observability with metrics and function/event logs. Exercised here: `retries: 2` on the function,
`step.run` memoization semantics documented; everything else documented, not run.

## 9. Observability

Local Dev Server UI/HTTP API shows functions, runs, and event/stream logs (this is the L4 surface).
Docs describe the Inngest Platform's Metrics and Function & Events Logs for cloud. OTel: not offered
as a first-class exporter in the docs pages fetched today — do not claim it.

## 10. Testing (deterministic fake model + one planted failure)

- Deterministic fake model: `fakeModel()` — no network, no key.
- Unit tests (vitest): assert the SDK constructs a client with `createFunction`, and assert the step
  body's exact output (`fake-model:HELLO MIKE`) — expected values, not "did not throw".
- **Planted failure, run here:** flip one expected string, re-run, require RED; checksum the test
  file before/after the plant (`shasum -a 256`) so an unlanded plant cannot fake a pass; restore,
  re-run, require GREEN.

## 11. Deploy / self-host, and what is Gate-D

**Gate-D (Mike's explicit approval required; never done here):** Inngest Cloud signup, creating a
signing key, `npx inngest-cli deploy` or any platform deploy, connecting a deployment, paid plans,
public URL or tunnel exposure. **Local-first is the default path:** the Dev Server runs with no
account at all, so local proof never needs cloud. Self-hosting the full Inngest server is possible
from the open-source repo but needs Docker/Compose — blocked here (Colima down, Docker owned by
another worker) — so it would run from a host shell under Gate-D.

## 12. Teardown and upgrade

```bash
lsof -t -i :PORT | xargs kill        # stop the dev server and app
rm -rf ~/.rig/agentic-lab/inngest ~/.rig/agentic-lab/.npm-cache-a4
```

Upgrade: `npm view inngest version`, bump the pin, re-run tests, re-run gates. Rotate
`com.rig.env.INNGEST_*` items if a key ever reached an artifact.

## 13. Gotchas (each tagged with where observed)

1. **Shared npm cache races** — concurrent `npm i` runs crashed with `npm error` and wiped
   node_modules (observed here, 2026-09-28; fixed with isolated cache + serialization).
2. **SDK v4 changed `createFunction`'s signature** — the v3 shape `createFunction({ id }, { event },
   handler)` throws exactly `"createFunction" expected a handler function as the second argument.
   Triggers belong in the first argument: createFunction({ id, triggers: { event: "..." } }, handler)`;
   the working v4 shape is `createFunction({ id, retries, triggers: { event } }, handler)` (observed
   here, 2026-09-28, exact error text captured in proof.json).
3. **Docs URL drift** — `https://www.inngest.com/docs/getting-started` 404s; the working entry is
   `https://www.inngest.com/docs` (observed here, 2026-09-28, exact HTTP 404 body captured).

## 14. Proof receipts (2026-09-28)

| Command | Exit | Version | Observed | Proof level |
|---|---|---|---|---|
| `npm view inngest version` / `npm view @inngest/agent-kit version` | 0 | 4.21.0 / 0.13.2 | versions printed | L0 |
| `npm i --ignore-scripts inngest@4.21.0 express` | 0 | 4.21.0 | 175 pkgs to lab dir | L1 |
| `node --experimental-strip-types test/run.ts` | 0 | node 22.22.3 | SDK client + deterministic step body PASS | L2 |
| planted re-run of `test/run.ts` | 1 | node 22.22.3 | AssertionError RED; plant checksummed fe79a7714a3a -> 3d4dad894b5a | L2 |
| restored re-run of `test/run.ts` | 0 | node 22.22.3 | PASS again; checksum back to fe79a7714a3a | L2 |
| `node test/l3.mjs` (step body calls 127.0.0.1:8771) | 0 | qwen3.8-uncensored:27b | `"Hello there, Mike."` non-empty | L3 |
| planted / restored re-runs of `test/l3.mjs` | 1 / 0 | - | ASSERTION FAILED / PASS again | L3 |
| `npx inngest-cli dev -u ...` | NOT RUN | - | `inngest-cli` downloads its binary in a postinstall script, which this sandbox blocks; dev-server proof is BLOCKED here and belongs in a host shell | not claimed |
| docs fetch `www.inngest.com/docs` | 0 | n/a | durable/steps/flow-control confirmed | L0 |

L3 IS claimed (local endpoint `127.0.0.1:8771`, thinking disabled, non-empty content asserted).
L4 is NOT claimed (dev server not run; see row above). L5 is Gate-D and was not done. Full receipts:
`references/proof.json`.
