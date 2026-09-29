---
name: agentic-systems-setup
description: "META skill for setting up agentic systems at RIG: picks the framework for the job (LangChain/LangGraph, LlamaIndex, Pydantic AI, CrewAI, OpenAI Agents SDK, Google ADK, Microsoft Agent Framework, Prefect, Temporal, Dagster, Airflow, Trigger.dev, Inngest, Mastra, n8n, Dify, Kestra, Flowise, Langflow), then runs one universal setup protocol with an L0-L5 proof ladder, local-first models, keychain-named secrets, and Gate-D on anything outward. JEV-FIRST MANDATE."
tags: [rig, meta-skill, agentic-systems, frameworks, setup, orchestration, workflows]
metadata:
  tier: meta
  purpose: meta-skill
  category: agent-engineering
  family: agentic-systems-setup
  built: "2026-09-28"
outcome: "A named agentic framework installed in the right route with a proof receipt that validates: docs fetched today, installed, hello run on a fake model and on a local endpoint, one durable or observed feature exercised, blocked levels named, and nothing outward without a Gate-D approval id."
activation: "Load first for any request to install, set up, wire, self-host, compare, or evaluate an agent framework, LLM app platform, or workflow engine, and whenever agentic-setup-conductor opens an agentic-setup-session."
instruction: "Probe the machine, pick the framework from the selection matrix (check its when-not), load exactly that framework's agentic-setup-<slug> skill plus the sub-skills its stage needs, climb the proof ladder recording receipts, validate them with proof_ladder.py, judge them with rig-s1gate agentic.setup, and stop at Gate-D for any deploy, signup, or paid call."
applies_when:
  env: "Aside sandbox for uv and pure-JS work; Orca terminal for native addons, JVM, daemons; Docker only when docker info answers"
  runtime: "Python 3.12/3.13 via uv, Node 22 with pnpm/npx, Docker (Colima socket), local OpenAI-compatible model routes"
  deps: "rig-capabilities checked out; rig-s1gate with the agentic.setup rubric; experience-lesson-records validator"
  params: "the job in one sentence, the framework if Mike named one, the target proof level (default L4)"
  budget: "one framework per session; three fix attempts per level, then BLOCKED"
  scale: "a working local setup and a reusable skill, not a production platform migration"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
  - gate-d-required:deploy
  - gate-d-required:signup
  - gate-d-required:paid-api
  - gate-d-required:push
flow:
  - Probe the environment and choose the route from observed facts, not memory.
  - Pick the framework from the selection matrix and read its when-not column.
  - Load the framework skill and the stage sub-skills; fetch today's official docs.
  - Climb L0 to L4 with a receipt per level; name BLOCKED levels with the failing check.
  - Validate receipts, judge them with agentic.setup, and hold L5 at Gate-D.
done_when:
  - "cmd:python3 capabilities/skills/agentic-systems-setup/scripts/validate_hierarchy.py"
  - "cmd:python3 capabilities/skills/agentic-systems-setup/scripts/validate_hierarchy.py --plant bad_path; test $? -eq 2"
  - "cmd:python3 capabilities/skills/agentic-systems-setup/scripts/validate_hierarchy.py --plant unwired_sub; test $? -eq 2"
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/agentic-systems-setup/references/lessons.jsonl"
  - "cmd:python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/agentic-systems-setup/references/lessons.jsonl --run capabilities/skills/agentic-systems-setup/fixtures/run_setup_missing_receipt.jsonl; test $? -eq 2"
  - "file:capabilities/skills/agentic-systems-setup/references/frameworks.md"
out_of_scope:
  - deploying, signing up to a vendor cloud, creating API keys, or spending without Mike's recorded approval id
  - replacing a framework a project already runs without a written migration reason
  - printing, pasting, or storing any credential value
  - projects Mike did not name (First Mate home rule)
---
# agentic-systems-setup

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt sends
semantic triage, routing, and classification (which framework, which route, is this receipt
real) to the rig-s1gate Jev path BEFORE any frontier LLM call; receipts are judged with
`rig-s1gate check agentic.setup`. When the classifier is unavailable: DEFER, never guess a
verdict locally. A required signal passes only above 0.9; below that the level does not count.
Deterministic checks run first: `proof_ladder.py` and `leak_scan.py` are code, not judgment.

