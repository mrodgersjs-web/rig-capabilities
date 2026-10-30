---
name: job-daily-ats-reconciliation
description: Execute only an approved exact application and reconcile uncertain results.
metadata:
  version: 1.3.0
---

# Ats reconciliation

## Inputs
Current factual/page/quality reviews, exact application manifest, authenticated specific approval, synchronized tracker reservation, verified browser adapter.

## Actions
Recheck target and payload. Reserve one action owner. Upload exact approved files and submit only under valid scope. Capture real receipt and reconcile destination/application history. Persist unknown outcomes without retry.

## Outputs
Receipt-bound submitted state, proven no-submission outcome, or submission_unknown with next action.

## Gates
Any payload change, tracker hold, expired target, unknown answer, browser ownership error or missing approval blocks action.

## Recovery
Never repeat submit after timeout. Reconcile existing attempt using receipt/history; preserve pending tracker writes.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Receipt reconciliation](../../subskills/receipt-reconciliation/SKILL.md) and [application approval](../application-approval/SKILL.md).
