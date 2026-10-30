---
name: job-applier-ideal-candidate-persona
description: Build the FULL IDEAL CANDIDATE PERSONA on every run before achievements or resume drafting.
metadata:
  parent: job-applier
  version: 1.2.1
---

# Ideal Candidate Persona

## Inputs

Exact captured JD, target identity, complete atomic inventory and optional relevant public employer/industry sources.

## Outputs

persona.json and human-readable full persona; persona_review.json with actual typed Jev decision and provider response bound to JD, inventory and persona hashes.

## Execute

Run this leaf in one bounded Aside session using [the context and recovery limits](../../references/bounded-step-execution.md). Use checkpoint pointers/hashes, at most 8,000 source-pack tokens and 1,500 characters per shown tool result by default. On context-limit failure, stop the old session and recover this same logical step from its checkpoint in a fresh session; retain attempt caps, holds and existing-operation state.

Create all 13 persona sections defined in ../../references/family-packet.md. Explain the mandate, decision rights, operating environment, industry/economics, first 90-day and year-one outcomes, capability depth, leadership behaviors, ideal career proof and metrics, hard criteria, tradeoffs/failure modes, likely hiring questions, and adjacent versus direct fit. Cover each requirement ID. Describe what excellent performance would require, not just a paraphrase of the role title. Separate explicit JD expectations, public-source evidence and labeled inferences; never invent private hiring-manager beliefs. Ideal proof metrics are illustrative expectations, never candidate history. Produce the full persona on every run, including recovery. Historical persona/ideal Markdown cannot bypass current content/hash/identity checks. Semantic completeness requires a current real Jev receipt; the structural validator cannot detect generic prose. Preserve any semantic hold and repair the persona before advancing.

Read [the packet contract](../../references/family-packet.md). Log this leaf's exact path, current artifact hashes, actual command/tool invocation, timestamps and retained response artifact. A checked box, invented receipt or boolean is not execution evidence. Follow existing privacy and approval boundaries.

## Gate

All sections, requirement coverage, current bindings and actual passing persona review. Missing provider leaves the persona saved but held.

## Daily durable checkpoint

When running the daily process, execute this leaf as its own durable child workflow under [the daily Temporal contract](../../references/temporal-daily-workflow.md). Bind the existing job/step/revision identity, inputs/outputs, Aside session/task IDs and actual activity receipts. Resume accepted work before redispatch; preserve human/Jev holds and exact hash-bound approvals across worker restart. This instruction is a runtime requirement, not evidence that Temporal integration exists.

## Next skill

../ideal-achievement-bank/SKILL.md
