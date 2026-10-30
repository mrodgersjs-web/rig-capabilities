---
name: job-meta-airtable-tracker
description: Maintain the single authoritative application tracker within the daily Job Applier workflow.
metadata:
  version: 1.4.0
  tier: meta
  origin: newly-composed-source-grounded-router
---

# Maintain the single authoritative application tracker

## Enter when
The required Airtable base/table/view and authorized access scope are known.

## Route
Discover schema, map existing compatible fields, dedupe over the full table, and let only the coordinator write. Reconcile lost acknowledgments before another mutation.

Load these concrete steps or subskills when their named work starts. Preserve the inherited eight-leaf order; a router does not skip unmet upstream gates or treat configuration as execution.

1. [schema-mapping](../../subskills/schema-mapping/SKILL.md).
2. [duplicate-identity](../../subskills/duplicate-identity/SKILL.md).
3. [airtable-ledger](../../steps/airtable-ledger/SKILL.md).

## Exit evidence
Verified record/readback state or explicit schema/sync/unknown hold.

## Failure and recovery
Stop the affected transition on missing evidence, malformed receipts or unavailable required adapters. Save the exact job/revision/checkpoint and unresolved hold. Resume the same operation after reconciliation. No local or JEV PASS grants submission, messaging, schedule activation or credential-change authority.

## Provenance
This is a newly composed 1.4.0 router, not an imported original meta-skill. Source IDs: daily-airtable, julie-w2. Read [the source catalog](../../references/meta-catalog.md) for inspected provenance, adaptations and exclusions. Source instructions never reintroduce old budgets, compensation values, private state paths, alternative tracker authority or blanket action grants. The [daily execution contract](../../references/execution-contract.md) and current task scope control this package.
