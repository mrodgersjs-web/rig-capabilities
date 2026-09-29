---
name: agentic-setup-crewai
description: "agentic-systems-setup family, one skill per framework: install and run CrewAI crews plus Flows end to end on Mike's Mac - uv venv in ~/.rig/agentic-lab, local-first model wiring through LiteLLM strings and base_url to Mike's own endpoints (no paid keys), telemetry disabled, hello-world proven with a deterministic fake model, and every rung of the proof ladder claimed only as far as it was executed. JEV-FIRST MANDATE: send typed judgments like 'which framework fits' or 'did the proof pass' to rig-s1gate before any frontier model call, and fail closed. Always-loaded task-start surface, not a deep reference: start here when installing, upgrading, or debugging CrewAI crews or Flows on this Mac."
tags: [rig, agentic-systems, sub-skill, crewai, agents, python, setup]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: framework-setup
  extends: "agentic-env-probe, agentic-local-models, agentic-secrets, agentic-observability, agentic-proof-ladder"
outcome: "A CrewAI crew that runs on Mike's Mac against a deterministic fake model (L2) and, when a local endpoint answers, a local model (L3), with telemetry off, secrets in the keychain, and a receipts table that claims no rung it did not execute."
activation: "Always loaded at the start of any task that names CrewAI, crew.kickoff, Crew Flows, agents.yaml/crew.jsonc, or 'build a crew of agents', and before choosing among the agentic-systems-setup framework skills."
instruction: "Probe the environment first (agentic-env-probe), install into ~/.rig/agentic-lab/crewai with PYTHONHOME unset, wire the LLM to a local OpenAI-compatible endpoint with a LiteLLM model string and base_url, disable telemetry, prove with a fake model before any real call, and send every typed judgment to rig-s1gate before a frontier model."
applies_when:
  env: "Aside bash sandbox or Orca host shell on Mike's Mac; uv at ~/.local/bin/uv"
  runtime: "Python 3.10 to 3.13 (CrewAI requires >=3.10,<3.14)"
  deps: "crewai==1.15.22 (verified 2026-09-28 via PyPI JSON); uv venv in ~/.rig/agentic-lab/crewai"
  params: "model string provider/model-id; base_url for local OpenAI-compatible endpoints"
  budget: "one crew or one Flow per run; installs never land in a repo"
  scale: "single Mac; multi-crew production belongs in deploy with Gate-D"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe the environment and the local model routes before the first install command.
  - Create the lab venv with PYTHONHOME and PYTHONPATH unset and install the pinned version.
  - Wire the LLM to a local OpenAI-compatible endpoint (base_url + LiteLLM model string), never a paid key.
  - Disable telemetry (CREWAI_DISABLE_TELEMETRY, OTEL_SDK_DISABLED) before any run that proves something.
  - Prove the crew with a deterministic FakeLLM first (L2), then a local endpoint (L3) asserting non-empty content.
  - Judge typed calls (framework fit, proof verdict) through rig-s1gate and fail closed.
done_when:
  - "grep:capabilities/skills/agentic-setup-crewai/SKILL.md:FAKE_MODEL_OK"
  - "grep:capabilities/skills/agentic-setup-crewai/SKILL.md:CREWAI_DISABLE_TELEMETRY"
  - "grep:capabilities/skills/agentic-setup-crewai/SKILL.md:Planted failure"
  - "file:capabilities/skills/agentic-setup-crewai/references/proof.json"
out_of_scope:
  - CrewAI AMP (app.crewai.com) signup, CrewAI Factory cloud deployment, or any paid plan (Gate-D)
  - installing into a git repo or a harness root (the lab dir is ~/.rig/agentic-lab/crewai)
  - running any paid API call or shipping a key into code
---

# agentic-setup-crewai

Start here when: the task names CrewAI, crews, or Flows and you must install, wire, or prove it on
this Mac. Always-loaded task-start surface: this file opens every CrewAI setup task.

