---
name: job-daily-airtable-ledger
description: Synchronize the authoritative application tracker with schema and readback proof.
metadata:
  version: 1.3.0
---

# Airtable ledger

## Inputs
Target base/table/view, verified mapping or schema discovery capability, stable job key, checkpoint and authorized mutation scope.

## Actions
Discover schema before writes. Read complete table for identity matches. Coordinator writes only mapped existing compatible fields, preserving unrelated values. Save intent, real response and readback; detect conflicts.

## Outputs
Record ID, schema fingerprint, actual write/readback receipts or sync/schema/unknown hold.

## Gates
Empty mapping, incomplete reads, wrong base/table, missing permissions or uncertain prior writes block outward progress. No auto field creation.

## Recovery
Reconcile by stable identity before retry. If already submitted retain receipt and repair tracking only.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Airtable contract](../../references/airtable-contract.md), [schema mapping](../../subskills/schema-mapping/SKILL.md), [duplicate identity](../../subskills/duplicate-identity/SKILL.md).
