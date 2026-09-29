---
name: agentic-setup-flowise
description: "Agentic Systems Setup: Flowise on Mike's Mac - visual LLM agent/flow builder (LangChain.js based), installed via npm (or Docker), with chatflows/agentflows, OpenAI-compatible local model credentials, tools/memory, API and embedded chat. Use when Mike wants a fast drag-and-drop agent builder with JS-native integrations, a public API per chatflow, or an embeddable chat widget. JEV-FIRST MANDATE."
when_to_use: "Flowise, chatflow, agentflow, Flowise API, embeddable chat, LangChain.js. JEV-FIRST MANDATE: route typed judgments to rig-s1gate before any frontier model; DEFERRED when the classifier is down."
tags: [rig, agentic-systems-setup, flowise, node, npm, agents, chatflows]
metadata:
  family: agentic-systems-setup
  tier: framework
  siblings: "agentic-setup-dify, agentic-setup-kestra, agentic-setup-langflow, agentic-selfhost-docker"
outcome: "A Flowise instance running from the lab dir on a 45xx port, with one chatflow whose model credential points at a local OpenAI-compatible endpoint and whose prediction API answers deterministically."
activation: "JEV-FIRST MANDATE, findable at task start: route typed judgments to rig-s1gate before any frontier model; DEFERRED is the only answer when the classifier is down. Load for any request to run, script, or embed Flowise: chatflows, agentflows, credentials, prediction API, or its Docker/npm lifecycle."
instruction: "JEV FIRST, findable at start: run ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model; PASS continues, ESCALATE rewrites, BLOCK stops, DEFERRED fails closed. Then: install only under ~/.rig/agentic-lab/flowise; wire credentials to local endpoints; treat npm install success as setup, not completion."
applies_when:
  env: "Mike's Mac, local-only; Aside sandbox bash or host shell"
  runtime: "Node 18.15.0 or 20+ (docs); npm-global install into the lab prefix; or Docker via agentic-selfhost-docker"
  deps: "node/npm in ~/.local/bin; native .node addons may be BLOCKED in the Aside sandbox (see gotchas)"
  params: "FLOWISE_PORT=4520 (lab range 4500-4599); storage dir under ~/.rig/agentic-lab/flowise"
  budget: "one instance; teardown after proof"
  scale: "single-user local; SQLite-backed by default, not multi-tenant"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - JEV FIRST, findable at task start: route every typed judgment to rig-s1gate (Jev) via ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model call; DEFERRED when the classifier is down, fail closed.
  - Verify the Node runtime and pin the Flowise version from the npm registry.
  - Install with --prefix into the lab dir and record the exact npm output and exit code.
  - Start on a lab port with the storage dir inside the lab dir; prove /health or the UI port.
  - Create a chatflow wired to a local OpenAI-compatible endpoint (or record BLOCKED).
  - Call the prediction API for a deterministic receipt, then stop the server and clean up.
done_when:
  - "grep:capabilities/skills/agentic-setup-flowise/SKILL.md:flowise@3.1.4"
  - "grep:capabilities/skills/agentic-setup-flowise/SKILL.md:com.rig.env"
  - "grep:capabilities/skills/agentic-setup-flowise/SKILL.md:Gate-D"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-flowise/SKILL.md"
out_of_scope:
  - Flowise Cloud signup, enterprise license keys, paid plans (Gate-D)
  - paid model API keys (local endpoints only)
  - public URLs, tunnels, embeds on live client sites (Gate-D)
---

# agentic-setup-flowise

JEV FIRST, binding on every Flowise-setup decision: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; receipts are judged with `rig-s1gate check doctrine.surface`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the gate does not advance.

## Load surface

Always loaded at the start of every agentic-systems-setup task: the agentic-systems-setup family routes here before the first install, start or teardown command. It is a task-start surface, not a deep reference an agent must already know about. Typed judgments it forces: did install really finish; is the server healthy; did the prediction call return the expected body; is this a native-addon BLOCK (environment) or a code failure.


