---
name: "ns-delegation"
description: "Hand the bottleneck to a new agent harness or a contractor, gated by a paid work test. Sub-skill of ns-agency-scale (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Hand the bottleneck to a new agent harness or a contractor, gated by a paid work test."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-agency-scale
---

# ns-delegation

Hand the bottleneck to a new agent harness or a contractor, gated by a paid work test.

## Steps
1. Write the SOP for the bottleneck task.
2. For repeated patterns (3+ times) build an agent harness; otherwise test a contractor on a paid task.
3. Keep acceptance with a separate reviewer.

## Laws
- Fix operations before adding people. CLAIM(zAMoAWA_BOE@0m) CLAIM(zAMoAWA_BOE@3m)
- Hire on paid work tests, not resumes. CLAIM(YLg8HTafhlk@3m) CLAIM(gGo7M4cvPxQ@8m)

## Done-test (fails if any is true)
- Someone is hired with no paid test.
- No SOP exists for the delegated task.

## Where this sits
Layer 3 under `ns-agency-scale`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
