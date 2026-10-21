---
name: "ns-productization"
description: "Mine finished project logs for repeated blocks and turn them into templates and SOPs. Sub-skill of ns-agency-scale (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Mine finished project logs for repeated blocks and turn them into templates and SOPs."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-agency-scale
---

# ns-productization

Mine finished project logs for repeated blocks and turn them into templates and SOPs.

## Steps
1. Collect at least two finished projects.
2. Mark the deliverables that repeat.
3. Template them and time the next delivery against the old one.

## Laws
- Productize after custom work proves the pattern. CLAIM(g1iiirHCEbM@17m) CLAIM(52yOx4nAGM8@19m)
- Templates cut delivery time sharply. CLAIM(g1iiirHCEbM@21m) CLAIM(gjW084ll5T8@19m)

## Done-test (fails if any is true)
- A template ships from one project.
- No before-and-after delivery time is recorded.

## Where this sits
Layer 3 under `ns-agency-scale`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
