---
name: job-applier-document-quality
description: Verify template fidelity, all fifteen quality criteria and actual rendered pages.
metadata:
  parent: job-applier
  version: 1.2.2
---

# Document Quality

## Inputs

Current reviewed clean DOCX, source template/hash, persona, JD, claim decisions and before/after map.

## Outputs

images.json with actual page-file hashes and clean DOCX hash; quality.json with actual typed Jev decision ID, all 15 criteria and original provider receipt; Mike's exact-page approval evidence added to confirmations.json.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

Read ../../references/quality-gates.md. Follow [original Word fidelity](../../references/word-format-fidelity.md). Compare paragraph/run properties, tabs, date alignment, bullets, spacing and section order, plus styles/numbering/section properties. Render original and output with the same renderer/settings and inspect every page. Style-hash or paragraph-count parity alone cannot pass; check rendered content-fit line budgets and original break intent, with no newly orphaned headings/bullets or unexplained extra pages; reject inserted banners, inline hold notes, JD checklists or process paragraphs in the resume body. Inspect the separate linked worksheet and exact draft/claim bindings for UNCONFIRMED proposals. Review actual pixels for red-review clarity, final typography, clipping, whitespace and pagination. Sanitized page images require actual redaction review before provider transmission. Jev unavailability or uncertainty stays a hold. Passing structure is not semantic truth or an image verdict. Show Mike the exact clean pages and obtain his approval bound to their image manifest and DOCX hash. Any edited document invalidates page approval and downstream receipts. The final contains no UNCONFIRMED content, hypothetical patterns, unresolved placeholders or working labels.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

Current source, persona, content and images bound; actual required passing Jev receipts plus factual review and exact-page human approval. Run structural validator -- it adds no approval authority.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

../application-approval/SKILL.md
