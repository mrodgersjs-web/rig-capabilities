---
name: traject-gtm-pricing-offer
description: "Traject GTM stage: offer and pricing design for the Traject room passes - Room Pass vs Active Search vs Coach seats, anchoring against real coaching-market benchmarks, risk reversal, the Offer Doc, and the pricing-page fixes. Use when setting, defending, or changing any Traject price or package."
tags: [rig, gtm, pricing, offer, packaging, traject]
metadata:
  tier: sub
  purpose: stage-skill
  category: gtm-sales-revenue
  family: traject-gtm
  built: "2026-09-28"
outcome: "A pricing recommendation that names its benchmark source and labels what is unverified, an offer doc in Taki's shape, a risk-reversal clause written for zero-customer reality, and a prioritized pricing-page friction list with one concrete fix per finding."
activation: "Load from traject-gtm when the stage is PRICING-OFFER, or when any Traject price, package, guarantee, bundle, or pricing-page element is proposed or audited."
instruction: "Anchor every price to a sourced benchmark and mark willingness-to-pay as UNVERIFIED until paid. Design the offer ladder before touching copy. Risk reversal must be specific (duration, condition, who pays) and must not promise an outcome. Route pricing verdicts to rig-s1gate; hold publication at Gate-D."
applies_when:
  env: "draft/audit only"
  runtime: "Stripe products in code: room_pass $49 one-time, active_search $49/month, coach (3 seats + overage)"
  deps: "gtm-pricing-page-auditor; pmm-productized-service-offers; taki-doctrine (Offer Doc, MicroMagnet); content-cta-optimizer"
  params: "tier, segment (candidate B2C, coach B2B2C), currency USD"
  budget: "one ladder, one price test at a time"
  scale: "3 products maximum at launch"
permissions:
  - fs.read
  - fs.write
  - net.read
  - gate-d-required:publish
  - gate-d-required:price-change
  - gate-d-required:spend
flow:
  - Route through traject-gtm first; JEV-first paragraph applies.
  - Inventory the benchmark market (coaching sessions, AI mock tools) with sources and dates.
  - Build the offer ladder in Offer Doc shape: who, problem, mechanism, deliverable, price, proof, risk reversal, one CTA.
  - Recommend the price and name what is unverified (WTP, conversion).
  - Run the pricing-page auditor checklist and write one fix per finding.
done_when:
  - "cmd:bash capabilities/skills/traject-gtm/scripts/verify_paths.sh"
  - "Every price claim carries a source and date or is explicitly labelled UNVERIFIED"
  - "Risk reversal names duration, condition and who pays; no outcome promise"
  - "Pricing-page findings each carry evidence and one concrete fix"
  - "No price is changed on any platform by this skill"
---

# traject-gtm-pricing-offer

## JEV FIRST
Pricing and offer verdicts (is this price defensible, does this package pass review, is this claim
admissible) go to `/Users/rig128gb/.rig/bin/rig-s1gate check <rubric> --file <abs path> --subject
<kind> --json` BEFORE any frontier LLM call, decision id recorded. Fail closed: classifier down =
DEFERRED. An advisory PASS is never permission to publish a price or change a Stripe product; that is
Gate-D and it is a spend-affecting change whose exact values must be shown to Mike in the same turn.

## Benchmark set (sourced 2026-09-28, cite in any pricing argument)
- Human interview coaching: roughly $100-300 per session; executive packages $500 to the thousands
  (igotanoffer.com 2026 roundup; hackingthecaseinterview.com 2026; loopcv.pro 2026-07-11).
- Find My Profession $299 per 90-minute session; Hello Interview $189 general / $298
  company-specific per session (igotanoffer.com roundup).
- AI interview-prep SaaS: Big Interview $39/month, $99/3 months, $299 lifetime; InterviewCoach.ai
  from $9.99/month; DataInterview $30-60/month billed annually (vendor pricing pages, 2026).
- What no benchmark gives you: what a senior candidate will pay for a per-company room. That is
  UNVERIFIED until Traject has buyers.

## Recommendation (from the GTM package)
Hold **$49 one-time Room Pass** at launch. It sits under one coaching session by 2-6x and under the
$299 lifetime AI tier, while owning a slot no subscription tool claims: one company, one role, one
room built from the posting. Do not discount pre-revenue; a low price set by anxiety is the hardest
thing to raise later. `active_search` $49/month is the anchor that makes the one-time pass read as a
bargain. Coach (3 seats + overage) is priced and held until B2B2C demand is observed.

## Offer Doc shape (Taki)
Who it is for / the problem in their words / the mechanism (the four moves) / exactly what they get
(the room: ownership map, regulation reality, numbers to prove, restraint story, ruin + recall
drills) / price and what is included / proof (the mechanism and the artifact - never a fabricated
customer result) / risk reversal / one CTA.

## Risk reversal for a zero-customer product
Specific and cheap to honor: "If the room does not clearly beat your own prep notes within 7 days of
buying, email us and we refund in full - you keep the room." Duration, condition, who pays, all
named. It never says "you will get the offer", because no customer has and none may be implied.

## Pricing-page audit (the canonical finding set)
Run gtm-pricing-page-auditor's checklist: anchoring, tier self-selection in 30 seconds, risk reversal
specificity, trust near the CTA, FAQ/objection handling, and CTA clarity (login vs buy conflation).
Each finding in the GTM package carries evidence and one fix.

## MicroMagnet (Taki)
The free magnet for Traject is one sample room for one real public job posting - one person, one
problem, delivered before the ask. It is the only "free" thing that demonstrates the mechanism
without requiring a customer testimonial.
