---
name: job-applier-word-review-copy
description: Produce the whole job-specific Word review copy with visibly red unconfirmed examples.
metadata:
  parent: job-applier
  version: 1.2.2
---

# Word Review Copy

## Inputs

Immutable selected source DOCX/hash, full persona, ideal bank, alignment and source facts.

## Outputs

Separate red review DOCX, clean supported-content DOCX, and linked review worksheet containing before/after changes, requirement map, gaps and explicit UNCONFIRMED draft/claim bindings. The clean copy remains provisional until factual/page review.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

Read [the original Word fidelity contract](../../references/word-format-fidelity.md). Use the immutable master as the actual DOCX package, editing existing appropriate paragraph/run slots. Preserve tabs, date alignment, bullets, spacing, section order and all original formatting. Do not prepend banners, inline editorial arrows/holds, UNCONFIRMED paragraphs, a JD checklist or questions in the resume body. Keep process notes, before/after map, requirement coverage, gaps and unplaced hypothetical patterns in a separate linked review worksheet.

Apply actual FF0000 run color to tailored proposals in appropriate existing slots. Explicit UNCONFIRMED status/tentative placement belongs in Word comments or the linked worksheet bound to exact draft hash and claim ID; do not add body paragraphs for labels. Render to verify visible red. The separate clean version retains supported original wording where a proposed replacement remains unconfirmed. Do not delete employment history, shrink formatting or deliver a source-only copy as completed tailoring. Include meaningful role-specific edits and the full supported resume. Fit rewritten headline, summary and bullets to the original rendered slot line budgets and preserve explicit break intent; correct overflow through concise supported wording, never hidden layout changes. A text-identical clean copy is SOURCE-ONLY RECOVERY — TAILORING INCOMPLETE and remains held. Render original and output with the same renderer/settings and inspect all pages; style hashes alone are insufficient.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

Immutable source hash, actual DOCX styling/color inspection, complete before/after map and full draft. Red proposals have explicit comment/worksheet status bindings and are excluded from the clean copy until supported. Property checks plus all-page same-renderer comparison pass; no process material was inserted in the resume body.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

../targeted-confirmation/SKILL.md
