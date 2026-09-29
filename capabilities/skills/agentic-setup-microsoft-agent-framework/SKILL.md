---
name: agentic-setup-microsoft-agent-framework
description: "agentic-systems-setup family, one skill per framework: install and run Microsoft Agent Framework (agent-framework, successor to AutoGen and Semantic Kernel) on Mike's Mac - uv venv in ~/.rig/agentic-lab, local-first model wiring through OpenAIChatCompletionClient with base_url pointed at Mike's own endpoints (no paid keys), hello-world proven with a deterministic fake chat client, and proof claims limited to executed rungs. JEV-FIRST MANDATE: send typed judgments like 'which framework fits' or 'did the proof pass' to rig-s1gate before any frontier model call, and fail closed. Always-loaded task-start surface, not a deep reference: start here when installing, upgrading, or debugging Microsoft Agent Framework agents, workflows, or migrating an AutoGen or Semantic Kernel project on this Mac."
tags: [rig, agentic-systems, sub-skill, microsoft-agent-framework, autogen, semantic-kernel, agents, python, setup]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: framework-setup
  extends: "agentic-env-probe, agentic-local-models, agentic-secrets, agentic-observability, agentic-proof-ladder"
outcome: "A Microsoft Agent Framework agent that runs on Mike's Mac against a deterministic fake chat client (L2) and, when a local endpoint answers, a local model through OpenAIChatCompletionClient(base_url=...) (L3), with the AutoGen/Semantic Kernel succession stated from Microsoft's own pages and a receipts table that claims no rung it did not execute."
activation: "Always loaded at the start of any task that names Microsoft Agent Framework, agent-framework, Microsoft.Agents.AI, an AutoGen or Semantic Kernel migration, or 'MAF', and before choosing among the agentic-systems-setup framework skills."
instruction: "Probe the environment first (agentic-env-probe), install into ~/.rig/agentic-lab/microsoft-agent-framework with PYTHONHOME unset, wire a local endpoint through OpenAIChatCompletionClient(model, api_key, base_url), disable OTel export for proof runs, prove with a fake SupportsChatGetResponse client first, and send every typed judgment to rig-s1gate before a frontier model."
applies_when:
  env: "Aside bash sandbox or Orca host shell on Mike's Mac; uv at ~/.local/bin/uv"
  runtime: "Python 3.10+ (agent-framework requires >=3.10); .NET sibling exists but is out of scope here"
  deps: "agent-framework==1.19.0 (verified 2026-09-28 via PyPI JSON); agent_framework_openai for the OpenAI-compatible client"
  params: "OpenAIChatCompletionClient(model=<id>, api_key=..., base_url=...) or a custom SupportsChatGetResponse client"
  budget: "one agent run per proof; installs never land in a repo"
  scale: "single Mac; Azure/Foundry deployment is Gate-D"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the environment and the local model routes before the first install command.
  - Create the lab venv with PYTHONHOME and PYTHONPATH unset and install the pinned version.
  - Wire a local OpenAI-compatible endpoint through OpenAIChatCompletionClient(base_url=...), never a paid key.
  - Localize or disable OTel export (OTEL_SDK_DISABLED) for proof runs.
  - Prove with a deterministic fake chat client first (L2), then a local endpoint (L3) asserting non-empty content.
  - Judge typed calls through rig-s1gate and fail closed.
done_when:
  - "grep:capabilities/skills/agentic-setup-microsoft-agent-framework/SKILL.md:FAKE_MODEL_OK"
  - "grep:capabilities/skills/agentic-setup-microsoft-agent-framework/SKILL.md:OPENAI_BASE_URL"
  - "grep:capabilities/skills/agentic-setup-microsoft-agent-framework/SKILL.md:Planted failure"
  - "file:capabilities/skills/agentic-setup-microsoft-agent-framework/references/proof.json"
out_of_scope:
  - Azure AI Foundry / Microsoft Foundry signups, cloud deploys, paid plans, public URLs (Gate-D)
  - installing into a git repo or a harness root (lab dir: ~/.rig/agentic-lab/microsoft-agent-framework)
  - .NET (Microsoft.Agents.AI) setup; this skill covers the Python package only
---

# agentic-setup-microsoft-agent-framework

