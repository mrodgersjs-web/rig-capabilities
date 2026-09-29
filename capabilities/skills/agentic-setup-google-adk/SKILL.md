---
name: agentic-setup-google-adk
description: "agentic-systems-setup family, one skill per framework: install and run Google Agent Development Kit (google-adk) agents end to end on Mike's Mac - uv venv in ~/.rig/agentic-lab, local-first model wiring through the LiteLlm connector with openai/<model> strings and api_base pointed at Mike's own endpoints (no paid keys), hello-world proven with a deterministic fake BaseLlm, and proof claims limited to executed rungs. JEV-FIRST MANDATE: send typed judgments like 'which framework fits' or 'did the proof pass' to rig-s1gate before any frontier model call, and fail closed. Always-loaded task-start surface, not a deep reference: start here when installing, upgrading, or debugging google-adk agents, LlmAgent, InMemoryRunner, or ADK tools/workflows on this Mac."
tags: [rig, agentic-systems, sub-skill, google-adk, agents, python, setup]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: framework-setup
  extends: "agentic-env-probe, agentic-local-models, agentic-secrets, agentic-observability, agentic-proof-ladder"
outcome: "A google-adk agent that runs on Mike's Mac against a deterministic fake BaseLlm (L2) and, when a local endpoint answers, a local model through the LiteLlm connector (L3), with secrets in the keychain, phone-home telemetry off, and a receipts table that claims no rung it did not execute."
activation: "Always loaded at the start of any task that names Google ADK, google-adk, LlmAgent, adk web/adk deploy, or the Agent Development Kit, and before choosing among the agentic-systems-setup framework skills."
instruction: "Probe the environment first (agentic-env-probe), install into ~/.rig/agentic-lab/google-adk with PYTHONHOME unset, wire models through LiteLlm(openai/<id>, api_base=local endpoint) or a BaseLlm subclass, prove with a fake model first (L2) then a local endpoint asserting non-empty content (L3), and send every typed judgment to rig-s1gate before a frontier model."
applies_when:
  env: "Aside bash sandbox or Orca host shell on Mike's Mac; uv at ~/.local/bin/uv"
  runtime: "Python 3.10+ (google-adk requires >=3.10)"
  deps: "google-adk==2.10.0 (verified 2026-09-28 via PyPI JSON); litellm>=1.84 for the LiteLlm connector"
  params: "LiteLlm(model='openai/<id>', api_base=...) for local endpoints; BaseLlm subclass for fakes"
  budget: "one agent run per proof; installs never land in a repo"
  scale: "single Mac; Cloud Run / Vertex AI Agent Engine deployment is Gate-D"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the environment and the local model routes before the first install command.
  - Create the lab venv with PYTHONHOME and PYTHONPATH unset and install the pinned version.
  - Wire the model through LiteLlm pointed at a local OpenAI-compatible endpoint (api_base), never a paid key.
  - Disable or localize telemetry (OTEL_SDK_DISABLED) for proof runs.
  - Prove with a deterministic FakeLlm first (L2), then a local endpoint (L3) asserting non-empty content.
  - Judge typed calls through rig-s1gate and fail closed.
done_when:
  - "grep:capabilities/skills/agentic-setup-google-adk/SKILL.md:FAKE_MODEL_OK"
  - "grep:capabilities/skills/agentic-setup-google-adk/SKILL.md:enable_thinking"
  - "grep:capabilities/skills/agentic-setup-google-adk/SKILL.md:Planted failure"
  - "file:capabilities/skills/agentic-setup-google-adk/references/proof.json"
out_of_scope:
  - Google AI Studio / Vertex signups, Cloud Run or Vertex AI Agent Engine deploys, paid plans (Gate-D)
  - installing into a git repo or a harness root (the lab dir is ~/.rig/agentic-lab/google-adk)
  - rotating secrets after a supply-chain advisory without Mike's say-so (report first)
---

# agentic-setup-google-adk

Start here when: the task names Google ADK (Agent Development Kit) and you must install, wire, or
prove it on this Mac. Always-loaded task-start surface: this file opens every ADK setup task.

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM
call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a local
guess. Typed judgments in this skill ("which framework fits this task", "did the proof pass",
"is this agent production-ready") go to `./bin/rig-s1gate check doctrine.surface` or the runtime
rubric before any frontier model. A required signal passes only above 0.9; below that the step
does not advance.

## Load surface

