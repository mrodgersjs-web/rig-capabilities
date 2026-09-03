---
name: north-star-lock-loop
description: "RIG doctrine — North-Star Lock + Anchor as a code-enforced loop. Lock a Goal Card (GOAL, buyer METRIC, executable DONE-TEST, OUT-OF-SCOPE, ACTIVE-PROJECT, EFFORT-BUDGET) before any build, log a drift check at every checkpoint, allow scope changes only with a named cost, and close the session against the card. Banned working-metrics are refused by the gate."
when_to_use: "At session start for any multi-hour build, and whenever Mike asks 'what was the intent again' or the work drifts. Say 'lock the goal', 'north star', 'anchor block', 'drift check', 'are we still on track'."
version: 11.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: one locked goal per session, drift caught at checkpoints, scope moved only by named decision, session closed against the card"
done_when:
  - "cmd:python3 bin/rig-loop test north-star-lock-loop"
  - "file:capabilities/skills/north-star-lock-loop/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  doctrine_source: "~/.claude/rules/north-star-doctrine.md; north-star-lock.md; anchor-doctrine.md"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill north-star-lock-loop"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# North-Star Lock loop

The drift guard as machinery. Until the Goal Card passes its gate, code writes are
denied. Every prompt injects the card's stage banner; every checkpoint gets a
drift line; `MATCH: no` must be reconciled before the session can close.

```
L Lock → D Drift-check (repeat) → S Scope-alarm → C Close → P Proof
                 ▲                                   │ goal not met → back to D (max 3) → escalate
                 └───────────────────────────────────┘
```

## Step 0

```bash
rig-loop activate north-star-lock-loop --intent "<Mike's words>"
rig-loop artifact L docs/plans/$(date +%F)-goal-card.md   # optional: keep the card in the repo
```

## Stages

| Stage | Artifact | Gate | Command |
|---|---|---|---|
| **L Lock** | `goal-card.md` | `## GOAL` (outcome, Mike's words) `## METRIC` (buyer/outcome terms — fidelity/looks-like/award-tier refused) `## DONE-TEST` (executable) `## OUT-OF-SCOPE` `## ACTIVE-PROJECT` `## EFFORT-BUDGET` | `rig-loop stage L pass` — build unlocks |
| **D Drift-check** | `drift-log.md` | `## Checks` with lines `- <ts> NOW: <what I'm optimizing> \| MATCH: yes\|no`; counter `drift_checks ≥ 1` | at every checkpoint: append a line, `rig-loop counter drift_checks --inc`; `rig-loop stage D pass` |
| **S Scope-alarm** | `scope.md` | `## Scope-changes` each with `named-cost: …` or `none`; no `MATCH: no` line without `RECONCILED:` | `rig-loop stage S pass` |
| **C Close** | `close-card.md` | `## Goal-met` yes/no, `## Parked`, `## Next-action` (one), `## Proliferation-delta` | `rig-loop stage C pass` (no → `stage C fail` loops to D) |
| **P Proof** | `proof.json` | sealed | `rig-loop seal && rig-loop stage P pass` |

## The seven laws, where they bite

- **L1 metric lock** — METRIC gate refuses banned working-metrics.
- **L2 reference-as-hypothesis / L4 one visual system** — a reference or aesthetic change is a scope change: `named-cost:` line or it does not pass S.
- **L3 gate every iteration** — pair with `proof-loop` per artifact.
- **L5 scope rank / budget** — `## EFFORT-BUDGET` is on the card; overrun is a `MATCH: no`.
- **L6 tooling is not progress** — two-strikes/15-min lands in the drift log as `MATCH: no`.
- **L7 check-ins** — `MATCH: no` must be `RECONCILED:` with Mike's re-lock or a return.

## Honesty notes

- The drift line is agent-written; the gate only enforces that it exists and is reconciled. The banner on every prompt is the reminder.
- `EFFORT-BUDGET` is not timed by the engine beyond the 12h wall-clock kill switch.