JEV FIRST, binding on every setup step: an agent whose only context is this excerpt routes
semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any frontier LLM
call, and FAILS CLOSED: when the classifier is unavailable the verdict is DEFERRED, never a local
guess. Typed judgments in this skill ("which framework fits this task", "did the proof pass",
"is this crew production-ready") go to `./bin/rig-s1gate check doctrine.surface` or the runtime
rubric in `capabilities/harnesses/s1gate/work-criteria.json` before any frontier model. A required
signal passes only above 0.9; below that the step does not advance.

## Load surface

Always loaded at the START of every CrewAI setup task: the `agentic-systems-setup` family routes
here before the first setup action. It is a task-start surface, not a deep reference an agent
must already know about. Sibling skills own the shared machinery - `agentic-env-probe`
(environment and routes), `agentic-local-models` (endpoint wiring), `agentic-secrets` (keychain),
`agentic-observability` (telemetry posture), `agentic-proof-ladder` (L0-L5 claim discipline).
Read those instead of duplicating them here.

## 1. When to choose it, and when not

Choose CrewAI when the deliverable is a **role-playing multi-agent crew**: several agents with
roles, goals and backstories handing tasks to each other (sequential or hierarchical process),
optionally wrapped in a **Flow** for explicit orchestration steps, and you want Python with
YAML/JSONC declarative definitions (`crewai create crew` scaffolds agents in `agents/*.jsonc` and
`crew.jsonc`).

Do **not** choose it when:

- The ask is a single agent with tools and typed outputs - that is `openai-agents-sdk` (nearest
  alternative 1) or `pydantic-ai`, which stay far lighter than a crew.
- The ask is enterprise multi-agent with graph workflows, sessions and middleware on a Microsoft
  stack - that is `microsoft-agent-framework` (nearest alternative 2); for Google-cloud-native
  agent platforms see `google-adk`.
- The ask is a durable job substrate (retries, schedules) - that is Trigger.dev, Inngest, Temporal,
  Prefect, Dagster, Airflow or Kestra, not a crew.
- The ask is low-code builders (n8n, Dify, Flowise, Langflow) or a TS stack (Mastra).

Nearest alternatives in this family: **openai-agents-sdk** and **microsoft-agent-framework**.

## 2. Current version and sources (fetched 2026-09-28)

