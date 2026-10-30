---
name: job-daily-jev-decision
description: Run the bundled hosted TypeSafe JEV adapter and preserve real typed stage receipts.
metadata:
  version: 1.4.0
---

# Hosted JEV decision

## Inputs
Current source-bound context, candidate-authorized sanitized hosted payload, destination-owned `TYPESAFE_API_KEY`, prior immutable receipts and current artifact hashes.

## Actions
Read [the exact adapter commands](../../references/jev-adapters.md). Invoke the sibling core's `tools/resume_quality.py` for `posting`, `ideal_profile`, `working_draft`, `evidence_review`, `final_content` and `application_ready`, interleaving the two required image stages. Preserve each original result, request/response receipt and hashes. Inspect `can_advance` and the underlying receipt, not just its outer status.

## Outputs
Immutable stage result; receipt ID, request/response, rubric/request versions, source/context/artifact bindings, criterion probabilities, blocking questions and `provider_live` evidence.

## Gates
The fifteen criteria span the full workflow, with stage-specific subsets and a 0.90 support threshold. Missing, malformed, stale or non-live evidence cannot advance. Code owns readiness and permission decisions. JEV cannot establish personal contribution, supply missing facts, approve a resume, or authorize submission. Red UNCONFIRMED proposals remain provisional until the candidate explicitly confirms personal participation, contribution, result and intended inclusion. Each first-five resume is reviewed individually; exact-application approval remains separate.

## Recovery
Keep `BLOCK`, `DEFER` and `NEEDS_HUMAN_REVIEW` intact. Correct the specific source, fact, credential, schema or dependency problem before any justified rerun; preserve the earlier receipt. No repeated unchanged scoring until PASS. Missing destination credentials or hosted authorization remains a hold, never a fabricated local PASS.

## Required skills and contracts
[Meta-skill](../../SKILL.md), [JEV image](../jev-image/SKILL.md), [document quality](../document-quality/SKILL.md) and [execution contract](../../references/execution-contract.md).
