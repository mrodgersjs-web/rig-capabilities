---
name: strategy-document
description: "Pillar skill of business-strategy-os: write the five-section strategy document and the strategy argument inside it. Sections: context (with the customer-named category), the strategy argument (status quo, why it sucks, unique belief, what we do, the value), how we must change, the strategy statement, and execution as delivery plus communication (CLAIM(y1-5nxulR68)). Written longhand as a story with the business as hero, owned by one person, tested on someone who does not care (CLAIM(LeBAj6jRyk4), CLAIM(TjEwEUWtwbk)). Load when the strategy is named but undocumented, or when a document exists and changes nothing."
tags: [rig, doctrine, business-strategy, writing, strategy-document]
metadata:
  source: "Alex M H Smith corpus; claims resolve in data/corpora/strategy/manifest.jsonl"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-document: a longhand strategy document whose five sections are all present, whose only-statement and trade-offs survive the fiercest-competitor test, and whose execution names delivery and communication actions an outsider could see in the business"
activation: "Load when a strategy is named but not written down, when a document exists but the business has not changed because of it, or when a team cannot answer 'what is our strategy' consistently."
instruction: "Write it as a story with the business as hero, longhand, not a deck. If you cannot list what the business will stop doing, you have validation of the status quo, not a strategy. Deliver and communicate are the whole business; the strategy does not exist until an outsider can see it just by looking at what you do."
applies_when:
  env: "one business with a named new value, innovation and only-statement from strategy-innovation"
  runtime: "python3 stdlib; strategy_lint.py and rig-s1gate for the gates"
  deps: "corpus at data/corpora/strategy; no other network dependency"
  params: "one business; one decision-maker; the category and the competitive set already named"
  budget: "one working session per draft; a Jev check a fraction of a cent"
  scale: "one business or client engagement"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
  - gate-d-required:send
flow:
  - "Write section one, context: what the business is, its situation, and crucially the category the way a customer shops for it, since the category sets the status quo you push against."
  - "Write the strategy argument as a narrative: the status quo of the category, why it sucks, your unique belief nobody else holds, what you do about it, and the value the customer gains that they lack."
  - "Write how we must change: the things the business does today that do not fit the strategy and will stop; if none exist, the document is a description of the status quo."
  - "Write the strategy statement (the only-statement in one line) and the execution: delivery (operations, product, distribution) plus communication (branding, marketing, sales script), each with bullet actions."
  - "Gate it: strategy_lint.py then rig-s1gate check strategy.output; hand any outward version to Gate-D."
done_when:
  - "grep:capabilities/skills/strategy-document/SKILL.md:## The five sections"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-document/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-document/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.75
out_of_scope:
  - "finding the value or the innovation (strategy-new-value, strategy-innovation)"
  - "sending the document to anyone (Gate-D)"
---

# strategy-document

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through
> the meta-skill. Send every typed judgment it forces (whether this document is a strategy rather than a goal, whether it is a how, and whether it names trade-offs) to `rig-s1gate` BEFORE any
> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is
> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage
> advance.**



## Why write it at all

Three reasons, in the corpus's order: to get clear on the unique value offered to the customer, since that is what people pay for and where margin comes from; to give everyone inside one focus instead of throwing things at the wall; and to lay out an exciting mission rather than meandering toward 10-15% growth CLAIM(y1-5nxulR68, eR9xNJiuTQ4). Most businesses have no strategy document at all.

## The five sections

1. **Context.** What the business is, what it does, its situation, and the category it plays in, written the way a customer names it. The category sets the status quo you will push against and the frame the customer judges you in. The category is not what you think; it is what the customer is shopping for and comparing you to (an online course is not an "online education" category; it is singing lessons) CLAIM(y1-5nxulR68).
2. **The strategy argument.** A narrative with four beats: the status quo of the category and what it gives customers; why that sucks, because if you are entering a category the only reason is that you think something is wrong with it; your unique belief, the unusual point of view on how the category works that nobody else holds; what the business will do about it; and the value the customer gains that they do not have now. Tesla's early argument, as told in the corpus, runs exactly this shape CLAIM(y1-5nxulR68).
3. **How we must change.** The things the business does today that do not fit the strategy and will stop. Most strategies fail here: they are written to validate decisions already made rather than to force change. If you cannot write down what you are doing now that does not fit, you have written up the status quo CLAIM(y1-5nxulR68).
4. **The strategy statement.** One line: we are the only X who Y, so customers get Z. See strategy-innovation for the test it must pass.
5. **Execution.** Delivery (what the business physically does: product, production, distribution) plus communication (how the customer hears about it: branding, marketing, pitch, sales script). Together these are basically the whole business; everything else is admin. Each carries bullet actions, and the strategy is only truly followed when those actions are executed CLAIM(y1-5nxulR68).

## The form: a story, one owner

- Write it longhand as an essay, not a diagram or an onion. Strategy is a narrative with the business as the hero: where it came from, what it will do, where it is going. In that form a team, an investor, anyone can read it in their own time and understand their role in it CLAIM(y1-5nxulR68).
- One point of view owns it. Collaborative, consensus strategy validates the status quo and produces boring thinking; a risky point of view can only come from one person, usually the founder, and the team wants a strong preset vision more than a say. "Nobody ever built a statue of a committee" CLAIM(TjEwEUWtwbk). Decide, then tell the team; do not workshop the strategy CLAIM(dt9wpjlT-zA).
- Test it on someone who does not care: a spouse, a friend, a stranger. If the strategy is unclear, boring, senseless or complicated, they will show it; their ignorance is the feature CLAIM(LeBAj6jRyk4).
- It does not exist until it is externally visible. Until a customer, investor or partner can see the strategy just by looking at the business, the paper does not count; Patagonia, Red Bull, Nike and Apple are named because their strategies are vivid from outside CLAIM(y1-5nxulR68).

## Traps

- Writing it to validate past decisions instead of forcing a change (the third section is where this shows).
- Technical, MBAs-on-jargon prose: the classical treatment bloated and confused; the plain story is the point CLAIM(ElaWyEeHS1w, TjEwEUWtwbk).
- A strategy that is invisible outside; an internal document that changes no action.
- Letting the committee average the point of view back to the status quo CLAIM(TjEwEUWtwbk).
