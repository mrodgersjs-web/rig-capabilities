---
name: tool-pydantic-ai
description: Build and test typed Pydantic AI agents for the RIG Design Harness without network-dependent verification.
outcome: "code-engineering: Runtime and Orchestration model stages have typed inputs, typed outputs, stable names, and offline TestModel proof"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('pydantic-ai-slim') == '2.43.0'; from pydantic_ai import Agent; from pydantic_ai.models.test import TestModel; assert Agent(TestModel(), name='check').name == 'check'"
great_example: "A Design Harness proposer uses Agent(TestModel(), output_type=Proposal) in tests and the production agent has the same stable name and output schema."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: registry:pydantic/skills
---

# tool-pydantic-ai

## Role in our stack

Pydantic AI 2.43.0 owns typed LLM stages in the **Runtime** and **Orchestration** components: `Agent`, Pydantic `output_type`, stable agent names for Temporal, tool schemas, and offline `TestModel` verification. The official `pydantic-ai-harness` skill is also sourced, but CodeMode is optional and requires the separate `pydantic-ai-harness[codemode]` package; the reusable Design Harness does not assume it is installed.

## Verified snippets

### 1. Construct a named offline agent

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

agent = Agent(TestModel(), name="rig_specialist")
assert agent.name == "rig_specialist"
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/pydantic-ai/verify.py 1` → exit 0.

### 2. Bind a tool and structured output

```python
from pydantic import BaseModel
from pydantic_ai import Agent, Tool
from pydantic_ai.models.test import TestModel

class Score(BaseModel):
    value: int

def double(value: int) -> int:
    return value * 2

agent = Agent(TestModel(), name="scorer", output_type=Score, tools=[Tool(double)])
assert double(3) == 6
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/pydantic-ai/verify.py 2` → exit 0.

### 3. Execute without a provider call

```python
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

result = Agent(TestModel(), name="offline_runner").run_sync("hello")
assert result.output == "success (no tool calls)"
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/pydantic-ai/verify.py 3` → exit 0.

## Pitfalls

- Set `name=` on every agent registered with Temporal; durable operation names must remain stable.
- Use `TestModel` or `FunctionModel` for tests. Provider-backed models violate the no-network test contract.
- `pydantic-ai-harness` capabilities are not part of `pydantic-ai-slim`; install the exact extra before using CodeMode.
- Keep `output_type` strict and serializable across the Temporal activity boundary.

## Planted failure

A Temporal-bound agent without a stable name must go RED:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "from pydantic_ai import Agent; from pydantic_ai.models.test import TestModel; assert Agent(TestModel()).name, 'stable agent name required'"
```

Expected: non-zero exit with `stable agent name required`.
