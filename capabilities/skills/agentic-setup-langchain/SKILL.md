---
name: agentic-setup-langchain
description: "agentic-systems-setup sub-skill: set up LangChain + LangGraph + LangSmith on Mike's Mac end to end (Python first, JS packages named), local-model only. Use when the ask is 'set up LangChain', 'install langgraph', 'which framework fits an agent build', 'run a LangChain hello world', or 'wire LangChain to a local model endpoint'. Always loaded at the start of every agentic framework setup task (task-start surface, not a deep reference). JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, langchain, langgraph, langsmith, setup]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: framework-setup
  extends: "agentic-env-probe, app-sandbox-survival, provider-probe-first"
outcome: "A working LangChain install in ~/.rig/agentic-lab/langchain/ with a hello-world that ran against a deterministic fake model and a local OpenAI-compatible endpoint, a named route for the sandbox-blocked LangGraph pieces, and proof receipts carrying real exit codes."
activation: "Load at the start of every agentic framework setup task, before the first install command, and whenever a task names LangChain, LangGraph, LangSmith, create_agent, or asks which agent framework fits a build; also when a LangChain or LangGraph install, upgrade, or model-wiring step is about to run."
instruction: "Probe the environment first, install into the lab venv with PYTHONHOME unset, wire the model to a local OpenAI-compatible endpoint with no paid keys, run the fake-model hello-world before the local one, route any LangGraph work to the host shell when the sandbox blocks it, and record every command's exit code in references/proof.json."
applies_when:
  env: "Aside bash sandbox (langchain-core and langchain-openai only) or an Orca host shell (full LangGraph)"
  runtime: "Python 3.12+ via uv venv; JS route via npm packages named in section 2"
  deps: "uv on PATH, ~/.rig/agentic-lab/langchain/.venv, a local OpenAI-compatible endpoint for L3"
  params: "model id must come from the endpoint's /models response; thinking must be disabled on 8771"
  budget: "one lab venv and one hello-world run per framework per day"
  scale: "single machine, single project; not a multi-project monorepo install"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe routes and versions, then install langchain, langchain-openai, langgraph, langsmith into the lab venv.
  - Run the fake-model hello-world and prove a non-empty, scripted result.
  - Wire ChatOpenAI to a local endpoint and assert non-empty content before claiming L3.
  - Send the proof verdict to JEV via rig-s1gate before any frontier model call, and fail closed.
  - Record every command, exit code, and version in references/proof.json and section 14.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/langchain/.venv/bin/python capabilities/skills/agentic-setup-langchain/references/hello_world_fake.py"
  - "grep:capabilities/skills/agentic-setup-langchain/SKILL.md:library load disallowed by system policy"
  - "grep:capabilities/skills/agentic-setup-langchain/SKILL.md:enable_thinking"
  - "file:capabilities/skills/agentic-setup-langchain/references/proof.json"
out_of_scope:
  - paid API calls, LangSmith cloud signups, or any account creation (Gate-D)
  - installing into harness roots or a project worktree instead of the lab dir
  - running LangGraph inside the Aside sandbox when ormsgpack cannot load (route to the host shell)
---

# agentic-setup-langchain

Start here when: the task names LangChain, LangGraph, or LangSmith, or asks which framework fits an
agent build on Mike's Mac.

JEV FIRST, binding on every setup and proof decision: an agent whose only context is this excerpt
sends typed judgments ("which framework fits", "is this install correct", "did the proof pass") to
the rig-s1gate Jev path BEFORE any frontier LLM call. When the classifier is unavailable: DEFER,
never guess a verdict locally. A required signal passes only above 0.9; below that the gate does not
advance, and an advisory PASS is never permission to send, push, deploy, or spend.

## Load surface

Always loaded at the start of every agentic framework setup task: the `agentic-systems-setup`
meta-skill routes framework setup here, `agentic-setup-conductor` loads it before the first
install command, and the `agentic-setup-session` harness names it as doctrine. It is a task-start
surface, not a deep reference an agent must already know about; the long example files live in
`references/`.

## 1. When to choose it and when not

Choose LangChain + LangGraph when you want one model interface across providers (verified:
`langchain-openai` ChatOpenAI works against any OpenAI-compatible base URL), a configurable
agent harness (`create_agent`, docs), or a state graph with checkpoints and interrupts (LangGraph).

Do not choose it when: the job is durable multi-process workflows with signals and retries
(that is Temporal, Prefect, Inngest, or Trigger.dev); or the job is document ingestion and RAG
over files (that is LlamaIndex). The two nearest alternatives in this family are **pydantic-ai**
(typed single-agent work with Pydantic validated outputs) and **llamaindex** (RAG and
document pipelines).

