---
name: agentic-setup-n8n
description: "Agentic-systems-setup skill for self-hosted n8n on Mike's Mac: the AI Agent node, credentials with a custom base URL, workflows as JSON, webhook triggers, and CLI import/publish against an isolated N8N_USER_FOLDER, with receipts from a verified local run. JEV FIRST: route typed judgments to rig-s1gate before any frontier model and fail closed. Use when an agent must stand up n8n end to end without cloud, or when an n8n workflow run is claimed without a receipt."
tags: [rig, agentic-systems-setup, n8n, workflows, automation, self-hosted]
metadata:
  family: agentic-systems-setup
  tier: framework
  model: "mimo-plan/mimo-v2.6-pro (fallback xai-oauth/grok-4.7, then anthropic/claude-opus-5-5; never Flash)"
outcome: "An n8n instance running from an isolated user folder with a workflow imported as JSON and verified in its database, its cloud/owner steps named and untouched, and its model credentials pointing at local OpenAI-compatible endpoints only."
activation: "Load for any n8n install/start, workflow-as-JSON work, AI Agent node wiring, credential setup, or webhook trigger request on Mike's Mac, or when an n8n run is claimed without a receipt."
instruction: "JEV first via rig-s1gate before any frontier model call, fail closed (DEFER) when it is down; prove installs and runs with receipts, isolate N8N_USER_FOLDER, keep model credentials on local base URLs, stop at owner/cloud boundaries, and gate outward steps with Gate-D."
applies_when:
  env: "Aside sandbox runs the n8n binary locally; host shell for Docker-based hosting"
  runtime: "Node 22 (verified v22.22.3); n8n binary at ~/.local/bin/n8n (verified 2.33.3)"
  deps: "n8n (global npm install); a workflow JSON per project"
  params: "lab dir ~/.rig/agentic-lab/n8n; N8N_USER_FOLDER inside the lab dir; port 4400"
  budget: "one instance, one hello-world workflow, one run attempt per session"
  scale: "single self-hosted instance; not n8n Cloud"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Verify the environment (PATH prefix, n8n --version) and isolate N8N_USER_FOLDER inside the lab dir.
  - Start n8n locally, confirm health, and keep the run log.
  - Write the workflow as JSON and import it through the CLI; verify persistence by a second read path.
  - Wire model credentials to a local OpenAI-compatible base URL (no paid keys) and stop at owner/cloud steps.
  - Stop the server, write proof receipts, and gate the skill with rig-s1gate and the skill contract.
done_when:
  - "grep:capabilities/skills/agentic-setup-n8n/SKILL.md:fake-model"
  - "grep:capabilities/skills/agentic-setup-n8n/SKILL.md:Gate-D"
  - "grep:capabilities/skills/agentic-setup-n8n/references/proof.json:exit_code"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-n8n/SKILL.md"
out_of_scope:
  - "n8n Cloud signup or paid plans (Gate-D, never in this skill's runs)"
  - "creating an owner account or public webhook/tunnel exposure without Mike's approval"
  - "editing any existing n8n data outside the lab user folder"
---

# agentic-setup-n8n

Start here when: a project needs self-hosted n8n workflows, the AI Agent node, credentials, or webhook triggers on Mike's Mac.

JEV FIRST (findable at task start), binding on every setup step: route typed judgments to rig-s1gate (Jev) BEFORE any frontier LLM call, and FAIL CLOSED (DEFER, never guess). Specifically: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier
LLM call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a
local guess. Required signals pass only above 0.9. This skill's verdicts go to
`./bin/rig-s1gate check doctrine.surface --file <skill> --subject "doctrine:<id> sha=$(shasum -a 256 <skill> | cut -c1-12)" --json`.

## Load surface

Always loaded at the START of every n8n self-hosted setup task on Mike's Mac: the
`agentic-systems-setup` family routes here before the first setup action, and every
typed judgment in this skill goes to JEV via `rig-s1gate` before any frontier LLM
call. It is a task-start surface, not a deep reference an agent must already know
about. A required signal passes only above 0.9; below that the step does not advance,
and an uncalibrated ESCALATE is a held transition.