Start here when: the task names Microsoft Agent Framework (Python `agent-framework`) - or an
AutoGen / Semantic Kernel migration - and you must install, wire, or prove it on this Mac.
Always-loaded task-start surface: this file opens every MAF setup task.

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM
call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a local
guess. Typed judgments in this skill ("which framework fits this task", "did the proof pass",
"is this workflow production-ready") go to `./bin/rig-s1gate check doctrine.surface` or the
runtime rubric before any frontier model. A required signal passes only above 0.9; below that the
step does not advance.

## Load surface

Always loaded at the START of every Microsoft Agent Framework setup task: the
`agentic-systems-setup` family routes here before the first setup action. It is a task-start
surface, not a deep reference an agent must already know about. Sibling skills own shared
machinery: `agentic-env-probe`, `agentic-local-models`, `agentic-secrets`, `agentic-observability`,
`agentic-proof-ladder`. Read those instead of duplicating them here.

## 1. When to choose it, and when not

Choose Microsoft Agent Framework when the deliverable needs **enterprise multi-agent structure in
Python or .NET**: single agents with tools and sessions, a batteries-included Harness Agent for
long multi-step tasks, and explicit **graph/functional workflows** with middleware, type-safe
tools, MCP clients and OTel telemetry - especially if the codebase already has AutoGen or Semantic
Kernel in it (this framework is their successor, see section 2).

Do **not** choose it when:

- The ask is a role-playing crew with declarative YAML and backstories - that is `crewai`
  (nearest alternative 1), or a minimal single-agent loop - `openai-agents-sdk` / `pydantic-ai`.
- The ask is a Google-cloud-native agent platform (Agent Platform, Gemini-first) - that is
  `google-adk` (nearest alternative 2).
- The ask is durable jobs (Temporal, Prefect, Dagster, Airflow, Trigger.dev, Inngest, Kestra),
  low-code builders (n8n, Dify, Flowise, Langflow), or TypeScript-only (Mastra).

Nearest alternatives in this family: **crewai** and **google-adk**.

## 2. Current version and sources (fetched 2026-09-28) - including what happened to AutoGen and Semantic Kernel

| Source | URL | Verified |
| --- | --- | --- |
| PyPI JSON API | `https://pypi.org/pypi/agent-framework/json` | `1.19.0`, requires_python `>=3.10` ("core and optional packages" meta-package) |
| Microsoft Learn overview | `https://learn.microsoft.com/en-us/agent-framework/overview` | "Agent Framework combines AutoGen's simple agent abstractions with Semantic Kernel's enterprise features ... and adds graph-based workflows"; "Semantic Kernel and AutoGen pioneered the concepts ... The Agent Framework is the direct successor, created by the same teams"; "the next generation of both Semantic Kernel and AutoGen"; migration guides from both; **does not auto-load `.env`** |
| Microsoft devblogs | `https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0` | Version 1.0 (GA) announced 2026-04-03; migration assistants for Semantic Kernel and AutoGen; DevUI local debugger as preview |
| Semantic Kernel README (Microsoft repo) | `https://github.com/microsoft/semantic-kernel/blob/main/README.md` | "Semantic Kernel is now Microsoft Agent Framework! ... enterprise-ready successor ... available at version 1.0" |
| Microsoft Agent Framework blog Q&A | `https://devblogs.microsoft.com/agent-framework/semantic-kernel-and-microsoft-agent-framework/` | "Think of Microsoft Agent Framework as Semantic Kernel v2.0 ... we will continue to support Semantic Kernel v1.x ... for at least one year after Microsoft Agent Framework leaves Preview and is Generally Available"; new projects should start on Agent Framework |
| AutoGen announcement (Microsoft repo) | `https://github.com/microsoft/autogen/discussions/7066` | "AutoGen and Semantic Kernel are merging into a single, unified framework under the name Microsoft Agent Framework" (2025-10-02) |

**What happened, in Microsoft's own words:** AutoGen (multi-agent orchestration, Microsoft Research)
and Semantic Kernel (enterprise orchestration) merged into **Microsoft Agent Framework** (announced
2025-10; GA 1.0 on 2026-04-03). Both old projects remain supported during transition - Semantic
Kernel v1.x gets critical fixes "for at least one year after" GA, and AutoGen lives on as the
merged framework's single-agent interface heritage - but **most new investment goes to Agent
Framework**, and Microsoft publishes migration guides from both
(`learn.microsoft.com/en-us/agent-framework/migration-guide/from-semantic-kernel` and
`.../from-autogen`, listed on the overview page).

