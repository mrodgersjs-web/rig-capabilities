---
name: job-applier-ideal-achievement-bank
description: Write an ideal result/action/strategy example for every substantive requirement.
metadata:
  parent: job-applier
  version: 1.2.1
---

# Ideal Achievement Bank

## Inputs

Current full persona, inventory, JD and persona-review receipt.

## Outputs

achievement_bank.json plus readable requirement-to-example table; each example has stable ID, requirement IDs, result, personal_action, strategy and hypothetical_not_candidate_fact status.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

Write ideal evidence patterns for responsibilities AND minimum/preferred qualifications and gaps. Hard constraints still need explicit coverage; do not invent an achievement that pretends a credential or location requirement has been met. Describe the ideal proof and flag its factual gap. Include mechanism, scope and defensible metric shape; proposed numbers remain explicitly hypothetical. Distinct requirements need relevant examples. Shared examples need an explicit substantive rationale, not repetition. Never put these research examples into Mike's factual record.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

Every inventory ID covered, no invented IDs or duplicated generic example, current persona/JD binding.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

../evidence-alignment/SKILL.md
