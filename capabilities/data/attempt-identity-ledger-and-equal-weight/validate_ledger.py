#!/usr/bin/env python3
"""Enforce the attempt-identity ledger contract mechanically.

An ATTEMPT is one complete run of the agent on one task, terminated at exactly
one of submitted / verified / limit / failed. A unique rollout_id is minted at
that boundary and stamps every model call, every tool event, and the single
terminal reward row. One attempt, one reward — binary, 0 or 1.

The failure mode this closes is event-weighted accounting: a ledger that
aggregates over recorded STEPS lets a chatty 50-step run out-vote a clean
2-step run. Here every aggregate scores per ATTEMPT: the 2-step and the
50-step run carry identical weight, and step/token counts live on a separate
cost axis that scoring never touches.

Ledger format (JSONL): one JSON object per line, one of two row types —

  step row:    {"row": "step",   "rollout_id": ..., "seq": <int>=1,
                "event": "model_call" | "tool_event"}
  reward row:  {"row": "reward", "rollout_id": ..., "task_id": ...,
                "end_reason": submitted|verified|limit|failed,
                "reward": 0 | 1}

The invariants, each independently violable:

  I1  one reward row per attempt:   reward-row count == distinct rollout_id
      count, and no rollout_id appears in two reward rows (a double reward is
      an attempt scored twice);
  I2  no orphans:                   every step row's rollout_id has exactly
      one reward row — orphan step rows == 0;
  I3  closed termination enum:      every end_reason resolves to
      {submitted, verified, limit, failed};
  I4  binary reward:                reward is the INTEGER 0 or 1 — bool True
      and float 1.0 are not rewards;
  I5  equal weight:                 per-task aggregate is attempts x 1.0 with
      reward_sum = sum of rewards, whatever the step counts. A claim passed
      via --expect-weight TASK=ATTEMPTS:REWARD_SUM that does not match the
      per-attempt computation is a violation — a claim weighted by steps
      (50 steps claiming weight 50) is exactly what this clause refuses.

Exit codes (the honesty contract):
  0  every row well-formed, every invariant holds, every weight claim matches
  1  usage / file-not-found / unparseable claim (a refusal to judge, not a
     verdict — `ran` is never `clean`)
  2  a contract violation: a malformed row, a double reward, an orphan step,
     an end_reason outside the enum, a non-binary reward, a zero-attempt
     ledger, or a per-attempt weight claim that does not hold

Stdlib only. Reads only the paths it is given. Writes nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

END_REASONS = {"submitted", "verified", "limit", "failed"}
EVENTS = {"model_call", "tool_event"}
STEP_REQUIRED = ("row", "rollout_id", "seq", "event")
REWARD_REQUIRED = ("row", "rollout_id", "task_id", "end_reason", "reward")


class RefuseArgumentParser(argparse.ArgumentParser):
    """A usage error is a refusal (exit 1), never a verdict (exit 2)."""

    def error(self, message: str):  # pragma: no cover - exercised via rc 1
        self.print_usage(sys.stderr)
        print(f"usage_error: {message}", file=sys.stderr)
        raise SystemExit(1)


def _nonempty_str(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def _is_binary_int(v) -> bool:
    # bool is an int subclass in Python; `reward: true` is NOT a 1.
    return isinstance(v, int) and not isinstance(v, bool) and v in (0, 1)


def _load_jsonl(path: Path, origin: str, violations: list):
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            violations.append((f"{origin}:{lineno}", f"bad_json: {e}"))
            continue
        if not isinstance(obj, dict):
            violations.append((f"{origin}:{lineno}", "row_not_object"))
            continue
        rows.append((lineno, obj))
    return rows


def parse_weight_claims(raw_claims):
    """Parse TASK=ATTEMPTS:REWARD_SUM claims. Returns None on any syntax
    fault — a malformed claim is the caller's usage error, a refusal (exit
    1), never a verdict on the ledger (exit 2)."""
    claims = []
    for raw in raw_claims or []:
        task, sep, spec = str(raw).rpartition("=")
        if not sep or not _nonempty_str(task):
            print(f"usage_error: unparseable_weight_claim: {raw!r}", file=sys.stderr)
            return None
        parts = spec.split(":")
        if len(parts) != 2 or not all(p.lstrip("-").isdigit() for p in parts):
            print(f"usage_error: unparseable_weight_claim: {raw!r}", file=sys.stderr)
            return None
        attempts, reward_sum = (int(p) for p in parts)
        if attempts < 0 or reward_sum < 0:
            print(f"usage_error: negative_weight_claim: {raw!r}", file=sys.stderr)
            return None
        claims.append((task, attempts, reward_sum))
    return claims


def check_rows(rows, origin, violations):
    """Validate row shape. Returns (reward_rows, step_rollouts).

    reward_rows: list of (lineno, well-formed reward row dict)
    step_rollouts: {rollout_id: step count} for structurally valid step rows
    """
    seen_steps: dict = {}          # rollout_id -> set of seq
    reward_rows = []
    for lineno, row in rows:
        where = f"{origin}:{lineno}"
        kind = row.get("row")
        if kind == "step":
            missing = [f for f in STEP_REQUIRED if f not in row]
            if missing:
                violations.append((where, f"step_missing_fields: {','.join(missing)}"))
                continue
            rid = row["rollout_id"]
            if not _nonempty_str(rid):
                violations.append((where, "step_rollout_id_empty"))
                continue
            seq = row["seq"]
            if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
                violations.append((where, f"{rid}: step_seq_must_be_positive_int"))
            elif seq in seen_steps.setdefault(rid, set()):
                violations.append((where, f"{rid}: duplicate_step_seq: {seq}"))
            else:
                seen_steps[rid].add(seq)
            if row["event"] not in EVENTS:
                violations.append((where, f"{rid}: unknown_event {row['event']!r}"))
        elif kind == "reward":
            missing = [f for f in REWARD_REQUIRED if f not in row]
            if missing:
                violations.append((where, f"reward_missing_fields: {','.join(missing)}"))
                continue
            rid = row["rollout_id"]
            if not _nonempty_str(rid):
                violations.append((where, "reward_rollout_id_empty"))
                continue
            if not _nonempty_str(row["task_id"]):
                violations.append((where, f"{rid}: task_id_empty"))
                continue
            # I3/I4 are per-row and reported here so a bad end_reason and a
            # double reward can both name themselves; the row is then kept
            # for the counting invariants (it is still an attempt boundary).
            if row["end_reason"] not in END_REASONS:
                violations.append((where, f"{rid}: unknown_end_reason "
                                          f"{row['end_reason']!r} not in "
                                          f"{sorted(END_REASONS)}"))
            if not _is_binary_int(row["reward"]):
                violations.append((where, f"{rid}: reward {row['reward']!r} "
                                          f"is not the integer 0 or 1"))
            reward_rows.append((lineno, row))
        else:
            violations.append((where, f"unknown_row_type: {kind!r}"))
    steps_per_rollout = {rid: len(seqs) for rid, seqs in seen_steps.items()}
    return reward_rows, steps_per_rollout


def check_attempt_identity(reward_rows, steps_per_rollout, origin, violations):
    """I1 + I2: one reward per rollout_id; zero orphan step rows."""
    rewards_by_rollout: dict = {}
    for lineno, row in reward_rows:
        rewards_by_rollout.setdefault(row["rollout_id"], []).append(lineno)
    for rid, linenos in sorted(rewards_by_rollout.items()):
        if len(linenos) > 1:
            where = f"{origin}:{linenos[-1]}"
            violations.append((where, f"double_reward: rollout_id {rid!r} carries "
                                      f"{len(linenos)} reward rows at lines "
                                      f"{linenos}; an attempt is scored once"))
    orphans = sorted(rid for rid in steps_per_rollout if rid not in rewards_by_rollout)
    for rid in orphans:
        violations.append((origin, f"orphan_step_rows: rollout_id {rid!r} has "
                                   f"{steps_per_rollout[rid]} step row(s) and no "
                                   f"reward row — a run whose end was never recorded"))
    n_rewards = len(reward_rows)
    n_rollouts = len(set(rewards_by_rollout) | set(steps_per_rollout))
    if n_rewards != n_rollouts:
        violations.append((origin, f"count_identity: reward rows ({n_rewards}) != "
                                   f"distinct rollout_ids ({n_rollouts})"))


def check_equal_weight(reward_rows, steps_per_rollout, claims, origin, violations):
    """I5: per-task aggregate weight is attempts x 1.0, never steps x 1.0."""
    per_task: dict = {}
    for _, row in reward_rows:
        t = per_task.setdefault(row["task_id"], {"attempts": 0, "reward_sum": 0,
                                                 "steps": 0})
        t["attempts"] += 1
        reward = row["reward"]
        if _is_binary_int(reward):
            t["reward_sum"] += reward
        t["steps"] += steps_per_rollout.get(row["rollout_id"], 0)
    for task, want_attempts, want_reward_sum in claims:
        got = per_task.get(task)
        if got is None:
            violations.append((origin, f"weight_claim_task_absent: {task!r} "
                                       f"names no task in the ledger"))
            continue
        if got["attempts"] != want_attempts or got["reward_sum"] != want_reward_sum:
            violations.append((origin, f"equal_weight_claim_failed: task {task!r} "
                                       f"claims {want_attempts}:{want_reward_sum}, "
                                       f"per-attempt accounting says "
                                       f"{got['attempts']}:{got['reward_sum']} "
                                       f"(steps={got['steps']} are a cost axis, "
                                       f"not weight)"))
    return per_task


def main(argv=None) -> int:
    ap = RefuseArgumentParser(description="validate an attempt-identity ledger")
    ap.add_argument("ledger", help="ledger JSONL (step rows + one reward row per attempt)")
    ap.add_argument("--expect-weight", action="append", metavar="TASK=N:M",
                    help="per-attempt aggregate claim: TASK=ATTEMPTS:REWARD_SUM "
                         "(repeatable); a step-weighted claim must not pass")
    ap.add_argument("--show-weight", action="store_true",
                    help="print the per-attempt aggregate for every task")
    args = ap.parse_args(argv)

    lp = Path(args.ledger)
    if not lp.is_file():
        print(f"ledger file not found: {lp}", file=sys.stderr)
        return 1

    violations: list = []
    claims = parse_weight_claims(args.expect_weight)
    if claims is None:
        return 1        # the claim is broken, not the ledger: refuse to judge
    rows = _load_jsonl(lp, lp.name, violations)
    reward_rows, steps_per_rollout = check_rows(rows, lp.name, violations)

    if not violations and not reward_rows:
        # A ledger with zero attempts satisfies every invariant vacuously.
        # Vacuous green is decoration: this file records no attempt at all.
        violations.append((lp.name, "ledger_has_no_attempts: zero reward rows — "
                                    "nothing was terminated, nothing was scored"))

    if not violations:
        check_attempt_identity(reward_rows, steps_per_rollout, lp.name, violations)
        per_task = check_equal_weight(reward_rows, steps_per_rollout, claims,
                                      lp.name, violations)

    if violations:
        for where, msg in violations:
            print(f"VIOLATION {where}: {msg}")
        print(f"\nledger: {len(violations)} violation(s)")
        return 2

    total_steps = sum(steps_per_rollout.values())
    print(f"OK {lp.name}: {len(reward_rows)} attempt(s), "
          f"{total_steps} step row(s), 0 orphan(s); weight is per-attempt")
    if args.show_weight or claims:
        for task in sorted(per_task):
            t = per_task[task]
            print(f"  task {task}: weight={float(t['attempts'])} "
                  f"reward_sum={t['reward_sum']} steps={t['steps']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
