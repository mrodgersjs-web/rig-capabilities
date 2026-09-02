---
name: great-attempt-identity-ledger-and-equal-weight
lane: agent-engineering
source: canonical-curated
exemplar_of: attempt-identity-ledger-and-equal-weight
description: Reference exemplar — the attempt ledger GREEN on a balanced four-attempt file and GREEN on both a 2-step and a 50-step run of one task claiming identical per-attempt weight 1:1, RED (exit 2) on each planted failure (double reward, orphan step, unknown end_reason, non-binary reward, task-less terminal row, step-weighted 50:1 claim)
---

# attempt-identity-ledger-and-equal-weight — reference

Canonical asset `attempt-identity-ledger-and-equal-weight` (data). Path:
`capabilities/data/attempt-identity-ledger-and-equal-weight`.

> An attempt is one complete run on one task, terminated at exactly one of
> `submitted | verified | limit | failed`. One `rollout_id` is minted at that
> boundary and stamps every model call, tool event, and the single terminal
> reward row. Scoring aggregates weight **per attempt** — steps are a cost
> axis. `validate_ledger.py` enforces every clause; the planted fixtures are
> permanent regression cases.

## What good looks like

The two row types of the ledger, side by side — three steps and one terminal
reward, one attempt:

```json
{"row":"step","rollout_id":"rl-a1","seq":1,"event":"model_call"}
{"row":"step","rollout_id":"rl-a1","seq":2,"event":"tool_event"}
{"row":"step","rollout_id":"rl-a1","seq":3,"event":"model_call"}
{"row":"reward","rollout_id":"rl-a1","task_id":"task-invoice-fix","end_reason":"verified","reward":1}
```

`validate_ledger.py fixtures/ledger_valid.jsonl` (four attempts across two
tasks, all four end reasons, rewards `{0,1}`) → **exit 0**.

## The equal-weight proof

Two ledgers, one task, wildly different step counts — and the *same* verdict
and weight, because weight is attempts × 1.0:

```
$ python3 validate_ledger.py fixtures/ledger_short_run.jsonl --expect-weight task-demo=1:1
OK ledger_short_run.jsonl: 1 attempt(s), 2 step row(s), 0 orphan(s); weight is per-attempt
  task task-demo: weight=1.0 reward_sum=1 steps=2
$ python3 validate_ledger.py fixtures/ledger_long_run.jsonl --expect-weight task-demo=1:1
OK ledger_long_run.jsonl: 1 attempt(s), 50 step row(s), 0 orphan(s); weight is per-attempt
  task task-demo: weight=1.0 reward_sum=1 steps=50
```

Plant the 50-step run and the verdict does not move. Claim the 50-step run
deserves weight 50 (steps-as-weight) and the gate bites:

```
$ python3 validate_ledger.py fixtures/ledger_long_run.jsonl --expect-weight task-demo=50:1
VIOLATION ledger_long_run.jsonl: equal_weight_claim_failed: task 'task-demo' claims 50:1, per-attempt accounting says 1:1 (steps=50 are a cost axis, not weight)
```

## The ten done-test forms

| fixture | claim | exit | why |
|---------|-------|------|-----|
| `ledger_valid.jsonl` | — | 0 | 4 attempts, 1 reward each, all four end reasons |
| `ledger_short_run.jsonl` | `task-demo=1:1` | 0 | 2-step run, per-attempt weight 1 |
| `ledger_long_run.jsonl` | `task-demo=1:1` | 0 | 50-step run, **identical** weight — planting it moves nothing |
| `ledger_double_reward.jsonl` | — | 2 | one `rollout_id`, two reward rows: an attempt scored twice |
| `ledger_orphan_step.jsonl` | — | 2 | 3 step rows whose run was never terminated |
| `ledger_unknown_end_reason.jsonl` | — | 2 | `end_reason:"gave_up"` is outside the closed enum |
| `ledger_nonbinary_reward.jsonl` | — | 2 | `0.5` is a mood and `true` is a bool; neither is a reward |
| `ledger_reward_missing_task.jsonl` | — | 2 | a terminal row that names no task scores nothing |
| `ledger_long_run.jsonl` | `task-demo=50:1` | 2 | the step-weighted claim — exactly the bias this gate exists to refuse |

A missing ledger or an unparseable claim is **exit 1** (refusal to judge),
never conflated with a verdict. An empty ledger is exit 2: zero attempts
satisfies every clause vacuously and certifies nothing.

## Why events must not vote

The RIG delta: `~/.rig/prime-agent-traces/<agent>.jsonl` records runs and
steps with no termination enum and no one-reward-per-attempt invariant, and
`capabilities-realign.md`, `capabilities-round.md`, and the fleet quality
roster aggregate over EVENTS — so a chatty failing run currently out-votes a
clean two-step one in RIG's own honesty metrics. Here the attempt is the vote
and the step count is a cost axis the scorer never reads.

Risk: this is the paper's accounting discipline without its gradients; if RIG
ever trains, this same ledger is the training substrate — do not fork two
schemas.

Provenance: video `1Tlv7XNsPy8`; arXiv:2608.17528 (Agent Lightning v1.0);
OSS `microsoft/agent-lightning`.
