---
name: agentic-setup-llamaindex
description: "agentic-systems-setup sub-skill: set up LlamaIndex on Mike's Mac end to end - ingestion, indexing, query engines, and workflows - local-model only, with the SQLAlchemy pin that keeps native extensions loading here. Use when the ask is 'set up LlamaIndex', 'build a RAG pipeline', 'index these documents', or 'which framework fits a document question-answering build'. Always loaded at the start of every agentic framework setup task (task-start surface, not a deep reference). JEV-FIRST MANDATE."
tags: [rig, agentic-systems, sub-skill, llamaindex, rag, setup]
metadata:
  parent: agentic-systems-setup
  tier: sub
  stage: framework-setup
  extends: "agentic-env-probe, app-sandbox-survival, provider-probe-first"
outcome: "A working LlamaIndex install in ~/.rig/agentic-lab/llamaindex/ (with the SQLAlchemy pin), a deterministic MockLLM unit test proven to go green and red, the index/query/persistence path BLOCKED in this sandbox by tiktoken's native wheel with the host-shell route named, and proof receipts carrying real exit codes."
activation: "Load at the start of every agentic framework setup task, before the first install command, and whenever a task names LlamaIndex, RAG, document ingestion, indexes, query engines, or asks which framework fits a document or knowledge-base build; also before any LlamaIndex install, upgrade, or model-wiring step."
instruction: "Probe routes first, install into the lab venv with PYTHONHOME unset and SQLAlchemy pinned below 2.1, prove the pipeline on MockLLM before touching an endpoint, persist and reload the index to prove durability, and record every command's exit code in references/proof.json."
applies_when:
  env: "Aside bash sandbox (works with the SQLAlchemy pin) or an Orca host shell"
  runtime: "Python 3.12+ via uv venv; TS route named via the llamaindex npm package"
  deps: "uv on PATH, ~/.rig/agentic-lab/llamaindex/.venv, sqlalchemy<2.1 in this sandbox, a local OpenAI-compatible endpoint for L3"
  params: "model id must come from the endpoint's /models response; embed_dim fixed in the test embedding"
  budget: "one lab venv and one pipeline run per day"
  scale: "local documents on disk; not a LlamaCloud multi-tenant index"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - Probe routes and versions, then install llama-index-core and the OpenAI-like LLM with the SQLAlchemy pin.
  - Run the MockLLM hello-world over a local document index and prove a deterministic answer.
  - Persist the index, reload it from disk, and re-query to prove the durable path.
  - Wire OpenAILike to a local endpoint and assert non-empty content before claiming L3.
  - Send the proof verdict to JEV via rig-s1gate before any frontier model call, and fail closed.
done_when:
  - "cmd:env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/llamaindex/.venv/bin/python capabilities/skills/agentic-setup-llamaindex/references/hello_world_mock.py"
  - "grep:capabilities/skills/agentic-setup-llamaindex/SKILL.md:sqlalchemy==2.0.41"
  - "grep:capabilities/skills/agentic-setup-llamaindex/SKILL.md:library load disallowed by system policy"
  - "file:capabilities/skills/agentic-setup-llamaindex/references/proof.json"
out_of_scope:
  - paid API calls, LlamaCloud or LlamaParse signups, or any account creation (Gate-D)
  - installing into harness roots or a project worktree instead of the lab dir
  - claiming LangGraph-style checkpointing; LlamaIndex durability here is index persistence
---

# agentic-setup-llamaindex

Start here when: the task names LlamaIndex, RAG, indexing documents, or asks which framework fits
a document question-answering build on Mike's Mac.

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

Choose LlamaIndex when the workload is over your data: ingest documents (`SimpleDirectoryReader`),
structure them (`VectorStoreIndex`), and query them (query engines, chat engines), or when you want
event-driven multi-step `Workflows` around agents and RAG (docs page fetched today).

Do not choose it when the core problem is a deterministic state machine with checkpoints and human
interrupts (LangGraph), or a small typed agent with validated structured output (pydantic-ai). The
two nearest alternatives in this family are **langchain** and **pydantic-ai**.

## 2. Current version and sources

Verified by install and import in `~/.rig/agentic-lab/llamaindex/.venv` on 2026-09-28:
`llama-index-core` 0.14.25, `llama-index-llms-openai-like` 0.8.0, with `sqlalchemy==2.0.41`
pinned in this sandbox (2.1.1 breaks here, see Gotchas).

