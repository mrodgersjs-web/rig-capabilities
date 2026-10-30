---
name: strategy-marketing
description: "Pillar skill of business-strategy-os: why marketing stopped working and what to do instead. The rule that when something is abundant it loses value (CLAIM(JZVmL99ClfA)), marketing presents value rather than creating demand (CLAIM(qxdY2kdKz9g)), the marketability check before spending (good marketing versus marketable), and the three moves that make marketing hard again: make it unfair, make it tedious and expensive, replace rather than add (CLAIM(JZVmL99ClfA)). Includes the institutional-credibility and trust-retreat dynamic. Load when marketing spend is not converting or the plan is more content."
tags: [rig, doctrine, business-strategy, marketing]
metadata:
  source: "Alex M H Smith corpus (CLAIM(JZVmL99ClfA), CLAIM(qxdY2kdKz9g), CLAIM(XPhxUrUPO-A)); peer: Jeremy Haynes offer-and-swarm content (CLAIM(JfdmFP8x1qY)), Hormozi offer-first (CLAIM(4GjwtnA76ig))"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-marketing: a marketing plan whose every element passes the stuff-to-attention and 10x-cost tests, built on an already-marketable offer, that makes the marketing hard, unfair, tedious or replacement rather than additive"
activation: "Load when marketing spend is not converting, when the plan is more content or a new channel, when the offer is being compared, or when AI has made the category's output interchangeable."
instruction: "Marketing presents an iceberg; it does not create the ice. Before spending, prove the offer is marketable: what unique value, can others deliver it, does anyone want it. Then make the marketing hard: scarcity over quality, unfair and tedious over easy, replace rather than add. If a tactic would be dropped at ten times its cost, kill it."
applies_when:
  env: "one business with a marketable offer and a known customer problem"
  runtime: "python3 stdlib; Jev for verdict checks; no ad spend, no publishing"
  deps: "corpus at data/corpora/strategy; no other network dependency"
  params: "the channel and its supply-to-attention ratio; the 10x-cost answer for each element"
  budget: "one session; Jev checks a fraction of a cent"
  scale: "one business or client offer; not a media-buying or ad-operations role"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
flow:
  - "Prove marketability first (unique value, exclusivity, demand); if it fails, route to strategy-new-value, not to a campaign."
  - "Run the stuff-to-attention ratio on the channel; do not diagnose it as 'the algorithm changed'."
  - "Apply the three moves: make it unfair, make it tedious and expensive, replace rather than add."
  - "Run the 10x-cost test on every element and the uncopyable-advantage inventory; keep low-volume posts as practice, not as the engine."
  - "Return the plan to strategy-document for execution, and any outward asset to Gate-D."
done_when:
  - "grep:capabilities/skills/strategy-marketing/SKILL.md:## The three moves"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-marketing/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-marketing/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.75
out_of_scope:
  - "creating demand or changing the offer (strategy-new-value)"
  - "spending, posting or publishing (Gate-D)"
---

# strategy-marketing

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through
> the meta-skill. Send every typed judgment it forces (whether the offer is marketable, whether this element is hard enough, and whether we would still do it at ten times the cost) to `rig-s1gate` BEFORE any
> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is
> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage
> advance.**



## The rule

When something is abundant, it loses value; goodness is only a function of scarcity. Every channel is on the wrong side of the ratio of stuff to attention, and once consciousness is full, a good product stops mattering; overwhelming choice makes people choose less, not more CLAIM(JZVmL99ClfA). AI did not start the flood, it finished a twenty-year war on friction, channel by channel in order of how easily the machine could do the work: text first, then feeds, then higher-production channels.

## Marketing presents; it does not create

Marketing is the tip of the iceberg: branding, positioning and messaging show off and frame a thing that already exists, and they matter and can make a huge difference, but they are limited. The pressure "get us some customers" is the wrong assignment for marketing. Ask the three questions: what unique value do you deliver, can people get it from someone else, does anybody actually want it; if the answer fails any of them, the money is already wasted and no agency or budget fixes it CLAIM(qxdY2kdKz9g). Point at the mechanism, not the claim: flatpack unlocked IKEA's low prices, the handle on the back of the iMac made it feel friendly CLAIM(qxdY2kdKz9g).

## The three moves

1. **Make it unfair.** Whatever you do, a motivated competitor can copy it; what they cannot copy at once is your unfair advantage: your speaking, your face on camera, a real track record, people worth interviewing, serious credentials CLAIM(JZVmL99ClfA). The Old Spice move is to retarget the real buyer and let the ad become obvious CLAIM(deXsHn7mANQ, c_AwFCghnBU).
2. **Make it tedious and expensive.** Do what most people will not bother with: original research, dozens of speaking slots, a book with a serious publisher, video that needs real crews and money, your own events. Run the 10x-cost test on every idea: would you drop this if it cost ten times more? If not, it is not hard enough CLAIM(JZVmL99ClfA, KBCFjK4ziUM).
3. **Replace, don't add.** Every channel is born, lives and dies the same way; the frontier is empty and early players win on scarcity, not quality, and then the equation flips. Add a tactic and you add supply; replace an old one or leave the ground CLAIM(JZVmL99ClfA).

## Trust has retreated to a small set

In saturation, customers do not filter harder; they retreat to a tiny closed set of trusted sources, so trust means attachment to a name already known, and institutional credibility is back for a new reason: not reach, but the only places the audience trusts the thing is not garbage CLAIM(JZVmL99ClfA). Compile the list of people you have interviewed, the titles you hold and the rooms you speak in; it is the trust list.

## Peer notes (offer-first, swarm-occupied)

- Peer (Jeremy Haynes): after a click, the feed swarms the category with competitors, so outspending no longer hides alternatives; occupy the swarm with unique-mechanism and process content or the lead arrives already comparing two to five options CLAIM(JfdmFP8x1qY). (His revenue figures are his own unverified claims.)
- Peer (Hormozi): the offer is the strongest lever, the market is chosen for pain, purchasing power, targeting and growth CLAIM(4GjwtnA76ig); treat the offer as the bridge between product and market CLAIM(pxVeOkOVr2w). His numbers are unverified.

## Traps

- Answering a failed campaign with a bigger budget, a new agency or more content; fix the marketability of the offer first CLAIM(qxdY2kdKz9g).
- Keeping low-level posting as the engine rather than as practice CLAIM(JZVmL99ClfA).
- Chasing an algorithm diagnosis when the channel is simply oversupplied CLAIM(JZVmL99ClfA).
