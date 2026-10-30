---
name: job-meta-jev-decision
description: Obtain typed source-bound transition decisions within the daily Job Applier workflow.
metadata:
  version: 1.4.0
  tier: meta
  origin: newly-composed-source-grounded-router
---

# Obtain typed source-bound transition decisions

## Enter when
A bounded sanitized question, fixed answer set and consuming gate are defined.

## Route
Use the JEV decision adapter with actual provider receipts. Validate types, provenance and source hashes. Preserve holds; send missing facts to confirmation rather than inventing a local verdict.

Load these concrete steps or subskills when their named work starts. Preserve the inherited eight-leaf order; a router does not skip unmet upstream gates or treat configuration as execution.

1. [jev-decision](../../steps/jev-decision/SKILL.md).
2. [targeted-confirmation](../../steps/targeted-confirmation/SKILL.md).
3. [application-approval](../../steps/application-approval/SKILL.md).

## Exit evidence
Original typed receipt with valid current bindings, or explicit deferred transition.

## Failure and recovery
Stop the affected transition on missing evidence, malformed receipts or unavailable required adapters. Save the exact job/revision/checkpoint and unresolved hold. Resume the same operation after reconciliation. No local or JEV PASS grants submission, messaging, schedule activation or credential-change authority.

## Provenance
This is a newly composed 1.4.0 router, not an imported original meta-skill. Source IDs: typesafe-jev, jev-everywhere, job-quality. Read [the source catalog](../../references/meta-catalog.md) for inspected provenance, adaptations and exclusions. Source instructions never reintroduce old budgets, compensation values, private state paths, alternative tracker authority or blanket action grants. The [daily execution contract](../../references/execution-contract.md) and current task scope control this package.
