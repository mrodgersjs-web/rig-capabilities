---
name: job-daily-resume-writer
description: Tailor a complete Word resume inside the selected original template.
metadata:
  version: 1.3.0
---

# Resume writer

## Inputs
Immutable master DOCX/hash, JD/persona, evidence alignment and claim states.

## Actions
Load Lucy. Edit a separate copy in existing slots; tailor summary, capabilities and supported experience. Keep history and format. Put red proposed text in suitable slots and UNCONFIRMED context in comments or a linked worksheet. Preserve a separate supported clean copy.

## Outputs
Red review DOCX, supported clean DOCX, exact before/after claim map and source hash.

## Gates
No invented numbers, promoted company achievements, generic rebuilt Word file, hidden shrinkage or source-only completed claim.

## Recovery
Retain text and label Word-template preservation blocked if renderer/editing support is missing.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Lucy](../../../lucy-resume-evidence/SKILL.md) and [format comparison](../../subskills/format-comparison/SKILL.md).
