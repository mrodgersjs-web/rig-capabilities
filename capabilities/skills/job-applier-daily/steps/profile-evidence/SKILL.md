---
name: job-daily-profile-evidence
description: Capture current candidate evidence and constraints before discovery or tailoring.
metadata:
  version: 1.4.0
  origin: newly-composed-source-grounded-step
---

# Profile evidence

## Inputs
Selected original Word resume; Mike's current role, location, work-arrangement and compensation constraints; supported career artifacts.

## Actions
Hash the selected master and retain it unchanged. Inventory source-backed employers, roles, dates, education, credentials and metrics. Keep grouped dates grouped. Distinguish employers from clients/partners. Record current constraints with their direct response references; do not import stale defaults. Inventory screening questions as confirmed, unknown or needs-current-confirmation without copying credentials or private answer stores into the package.

## Outputs
Profile evidence index with source IDs/hashes, employer alias evidence, current constraints and unresolved screening facts.

## Gates
No memory, generated persona, company announcement or LinkedIn wording overrides the selected career evidence. Unknown facts remain questions; a source conflict holds the affected claim.

## Recovery
Keep the prior source revision. When Mike changes masters or corrects a fact, invalidate dependent claims/documents and refresh only affected approvals. Missing source DOCX holds Word preparation but permits clearly labeled research.

## Required skills and contracts
- [evidence-alignment](../../steps/evidence-alignment/SKILL.md).
- [contribution-questions](../../subskills/contribution-questions/SKILL.md).

Follow the [daily execution contract](../../references/execution-contract.md). Source IDs resume-only, julie-w2 identify the inspected antecedents in [the provenance catalog](../../references/meta-catalog.md). This is a newly composed portable adaptation; it does not import those sources' historical private paths, grants, compensation defaults or alternative ledgers. Real receipts and current approvals remain required.
