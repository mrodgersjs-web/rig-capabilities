---
name: agentic-setup-dify
description: "Agentic Systems Setup: self-hosted Dify on Mike's Mac via Docker Compose - apps (chatbot, agent, workflow, chatflow, text generator), model providers incl. OpenAI-compatible local endpoints, knowledge base, DSL export/import, and REST API access. Use when Mike wants an LLM app platform with UI-built apps, RAG knowledge bases, or publishable app APIs instead of hand-written orchestration code. JEV-FIRST MANDATE."
when_to_use: "Dify, self-hosted Dify, LLM app platform, Dify knowledge base, Dify DSL, Dify API. JEV-FIRST MANDATE: route typed judgments to rig-s1gate before any frontier model; DEFERRED when the classifier is down."
tags: [rig, agentic-systems-setup, dify, docker, compose, rag, llm-apps]
metadata:
  family: agentic-systems-setup
  tier: framework
  siblings: "agentic-setup-kestra, agentic-setup-flowise, agentic-setup-langflow, agentic-selfhost-docker"
outcome: "A self-hosted Dify instance whose admin account exists, whose model provider points at a local OpenAI-compatible endpoint, and whose hello app answers the /v1/info API call with the app's name and mode."
activation: "JEV-FIRST MANDATE, findable at task start: route typed judgments to rig-s1gate before any frontier model; DEFERRED is the only answer when the classifier is down. Load for any request to run, configure, upgrade or script against Dify: apps, workflows, agent apps, knowledge bases, DSL import/export, or its REST API."
instruction: "JEV FIRST, findable at start: run ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model; PASS continues, ESCALATE rewrites, BLOCK stops, DEFERRED fails closed. Then: run it under agentic-selfhost-docker's lifecycle, change every shipped default secret before first start, wire model providers to local endpoints only, and gate every outward step."
applies_when:
  env: "Mike's Mac, local-only; Docker runtime via Colima (see agentic-selfhost-docker)"
  runtime: "Docker Compose stack: langgenius/dify-api, dify-web, db, redis, sandbox, plugin-daemon, nginx"
  deps: "Docker + Compose 2.24.0+; 2 vCPU / 4 GiB minimum (docs size the macOS VM at 2 vCPU / 8 GiB)"
  params: "host port 4510 (lab range 4500-4599) mapped to nginx 80"
  budget: "one instance; teardown after proof"
  scale: "single tenant local instance; not HA, not multi-node"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - JEV FIRST, findable at task start: route every typed judgment to rig-s1gate (Jev) via ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model call; DEFERRED when the classifier is down, fail closed.
  - Pull the pinned compose file from the verified release and diff .env.example secrets.
  - Set EXPOSE_NGINX_PORT to a lab port and change every default secret key.
  - Bring the stack up through agentic-selfhost-docker and finish the /install admin setup.
  - Wire a model provider to a local OpenAI-compatible endpoint and probe it first.
  - Build the hello app, prove it through the API, export its DSL, and tear down.
done_when:
  - "grep:capabilities/skills/agentic-setup-dify/SKILL.md:DIFY_AGENT_SERVER_SECRET_KEY"
  - "grep:capabilities/skills/agentic-setup-dify/SKILL.md:Bearer [$]DIFY_API_KEY"
  - "grep:capabilities/skills/agentic-setup-dify/SKILL.md:Gate-D"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-dify/SKILL.md"
out_of_scope:
  - Dify Cloud signup, marketplace plugin installs that phone home, paid plans (Gate-D)
  - any paid model API key (local endpoints only)
  - production deployment or public URLs (Gate-D)
---

# agentic-setup-dify

JEV FIRST, binding on every Dify-setup decision: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; receipts are judged with `rig-s1gate check doctrine.surface`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the gate does not advance.

## Load surface

Always loaded at the start of every agentic-systems-setup task: the agentic-systems-setup family routes here before the first install, start or teardown command. It is a task-start surface, not a deep reference an agent must already know about. Typed judgments it forces: is the stack healthy; did this API call actually return the app payload; is this DSL valid; is this error BLOCKED (environment) or FAILED (it ran and failed).


## 1. When to choose it and when not

Choose Dify when the deliverable is a **user-facing LLM app platform**: visual app building (chatbot / agent / workflow / chatflow / text generator), a RAG knowledge base with a UI, app DSL portability, and a publishable REST API per app. Do not choose it when the deliverable is scheduled or event-driven batch orchestration - the two nearest alternatives are **kestra** (declarative YAML flows, cron/event triggers, namespaces - a data/ops orchestrator, not an app builder) and **langflow** (Python-native visual flows with deeper custom-component control and a lighter single-process runtime). Pick Dify over those when non-developers must edit apps and when knowledge-base RAG is central.

