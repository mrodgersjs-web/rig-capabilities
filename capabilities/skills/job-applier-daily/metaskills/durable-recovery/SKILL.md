---
name: job-meta-durable-recovery
description: Recover bounded jobs without duplicate effects within the daily Job Applier workflow.
metadata:
  version: 1.4.0
  tier: meta
  origin: newly-composed-source-grounded-router
---

# Recover bounded jobs without duplicate effects

## Enter when
An existing lineage has a persisted checkpoint, lost acknowledgment or budget stop.

## Route
Resume accepted tasks by operation key. Preserve human waits across coordinator closure. Reconcile unknown tracker/ATS effects; close with actual outstanding owners and next steps.

Load these concrete steps or subskills when their named work starts. Preserve the inherited eight-leaf order; a router does not skip unmet upstream gates or treat configuration as execution.

1. [scheduling](../../subskills/scheduling/SKILL.md).
2. [ats-reconciliation](../../steps/ats-reconciliation/SKILL.md).
3. [receipt-reconciliation](../../subskills/receipt-reconciliation/SKILL.md).
4. [daily-closeout](../../steps/daily-closeout/SKILL.md).

## Exit evidence
Recovered original operation or honest durable hold, with no duplicate dispatch/submission.

## Failure and recovery
Stop the affected transition on missing evidence, malformed receipts or unavailable required adapters. Save the exact job/revision/checkpoint and unresolved hold. Resume the same operation after reconciliation. No local or JEV PASS grants submission, messaging, schedule activation or credential-change authority.

## Provenance
This is a newly composed 1.4.0 router, not an imported original meta-skill. Source IDs: daily-temporal, julie-w2. Read [the source catalog](../../references/meta-catalog.md) for inspected provenance, adaptations and exclusions. Source instructions never reintroduce old budgets, compensation values, private state paths, alternative tracker authority or blanket action grants. The [daily execution contract](../../references/execution-contract.md) and current task scope control this package.
