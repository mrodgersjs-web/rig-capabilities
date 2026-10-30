---
name: job-daily-format-comparison
description: Compare source and tailored Word structure and every actual rendered page.
metadata:
  version: 1.3.0
---

# Format comparison

## Inputs
Immutable original DOCX, red/clean outputs, cover letter, exact renderer identity and settings.

## Actions
Compare paragraph/run properties, fonts, numbering, tabs, margins, headers, sections, date alignment and history. Render original and outputs with the same renderer/settings. Inspect every page for clipping, orphan headings/bullets and blank spill pages. Fit wording to existing slots rather than shrinking format.

## Outputs
Property diff, source/output hashes, page manifests, actual visual inspection record and holds.

## Gates
Matching styles alone is insufficient. Missing pixels, removed history, unexplained page drift or hidden shrinkage blocks final readiness. Cover-letter layout also requires all-page review.

## Recovery
Revise content within slot budgets, rerender and renew exact-page approval. Keep renderer absence explicit.

## Required skills and contracts
[Original Word fidelity](../../../job-applier/references/word-format-fidelity.md).
