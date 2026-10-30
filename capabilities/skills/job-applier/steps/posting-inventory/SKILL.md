---
name: job-applier-posting-inventory
description: Capture the current posting and enumerate every atomic requirement.
metadata:
  parent: job-applier
  version: 1.2.1
---

# Posting Inventory

## Inputs

Official employer/ATS URL, existing application record, selected immutable master resume.

## Outputs

Captured complete JD with URL/time/hash, verified target identity and activity evidence, duplicate check, inventory.json with stable IDs and exact JD quotations for responsibilities, minimum and preferred qualifications, location/work arrangement and other constraints.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

Compare every substantive JD clause against the inventory. Split compound clauses so missing qualifications cannot hide inside a broad responsibility. Record coverage review evidence. A closed/stale/mismatched/incomplete posting blocks this job. Use the existing source admission and active-identity receipts in the workflow contract.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

Full current posting and complete atomic inventory are required; no aggregate title-only substitute.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

../ideal-candidate-persona/SKILL.md