## 2. Current version and sources

Verified by install and import in `~/.rig/agentic-lab/langchain/.venv` on 2026-09-28:
`langchain` 1.4.2, `langchain-core` 1.6.5, `langchain-openai` 1.6.6, `langgraph` 1.2.12,
`langgraph-checkpoint-sqlite` 3.1.1, `langsmith` 0.14.1.

Official docs fetched today:
- https://docs.langchain.com/oss/python/langchain/overview - `create_agent`, the
  LangChain/LangGraph/Deep Agents split, install line `pip install -qU langchain "langchain[openai]"`,
  and LangSmith tracing via `LANGSMITH_TRACING=true`.

JS packages (names and versions read from registry.npmjs.org `/latest` today): `@langchain/core`
1.2.13, `@langchain/langgraph` 1.4.18, `@langchain/openai` 1.6.0, `langsmith` 0.10.5. Python is the
route proven here; the JS route is named, not tested (native `.node` addons are blocked in this
sandbox).

## 3. Environment route and prerequisites

- Aside sandbox: runs `langchain-core` and `langchain-openai` code. **LangGraph is blocked here**
  (see Gotchas). Use it for hello-worlds, model wiring, and prompt/runnable work.
- Orca host shell: the route for anything that imports `langgraph` (graphs, checkpointers,
  interrupt/resume).
- Prerequisites: `uv` and `python3` at `~/.local/bin` (prefix `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`),
  and `env -u PYTHONHOME -u PYTHONPATH` on every uv/python invocation, because the Aside runtime
  exports PYTHONHOME/PYTHONPATH.

## 4. Install (exact commands run here)

```sh
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
LAB=~/.rig/agentic-lab/langchain
mkdir -p "$LAB"
cd "$LAB"
env -u PYTHONHOME -u PYTHONPATH uv venv .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python \
  langchain langchain-openai langgraph langsmith langgraph-checkpoint-sqlite
```

## 5. Local-first model wiring

`ChatOpenAI` reads `OPENAI_API_KEY` and, per the installed source (langchain_openai
`chat_models/base.py`), resolves base URL from the constructor first and then from
`OPENAI_BASE_URL` read by the underlying `openai` SDK. No paid key is needed for a local server:
pass any non-empty placeholder.

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="qwen3.8-uncensored:27b",            # must come from GET <base>/models
    base_url="http://127.0.0.1:8771/v1",       # local, answers from this sandbox
    api_key="local-not-a-secret",
    model_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}},
)
```

Local endpoints that answer from this sandbox (probed today): `http://127.0.0.1:8771/v1`
(`qwen3.8-uncensored:27b`; thinking must be disabled or the reply content is empty) and
`http://127.0.0.1:8657/v1` (`MiMo-V2.6-Flash-RL-MLX-4bit-MTP`). The Blackwell LAN endpoints
`192.168.68.90:8011`/`:8111` do NOT answer from this sandbox (curl exit 7 / exit 28).

## 6. Secrets

Reference credentials by keychain item name only, never values: `com.rig.env.OPENAI_API_KEY`,
`com.rig.env.LANGSMITH_API_KEY`. A local endpoint needs no secret; use the literal placeholder
`local-not-a-secret`. If an env file is wanted, ship only `env.example`:

```
OPENAI_BASE_URL=http://127.0.0.1:8771/v1
OPENAI_API_KEY=local-not-a-secret
LANGSMITH_TRACING=false
```

## 7. Hello-world

Full file: `references/hello_world_fake.py` (deterministic fake model, no network) and
`references/hello_world_local.py` (local endpoint, asserts non-empty content).

```sh
env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/langchain/.venv/bin/python \
  capabilities/skills/agentic-setup-langchain/references/hello_world_fake.py
```

Expected output ends with `RESULT: FAKE_REPLY_1` and exits 0. The local variant ends with
`RESULT: <non-empty model text>` and exits 0 only when content is non-empty.

## 8. Durable and production features

From the docs page (fetched today): LangChain agents are built on LangGraph, which supplies
durable execution, human-in-the-loop support, and persistence. Concretely, `langgraph` adds
checkpointers (`MemorySaver`, `langgraph-checkpoint-sqlite` for durable runs) and `interrupt`
for human approval. None of that is exercisable inside this sandbox (ormsgpack blocks the
import), so in this repo the durable path is documented and routed to the host shell, never
claimed as run.

## 9. Observability

