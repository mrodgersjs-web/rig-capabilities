---
name: attempt-identity-ledger-and-equal-weight
description: >-
  Use when a harness scores agents over recorded events. An attempt is one
  complete run on one task, terminated at exactly one of submitted/verified/
  limit/failed; one rollout_id stamps every step and the single terminal
  reward row (integer 0/1). validate_ledger.py enforces over the ledger:
  reward rows == distinct rollout_ids, orphan step rows == 0, end_reason in
  the closed enum, and weight per ATTEMPT — a 2-step and a 50-step run of one
  task carry identical weight (steps are a cost axis, not a vote). Exit 2 on
  any violation; exit 1 is a refusal to judge.
allowed-tools: Bash Read
owner: rig-intelligence
domain: Agent evaluation / run accounting
status: Draft
outcome: >-
  agent-engineering: every RIG aggregate weighs attempts, not events — a
  chatty 50-step run can no longer out-vote a clean 2-step run, because the
  ledger cannot record an attempt twice, orphan a step, or fake a reward
done_when:
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_valid.jsonl; test $? -eq 0
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_short_run.jsonl --expect-weight task-demo=1:1; test $? -eq 0
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_long_run.jsonl --expect-weight task-demo=1:1; test $? -eq 0
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_double_reward.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_orphan_step.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_unknown_end_reason.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_nonbinary_reward.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_reward_missing_task.jsonl; rc=$?; test $rc -eq 2
  - cmd:python3 capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py capabilities/data/attempt-identity-ledger-and-equal-weight/fixtures/ledger_long_run.jsonl --expect-weight task-demo=50:1; rc=$?; test $rc -eq 2
  - file:capabilities/data/attempt-identity-ledger-and-equal-weight/validate_ledger.py
great_example: examples/great/agent-engineering/attempt-identity-ledger-and-equal-weight.md
quality_floor: 0.6
---

# attempt-identity-ledger-and-equal-weight

THE LAW: **an attempt is the unit of account — one run, one termination, one
reward, one unit of weight.** A ledger that scores events lets the chattiest
run win; a ledger without attempt identity cannot even tell you how many runs
it scored.

The source names the accounting discipline (arXiv:2608.17528, *Agent Lightning
v1.0: Towards Harnessed Agentic RL*; OSS `microsoft/agent-lightning`; video
`1Tlv7XNsPy8`): every model call, tool event, and the single terminal reward
row carry one `rollout_id` minted at the attempt boundary, and scoring
aggregates weight per attempt.

The RIG delta this closes: `~/.rig/prime-agent-traces/<agent>.jsonl`
(`rlm_run_start`/`rlm_step_record`/`rlm_run_finish`) records runs and steps
with no termination-cause enum and no one-reward-per-attempt invariant, and
`capabilities/commands/capabilities-realign.md`, `capabilities-round.md`, and
the `rig_fleet` quality roster aggregate over recorded EVENTS — the per-step
weighting bias that lets a 50-step run out-vote a clean 2-step run in RIG's
own honesty metrics.

## The ledger: one JSONL file, two row types

| row | required fields | contract |
|-----|-----------------|----------|
| `step` | `row:"step"`, `rollout_id`, `seq` (positive int, unique per rollout), `event` ∈ `model_call` \| `tool_event` | stamps activity; **never carries weight** |
| `reward` | `row:"reward"`, `rollout_id`, `task_id`, `end_reason`, `reward` | the attempt boundary: exactly one per `rollout_id` |

The closed termination enum: `submitted | verified | limit | failed`. A run
that ends any other way did not terminate under this contract. The reward is
the **integer** 0 or 1 — `true` is a bool, `1.0` is a float; neither is a
reward (a scorer that accepts `true` silently invents rewards out of flags).

## The invariants

1. **One reward per attempt.** Reward-row count == distinct `rollout_id`
   count, and no `rollout_id` appears in two reward rows. A double reward is
   one attempt scored twice — exit 2.
2. **Zero orphan step rows.** Every step's `rollout_id` has a reward row. A
   step whose run was never terminated is an accounting hole — exit 2.
3. **Closed enum.** `end_reason: "gave_up"` is not a termination the ledger
   understands — exit 2.
4. **Binary reward.** `reward: 0.5` is a mood, not a signal — exit 2.
5. **Equal weight.** The per-task aggregate is `attempts × 1.0`, reward_sum
   the sum of binary rewards, **whatever the step counts**.
   `--expect-weight TASK=N:M` states the claim; per-attempt accounting must
   match. A 2-step run and a 50-step run of one task both claim `1:1` and
   both pass; the same 50-step run claiming `50:1` (steps-as-weight) exits 2.

An empty ledger satisfies every clause vacuously and is still exit 2: a file
with zero attempts records nothing and certifying it would be decoration.

## Done-tests (the planted failures are permanent regression cases)

Ten `done_when` forms: three GREEN (the balanced ledger; the 2-step and the
50-step runs of one task both claiming per-attempt weight `1:1` — planting
the 50-step run does not move the verdict) and six RED at exit 2 — double
reward on one `rollout_id`, orphan step rows, an end_reason outside the enum,
a non-binary reward (`0.5` and `true`), a terminal row with no `task_id`, and
the step-weighted claim `50:1` refused. Each RED fixture stays in `fixtures/`
so the gate cannot silently stop biting.

## Risk

This applies the source paper's accounting discipline **without its
gradients**: the ledger is an honesty gate today. If RIG ever trains, this
same ledger is the training substrate — do not fork two schemas.

## Provenance

Source video `1Tlv7XNsPy8`; paper arXiv:2608.17528 (*Agent Lightning v1.0:
Towards Harnessed Agentic RL*); implementation `microsoft/agent-lightning`.
No creator text is reproduced; the mechanism is re-derived as an enforceable
ledger contract.