| Source | URL | Verified |
| --- | --- | --- |
| PyPI JSON API | `https://pypi.org/pypi/crewai/json` | `1.15.22`, requires_python `>=3.10,<3.14` |
| Install docs | `https://docs.crewai.com/en/installation` | Python >=3.10,<3.14; uv-based; `crewai create crew` is JSON-first (agents/*.jsonc + crew.jsonc) |
| LLM docs | `https://docs.crewai.com/en/concepts/llms` | `LLM(model=..., base_url=..., api_key=...)`; `MODEL=provider/model-id` env; non-native providers via LiteLLM (`crewai[litellm]` extra) |
| PyPI description | `https://pypi.org/project/crewai` | telemetry opt-out: `CREWAI_DISABLE_TELEMETRY=true/1/yes/on`, `OTEL_SDK_DISABLED` with the same values |

Pinned version for this skill: **crewai==1.15.22** (re-verify before install; nightly
`.devYYYYMMDD` builds exist on PyPI and are not what this skill pins).

## 3. Environment route and prerequisites

- Route: Aside bash sandbox works for install and fake-model runs (L1/L2). A run against a local
  model endpoint (L3) needs network reachability from the sandbox to that endpoint. Anything
  needing Docker or a GUI goes to the Orca host shell - see `agentic-env-probe` routes.
- PATH is missing `~/.local/bin`: prefix `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"` (uv lives there).
- The Aside runtime exports `PYTHONHOME`/`PYTHONPATH`; every python invocation must unset them:
  `env -u PYTHONHOME -u PYTHONPATH uv venv --python 3.12 .venv`.
- Prereqs: `uv`, Python 3.10-3.13 (`python3.12` at `~/.local/bin/python3.12`). No Docker, no JVM
  needed.
- Install location is `~/.rig/agentic-lab/crewai/`, never inside a repo.

## 4. Install (exact commands)

```sh
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
mkdir -p ~/.rig/agentic-lab/crewai && cd ~/.rig/agentic-lab/crewai
env -u PYTHONHOME -u PYTHONPATH uv venv --python 3.12 .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python crewai==1.15.22
.venv/bin/python -c "import crewai; print(crewai.__version__)"
```

Optional LiteLLM extra for non-native providers (local vLLM/Ollama-style OpenAI endpoints work
through the OpenAI-compatible path without it, per the LLM docs examples):

```sh
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python "crewai[litellm]"
```

If a native `.so` fails with `code signature ... not valid for use in process: library load
disallowed by system policy` (observed here on pydantic-core in one sandbox run), try once:
`xattr -cr .venv` and `codesign --force -s - <path/to/file.so>`, then re-run. If it still fails,
record **BLOCKED (sandbox library validation)** with the exact error and run the proof from the
Orca host shell.

## 5. Local-first model wiring (no paid keys)

CrewAI reads a LiteLLM-style model string. For a local OpenAI-compatible server (vLLM, Ollama
`/v1`, llama.cpp, or Mike's own endpoints) use the OpenAI prefix with `base_url` - this is the
pattern the official LLM docs show for a local NIM-style server
(`model="openai/meta/llama-3.1-8b-instruct"`, `base_url="http://localhost:8000/v1"`, `api_key` any
placeholder text):

```python
from crewai import LLM

llm = LLM(
    model="openai/<model-id-exactly-as-/v1/models-returns>",
    base_url="http://127.0.0.1:8771/v1",   # probe with: curl -s -m 5 <base>/models
    api_key="local-not-a-secret",           # required by the SDK, any text for a local server
    temperature=0.0,
)
agent = Agent(role=..., goal=..., backstory=..., llm=llm)
```

Environment-variable route (docs): `MODEL=provider/model-id` plus provider key vars in `.env`.
Mike's local endpoints as of 2026-09-28: `http://127.0.0.1:8771/v1` (model `qwen3.8-uncensored:27b`;
with thinking enabled it returns HTTP 200 with EMPTY content - disable thinking via
`extra_body={"chat_template_kwargs": {"enable_thinking": false}}` and assert non-empty content) and
`http://127.0.0.1:8657/v1` (model `MiMo-V2.6-Flash-RL-MLX-4bit-MTP`). The Blackwell LAN endpoints
`192.168.68.90:8011` and `:8111` do NOT answer from this sandbox. Always pick a model id returned
by `<base>/models`; never guess one.

## 6. Secrets

- Keychain item names only, never values: `com.rig.env.OPENAI_API_KEY` etc. (see `agentic-secrets`).
- A local endpoint with no auth takes any placeholder `api_key` string; do not invent a real key.
- `.env.example` placeholders only in files: `OPENAI_API_KEY=<from com.rig.env.OPENAI_API_KEY>`,
  `MODEL=openai/<model-id>`. Never commit `.env`; the docs say the same ("Never commit API keys").

## 7. Hello-world (deterministic, no network)

File: `hello_crewai.py` (also under `~/.rig/agentic-lab/crewai/run/`):

```python
"""CrewAI hello-world with a deterministic fake model. No network, no API keys."""
import os
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

from crewai import Agent, Crew, Process, Task
from crewai.llm import BaseLLM


class FakeLLM(BaseLLM):
    """Deterministic BaseLLM implementation (the documented custom-LLM seam)."""
    model: str = "fake/deterministic"

    def call(self, messages, tools=None, callbacks=None, available_functions=None, **kwargs):
        return "FAKE_MODEL_OK: greeting from the deterministic fake crew model"

    def supports_function_calling(self):
        return False


def build_crew(llm):
    greeter = Agent(
        role="Greeter", goal="Greet the user exactly once",
        backstory="You are a deterministic greeter.",
        llm=llm, verbose=False, allow_delegation=False,
    )
    greet = Task(description="Say hello to RIG.", expected_output="A single greeting line.", agent=greeter)
    return Crew(agents=[greeter], tasks=[greet], process=Process.sequential)


if __name__ == "__main__":
    result = build_crew(FakeLLM(model="fake/deterministic")).kickoff()
    out = str(result).strip()
    print(out)
    assert "FAKE_MODEL_OK" in out, f"fake model output missing marker: {out!r}"
    print("HELLO_CREWAI_GREEN")
```

Command and expected output:

```sh
cd ~/.rig/agentic-lab/crewai/run
env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python hello_crewai.py
# -> FAKE_MODEL_OK: greeting from the deterministic fake crew model
# -> HELLO_CREWAI_GREEN   (exit 0)
```

## 8. Durable and production features

- **Flows**: `@start`/`@listen` decorated methods give explicit orchestration, state and router
  steps around crews (`from crewai.flow.flow import Flow`).
- **Structured outputs**: `LLM(..., response_format={...})` and task `output_pydantic` for typed results.
- **Declarative projects**: `crewai create crew` scaffolds JSONC definitions; `crewai run` executes them.
- **Persistence/observability hooks**: sequential/hierarchical processes, task callbacks, and the
  `share_crew` opt-in (keep it OFF - see section 9).
- Treat a `crew.kickoff()` return as a draft until it is read back and asserted; a clean run with
  empty content is not success (see the thinking-mode gotcha in section 13).

## 9. Observability (and turning off phone-home)

CrewAI telemetry is ON by default and collects version/OS/crew-shape data (PyPI description). The
same page documents the opt-out:

```sh
export CREWAI_DISABLE_TELEMETRY=true   # also: 1, yes, on
export OTEL_SDK_DISABLED=true          # same accepted values per the PyPI description
```

Set both before any proof run. Keep `share_crew` disabled: when it is enabled "detailed data
including task descriptions, agents' backstories or goals ... are collected" (PyPI description).
For local tracing, export OTel to a local collector instead of a hosted one; do not enable a
hosted observability backend without Gate-D.

## 10. Testing and evals (one planted failure that goes red)

- Deterministic fake model first: the `FakeLLM(BaseLLM)` above is the test seam; unit tests assert
  on `str(crew.kickoff())` with `temperature=0` semantics.
- Assertion style: assert the expected **marker content**, not "did not throw". An empty result is
  a failure.
- **Planted failure must fail the exit code, not print RED.** A caught AssertionError that prints
  `PLANTED_FAILURE_RED` and exits 0 proves nothing: an exit-code gate would pass it. The harness
  (`test_planted_crewai.py`) must leave the assertion UNCAUGHT so the plant run exits non-zero.
  Executed cycle here (2026-09-28): checksum `hello_crewai.py` (sha256 `bc214e71b6ea..`), plant
  `WRONG_PLANTED` into the fake (sha `01240f338e37..`; **refuse the plant if the bytes did not
  move**), run the harness and record the real **exit 1** (RED, uncaught `AssertionError`), restore
  (sha back to `bc214e71b6ea..`, match verified) and record **exit 0** (GREEN). Clear `__pycache__`
  between runs: a same-length plant token plus same-second mtime can leave a stale `.pyc` faking a
  green. Keep the planted file as a regression fixture.
- Telemetry and network must be off during tests so a red means the code, not the environment.

## 11. Deploy / self-host (Gate-D)

Local `crewai run` on Mike's Mac is fine. **Gate-D, do not do without Mike's explicit approval:**
CrewAI AMP signup (`app.crewai.com`), CrewAI Factory / cloud deployment, any paid plan, any public
URL, any push. `agentic-deploy-gate` owns the checklist.

## 12. Teardown and upgrade

```sh
rm -rf ~/.rig/agentic-lab/crewai/.venv            # teardown the environment
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python -U crewai==<new-pin>
.venv/bin/python -c "import crewai; print(crewai.__version__)"   # verify after upgrade
```

Re-run the fake-model hello-world after every upgrade; a version bump that changes the
`BaseLLM.call` signature breaks fakes first.

## 13. Gotchas (each tagged with where observed)

- **HTTP 200 with empty content is not success.** qwen3.8-uncensored:27b returns empty content when
  thinking is enabled; disable it via `extra_body={"chat_template_kwargs": {"enable_thinking": false}}`
  and assert non-empty output. [observed here 2026-09-28, worker-verified endpoint behavior]
- **Native `.so` can be blocked by sandbox library validation** (`library load disallowed by system
  policy`, seen on pydantic-core during a CrewAI run here): `xattr -cr .venv` + one
  `codesign --force -s - <file.so>`, else BLOCKED (sandbox library validation) and prove from the
  Orca host shell. [observed here 2026-09-28]
- **PYTHONHOME/PYTHONPATH leak** from the Aside runtime breaks uv venvs and system python; always
  `env -u PYTHONHOME -u PYTHONPATH`. [observed here 2026-09-28]
- **Telemetry ships by default** unless `CREWAI_DISABLE_TELEMETRY`/`OTEL_SDK_DISABLED` are set.
  [docs: https://pypi.org/project/crewai]
- **Nightly `.devYYYYMMDD` builds** appear on PyPI beside the stable pin; install the exact pin.
  [observed here 2026-09-28 on PyPI JSON/RSS]
- **`BaseLLM` requires a non-empty model name**: `FakeLLM()` with no args raises
  `ValidationError: Model name is required and cannot be empty`; construct
  `FakeLLM(model="fake/deterministic")`. [observed here 2026-09-28]
- **This venv's pydantic-core 2.41.5 wheel was sandbox-blocked** while 2.46.5 loads: the working
  fix here was `uv pip install --reinstall-package pydantic --reinstall-package pydantic-core
  pydantic` (pydantic 2.13.5 + pydantic-core 2.46.5, then `import crewai` ok). [observed here 2026-09-28]
- **Python ceiling**: CrewAI refuses 3.14 (`>=3.10,<3.14`). [docs: https://docs.crewai.com/en/installation]

## 14. Proof receipts (claim only what ran)

| Command | Exit | Version | Date | Proof level |
| --- | --- | --- | --- | --- |
| WebFetch `https://pypi.org/pypi/crewai/json` (version pin) | 0 | 1.15.22 | 2026-09-28 | L0 |
| WebFetch `https://docs.crewai.com/en/installation` | 0 | - | 2026-09-28 | L0 |
| WebFetch `https://docs.crewai.com/en/concepts/llms` | 0 | - | 2026-09-28 | L0 |
| `uv pip install --python .venv/bin/python crewai==1.15.22` (lab venv) | 0 | 1.15.22 | 2026-09-28 | L1 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python hello_crewai.py` (FakeLLM) | 0 (`HELLO_CREWAI_GREEN`) | 1.15.22 | 2026-09-28 | L2 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python l3_crewai.py` (local endpoint 8657) | 0 (`L3_CREWAI_GREEN`, output `HELLO`, non-empty asserted) | 1.15.22 | 2026-09-28 | L3 |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python test_planted_crewai.py` with `WRONG_PLANTED` planted in `hello_crewai.py` (sha `bc214e71b6ea..` -> `01240f338e37..`, plant refused if bytes unchanged) | **1** (RED, uncaught `AssertionError`) | 1.15.22 | 2026-09-28 | L2 (planted-failure gate) |
| `env -u PYTHONHOME -u PYTHONPATH ../.venv/bin/python test_planted_crewai.py` after restore (sha back to `bc214e71b6ea..`, match verified) | 0 (GREEN) | 1.15.22 | 2026-09-28 | L2 (green after restore) |

Full command ledger: `references/proof.json`. A rung not in that file is not claimed.
