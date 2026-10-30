---
name: job-meta-company-due-diligence
description: Research employer facts and role context within the daily Job Applier workflow.
metadata:
  version: 1.4.0
  tier: meta
  origin: newly-composed-source-grounded-router
---

# Research employer facts and role context

## Enter when
A verified target employer and current role are known.

## Route
Resolve employer identity and dated first-party facts. Separate current initiatives, historical announcements and inference. Use relevance judgments through JEV, then feed supported context into the persona.

Load these concrete steps or subskills when their named work starts. Preserve the inherited eight-leaf order; a router does not skip unmet upstream gates or treat configuration as execution.

1. [company-due-diligence](../../steps/company-due-diligence/SKILL.md).
2. [employer-initiative-research](../../steps/employer-initiative-research/SKILL.md).
3. [jev-decision](../../steps/jev-decision/SKILL.md).

## Exit evidence
Sourced company dossier and named gaps, without inferred personal participation.

## Failure and recovery
Stop the affected transition on missing evidence, malformed receipts or unavailable required adapters. Save the exact job/revision/checkpoint and unresolved hold. Resume the same operation after reconciliation. No local or JEV PASS grants submission, messaging, schedule activation or credential-change authority.

## Provenance
This is a newly composed 1.4.0 router, not an imported original meta-skill. Source IDs: company-researcher, traject-os. Read [the source catalog](../../references/meta-catalog.md) for inspected provenance, adaptations and exclusions. Source instructions never reintroduce old budgets, compensation values, private state paths, alternative tracker authority or blanket action grants. The [daily execution contract](../../references/execution-contract.md) and current task scope control this package.