Pinned version: **agent-framework==1.19.0** (Python). The .NET package is `Microsoft.Agents.AI`
(NuGet); Go is in public preview (overview page) - out of scope here.

## 3. Environment route and prerequisites

- Route: Aside sandbox works for install and fake-client runs (L1/L2); L3 needs sandbox network
  reachability to the endpoint. DevUI or Docker-based work goes to the Orca host shell
  (`agentic-env-probe`).
- Prefix `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`; run python as
  `env -u PYTHONHOME -u PYTHONPATH <venv>/bin/python ...`.
- Prereqs: `uv`, Python 3.10+ (`~/.local/bin/python3.12`). No Docker, no JVM, no .NET needed.
- Install location `~/.rig/agentic-lab/microsoft-agent-framework/`, never inside a repo.
- The framework **does not auto-load `.env`** (overview page): call `load_dotenv()` yourself or
  export variables in the shell.

## 4. Install (exact commands)

```sh
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/microsoft-agent-framework && cd ~/.rig/agentic-lab/microsoft-agent-framework
env -u PYTHONHOME -u PYTHONPATH uv venv --python 3.12 .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python agent-framework==1.19.0
.venv/bin/python -c "import agent_framework; print(agent_framework.__version__)"
.venv/bin/python -c "from agent_framework_openai import OpenAIChatCompletionClient; print('openai client ok')"
```

If a native `.so` fails `code signature ... not valid for use in process: library load disallowed
by system policy`, try once `xattr -cr .venv` and `codesign --force -s - <file.so>`; if still
blocked, record **BLOCKED (sandbox library validation)** with the exact error and prove from Orca.

## 5. Local-first model wiring (no paid keys)

Use the OpenAI-compatible client with `base_url` (constructor and env verified in the installed
package, `agent_framework_openai/_chat_completion_client.py`): the constructor reads
`OPENAI_CHAT_COMPLETION_MODEL` (then `OPENAI_MODEL`), `OPENAI_API_KEY`, `OPENAI_ORG_ID`, and
`OPENAI_BASE_URL` when the arguments are omitted.

```python
import asyncio
from agent_framework import Agent
from agent_framework_openai import OpenAIChatCompletionClient

client = OpenAIChatCompletionClient(
    model="qwen3.8-uncensored:27b",       # exactly an id from /v1/models
    api_key="local-not-a-secret",
    base_url="http://127.0.0.1:8771/v1",  # probe first: curl -s -m 5 <base>/models
)

agent = Agent(client=client, name="LocalAgent", instructions="You are a local assistant.")

async def main():
    result = await agent.run("Say hello to RIG.")
    print(result.text)

asyncio.run(main())
```

Env alternative: `OPENAI_BASE_URL=http://127.0.0.1:8771/v1`, `OPENAI_CHAT_COMPLETION_MODEL=<id>`,
placeholder `OPENAI_API_KEY` (remember: no auto `.env` loading). Mike's local endpoints as of
2026-09-28: `http://127.0.0.1:8771/v1` (model `qwen3.8-uncensored:27b` - with thinking enabled it
returns HTTP 200 with EMPTY content; disable thinking via
`extra_body={"chat_template_kwargs": {"enable_thinking": false}}` passed as request kwargs, and
assert non-empty content) and `http://127.0.0.1:8657/v1` (model
`MiMo-V2.6-Flash-RL-MLX-4bit-MTP`). Blackwell LAN endpoints `192.168.68.90:8011/:8111` do NOT
answer from this sandbox.

## 6. Secrets

- Keychain names only: `com.rig.env.OPENAI_API_KEY`, `com.rig.env.AZURE_*` (`agentic-secrets`).
  Local endpoints take any placeholder `api_key`; the client also accepts a callable key.
