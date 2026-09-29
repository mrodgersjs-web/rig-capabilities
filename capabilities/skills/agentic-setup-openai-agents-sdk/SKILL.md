---
name: agentic-setup-openai-agents-sdk
description: "agentic-systems-setup family, one skill per framework: install and run the Python OpenAI Agents SDK (openai-agents) end to end on Mike's Mac - uv venv in ~/.rig/agentic-lab, local-first model wiring via OpenAIChatCompletionsModel with a custom AsyncOpenAI client pointed at Mike's own endpoints (no paid keys), default tracing disabled, hello-world proven with a deterministic fake Model, and proof claims limited to executed rungs. JEV-FIRST MANDATE: send typed judgments like 'which framework fits' or 'did the proof pass' to rig-s1gate before any frontier model call, and fail closed. Always-loaded task-start surface, not a deep reference: start here when installing, upgrading, or debugging openai-agents (Python) agents, Runner, handoffs, or guardrails on this Mac."
tags: [rig, agentic-systems, sub-skill, openai-agents, agents, python, setup]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: framework-setup
  extends: "agentic-env-probe, agentic-local-models, agentic-secrets, agentic-observability, agentic-proof-ladder"
outcome: "An openai-agents agent that runs on Mike's Mac against a deterministic fake Model (L2) and, when a local endpoint answers, a local model through a custom OpenAI-compatible client (L3), with tracing off by default, secrets in the keychain, and a receipts table that claims no rung it did not execute."
activation: "Always loaded at the start of any task that names the OpenAI Agents SDK, agents.Runner, Agent/Runner/handoff/guardrail, or openai-agents, and before choosing among the agentic-systems-setup framework skills."
instruction: "Probe the environment first (agentic-env-probe), install into ~/.rig/agentic-lab/openai-agents-sdk with PYTHONHOME unset, wrap a local endpoint in AsyncOpenAI + OpenAIChatCompletionsModel, disable tracing before any non-OpenAI run, prove with a fake Model first, and send every typed judgment to rig-s1gate before a frontier model."
applies_when:
  env: "Aside bash sandbox or Orca host shell on Mike's Mac; uv at ~/.local/bin/uv"
  runtime: "Python 3.10+ (openai-agents requires >=3.10)"
  deps: "openai-agents==0.22.3 (verified 2026-09-28 via PyPI JSON); uv venv in ~/.rig/agentic-lab/openai-agents-sdk"
  params: "OpenAIChatCompletionsModel(model=<id>, openai_client=AsyncOpenAI(base_url=..., api_key=...))"
  budget: "one agent run per proof; installs never land in a repo"
  scale: "single Mac; hosted deployment is Gate-D"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the environment and the local model routes before the first install command.
  - Create the lab venv with PYTHONHOME and PYTHONPATH unset and install the pinned version.
  - Wire a local OpenAI-compatible endpoint through AsyncOpenAI(base_url) + OpenAIChatCompletionsModel.
  - Disable tracing (OPENAI_AGENTS_DISABLE_TRACING / set_tracing_disabled) for every non-OpenAI run.
  - Prove with a deterministic FakeModel first (L2), then a local endpoint (L3) asserting non-empty content.
  - Judge typed calls through rig-s1gate and fail closed.
done_when:
  - "grep:capabilities/skills/agentic-setup-openai-agents-sdk/SKILL.md:FAKE_MODEL_OK"
  - "grep:capabilities/skills/agentic-setup-openai-agents-sdk/SKILL.md:OPENAI_AGENTS_DISABLE_TRACING"
  - "grep:capabilities/skills/agentic-setup-openai-agents-sdk/SKILL.md:Planted failure"
  - "file:capabilities/skills/agentic-setup-openai-agents-sdk/references/proof.json"
out_of_scope:
  - platform.openai.com signups, paid API calls, or the hosted Traces dashboard (Gate-D)
  - installing into a git repo or a harness root (the lab dir is ~/.rig/agentic-lab/openai-agents-sdk)
  - the JavaScript package beyond a pointer (this skill covers the Python SDK)
---

# agentic-setup-openai-agents-sdk

Start here when: the task names the OpenAI Agents SDK (Python `openai-agents`) and you must
install, wire, or prove it on this Mac. Always-loaded task-start surface: this file opens every
Agents SDK setup task.

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM
call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a local
guess. Typed judgments in this skill ("which framework fits this task", "did the proof pass",
"is this run production-ready") go to `./bin/rig-s1gate check doctrine.surface` or the runtime
rubric before any frontier model. A required signal passes only above 0.9; below that the step
does not advance.

