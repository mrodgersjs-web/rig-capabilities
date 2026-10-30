---
name: job-daily-daily-discovery
description: Discover eligible current jobs within daily limits and attach existing lineages.
metadata:
  version: 1.3.0
---

# Daily discovery

## Inputs
Verified preflight, current candidate constraints, full-table tracker snapshot, remaining run budget.

## Actions
Find official employer postings. Apply confirmed constraints. Normalize identity and reconcile existing applications before admission. Stop at active-lineage cap or exhausted time/calls; target thirty is not a requirement to manufacture matches.

## Outputs
Candidate queue with source URLs, stable identity, admission reasons and explicit holds.

## Gates
No incomplete dedupe, closed posting, relaxed candidate constraint or admission beyond cap.

## Recovery
Save cursor and checkpoint. Resume exact job identities; do not restart quotas after a crash.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Duplicate identity](../../subskills/duplicate-identity/SKILL.md) and [Airtable ledger](../airtable-ledger/SKILL.md).
