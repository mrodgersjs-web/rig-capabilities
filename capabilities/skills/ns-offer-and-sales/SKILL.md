---
name: "ns-offer-and-sales"
description: "Turn a qualified conversation into a priced, scoped first project that is built to become a retainer. Nick Saraev method. Use for: price this; write the proposal; structure the offer; prep the sales call; convert to retainer; what niche; they want a discount."
tier: main
owner: rig-intelligence
status: draft
acl: internal
verified_on: 2026-10-21
outcome: "Turn a qualified conversation into a priced, scoped first project that is built to become a retainer."
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

# ns-offer-and-sales

Turn a qualified conversation into a priced, scoped first project that is built to become a retainer.

**Use when:** price this; write the proposal; structure the offer; prep the sales call; convert to retainer; what niche; they want a discount.

## Laws
- Charge more the closer the work is to revenue; buyers fund revenue-side systems more readily than savings. CLAIM(T5-RXi-Zk_g@1m)
- Pitch outcomes, not models or specs; buyers pay to remove a problem and a risk. CLAIM(Fw8NGGnEchs@0m) CLAIM(Y54kp53gi_M@2m)
- Sell relief for the single tightest constraint and price against it. CLAIM(Gz8tbgZTdpI@4m) CLAIM(OLwEtOEF36A@29m)
- Price as a share of impact, not hours; hourly billing punishes efficiency. CLAIM(owdN96DwdT4@7m) CLAIM(NsQWWnu7vzI@6m) CLAIM(Y54kp53gi_M@15m)
- Make the first project fast and low-risk, and pick one that naturally creates the next need. CLAIM(ArNmQRpctIc@3m) CLAIM(eLqveVYFWc4@10m) CLAIM(RmYTguzXrVM@9m)
- Recurring revenue beats one-off revenue. CLAIM(T5-RXi-Zk_g@4m) CLAIM(RmYTguzXrVM@4m) CLAIM(kChb6HrYOeE@2m)
- Sell rigid deterministic systems, not all-in-one agents that try to run a whole operation. CLAIM(whXs1RaQIDA@26m) CLAIM(cZuvJxmjdxU@12m)
- Fix success criteria up front and keep client input to one intake; that is the defense against scope creep. CLAIM(ArNmQRpctIc@9m) CLAIM(hRBL6ISvB3s@29m)

## Procedure: Call to retainer
1. Ask why the prospect replied, then have them walk through the process to find the bottleneck. CLAIM(PRxtWdI3xvA@16m) CLAIM(PRxtWdI3xvA@17m)
2. Put a number on the cost of doing nothing. CLAIM(rQcXmY6rSVY@37m) CLAIM(ite9u07MhsM@7m)
3. Present the fix as recovering that amount. CLAIM(QTWBgFLuNvY@5m)
4. State the long-term partnership intent on the call. CLAIM(RmYTguzXrVM@7m)
5. Send the proposal within the hour; during delivery send updates every one to two days. CLAIM(RmYTguzXrVM@11m)

## Sub-skills (load one at a time)
- `ns-niche-and-offer`: Pick the niche and design a first project with a built-in path to the next service.
- `ns-value-pricing`: Turn a quantified impact into a fee. This sub-skill is the only owner of pricing in the family.
- `ns-sales-call-and-proposal`: Run discovery that finds the bottleneck, prices inaction, and sends a fast proposal.
- `ns-retainer-conversion`: Move a one-off client to recurring revenue through onboarding, proactive updates and the next service.

## Done-test (fails if any is true)
- The proposal has no cost-of-inaction number.
- The fee cannot be traced to that number by a stated percentage band.
- The proposal does not name the follow-on service.
- Success criteria are not written.
- The deal is marked closed before money arrives.
- A price or proposal is sent without Mike approving the exact text.

## Does not fit RIG
- Lead-count guarantees: for fractional CAIO work guarantee a proof obligation (a passing eval, a governance packet, a named metric) instead.
- The low-price ramp of starting cheap and raising per client: a commodity price-discovery play. CAIO work starts at a value-priced diagnostic.
- Avoiding regulated niches. For RIG this flips: compliance friction is where governed builds earn their fee.
- Hourly as a pricing rung.

## Deeper doctrine
`references/doctrine.md` holds the full stage doctrine: core laws marked consensus or single-source, procedures, decision rules, failure modes and changed views, all cited. Malformed tags from distillation were removed by the tag validator.

## Where this sits
Layer 2 under `nick-saraev-os`. Front door: `nick-saraev-os`. Doctrine and citations: `ns-*` references; every law cites a video id and minute from the Nick Saraev corpus. Outward actions (sending, publishing, pricing a real client) stay under RIG's approval rules; this skill never sends.
