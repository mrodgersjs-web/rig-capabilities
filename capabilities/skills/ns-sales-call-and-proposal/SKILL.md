---
name: "ns-sales-call-and-proposal"
description: "Run discovery that finds the bottleneck, prices inaction, and sends a fast proposal. Sub-skill of ns-offer-and-sales (Nick Saraev method)."
tier: sub
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Run discovery that finds the bottleneck, prices inaction, and sends a fast proposal."
done_when:
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/nick-saraev-os/scripts/check_family.py --plant
quality_floor: 0.6
metadata:
  corpus: "Nick Saraev YouTube (@nicksaraev), 349 of 350 uploads transcribed 2026-10-21"
  recall_build_card: "https://app.recall.it/item/3e0eb98f-d8de-4c40-a8ce-548b55640a50"
  parent: ns-offer-and-sales
---

# ns-sales-call-and-proposal

Run discovery that finds the bottleneck, prices inaction, and sends a fast proposal.

## Steps
1. Open with why they replied.
2. Walk the process; find the one constraint.
3. Price the cost of inaction.
4. Send the proposal within an hour (target 30 minutes).

## Laws
- Discovery is about the customer journey and its bottleneck. CLAIM(PRxtWdI3xvA@17m) CLAIM(QTWBgFLuNvY@5m)
- Quantify the cost of doing nothing. CLAIM(rQcXmY6rSVY@37m) CLAIM(ite9u07MhsM@7m)
- Talk outcomes, not technology. CLAIM(Fw8NGGnEchs@0m)

## Done-test (fails if any is true)
- The call notes have no cost-of-inaction number.
- The proposal went out more than 60 minutes after the call with no reason logged.

## Where this sits
Layer 3 under `ns-offer-and-sales`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