## 2. Current version and sources

Verified 2026-09-28:
- **Dify 1.17.1** (GitHub latest release, published 2026-09-10, from `https://api.github.com/repos/langgenius/dify/releases/latest`).
- Docs fetched today: https://docs.dify.ai/getting-started/install-self-hosted/docker-compose (requirements, /install flow, upgrade guidance) and https://docs.dify.ai/en/guides/application-publishing/developing-with-apis (API keys, first call, app-type endpoints).
- Compose file fetched today (HTTP 200): `https://raw.githubusercontent.com/langgenius/dify/1.17.1/docker/docker-compose.yaml` - image tags read from it: `langgenius/dify-api:1.17.1`, `langgenius/dify-web:1.17.1`, `langgenius/dify-sandbox:0.2.15`, `langgenius/dify-agent-local-sandbox:1.17.1`, `langgenius/dify-plugin-daemon:0.6.10-local`, `langgenius/dify-agent-backend:1.17.1`, `postgres:15-alpine`, `mysql:8.0`, `redis:6-alpine`, `nginx:latest`, `ubuntu/squid:latest`, `certbot/certbot`, `busybox:latest`.

## 3. Environment route and prerequisites

- **Docker route (primary):** via agentic-selfhost-docker (Colima + compose). BLOCKED on 2026-09-28: Colima 0.10.3 IS installed at ~/.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`.homebrew/bin/colima start --cpu 4 --memory 8` - recorded in references/proof.json.
- **Aside sandbox bash** drives the host Docker CLI; long pulls run under `nohup` with polling.
- **No pip/npm fallback exists for Dify** - it is a multi-service compose stack (api, web, db, redis, sandbox, plugin daemon, nginx). If Docker is unavailable, the skill is BLOCKED, not installable another way.
- Prerequisites (docs): CPU >= 2 cores, RAM >= 4 GiB; macOS Docker VM configured with 2 vCPU and 8 GiB; Docker Compose 2.24.0+ (this Mac has Compose v5.3.0).

## 4. Install (exact, pinned)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/dify && cd ~/.rig/agentic-lab/dify
curl -fsSL -o docker-compose.yaml https://raw.githubusercontent.com/langgenius/dify/1.17.1/docker/docker-compose.yaml
curl -fsSL -o .env.example https://raw.githubusercontent.com/langgenius/dify/1.17.1/docker/.env.example
# 1. MANDATORY first: compose exits 1 on a missing .env before it ever reaches the daemon
cp .env.example .env
# 2. rotate EVERY default secret named in .env (upstream ships difyai123456 in 3 slots and the published
#    DIFY_AGENT_SERVER_SECRET_KEY) with generated values - never printed, never committed:
grep -E "^[A-Z_]*(SECRET|PASSWORD|KEY)[A-Z_]*=.+" .env | cut -d= -f1 | while read -r k; do
  sed -i '' "s|^$k=.*|$k=$(openssl rand -hex 32)|" .env
done
# 3. EXPOSE_NGINX_PORT=4510 (lab range), then and only then:
docker compose up -d
```

Pin the release by tag (`1.17.1`) exactly as above; the compose file itself pins `langgenius/dify-api:1.17.1` etc. `nginx:latest`, `ubuntu/squid:latest` and `busybox:latest` are unpinned upstream - acceptable for a lab stack, record the digests if a receipt needs immutability.

## 5. Local-first model wiring

In Dify: **Settings -> Model Provider -> OpenAI-API-compatible** (self-hosted exposes this provider type), base URL `http://192.168.68.90:8011/v1` (LAN IP is reachable from containers; never `localhost`). Probe first: `curl -s -m 5 http://192.168.68.90:8011/v1/models`. On 2026-09-28 Local OpenAI-compatible endpoints verified ANSWERING from this sandbox on 2026-09-28: http://127.0.0.1:8771/v1 (model qwen3.8-uncensored:27b; disable thinking or the content comes back empty) and http://127.0.0.1:8657/v1 (model MiMo-V2.6-Flash-RL-MLX-4bit-MTP). The Blackwell LAN endpoints http://192.168.68.90:8011/v1 and :8111/v1 refuse (curl exit 7). Probe first: `curl -s -m 5 <base>/models`. From containers use the host LAN address of these same servers; never a paid key.

## 6. Secrets