Always loaded at the START of every ADK setup task: the `agentic-systems-setup` family routes here
before the first setup action. It is a task-start surface, not a deep reference an agent must
already know about. Sibling skills own shared machinery: `agentic-env-probe`,
`agentic-local-models`, `agentic-secrets`, `agentic-observability`, `agentic-proof-ladder`.
Read those instead of duplicating them here.

## 1. When to choose it, and when not

Choose google-adk when the deliverable is an **agent platform kit**: hierarchical multi-agent
systems, a workflow runtime (graph execution, fan-out/fan-in, HITL), tools (function, OpenAPI, MCP),
`adk web` local debugging, and eventual deployment to Google infrastructure - and you want Python
first.

Do **not** choose it when:

- The ask is a Microsoft/enterprise .NET-or-Python stack with graph workflows and middleware - that
  is `microsoft-agent-framework` (nearest alternative 1).
- The ask is a role-playing crew with declarative YAML/backstories - that is `crewai`
  (nearest alternative 2); for a minimal single-agent loop see `openai-agents-sdk` or `pydantic-ai`.
- The ask is durable jobs (Temporal, Prefect, Dagster, Airflow, Trigger.dev, Inngest, Kestra) or
  low-code builders (n8n, Dify, Flowise, Langflow) or TypeScript (Mastra).

Nearest alternatives in this family: **microsoft-agent-framework** and **crewai**.

## 2. Current version and sources (fetched 2026-09-28)

| Source | URL | Verified |
| --- | --- | --- |
| PyPI JSON API | `https://pypi.org/pypi/google-adk/json` | `2.10.0`, requires_python `>=3.10` |
| Models docs | `https://google.github.io/adk-docs/agents/models/` | three integration paths: direct string/registry (Gemini, Agent Platform), model connectors (`LiteLlm`, `ApigeeLlm`), and model routing |
| LiteLLM connector docs | `https://google.github.io/adk-docs/agents/models/litellm/` | `LiteLlm(model="openai/<model>")` on `LlmAgent.model`; `litellm>=1.84` required; provider keys via env vars; local model hosting supported (Ollama/vLLM pages) |
| PyPI description | `https://pypi.org/project/google-adk` | ADK 2.0 breaking changes vs 1.x (agent API, event model, session schema); deploy targets Cloud Run / Vertex AI Agent Engine |

Pinned version: **google-adk==2.10.0**. **ADK 2.x sessions are not readable by ADK < 1.28** (PyPI
description) - do not mix 1.x and 2.x tooling on one session store.

## 3. Environment route and prerequisites

- Route: Aside sandbox works for install and fake-model runs (L1/L2); L3 needs sandbox network
  reachability to the endpoint. `adk web` (a local dev UI server) should run under the
  self-destruct-server pattern in the sandbox, or in the Orca host shell (`agentic-env-probe`).
- Prefix `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`; run python as
  `env -u PYTHONHOME -u PYTHONPATH <venv>/bin/python ...`.
- Prereqs: `uv`, Python 3.10+ (`~/.local/bin/python3.12`). For the LiteLlm connector: `litellm>=1.84`
  (pulled by `google-adk[extensions]`, or `pip install "litellm>=1.84"` per the docs).
- Install location `~/.rig/agentic-lab/google-adk/`, never inside a repo.

## 4. Install (exact commands)

```sh
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/google-adk && cd ~/.rig/agentic-lab/google-adk
env -u PYTHONHOME -u PYTHONPATH uv venv --python 3.12 .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python google-adk==2.10.0 "litellm>=1.84"
.venv/bin/python -c "import google.adk; from google.adk.models.lite_llm import LiteLlm; print('adk ok')"
```

If a native `.so` fails `code signature ... not valid for use in process: library load disallowed
by system policy`, try once `xattr -cr .venv` and `codesign --force -s - <file.so>`; if still
blocked, record **BLOCKED (sandbox library validation)** with the exact error and prove from Orca.

## 5. Local-first model wiring (no paid keys)

Two routes, both local-first:

**A. LiteLlm connector to a local OpenAI-compatible server** (docs: "Local model host - Use the
`LiteLlm` wrapper class configured to point to your local model server"):

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

agent = LlmAgent(
    name="local_agent",
    model=LiteLlm(
        model="openai/qwen3.8-uncensored:27b",   # exactly an id from /v1/models
        api_base="http://127.0.0.1:8771/v1",     # LiteLLM standard param; probe first
        api_key="local-not-a-secret",
    ),
    instruction="You are a local assistant.",
)
```

Env-var alternative: LiteLLM's standard `OPENAI_API_BASE` plus `OPENAI_API_KEY` (placeholder for a
local server), with the same `openai/<id>` string. Provider env var names: LiteLLM providers docs
(cited by the ADK page).

**B. Direct BaseLlm subclass** - the deterministic seam used for tests (section 7).

Mike's local endpoints as of 2026-09-28: `http://127.0.0.1:8771/v1` (model
`qwen3.8-uncensored:27b` - with thinking enabled it returns HTTP 200 with EMPTY content; disable
thinking via `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` passed through the
LiteLLM call kwargs) and `http://127.0.0.1:8657/v1` (model `MiMo-V2.6-Flash-RL-MLX-4bit-MTP`).
Blackwell LAN endpoints `192.168.68.90:8011/:8111` do NOT answer from this sandbox. Always assert
non-empty content.