## Load surface

Always loaded at task start: load this file first for any request to install, set up, wire,
self-host, compare, or evaluate an agent framework or workflow engine. `agentic-setup-conductor`
loads it before its first action and the `agentic-setup-session` harness names it as doctrine.
It is a task-start surface, not a deep reference an agent must already know about.

## The route in five lines

1. `env -u PYTHONHOME -u PYTHONPATH python3 capabilities/skills/agentic-env-probe/scripts/env_probe.py --out <run>/probe.json`
2. Pick the framework from the matrix below; read its **when not** and its proven level first.
3. Load `agentic-setup-<slug>` and the sub-skills for the stage you are in.
4. Climb the ladder from the level already proven; write `<run>/receipt.json`; run `proof_ladder.py`.
5. `rig-s1gate check agentic.setup --file <run>/receipt.json --subject "agentic:<slug> sha=<12>" --json`; L5 waits for Gate-D.

## Selection matrix (job to framework, with the level proven on this Mac)

Start with the simplest thing that works: plain code plus typed JEV judgments beats a framework
for one call or a fixed 2-5 step pipeline (Anthropic, grounding G1). Pick a framework only when
the job needs what it owns.

| Job | Framework skill | Proven here | When not |
|---|---|---|---|
| One model call or a fixed short pipeline | none: plain code (`hello_baseline.py`) | L3 | never add a framework to save ten lines |
| Stateful agent: tools, branching, human-in-the-loop, resumable threads | `agentic-setup-langchain` | L3 | fixed pipeline; role-play teams |
| RAG and document agents over private data | `agentic-setup-llamaindex` | L2 narrow | retrieval is one query |
| Typed, validated outputs with a thin agent loop | `agentic-setup-pydantic-ai` | L4 | multi-agent durable threads |
| Role-based agent teams plus event-driven Flows | `agentic-setup-crewai` | L3 | step-level durability needed (run under Temporal or Prefect) |
| OpenAI-model agents with handoffs, guardrails, tracing | `agentic-setup-openai-agents-sdk` | L1 | the sandbox (cffi refused); local-only without an adapter |
| Gemini or Vertex-native agents | `agentic-setup-google-adk` | L3 | no Google Cloud account (signup is Gate-D) |
| .NET or Azure agents (AutoGen + Semantic Kernel successor) | `agentic-setup-microsoft-agent-framework` | L3 | Python-only local shop |
| TypeScript agents, workflows, and evals in one package | `agentic-setup-mastra` | L3 | Python shop |
| Durable workflows surviving crashes for hours or days | `agentic-setup-temporal` | L1 + L2 logic | short scheduled jobs |
| Python pipelines with retries, caching, schedules, UI | `agentic-setup-prefect` | L4 | long-lived state machines |
| TypeScript background jobs and long AI tasks | `agentic-setup-trigger-dev` | L3 | no Node project; account refused |
| TypeScript event-driven step functions | `agentic-setup-inngest` | L3 | long CPU-bound runs |
| Declarative YAML event-driven orchestration, polyglot tasks | `agentic-setup-kestra` | L1 | no JDK 25+ and no Docker |
| Asset-centric data pipelines with lineage | `agentic-setup-dagster` | L2 + L4 | agent orchestration |
| Existing Airflow estates, batch DAGs | `agentic-setup-airflow` | L1 + L2 logic | greenfield agent work |
| Business automations across hundreds of SaaS integrations | `agentic-setup-n8n` | L2 + L4 | typed code logic, strict tests |
| Low-code LLM apps (chatflow, RAG, agent apps) for non-engineers | `agentic-setup-dify` | L0 | Docker down; code-first team |
| Visual LLM flow prototyping | `agentic-setup-flowise`, `agentic-setup-langflow` | L1, L1 | production durable workloads |

## Proof matrix (2026-09-28: five workers, levels from their receipts)

Receipts: `capabilities/skills/<skill>/references/proof.json` (step lists; `proof_ladder.py` STEP
mode found all 20 well-formed). "Next" says where the next level has to run.