- macOS keychain names only: `com.rig.env.OPENAI_API_KEY_LOCAL`, `com.rig.env.DIFY_SECRET_KEY`, `com.rig.env.DIFY_ADMIN_PW` - never values in transcripts or files.
- `.env.example` placeholders only in the repo/references; the working `.env` lives under `~/.rig/agentic-lab/dify/` and is never committed.
- **Change every default the compose ships with** - observed in the 1.17.1 compose file: `DIFY_AGENT_SERVER_SECRET_KEY` defaults to `MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY`, plus `SECRET_KEY`, `INIT_PASSWORD`, db passwords and `PLUGIN_AWS_SECRET_KEY`/`TENCENT_COS_SECRET_KEY`/`VOLCENGINE_TOS_SECRET_KEY` slots in `.env.example`.
- App API keys are per-app Bearer tokens created in the UI; call the API from a backend only (docs).

## 7. Hello-world

Deterministic, no model required (references/hello-app.dsl.yml holds the importable skeleton; the API proof needs only the key):

```bash
curl http://127.0.0.1:4510/v1/info -H "Authorization: Bearer [$]DIFY_API_KEY"
# expected: {"name": "...", "mode": "chat"|"workflow"|..., ...}
```

The `/v1/info` call is the docs' "fastest first call" and works for every app type. DSL export/import: export an app's DSL YAML from the app menu (Export DSL) and re-import it via Create App -> Import DSL; keep the file in references/ as the reproducible hello artifact.

## 8. Durable and production features

Knowledge bases (RAG with scoped Service API keys), workflows with iteration/error branches, agent apps with tools, app-level API keys with per-end-user `user` identity, and DSL versioning of apps. Durable state lives in the `postgres`/`mysql` and volume mounts of the compose stack - back those up before upgrade (section 12).

## 9. Observability

Compose logs per service (`docker compose logs -f api web sandbox plugin_daemon`), the built-in app logging/annotation features in the UI, and API-level receipts (`/v1/info`, app chat/message endpoints). A healthy container is activity, not completion: require an API response body as the receipt.

## 10. Testing

Deterministic test = `/v1/info` returns the app's `name`/`mode` (no model involved). **Planted failure:** revoke/regenerate the app API key and re-run the same curl - the call must go red with HTTP 401 `{"code": "unauthorized", ...}`; if it still answers 200 the check is theater. Restore by re-issuing the key. Log both runs in references/proof.json.

## 11. Deploy / self-host hardening and Gate-D

Keep `EXPOSE_NGINX_PORT` on a lab port bound to 127.0.0.1, rotate `SECRET_KEY`/`INIT_PASSWORD`/`DIFY_AGENT_SERVER_SECRET_KEY`, keep the sandbox service enabled (it executes code - do not expose it), and leave `CONSOLE_API_URL` empty for local use. **Gate-D - none of these without Mike's explicit approval:** finishing the /install admin setup is local and allowed; any Dify Cloud signup, marketplace install that downloads externally on Mike's behalf, deploy, push, paid plan, public URL or tunnel is NOT.

## 12. Teardown and upgrade

Teardown: `docker compose down` (add `-v` only for disposable lab volumes), then return Colima to its found state via agentic-selfhost-docker. Upgrade: follow the release-notes upgrade guide for the target version (docs), diff every `.env.example` against `.env` for new keys, re-apply custom compose edits onto the new file rather than keeping the old one, pull the new pinned tags, restart.

## 13. Gotchas

- Running `docker compose up -d` straight from `references/` fails with exit 1 on the **missing .env**, before it ever reaches the Docker daemon error (independent verifier, 2026-09-28) - the copy-then-rotate order in section 4 is load-bearing, not cosmetic.
- The compose file ships real upstream defaults - `difyai123456` in three `.env` slots and the published `DIFY_AGENT_SERVER_SECRET_KEY` (both verified in the fetched files, 2026-09-28) - so step 2's rotation is mandatory before first start.
- Docs require Compose **2.24.0+** and warn macOS VMs need 8 GiB even though the minimum says 4 GiB (docs page fetched 2026-09-28) - undersized VMs fail late, at sandbox/plugin services.
- Upgrade instructions are release-specific and the docs tell you to re-apply customizations onto the NEW compose file (docs, 2026-09-28) - a retained old file silently misses new services.
- Docker route BLOCKED here: Colima 0.10.3 exists under ~/.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`.

## 14. Proof receipts

| Command | Exit | Observed | Date | Proof |
|---|---|---|---|---|
| `curl .../releases/latest` (langgenius/dify) | 0 | tag 1.17.1, published 2026-09-10 | 2026-09-28 | L0 |
| `curl -o docker-compose.yaml raw.githubusercontent.com/.../1.17.1/docker/docker-compose.yaml` | 0 | HTTP 200; image tags enumerated | 2026-09-28 | L0 |
| docs.dify.ai install + API pages fetch | 0 | requirements + `/v1/info` contract | 2026-09-28 | L0 |
| `docker compose up -d` | - | BLOCKED (daemon down: Colima 0.10.3 in ~/.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. L1+ BLOCKED by the missing Docker runtime - the exact errors are in references/proof.json.
