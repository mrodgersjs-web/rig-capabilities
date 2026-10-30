---
name: job-daily-application-approval
description: Obtain separate permission for the exact current application manifest.
metadata:
  version: 1.3.0
---

# Application approval

## Inputs
Passed factual/inclusion/page/quality gates, synchronized tracker, active target and complete final payload.

## Actions
Execute inherited application-approval. Show exact destination, resume, cover letter, attachments, answers and attestations. Record authenticated current submission approval tied to all hashes. Check approval scope before the ATS adapter acts.

## Outputs
Specific application approval or durable awaiting-approval state.

## Gates
Resume approval, inclusion permission, daily target, prior application or scheduled routine never substitutes for this approval.

## Recovery
Any changed payload invalidates dependent approval. Preserve old decisions as superseded and ask only for the changed current scope.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Inherited application-approval](../../../job-applier/steps/application-approval/SKILL.md).
[ATS reconciliation](../ats-reconciliation/SKILL.md) and [receipt reconciliation](../../subskills/receipt-reconciliation/SKILL.md).
