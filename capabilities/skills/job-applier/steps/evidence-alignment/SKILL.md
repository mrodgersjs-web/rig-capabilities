---
name: job-applier-evidence-alignment
description: Align ideal proof to Mike without converting research into facts.
metadata:
  parent: job-applier
  version: 1.2.1
---

# Evidence Alignment

## Inputs

Ideal bank, full persona, atomic inventory, selected resume, source-backed career evidence, refreshed authenticated GitHub account/repository inventory and the existing portfolio evidence bank.

## Outputs

alignment.json with stable claim IDs, example/requirement IDs, confirmed/adjacent/unconfirmed status, source IDs, actual employer/role/period/ownership/result where known, gaps and targeted questions.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

First read [the GitHub portfolio evidence contract](../../references/github-portfolio-evidence.md). On every role, inventory all currently accessible authenticated accounts and repositories, including private repositories within the approved scope. Inspect JD-relevant source and tests at exact commit SHAs. Save `portfolio_audit` with inventory coverage, source paths, implementation status, inspection/execution distinction, requirement IDs and remaining attribution/outcome gaps. If access is unavailable, record a visible partial audit and never claim the public subset represents the full estate. Use verified implementation evidence for cautious capability wording; do not turn ownership of a repository or an imported fork into personal authorship.


Keep persona research separate from candidate facts. Use confirmed only with actual supporting evidence and attribution. Adjacent experience retains its actual industry and scope. Unconfirmed examples remain UNCONFIRMED. Tentative employer placement is a review suggestion, not attribution. Do not fabricate metrics, tenure, credentials, production ownership or sole credit. A hypothetical origin requires explicit factual confirmation evidence before it can become confirmed. Do not withhold the useful full review draft while waiting for a full questionnaire.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

Every requirement represented by supported alignment or a visible gap; authenticated account coverage and JD-relevant source inspection recorded; private material sanitized; personal contribution and outcomes distinguished from code evidence. Audit/access gaps remain visible holds on affected portfolio claims, not an excuse to withhold the useful red review draft. No silent invention or promotion.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

../word-review-copy/SKILL.md
