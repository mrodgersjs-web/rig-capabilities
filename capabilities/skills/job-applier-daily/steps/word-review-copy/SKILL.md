---
name: job-daily-word-review-copy
description: Create the full provisional review packet without replacing the original Word design.
metadata:
  version: 1.3.0
---

# Word review copy

## Inputs
Immutable original DOCX, evidence alignment, full persona and source-bound initiative questions.

## Actions
Execute inherited word-review-copy. Then execute resume-writer, cover-letter-writer and slopmonster-review. Render current documents and compare the resume to the original. Keep process notes and questions in the linked worksheet.

## Outputs
Red review resume, separate supported clean resume, provisional cover letter, worksheet and before/after map with exact hashes.

## Gates
Unconfirmed propositions remain explicit red proposals or worksheet items. No generic rebuilt template or source-only final claim.

## Recovery
Preserve drafts when rendering fails and label affected visual state held. Changes require rerender.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Inherited word-review-copy](../../../job-applier/steps/word-review-copy/SKILL.md).
[Resume writer](../resume-writer/SKILL.md), [cover-letter writer](../cover-letter-writer/SKILL.md), [SlopMonster review](../slopmonster-review/SKILL.md), [format comparison](../../subskills/format-comparison/SKILL.md).
