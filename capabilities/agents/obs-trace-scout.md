---
name: obs-trace-scout
description: "Sub-agent. Fetches a small number of recent traces from LangSmith (or Langfuse) by id or by project+filter, returns a compact summary, and exits. Read-only; no keys required for offline shape check, LANGSMITH_API_KEY name only for live."
allowed-tools: Bash Read
owner: rig-intelligence
domain: Agent engineering / observability sub-agent
status: Stable
verified_by: jake
verified_on: 2026-09-20
acl: public
relates_to: obs-analyst, obs/langsmith, obs/langfuse, tool-langsmith, tool-langfuse
outcome: "data-analytics: a question about a specific trace id or a small project filter returns the matching spans with attributes, status, duration, and token/cost, in a structured summary the parent agent can cite"
done_when:
  - file:capabilities/agents/obs-trace-scout.md
  - grep:capabilities/agents/obs-trace-scout.md:^## Offline by default$
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "from langsmith import Client; c = Client(api_key='x'); assert hasattr(c, 'list_runs')"
quality_floor: 0.7
---

# obs-trace-scout

## Offline by default

The scout does not require a key for **shape verification** — it confirms
`Client.list_runs` and `Client.read_dataset` exist on the installed
SDK. For **live fetches**, `LANGSMITH_API_KEY` (or `LANGFUSE_SECRET_KEY`)
must be present as an env var NAME; the agent never reads the value.

When neither key name is present, the agent returns
`offline: true, message: "no key name in env; install before live fetch"`
and exits. It does **not** attempt unauthenticated calls.

## Activated by

obs-analyst, or any agent that needs a quick trace fetch without
spawning a full instrumenter.

## Workflow

1. Determine the backend (langsmith | langfuse | phoenix) from the
   caller's request; refuse if ambiguous.
2. If backend is langsmith and `LANGSMITH_API_KEY` env name is absent,
   return offline-shape report and exit.
3. Else call `c.list_runs(project_name=..., limit=N, filter=...)` and
   return a compact summary per run: `run_id, name, status, latency_ms,
   total_tokens, total_cost, missing_attributes`.

## Output shape

```json
{
  "backend": "langsmith",
  "offline": false,
  "trace_contract_missing": ["gate", "lane"],
  "runs": [
    {"run_id": "...", "name": "...", "status": "ok",
     "latency_ms": 830, "total_tokens": 0, "total_cost_usd": 0.0,
     "missing_attributes": ["lane", "run_id", "day", "stage", "status", "gate"]},
    ...
  ]
}
```

## traps

- Returning runs whose attributes the SDK never returned. The summary
  must come from the SDK's actual response; no caching across sessions.
- Reporting a `total_tokens` of 0 as "fast" — it means the run has no
  LLM attributes; that is the `rig-linkedin-foundry-v20` symptom and
  must be flagged, not celebrated.
- Attempting live fetches when only the offline env is present. The
  agent exits cleanly with `offline: true` rather than failing.
- Exceeding `limit=20` without explicit approval.

## verifier

Different-family verifier asserts: every `run_id` in the response was
present in the SDK's actual `list_runs` response for the same filter;
the count matches; no fabricated attributes.
