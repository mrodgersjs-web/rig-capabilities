---
name: capabilities-round
description: Run a 1000x improvement round in one capability lane — five stages (rollouts, failure analysis, hypothesis, modification, score), a persistent optimization record that refuses to re-propose a rejected diff, deterministic contract upgrades applied only when done-tests stay green.
argument-hint: "[<lane> [n]] [dry]"
allowed-tools: Read, Bash, Task
category: meta
outcome: "meta: every round raises the lane's weakest contract without breaking a green, and remembers which edits the evidence already refuted"
done_when:
  - file:capabilities/commands/capabilities-round.md
  - file:examples/great/meta/capabilities-round.md
  - grep:capabilities/commands/capabilities-round.md:Never fabricate a round score
  - grep:capabilities/commands/capabilities-round.md:persistent optimization record
  - file:tests/test_round_record.py
  - cmd:python3 -m rig_capabilities.rounds --plant rejected; rc=$?; test $rc -eq 1
  - cmd:python3 -m rig_capabilities.rounds --plant novel; rc=$?; test $rc -eq 0
great_example: examples/great/meta/capabilities-round.md
acl: public
quality_floor: 0.7
---

# capabilities-round

`rig_capabilities.rounds.run_round(repo, lane, n, dry, budget, strategy)`. A round is one pass of
the loop the record makes cumulative: it reads what already failed, proposes one bounded edit per
candidate, and writes a verdict the next round has to obey.

1. Parse args: lane (default = the lane with the lowest mean trust), n (default 3), and `dry` if
   the word appears. All three surfaces carry the report's `exit_code` out, and agree:
   `./bin/rig-capabilities round <lane> --n 3 [--dry] [--budget N]` returns it as the process
   status, `python3 -m rig_capabilities.rounds <lane> …` prints the report and exits on it, and the
   `capabilities_round` MCP tool raises `ToolError` (so `isError: true`) with the whole report in
   the text rather than returning a refused round as a successful call. A cron or an agent that
   only checks `$?` must not be able to record a `BLOCKED-REPLAY` as a green round.
2. Five stages, one artifact each, all under `.context/rounds/`. Stages 1-4 land in
   `.context/rounds/<ts>-<lane>/`: `rollouts.json` (the recorded done-test runs this round may
   reason from), `failure_analysis.json` (`failing` with per-check fail counts and the assets they
   failed on, plus `held_out_green` — the checks that have always been green and must not break),
   `hypothesis.json` (one stated hypothesis per proposal, citing the failure it claims to address
   and carrying a `diff_hash`), `modification.json` (applied or refused). Stage 5 is the score:
   `score_select.json` beside them, with the full report at `.context/rounds/<ts>-<lane>.json`.
3. The round loads the **persistent optimization record** (`.context/rounds/record.jsonl`:
   previous hypotheses, diff-hashes, scores, verdicts) *before* it proposes — "a persistent
   optimization history, the previous hypothesis, the previous changes" (Discover AI `LEsKxMfRFjA`,
   arXiv 2608.13560 AutoDesign). Report `record: {loaded, appended, rejected_known, blocked}`.
4. A modification whose `diff_hash` is already recorded `REJECTED` is refused, not re-applied:
   `action="rejected-repeat"`, `plan: null`, zero evaluations spent, a `BLOCKED-REPLAY` line in the
   record, and `exit_code: 1`. That is the whole point — before V54 the round had no history, so
   every cycle re-patched the same asset forever. Quoting a round that says `replay_rejected: 1`
   as a clean round is a fabrication.
5. Stage order is the paper's: "We have rollouts, then we have a failure analysis, then the AI
   comes up with some hypothesis" (`LEsKxMfRFjA`). Stages 1-3 run before any file is touched, so
   the artifact chain answers *why* an edit was proposed, not only that it passed.
6. Attempt budget, routing and the stopping rule are declared knobs, not constants:
   `.context/rounds/knobs.json` overrides `KNOBS` keys `eval_budget_default`, `strategy_default`,
   `stopping_rule` (`budget-exhausted` | `first-reject`) and `recurring_failure_min` without a code
   edit; `attempt budget routing, stopping, candidate selection, fallback routes` is editable
   config there too (`LEsKxMfRFjA`). An unknown key or a bad rule is named in
   `knobs.unknown` — never silently applied, never silently dropped — and a version mismatch sets
   `knobs.version_mismatch`. `first-reject` stops the round at the first refutation; the rest read
   `stopped-by-rule` and no evaluation is spent on them.
7. Budget is enforced, not advisory: candidates past it land in `deferred` with their value
   ("70% of the 100 validation task here provide almost no, very, very little information" —
   Discover AI `MvI17TNFW9c`, arXiv 2608.20169 on why most of the pool cannot discriminate).
   `strategy="informative"` (default) ranks by need x Bernoulli variance; `"weakest"` reproduces
   the old order. Report `eval_budget_effective` and `eval_spent`.
8. Graduation needs green done-tests AND no held-out regression. A refuted edit is rolled back —
   `rolled_back: true`, the file byte-identical to what it was — so step "if any candidate fails
   its done-tests, it stays untouched" is a mechanism, not an intention, and the same diff stays
   proposable (a patched file would silently make the proposal empty and the replay guard
   untestable). Every accepted upgrade must show old done_when, new done_when, and the green run.
9. After apply, call `capabilities_quality_report` and quote the movement on the assets touched,
   plus the record's verdict counts. Quote `stopped_reason` when it is set.

Never fabricate a round score. If n assets were skipped for missing evidence, say so — and say so
when `failure_analysis.failing` is empty: no recorded failure in a lane is not the claim that the
lane is healthy.

Two limits that are not fixed here. The hypothesis is derived from recorded evidence by
`_statement()` and the modification is the deterministic contract edit — no model is called, so
hypothesis *quality* is still the bottleneck; these artifacts make a model-authored round
checkable later, they do not make a guess good. And `applied-unevaluated` stays unreachable while
`select()` caps candidate count at the evaluation budget: the state is named in code so an unrun
edit can never be counted as graduated, not because a round has produced it.

The two `cmd:` checks are a plant-failure pair, not decoration. `--plant rejected` builds a
throwaway estate (never this tree) where the only upgradeable asset carries a held-out green check
that any inserted byte breaks, runs the round twice over the same evidence, and must exit **1** —
the second round re-proposed a `REJECTED` diff and the guard refused it. `--plant novel` runs the
same engine over an asset with a green check and no prior rejection and must exit **0** — the proof
that the guard is a memory, not a wall. A guard that always blocked passed the first and failed the
second.
