---
name: strategy-innovation
description: "Pillar skill of business-strategy-os: turn new value into a concrete, observable innovation and the only-statement that survives a competitor. Applies the nine types of innovation (CLAIM(FF46sruCVpY), CLAIM(ElaWyEeHS1w)) - product features, production method, routes to market, service bundling, branding, targeting, customer experience, pricing, culture - enforces 'if you say you are different you must do something different' (CLAIM(FF46sruCVpY)), and builds the 'we are the only X who Y so customers get Z' statement with the fiercest-competitor test (CLAIM(kIw__JxmbUo)). Load after strategy-new-value has named the value, and before strategy-document."
tags: [rig, doctrine, business-strategy, innovation, positioning]
metadata:
  source: "Alex M H Smith corpus; peer: Win Without Pitching value-pricing rules (CLAIM(kSMVqwGEtIE)), Hormozi offer value equation (CLAIM(4GjwtnA76ig))"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-innovation: one observable innovation that delivers the new value, named as the only-statement 'we are the only X who Y, so customers get Z', which a fiercest competitor would concede in good faith and which no claimed virtue substitutes for"
activation: "Load once the new value is named, or when a business claims to be different and the claim rests on a virtue ('excellent service', 'quality') rather than a fact."
instruction: "If you want to say that you're different, you've got to do something different; claims without facts are crickets. Pick the innovation type that fits the value (most services default to product features and stay undifferentiated), make it concrete enough to put a finger on, and test the only-statement against the fiercest competitor. A claimed service without an innovation behind it is the single most common failure."
applies_when:
  env: "one business or offer with a named new value and a known competitive set"
  runtime: "python3 stdlib; strategy_lint.py for the statement check; rig-s1gate for Jev"
  deps: "corpus at data/corpora/strategy; no other network dependency"
  params: "the category X; the differentiated action Y; the customer value Z; the fiercest competitor's name"
  budget: "one session; Jev checks a fraction of a cent each"
  scale: "one business or offer"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - "Choose the innovation type: walk all nine, not just product features; the customer need not see the method but should see its benefits."
  - "Make the innovation concrete: name the physical, operational or pricing fact that a competitor could not copy tomorrow without dismantling something."
  - "Write the only-statement: 'We are the only X who Y, so customers get Z' with X the customer-named category, Y the action, Z the value."
  - "Run the fiercest-competitor test: if the fiercest competitor read it and agreed, the claim is empty; real strategy produces good-faith disagreement."
  - "Check value-first pricing: price from the value created, then test it against worst-case cost; own more of the value chain to justify a larger share (peer: Win Without Pitching)."
done_when:
  - "grep:capabilities/skills/strategy-innovation/SKILL.md:## The nine types of innovation"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-innovation/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-innovation/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.75
out_of_scope:
  - "finding the new value itself (strategy-new-value)"
  - "the full strategy document, stories and execution (strategy-document)"
---

# strategy-innovation

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through
> the meta-skill. Send every typed judgment it forces (whether this is a claimed virtue or a concrete innovation, and whether the only-statement survives a fiercest competitor) to `rig-s1gate` BEFORE any
> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is
> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage
> advance.**



## The first and only rule

If you want to say that you're different, you've got to do something different; claims without facts are crickets. The rule applies to products, services, marketing and operations CLAIM(FF46sruCVpY). A business that claims excellent service and cannot say what specifically it does to create outlier service has nothing: "they just think that claiming it or wishing it makes it so" CLAIM(ElaWyEeHS1w). Octopus Energy's answer is a real innovation, a human being answers the phone with no menu and is empowered to fix the problem, an insane, hard, practical fact you can put a finger on CLAIM(ElaWyEeHS1w, FF46sruCVpY).

## The nine types of innovation

Most people only explore product features, which is why most services stay undifferentiated CLAIM(FF46sruCVpY, ElaWyEeHS1w).
1. **Product features**: add or remove bells and whistles; low-hanging fruit for product businesses, hard for services.
2. **Production method**: how you make it, so it is cheaper, faster or more consistent (McDonald's, Method's ugly-on-purpose cleaners); the customer may not see the method but should see the benefits CLAIM(FF46sruCVpY, 2KM0FMKI2iU).
3. **Routes to market**: generic product, different delivery or context; ask where products like yours do not show up but could (ClickFunnels as an alternative to websites) CLAIM(FF46sruCVpY, c_AwFCghnBU).
4. **Service bundling**: two generic things stuck together, sold as one new thing (Peloton: existing hardware plus existing software) CLAIM(FF46sruCVpY, AnpT-o6cZZk).
5. **Branding**: normally not an innovation; only when presentation is so wild it alters the category landscape (Liquid Death inverting water's innocent aesthetic). A slightly prettier brand is a get-out-of-jail-free card CLAIM(FF46sruCVpY, EBR31-M7RbU).
6. **Targeting**: a coherent audience in the category nobody has labelled yet; cut the people so they recognise themselves, then name and serve them (Justin Welsh and solopreneurs) CLAIM(FF46sruCVpY).
7. **Customer experience**: name the hard factual innovation that creates an "insane chasm of difference"; if you cannot, you do not own the territory.
8. **Pricing**: new ways of charging (free core, inconvenient free, charge for smooth; the 10x/50x/100x anchor) CLAIM(FF46sruCVpY, yEKu6q0W3gs, ONV__y1z7MI).
9. **Culture**: new ways of handling your team; start from the perfect employee archetype and work backward CLAIM(FF46sruCVpY).

## The only-statement

Write it as one sentence: "We are the only X, the category we're playing in, who do Y, the differentiated action, so customers get Z, this particular form of value" CLAIM(kIw__JxmbUo). X is the customer-named category, not your delivery format; Y is the innovation; Z is the value they cannot get elsewhere. Tesla's early statement fits the shape: the only EV maker whose first car is a supercar, so customers get luxury, performance and status from an electric car CLAIM(y1-5nxulR68).

**The fiercest-competitor test.** Show the statement to the competitor you fear most. If they would agree "yes, you are the only one doing that", it is a sign of a beautiful strategy: they have no argument, they think it is a stupid idea and wish you well. If the statement is something your competitors could also honestly claim, it is self-deception, and the value is one the customer can get elsewhere CLAIM(kIw__JxmbUo, y1-5nxulR68).

## Value-first pricing (peer: Win Without Pitching)

- Price from the value created, then check against worst-case cost; detailed scoping is only needed when cost is close to price CLAIM(gDsm47sMp6A).
- Value price only where you can greatly impact value; when your deliverable is a small part of the value chain, clients rightly resist outcome-based pay, and to claim a larger share of results you must own more of the chain CLAIM(kSMVqwGEtIE, xBeeXwFydG8).
- Diagnose before prescribing: make diagnosis a paid, non-negotiable step; give no strategy away free CLAIM(xBeeXwFydG8, zx7qrKR6clI).
- Peer (Hormozi): the value equation is dream outcome, likelihood of achievement, speed of achievement, effort and sacrifice; price is what you pay, value is what you get, and price is the strongest under-tested profit lever CLAIM(4GjwtnA76ig, k-3PoOT4vOM, _ArQlwPvGUA, yEKu6q0W3gs). His revenue and ROAS figures are his own unverified claims.

## Traps

- Claiming a virtue (service, quality, care) with no innovation behind it.
- Reaching for product features when the value lives in method, route to market, targeting or pricing.
- Writing an only-statement your competitors would also sign.
- A branded "only" that is a category everyone uses ("the only X with guaranteed results"): the customer must be unable to get Z elsewhere, not merely see the claim CLAIM(y1-5nxulR68).
