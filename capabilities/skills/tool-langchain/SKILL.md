---
name: tool-langchain
description: "Use LangChain core primitives (messages, runnables, prompts) via `langchain-core` 1.6.3. The top-level `langchain` package is ABSENT in the design-harness venv; install only when chains/agents are required."
outcome: "code-engineering: a runnable built from langchain-core primitives has typed messages, the Runnable protocol, and a docstring'd interface that does not depend on the absent `langchain` package"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('langchain-core') == '1.6.3'; from langchain_core.messages import HumanMessage, SystemMessage, AIMessage; from langchain_core.prompts import ChatPromptTemplate; from langchain_core.runnables import RunnableLambda; assert all([HumanMessage, ChatPromptTemplate, RunnableLambda])"
great_example: "A pipeline of `ChatPromptTemplate | RunnableLambda | RunnableLambda` is invoked with a dict input, returns a typed `AIMessage`, and traces to LangSmith via `LANGSMITH_TRACING=true` without any extra wiring."
quality_floor: 0.7
relates_to: rig-design-harness, obs/langgraph
provenance: "local:rig-capabilities/cells/obs/langgraph"
---

# tool-langchain

## Role in our stack

`langchain-core` 1.6.3 is installed in
`~/Developer/rig-intelligence/packages/rig-design-harness/.venv`. The
**top-level `langchain` package is ABSENT** there. That is deliberate on
this fleet:

- Use `langchain-core` directly for messages, prompts, and the Runnable
  protocol — the orchestrating cells rely on these without depending on the
  heavier `langchain` package.
- Use `langgraph` for **state graphs** (see `tool-langgraph`,
  `obs/langgraph`). `langgraph` is the right answer when the process has
  branches, checkpoints, or interrupts.
- Use Temporal for **durable workflows** with retries / signals /
  cross-process state. Don't make `langchain` carry that.
- Install `langchain` only when `langchain.chains` or `langchain.agents`
  is required; that decision is out-of-scope for this skill.

## Verified snippets

### 1. Typed messages

```python
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
msgs = [
    SystemMessage(content="You are a precise extractor."),
    HumanMessage(content="Extract: 'Acme Corp, 12 employees, Denver CO'"),
]
```

### 2. Chat prompt template

```python
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a precise extractor."),
    ("human", "Extract: {text}"),
])
value = prompt.invoke({"text": "Acme Corp, 12 employees, Denver CO"})
```

### 3. Compose a runnable

```python
from langchain_core.runnables import RunnableLambda
pipeline = (
    prompt
    | RunnableLambda(lambda v: {"extracted": "Acme"})
    | RunnableLambda(lambda v: AIMessage(content=v["extracted"]))
)
out = pipeline.invoke({"text": "Acme Corp"})
assert isinstance(out, AIMessage)
```

### 4. Tracing — auto, no extra wiring

With `LANGSMITH_TRACING=true` in env (and the model client wrapped via
`wrap_openai` from `tool-langsmith`), every `invoke()` lands a span. No
`@traceable` decorator needed; the Runnable protocol is auto-instrumented.

## Pitfalls

- Importing from `langchain.chains` or `langchain.agents` will raise
  `ModuleNotFoundError` until the top-level `langchain` package is
  installed. **Do not install it speculatively.** Decide first whether
  the chains/agents API is needed.
- `langchain_core.messages` and `langchain_core.prompts` exist; `langchain`
  (no underscore) does NOT export them in the installed env. Never
  `from langchain.messages import ...` — that path does not exist.
- `ChatPromptTemplate.from_messages` accepts the `(role, content)` tuple
  form. The deprecated list-of-`BaseMessage` form still works but produces
  a deprecation warning.
- `RunnableLambda` is **synchronous**. For async, use `RunnableLambda`
  with a coroutine body and run via `.ainvoke()`. Mixing sync and async
  in the same pipeline raises at first `.invoke()`.
- LangChain auto-tracing requires `LANGSMITH_TRACING=true` to be set at
  import time. Changing it mid-process requires a restart.

## Planted failure

The top-level `langchain` package must NOT be importable from the design
harness venv; if a missing dep was silently added, this gate fails to RED
and exposes the dependency drift:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib, sys; spec = importlib.util.find_spec('langchain'); sys.exit(0 if spec is None else 1)"
```

Expected: exit 0 (langchain absent). If exit 1, langchain was installed
without approval — the gate catches that.
