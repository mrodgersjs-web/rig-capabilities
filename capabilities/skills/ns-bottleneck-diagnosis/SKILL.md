---
name: "ns-bottleneck-diagnosis"
description: "Measure each stage's throughput, name the single constraint and pick the fix type. Sub-skill of ns-agency-scale (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Measure each stage's throughput, name the single constraint and pick the fix type."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-agency-scale
---

# ns-bottleneck-diagnosis

Measure each stage's throughput, name the single constraint and pick the fix type.

## Steps
1. List stages with a weekly throughput number each.
2. Name the lowest one.
3. Choose widen, research or restructure.
4. Re-measure after the fix.

## Laws
- One stage limits the whole system. CLAIM(8HQb8aji_xs@4m) CLAIM(wamAXd1V5C8@4m)
- Effort off the bottleneck produces no growth. CLAIM(8HQb8aji_xs@21m)

## Done-test (fails if any is true)
- A stage has no number.
- Two bottlenecks are named.

## Where this sits
Layer 3 under `ns-agency-scale`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
