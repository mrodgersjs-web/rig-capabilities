---
name: strategy-stories
description: "Pillar skill of business-strategy-os: turn a strategy into the two stories that carry it. The customer story translates strategy into a customer-facing narrative where the customer is the hero and the business is Q, not James Bond (CLAIM(uAP9fPmv35U), CLAIM(ElaWyEeHS1w)); the company story is the origin-to-world narrative told to the team, investors and the trade (CLAIM(ElaWyEeHS1w), CLAIM(qZ_XP5xIpBk)). Peer: StoryBrand's problem-empathy-answer-change-end-result sound bites and the one-liner (CLAIM(C9CBjaAOuNE), CLAIM(xhOWQG45pEQ)). Load once the strategy statement is fixed."
tags: [rig, doctrine, business-strategy, messaging, storybrand]
metadata:
  source: "Alex M H Smith corpus; peer: StoryBrand (Donald Miller) and Win Without Pitching"
  extracted: "2026-09-26"
  parent: business-strategy-os
outcome: "strategy-stories: a customer story in the customer-as-hero frame that a buyer recognises as their own problem, and a company story in the origin-problem-belief-action-value-world shape that gives the team, investors and press a reason to back the strategy"
activation: "Load when the strategy is fixed and needs to be told, when messaging keeps missing, or when the team and investors cannot articulate why the business exists."
instruction: "Strategy is not your message: it is your read of the market and your instructions to yourself. Translating it into a customer story is a translation job, and the frame is the customer's, not yours: talk about them, not about how clever your strategy is. The company story is told to everyone else, including yourself, and it orients the thinking."
applies_when:
  env: "one business with a fixed strategy statement and only-statement"
  runtime: "python3 stdlib; no network beyond Jev"
  deps: "corpus at data/corpora/strategy; StoryBrand material is CC-BY material referenced, not copied"
  params: "one primary customer problem chosen for pain and scale; one audience per variant"
  budget: "one session; Jev checks a fraction of a cent"
  scale: "one business or client offer"
permissions:
  - fs.read
  - fs.write
  - bash
  - net.api-calls
  - gate-d-required:publish
flow:
  - "Customer story: ask what life looks like for the customer without this value, find several problems in its absence, and pick the primary one by pain times scale."
  - "Write it in the customer-as-hero frame: you know (the problem in their words), we (the innovation that solves it), so you (the after state); the business is Q, not James Bond."
  - "Company story: origin (why you started), the industry problem you noticed, your unique belief, what you will do, what it means for customers, and what it means for the world."
  - "Check primary-vs-secondary: lead with why you care, why you are competent, how you solve it and the customer's result; goals, history, values and 'we're better' belong later, if at all."
  - "Any outward version (site, ads, pitch) goes to Gate-D."
done_when:
  - "grep:capabilities/skills/strategy-stories/SKILL.md:## The customer story"
  - "cmd:python3 capabilities/skills/business-strategy-os/scripts/claims_check.py capabilities/skills/strategy-stories/SKILL.md"
  - "cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/strategy-stories/SKILL.md"
great_example: "examples/great/business-ops/great-strategy-document.md"
quality_floor: 0.75
out_of_scope:
  - "changing the strategy itself (strategy-document)"
  - "publishing anything (Gate-D)"
---

# strategy-stories

> **JEV FIRST.** This pillar is a task-start surface in its own right, not only through
> the meta-skill. Send every typed judgment it forces (whether the customer is the hero, and whether the primary problem is chosen by pain times scale) to `rig-s1gate` BEFORE any
> frontier LLM call; a required noul passes only above 0.9. **When the fast classifier is
> unavailable: DEFER, never guess a verdict locally, and never let an unjudged stage
> advance.**



## The customer story

Strategy is not your message, proposition or tagline; it is your read of the market and your instructions to yourself. Turning it into a message is a translation job, and the customer story is how you do it: a narrative logic you can turn into any copy, the underlying basis of every sales and marketing sentence, from website to script to bio to ad CLAIM(ElaWyEeHS1w).

- **The frame.** Most companies market as if they are the hero. Flip it: the customer is James Bond, the business is Q, a small insert that helps them over a hurdle; you are there and crucial, but you are not the crux CLAIM(uAP9fPmv35U, ElaWyEeHS1w). Talk about them, not about your business, your cleverness or your greatness.
- **The primary problem.** Ask what life looks like for the customer without this value; find several problems in its absence, not one, then pick the primary by the combination of pain and scale, broad enough to apply loosely to many customers CLAIM(ElaWyEeHS1w). (Peer: StoryBrand's sound bites are problem, empathy, answer, change, end result CLAIM(C9CBjaAOuNE); the one-liner is problem, product, result CLAIM(xhOWQG45pEQ).)
- **The shape.** You know (the problem in the customer's words), we (your innovation that fundamentally solves it), so you (the dream end state after buying). Two parts about the customer, one about you: that is roughly the right communications ratio CLAIM(ElaWyEeHS1w). Polish it, expand it into a manifesto or contract it to a tagline, but it is the only thing you keep saying.
- **Primary before secondary.** Lead with why you care, why you are competent, how you solve it and the customer's result; your goals, company history, values and competitive claims are secondary and come later, if at all CLAIM(rnwvrvWZ9CY, wYCsbGt76Z8). A story about yourself will not grow the business; inviting the customer into a story where they are the hero might CLAIM(2VidhUB66R4).

## The company story

The company story is how the strategy is told to everyone else: the team, investors, partners, the trade, the press, and most importantly yourself. It is the story you tell yourself about what the business is doing, and it orients all of your thinking CLAIM(ElaWyEeHS1w, qZ_XP5xIpBk).

- It is what set the great founders apart: not that their strategies on paper were better, but that they got people and industries behind them; a dumb strategy with a great company story might just work, so do not treat this as the least important bit CLAIM(ElaWyEeHS1w).
- **The six beats**: origin (why you started, some humanity and colour), the problem you noticed (a flaw in the industry, not only the customer's), your unique belief (the 3-D insight everything hinges on), what you will do about it (the inevitable action), what it means for customers (the new value, the commercial leverage), and what it means for the world at large (your purpose, the exciting part) CLAIM(ElaWyEeHS1w).

## Traps

- Selling your strategy instead of the customer's problem; the hero flip is the whole correction CLAIM(uAP9fPmv35U).
- Leading with the company story or secondary messaging; it is for after the customer is in the story CLAIM(rnwvrvWZ9CY, 2VidhUB66R4).
- A customer story with one thin problem; the value solves several, pick the primary by pain times scale CLAIM(ElaWyEeHS1w).
