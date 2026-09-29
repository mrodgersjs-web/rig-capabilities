---
name: agentic-setup-langflow
description: "Agentic Systems Setup: Langflow on Mike's Mac - Python-native visual agent/flow builder, installed with uv into a lab venv (or Docker), with custom components, MCP support, importable flow JSON, and a REST API (run flows, /api/v1/version). Use when Mike wants a Python-first visual builder, custom components in code, or flows that export as portable JSON. JEV-FIRST MANDATE."
when_to_use: "Langflow, visual flow, Langflow API, MCP, Python custom component, flow JSON. JEV-FIRST MANDATE: route typed judgments to rig-s1gate before any frontier model; DEFERRED when the classifier is down."
tags: [rig, agentic-systems-setup, langflow, python, uv, visual-flows, mcp]
metadata:
  family: agentic-systems-setup
  tier: framework
  siblings: "agentic-setup-dify, agentic-setup-kestra, agentic-setup-flowise, agentic-selfhost-docker"
outcome: "A Langflow instance from the lab venv answering its version API on a 45xx port, with one imported hello flow and a model component pointed at a local OpenAI-compatible endpoint (or an honest L2 stop)."
activation: "JEV-FIRST MANDATE, findable at task start: route typed judgments to rig-s1gate before any frontier model; DEFERRED is the only answer when the classifier is down. Load for any request to run, script, or extend Langflow: flows, components, MCP, flow import/export, the run API, or its uv/pip/Docker lifecycle."
instruction: "JEV FIRST, findable at start: run ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model; PASS continues, ESCALATE rewrites, BLOCK stops, DEFERRED fails closed. Then: unset PYTHONHOME/PYTHONPATH for every uv/venv command; prove the service with an HTTP receipt, not a log line."
applies_when:
  env: "Mike's Mac, local-only; Aside sandbox bash or host shell"
  runtime: "Python 3.10-3.14 (docs) in a uv venv under ~/.rig/agentic-lab/langflow; or Docker via agentic-selfhost-docker"
  deps: "uv in ~/.local/bin; 2 GB RAM min / 4 GB recommended (docs)"
  params: "host port 4500 (lab range 4500-4599); LANGFLOW env names from docs.langflow.org/deployment-docker"
  budget: "one instance; teardown after proof"
  scale: "single-user local; not a multi-tenant deployment"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - JEV FIRST, findable at task start: route every typed judgment to rig-s1gate (Jev) via ./bin/rig-s1gate check doctrine.surface BEFORE any frontier model call; DEFERRED when the classifier is down, fail closed.
  - Pin the Langflow version from PyPI and install into a uv venv with PYTHONHOME/PYTHONPATH unset.
  - Start the server on a lab port and poll until /api/v1/version answers (imports are slow).
  - Import the hello flow JSON and run it deterministically through the API.
  - Wire a model component to a local OpenAI-compatible endpoint (or record BLOCKED at L2).
  - Stop the server via lsof kill and archive the lab dir state.
done_when:
  - "grep:capabilities/skills/agentic-setup-langflow/SKILL.md:langflow==1.12.3"
  - "grep:capabilities/skills/agentic-setup-langflow/SKILL.md:env -u PYTHONHOME -u PYTHONPATH"
  - "grep:capabilities/skills/agentic-setup-langflow/SKILL.md:Gate-D"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/agentic-setup-langflow/SKILL.md"
out_of_scope:
  - Langflow Cloud / DataStax signup, paid plans (Gate-D)
  - paid model API keys (local endpoints only)
  - production deploys (K8s), public URLs, tunnels (Gate-D)
---

# agentic-setup-langflow

JEV FIRST, binding on every Langflow-setup decision: an agent whose only context is this excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM call; receipts are judged with `rig-s1gate check doctrine.surface`. When the classifier is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below that the gate does not advance.

## Load surface