## 6. Secrets

- Keychain names only: `com.rig.env.GOOGLE_API_KEY`, `com.rig.env.OPENAI_API_KEY`
  (`agentic-secrets`); the docs say env vars must be set before instantiating `LiteLlm`.
- `.env.example`: `OPENAI_API_KEY=<from com.rig.env.OPENAI_API_KEY>`,
  `OPENAI_API_BASE=http://127.0.0.1:8771/v1`. Never commit `.env`; never print values.

## 7. Hello-world (deterministic, no network)

File: `hello_adk.py` (also under `~/.rig/agentic-lab/google-adk/run/`):

```python
"""Google ADK hello-world with a deterministic fake BaseLlm. No network, no API keys."""
import asyncio

from google.adk.agents import LlmAgent
from google.adk.models import BaseLlm, LlmRequest, LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types


class FakeLlm(BaseLlm):
    """Deterministic BaseLlm implementation (the documented model-connector seam)."""
    model: str = "fake/deterministic"

    async def generate_content_async(self, llm_request: LlmRequest, stream: bool = False):
        yield LlmResponse(
            content=types.Content(role="model", parts=[types.Part(text="FAKE_MODEL_OK: hello from the fake ADK model")])
        )


async def main():
    agent = LlmAgent(name="hello_agent", model=FakeLlm(model="fake/deterministic"),
                     instruction="Greet RIG in one line.")
    runner = InMemoryRunner(agent=agent, app_name="hello_adk")
    session = await runner.session_service.create_session(app_name="hello_adk", user_id="u1")
    out = ""
    async for event in runner.run_async(
        user_id="u1", session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text="Say hello")]),
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            out += event.content.parts[0].text
    print(out.strip())
    assert "FAKE_MODEL_OK" in out, f"fake model output missing marker: {out!r}"
    print("HELLO_ADK_GREEN")


if __name__ == "__main__":
    asyncio.run(main())
```

```sh
cd ~/.rig/agentic-lab/google-adk/run
env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python hello_adk.py
# -> FAKE_MODEL_OK: hello from the fake ADK model
# -> HELLO_ADK_GREEN   (exit 0)
```

## 8. Durable and production features

- Workflow runtime (graph execution, routing, fan-out/fan-in, loops, retry, HITL - PyPI
  description), Task API for agent-to-agent delegation, multi-agent hierarchies, MCP/OpenAPI tools.
- Sessions/state via `SessionService` (`InMemoryRunner` for tests; a persistent service for
  durability - 2.x session schema, see gotchas).
- `adk web` local dev UI for stepping through agents; `adk eval` for eval sets (see section 10).

## 9. Observability (and turning off phone-home)

ADK emits OpenTelemetry spans through `google.adk.telemetry` when the OTel SDK is configured.
For proof runs keep it local and quiet:

```sh
export OTEL_SDK_DISABLED=true   # OTel-standard switch: no spans exported anywhere
```

(This standard variable is the same one CrewAI's docs name for killing OTEL instrumentation; for
ADK it is the OTel SDK-level switch and was not separately exercised against an ADK exporter in
this proof - treat "spans never leave the machine" as the rule and verify locally before relying
on it.) Do not point ADK telemetry at a hosted backend without Gate-D.

## 10. Testing and evals (one planted failure that goes red)

- Test seam: subclass `google.adk.models.BaseLlm` and implement
  `generate_content_async(llm_request, stream=False)` yielding one `LlmResponse` (non-streaming
  mode yields exactly one response with `partial=False` - docs). Assert on the event text content,
  never on "did not throw".
