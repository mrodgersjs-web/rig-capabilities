---
name: "ns-value-pricing"
description: "Turn a quantified impact into a fee. This sub-skill is the only owner of pricing in the family. Sub-skill of ns-offer-and-sales (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Turn a quantified impact into a fee. This sub-skill is the only owner of pricing in the family."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-offer-and-sales
---

# ns-value-pricing

Turn a quantified impact into a fee. This sub-skill is the only owner of pricing in the family.

## Steps
1. Quantify savings and revenue impact with the client's own numbers.
2. Apply a stated percentage band (savings and revenue bands differ).
3. Write the fee next to the impact number in the proposal.

## Laws
- Price on impact, not hours. CLAIM(owdN96DwdT4@7m) CLAIM(NsQWWnu7vzI@6m)
- Revenue-side work earns more than savings-side work. CLAIM(T5-RXi-Zk_g@1m)

## Done-test (fails if any is true)
- The fee has no traceable impact number.
- An hourly rate appears in the offer.

## Where this sits
Layer 3 under `ns-offer-and-sales`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