Always loaded at the start of every agentic-systems-setup task: the agentic-systems-setup family routes here before the first install, start or teardown command. It is a task-start surface, not a deep reference an agent must already know about. Typed judgments it forces: is the service really up (HTTP body, not a log line); did this flow run return the expected output; is this a slow import or a dead process; is this error BLOCKED (environment) or FAILED (it ran and failed).


## 1. When to choose it and when not

Choose Langflow when the deliverable is a **Python-first visual flow**: custom components written in Python, MCP server/client support, flows exported as portable JSON, and a REST API to run them. Do not choose it for declarative YAML batch orchestration with cron/webhook triggers - the two nearest alternatives are **kestra** (YAML flows, namespaces, schedules) and **flowise** (JS-based visual builder with embeddable chat). Pick Langflow over those when Python custom components or MCP are the point.

## 2. Current version and sources

Verified 2026-09-28:
- **Langflow 1.12.3** (PyPI `https://pypi.org/pypi/langflow/json`, fetched today).
- Docs fetched today: https://docs.langflow.org/get-started-installation - Python **3.10-3.14**, `uv` recommended, min dual-core CPU + 2 GB RAM (recommended multi-core + 4 GB), start with `uv run langflow run`, default URL `http://127.0.0.1:7860`, Docker image `langflowai/langflow:latest` with `LANGFLOW_AUTO_LOGIN=false` default and `LANGFLOW_SUPERUSER_PASSWORD`, upgrade via `uv pip install langflow -U`, install a pinned version with `uv pip install langflow==X.Y.Z`.
- API surface verified today (https://docs.langflow.org/api): `GET /api/v1/version`, a webhook run-flow endpoint, and a Model Provider Policy API.

## 3. Environment route and prerequisites

- **pip/uv route (primary here):** `env -u PYTHONHOME -u PYTHONPATH uv venv .venv` then `uv pip install --python .venv/bin/python langflow==1.12.3`. The Aside runtime exports PYTHONHOME/PYTHONPATH - always unset them (environment fact, verified 2026-09-28).
- **Docker route:** `langflowai/langflow:latest` via agentic-selfhost-docker (BLOCKED here: Colima 0.10.3 in ~/.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.CORRECTED (verified 2026-09-28 14:45): lima 2.1.3 IS installed at ~/.homebrew/bin/lima (`PATH="$HOME/.homebrew/bin:$PATH" ~/.homebrew/bin/lima --version` -> `limactl version 2.1.3`); Colima's "lima not found" was a PATH artifact - the fix is PATH, never `brew install lima`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`. With PATH set, `colima status` -> `time="2026-09-28T14:45:39-06:00" level=fatal msg="colima is not running"`.
- Prerequisites (docs): Python 3.10-3.14, 2 GB RAM min / 4 GB recommended. Cold imports are slow ("It can take a few minutes for Langflow to start" - docs).

## 4. Install (exact, pinned)

```bash
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/langflow && cd ~/.rig/agentic-lab/langflow
env -u PYTHONHOME -u PYTHONPATH uv venv .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python langflow==1.12.3
env -u PYTHONHOME -u PYTHONPATH .venv/bin/langflow run --host 127.0.0.1 --port 4500
```

Pinned `langflow==1.12.3` (verified on PyPI today). Installed here on CPython 3.14.0 with exit 0 (receipt in references/proof.json).

## 5. Local-first model wiring

Model components (the OpenAI-family components) take a provider credential plus a base-URL input pointing at `http://192.168.68.90:8011/v1` (LAN IP from containers; probe `curl -s -m 5 <base>/models` first). Verify the exact input name against docs.langflow.org's model-component reference at use time - do not write a flag you have not seen. On 2026-09-28 Local OpenAI-compatible endpoints verified ANSWERING from this sandbox on 2026-09-28: http://127.0.0.1:8771/v1 (model qwen3.8-uncensored:27b; disable thinking or the content comes back empty) and http://127.0.0.1:8657/v1 (model MiMo-V2.6-Flash-RL-MLX-4bit-MTP). The Blackwell LAN endpoints http://192.168.68.90:8011/v1 and :8111/v1 refuse (curl exit 7). Probe first: `curl -s -m 5 <base>/models`. From containers use the host LAN address of these same servers; never a paid key.

## 6. Secrets

Langflow's own auth env names seen in fetched docs: `LANGFLOW_AUTO_LOGIN`, `LANGFLOW_SUPERUSER_PASSWORD` (Docker images default `LANGFLOW_AUTO_LOGIN=false`); other names come from docs.langflow.org/deployment-docker - copy them from there, never invent. Keychain: `com.rig.env.OPENAI_API_KEY_LOCAL`, `com.rig.env.LANGFLOW_SUPERUSER_PW`. `.env.example` placeholders only; change every default password before any non-loopback bind.

## 7. Hello-world

Two receipts: (a) `curl -s http://127.0.0.1:4500/api/v1/version` -> JSON version payload; (b) import references/hello-flow.json (a Chat Input -> Chat Output pass-through with a constant Text, no model) via the UI's import or `POST /api/v1/flows/`, then run it via the run-flow API and assert the deterministic output string. If (b)'s exact endpoint shape differs, read the OpenAPI at `/openapi.json` on the running instance and use it - record what you actually called.

## 8. Durable and production features

Flow import/export as JSON (portable artifacts in references/), custom Python components, MCP server support, per-flow API access, and the Model Provider Policy API. Flows persist in Langflow's local database under its config dir - back it up before upgrades.

## 9. Observability

Server log via nohup capture, `/api/v1/version` as a liveness probe, and the API's run responses. A logged startup line is activity, not completion - require an HTTP body.

## 10. Testing

Deterministic test = run the constant-output hello flow and assert the exact string (no model). **Planted failure:** POST the run API with a nonexistent flow id - it must return 404/422; if it returns 200 the test is theater. Record both receipts.

## 11. Deploy / self-host hardening and Gate-D

Bind 127.0.0.1 only, set `LANGFLOW_AUTO_LOGIN=false` with a rotated superuser password for anything shared, and keep venvs under the lab dir. **Gate-D (never without Mike's explicit approval):** Langflow Cloud signup, deploys, pushes, paid plans, public URLs/tunnels.

## 12. Teardown and upgrade

Stop: `lsof -t -i :4500 | xargs kill`; confirm closed (curl exit 7). Upgrade: back up the config dir, `uv pip install --python .venv/bin/python langflow==<new> -U` after reading release notes (docs advise backup first), re-run the hello receipts.

## 13. Gotchas

- The Aside runtime exports PYTHONHOME/PYTHONPATH and they break other Pythons (observed environment fact) - every uv/venv command needs `env -u PYTHONHOME -u PYTHONPATH`.
- Cold start is genuinely slow (docs: "a few minutes"); an empty log file plus an unopened port is NOT proof of death - find the pid with `lsof -t <logfile>` before declaring failure (observed here: pid alive and still importing after 5+ minutes).
- Docs 1.12 package migration: `langflow-base` is now the runnable base and both packages expose the `langflow` command (docs, 2026-09-28) - do not look for a `langflow-base` executable.
- `docs.langflow.org/installation` and `/getting-started/installation` both 404; the live path is `/get-started-installation` (observed here 2026-09-28).

## 14. Proof receipts

| Command | Exit | Observed | Date | Proof |
|---|---|---|---|---|
| `curl https://pypi.org/pypi/langflow/json` | 0 | latest 1.12.3 | 2026-09-28 | L0 |
| docs.langflow.org/get-started-installation fetch | 0 | Py 3.10-3.14, 2/4 GB, uv route, :7860 | 2026-09-28 | L0 |
| `env -u PYTHONHOME -u PYTHONPATH uv venv .venv && uv pip install ... langflow==1.12.3` | 0 | INSTALL_EXIT=0 on CPython 3.14.0 | 2026-09-28 | L1 |
| `.venv/bin/langflow run --host 127.0.0.1 --port 4500` | see proof.json | startup status + API receipt recorded there | 2026-09-28 | up to L2 |
