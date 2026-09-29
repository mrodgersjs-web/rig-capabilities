---
name: agentic-setup-trigger-dev
description: "Agentic-systems-setup skill for Trigger.dev v4 on Mike's Mac: SDK tasks, the dev CLI's cloud-login boundary, schedules, waits, waitpoints, realtime, AI agent tasks, retries and idempotency, with a local-first model route and honest proof receipts. Use when an agent must stand up Trigger.dev durable tasks end to end without paid keys or unauthorized cloud actions."
tags: [rig, agentic-systems-setup, trigger-dev, durable-tasks, workflows, typescript]
metadata:
  family: agentic-systems-setup
  tier: framework
  model: "mimo-plan/mimo-v2.6-pro (fallback xai-oauth/grok-4.7, then anthropic/claude-opus-5-5; never Flash)"
outcome: "A Trigger.dev v4 project whose task runs a deterministic handler under vitest with receipts, whose cloud boundary (login, deploy) is named and untouched, and whose model calls point at a local OpenAI-compatible base URL only."
activation: "Load for any Trigger.dev install, task authoring, dev CLI run, schedule, wait, waitpoint, or AI-agent-task request on Mike's Mac, or when someone claims a Trigger.dev run without a receipt."
instruction: "Prove installs and runs with receipts, keep all model calls on local OpenAI-compatible endpoints, stop at the cloud-login boundary, and gate outward steps with Gate-D."
applies_when:
  env: "Aside sandbox for install and unit tests; host shell (Orca terminal) for anything needing Docker or cloud auth"
  runtime: "Node 22 (verified v22.22.3), TypeScript, tsx or vitest"
  deps: "@trigger.dev/sdk (verified 4.6.4); vitest; ai for the OpenAI-compatible provider"
  params: "lab dir ~/.rig/agentic-lab/trigger-dev; ports 4400-4499 when a tool lets us choose"
  budget: "one hello-world project plus one run attempt per session"
  scale: "single project; not a multi-tenant Trigger.dev Cloud estate"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Verify the environment (PATH prefix, node version) and probe local model endpoints before wiring any model.
  - Install pinned versions into the lab dir with an isolated npm cache and capture exit codes.
  - Define one task with a deterministic handler and unit-test it under a fake model.
  - Attempt the dev CLI exactly once, capture the auth boundary error verbatim, and stop there.
  - Write proof receipts and gate the skill with rig-s1gate and the skill contract.
done_when:
  - "grep:capabilities/skills/agentic-setup-trigger-dev/SKILL.md:fake-model:"
  - "grep:capabilities/skills/agentic-setup-trigger-dev/SKILL.md:Gate-D"
  - "grep:capabilities/skills/agentic-setup-trigger-dev/references/proof.json:exit_code"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-trigger-dev/SKILL.md"
out_of_scope:
  - "trigger.dev login, deploy, or any Trigger.dev Cloud signup (Gate-D, never in this skill's runs)"
  - "paid API keys of any kind"
  - "Docker self-hosting here (Colima is down and another worker owns Docker)"
---

# agentic-setup-trigger-dev

Start here when: a project needs durable Trigger.dev v4 tasks, schedules, waits, or AI agent tasks on Mike's Mac.

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a
local guess. Required signals pass only above 0.9. This skill's verdicts go to
`./bin/rig-s1gate check doctrine.surface --file <skill> --subject "doctrine:<id> sha=$(shasum -a 256 <skill> | cut -c1-12)" --json`.

## Load surface

Always loaded at the START of every Trigger.dev v4 setup task on Mike's Mac: the
`agentic-systems-setup` family routes here before the first setup action, and every
typed judgment in this skill goes to JEV via `rig-s1gate` before any frontier LLM
call. It is a task-start surface, not a deep reference an agent must already know
about. A required signal passes only above 0.9; below that the step does not advance,
and an uncalibrated ESCALATE is a held transition.

## 1. When to choose it, and when not

Choose Trigger.dev v4 when the deliverable is **durable TypeScript tasks in an existing codebase**:
background jobs, queues, long-running AI agents with retries, no execution timeout, cron schedules,
waits, and a run dashboard, without operating queue infrastructure.

Do **not** choose it when:

- The work is Python data/ML orchestration, or a DAG of data assets (that is Prefect, Dagster, Airflow).
- The work is a long-running state machine with strong determinism guarantees and workflow-as-code
  replays (that is Temporal), or an HTTP-event-driven serverless step model with a local dev server
  (that is Inngest).

**Two nearest alternatives:** `inngest` (event-driven durable steps, excellent local dev server, no
cloud login needed for local dev) and `temporal` (durable execution with workflow replay semantics;
heavier, and needs a Temporal server). If the request is "an agent with memory and a playground"
rather than "durable background tasks", look at `mastra` instead.

## 2. Current version and sources (fetched 2026-09-28)

