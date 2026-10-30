---
name: job-meta-fit-prioritization
description: Apply current fit constraints and rank eligible roles within the daily Job Applier workflow.
metadata:
  version: 1.4.0
  tier: meta
  origin: newly-composed-source-grounded-router
---

# Apply current fit constraints and rank eligible roles

## Enter when
Full postings and confirmed candidate constraints are available.

## Route
Apply deterministic hard constraints first. Send bounded semantic fit questions through JEV with the current rubric and source hashes. Keep unknown pay/credentials explicit and never import historical defaults.

Load these concrete steps or subskills when their named work starts. Preserve the inherited eight-leaf order; a router does not skip unmet upstream gates or treat configuration as execution.

1. [fit-prioritization](../../steps/fit-prioritization/SKILL.md).
2. [jev-decision](../../steps/jev-decision/SKILL.md).
3. [duplicate-identity](../../subskills/duplicate-identity/SKILL.md).

## Exit evidence
Eligible ranked queue with original typed receipts, or held/rejected roles with reasons.

## Failure and recovery
Stop the affected transition on missing evidence, malformed receipts or unavailable required adapters. Save the exact job/revision/checkpoint and unresolved hold. Resume the same operation after reconciliation. No local or JEV PASS grants submission, messaging, schedule activation or credential-change authority.

## Provenance
This is a newly composed 1.4.0 router, not an imported original meta-skill. Source IDs: target-qualify, jev-everywhere. Read [the source catalog](../../references/meta-catalog.md) for inspected provenance, adaptations and exclusions. Source instructions never reintroduce old budgets, compensation values, private state paths, alternative tracker authority or blanket action grants. The [daily execution contract](../../references/execution-contract.md) and current task scope control this package.