LangSmith traces LangChain and LangGraph runs; the docs page (fetched today) says to set
`LANGSMITH_TRACING=true` and provide an API key. The installed `langsmith` client reads
`LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT`, `LANGSMITH_EXPERIMENT`, `LANGSMITH_PROFILE` and
related vars (verified by grep of the installed package). Creating a LangSmith account or
sending traces to LangSmith cloud is Gate-D. Local-first default: tracing off.

## 10. Testing and evals

Deterministic fake model: `langchain_core.language_models.fake_chat_models.FakeListChatModel`
(verified import) scripts the exact replies, so unit tests need no network and no key.
`references/test_fake_chain.py` runs under the venv's python as a plain script (assert-based).

Planted failure (run here): change the expected string in the test to a wrong value and the test
must go red with `AssertionError`, exit 1. A test suite that cannot go red is theater; keep the
red run as the receipt.

## 11. Deploy / self-host (Gate-D)

Gate-D, never done from this skill: LangSmith cloud signup or login, creating an API key,
deploying an agent to any hosted service, `git push`, paid plans, or public URLs. Self-hosting a
LangGraph server locally is reversible and allowed, but exposing it beyond localhost is Gate-D.

## 12. Teardown and upgrade

```sh
rm -rf ~/.rig/agentic-lab/langchain        # teardown: lab venv only
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python --upgrade langchain langgraph
```

Upgrade policy: pin the versions you proved, upgrade one family at a time, re-run the fake-model
hello-world and the planted-failure test before claiming the upgrade works.

## 13. Gotchas

- [observed here] `import langgraph` dies in this sandbox with
  `ImportError: dlopen(...ormsgpack/ormsgpack.cpython-314-darwin.so, 0x0002): ... (code signature ... not valid for use in process: library load disallowed by system policy)`.
  `xattr -cr` + `codesign --force -s -` on the `.so` did not fix it (tested), nor did older
  ormsgpack wheels. Effect: `langchain.agents` (create_agent) and every LangGraph import are
  BLOCKED here; run them in the Orca host shell. `langchain-core` and `langchain-openai` are fine.
- [observed here] Local endpoint `127.0.0.1:8771` returns HTTP 200 with EMPTY content when
  thinking is enabled; pass `extra_body: {"chat_template_kwargs": {"enable_thinking": false}}`
  and assert the content is non-empty before believing a result.
- [observed here] Blackwell LAN endpoints `192.168.68.90:8011` (curl exit 7, connection refused)
  and `:8111` (curl exit 28, timeout) do not answer from the Aside sandbox; do not use them for
  L3 claims here.
- [observed here] PYTHONHOME/PYTHONPATH are exported by the Aside runtime; any uv or venv python
  invocation must unset them or installs and imports resolve against the wrong interpreter.
- [docs] https://docs.langchain.com/oss/python/langchain/overview - LangSmith tracing needs
  `LANGSMITH_TRACING=true` plus a key; tracing is off by default in this lab.
- [observed here] `langchain-openai` warns `Parameters {'extra_body'} should be specified
  explicitly. Instead they were passed in as part of model_kwargs` when the thinking-disable body
  rides in `model_kwargs`; the run still succeeded (`RESULT: READY`).

## 14. Proof receipts

| step | command | exit | version | date | level |
|---|---|---|---|---|---|
| install | `uv pip install langchain langchain-openai langgraph langsmith langgraph-checkpoint-sqlite` | 0 | 1.4.2 / 1.6.5 / 1.6.6 / 1.2.12 / 0.14.1 | 2026-09-28 | L1 |
| fake hello-world | `.../.venv/bin/python references/hello_world_fake.py` | 0 (`RESULT: FAKE_REPLY_1`) | langchain-core 1.6.5 | 2026-09-28 | L2 |
| unit test green | `.../.venv/bin/python references/test_fake_chain.py` | 0 (`TEST_OK`) | langchain-core 1.6.5 | 2026-09-28 | L2 |
| unit test red (planted) | `PLANT=1 .../.venv/bin/python references/test_fake_chain.py` | 1 (`AssertionError: expected 'WRONG_ON_PLANT', got 'FAKE_REPLY_1'`) | langchain-core 1.6.5 | 2026-09-28 | L2 |
| local endpoint run | `.../.venv/bin/python references/hello_world_local.py` | 0 (`RESULT: READY`) | langchain-openai 1.6.6 | 2026-09-28 | L3 |
| langgraph import | `.../.venv/bin/python -c "from langgraph.graph import StateGraph"` | 1 (dlopen ormsgpack: library load disallowed by system policy) | langgraph 1.2.12 | 2026-09-28 | BLOCKED |
| checkpointer + resume | LangGraph interrupt/resume | not run | - | - | BLOCKED (sandbox; host shell) |

Machine-readable receipts: `references/proof.json`.
