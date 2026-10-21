---
name: "ns-retainer-conversion"
description: "Move a one-off client to recurring revenue through onboarding, proactive updates and the next service. Sub-skill of ns-offer-and-sales (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Move a one-off client to recurring revenue through onboarding, proactive updates and the next service."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-offer-and-sales
---

# ns-retainer-conversion

Move a one-off client to recurring revenue through onboarding, proactive updates and the next service.

## Steps
1. Run a single structured onboarding intake.
2. Send updates every one to two days during delivery.
3. Propose the follow-on service before the first project closes.

## Laws
- Recurring beats one-off. CLAIM(T5-RXi-Zk_g@4m) CLAIM(RmYTguzXrVM@4m)
- Proactive updates keep the relationship moving. CLAIM(RmYTguzXrVM@11m)
- Onboarding is a churn defense, not admin. CLAIM(hRBL6ISvB3s@3m)

## Done-test (fails if any is true)
- No follow-on proposal was made before handoff.
- A delivery week passed with no update.

## Where this sits
Layer 3 under `ns-offer-and-sales`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
