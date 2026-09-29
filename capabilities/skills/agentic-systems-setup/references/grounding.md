# Grounding for agentic-systems-setup (fetched 2026-09-28)

Every page below was fetched on 2026-09-28 (~09:15 MDT) with `docgrep.py` (urllib GET, tags
stripped). `sha` is the first 12 hex of sha256 over the stripped text; re-fetch and compare to
detect drift. Quotes are verbatim from that text.

| Id | Source | http | sha | Quote |
|---|---|---|---|---|
| G1 | https://www.anthropic.com/engineering/building-effective-agents | 200 | 89870adf27e0 | "we recommend finding the simplest solution possible, and only increasing complexity when needed. This might mean not building agentic systems at all." / "Workflows are systems where LLMs and tools are orchestrated through predefined code paths. Agents, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage" / "they often create extra layers of abstraction that can obscure the underlying prompts and responses, making them harder to debug" |
| G2 | https://docs.langchain.com/oss/python/langgraph/overview | 200 | ed80d7c822bd | "LangGraph is a low-level orchestration framework and runtime for building, managing, and deploying long-running, stateful agents." / "durable execution, streaming, human-in-the-loop, and more" |
| G3 | https://docs.crewai.com/en/introduction | 200 | 73f8788bfc6c | "Flows provide: State Management : Persist data across steps and executions. Event-Driven Execution" / "Crews are teams of autonomous agents that collaborate to solve specific tasks delegated to them by the Flow." |
| G4 | https://docs.prefect.io/v3/get-started/index | 200 | b39bf9481d23 | "Robust state management that tracks success, failure, and retry states. Resume interrupted runs from the last successful point, and cache expensive computations to avoid unnecessary rework." |
| G5 | https://github.com/humanlayer/12-factor-agents | 200 | 6d71b98c1182 | "Factor 8: Own your control flow" / "Factor 10: Small, Focused Agents" / "Factor 12: Make your agent a stateless reducer" |
| G6a | https://kestra.io/docs/getting-started/quickstart | 200 | 227274c3618a | "start Kestra with a single command: docker run --pull=always --rm -it -p 8080:8080 --user=root ... kestra/kestra:latest-slim server local" |
| G6b | https://docs.dify.ai/en/getting-started/install-self-hosted/docker-compose | 200 | ac3c0061d500 | "CPU >= 2 Core RAM >= 4 GiB" / "Docker Desktop with Docker Compose 2.24.0+" / "docker compose up -d" (7 core services plus 8 dependent components) |
| G6c | https://trigger.dev/docs/quick-start | 200 | d73d176e14c8 | "trigger.dev to sign up. Wait for me to confirm. 2. Run `npx trigger.dev@latest init` in the project root." |

## How others structure selection and setup (what this family copies)

- Start from plain code and add a framework only when the job needs what it owns (G1). The
  selection matrix's first row is "no framework", and `hello_baseline.py` is the baseline.
- Separate workflow (predefined paths) from agent (model-directed) and keep control flow in your
  code (G1, G5). The matrix splits agent frameworks from durable orchestrators for that reason.
- Durability is a runtime property, not a prompt property: LangGraph checkpoints, Prefect state
  and resume, Temporal histories (G2, G4). L4 asks for a feature exercised, not described.
- Vendor quickstarts front-load signup (G6c) and heavy Docker stacks (G6a, G6b); the Gate-D
  table and the Docker route check exist because of that.

Re-verify: `agentic-docs-verifier` re-fetches each URL, recomputes the sha, and flags drift.