## 1. When to choose it, and when not

Choose n8n when the deliverable is **self-hosted, visual, node-based automation**: workflow-as-JSON,
hundreds of app integrations, webhooks and schedules as triggers, and an AI Agent node that connects
a chat model with tools. Good for ops automation Mike wants to inspect and edit in a UI.

Do **not** choose it when:

- The workflow must be code-first with real durable execution semantics (step memoization, replay,
  per-step retries) — that is Inngest or Trigger.dev.
- The ask is a hosted low-code AI builder with RAG apps out of the box (that is Dify or Flowise), or
  a data-orchestration DAG (Prefect/Dagster/Airflow) or a job-scheduler YAML DSL (Kestra).

**Two nearest alternatives:** `dify` (hosted/self-hosted LLM app builder with RAG) and `flowise`
(self-hosted LangChain visual builder). For code-first durable steps, see `inngest`.

## 2. Current version and sources (fetched 2026-09-28)

- n8n binary **2.33.3** — verified here: `~/.local/bin/n8n --version` printed `2.33.3`
  (symlink: `~/.local/bin/n8n -> ../lib/node_modules/n8n/bin/n8n`).
- Official docs fetched today: https://docs.n8n.io/hosting/installation/docker/ (self-hosting;
  notes npm latest is `stable` 2.40.7 while **2.33.3 is the version proven here** (do not claim
  2.40.7); Docker/Compose is n8n's
  recommended host route; SQLite default database, Postgres optional) and
  https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/
  (AI Agent node: connect a chat model plus at least one tool sub-node; the agent-type setting is
  deprecated from 1.82.0 and node v1 goes away in n8n 3.0; MCP servers can attach as tools).

## 3. Environment route and prerequisites

- **Aside sandbox:** the n8n binary runs here (verified). Use the PATH prefix:
  `export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"` (node v22.22.3, npm 10.9.8).
- **Isolate the data dir (mandatory):** `export N8N_USER_FOLDER="$HOME/.rig/agentic-lab/n8n/data"`
  before any start or CLI command, so an existing n8n instance's data is never touched. Observed
  here: with `N8N_USER_FOLDER` set, the real database lands at **`$N8N_USER_FOLDER/.n8n/database.sqlite`**
  (n8n appends `.n8n` under the user folder).
- **Host shell:** Docker-based hosting per docs (Colima is down here and Docker is another worker's
  lane); n8n also warns that running outside a container is deprecated.
- Observed runtime notes from the verified run: the internal Python task runner failed
  ("its virtual environment is missing from this system") — JS task runner registered fine; n8n
  prints deprecation notices for `N8N_RUNNERS_ENABLED` (not needed since 2.0) and other defaults.

## 4. Install (exact commands)

n8n is already installed on this Mac (verified 2.33.3). To install elsewhere:

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
npm i -g n8n          # global npm route (what this Mac uses)
# n8n's recommended host route is Docker/Compose - Gate-D and host shell
```

Start (run here):

```bash
export N8N_USER_FOLDER="$HOME/.rig/agentic-lab/n8n/data"
nohup env N8N_USER_FOLDER="$N8N_USER_FOLDER" N8N_PORT=4400 N8N_SECURE_COOKIE=false \
  ~/.local/bin/n8n start > n8n.log 2>&1 &
curl -s -m 5 http://localhost:4400/healthz    # {"status":"ok"}
```

## 5. Local-first model wiring

The AI Agent node takes a chat model sub-node (for example the OpenAI Chat Model) whose credential
carries an API-key field and a **base URL override** — point that base URL at Mike's local
OpenAI-compatible endpoints and use no paid key. Probe first:

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

- n8n encrypts credentials with its own instance encryption key kept in the user folder — another
  reason `N8N_USER_FOLDER` isolation matters (observed here: `$N8N_USER_FOLDER/.n8n/`).
- API keys for model endpoints are referenced by keychain item name (`com.rig.env.LOCAL_LLM_API_KEY`)
  and entered into n8n's credential store through its UI/API; values never appear in workflow JSON,
  logs, or this skill. Workflow JSON files export without credential values (n8n exports ids only).

## 7. Hello-world (run here)

`hello-workflow.json`: Webhook node (POST `a4-hello`, respond-with-response-node) → Code node with
`// Deterministic fake model: no network, no paid key.` computing
`fake-model:HELLO <NAME>` → Respond to Webhook node. Import and list:

```bash
export N8N_USER_FOLDER="$HOME/.rig/agentic-lab/n8n/data"
~/.local/bin/n8n import:workflow --input=hello-workflow.json   # "Successfully imported 1 workflow."
~/.local/bin/n8n list:workflow                                # a4hello|A4 hello (fake model)
```

Observed: `import:workflow` **fails with `SQLITE_CONSTRAINT: NOT NULL constraint failed:
workflow_entity.id`** if the JSON has no top-level `"id"` — add one. Verified persistence by reading
the instance database through a second path:
`sqlite3 "$N8N_USER_FOLDER/.n8n/database.sqlite" "select id,name,active from workflow_entity;"`
→ `a4hello|A4 hello (fake model)|1`.

## 8. Durable and production features (docs + observed)

n8n workflows have retries (per-node error workflow / retry settings), wait nodes, execution
concurrency settings, schedules (Schedule Trigger), and webhooks (production vs test URLs).
Observed here: server start, migration run, health endpoint, CLI import/list/publish. **Not achieved
here:** production webhook activation — with `active=1` the live webhook still answered
`404 The requested webhook "POST a4-hello" is not registered` and `webhook_entity` stayed empty,
because n8n 2.x registers production webhooks from a published version through the editor/API, and
this instance had no owner account. Record this as an open step, not as a pass.

## 9. Observability

n8n's editor UI (http://localhost:4400 when running) shows executions, per-node run data, and logs;
executions persist in the instance database (`execution_entity`). AI Agent runs additionally log
model/tool activity in the node output. No OTel claim is made without a run proving it.

## 10. Testing (deterministic fake model + one planted failure)

- Deterministic fake model: the Code node computes `fake-model:HELLO <NAME>` — no network, no key.
- Unit-style test here = the CLI import + `list:workflow` + second-path database read-back (assert
  the exact row, not merely exit 0).
- **Planted failure, run here:** corrupt one field of the workflow JSON (drop `"id"`), re-run import,
  require RED (`SQLITE_CONSTRAINT`, exit 1); restore, re-run, require GREEN (exit 0). Checksum the
  JSON before and after the plant so an unlanded plant cannot fake a pass.

## 11. Deploy / self-host, and what is Gate-D

