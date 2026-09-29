# agentic-systems-setup inventory (2026-09-28, finalized)

Machine-readable twin: `inventory.json`. Org chart: `../hierarchy.json`.

## New in this family

- Meta skill: `agentic-systems-setup` (selection matrix, protocol E1-E8, proof ladder, Gate-D table).
- Sub-skills: `agentic-env-probe`, `agentic-local-models`, `agentic-secrets`, `agentic-proof-ladder`,
  `agentic-durable-execution`, `agentic-observability`, `agentic-testing-evals`,
  `agentic-mcp-integration`, `agentic-deploy-gate`; `agentic-selfhost-docker` (self-host lane, A5).
- Tools (stdlib, run 2026-09-28): `env_probe.py`, `probe_endpoint.py`, `fake_openai_server.py`,
  `leak_scan.py`, `proof_ladder.py`, `hello_baseline.py`.
- Agents: `agentic-setup-conductor` (meta), `agentic-env-prober`, `agentic-proof-runner`,
  `agentic-docs-verifier`.
- Harness `agentic-setup-session.yaml` (E1-E8), loop `agentic-setup-proof-loop.md`,
  JEV rubric `agentic.setup` with good and bad fixtures, lesson ledger AS-01 to AS-10.

## Existing skills reused (role unchanged)

| Skill | Role it keeps |
|---|---|
| tool-langchain | langchain-core primitives in the Design Harness venv |
| tool-langgraph | graph-shaped Design Harness slices |
| tool-mastra | verifying the installed Mastra CLI |
| tool-temporal | Temporal Python workflows for Design Harness runtimes |
| tg-durable-ai-pipelines | durable AI pipelines inside App Studio builds |
| autonomous-ai-agents | router for autonomous coding agents, not frameworks |
| app-sandbox-survival | Aside sandbox build and process rules |

## Framework skills (landed 2026-09-28; level proven on this Mac)

A1: agentic-setup-langchain (L3), agentic-setup-llamaindex (L2 narrow), agentic-setup-pydantic-ai (L4).
A2: agentic-setup-crewai (L3), agentic-setup-openai-agents-sdk (L1), agentic-setup-google-adk (L3),
agentic-setup-microsoft-agent-framework (L3).
A3: agentic-setup-prefect (L4), agentic-setup-temporal (L1 + L2 logic), agentic-setup-dagster (L2 + L4),
agentic-setup-airflow (L1 + L2 logic).
A4: agentic-setup-trigger-dev (L3), agentic-setup-inngest (L3), agentic-setup-mastra (L3), agentic-setup-n8n (L2 + L4).
A5: agentic-setup-dify (L0), agentic-setup-kestra (L1), agentic-setup-flowise (L1), agentic-setup-langflow (L1),
plus sub-skill agentic-selfhost-docker (L1).

## Retired from this family

`docker-agentic-stack` (Hermes): archived to `~/.hermes/skills/.archive/docker-agentic-stack` by
2026-09-28 14:35; `agentic-selfhost-docker` owns Docker and Colima self-hosting.

## Lessons

Active: `lessons.jsonl` AS-01 to AS-13. Candidates: `lessons-candidates.jsonl` AS-14 to AS-18.