## 1. When to choose it and when not

Choose Flowise for fast visual chatflow/agentflow building on a JS stack, embeddable chat widgets, and per-chatflow REST prediction APIs. Do not choose it for declarative, git-friendly, schedule/event-driven batch orchestration - the two nearest alternatives are **kestra** (YAML flows with cron/webhook triggers and namespaces) and **langflow** (Python-native visual flows with custom components and MCP). Pick Flowise over those when the deliverable is a chat/agent experience to embed, not a pipeline.

## 2. Current version and sources

Verified 2026-09-28:
- **Flowise 3.1.4** (npm registry `https://registry.npmjs.org/flowise/latest`, fetched today).
- Docs fetched today: https://docs.flowiseai.com/getting-started - Node `v18.15.0` or `v20` and above supported; install `npm install -g flowise`; start `npx flowise start`; UI at http://localhost:3000; Docker Compose via the repo's `docker/` folder with its `.env.example`; enterprise env keys `LICENSE_URL` / `FLOWISE_EE_LICENSE_KEY` (not used here).

## 3. Environment route and prerequisites

- **npm route (primary here):** `npm install --prefix ~/.rig/agentic-lab/flowise flowise@3.1.4`. Node here is ~/.local/bin/node.
- **Docker route:** `flowise` compose from the repo `docker/` folder via agentic-selfhost-docker - BLOCKED on 2026-09-28 (Colima 0.10.3 in ~/.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`.
- **Sandbox limitation:** native Node `.node` addons are BLOCKED in the Aside sandbox; Flowise bundles SQLite native bindings, so if the server fails on a `.node`/`better-sqlite3` error, record BLOCKED (environment) and switch to the host shell or Docker route - do not report FAILED as a Flowise defect.
- Docs state no RAM floor for the npm route; keep 4 GB free like the sibling stacks.

## 4. Install (exact, pinned)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/flowise
npm install --prefix ~/.rig/agentic-lab/flowise flowise@3.1.4
# start (docs: "npx flowise start") on a lab port with local storage:
FLOWISE_PORT=4520 FLOWISE_HOME=~/.rig/agentic-lab/flowise/data \
  ~/.rig/agentic-lab/flowise/node_modules/.bin/flowise start
```

Pin `flowise@3.1.4` (verified tag, 2026-09-28). `FLOWISE_PORT` and `FLOWISE_HOME` are Flowise's documented env names (docs `.env.example` reference) - read `node_modules/flowise/.env.example` after install and record the exact names if they differ.

## 5. Local-first model wiring

In a chatflow, the OpenAI-compatible models take an **OpenAI API credential** whose `BasePath` points at the local endpoint (e.g. `http://192.168.68.90:8011/v1`) - no paid key. Probe first: `curl -s -m 5 http://192.168.68.90:8011/v1/models`; on 2026-09-28 Local OpenAI-compatible endpoints verified ANSWERING from this sandbox on 2026-09-28: http://127.0.0.1:8771/v1 (model qwen3.8-uncensored:27b; disable thinking or the content comes back empty) and http://127.0.0.1:8657/v1 (model MiMo-V2.6-Flash-RL-MLX-4bit-MTP). The Blackwell LAN endpoints http://192.168.68.90:8011/v1 and :8111/v1 refuse (curl exit 7). Probe first: `curl -s -m 5 <base>/models`. From containers use the host LAN address of these same servers; never a paid key.

## 6. Secrets

Credentials live in Flowise's encrypted credential store (SQLite), entered via the UI - never in files. Keychain names for anything scripted: `com.rig.env.OPENAI_API_KEY_LOCAL`, `com.rig.env.FLOWISE_SECRETKEY_OVERWRITE` (if you set Flowise's own secret-key env, name it from `node_modules/flowise/.env.example`, never invent it). `.env.example` placeholders only; change every default password/secret (Flowise ships `FLOWISE_SECRETKEY_OVERWRITE`, `APIKEY_PATH`, and optional `FLOWISE_USERNAME`/`FLOWISE_PASSWORD`).