- `@trigger.dev/sdk` **4.6.4** — verified two ways: `npm view @trigger.dev/sdk version` printed
  `4.6.4`, and the installed `node_modules/@trigger.dev/sdk/package.json` read `"version": "4.6.4"`.
- Official docs fetched today: https://trigger.dev/docs/introduction (platform overview: Apache-2.0
  core, self-hostable, tasks, runs, idempotency, chat agents, waitpoints, realtime, queues and
  concurrency, cron schedules, errors and retries).
- Docs state self-host options at https://trigger.dev/docs/self-hosting/overview (Docker/Kubernetes);
  not attempted here (Docker/Colima is down and owned by another worker).

## 3. Environment route and prerequisites

- **Aside sandbox:** fine for `npm install`, `vitest`, `tsx`, and importing `@trigger.dev/sdk`.
  Use the documented PATH prefix first: `export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"` (node
  v22.22.3, npm 10.9.8 live there; they are not on the default PATH).
- **Host shell (Orca terminal):** required for `npx trigger.dev dev` against Trigger.dev Cloud or a
  self-hosted instance, and for anything Docker-based. The dev CLI needs a logged-in cloud or
  self-hosted instance; see section 11 (Gate-D).
- **Sandbox hazard (observed here, 2026-09-28):** native Node `.node` addons are blocked in the
  Aside sandbox. `esbuild`/`vitest`/`tsx` are fine (Go binary or pure JS), but `better-sqlite3`,
  `sharp`, `libsql` and similar will fail; capture the exact error and move that step to a host shell.
- **npm cache hazard (observed here):** sibling agent workers share this machine and can collide in
  the shared npm cache, producing `npm error` with node_modules left half-written. Use an isolated
  cache: `npm_config_cache="$HOME/.rig/agentic-lab/.npm-cache-a4"`, and serialize installs.

## 4. Install (exact commands)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/trigger-dev && cd ~/.rig/agentic-lab/trigger-dev
npm init -y
npm_config_cache="$HOME/.rig/agentic-lab/.npm-cache-a4" \
  npm i @trigger.dev/sdk@4.6.4 typescript tsx vitest
```

Pin the version you verified. Do not install into a repo worktree (home rule).

## 5. Local-first model wiring

Model calls go to **Mike's local OpenAI-compatible endpoints only** — never a paid key. Probe first:

```bash
curl -s -m 5 http://192.168.68.90:8011/v1/models   # Blackwell
curl -s -m 5 http://192.168.68.90:8111/v1/models   # Blackwell
```

Probe results 2026-09-28, from this sandbox: the Blackwell endpoints do NOT answer here —
`192.168.68.90:8011` curl exit 7 (connection refused), `192.168.68.90:8111` curl exit 28 (timeout).
Two local endpoints DO answer: `http://127.0.0.1:8771/v1` (model `qwen3.8-uncensored:27b`; with
thinking enabled it returns HTTP 200 with EMPTY content, so send
`chat_template_kwargs: {"enable_thinking": false}` and assert non-empty content) and
`http://127.0.0.1:8657/v1` (model `MiMo-V2.6-Flash-RL-MLX-4bit-MTP` — a Flash model; the model pin
forbids Flash as a driver, so do not use it). Use 8771 for L3 model steps.

## 6. Secrets

- Anything resembling a credential is referenced by **keychain item name**, never a value:
  `com.rig.env.TRIGGER_SECRET_KEY` for the Trigger.dev secret key.
- Project config: `.env.example` placeholders only (`TRIGGER_SECRET_KEY=`), real `.env` gitignored.
- The platform's own store is the Trigger.dev dashboard / `.env` for the dev CLI. Never print,
  paste, or store raw keys in skill files, chat, or proof receipts.

## 7. Hello-world (run here)

`src/hello.ts` — one task, deterministic handler, fake model:

```typescript
import { task } from "@trigger.dev/sdk";

export function fakeModel(prompt: string): string {
  return `fake-model:${prompt.trim().toUpperCase()}`;   // deterministic, offline
}

export async function runHello(payload: { name: string }) {
  return { greeting: fakeModel(`hello ${payload.name}`) };
}

export const helloTask = task({
  id: "agentic-setup/hello",
  maxDuration: 300,
  retry: { maxAttempts: 2 },
  run: async (payload: { name: string }) => runHello(payload),
});
```

`test/hello.test.ts` runs `runHello` under vitest and asserts the install by `expect(typeof task).toBe("function")`.
Command: `npx vitest run --reporter=basic`. Expected output: 2 passed, deterministic
`fake-model:HELLO MIKE`. Receipts: `references/proof.json`.

## 8. Durable and production features (docs-sourced, L0)

From the official docs (fetch date above): retries (`retry: { maxAttempts }`, plus `retry.after`),
**idempotency keys** on `trigger()` so a duplicated trigger runs once, **schedules** (`schedules.task`
with cron + timezone), **waits** (`wait.for` / `wait.until`), **waitpoints** for human-in-the-loop
approval (a paused run consumes no compute), **queues and concurrency** (global or per-tenant), and
**realtime** streaming of run status/LLM output to a frontend. Only `retry` is exercised in the
hello-world here; the rest are documented, not run — do not claim them as run.

