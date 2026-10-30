---
name: job-meta-jev-image
description: Review actual rendered Word page images within the daily Job Applier workflow.
metadata:
  version: 1.4.0
  tier: meta
  origin: newly-composed-source-grounded-router
---

# Review actual rendered Word page images

## Enter when
Current source/output DOCX files and a verified renderer are available.

## Route
Compare Word properties and actual rendered pages, sanitize image payloads, and call the image adapter. Preserve uncertain image judgments and obtain exact-page human review.

Load these concrete steps or subskills when their named work starts. Preserve the inherited eight-leaf order; a router does not skip unmet upstream gates or treat configuration as execution.

1. [format-comparison](../../subskills/format-comparison/SKILL.md).
2. [jev-image](../../steps/jev-image/SKILL.md).
3. [document-quality](../../steps/document-quality/SKILL.md).

## Exit evidence
All-page manifests, real image review receipt and current page approval or hold.

## Failure and recovery
Stop the affected transition on missing evidence, malformed receipts or unavailable required adapters. Save the exact job/revision/checkpoint and unresolved hold. Resume the same operation after reconciliation. No local or JEV PASS grants submission, messaging, schedule activation or credential-change authority.

## Provenance
This is a newly composed 1.4.0 router, not an imported original meta-skill. Source IDs: job-quality, word-fidelity. Read [the source catalog](../../references/meta-catalog.md) for inspected provenance, adaptations and exclusions. Source instructions never reintroduce old budgets, compensation values, private state paths, alternative tracker authority or blanket action grants. The [daily execution contract](../../references/execution-contract.md) and current task scope control this package.