## Load surface

Always loaded at the START of every Agents SDK setup task: the `agentic-systems-setup` family
routes here before the first setup action. It is a task-start surface, not a deep reference an
agent must already know about. Sibling skills own shared machinery:
`agentic-env-probe`, `agentic-local-models`, `agentic-secrets`, `agentic-observability`,
`agentic-proof-ladder`. Read those instead of duplicating them here.

## 1. When to choose it, and when not

Choose the OpenAI Agents SDK when the deliverable is a **lightweight Python agent loop**: one agent
(or a small handoff graph) with tools, typed outputs, guardrails and sessions, with the smallest
possible abstraction over a model call - the SDK's core is `Agent`, `Runner`, `handoff`,
`function_tool`, and a `Model` interface you can swap.

Do **not** choose it when:

- The ask is a typed, schema-first agent with heavy validation ergonomics - that is `pydantic-ai`
  (nearest alternative 1) or a LangChain/LlamaIndex pipeline.
- The ask is a role-playing multi-agent crew with backstories and declarative YAML - that is
  `crewai` (nearest alternative 2).
- The ask is graph workflows with enterprise middleware on Microsoft infra - `microsoft-agent-framework`;
  Google-cloud-native agent platform - `google-adk`; durable jobs - Temporal/Prefect/Dagster/Airflow/
  Trigger.dev/Inngest/Kestra; low-code - n8n/Dify/Flowise/Langflow; TypeScript - Mastra.

Nearest alternatives in this family: **pydantic-ai** and **crewai**.

## 2. Current version and sources (fetched 2026-09-28)

| Source | URL | Verified |
| --- | --- | --- |
| PyPI JSON API | `https://pypi.org/pypi/openai-agents/json` | `0.22.3`, requires_python `>=3.10` |
| Models docs | `https://openai.github.io/openai-agents-python/models/` | `OpenAIResponsesModel` (default path) and `OpenAIChatCompletionsModel`; custom endpoint via `set_default_openai_client`, `ModelProvider`, or `Agent.model`; sample: `AsyncOpenAI(api_key=..., base_url=...)` + `OpenAIChatCompletionsModel(model=..., openai_client=client)` + `set_tracing_disabled(True)` |
| Tracing docs | `https://openai.github.io/openai-agents-python/tracing/` | tracing ON by default; disable with `OPENAI_AGENTS_DISABLE_TRACING=1`, `set_tracing_disabled(True)`, or `RunConfig.tracing_disabled` |
| npm registry | `https://registry.npmjs.org/@openai/agents` | separate JS package `@openai/agents` latest `0.18.0` (not covered by this skill) |

Pinned version: **openai-agents==0.22.3**. Note the JS package: `@openai/agents` (npm, 0.18.0 as of
2026-09-28) is the TypeScript sibling with its own API surface; this skill covers Python only.

## 3. Environment route and prerequisites

- Route: Aside sandbox works for install and fake-model runs (L1/L2); L3 needs sandbox network
  reachability to the endpoint. Docker/GUI work goes to the Orca host shell (`agentic-env-probe`).
- Prefix `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`; run python as
  `env -u PYTHONHOME -u PYTHONPATH <venv>/bin/python ...`.
- Prereqs: `uv`, Python 3.10+ (use `~/.local/bin/python3.12`). No Docker, no JVM.
- Install location `~/.rig/agentic-lab/openai-agents-sdk/`, never inside a repo.

## 4. Install (exact commands)

```sh
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/openai-agents-sdk && cd ~/.rig/agentic-lab/openai-agents-sdk
env -u PYTHONHOME -u PYTHONPATH uv venv --python 3.12 .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python openai-agents==0.22.3
.venv/bin/python -c "import agents; print(agents.__version__)"
```

If a native `.so` fails `code signature ... not valid for use in process: library load disallowed
by system policy` (observed here on `_cffi_backend`/cryptography during an SDK import): try once
`xattr -cr .venv` and `codesign --force -s - <file.so>`; if still blocked, record
**BLOCKED (sandbox library validation)** with the exact error and prove from the Orca host shell.

## 5. Local-first model wiring (no paid keys)

The docs' custom-endpoint pattern (models page, "Non-OpenAI models"):

