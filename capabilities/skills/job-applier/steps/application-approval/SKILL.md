---
name: job-applier-application-approval
description: Stage one exact application; submit only with specific authorization and retain its real receipt.
metadata:
  parent: job-applier
  version: 1.2.1
---

# Application Approval

## Inputs

Final reviewed DOCX/hash, employer/title/requisition/destination, exact form answers and attachments, duplicate-check result, current quality and human-page approval.

## Outputs

Approval evidence for this specific application and, only after authorized submission, actual employer/ATS receipt bound to target and exact DOCX hash. Before submission retain awaiting_application_approval state.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

Read ../../references/pilot-and-recovery.md. Present exact destination, resume, fields, optional attachments and attestations. Resume approval is not submission approval. The local app stages only. Do not invent screening answers, consent or protected demographic data. If explicitly approved, use the established operator within scope, retain provider receipt, and reconcile unknown outcomes before retrying. Count the first five only from real receipts. A click, test, saved approval or successful draft never counts as submitted.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

Specific current application authorization before outward action; actual receipt before submitted claim. No approval or missing receipt means stop or reconcile, not infer success.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

Stop after receipt or hold; no automatic next application.
