# RIG Deviator System — 28 BMS Archetypes

7 levels × 4 BMS modes = **28 archetypes**.

The orchestrator (`system.run_system()`) routes confidence → BMS mode → archetype per level.

## BMS Modes (per `enterprise.iqrsqpi.BMSMode`)

| Mode | Confidence | Cost cap | Description |
|---|---|---|---|
| **A1** Python-only | ≥ 0.75 | $0.00 | Pure deterministic code. No LLM calls. Fastest path. |
| **A2** Hybrid | 0.45 – 0.74 | $0.10 | Code + light LLM grading on ambiguous metrics. |
| **A3** Bounded | 0.25 – 0.44 | $0.50 | LLM with cost cap. Single-shot per level. |
| **A4** Agent-free | < 0.25 | $0.00 | Human gate mandatory. System suggests but does not execute. |

## The 7 Levels

| Level | Purpose | Output |
|---|---|---|
| **L1 CAPTURE** | Pull artifact from any source | text + content_hash + source_meta |
| **L2 PROCESS** | 40-engine audit + DES² inner-loop | audit + des2 + rig_l + status |
| **L3 CREATE** | Generate +20σ variants per weak engine | variants[] + weakest_engines[] |
| **L4 DISTRIBUTE** | Render reports + JSON receipts | receipt + html_path + md_path |
| **L5 ENGAGE** | Surface blockers + next-step copy | blockers[] + fix_suggestions[] |
| **L6 CONVERT** | Apply patches → strict-passing artifact | final_text + final_audit |
| **L7 AUTONOMIZE** | Daemon tick + Brier outcome logging | daemon_status + prediction |

## The 28 Archetypes — full table

| | A1 Python | A2 Hybrid | A3 Bounded | A4 Agent-Free |
|---|---|---|---|---|
| **L1 CAPTURE** | File/stdin read | + urllib URL fetch | + scraper escalation hook | Human capture instruction |
| **L2 PROCESS** | 40-engine audit + DES² | + LLM specificity grade | + full LLM-judge (cost cap) | Audit + human review flag |
| **L3 CREATE** | Deterministic patch overlay | + 1 targeted LLM rewrite | + N +20σ agents + mesh | Human rewrite instructions |
| **L4 DISTRIBUTE** | Receipt + HTML render | + auto exec summary | + LLM exec summary (cost cap) | Raw audit for human curation |
| **L5 ENGAGE** | Blockers + fix suggestions | + coherence score | + adversarial reviewer | Human acknowledgement gate |
| **L6 CONVERT** | Patch overlay + re-audit | + DES² re-amplify | + LLM polish pass | Human accept gate |
| **L7 AUTONOMIZE** | Daemon tick + Brier log | + LangSmith/LangFuse | + CrewAI outcome crew | Runbook with manual steps |

## How to invoke

### From Python

```python
from system import run_system
from enterprise.iqrsqpi import BMSMode

# Confidence-routed (recommended)
result = run_system(
    source="my_proposal.md",
    confidence=0.85,         # → BMS A1
    tier="client",
    author_persona="claude",
)

# Force a specific mode
result = run_system(source="my.md", mode_override=BMSMode.A3)

# Force human-gate path
result = run_system(source="my.md", force_a4=True)
```

### Per-level

```python
from system import run_level, L3_CREATE
from enterprise.iqrsqpi import BMSMode

state = {"L1_CAPTURE": {"text": "..."}, "L2_PROCESS": {"audit": {...}}}
level_result = run_level(L3_CREATE, state, BMSMode.A2)
```

### Integrations status

```python
from enterprise.integrations import integrations_status
print(integrations_status())
# {
#   "langsmith":     {"available": False},  # set LANGSMITH_API_KEY to enable
#   "langfuse":      {"available": False},  # set LANGFUSE_PUBLIC_KEY+SECRET
#   "crewai":        {"available": False, "crews": ["outcome_observer", ...]},
#   "litellm":       {"available": True},   # installed
#   "opentelemetry": {"available": False},  # pip install opentelemetry-{api,sdk}
# }
```

## State contract between levels

Each level reads `state[<PREV_LEVEL>.value]` and writes its output back.

```
state = {
    "mission_id": "sys-...",
    "source": "...",
    "tier": "client",
    "author_persona": "claude",
    "confidence": 0.85,
    "bms_mode": "A1",
    "L1_CAPTURE":   {"text": "...", "content_hash": "...", ...},
    "L2_PROCESS":   {"audit": {...}, "des2": {...}, "rig_l": ..., ...},
    "L3_CREATE":    {"variants": [...], "weakest_engines": [...]},
    "L4_DISTRIBUTE":{"receipt": {...}, "receipt_id": "..."},
    "L5_ENGAGE":    {"blockers": [...], "fix_suggestions": [...]},
    "L6_CONVERT":   {"final_text": "...", "final_audit": {...}},
    "L7_AUTONOMIZE":{"daemon_status": {...}, "prediction_logged": {...}},
}
```

## Cost model per system run

| BMS mode | Worst-case cost | Typical latency (HED-sized artifact) |
|---|---|---|
| A1 | $0.00 | ~4 s |
| A2 | $0.10 | ~10 s |
| A3 | $0.50 | ~30 s |
| A4 | $0.00 (human time) | hours-days |

## Short-circuit behavior

If any level fails, the orchestrator halts and `SystemRun.short_circuited_at` names the failing level. The L1 → L7 chain is **non-recoverable** in a single run — you re-invoke `run_system()` after fixing the underlying issue.

L3 / L5 / L6 can usefully degrade if upstream succeeded; they emit warnings rather than fail.