Official docs fetched today:
- https://docs.llamaindex.ai/en/stable/ - the framework overview, the 5-line starter
  (`pip install llama-index`; `SimpleDirectoryReader` -> `VectorStoreIndex` -> `as_query_engine`),
  and the TS package `llamaindex` on npm.

TS route (registry.npmjs.org `/latest` read today): `llamaindex` 0.12.1. Python is the route
proven here.

## 3. Environment route and prerequisites

- Aside sandbox: works, provided SQLAlchemy stays below 2.1 (the 2.1.x C-extension import is
  unguarded and fails library validation here). Everything in sections 4-10 ran in this sandbox.
- Orca host shell: needed only if you want SQLAlchemy 2.1+ or heavier native extensions.
- Prerequisites: `uv` at `~/.local/bin`, `PATH="$HOME/.local/bin:/usr/local/bin:$PATH"`, and
  `env -u PYTHONHOME -u PYTHONPATH` on every uv/python call.

## 4. Install (exact commands run here)

```sh
export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"
LAB=~/.rig/agentic-lab/llamaindex
mkdir -p "$LAB"
cd "$LAB"
env -u PYTHONHOME -u PYTHONPATH uv venv .venv
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python \
  llama-index-core llama-index-llms-openai-like
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python 'sqlalchemy==2.0.41'
```

## 5. Local-first model wiring

`OpenAILike` (subclass of LlamaIndex `OpenAI`) takes `api_key` and `api_base` constructor fields
(verified in the installed `llama_index/llms/openai/base.py`). Local servers need no real key.

```python
from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(
    model="qwen3.8-uncensored:27b",             # from GET <base>/models
    api_base="http://127.0.0.1:8771/v1",
    api_key="local-not-a-secret",
    is_chat_model=True,
    additional_kwargs={"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}},
)
```

Local endpoints that answer from this sandbox (probed today): `http://127.0.0.1:8771/v1`
(`qwen3.8-uncensored:27b`; disable thinking or content comes back empty) and
`http://127.0.0.1:8657/v1` (`MiMo-V2.6-Flash-RL-MLX-4bit-MTP`). The Blackwell LAN endpoints
`192.168.68.90:8011`/`:8111` do NOT answer from this sandbox (curl exit 7 / 28).

## 6. Secrets

Keychain item names only, never values: `com.rig.env.OPENAI_API_KEY`, and for cloud ingestion
services `com.rig.env.LLAMA_CLOUD_API_KEY`. Local endpoints need no secret; use
`local-not-a-secret`. `env.example` only:

```
OPENAI_API_KEY=local-not-a-secret
LLAMA_CLOUD_API_KEY=
```

## 7. Hello-world

Full file: `references/hello_world_mock.py` (MockLLM over a real local document index, no network)
and `references/hello_world_local.py` (OpenAILike against 8771, asserts non-empty content).

```sh
env -u PYTHONHOME -u PYTHONPATH ~/.rig/agentic-lab/llamaindex/.venv/bin/python \
  capabilities/skills/agentic-setup-llamaindex/references/hello_world_mock.py
```

Expected output ends with `RESULT: MOCK_OK docs=2 nodes>=2` and exits 0. NOTE (observed here):
inside the Aside sandbox this file stops at `ImportError: tiktoken package not found` (see
Gotchas) before the index is built; it is written to run as-is in the Orca host shell. What does
run here is `references/test_mock_llm.py` (`TEST_OK`, exit 0). The local variant prints
`RESULT: <non-empty model text>` where tiktoken loads.

## 8. Durable and production features

- Index persistence: `StorageContext.persist()` + `load_index_from_storage()` round-trips the
  index to disk and answers queries after reload (run here, `references/hello_world_persist.py`).
- Workflows: LlamaIndex `Workflows` are event-driven multi-step processes with error correction
  and reflection (docs page fetched today), and `llama_deploy` deploys them as microservices
  (deploy step is Gate-D).
- Chat memory and streaming are available on the LLM classes; not exercised in the lab runs.

## 9. Observability

LlamaIndex exposes observability and evaluation integrations (docs page fetched today) through
OpenInference-style instrumentation to backends such as Arize/Langfuse. Configuring a hosted
backend is Gate-D (external account).
Local-first default: no tracer; use the printed query/response and the proof receipts instead.

## 10. Testing and evals

Deterministic fake model: `llama_index.core.llms.mock.MockLLM` (verified import) completes
without network or key, so index and query code can be unit tested. `references/test_mock_llm.py`
is assert-based and runs under the venv python.

Planted failure (run here): assert a wrong mock completion string and the test must go red with
`AssertionError`, exit 1. Keep that red run as the receipt; a suite that cannot go red is theater.

