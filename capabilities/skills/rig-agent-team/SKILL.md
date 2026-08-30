---
name: rig-agent-team
description: "Use when Hermes, Jake, PyCode/Pi, Claude Code, Codex, or a coding agent needs the RIG agent-team pattern: five-layer runtime (lattice routing, doctrine/context, contracts, deterministic guardrails, ProofPackets). Live dispatch surfaces: Orca worktrees/terminals, Hermes cron fleet, and mounted Temporal/Kestra/Prefect MCP tools."
---

# RIG Agent Team Runtime

Use this skill when a task should go through the RIG five-layer runtime instead of a single chat response.

## Runtime

Local API:

```text
http://127.0.0.1:4141
```

OpenAI-compatible endpoint:

```text
http://127.0.0.1:4141/v1/chat/completions
```

Model id:

```text
rig-agent-team
```

Primary app:

```text
/Users/rig128gb/Startup-Intelligence-OS/apps/rig_agent_team
```

## What It Does

1. Routes the goal into the RIG lattice.
2. Pulls local doctrine/context and fleet health.
3. Fans work out across Orca worktrees/terminals and the Hermes cron fleet.
4. Assigns multi-role work to the RIG department agents (~/.rig/departments).
5. Applies Pydantic contracts and deterministic Guardrails/ARC approvals.
6. Writes ProofPackets and dispatches through Orca terminals, Hermes crons, or Temporal/Kestra/Prefect when approved.

## Commands

> **STALE (verified 2026-08-30):** the `127.0.0.1:4141` API is not running
> (`curl -m 2` refused) and `/Users/rig128gb/Startup-Intelligence-OS/apps/rig_agent_team`
> does not exist (that path is an Obsidian vault, no `apps/`). The commands
> below only work if the app is restored from its source repo. Do not treat a
> connection error as a mission failure — the runtime simply is not installed.


Health:

```bash
curl -s http://127.0.0.1:4141/health
```

Mission:

```bash
curl -s http://127.0.0.1:4141/v1/missions \
  -H 'Content-Type: application/json' \
  -d '{"goal":"Verify the RIG agent team","execute":false}'
```

Local smoke:

```bash
cd /Users/rig128gb/Startup-Intelligence-OS/apps/rig_agent_team
uv run rig_agent_smoke
uv run rig_swarm_smoke
uv run rig_agent_demo
uv run rig_agent_monitor
```

Start API:

```bash
cd /Users/rig128gb/Startup-Intelligence-OS/apps/rig_agent_team
./scripts/run_api.sh
```

LangGraph Studio:

```bash
cd /Users/rig128gb/Startup-Intelligence-OS/apps/rig_agent_team
./scripts/run_langgraph_studio.sh
```

Graph id: `rig_swarm_os`

Dashboard:

```text
http://127.0.0.1:4141/dashboard
```

Status:

```text
http://127.0.0.1:4141/v1/status
```

Install daily desktop widget/monitor:

```bash
cd /Users/rig128gb/Startup-Intelligence-OS/apps/rig_agent_team
./scripts/install_desktop_widget.sh
```

Pinned intake sources:

```text
/Users/rig128gb/.rig/intake/repos/2026-05-22
```

## Hard Rules

- Do not spawn workers, use paid models, publish, deploy, delete, or migrate unless the request includes the correct approval packet.
- Dispatch surfaces (Orca terminals, Hermes crons, Temporal/Kestra/Prefect) are capability adapters, not proof by themselves.
- If context retrieval times out, continue with doctrine and fleet health and mark the layer degraded.
- Every meaningful mission writes a ProofPacket (jake_pai `proofpacket_seal`, or `~/.rig/proof/`).