| Skill | Level here | Blocker | Next step (host shell = Orca terminal) |
|---|---|---|---|
| langchain | L3 | L4 checkpointer: ormsgpack .so refused | host shell: checkpointer kill-and-resume (L4) |
| llamaindex | L2 narrow | tiktoken .so refused blocks index/query; SQLAlchemy pinned 2.0.41 | host shell: index + query, then L3 |
| pydantic-ai | L4 | none | L5 only through Gate-D |
| crewai | L3 (8657) | planted proof re-done: uncaught AssertionError, RED exit 1, GREEN exit 0; L4 not yet exercised | sandbox: Flow persistence kill-and-resume |
| openai-agents-sdk | L1 | import refused: cffi .so via mcp -> cryptography | host shell: L2 fake, L3 local, tracing off |
| google-adk | L3 (8657) | LiteLLM 1.82.7/1.82.8 advisory | keep LiteLLM >=1.84; L4 session persistence |
| microsoft-agent-framework | L3 | L4 not yet exercised | sandbox: checkpointed workflow |
| mastra | L3 | in-memory storage warning | persistent storage, then L4 |
| prefect | L4 | asyncpg .so stubbed; retry fired; server health 200 | host shell with real asyncpg; L5 through Gate-D |
| temporal | L4 | CLI 1.7.2 in ~/.homebrew/bin (not on PATH); own dev server on 4360: L3 model call to 8657 returned PONG, L4 retry after a planted activity failure (attempts 2), planted RED exit 1 | start the dev server under `scripts/bounded_run.sh` (Go ignores SIGALRM, AS-19); Mike's server on :7233 (pid 7353) is off-limits |
| dagster | L2 + L4 | DISABLE_SQLALCHEMY_CEXT=1; native .so moved aside | L3 against a local endpoint |
| airflow | L1 + L2 logic | cffi .so refused | host shell: `airflow standalone` |
| trigger-dev | L3 | esbuild postinstall hangs (`npm i --ignore-scripts`) | dev runs need an account (Gate-D) or self-host |
| inngest | L3 | v4 `createFunction` signature changed | Inngest dev server: step memoization (L4) |
| n8n | L2 + L4 | import:workflow needs a top-level id; DB at `$N8N_USER_FOLDER/.n8n`; L4 re-run on 127.0.0.1:4413 with `N8N_LISTEN_ADDRESS=127.0.0.1` and `N8N_RUNNERS_BROKER_PORT=4459` (healthz ok) | stray node pid 23506 (*:4400, owner-locked) for Mike's terminal; L3 model node |
| dify | L0 | Docker daemon down | Mike: start Colima in a normal terminal, then `docker compose up -d` |
| kestra | L1 | needs Java 25 (not 21); API 401 | stop stray java pid 54463 (*:8080); JAVA_HOME=openjdk@26 or Docker |
| flowise | L1 | server never answered | host shell run |
| langflow | L1 | never bound a port | host shell run, then check the port |
| selfhost-docker (sub) | L1 | Colima not running | Mike: `PATH=~/.homebrew/bin:$PATH colima start` in a normal terminal |

Correction (A6, 14:30 probe): Colima 0.10.3, docker 29.6.1, lima 2.1.3, ollama, and Temporal CLI 1.7.2
are installed in `~/.homebrew/bin`, which is not on the sandbox PATH; JDK 17/21/26 sit keg-only in
`~/.homebrew/opt` (JDK 26 at `~/.homebrew/opt/openjdk@26`). Workers and the first probe missed them
because nothing searched `~/.homebrew` (lesson AS-13). The Temporal dev server on 127.0.0.1:7233
(pid 7353) is Mike's and is not used by setup proofs.

Independent verification (2026-09-28, different model family xai-oauth/grok-4.7): langchain,
prefect, and trigger-dev CONFIRMED. crewai: the planted-failure proof was invalid (the plant exited
0); the worker re-did it (RED exit 1, GREEN exit 0, sha-guarded) and fixed the same defect in
google-adk and microsoft-agent-framework. n8n: the verifier could not reproduce L4 while the stray
held 127.0.0.1:5679; the worker then reproduced it on free loopback ports (4413, broker 4459). dify: the Docker Compose docs quote is confirmed
against grounding sha ac3c0061d500. The other levels are worker-reported and not yet re-verified.

## Where it runs (route)

