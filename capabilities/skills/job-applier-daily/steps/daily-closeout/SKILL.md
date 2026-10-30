---
name: job-daily-daily-closeout
description: Close a bounded daily run with reconciled counts, saved holds and next actions.
metadata:
  version: 1.3.0
---

# Daily closeout

## Inputs
Current run/task ledger, all real receipts, budget usage, pending operations and tracker state.

## Actions
Stop dispatch at ninety minutes or 350 calls. Reconcile accepted tasks and writes within remaining budget. Count unique submitted receipts by actual timestamp in configured timezone. Distinguish discovered, prepared, awaiting facts/pages/approval, submitted, unknown and tracker-unsynced.

## Outputs
Idle/blocked/handoff report, receipt references, pending checkpoint owners, next safe actions and budget totals.

## Gates
No running status after workers stop, fabricated target completion, quota carryover, or unknown counted submitted.

## Recovery
Preserve human waits and unknown effects across day rollover. Next run attaches same lineages.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Scheduling](../../subskills/scheduling/SKILL.md) and [receipt reconciliation](../../subskills/receipt-reconciliation/SKILL.md).
