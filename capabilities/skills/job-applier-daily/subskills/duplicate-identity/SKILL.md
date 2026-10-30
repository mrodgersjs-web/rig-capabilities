---
name: job-daily-duplicate-identity
description: Resolve employer and requisition aliases into one stable application lineage.
metadata:
  version: 1.3.0
---

# Duplicate identity

## Inputs
Candidate identity, employer/ATS identifiers, canonical posting URL and fully paginated table records.

## Actions
Prefer candidate plus normalized employer plus ATS requisition. Use deterministic canonical URL only if requisition absent. Preserve employer alias evidence. Match across the full table and saved operation history. A changed JD remains the same lineage; a genuinely different requisition needs its own reviewed identity.

## Outputs
Stable job key, matched record/workflow IDs and duplicate decision evidence.

## Gates
Incomplete reads, ambiguous aliases, multiple candidate matches or uncertain prior submission remain holds. Do not create per-day random keys.

## Recovery
Reconcile old intents and records before any create. Retain unknown submissions across dates.

## Required skills and contracts
[Airtable contract](../../references/airtable-contract.md) and [execution contract](../../references/execution-contract.md).
