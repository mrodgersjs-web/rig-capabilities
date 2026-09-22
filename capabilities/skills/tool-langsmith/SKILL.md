---
name: tool-langsmith
description: "Instrument Design Harness runs with LangSmith SDK traces, datasets, evaluators, and annotation queues while keeping offline tests network-free. Pinned langsmith 0.12.6."
outcome: "data-analytics: every evaluated run can carry complete trajectory attributes, run_ids, and scores into the LangSmith ledger adapter"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('langsmith') == '0.12.6'; from langsmith import Client, traceable; assert Client and traceable"
great_example: "A benchmark run carries lane, run_id, day, stage, status, and gate attributes under @traceable + propagate_attributes, with `LANGSMITH_TRACING=false` in tests and `LANGSMITH_TRACING=true` in live."
quality_floor: 0.7
relates_to: rig-design-harness, obs/langsmith
provenance: "local:rig-capabilities/cells/obs/langsmith"
---

# tool-langsmith

## Role in our stack

LangSmith 0.12.6 is the **primary cloud ledger** for runs that produce
labelled data or run an evaluator. It is not the runtime carrier — that is
LangGraph or Temporal — it records what happened. The orchestrating cell
tree lives at `capabilities/cells/obs/langsmith/`; this skill is the
**API-fact leaf** with version-verified snippets.

Verified against the installed `langsmith 0.12.6` (in
`~/Developer/rig-intelligence/packages/rig-design-harness/.venv`) on
2026-09-20. The **only** authoritative source for API shapes is the
installed package; this file mirrors that, not docs or memory.

## Verified snippets

### 1. Wrap a model client (auto-instrument chat completions)

```python
from openai import OpenAI
from langsmith.wrappers import wrap_openai
client = wrap_openai(OpenAI())
resp = client.chat.completions.create(model="gpt-5", messages=[{"role":"user","content":"ping"}])
```

Requires `LANGSMITH_TRACING=true` in env (read at import time, not in code).

### 2. Decorate a function (non-LangChain)

```python
from langsmith import traceable
@traceable(name="rig-extract", metadata={"lane":"rig","stage":"extract","gate":"none"})
def extract(text: str) -> dict:
    return {"len": len(text)}
```

### 3. Read the current run tree

```python
from langsmith.run_helpers import get_current_run_tree
rt = get_current_run_tree()
assert rt is not None
rt.metadata = {"day": "2026-09-20"}
```

### 4. Run an experiment offline-safe

```python
from langsmith import evaluate
def has_no_pii(run, example):
    return {"key": "no_pii", "score": int("@" not in (run.outputs or {}).get("text",""))}

results = evaluate(
    target=lambda x: x,
    data="foundry-prod-samples",
    evaluators=[has_no_pii],
    experiment_prefix="rig-pii-baseline",
    max_concurrency=2,
    upload_results=False,                # dry-run first
    error_handling="log",
)
```

## API surface (verified 0.12.6)

**Wrappers:** `langsmith.wrappers.wrap_openai`, `wrap_anthropic`,
`wrap_gemini`, `OpenAIAgentsTracingProcessor`. **No** `wrap_langchain`,
**no** `wrap_openai_responses`.

**Client methods that exist:** `create_feedback, create_prompt, pull_prompt,
get_prompt, create_dataset, list_runs, create_run, share_run, evaluate,
aevaluate, evaluate_existing, evaluate_comparative, delete_dataset,
list_datasets, read_dataset, run_evaluator`.
**Methods that DO NOT exist:** `read_runs` (use `list_runs`),
`upload_run_multipart` (removed), `list_shared_prompts`, `update_dataset`.

**Eval family:** `langsmith.evaluation.{evaluate, aevaluate,
evaluate_existing, evaluate_comparative, run_evaluator,
EvaluationResult, RunEvaluator, StringEvaluator}`.

**Testing helpers:** `langsmith.testing.{log_inputs, log_outputs,
log_reference_outputs, log_feedback, trace_feedback}`.

**Current-span accessor:** `langsmith.run_helpers.get_current_run_tree()`.
The older `update_current_span` and `current_trace_tree` are **gone**.

## Env vars (verified by grep of installed package)

`LANGSMITH_API_KEY`, `LANGSMITH_ENDPOINT`, `LANGSMITH_TRACING`,
`LANGSMITH_PROJECT`, `LANGSMITH_WORKSPACE_ID`, `LANGSMITH_TRACING_V`,
`LANGSMITH_TRACING_MODE` (otel | default), `LANGSMITH_TRACING_SAMPLING_RATE`,
`LANGSMITH_TAGS`, `LANGSMITH_NAME`, `LANGSMITH_OTEL_SPAN_TTL_SECONDS`,
`LANGSMITH_RUNTIME`. The legacy `LANGCHAIN_*` names still alias
(`LANGCHAIN_API_KEY`, `LANGCHAIN_ENDPOINT`, `LANGCHAIN_PROJECT`,
`LANGCHAIN_TRACING_V`).

## Account context (read from this account on 2026-09-20)

- Org `RIG`, Workspace 1, account `rodgemd1@gmail.com`.
- 1 dataset: `foundry-prod-samples`, 56 examples, 0 experiments.
- 0 evaluators. 1 annotation queue. 30 prompts.
- 6 active API keys; only `foundry-v20-trace-v3` has been used in 2026.
- 0 MCP servers configured. The LangSmith MCP server exists and offers
  `list_model_price_maps` (changelog 2026-09-14) plus trace-query tools;
  adding it lets agents in this fleet reach the ledger without the Python
  client.
- SaaS retention cap dropped to **180 days on 2026-09-14** (changelog
  confirmed); settings above 180 are rejected; self-hosted and BYOC
  unchanged.

## Pitfalls

- `Client(api_key="x", timeout=5)` **raises `TypeError`** in 0.12.6 — the
  `timeout` kwarg is not on Client. Use `LANGSMITH_REQUEST_TIMEOUT` env
  var or set it on the private `_httpx_client` after construction.
- `tracing_enabled` exists on `Langfuse`, not `langsmith.Client`. Use
  `LANGSMITH_TRACING=false` in env to disable.
- `evaluate(..., error_handling="raise")` is **not** a valid value; only
  `"log"` or `"ignore"`.
- `wrap_langchain` does not exist. To instrument LangChain pipelines,
  wrap the model client and decorate inner steps with `@traceable`.
- A span missing `lane / run_id / day / stage / status / gate` (the obs
  trace contract) is un-attributable; the orchestrating cell refuses to
  close.
- A span with `LANGSMITH_TRACING_V` flipped mid-process is unsupported;
  restart the process.

## Planted failure

The attribute-completeness gate must go RED on a missing `gate`:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "required={'lane','run_id','day','stage','status','gate'}; attrs={'lane':'x','run_id':'r','day':'d','stage':'s','status':'ok'}; missing=required-attrs.keys(); assert not missing, f'missing span attributes: {sorted(missing)}'"
```

Expected: non-zero exit naming `gate`.