## 7. Hello-world

Deterministic receipt (no model): after start, `curl -s -m 5 http://127.0.0.1:4520/health` (or the UI returning 200 at `/`). Then the API path with a model-step chatflow: `POST /api/v1/prediction/<chatflow-id>` with JSON `{"question": "ping"}`. references/hello-chatflow.json is the importable skeleton (Import via the UI's chatflow import).

## 8. Durable and production features

Chatflows vs agentflows (agent with tools/memory), credential store, per-chatflow API keys (`Authorization: Bearer <FLOWISE_API_KEY>`), embedded chat iframes, and file uploads/attachments for RAG. Persistence is the SQLite file under `FLOWISE_HOME` - back it up before upgrades.

## 9. Observability

Server stdout log (`nohup ... > /tmp/fw-run.log`), `/health`, and per-prediction responses. A running process is setup, not completion - require an HTTP response body.

## 10. Testing

Deterministic test = `/health` 200 and a `/api/v1/prediction/<id>` response whose body contains the deterministic echo of the input (e.g. a Text node concatenating a constant). **Planted failure:** POST to a nonexistent chatflow id - the API must return an error (404-ish `Chatflow ... not found`); if it returns 200 the test is theater. Record both receipts.

## 11. Deploy / self-host hardening and Gate-D

Bind to 127.0.0.1, set `FLOWISE_USERNAME`/`FLOWISE_PASSWORD` or API keys for any non-loopback use, and keep the storage dir inside the lab dir. **Gate-D (never without Mike's explicit approval):** Flowise Cloud signup, `FLOWISE_EE_LICENSE_KEY` purchases, deploys, pushes, paid plans, public URLs or tunnels/ embeds on live sites.

## 12. Teardown and upgrade

Stop the server with `lsof -t -i :4520 | xargs kill` (ps/pgrep are blocked here), confirm the port is closed (`curl` returns 7), archive/delete `~/.rig/agentic-lab/flowise/data` if disposable. Upgrade = `npm install --prefix ... flowise@<new>` after reading the changelog; back up the SQLite store first.

## 13. Gotchas

- Flowise is LangChain.**js**-based: a LangChain Python mental model misleads on custom tools (docs repo structure, fetched today).
- Native `.node` addons are BLOCKED in this sandbox (environment fact verified 2026-09-28) - the likely first failure is SQLite's `better-sqlite3` binding at startup; classify BLOCKED, not FAILED.
- Docs' quick start uses `npm install -g flowise` + `npx flowise start` on port 3000 (docs, 2026-09-28) - the lab rule moves it to a 45xx port and a lab prefix; record the port/env names you actually used.
- Enterprise keys (`LICENSE_URL`, `FLOWISE_EE_LICENSE_KEY`) are only for licensed features (docs, 2026-09-28) - leave unset; they are Gate-D purchases.

## 14. Proof receipts

| Command | Exit | Observed | Date | Proof |
|---|---|---|---|---|
| `curl https://registry.npmjs.org/flowise/latest` | 0 | version 3.1.4 | 2026-09-28 | L0 |
| docs.flowiseai.com/getting-started fetch | 0 | Node 18.15+/20+, install/start commands | 2026-09-28 | L0 |
| `npm install --prefix ~/.rig/agentic-lab/flowise flowise@3.1.4` | see proof.json | running at time of writing; final status recorded there | 2026-09-28 | L1 |
| `docker compose up -d` (docker route) | - | BLOCKED (no Docker daemon) | 2026-09-28 | L0 |

Proof level reached is recorded in references/proof.json (L1 if npm install completed, L2 only if the server answered).
