---
name: job-daily-receipt-reconciliation
description: Reconcile original operations and count only unique real application receipts.
metadata:
  version: 1.3.0
---

# Receipt reconciliation

## Inputs
Stable job key, reserved attempt, application manifest, current approval and original ATS operation state.

## Actions
Inspect original ATS receipt/application history and match employer, requisition, candidate, destination and artifact/attempt context. Deduplicate receipt IDs globally. Preserve uncertain outcomes. Synchronize verified results to Airtable with readback.

## Outputs
Verified submitted, verified not-submitted, or unknown state with evidence and next action.

## Gates
A click, screenshot of a form, local fixture, HTTP redirect or worker narrative alone is not a receipt. Unknown never counts submitted or triggers another click.

## Recovery
If receipt exists and tracking failed, repair only tracking. A new attempt requires reconciled no-submission evidence and still-valid approval.

## Required skills and contracts
[ATS reconciliation](../../steps/ats-reconciliation/SKILL.md) and [Airtable ledger](../../steps/airtable-ledger/SKILL.md).
