---
name: job-daily-outcome-learning
description: Summarize observed application outcomes and stage evidence-bound improvement proposals.
metadata:
  version: 1.4.0
  origin: newly-composed-source-grounded-step
---

# Outcome learning

## Inputs
Reconciled application receipts, tracker readback, dated outcomes, failures and current run budget.

## Actions
Compute counts from unique real evidence and explicit time windows. Distinguish submitted, rejected, invited, scheduled, attended, advanced and unknown; an invitation is not attendance. Record each observed failure as trigger, proposed check, source evidence and affected owner. Use JEV for bounded semantic interpretation only after sanitization; do not infer a rejection cause without evidence. Stage proposed lessons for review without editing policies, live schedules or memory automatically.

## Outputs
Outcome summary, denominators/time windows, unknown counts and proposed lesson records with evidence and status candidate.

## Gates
No invented conversion improvements, causal attribution from tiny samples, unsupported interview outcomes, or automatic lesson promotion. Tracker discrepancy remains explicit rather than choosing the favorable count.

## Recovery
Preserve original outcomes and corrections as revisions. Missing replies stay unknown. After a corrected receipt reconcile counts before comparing runs; never modify candidate facts to improve metrics.

## Required skills and contracts
- [daily-closeout](../../steps/daily-closeout/SKILL.md).
- [receipt-reconciliation](../../subskills/receipt-reconciliation/SKILL.md).
- [jev-decision](../../steps/jev-decision/SKILL.md).

Follow the [daily execution contract](../../references/execution-contract.md). Source IDs traject-learn, julie-w2 identify the inspected antecedents in [the provenance catalog](../../references/meta-catalog.md). This is a newly composed portable adaptation; it does not import those sources' historical private paths, grants, compensation defaults or alternative ledgers. Real receipts and current approvals remain required.
