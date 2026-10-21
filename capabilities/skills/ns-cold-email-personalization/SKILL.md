---
name: "ns-cold-email-personalization"
description: "Write icebreakers with two model calls (facts to JSON, then a styled rewrite) into a human-written template. Sub-skill of ns-lead-gen-outbound (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Write icebreakers with two model calls (facts to JSON, then a styled rewrite) into a human-written template."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-lead-gen-outbound
---

# ns-cold-email-personalization

Write icebreakers with two model calls (facts to JSON, then a styled rewrite) into a human-written template.

## Steps
1. Scrape several pages of the prospect site.
2. Call 1: extract facts as JSON.
3. Call 2: write the icebreaker against a style example into the template slot.
4. Queue for approval; never auto-send.

## Laws
- Deeper site reading drives better personalization. CLAIM(oAWe5wFwHlo@10m)
- Split extraction from writing into two calls. CLAIM(yYVfcfa7n5A@18m) CLAIM(yYVfcfa7n5A@15m)
- AI fills slots; humans write the template. CLAIM(5E580yoD4eo@6m)

## Done-test (fails if any is true)
- An icebreaker contains praise with no specific fact.
- The model wrote the whole email.
- A message sent without approval.

## Where this sits
Layer 3 under `ns-lead-gen-outbound`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