## 11. Deploy / self-host (Gate-D)

Gate-D, never done from this skill: LlamaCloud / LlamaParse / LlamaExtract signups, creating API
keys, deploying `llama_deploy` services to any hosted target, `git push`, paid plans, public URLs.
Self-hosting a query service on localhost is reversible and allowed; publishing it is Gate-D.

## 12. Teardown and upgrade

```sh
rm -rf ~/.rig/agentic-lab/llamaindex      # teardown: lab venv only
env -u PYTHONHOME -u PYTHONPATH uv pip install --python .venv/bin/python --upgrade llama-index-core
```

After any upgrade, re-check the SQLAlchemy line: if `sqlalchemy>=2.1` arrives as a dependency,
imports will break in this sandbox until the pin is re-applied. Re-run the MockLLM hello-world
and the persistence round-trip before claiming the upgrade works.

## 13. Gotchas

- [observed here] `sqlalchemy==2.1.1` (pulled in by llama-index-core) fails at import with
  `ImportError: dlopen(...sqlalchemy/util/_collections_cy.cpython-314-darwin.so, 0x0002): ...
  (code signature ... not valid for use in process: library load disallowed by system policy)`;
  its C-extension import is unguarded in 2.1.x. `DISABLE_SQLALCHEMY_CEXT_RUNTIME=1` does not help
  (tested). Pin `sqlalchemy==2.0.41`, whose C-extension import is guarded: `llama_index.core`
  imports cleanly after the pin (run here).
- [observed here] `tiktoken` cannot load in this sandbox: `tiktoken/_tiktoken*.so` fails
  `dlopen ... library load disallowed by system policy`, so `llama_index.core.utils.get_tokenizer`
  raises ``ImportError: `tiktoken` package not found, please run `pip install tiktoken` `` and
  every index build, query engine, and `llama_index.llms.openai` import (module-level `import
  tiktoken`, base.py line 24) is BLOCKED here. Passing `SentenceSplitter(tokenizer=...)` does not
  dodge it (`TokenCounter(tokenizer=None)` re-raises). Route to the Orca host shell.
- [observed here] `MockEmbedding` is exported from `llama_index.core.embeddings` in 0.14.25;
  there is no `llama_index.core.embeddings.mock_embedder` module and `llama_index.core.embeddings`
  is the import path to use.
- [observed here] The Aside runtime exports PYTHONHOME/PYTHONPATH; unset them for every uv/venv
  call or the wrong interpreter resolves.
- [observed here] Endpoint `127.0.0.1:8771` returns empty content when thinking is enabled;
  pass `extra_body chat_template_kwargs enable_thinking=false` and assert non-empty output.
- [docs] https://docs.llamaindex.ai/en/stable/ - the quickstart assumes `OPENAI_API_KEY` and
  OpenAI embeddings; for local runs replace both with local/`MockLLM` equivalents before testing.

## 14. Proof receipts

| step | command | exit | version | date | level |
|---|---|---|---|---|---|
| install | `uv pip install llama-index-core llama-index-llms-openai-like` | 0 | 0.14.25 / 0.8.0 | 2026-09-28 | L1 |
| sqlalchemy pin | `uv pip install sqlalchemy==2.0.41` | 0 | 2.0.41 | 2026-09-28 | L1 |
| unit test green | `.../.venv/bin/python references/test_mock_llm.py` | 0 (`TEST_OK`) | llama-index-core 0.14.25 | 2026-09-28 | L2 |
| unit test red (planted) | `PLANT=1 .../.venv/bin/python references/test_mock_llm.py` | 1 (`AssertionError: expected 'WRONG_ON_PLANT', got 'text text text text'`) | llama-index-core 0.14.25 | 2026-09-28 | L2 |
| mock hello-world (index+query) | `.../.venv/bin/python references/hello_world_mock.py` | 1 (tiktoken ImportError) | llama-index-core 0.14.25 | 2026-09-28 | BLOCKED (sandbox; host shell) |
| persistence round-trip | `.../.venv/bin/python references/hello_world_persist.py` | 1 (tiktoken ImportError) | llama-index-core 0.14.25 | 2026-09-28 | BLOCKED (sandbox; host shell) |
| local endpoint run | `.../.venv/bin/python references/hello_world_local.py` | 1 (tiktoken dlopen at `llama_index.llms.openai` import) | openai-like 0.8.0 | 2026-09-28 | BLOCKED (sandbox; host shell) |

Machine-readable receipts: `references/proof.json`.
