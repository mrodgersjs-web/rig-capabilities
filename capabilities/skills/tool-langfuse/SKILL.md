---
name: tool-langfuse
description: Instrument Design Harness runs with Langfuse traces, attributes, datasets, and scores while keeping offline tests network-free.
outcome: "data-analytics: every evaluated run can carry complete trajectory attributes and scores into the Langfuse ledger adapter"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('langfuse') == '4.15.4'; from langfuse import Langfuse; assert Langfuse(public_key='pk-offline', secret_key='sk-offline', base_url='http://127.0.0.1:1', tracing_enabled=False)"
great_example: "A benchmark run records lane, run_id, day, stage, status, and gate attributes under an @observe span, then flushes only in integration mode."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: registry:langfuse/skills
---

# tool-langfuse

## Role in our stack

Langfuse 4.15.4 is an **Evaluation** trajectory-ledger adapter. It captures model/tool spans, run attributes, dataset experiments, and scores. Offline verification disables tracing; live export requires explicit self-hosted credentials and is outside unit tests.

## Verified snippets

### 1. Construct a disabled client

```python
from langfuse import Langfuse
client = Langfuse(tracing_enabled=False)
assert isinstance(client, Langfuse)
client.shutdown()
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/langfuse/verify.py 1` → exit 0.

### 2. Decorate a function

```python
from langfuse import observe

@observe(name="offline_add")
def add(a: int, b: int) -> int:
    return a + b

assert add(2, 3) == 5
```

Verified with `LANGFUSE_TRACING_ENABLED=false`: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/langfuse/verify.py 2` → exit 0.

### 3. Propagate run attributes

```python
from langfuse import propagate_attributes

with propagate_attributes(user_id="rig-user", tags=["offline"]):
    value = {"score": 1.0}
assert value["score"] == 1.0
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/langfuse/verify.py 3` → exit 0.

## Pitfalls

- Set both public and secret keys plus the base URL for live export; never paste keys into code.
- `LANGFUSE_TRACING_ENABLED=false` prevents network export in tests.
- A span is incomplete unless it includes `lane`, `run_id`, `day`, `stage`, `status`, and `gate`.
- Call `flush()` or `shutdown()` only at process boundaries, not per stage.

## Planted failure

The attribute-completeness gate must go RED on a missing `gate`:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "required={'lane','run_id','day','stage','status','gate'}; attrs={'lane':'x','run_id':'r','day':'d','stage':'s','status':'ok'}; missing=required-attrs.keys(); assert not missing, f'missing span attributes: {sorted(missing)}'"
```

Expected: non-zero exit naming `gate`.
