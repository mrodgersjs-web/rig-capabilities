---
name: job-daily-posting-inventory
description: Capture the full active posting and preserve stable application identity.
metadata:
  version: 1.3.0
---

# Posting inventory

## Inputs
Official posting URL, candidate constraints, source resume and authoritative tracker snapshot.

## Actions
Execute inherited posting-inventory. Capture complete JD, active identity evidence and each atomic responsibility/qualification. Bind source hashes and dedupe before admission.

## Outputs
Current target/JD/inventory and actual posting review receipt.

## Gates
Missing full JD, stale/closed identity or unresolved duplicate stops this role.

## Recovery
Refresh changed sources and invalidate downstream dependencies; retain existing lineage.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Inherited posting-inventory](../../../job-applier/steps/posting-inventory/SKILL.md).
[Duplicate identity](../../subskills/duplicate-identity/SKILL.md).
