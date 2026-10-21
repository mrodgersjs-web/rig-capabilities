---
name: "ns-niche-and-offer"
description: "Pick the niche and design a first project with a built-in path to the next service. Sub-skill of ns-offer-and-sales (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Pick the niche and design a first project with a built-in path to the next service."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-offer-and-sales
---

# ns-niche-and-offer

Pick the niche and design a first project with a built-in path to the next service.

## Steps
1. Name the buyer, the bottleneck and the money it costs.
2. Design a first project deliverable in weeks, not months.
3. Name the follow-on service the first project leads to.

## Laws
- First projects should be quick, low-risk and lead to the next need. CLAIM(ArNmQRpctIc@3m) CLAIM(ArNmQRpctIc@22m) CLAIM(RmYTguzXrVM@9m)
- Sell deterministic systems over all-in-one agents. CLAIM(whXs1RaQIDA@26m)

## Done-test (fails if any is true)
- No follow-on service is named.
- The first project cannot ship within the stated window.

## Where this sits
Layer 3 under `ns-offer-and-sales`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
