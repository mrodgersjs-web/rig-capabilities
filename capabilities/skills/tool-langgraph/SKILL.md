---
name: tool-langgraph
description: Build explicit state graphs, checkpointed threads, and human interrupts when a Design Harness slice is genuinely graph-shaped.
outcome: "code-engineering: graph-shaped orchestration has typed state, explicit edges, checkpoint identity, and resumable human decisions"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('langgraph') == '1.2.11'; from langgraph.graph import StateGraph; assert StateGraph(dict)"
great_example: "A bounded inner loop compiles a StateGraph with an InMemorySaver in tests, a thread_id on every invocation, and Command(resume=...) for review."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: "local:/Users/rig128gb/.claude/skills/langchain-architecture + registry:langchain-ai/langchain-skills"
---

# tool-langgraph

## Role in our stack

LangGraph 1.2.11 is an **Orchestration** option only when the process is a real state graph. Temporal remains the durable carrier. Use LangGraph for explicit state transitions, checkpointed conversational state, or human interrupts inside an activity; do not add it to a linear deterministic sequence.

## Verified snippets

### 1. Compile and invoke a graph

```python
from typing import TypedDict
from langgraph.graph import END, START, StateGraph

class State(TypedDict):
    value: int

graph = StateGraph(State).add_node("inc", lambda s: {"value": s["value"] + 1}).add_edge(START, "inc").add_edge("inc", END).compile()
assert graph.invoke({"value": 1}) == {"value": 2}
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/langgraph/verify.py 1` → exit 0.

### 2. Persist thread state

```python
import operator
from typing import Annotated, TypedDict
from langgraph.checkpoint.memory import InMemorySaver

class State(TypedDict):
    values: Annotated[list[str], operator.add]

# Pass InMemorySaver at compile time and thread_id at invoke time.
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/langgraph/verify.py 2` → exit 0.

### 3. Pause and resume a human decision

```python
from langgraph.types import Command, interrupt

# A node calls interrupt("approve?").
# Resume the same checkpointed thread with Command(resume=True).
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/langgraph/verify.py 3` → exit 0.

## Pitfalls

- Every checkpointed invocation requires `configurable.thread_id`.
- Code before `interrupt()` runs again on resume; keep outward effects after the decision.
- `InMemorySaver` is for tests and local development, not production durability.
- Do not duplicate Temporal retry, scheduling, or durable state in LangGraph.

## Planted failure

Omit `thread_id` from a checkpointed graph invocation. The persistence gate must reject it:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "from langgraph.checkpoint.memory import InMemorySaver; from langgraph.graph import StateGraph,START,END; g=StateGraph(dict).add_node('n',lambda s:s).add_edge(START,'n').add_edge('n',END).compile(checkpointer=InMemorySaver()); g.invoke({})"
```

Expected: non-zero exit naming a missing configurable checkpoint key.
