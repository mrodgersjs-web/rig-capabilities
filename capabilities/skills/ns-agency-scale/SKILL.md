---
name: "ns-agency-scale"
description: "Find the one constraint limiting throughput, widen it, measure again, and productize whatever repeats. Nick Saraev method. Use for: we are stuck; where is the bottleneck; should I hire; productize this; delivery takes too long; next stage of growth."
tier: main
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Find the one constraint limiting throughput, widen it, measure again, and productize whatever repeats."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: nick-saraev-os
  stage_doctrine: references/doctrine.md
---

# ns-agency-scale

Find the one constraint limiting throughput, widen it, measure again, and productize whatever repeats.

**Use when:** we are stuck; where is the bottleneck; should I hire; productize this; delivery takes too long; next stage of growth.

## Laws
- The slowest stage sets total output, however fast the others are. CLAIM(8HQb8aji_xs@4m) CLAIM(wamAXd1V5C8@4m) CLAIM(miM6LCX08VQ@1m)
- Gains at the bottleneck flow straight to output; gains elsewhere are wasted. CLAIM(8HQb8aji_xs@20m) CLAIM(8HQb8aji_xs@11m)
- Choosing the right task matters more than doing tasks fast. CLAIM(8HQb8aji_xs@21m) CLAIM(cWYnMhu3AFg@2m)
- Fixing one bottleneck exposes the next, so this is a loop, not a project. CLAIM(8HQb8aji_xs@8m) CLAIM(wamAXd1V5C8@9m)
- Start custom, then productize: custom work proves demand and pays for the skill gap. CLAIM(g1iiirHCEbM@17m) CLAIM(52yOx4nAGM8@19m)
- Run AI as a normal service business; lead gen, sales and retention matter more than build cleverness. CLAIM(L4Qbx8OM9l4@4m) CLAIM(52yOx4nAGM8@0m)
- Do not add headcount before fixing operations; hire on paid work tests, not resumes. CLAIM(zAMoAWA_BOE@0m) CLAIM(YLg8HTafhlk@3m) CLAIM(gGo7M4cvPxQ@8m)

## Procedure: Bottleneck cycle, then crystallize
1. Map the pipeline from lead intake to completion. CLAIM(8HQb8aji_xs@1m) CLAIM(wamAXd1V5C8@2m)
2. Name the stage with the lowest throughput. CLAIM(wamAXd1V5C8@4m)
3. Pick the fix type: widen inputs if it works but is slow, research if it fails, structural change otherwise. CLAIM(8HQb8aji_xs@14m) CLAIM(wamAXd1V5C8@7m)
4. Widen it, measure again, name the new bottleneck. CLAIM(wamAXd1V5C8@8m) CLAIM(8HQb8aji_xs@9m)
5. Go through finished projects for repeated deliverables and turn them into templates. CLAIM(g1iiirHCEbM@17m) CLAIM(g1iiirHCEbM@21m) CLAIM(m4yA2A-gPwk@16m)

## Sub-skills (load one at a time)
- `ns-bottleneck-diagnosis`: Measure each stage's throughput, name the single constraint and pick the fix type.
- `ns-productization`: Mine finished project logs for repeated blocks and turn them into templates and SOPs.
- `ns-delegation`: Hand the bottleneck to a new agent harness or a contractor, gated by a paid work test.

## Done-test (fails if any is true)
- Any stage on the map has no measured throughput.
- More than one bottleneck is named.
- The fix targets a stage that is not the bottleneck.
- There is no before-and-after measurement.
- A template is promoted with fewer than two finished projects behind it.

## Does not fit RIG
- Revenue bands tied to hiring staff: for a solo fractional CAIO the scaling unit is a new governed agent harness or a contractor, gated by a paid test.
- Fixed revenue thresholds for hiring; use the bottleneck test instead.

## Deeper doctrine
`references/doctrine.md` holds the full stage doctrine: core laws marked consensus or single-source, procedures, decision rules, failure modes and changed views, all cited. Malformed tags from distillation were removed by the tag validator.

## Where this sits
Layer 2 under `nick-saraev-os`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
