---
name: tool-temporal
description: Build deterministic Temporal Python workflows, retryable activities, schedules, and time-skipping tests for Design Harness runtimes.
outcome: "infra-ops: clock-critical compiled lanes survive worker failure and replay without moving side effects into workflow code"
done_when:
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "import importlib.metadata as m; assert m.version('temporalio') == '1.33.0'; from temporalio.common import RetryPolicy; assert RetryPolicy()"
great_example: "A lane workflow contains only deterministic orchestration, calls all I/O through activities, and proves month-long timing with WorkflowEnvironment.start_time_skipping()."
quality_floor: 0.7
relates_to: rig-design-harness
provenance: "registry:temporalio/skill-temporal-developer + local:/Users/rig128gb/.claude/skills/temporal-python-testing"
---

# tool-temporal

## Role in our stack

Temporal Python SDK 1.33.0 owns the **Runtime** carrier: workflows, activities, workers, schedules, retries, signals, and replay. Workflow code is the deterministic brain; file, network, subprocess, model, and clock I/O belongs in activities.

## Verified snippets

### 1. Construct a retry policy

```python
from datetime import timedelta
from temporalio.common import RetryPolicy

policy = RetryPolicy(initial_interval=timedelta(seconds=2), maximum_attempts=3)
assert policy.maximum_attempts == 3
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/temporal/verify.py 1` → exit 0.

### 2. Define a workflow

```python
from temporalio import workflow

@workflow.defn
class EchoWorkflow:
    @workflow.run
    async def run(self, value: str) -> str:
        return value
```

Verified by direct offline execution: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/temporal/verify.py 2` → exit 0.

### 3. Define an activity

```python
from temporalio import activity

@activity.defn
async def normalize(value: str) -> str:
    return value.strip().lower()
```

Verified: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python /tmp/agentforge-snippets/temporal/verify.py 3` → exit 0.

## Pitfalls

- Workflow code must avoid system time, randomness, file access, network access, and subprocesses.
- Activity retryability and idempotency are separate; retries do not make an effect safe.
- Keep stable workflow/activity names across deployed histories or use Temporal versioning.
- Use time-skipping integration tests with stubbed activities; unit tests alone miss replay behavior.

## Planted failure

A source gate must reject wall-clock access in workflow code:

```bash
/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "source='def run(): return datetime.now()'; banned=('datetime.now(', 'time.time('); hits=[x for x in banned if x in source]; assert not hits, f'nondeterministic workflow calls: {hits}'"
```

Expected: non-zero exit naming `datetime.now(`.