- **Planted failure must fail the exit code, not print RED.** A caught AssertionError that prints
  `PLANTED_FAILURE_RED` and exits 0 proves nothing: an exit-code gate would pass it. The harness
  (`test_planted_adk.py`) must leave the assertion UNCAUGHT so the plant run exits non-zero.
  Executed cycle here (2026-09-28): checksum `hello_adk.py` (sha256 `fdee25975ab7..`), plant
  `WRONG_PLANTED` into the fake (sha `7b9aed94436e..`; **refuse the plant if the bytes did not
  move**), run the harness and record the real **exit 1** (RED, uncaught `AssertionError`), restore
  (sha back to `fdee25975ab7..`, match verified) and record **exit 0** (GREEN). Clear `__pycache__`
  between runs: a same-length plant token plus same-second mtime can leave a stale `.pyc` faking a
  green. Keep the planted file as a regression fixture.
- `adk eval` runs eval sets against agents for regression; keep them against fake/local models.

## 11. Deploy / self-host (Gate-D)

Local `InMemoryRunner`/`adk web` on Mike's Mac is fine. **Gate-D, do not do without Mike's explicit
approval:** Google AI Studio or Vertex signups/logins, `adk deploy` to Cloud Run or Vertex AI
Agent Engine (PyPI description's deploy targets), any paid plan, any public URL, any push.
`agentic-deploy-gate` owns the checklist.

## 12. Teardown and upgrade

```sh
rm -rf ~/.rig/agentic-lab/google-adk/.venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U google-adk==<new-pin>
.venv/bin/python -c "import google.adk; print('adk ok')"
```

Release cadence is roughly bi-weekly (PyPI description). Re-run the fake-model hello-world after
every upgrade; 2.x has already shipped breaking changes against 1.x APIs.

## 13. Gotchas (each tagged with where observed)

- **LiteLLM supply-chain advisory**: unauthorized code in LiteLLM 1.82.7/1.82.8 (2026-03-24); the
  ADK docs page tells users on `eval`/`extensions` extras to update immediately and rotate secrets
  if they installed those versions. Pin `litellm>=1.84` and check
  `https://github.com/google/adk-python/issues/5005`. [docs: https://google.github.io/adk-docs/agents/models/litellm/]
- **HTTP 200 with empty content** on qwen3.8-uncensored:27b when thinking is enabled; disable via
  `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` and assert non-empty output.
  [observed here 2026-09-28, worker-verified endpoint behavior]
- **ADK 2.x breaks 1.x** (agent API, event model, session schema) and 2.x sessions cannot be read
  by older 1.x. [docs: https://pypi.org/project/google-adk]
- **Native `.so` sandbox library validation** can block imports (`library load disallowed by system
  policy`); `xattr -cr` + one `codesign --force -s -`, else BLOCKED (sandbox library validation).
  [observed here 2026-09-28, sibling run]
- **PYTHONHOME/PYTHONPATH leak** breaks venvs; always `env -u PYTHONHOME -u PYTHONPATH`.
  [observed here 2026-09-28]
- **Port 8080 is taken** on this Mac by a stray Kestra; pick another port for `adk web`, and never
  kill a port you did not bind in the same bash call. [observed here 2026-09-28, environment facts]

## 14. Proof receipts (claim only what ran)

| Command | Exit | Version | Date | Proof level |
| --- | --- | --- | --- | --- |
| WebFetch `https://pypi.org/pypi/google-adk/json` (version pin) | 0 | 2.10.0 | 2026-09-28 | L0 |
| WebFetch `https://google.github.io/adk-docs/agents/models/` | 0 | - | 2026-09-28 | L0 |
| WebFetch `https://google.github.io/adk-docs/agents/models/litellm/` | 0 | - | 2026-09-28 | L0 |
| `uv pip install google-adk==2.10.0 "litellm>=1.84"` (lab venv) | 0 | 2.10.0 | 2026-09-28 | L1 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python hello_adk.py` (FakeLlm) | 0 (`HELLO_ADK_GREEN`) | 2.10.0 | 2026-09-28 | L2 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python l3_adk.py` (LiteLlm api_base -> 8657) | 0 (`L3_ADK_GREEN`, non-empty content asserted) | 2.10.0 | 2026-09-28 | L3 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python test_planted_adk.py` with `WRONG_PLANTED` planted in `hello_adk.py` (sha `fdee25975ab7..` -> `7b9aed94436e..`, plant refused if bytes unchanged) | **1** (RED, uncaught `AssertionError`) | 2.10.0 | 2026-09-28 | L2 (planted-failure gate) |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python test_planted_adk.py` after restore (sha back to `fdee25975ab7..`, match verified) | 0 (GREEN) | 2.10.0 | 2026-09-28 | L2 (green after restore) |

Full command ledger: `references/proof.json`. A rung not in that file is not claimed.