- `.env.example`: `OPENAI_API_KEY=<from com.rig.env.OPENAI_API_KEY>`,
  `OPENAI_BASE_URL=http://127.0.0.1:8771/v1`, `OPENAI_CHAT_COMPLETION_MODEL=<model-id>`. Load it
  explicitly with `load_dotenv()`; never commit it; never print values.

## 7. Hello-world (deterministic, no network)

The framework's own protocol docstring shows the custom-client seam (`SupportsChatGetResponse`).
File: `hello_maf.py` (also under `~/.rig/agentic-lab/microsoft-agent-framework/run/`):

```python
"""Microsoft Agent Framework hello-world with a deterministic fake chat client. No network, no keys."""
import asyncio

from agent_framework import Agent, ChatResponse, Content, Message


class FakeChatClient:
    """Deterministic chat client (the SupportsChatGetResponse protocol seam)."""
    additional_properties: dict = {}

    def get_response(self, messages, *, stream=False, client_kwargs=None, **kwargs):
        async def _response():
            return ChatResponse(
                messages=[Message(role="assistant", contents=[Content.from_text("FAKE_MODEL_OK: hello from the fake MAF client")])],
                response_id="fake-response-1",
            )
        return _response()


async def main():
    agent = Agent(client=FakeChatClient(), name="HelloAgent",
                  instructions="You are a helpful assistant. Reply with one short line.")
    result = await agent.run("Say hello to RIG.")
    out = (result.text or "").strip()
    print(out)
    assert "FAKE_MODEL_OK" in out, f"fake client output missing marker: {out!r}"
    print("HELLO_MAF_GREEN")


if __name__ == "__main__":
    asyncio.run(main())
```

```sh
cd ~/.rig/agentic-lab/microsoft-agent-framework/run
env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python hello_maf.py
# -> FAKE_MODEL_OK: hello from the fake MAF client
# -> HELLO_MAF_GREEN   (exit 0)
```

## 8. Durable and production features

- Sessions/threads for state management, middleware for intercepting agent actions, context
  providers for memory, MCP tool clients, type-safe function tools (overview page).
- **Workflows**: functional and graph-based execution paths for multi-agent orchestration with
  explicit control - the part that distinguishes MAF from AutoGen's original interface.
- **Harness Agent**: opinionated long-task agent (planning, compaction, tool approval,
  observability) - overview page; check its feature stage before relying on it in production.
- A2A and MCP interoperability (Semantic Kernel README statement, v1.0).

## 9. Observability (and turning off phone-home)

The OpenAI chat client is built on a `ChatTelemetryLayer` with OTel provider name `openai`
(installed source, `agent_framework_openai/_chat_completion_client.py`); telemetry is designed to
export OpenTelemetry spans. For proof runs, keep everything local:

```sh
export OTEL_SDK_DISABLED=true   # OTel-standard switch: nothing exported anywhere
```

The DevUI debugger is a local browser tool (devblogs 1.0 post lists it as preview) - fine locally,
but do not expose it publicly. Any hosted observability backend (Azure Monitor, App Insights) is
Gate-D.

## 10. Testing and evals (one planted failure that goes red)

- Test seam: implement `SupportsChatGetResponse` (structural protocol) - the installed protocol's
  docstring literally shows a `CustomChatClient` returning a canned `ChatResponse`. Assert on
  `result.text` content, never on "did not throw".
- **Planted failure must fail the exit code, not print RED.** A caught AssertionError that prints
  `PLANTED_FAILURE_RED` and exits 0 proves nothing: an exit-code gate would pass it. The harness
  (`test_planted_maf.py`) must leave the assertion UNCAUGHT so the plant run exits non-zero.
  Executed cycle here (2026-09-28): checksum `hello_maf.py` (sha256 `63f30b512051..`), plant
  `WRONG_PLANTED` into the fake (sha `2399467b1cf2..`; **refuse the plant if the bytes did not
  move**), run the harness and record the real **exit 1** (RED, uncaught `AssertionError`), restore
  (sha back to `63f30b512051..`, match verified) and record **exit 0** (GREEN). Clear `__pycache__`
  between runs: here the same-length plant token plus same-second mtime left a stale `.pyc` that
  faked a GREEN after restore on the first cycle. Keep the planted file as a regression fixture.
- For workflow tests, run the graph with fake clients at every node; eval integrations are listed
  on the overview's Integrations page but are not exercised here.