```python
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled

set_tracing_disabled(disabled=True)   # docs: recommended when no platform.openai.com key exists

client = AsyncOpenAI(
    api_key="local-not-a-secret",
    base_url="http://127.0.0.1:8771/v1",       # probe first: curl -s -m 5 <base>/models
)
model = OpenAIChatCompletionsModel(
    model="qwen3.8-uncensored:27b",            # exactly an id from /v1/models
    openai_client=client,
)
agent = Agent(name="LocalAgent", instructions="You are a local assistant.", model=model)
```

Global alternative (same page): `set_default_openai_client(AsyncOpenAI(base_url=..., api_key=...))`.
Per-run alternative: a `ModelProvider` passed in `RunConfig`.

Mike's local endpoints as of 2026-09-28: `http://127.0.0.1:8771/v1` (model
`qwen3.8-uncensored:27b` - with thinking enabled it returns HTTP 200 with EMPTY content; disable
thinking via `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` - `ModelSettings`
carries `extra_body` and `extra_args` fields, verified in `agents/model_settings.py`) and
`http://127.0.0.1:8657/v1` (model `MiMo-V2.6-Flash-RL-MLX-4bit-MTP`). Blackwell LAN endpoints
`192.168.68.90:8011/:8111` do NOT answer from this sandbox. Assert non-empty content on every run.

## 6. Secrets

- Keychain names only: `com.rig.env.OPENAI_API_KEY` (`agentic-secrets`). A local endpoint takes any
  placeholder `api_key`.
- `.env.example`: `OPENAI_API_KEY=<from com.rig.env.OPENAI_API_KEY>`, `OPENAI_BASE_URL=http://127.0.0.1:8771/v1`.
- Never commit keys; never print values.

## 7. Hello-world (deterministic, no network)

File: `hello_agents.py` (also under `~/.rig/agentic-lab/openai-agents-sdk/run/`):

```python
"""OpenAI Agents SDK hello-world with a deterministic fake Model. No network, no API keys."""
import asyncio, os
os.environ.setdefault("OPENAI_AGENTS_DISABLE_TRACING", "1")

from typing import AsyncIterator
from agents import Agent, Runner, set_tracing_disabled
from agents.items import ModelResponse, TResponseStreamEvent
from agents.models.interface import Model
from agents.usage import Usage


class FakeModel(Model):
    """Deterministic Model implementation (the SDK's custom-model seam)."""

    async def get_response(self, system_instructions, input, model_settings, tools,
                           output_schema, handoffs, tracing, *,
                           previous_response_id, conversation_id, prompt) -> ModelResponse:
        return ModelResponse(
            output=[{
                "type": "message", "role": "assistant", "status": "completed",
                "content": [{"type": "output_text", "text": "FAKE_MODEL_OK: hello from the fake model"}],
            }],
            usage=Usage(),
            response_id="fake-response-1",
        )

    def stream_response(self, *args, **kwargs) -> AsyncIterator[TResponseStreamEvent]:
        async def _gen():
            return
            yield  # pragma: no cover - makes this an async generator
        return _gen()


async def main():
    set_tracing_disabled(True)
    agent = Agent(name="HelloAgent",
                  instructions="You are a helpful assistant. Reply with one short line.",
                  model=FakeModel())
    result = await Runner.run(agent, "Say hello to RIG.")
    out = str(result.final_output).strip()
    print(out)
    assert "FAKE_MODEL_OK" in out, f"fake model output missing marker: {out!r}"
    print("HELLO_AGENTS_GREEN")


if __name__ == "__main__":
    asyncio.run(main())
```

```sh
cd ~/.rig/agentic-lab/openai-agents-sdk/run
env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python hello_agents.py
# -> FAKE_MODEL_OK: hello from the fake model
# -> HELLO_AGENTS_GREEN   (exit 0)
```

## 8. Durable and production features

- Handoffs, `@function_tool`, guardrails, sessions/memory, structured outputs
  (`Agent(output_type=...)`), `Runner.run_streamed`, and `RunConfig` for per-run model/tracing control.
- `flush_traces()` matters for long-running workers when tracing is deliberately enabled (docs).
- Approval-gated function tools exist for dangerous calls; keep outward actions behind Gate-D anyway.

## 9. Observability (and turning off phone-home)

Tracing is **enabled by default** and exports to OpenAI's backend (docs). For any run without a
platform.openai.com key - i.e. all local runs here - the docs recommend disabling tracing:

```sh
export OPENAI_AGENTS_DISABLE_TRACING=1      # or set_tracing_disabled(True) in code
```

Per-run: `RunConfig(tracing_disabled=True)`/tracing config. Sensitive-data capture
(`trace_include_sensitive_data`) defaults to True when tracing is on. To keep tracing, use
`set_trace_processors([...])` with a local processor instead of the default OpenAI exporter; a
hosted tracing backend is Gate-D.

## 10. Testing and evals (one planted failure that goes red)

- Test seam: subclass `agents.models.interface.Model` (abstract `get_response` + `stream_response`)
  and assert on `result.final_output` content, never on "did not throw".
- **Planted failure**: run the same assertion with a FakeModel returning `"WRONG"`; the
  `assert "FAKE_MODEL_OK" in out` check must go RED. Record red, restore, re-run GREEN, keep the
  degraded model as a regression fixture (`test_planted_failure` asserts `AssertionError`).
- Keep tracing disabled during tests so red means the code, not the network.

## 11. Deploy / self-host (Gate-D)

Running `Runner` locally on Mike's Mac is fine. **Gate-D, do not do without Mike's explicit
approval:** platform.openai.com signup or login, API key creation, enabling the hosted Traces
dashboard, any paid plan, any deploy/push/public URL. `agentic-deploy-gate` owns the checklist.

## 12. Teardown and upgrade

```sh
rm -rf ~/.rig/agentic-lab/openai-agents-sdk/.venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U openai-agents==<new-pin>
.venv/bin/python -c "import agents; print(agents.__version__)"
```

Note from the project's release notes: minor releases can change the default model (0.20.0 made
`gpt-5.6-luna` the default) and MCP dependency majors (MCP v1/v2 support in 0.20.0); re-run the
fake-model hello-world after every upgrade.

## 13. Gotchas (each tagged with where observed)

- **Tracing phones home by default**; without a key the exporter still runs - disable it.
  [docs: https://openai.github.io/openai-agents-python/tracing/]
- **Empty content is not success**: qwen3.8-uncensored:27b answers HTTP 200 with empty content when
  thinking is on; disable thinking via `extra_body={"chat_template_kwargs": {"enable_thinking": false}}`
  and assert non-empty output. [observed here 2026-09-28, worker-verified endpoint behavior]
- **Native `.so` blocked by sandbox library validation** (`library load disallowed by system policy`
  on `_cffi_backend` during SDK import here; xattr -cr, codesign --force -s -, swapping the
  identical wheel that loads in sibling venvs, and a cffi reinstall all failed): the whole
  `import agents` chain dies at `agents->mcp->cryptography`, so L2/L3 are unreachable in this
  sandbox - prove from the Orca host shell. [observed here 2026-09-28]
- **PYTHONHOME/PYTHONPATH leak** breaks venvs; always `env -u PYTHONHOME -u PYTHONPATH`.
  [observed here 2026-09-28]
- **Default model changes between minor releases**; pin the model explicitly in every agent.
  [docs: https://github.com/openai/openai-agents-python/releases (0.20.0 notes)]

## 14. Proof receipts (claim only what ran)

| Command | Exit | Version | Date | Proof level |
| --- | --- | --- | --- | --- |
| WebFetch `https://pypi.org/pypi/openai-agents/json` (version pin) | 0 | 0.22.3 | 2026-09-28 | L0 |
| WebFetch `https://openai.github.io/openai-agents-python/models/` | 0 | - | 2026-09-28 | L0 |
| WebFetch `https://openai.github.io/openai-agents-python/tracing/` | 0 | - | 2026-09-28 | L0 |
| `curl https://registry.npmjs.org/@openai/agents` (JS sibling note) | 0 | 0.18.0 | 2026-09-28 | L0 |
| `uv pip install --python .venv/bin/python openai-agents==0.22.3` | 0 | 0.22.3 | 2026-09-28 | L1 (install only) |
| `.venv/bin/python -c "import agents"` | 1 | 0.22.3 | 2026-09-28 | **BLOCKED (sandbox library validation)** - `dlopen _cffi_backend.cpython-312-darwin.so ... library load disallowed by system policy` via agents->mcp->cryptography; xattr, codesign, wheel swap and cffi reinstall all failed; host-shell route: Orca terminal |
| hello_agents.py / L3 / planted test | not run | - | 2026-09-28 | NOT CLAIMED (blocked at import) |

Full command ledger: `references/proof.json`. A rung not in that file is not claimed.
