---
name: job-daily-document-quality
description: Review supported final Word documents, actual pages and current typed quality receipts.
metadata:
  version: 1.3.0
---

# Document quality

## Inputs
Resolved claim/inclusion decisions, final resume/letter revisions, source master and current render manifests.

## Actions
Execute inherited document-quality after incorporating decisions. Rerun the resume/letter writers and SlopMonster on changed content. Inspect every original/output page and all fifteen criteria. Use an independent final reviewer and authenticated exact-page approval.

## Outputs
Final resume and letter, page manifests, visual comparison, independent reviewer evidence and current JEV receipts.

## Gates
No simulated images, text-only layout proof, unknown JEV result, stale hash or unresolved candidate claim passes.

## Recovery
Repair precise defects; rerender affected files and renew dependent approvals without repeating unchanged JEV requests until PASS.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Inherited document-quality](../../../job-applier/steps/document-quality/SKILL.md).
[Acceptance](../../references/acceptance.md) and [format comparison](../../subskills/format-comparison/SKILL.md).
