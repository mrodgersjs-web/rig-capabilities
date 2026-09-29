---
name: agentic-setup-pydantic-ai
description: "agentic-systems-setup sub-skill: set up Pydantic AI on Mike's Mac end to end - typed agents, validated structured output, typed tools, TestModel/FunctionModel testing, and local OpenAI-compatible model wiring. Use when the ask is 'set up Pydantic AI', 'typed agent with structured output', 'wire an agent to my local model', or 'which framework fits a typed single-agent build'. Always loaded at the start of every agentic framework setup task (task-start surface, not a deep reference). JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, pydantic-ai, typed-agents, setup]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: framework-setup
  extends: "agentic-env-probe, app-sandbox-survival, provider-probe-first"
outcome: "A working Pydantic AI install in ~/.rig/agentic-lab/pydantic-ai/ with a deterministic TestModel hello-world producing validated structured output, unit tests that go red when planted, a local-endpoint run with non-empty content asserted, and proof receipts carrying real exit codes."
activation: "Load at the start of every agentic framework setup task, before the first install command, and whenever a task names Pydantic AI, pydantic-ai, typed agents, structured output from a model, or asks which framework fits a typed single-agent build; also before any Pydantic AI install, upgrade, or model-wiring step."
instruction: "Probe routes first, install into the lab venv with PYTHONHOME unset, prove the agent on TestModel before any endpoint, wire OpenAIChatModel (chat completions, not the Responses API) to a local base URL, plant one failure to prove the tests can go red, and record every command's exit code in references/proof.json."
applies_when:
  env: "Aside bash sandbox (fully works here) or an Orca host shell"
  runtime: "Python 3.12+ via uv venv"
  deps: "uv on PATH, ~/.rig/agentic-lab/pydantic-ai/.venv, a local OpenAI-compatible endpoint for L3"
  params: "model id must come from the endpoint's /models response; use the openai-chat prefix for local servers"
  budget: "one lab venv and one hello-world run per day"
  scale: "single agent, single process; durable multi-day execution needs an external engine (Gate-D to wire)"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe routes and versions, then install pydantic-ai into the lab venv.
  - Run the TestModel hello-world and prove validated structured output without network.
  - Plant one failure and prove the unit test goes red before trusting it.
  - Wire OpenAIChatModel to a local endpoint and assert non-empty content before claiming L3.
  - Send the proof verdict to JEV via rig-s1gate before any frontier model call, and fail closed.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/pydantic-ai/.venv/bin/python capabilities/skills/agentic-setup-pydantic-ai/references/hello_world_testmodel.py"
  - "grep:capabilities/skills/agentic-setup-pydantic-ai/SKILL.md:openai-chat:"
  - "grep:capabilities/skills/agentic-setup-pydantic-ai/SKILL.md:enable_thinking"
  - "file:capabilities/skills/agentic-setup-pydantic-ai/references/proof.json"
out_of_scope:
  - paid API calls, Logfire or Gateway cloud signups, or any account creation (Gate-D)
  - installing into harness roots or a project worktree instead of the lab dir
  - wiring durable engines (Temporal/DBOS/Prefect) or GitHub Agentic Workflows (Gate-D)
---

# agentic-setup-pydantic-ai

Start here when: the task names Pydantic AI, typed agents, validated structured output, or asks
which framework fits a typed single-agent build on Mike's Mac.

JEV FIRST, binding on every setup and proof decision: an agent whose only context is this excerpt
sends typed judgments ("which framework fits", "is this install correct", "did the proof pass") to
the rig-s1gate Jev path BEFORE any frontier LLM call. When the classifier is unavailable: DEFER,
never guess a verdict locally. A required signal passes only above 0.9; below that the gate does
not advance, and an advisory PASS is never permission to send, push, deploy, or spend.

## Load surface

Always loaded at the start of every agentic framework setup task: the `agentic-systems-setup`
meta-skill routes framework setup here, `agentic-setup-conductor` loads it before the first
install command, and the `agentic-setup-session` harness names it as doctrine. It is a task-start
surface, not a deep reference an agent must already know about; the long example files live in
`references/`.

## 1. When to choose it and when not

Choose Pydantic AI when the agent's outputs must be typed and validated (Pydantic models as
output_type), when tools should be plain typed functions, when dependencies should be injected
through a typed `RunContext`, or when one agent must swap models with a string (docs page
fetched today).

