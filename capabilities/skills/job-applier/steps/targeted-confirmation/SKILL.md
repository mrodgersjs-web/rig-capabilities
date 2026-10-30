---
name: job-applier-targeted-confirmation
description: Ask only the specific factual questions the full review draft exposes.
metadata:
  parent: job-applier
  version: 1.2.1
---

# Targeted Confirmation

## Inputs

Exact red review DOCX/hash, clean provisional copy, claim ledger and requirement map.

## Outputs

confirmations.json with per-claim confirm/replace/omit, Mike's actual response references and exact draft binding; revised documents and invalidated stale receipts when facts change.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

Walk Mike through consequential unconfirmed/adjacent claims, employer placement, personal contribution, outcome/units and period. Ask focused questions after delivering the full useful draft. “Sounds good” or wording approval does not confirm facts. Preserve candidate-reported provenance. Replace with supported facts, narrow or omit. Never carry hypothetical achievements into the final version without explicit factual confirmation. Update hashes and rerun dependent document quality after edits. Exact-page approval is collected only after the next step renders the current clean document; it is separate from factual confirmation.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

Every retained final factual clause supported and attributable; missing information stays a gap or is omitted.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

../document-quality/SKILL.md