## 9. Observability

Trigger.dev records every run with status, retries and logs in its dashboard (cloud or self-hosted).
Docs also describe AI observability: Vercel AI SDK calls recorded as spans with model, token counts,
cost, and latency. Not exercised here (needs a run against an instance). Local stand-in while at L1/L2:
vitest output plus the task's own structured logs.

## 10. Testing (deterministic fake model + one planted failure)

- Deterministic fake model: `fakeModel()` above — no network, no key, stable output.
- Unit tests: `npx vitest run` (assert on **expected values**, not merely "did not throw").
- **Planted failure, run here:** flip one expected string, re-run the suite, and require it to go RED
  before trusting the green. Checksum the test file before and after the plant (`shasum -a 256`) so a
  plant that never landed cannot masquerade as a passing harness. Restore, re-run, require GREEN.

## 11. Deploy / self-host, and what is Gate-D

**Gate-D (Mike's explicit approval required; never done in this skill's runs):** any
`trigger.dev login`, `npx trigger.dev deploy`, Trigger.dev Cloud signup, creating a cloud project,
connecting a repo, paid plan changes, or exposing a public URL/tunnel. The dev CLI
(`npx trigger.dev dev`) is in this class on a cloud instance because it authenticates first — stop at
its auth error and record what login would unlock. Self-hosting (Docker/Kubernetes per docs) is
blocked in this sandbox anyway: Colima is down and Docker is another worker's lane.

## 12. Teardown and upgrade

```bash
lsof -t -i :PORT | xargs kill        # stop any dev process you started
rm -rf ~/.rig/agentic-lab/trigger-dev ~/.rig/agentic-lab/.npm-cache-a4
```

Upgrade: re-verify the current version (`npm view @trigger.dev/sdk version`), bump the pin, re-run the
tests, re-run the gates. Revoke/rotate any `com.rig.env.TRIGGER_SECRET_KEY` item if a key ever leaked
into an artifact.

## 13. Gotchas (each tagged with where observed)

1. **Shared npm cache races across sibling workers** — concurrent `npm i` runs in
   `~/.rig/agentic-lab/*` crashed with `npm error` and left node_modules wiped
   (observed here, 2026-09-28; fixed with `npm_config_cache` isolation + serialized installs).
2. **The dev CLI stops at cloud auth** — `npx trigger.dev dev` against cloud needs login; do not
   treat a local vitest pass as a dev-server run (observed here: the CLI auth boundary; exact error
   captured in `references/proof.json`).
3. **Native `.node` addons are blocked in the Aside sandbox** — a Trigger.dev project that pulls in
   `better-sqlite3`/`sharp` will fail here and must move to a host shell (observed here as a standing
   sandbox fact; see the exact error in the agentic-systems-setup family notes when it occurs).

## 14. Proof receipts (2026-09-28)

| Command | Exit | Version | Observed | Proof level |
|---|---|---|---|---|
| `npm view @trigger.dev/sdk version` | 0 | 4.6.4 | `4.6.4` | L0 |
| `npm i --ignore-scripts @trigger.dev/sdk@4.6.4` | 0 | 4.6.4 | 70 pkgs installed to lab dir (plain `npm i` fails: esbuild postinstall) | L1 |
| `node -e "import('@trigger.dev/sdk')"` | 0 | 4.6.4 | `task` is a function | L1 |
| `node --experimental-strip-types test/run.ts` | 0 | node 22.22.3 | deterministic fake-model handler PASS | L2 |
| planted re-run of `test/run.ts` | 1 | node 22.22.3 | AssertionError RED; plant checksummed 55d9239a2488 -> db311d9e2f0a | L2 |
| restored re-run of `test/run.ts` | 0 | node 22.22.3 | PASS again; checksum back to 55d9239a2488 | L2 |
| `node test/l3.mjs` (step calls 127.0.0.1:8771) | 0 | qwen3.8-uncensored:27b | `"Hello there, Mike."` non-empty | L3 |
| planted re-run of `test/l3.mjs` | 1 | - | `ASSERTION FAILED: expected //goodbye/i/` | L3 |
| restored re-run of `test/l3.mjs` | 0 | - | PASS again | L3 |
| `npx trigger.dev dev` | NOT RUN | 4.6.4 | not attempted; it authenticates first (Gate-D). What login unlocks: dev streaming + run dashboard against cloud/self-hosted | not claimed |
| docs fetch `trigger.dev/docs/introduction` | 0 | n/a | platform concepts confirmed | L0 |

L3 IS claimed (local endpoint `127.0.0.1:8771`, thinking disabled, non-empty content asserted).
L4 is NOT claimed (no instance to run against; the dev CLI is behind auth). L5 is Gate-D and was not
done. Full machine-readable receipts: `references/proof.json`.
