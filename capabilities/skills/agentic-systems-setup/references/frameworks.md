# Framework coverage for agentic-systems-setup (2026-09-28, finalized after workers A1-A5 landed)

Each covered framework has one main-tier skill `agentic-setup-<slug>` that owns its install,
model wiring, hello, durable or observed feature, tests, and deploy path, and climbs the proof
ladder in `agentic-proof-ladder`. All 20 landed on 2026-09-28; "Proven here" is the level each
worker's receipt (`references/proof.json` in the skill) reached on this Mac, and
`validate_hierarchy.py --strict` resolves every one.

## Covered

| Framework | Skill | Lane | Language | Default route here | Worker | Status |
|---|---|---|---|---|---|---|
| LangChain + LangGraph + LangSmith | `agentic-setup-langchain` | agent-framework | Python, JS | sandbox (uv) | A1 | landed; proven L3 |
| LlamaIndex | `agentic-setup-llamaindex` | agent-framework | Python, TS | sandbox (uv) | A1 | landed; proven L2 narrow |
| Pydantic AI | `agentic-setup-pydantic-ai` | agent-framework | Python | sandbox (uv) | A1 | landed; proven L4 |
| CrewAI | `agentic-setup-crewai` | agent-framework | Python | sandbox (uv) | A2 | landed; proven L3 |
| OpenAI Agents SDK | `agentic-setup-openai-agents-sdk` | agent-framework | Python, TS | sandbox (uv) | A2 | landed; proven L1 |
| Google ADK | `agentic-setup-google-adk` | agent-framework | Python, Java | sandbox (uv); cloud is Gate-D | A2 | landed; proven L3 |
| Microsoft Agent Framework | `agentic-setup-microsoft-agent-framework` | agent-framework | Python, .NET | sandbox (uv) | A2 | landed; proven L3 |
| Prefect | `agentic-setup-prefect` | durable-workflow | Python | sandbox (uv) | A3 | landed; proven L4 |
| Temporal | `agentic-setup-temporal` | durable-workflow | Python, TS, Go, Java | CLI 1.7.2 in ~/.homebrew/bin; own dev server on fresh ports (Mike's :7233 is off-limits) | A3 | landed; proven L1 + L2 logic |
| Dagster | `agentic-setup-dagster` | data-pipeline | Python | sandbox (uv) | A3 | landed; proven L2 + L4 |
| Apache Airflow | `agentic-setup-airflow` | data-pipeline | Python | host shell or Docker | A3 | landed; proven L1 + L2 logic |
| Trigger.dev | `agentic-setup-trigger-dev` | durable-workflow | TypeScript | sandbox (pnpm); signup is Gate-D | A4 | landed; proven L3 |
| Inngest | `agentic-setup-inngest` | durable-workflow | TypeScript, Python, Go | sandbox (pnpm) | A4 | landed; proven L3 |
| Mastra | `agentic-setup-mastra` | agent-framework | TypeScript | sandbox (pnpm) | A4 | landed; proven L3 |
| n8n | `agentic-setup-n8n` | low-code-platform | TypeScript app | n8n 2.33.3 in ~/.local/bin; native deps need host shell | A4 | landed; proven L2 + L4 |
| Dify | `agentic-setup-dify` | low-code-platform | platform | Docker (Colima 0.10.3 installed, not running; needs ~/.homebrew/bin on PATH) | A5 | landed; proven L0 |
| Kestra | `agentic-setup-kestra` | durable-workflow | platform (JVM) | JDK 25+ (openjdk@26 keg-only) or Docker | A5 | landed; proven L1 |
| Flowise | `agentic-setup-flowise` | low-code-platform | platform (Node) | Docker or host shell | A5 | landed; proven L1 |
| Langflow | `agentic-setup-langflow` | low-code-platform | platform (Python) | sandbox (uv) or Docker | A5 | landed; proven L1 |
| Docker/Colima self-hosting (sub-skill) | `agentic-selfhost-docker` | cross-cutting | - | Colima 0.10.3 installed, not running | A5 | landed; proven L1 |

Existing estate skills that keep their narrower roles: `tool-langchain`, `tool-langgraph`,
`tool-temporal`, `tool-mastra` (Design Harness carriers), `tg-durable-ai-pipelines` (App Studio),
`autonomous-ai-agents` (coding-agent router). `docker-agentic-stack` (Hermes) was found archived at
`~/.hermes/skills/.archive/docker-agentic-stack` on 2026-09-28; `agentic-selfhost-docker` owns that
role now.

## Named candidates not yet covered

Named so a request for them routes to "no skill yet, write one with the protocol" instead of a
guess. None was installed or verified today; each needs L0 docs before any command is written.

| Candidate | Why it could earn a skill | Nearest covered choice meanwhile |
|---|---|---|
| Letta | stateful agents with long-term memory as a server | LangGraph with a checkpointer and store |
| Agno | lightweight Python agents and teams | Pydantic AI or CrewAI |
| smolagents (Hugging Face) | code-writing agents, minimal abstraction | plain code baseline or Pydantic AI |
| DSPy | programming and optimizing prompts as modules | plain code plus rig-s1gate rubrics |
| Haystack | production RAG and agent pipelines | LlamaIndex |
| DBOS | durable execution on Postgres, library not server | Temporal or Prefect |
| Restate | durable execution with virtual objects | Temporal |
| Hatchet | durable task queue on Postgres | Trigger.dev or Inngest |
| Windmill | scripts to workflows and internal apps platform | n8n or Kestra |
| Vercel AI SDK agents | TypeScript agent loop inside Next.js apps | Mastra |
| AWS Strands Agents | model-driven agents on AWS | OpenAI Agents SDK |
| AutoGen, Semantic Kernel (legacy) | existing code bases only | Microsoft Agent Framework |

## How the matrix was built

Sources and quotes: `references/grounding.md` (Anthropic building-effective-agents, LangGraph,
CrewAI, Prefect, 12-factor agents, Kestra, Dify, Trigger.dev quickstarts, all fetched
2026-09-28). The first row is always "no framework": G1's advice to find the simplest solution,
proven locally by `hello_baseline.py` (L3 on 2026-09-28).
