---
name: tg-free-tier-engineering
description: >
  Sub-skill of tubeguruji-doctrine: free-tier-first stack selection and quota-as-
  product per the TubeGuruji corpus — choosing tools by free tier (Gemini free
  daily credits, Neon/Convex/Firebase free DBs, Vercel, EAS free queue), credit
  systems as monetization, and upgrade UX that makes the limit the product.
tags: [rig, doctrine, free-tier, monetization, credits, tubeguruji]
metadata:
  source: "corpus — ciXiibK7Gds (Gemini-for-free-credits criterion, Remotion free AWS), bxhDP-e4NDA (credit-per-story, PayPal top-up), egQajXL7nn4 (sidebar credit counter), saoW6BaNamc + sXRDL-EPtrM (Arcjet quotas), rdaSPdCkoFQ (paid chapters), WSKpzyixLiI (credit stacking — sponsored claims, unverified), _GyIjVgIwtk (membership boolean)"
  extracted: "2026-09-25"
  parent: tubeguruji-doctrine
  subs: [tg-quota-gates]
outcome: "A stack that runs at ~zero cash until scale, with a credit/quota monetization surface designed in from the first commit."
activation: "Load when selecting vendors for a new build, when designing the monetization surface, or when a build's costs start before its revenue."
instruction: >
  Treat "is there a free tier" as a selection criterion with equal weight to
  capability. Design the credit/quota surface into the skeleton (stage 4 and 7),
  not bolted on. Defer anything paid until the product forces it, and route every
  paid step past Gate-D.
applies_when:
  env: "greenfield or pre-revenue build; vendor free tiers available"
  runtime: "any — the criterion is vendor-agnostic"
  deps: "vendors with free tiers (Gemini AI Studio, Neon, Convex, Firebase, Supabase, Vercel, EAS, Inngest, Arcjet)"
  params: "one quota number per free action; one credit price per generation; one upgrade path"
  budget: "cash cost target zero until product-market signal; paid lines appear first in voice minutes and media APIs"
  scale: "single product, early traffic; not enterprise procurement"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - gate-d-required:purchase
flow:
  - Select each vendor by free tier first; record the criterion when it decides a choice ("Gemini API chosen explicitly because it gives free daily credits", ciXiibK7Gds; "everything we use is completely free", Dsw0pMnblWg, AIA-3OkWjAs).
  - Map the product's costly actions (generations, files, messages, expert access) to a number users can understand (3 forms, s28yOCBVgGw; 2 uploads/day, -h1O73T0jmo; 15 msgs/24h, saoW6BaNamc).
  - Implement the gate per tg-quota-gates (Arcjet bucket / DB counter / entitlement flag).
  - Give credits a visible surface: counter in the sidebar (egQajXL7nn4), free credits on join (eMplIjZ80Zs), 1 credit consumed per generation with instant UI update (lJbIs8_5aqU).
  - Wire the top-up path: Stripe checkout + webhook credits or PayPal (bxhDP-e4NDA), or Clerk billing in one line (saoW6BaNamc).
  - Tier by product surface, not by plumbing: free = general physician, members = specialists (zjwj21wzs4U); free = 3 chapters, paid = hard difficulty (rdaSPdCkoFQ, HlR15YZM7fg).
done_when:
  - "grep:capabilities/skills/tg-free-tier-engineering/SKILL.md:free daily credits"
  - "grep:capabilities/skills/tg-free-tier-engineering/SKILL.md:Clerk billing"
  - "grep:capabilities/skills/tg-free-tier-engineering/SKILL.md:WSKpzyixLiI"
out_of_scope:
  - enterprise pricing/negotiation, usage-based billing infrastructure at scale
  - claiming sponsored credit-stacking totals as verified (WSKpzyixLiI is a sponsor pitch: GCP $2,000 / AWS $5,000 claims shown in a video, not audited)
  - purchases or paid-tier upgrades without Gate-D
quality_floor: "Every costly action has an explicit quota number and an upgrade path before launch; a build whose costs begin before its gates exist is RED."
---

# Free-Tier Engineering

## Selection criterion, stated on camera

The corpus picks vendors by free tier explicitly, not implicitly:
- "Gemini API chosen explicitly because it gives free daily credits" (ciXiibK7Gds).
- "Everything is free" framing as a design constraint: free CMS, free credits, free
  hosting, free render (_GyIjVgIwtk, ciXiibK7Gds, cRlRuJhM7WQ).
- Hosted tool trade-off: even "self-host for free" loses because the cloud still
  costs — hosted Chatterbox at <$1/45min beats self-hosting (kxM_oEMn3IM).

## Quota numbers the corpus actually shipped

| App | Free limit | Mechanism |
|---|---|---|
| AI form builder | 3 forms | DB counter (s28yOCBVgGw) |
| Long-to-short video | 2 uploads/day, self-resetting | Arcjet bucket (h1O73T0jmo) |
| Multi-model chat | 15 msgs/24h | Arcjet bucket (saoW6BaNamc) |
| Trip planner | 1 itinerary/day | Arcjet bucket (sXRDL-EPtrM) |
| Eraser clone | 5 files | DB check + upgrade prompt (sxn2GPQjJgc) |
| File manager | 50 MB with live usage readout; upgrades left as homework | quota readout (zlZ_7VTfxUs) |
| Medical agent | general physician only free | entitlement tier (zjwj21wzs4U) |
| Coding platform | free vs paid chapters | entitlement flag (rdaSPdCkoFQ) |
| Gamified course app | paid-only hard difficulty | entitlement flag (HlR15YZM7fg) |

Details and implementation recipes: tg-quota-gates.

## Credits as monetization

- Free credits on join (eMplIjZ80Zs), counter visible in the sidebar (egQajXL7nn4),
  debited per generation with instant UI update (lJbIs8_5aqU: 1 credit = 1 deck).
- One credit = one story, debited before generation, buy-more via PayPal
  (bxhDP-e4NDA). Stripe checkout + webhook credit grants are the other standard
  path (O_f55bWzsik) — with the local-dev caveat: webhooks need ngrok and demo
  credits were seeded manually in the DB.
- Clerk billing as the zero-code subscription: "just one line of code" (saoW6BaNamc).
- Free vs unlimited subscription tiers on a UI generator (c9qA-uhysIY); monthly
  plan + 2-day free trial on an analytics clone (Tol6p9kYhy4).

## The sponsor-shaped claim to carry carefully

The credit-stacking video (WSKpzyixLiI) claims $10,000+ in startup credits via an
aggregator (GCP $2,000, AWS $5,000, Supabase $300…), shown in billing consoles.
That is a sponsored pitch, not audited data. The transferable idea — new-vendor
free credits can fund a build — is real; the numbers are the creator's claims.