Do not choose it when the core problem is document ingestion and RAG over files (LlamaIndex), or
a checkpointed state graph with interrupts (LangGraph). The two nearest alternatives in this
family are **langchain** and **llamaindex**.

## 2. Current version and sources

Verified by install and import in `~/.rig/agentic-lab/pydantic-ai/.venv` on 2026-09-28:
`pydantic-ai` 2.51.0 (`pydantic-ai-slim` 2.51.0), `openai` 3.19.2, `pydantic-core` imports
cleanly in this sandbox (unlike some other native wheels).

Official docs fetched today:
- https://ai.pydantic.dev/ - overview, install (`pip install pydantic-ai`), the typed bank-support
  example (deps, tools, capabilities, structured output), and instrumentation notes.
- https://ai.pydantic.dev/docs/ai/models/openai/ - the `'openai:'` prefix resolves to the
  Responses API while `'openai-chat:'` resolves to Chat Completions; `OpenAIProvider(base_url=...,
  api_key=..., openai_client=...)`; the transport client retries with `max_retries=2` by default.

## 3. Environment route and prerequisites

- Aside sandbox: fully works here; `TestModel`, `FunctionModel`, `OpenAIProvider` all import and
  run (verified). No native-wheel blockers on this framework.
- Orca host shell: only needed for durable-engine wiring or heavier extras.
- Prerequisites: `uv` at `~/.local/bin`, `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`, and
  `env -u PYTHONHOME -u PYTHONPATH` on every uv/python call.

## 4. Install (exact commands run here)

```sh
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
LAB=~/.rig/agentic-lab/pydantic-ai
mkdir -p "$LAB"
cd "$LAB"
env -u PYTHONHOME -u PYTHONPATH uv venv .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python pydantic-ai
```

## 5. Local-first model wiring

`OpenAIProvider` reads `OPENAI_BASE_URL` and `OPENAI_API_KEY` from the environment when the
arguments are omitted, and raises if neither the argument nor the env var is present (verified in
installed `pydantic_ai/providers/openai.py`). For local OpenAI-compatible servers use the chat
completions model class, never the Responses one:

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