## 11. Deploy / self-host (Gate-D)

Local `agent.run(...)` on Mike's Mac is fine. **Gate-D, do not do without Mike's explicit
approval:** Microsoft Foundry / Azure AI Foundry signups and logins (the overview's get-started
sample uses `AzureCliCredential` against a Foundry endpoint), cloud deploys, NuGet/pypi pushes,
paid plans, public DevUI or API URLs. `agentic-deploy-gate` owns the checklist.

## 12. Teardown and upgrade

```sh
rm -rf ~/.rig/agentic-lab/microsoft-agent-framework/.venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U agent-framework==<new-pin>
.venv/bin/python -c "import agent_framework; print(agent_framework.__version__)"
```

Re-run the fake-client hello-world after every upgrade; this repo moves fast (1.19.0 while the
ecosystem is still absorbing the AutoGen/SK migration) and preview features (DevUI, some Harness
Agent pieces) can change.

## 13. Gotchas (each tagged with where observed)

- **No automatic `.env` loading** - `load_dotenv()` or export vars yourself; the MAF docs call this
  out explicitly. [docs: https://learn.microsoft.com/en-us/agent-framework/overview]
- **HTTP 200 with empty content** on qwen3.8-uncensored:27b when thinking is enabled; disable via
  `extra_body={"chat_template_kwargs": {"enable_thinking": false}}` and assert non-empty output.
  [observed here 2026-09-28, worker-verified endpoint behavior]
- **AutoGen and Semantic Kernel are merged successors, not peers** - new code should not start on
  `autogen` or `semantic-kernel` packages; migration guides exist from both, and Semantic Kernel
  v1.x support is time-boxed ("at least one year after" MAF GA). [docs: learn.microsoft.com
  overview; devblogs; SK README; autogen discussion 7066 - URLs in section 2]
- **`Message`/`ChatResponse` constructor kwargs vary by version** - verified here 2026-09-28:
  `Message(role=..., contents=[Content.from_text(...)])`; `Content(text=...)` alone raises
  `TypeError: Content.__init__() missing 1 required positional argument: 'type'`. Check the
  installed `agent_framework` types before relying on a canned fake. [observed here 2026-09-28]
- **Native `.so` sandbox library validation** can block imports (`library load disallowed by system
  policy`); `xattr -cr` + one `codesign --force -s -`, else BLOCKED (sandbox library validation).
  [observed here 2026-09-28, sibling run]
- **PYTHONHOME/PYTHONPATH leak** breaks venvs; always `env -u PYTHONHOME -u PYTHONPATH`.
  [observed here 2026-09-28]

## 14. Proof receipts (claim only what ran)

| Command | Exit | Version | Date | Proof level |
| --- | --- | --- | --- | --- |
| WebFetch `https://pypi.org/pypi/agent-framework/json` (version pin) | 0 | 1.19.0 | 2026-09-28 | L0 |
| WebFetch `https://learn.microsoft.com/en-us/agent-framework/overview` | 0 | - | 2026-09-28 | L0 |
| WebSearch: devblogs 1.0 + SK README + AutoGen discussion 7066 (succession facts) | 0 | - | 2026-09-28 | L0 |
| `uv pip install --python .venv/bin/python agent-framework==1.19.0` | 0 | 1.19.0 | 2026-09-28 | L1 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python hello_maf.py` (fake client) | 0 (`HELLO_MAF_GREEN`) | 1.19.0 | 2026-09-28 | L2 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python l3_maf.py` (base_url -> 8657) | 0 (`L3_MAF_GREEN`, output `HELLO`, non-empty asserted) | 1.19.0 | 2026-09-28 | L3 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python test_planted_maf.py` with `WRONG_PLANTED` planted in `hello_maf.py` (sha `63f30b512051..` -> `2399467b1cf2..`, plant refused if bytes unchanged) | **1** (RED, uncaught `AssertionError`) | 1.19.0 | 2026-09-28 | L2 (planted-failure gate) |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python test_planted_maf.py` after restore (sha back to `63f30b512051..`, match verified) | 0 (GREEN) | 1.19.0 | 2026-09-28 | L2 (green after restore) |

Full command ledger: `references/proof.json`. A rung not in that file is not claimed.
