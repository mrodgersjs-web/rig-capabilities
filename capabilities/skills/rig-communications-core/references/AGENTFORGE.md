# AgentForge Workflows (V11)

This repository ships declarative AgentForge-compatible workflow specs in `agentforge/`.

## Workflow schema

Each `.workflow` file is JSON and defines:
- `name`, `version`, `description`
- `steps[]` with `name`, `action`, and optional `input`, `output`, `channel`, `max_attempts`, `values`

Supported reference actions in `rig_comm.agentforge.runner`:
- `set`
- `evaluate`
- `guard`
- `human_approval`

## Included workflows

- `agentforge/comm-pipeline.workflow`
  - Signal → Tournament → Ensemble Draft → Score → Swarm → Gate → Ship/Learn
- `agentforge/single-message-guard.workflow`
  - draft → gate → revise loop → ship

## Run locally

```bash
rig run-workflow agentforge/single-message-guard.workflow --draft "..." --approved
```

## Mapping to rig_comm

- `evaluate` step → `rig_comm.evaluate`
- `guard` step → `rig_comm.integrations.CommunicationGuard`
- `human_approval` step → explicit final ship gate