**Gate-D (Mike's explicit approval required; never done here):** n8n Cloud signup or paid plan,
creating the instance owner account, exposing a public URL or tunnel (`--tunnel`), publishing
webhooks to the internet, or installing community packages that phone home. Self-hosting with
Docker/Compose (docs' recommended route) needs a host shell and Gate-D — Colima is down here and
Docker is another worker's lane. Local loopback on 4400 is the default posture.

## 12. Teardown and upgrade

```bash
lsof -t -i :4400 | xargs kill      # stop every n8n you started
rm -rf ~/.rig/agentic-lab/n8n      # removes the isolated user folder + database
```

Upgrade: `npm i -g n8n@<version>` (docs' stable is 2.40.7 as of 2026-09-28; this Mac runs 2.33.3),
then re-run the import/list/read-back receipts. Keep `N8N_USER_FOLDER` isolated across upgrades.

## 13. Gotchas (each tagged with where observed)

1. **`import:workflow` needs a top-level workflow `"id"`** — without it: `SQLITE_CONSTRAINT: NOT NULL
   constraint failed: workflow_entity.id` (observed here, 2026-09-28, exact error text).
2. **The real database is one level deeper than expected** — `$N8N_USER_FOLDER/.n8n/database.sqlite`,
   not `$N8N_USER_FOLDER/database.sqlite` (observed here: a direct sqlite3 read of the wrong path
   reported `no such table: workflow_entity`).
3. **Production webhooks need editor/API activation** — `active=1` in the database is not sufficient
   on a fresh ownerless instance: the live webhook still 404s and `webhook_entity` stays empty, and
   `update:workflow` is deprecated in favor of `publish:workflow` with "changes will not take effect
   if n8n is running" (observed here: exact 404 payload and CLI notices captured in proof.json).

4. **The task broker binds 5679 by default** — `N8N_RUNNERS_BROKER_PORT` (default `5679`) and the
   runner-side `N8N_RUNNERS_TASK_BROKER_URI` (default `http://127.0.0.1:5679`); docs:
   https://docs.n8n.io/hosting/configuration/environment-variables/task-runners/. A second
   instance then fails `port 5679 already in use` even on a free HTTP port (observed here
   2026-09-28 by an independent verifier on 4412). Move both when any other n8n exists.
5. **A sandbox-started n8n is LAN-exposed and ownerless** — `N8N_LISTEN_ADDRESS` defaults to `::`
   (all interfaces; docs: https://docs.n8n.io/hosting/configuration/environment-variables/deployment/),
   and until setup the instance has no owner. The stray on *:4400 proved the exposure; the
   parent has locked it (unauthenticated calls now 401) pending `kill 23506`. Always start with
   `N8N_LISTEN_ADDRESS=127.0.0.1` and either set up an owner or stop the instance.

## 14. Proof receipts (2026-09-28)

| Command | Exit | Version | Observed | Proof level |
|---|---|---|---|---|
| `~/.local/bin/n8n --version` | 0 | 2.33.3 | `2.33.3` | L0 |
| `N8N_USER_FOLDER=... N8N_PORT=4413 N8N_LISTEN_ADDRESS=127.0.0.1 N8N_RUNNERS_BROKER_PORT=4459 N8N_RUNNERS_TASK_BROKER_URI=http://127.0.0.1:4459 n8n start` + `curl /healthz` | 0 | 2.33.3 | `{"status":"ok"}` HTTP 200 on 127.0.0.1:4413; `n8n Task Broker ready on 127.0.0.1, port 4459`; lsof 127.0.0.1-only LISTEN (self-destructed via perl alarm 110) | L4 (reproduced) |
| `n8n import:workflow --input=hello-workflow.json` (no `"id"`) | 1 | 2.33.3 | `SQLITE_CONSTRAINT: NOT NULL constraint failed: workflow_entity.id` (planted-ish failure) | L2 |
| `n8n import:workflow --input=hello-workflow.json` (with `"id"`) | 0 | 2.33.3 | `Successfully imported 1 workflow.` | L2 |
| `n8n list:workflow` | 0 | 2.33.3 | `a4hello|A4 hello (fake model)` | L2 |
| `sqlite3 $N8N_USER_FOLDER/.n8n/database.sqlite "select id,name,active from workflow_entity"` | 0 | n/a | `a4hello|A4 hello (fake model)|1` (second-path read-back) | L2 |
| webhook POST `/webhook/a4-hello` | 404 | 2.33.3 | `not registered`; `webhook_entity` empty — production activation needs editor/API (open step) | not claimed |
| verifier's fresh `n8n start` on 4412 | 1 | 2.33.3 | `port 5679 already in use` — stray pre-stop instance (pid 23506 on *:4400) holds the default task-broker port; move it with `N8N_RUNNERS_BROKER_PORT` | documented in gotchas |
| docs fetches (hosting/installation/docker; AI Agent node) | 0 | n/a | self-host + AI Agent surface confirmed | L0 |

L3 is NOT claimed for n8n: the hello-world's model stand-in is a Code node (`fake-model:` string),
no model call was made. Local-endpoint wiring for the AI Agent node is documented in section 5.
Level now claimed: **L2 reproduced by an independent verifier; L4 observed once on 2026-09-28 and
reproduced 2026-09-28 on free ports (127.0.0.1:4413, broker 4459)**. Not reproducible on the
original port while the stray lives: pid 23506 still listens on *:4400 and holds broker 5679;
Mike must stop it with `kill 23506` from a normal terminal. L5 is Gate-D and was not done.
Full receipts: `references/proof.json`.