| Route | Use for | Observed 2026-09-28 14:30 (probe-2026-09-28-final.json) |
|---|---|---|
| Aside sandbox | uv venvs, pure-JS Node, HTTP to loopback model routes | uv, Python 3.12/3.13, node 22, pnpm, n8n in ~/.local/bin, not on the sandbox PATH; PYTHONHOME exported |
| Aside sandbox, native Python extensions | only if already loaded clean; otherwise fallback, pin, or stub | library_validation PRESENT: freshly written .so are refused ("library load disallowed by system policy"); AS-11 |
| Host shell (Orca terminal) | refused .so, native .node addons, daemons, long servers | full PATH; the next level for 7 frameworks runs here |
| Docker | Dify, Kestra, Langfuse, Flowise/Langflow images, Airflow compose | BLOCKED: Colima 0.10.3 installed, not running; `colima status` needs ~/.homebrew/bin on PATH or it fails "lima not found" (lima 2.1.3 is there); starting it is Mike's host-shell step |
| JVM | Kestra, Temporal Java SDK | JDK 26 via JAVA_HOME (keg-only Homebrew); the macOS `java` stub fails |
| Model routes | hellos (L3) | 127.0.0.1:8771 and :8657 answered; Blackwell :8111 answered at 14:30 (timed out at 09:25); :8011, :11435, OmniRoute :20128 refused |
| Vendor cloud | never by default | Gate-D (signup, data egress, spend) |

Strays to stop from a normal terminal (sandbox kills are refused): java pid 54463 on `*:8080`
(Kestra lab), node pid 23506 on `*:4400` (n8n lab). Both bind all interfaces, so they are
reachable from the LAN while they run.

## Universal setup protocol (gates E1-E8, harness `agentic-setup-session`)

| Gate | Step | Sub-skill | Proof |
|---|---|---|---|
| E1 | Probe the machine, model routes, library validation, and listeners | `agentic-env-probe` | probe.json from env_probe.py dated today |
| E2 | Select framework and route; fetch official docs today | `agentic-proof-ladder` (L0) | matrix row + when-not answered; doc URL + sha + pinned version |
| E3 | Install in the route; wire a local-first model with a named fallback | `agentic-local-models`, `agentic-selfhost-docker` | L1 receipt; probe_endpoint.py ANSWERED_OK |
| E4 | Secrets by keychain item name only | `agentic-secrets` | leak_scan.py exit 0 over project, logs, receipts |
| E5 | Hello proof on a fake model, then a local endpoint | `agentic-proof-ladder`, `agentic-local-models` | L2 and L3 receipts |
| E6 | One durable or observed feature exercised; MCP if the job needs tools | `agentic-durable-execution`, `agentic-observability`, `agentic-mcp-integration` | L4 receipt with run id |
| E7 | Tests and evals that can fail | `agentic-testing-evals` | assertion-bearing tests; planted failure RED then GREEN |
| E8 | Deploy only through Gate-D; close with lessons | `agentic-deploy-gate` | approval id or `held_at_gate`; agentic.setup decision id |

## Proof ladder

L0 official docs fetched today with sha and pinned version · L1 installed here · L2 hello on a
deterministic fake model · L3 same hello on a local endpoint · L4 durable or observed feature
exercised · L5 deployed, which requires a Gate-D approval id. A level that cannot run is
recorded BLOCKED with the failing check; BLOCKED is never PASS. Validator and baseline:
`agentic-proof-ladder` (the plain-code baseline reached L3 on 2026-09-28).

## Gate-D table (stop and ask Mike)

| Action | Examples | Free without Gate-D |
|---|---|---|
| Vendor signup or cloud login | `npx trigger.dev@latest login`, `prefect cloud login`, LangSmith, Dify Cloud, CrewAI AMP | local servers on loopback |
| Deploy or publish | `trigger.dev deploy`, `langgraph deploy`, `crewai deploy`, pushing images, publishing n8n/Dify apps | local `docker compose up` bound to 127.0.0.1 |
| Paid model calls | OpenAI, Anthropic, OpenRouter keys | fake models, local endpoints |
| Public exposure | ngrok or cloud tunnels, third-party webhooks, servers bound to all interfaces | loopback URLs |
| Data egress | traces to LangSmith or Langfuse Cloud | local traces, self-hosted Langfuse |
| Credentials | creating, rotating, or storing keys | reading a keychain item into a child env |
| Outward effects of a built workflow | an n8n or Dify flow that emails, posts, or pays | dry-run with the effect node disabled |
| Sandbox protections | stripping quarantine attributes, re-signing native code (AS-18) | routing to the host shell |
| Destructive cleanup | deleting volumes or databases holding data | removing a venv you created this session |

