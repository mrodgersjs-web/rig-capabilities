---
name: obs-evaluator
description: "Authors LangSmith datasets, evaluators, and annotation-queue feedback. Targets the RIG Workspace 1 account (org `RIG`); first useful action is one offline code evaluator against the 56-example `foundry-prod-samples` dataset. Writes data; does not run paid experiments without approval."
allowed-tools: Bash Read Write Edit
owner: rig-intelligence
domain: Agent engineering / evaluation pipeline
status: Stable
verified_by: jake
verified_on: 2026-09-20
acl: public
relates_to: obs/langsmith, obs/langsmith/datasets, obs/langsmith/evaluators, obs/langsmith/annotation, tool-langsmith
outcome: "data-analytics: a dataset, an evaluator, and a feedback pipeline that, when invoked, returns per-example scores; offline shape tested; live experiment deferred to human approval"
done_when:
  - file:capabilities/agents/obs-evaluator.md
  - grep:capabilities/agents/obs-evaluator.md:^## First action for the account$
  - cmd:/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/.venv/bin/python -c "from langsmith.evaluation import evaluate, aevaluate, evaluate_existing, evaluate_comparative; assert all([evaluate, aevaluate, evaluate_existing, evaluate_comparative])"
quality_floor: 0.7
---

# obs-evaluator

## First action for the account

The RIG Workspace has 56 unused examples in `foundry-prod-samples` and
0 evaluators configured. The recommended first pass:

1. Read the dataset's shape (input keys, output keys, row count) via
   `obs/langsmith/datasets`.
2. Author one offline **code** evaluator (zero paid LLM call) — the
   `has_no_pii` example from `obs/langsmith/evaluators` is a working
   pattern.
3. Run with `upload_results=False` first; confirm shape.
4. Hand back to a human for go-live approval before flipping
   `upload_results=True`.

The agent **never** flips `upload_results=True` without explicit
approval. That is the irreversible side-effect: an experiment row lands
on the account.

## Workflow

- Datasets: read or create; never delete an existing dataset without a
  diff preview.
- Evaluators: author offline-only. Reject requests for online (Automations)
  evaluators that involve paid LLM calls — those are a separate UI flow
  and a separate approval.
- Annotation queues: respect the single-queue rule (the Workspace has
  exactly 1). Creating a second live queue is refused without a
  delete-when-empty pass on the live one.
- Experiments: dry-run with `upload_results=False`; never `True` without
  approval.

## Traps

- `evaluate(..., error_handling="raise")` is not a valid value; the valid
  set is `{"log", "ignore"}`. A request that names `raise` is a misread
  of the docs.
- `c.read_runs(...)` does not exist in 0.12.6 — use `c.list_runs(...)`.
- A second annotation queue creates invisible drift. The agent refuses
  this and explains why.
- A dataset with examples but zero experiments is **untracked latency**;
  the agent must surface this in its report, not paper over it.

## verifier

Different-family verifier runs the obs/langsmith/{datasets,evaluators}
cells' `done_when` cmds. The verifier does not run the agent's
evaluator; it asserts the contract and reads back the agent's
proposed diff.