model = OpenAIChatModel(
    "qwen3.8-uncensored:27b",                    # from GET <base>/models
    provider=OpenAIProvider(
        base_url="http://127.0.0.1:8771/v1",
        api_key="local-not-a-secret",
    ),
)
agent = Agent(model, output_type=str,
              model_settings={"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}})
```

`ModelSettings.extra_body` is a real field in the installed `pydantic_ai/settings.py`. Local
endpoints that answer from this sandbox (probed today): `http://127.0.0.1:8771/v1`
(`qwen3.8-uncensored:27b`; disable thinking or content is empty) and `http://127.0.0.1:8657/v1`
(`MiMo-V2.6-Flash-RL-MLX-4bit-MTP`). Blackwell `192.168.68.90:8011`/`:8111` do NOT answer from
this sandbox (curl exit 7 / 28).

## 6. Secrets

Keychain item names only, never values: `com.rig.env.OPENAI_API_KEY`, and for observability
`com.rig.env.LOGFIRE_TOKEN`. Local endpoints need no secret; use `local-not-a-secret`.
`env.example` only:

```
OPENAI_BASE_URL=http://127.0.0.1:8771/v1
OPENAI_API_KEY=local-not-a-secret
LOGFIRE_TOKEN=
```

## 7. Hello-world

Full file: `references/hello_world_testmodel.py` (TestModel, validated structured output, no
network) and `references/hello_world_local.py` (OpenAIChatModel against 8771, asserts non-empty
content).

```sh
env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/pydantic-ai/.venv/bin/python \
  capabilities/skills/agentic-setup-pydantic-ai/references/hello_world_testmodel.py
```

Expected output ends with `RESULT: TESTMODEL_OK output=<validated model>` and exits 0. The local
variant prints `RESULT: <non-empty model text>`.

## 8. Durable and production features

- Conversation persistence: `result.all_messages()` is serializable and can be passed back as
  `message_history` on the next run (exercised here as the L4 receipt).
- Retries and validation repair: output validation failures prompt the model to try again (docs),
  and the transport client retries `max_retries=2` by default (docs URL above).
- Human-in-the-loop: deferred tools with approval are documented in the tool docs (docs page
  family at ai.pydantic.dev); not exercised in the lab.
- Durable execution on external engines (Temporal, DBOS, Prefect, ...) is documented at
  ai.pydantic.dev; wiring one is Gate-D scope.

## 9. Observability

Pydantic AI is OpenTelemetry-native: instrumentation emits spans for model and tool calls, with
Logfire as the easiest backend and any OTLP backend supported (docs page fetched today).
Logfire signup or sending traces to it is Gate-D. Local-first default: no tracer; the printed
run output and proof receipts are the evidence.

## 10. Testing and evals

Deterministic fake models (verified imports): `pydantic_ai.models.test.TestModel` and
`pydantic_ai.models.function.FunctionModel`. Run any agent against them with
`agent.override(model=TestModel())` so unit tests need no network and no key.
`references/test_agent.py` is assert-based and runs under the venv python.

Planted failure (run here): assert a wrong TestModel output and the test must go red with
`AssertionError`, exit 1. Keep that red run as the receipt; a suite that cannot go red is theater.

## 11. Deploy / self-host (Gate-D)

Gate-D, never done from this skill: Logfire or Gateway cloud signup, creating API keys, wiring
durable engines (Temporal/DBOS/Prefect), GitHub Agentic Workflows, `git push`, paid plans, public
URLs. Running the agent as a local CLI or localhost service is reversible and allowed; exposing
it publicly is Gate-D.

## 12. Teardown and upgrade

```sh
rm -rf ~/.rig/agentic-lab/pydantic-ai      # teardown: lab venv only
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python --upgrade pydantic-ai
```

Upgrade policy: pin the proved version, re-run the TestModel hello-world, the planted-failure
test, and one local-endpoint run before claiming the upgrade works.

## 13. Gotchas

- [docs] https://ai.pydantic.dev/docs/ai/models/openai/ - the bare `'openai:'` prefix resolves to
  OpenAIResponsesModel (the Responses API). Local OpenAI-compatible servers speak Chat
  Completions, so use `OpenAIChatModel` / `'openai-chat:'` or the model names a local server
  returns will look broken when the transport is wrong.
- [observed here] Endpoint `127.0.0.1:8771` returns HTTP 200 with empty content when thinking is
  enabled; pass `extra_body: {"chat_template_kwargs": {"enable_thinking": false}}` via
  `ModelSettings` and assert non-empty content.
- [source verified] `OpenAIProvider` raises if there is no `api_key` argument, no
  `OPENAI_API_KEY` env var, and no custom client (installed `providers/openai.py`); for a local
  server pass the placeholder `local-not-a-secret` explicitly.
- [observed here] The Aside runtime exports PYTHONHOME/PYTHONPATH; unset them for every uv/venv
  call. Contrast with other families: `pydantic-core` loads fine here even though ormsgpack and
  SQLAlchemy C extensions do not.

## 14. Proof receipts

| step | command | exit | version | date | level |
|---|---|---|---|---|---|
| install | `uv pip install pydantic-ai` | 0 | 2.51.0 | 2026-09-28 | L1 |
| testmodel hello-world | `.../.venv/bin/python references/hello_world_testmodel.py` | 0 (`RESULT: TESTMODEL_OK output= answer='a'`) | pydantic-ai 2.51.0 | 2026-09-28 | L2 |
| unit test green | `.../.venv/bin/python references/test_agent.py` | 0 (`TEST_OK`) | pydantic-ai 2.51.0 | 2026-09-28 | L2 |
| unit test red (planted) | `PLANT=1 .../.venv/bin/python references/test_agent.py` | 1 (`AssertionError: planted failure check: expected str, got Out`) | pydantic-ai 2.51.0 | 2026-09-28 | L2 |
| message history round-trip | `.../.venv/bin/python references/hello_world_persist.py` | 0 (`RESULT: HISTORY_OK turns=2 bytes=997`) | pydantic-ai 2.51.0 | 2026-09-28 | L4 |
| local endpoint run | `.../.venv/bin/python references/hello_world_local.py` | 0 (`RESULT: READY`) | pydantic-ai 2.51.0 | 2026-09-28 | L3 |

Machine-readable receipts: `references/proof.json`.