## Sub-skills (this family)

`agentic-env-probe`, `agentic-local-models`, `agentic-secrets`, `agentic-proof-ladder`,
`agentic-durable-execution`, `agentic-observability`, `agentic-testing-evals`,
`agentic-mcp-integration`, `agentic-deploy-gate`, and `agentic-selfhost-docker` (Docker and
Colima routes).

## Existing skills and the role each keeps

| Skill | Keeps this role | Relation |
|---|---|---|
| `tool-langchain` | langchain-core primitives inside the Design Harness venv | framework setup goes to `agentic-setup-langchain` |
| `tool-langgraph` | graph-shaped Design Harness slices | general LangGraph setup lives in `agentic-setup-langchain` |
| `tool-temporal` | deterministic Temporal Python workflows for Design Harness runtimes | fresh Temporal installs go to `agentic-setup-temporal` |
| `tool-mastra` | verifying the installed Mastra CLI; Mastra is not the Design Harness carrier | new Mastra projects go to `agentic-setup-mastra` |
| `tg-durable-ai-pipelines` | durable AI pipelines inside App Studio builds | shares `agentic-durable-execution` |
| `autonomous-ai-agents` | router for autonomous coding agents (Claude Code, Codex, Hermes) | adjacent: coding agents are not frameworks |
| `app-sandbox-survival` | Aside sandbox build and process rules | shares the sandbox lessons |
| `docker-agentic-stack` (Hermes) | archived by 14:35 (now `~/.hermes/skills/.archive/`) | role owned by `agentic-selfhost-docker` |

Machine-readable org chart: `hierarchy.json`; validator: `scripts/validate_hierarchy.py --strict`
(V1-V10, nine plants).

## Agents, harness, loop, JEV

Conductor `agentic-setup-conductor` (routes and gates; never installs; its framework routes table
names every `agentic-setup-*` skill with its proven level) dispatches `agentic-env-prober`,
`agentic-proof-runner`, and `agentic-docs-verifier`. Harness
`capabilities/harnesses/agentic-setup-session.yaml`; loop
`capabilities/loops/agentic-setup-proof-loop.md`; rubric `agentic.setup` judges receipts
(kinds `agentic.setup`, `agentic-setup`, `agent-framework-setup`).

## Lessons that fire as gates

Active (`references/lessons.jsonl`, each check performed by a script that writes a receipt):
AS-01 PyInstaller CLIs exit 1 · AS-02 PYTHONHOME leaks · AS-03 PATH lacks ~/.local/bin · AS-04
Docker daemon down · AS-05 JDKs are keg-only · AS-06 native .node addons · AS-07 reasoning models
return empty content · AS-08 probe routes, not memory · AS-09 docs before commands · AS-10 signup is
outward · AS-11 library validation refuses fresh native .so · AS-12 stray listeners · AS-13 tools
under ~/.homebrew. Candidates (`references/lessons-candidates.jsonl`, promoted when a script checks
them): AS-14 time-box long runs · AS-15 npm cache per lab · AS-16 `--ignore-scripts` · AS-17
supply-chain pins · AS-18 stripping quarantine is Mike's call. Fire them:
`python3 capabilities/skills/experience-lesson-records/validate_lessons.py capabilities/skills/agentic-systems-setup/references/lessons.jsonl --run <run>.jsonl`.

## Grounding (fetched 2026-09-28, quotes and sha in references/grounding.md)

- G1 Anthropic, Building effective agents: find the simplest solution possible; workflows run
  on predefined code paths, agents direct their own process; frameworks add abstraction layers.
- G2 LangGraph overview: low-level orchestration runtime for long-running stateful agents with
  durable execution, streaming, and human-in-the-loop.
- G3 CrewAI introduction: Flows own state and event-driven execution; Crews are agent teams
  inside a Flow.
- G4 Prefect: state and recovery, resume interrupted runs, cache expensive computations.
- G5 12-factor agents: own your control flow; small, focused agents.
- G6 Kestra, Dify, Trigger.dev quickstarts: Docker single command, Docker Compose with 2 CPU and
  4 GiB minimum, and a signup before `npx trigger.dev@latest init`.
