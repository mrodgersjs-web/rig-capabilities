---
name: "web-conversion-copy-proof"
description: "Build the evidence that makes a page believable - rank and place
outcome: "A ranked and attributed proof stack placed against the claims it
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-conversion-copy-proof/SKILL.md
  - observable: every proof element is attributed and evidenced, and nothing unattributed appears on the page
  - observable: the first proof element sits within one screen height of the hero claim it supports
  - observable: three testimonials are shown, each under 30 words and each containing a before-state, an after-state and a reason, with name, role, company and a face
  - observable: the case study headline carries exactly one number and one timeframe and the body follows the five-part structure
  - observable: pricing tiers are named for who is buying, the comparison table sits below the cards, and the top three objections are answered inline beside the CTA
great_example: examples/great/design-ux/web-conversion-copy-proof.md
quality_floor: "Every proof element is attributed and evidenced with nothing
activation: "A page has claims with nothing behind them, or it is
instruction: "Rank every proof element by strength and use the highest rung you
applies_when:
  env: "macOS or Linux workstation with the page template, the customer evidence and the offer definition available locally"
  runtime: "any marketing, product or pricing page rendered as HTML, or a CMS entry producing one"
  deps: "named customer evidence (results, quotes with attribution, permission to show logos) and the sales call record of real objections"
  params: "3 testimonials shown and up to 7 held; each quote under 30 words on the page; one number and one timeframe per case study headline"
  budget: "one page per pass, plus the time to collect real attribution and permission"
  scale: "one page at a time, up to 12 proof elements, 3 pricing tiers"
permissions:
  - Read the customer evidence file, sales call notes, pricing definition and the page copy deck
  - Write proof and pricing copy into the project's copy file or CMS entry
  - Read public review and directory pages to collect existing third-party evidence
  - Bash for word counts and quote-length checks only
  - Outward, deploy, paid or public actions (publishing a customer name or logo, contacting a customer for a quote, changing a public price) need Gate-D
flow:
  - Inventory every proof element available and rank them strongest first - measured result with a number and timeframe, named customer result,
  - Choose the highest rung you can genuinely evidence and drop anything you cannot attribute or prove
  - Place the first proof element within one screen height of the hero claim it backs, and give each feature claim its own supporting evidence within one screen height
  - Write each testimonial with a before-state, an after-state and a reason, under 30 words, with name, role, company and a face
  - Write the case study as situation, decision, mechanism, result, next step with one number and one timeframe in the headline
  - Structure the pricing page - tiers named for who buys, the tier you want to sell marked and placed in the middle, what is NOT included stated per
  - Rank the real objections by frequency from the sales record and answer the top three inline beside the CTA, each leading with the concession, with
out_of_scope:
  - Claiming any proof element or pricing structure converts better without a controlled test (Gate-D and Mike decide on testing)
  - Publishing a customer name, quote, logo or result without written permission (Gate-D, Mike approves)
  - Price setting and discount strategy, which are commercial decisions not page structure
  - The hero block itself (see web-conversion-copy-hero)
  - Fabricating a testimonial, a result, a logo relationship or a counter in any form
---
# Web Conversion Copy Proof

Proof is not a section at the bottom of a page. It is the answer to the doubt that forms at
the exact moment the claim is made, so it has to sit next to the claim.

**Standing rule for this skill family.** Every claim about what converts is UNVERIFIED unless
the corpus states it AND the corpus frames it as a recommendation. A creator's opinion is
never presented here as a measured outcome.

## Method

### 1. The proof ladder, strongest first

| rank | proof type | what makes it strong |
|---|---|---|
| 1 | measured result, with a number and a timeframe | checkable and specific |
| 2 | named customer result (who, what changed) | concrete and attributable |
| 3 | attributed quote with name, role, company and a face | a real person stands behind it |
| 4 | unattributed quote | weak, and often counterproductive |
| 5 | logo farm | borrowed recognition only |
| 6 | badges and counters | ambient, and easy to fake |

Climb as high as you can genuinely evidence and drop everything below the rung you landed on.
An unattributed quote is worse than no quote: it invites the reader to assume it was invented.

### 2. Placement answers the doubt while it is live

The first proof element goes within one screen height of the hero claim it supports. Each
feature claim gets its own supporting evidence within one screen height of that claim.

Proof filed at the bottom of the page is answering a question the reader stopped asking at
scroll 30%. That is the single most common failure in this skill and it costs nothing to fix
other than ordering.

### 3. Testimonial anatomy, and the cut

A usable quote has three parts: **before-state**, **after-state**, and **the reason** it
changed. "We used to spend four days on close. Now it is one, because the exceptions come to
us pre-flagged." Then attach a name, a role, a company and a face.

Numbers to hold: show 3 and hold up to 7 behind a link. One is an anecdote, seven on the page
is a wall. Keep each on-page quote under 30 words. Cut rather than pad: two quotes that were
pure praise with no before-state were dropped in the worked example rather than trimmed into
decoration.

### 4. Case study structure

Five parts, in order, one page each.

1. **Situation** - who they are and the number that hurt ("four-day close at 300 invoices a month").
2. **Decision** - why you, and what they rejected and why. This is what makes it a story rather
   than a promotion, because a real buyer knows there was a shortlist.
3. **Mechanism** - what you actually did. Concrete enough that a competitor reading it could not
   claim the same thing cheaply.
4. **Result** - the number and the timeframe. Exactly one number and one timeframe in the headline.
5. **Next step** - the action for the reader, matching the page's primary action.

The headline carries the one number: "Four days to one: how Corley Foods cut close by 78% in
one quarter."

### 5. Logo farms have rules

Grayscale, equal optical size (equal bounding boxes make small logos look lost), one row of
5 to 8, and only logos you have permission to show. A logo the visitor does not recognise is
worth less than a named quote from a company they do. Where the recognisable logo is the whole
point, pair each logo with a one-line result.

### 6. Pricing page structure

- **Name tiers for who is buying**, not for what is included. "Solo operator", "Finance team",
  "Multi-entity". Feature-count names make the reader do the segmenting work you should have done.
- **Three tiers, with the one you want to sell in the middle** and marked ("most chosen"). The
  anchor does its work only when the target sits beside two reference points.
- **State what is NOT included** per tier. This is what stops the mid-tier buyer from buying down.
- **Put the full comparison table below the cards**, not inside them. Cards decide, the table
  confirms.
- **State the unit and the renewal.** "Per seat per month, billed annually, renews at the same
  rate." Silence on renewal reads as a trap.

UNVERIFIED - that three tiers beats two or four, or that a marked middle tier lifts revenue.
These are recommendations and the corpus reports no pricing-page experiments.

### 7. Objection handling goes beside the button

Take the real objections from sales calls and lost-deal notes, count them by frequency, and
answer the **top three** inline next to the CTA. Not in a footer FAQ, not in a chatbot.

Each answer opens with the concession, then the mechanism: "Yes, it costs more than a template.
It costs more because a person reads your ledger schema and writes the matching rules." Leading
with the concession is what makes the rest believable.

Put the risk reversal (guarantee, trial, exit clause) with the CTA, not in the footer. It is
part of the ask.

## Corpus evidence

designcourse / Can GPT-5 One-Shot 4 DIFFICULT Apps in Cursor? / 0IJmQdWmyT0 / [04:23] / "testimonial section underneath the hero"
paige-brunton / How You're Going To Make $100k/Month Online Without Social Media / UN3ZF49bsKY / [02:32] / "social proof and leads which come from"
paige-brunton / How You're Going To Make $100k/Month Online Without Social Media / UN3ZF49bsKY / [29:10] / "case studies on successful projects"
paige-brunton / How To Pick Website Layouts 101 / S1GSwta-wIk / [09:58] / "Or your rave testimonials from"
self-made-web-designer / How to Overcome Client Objections as a Freelancer and Win More Projects / dXfMivmLUCE / [13:50] / "clients who have less objections"
self-made-web-designer / How to Overcome Client Objections as a Freelancer and Win More Projects / dXfMivmLUCE / [14:39] / "When a client raises an objection, come up with a solution to help them solve"

**Corpus coverage is real on placement and thin on outcomes.** The corpus supports a
testimonial section sitting underneath the hero, which is exactly the placement rule in step 2,
and it names social proof, case studies and testimonials as the material. On objections it
supports two moves: choose clients with fewer objections, and answer an objection with a
solution to the client's problem. It reports no conversion measurement for any of it.

UNVERIFIED against this corpus - the six-rank proof ladder and its ordering, the one-screen-height
placement rule beyond the single corroborating quote, the before/after/reason testimonial anatomy
and the 3-show 7-hold and 30-word numbers, the five-part case study structure and its one-number
rule, all six pricing-page rules including three tiers and the marked middle tier, and the
top-three-inline objection rule and the lead-with-the-concession technique. Per the standing
rule, none is presented as a measured outcome. All caption tracks in the corpus are automatic,
so no figure quoted from one is treated as verified.

## Anti-patterns

- Orphan quote: a testimonial with no name, role, company or face, which reads as invented.
- Bottom-of-page proof: evidence filed where the doubt has already stopped forming.
- Anonymous logo wall: borrowed recognition with no result attached to any name.
- Feature-count pricing: tiers named for what is included rather than for who is buying.
- FAQ burial: the three real objections answered where nobody scrolls, beside nothing.

## Links

- parent: when-designing-websites
- parent: web-conversion-copy
- children: none (leaf skill)

## description (full text)

"Build the evidence that makes a page believable - rank and place social proof and testimonials, structure a case study around one number, structure a pricing page for who is buying, and answer the top objections beside the CTA. Use when adding testimonials, logos, case studies, a pricing page or objection handling to any web page."

## outcome (full text)

"A ranked and attributed proof stack placed against the claims it supports, a five-part case study headlined by one number and one timeframe, a three-tier pricing page named for who buys with the comparison table below the cards, and the top three real objections answered in the buyer's words beside the call to action."

## quality_floor (full text)

"Every proof element is attributed and evidenced with nothing unattributed on the page, the first proof sits within one screen height of the claim it backs, pricing tiers are named for who buys, and the top three objections are answered inline beside the CTA. A fabricated testimonial, result or logo relationship fails the job outright."

## instruction (full text)

"Rank every proof element by strength and use the highest rung you can actually evidence, with a measured result and a timeframe above an attributed quote and an attributed quote above a logo. Place the first proof element within one screen height of the hero claim it supports, because proof at the bottom of the page answers a doubt the reader has already stopped having. Structure a case study as situation, decision, mechanism, result and next step with one number and a timeframe in its headline. Name pricing tiers for who is buying rather than what is included, and answer the top three real objections inline beside the call to action, each leading with the concession."

## description (full text)

"Build the evidence that makes a page believable - rank and place social proof and testimonials, structure a case study around one number, structure a pricing page for who is buying, and

## outcome (full text)

"A ranked and attributed proof stack placed against the claims it supports, a five-part case study headlined by one number and one timeframe, a three-tier pricing page named for who buys

## quality_floor (full text)

"Every proof element is attributed and evidenced with nothing unattributed on the page, the first proof sits within one screen height of the claim it backs, pricing tiers are named for who

## activation (full text)

"A page has claims with nothing behind them, or it is collecting testimonials, logos, case studies or pricing tiers and nobody has decided what each proof element is for or where it goes."

## instruction (full text)

"Rank every proof element by strength and use the highest rung you can actually evidence, with a measured result and a timeframe above an attributed quote and an attributed quote above a

## description (full text)

"Build the evidence that makes a page believable - rank and place social proof and testimonials, structure a case study around one number, structure a pricing

## outcome (full text)

"A ranked and attributed proof stack placed against the claims it supports, a five-part case study headlined by one number and one timeframe, a three-tier

## quality_floor (full text)

"Every proof element is attributed and evidenced with nothing unattributed on the page, the first proof sits within one screen height of the claim it backs

## activation (full text)

"A page has claims with nothing behind them, or it is collecting testimonials, logos, case studies or pricing tiers and nobody has decided what each proof

## instruction (full text)

"Rank every proof element by strength and use the highest rung you can actually evidence, with a measured result and a timeframe above an attributed quote and

## description (full text)

"Build the evidence that makes a page believable - rank and place social proof and testimonials, structure a case study around

## outcome (full text)

"A ranked and attributed proof stack placed against the claims it supports, a five-part case study headlined by one number and

## quality_floor (full text)

"Every proof element is attributed and evidenced with nothing unattributed on the page, the first proof sits within one screen

## activation (full text)

"A page has claims with nothing behind them, or it is collecting testimonials, logos, case studies or pricing tiers and nobody

## instruction (full text)

"Rank every proof element by strength and use the highest rung you can actually evidence, with a measured result and a timeframe

## description (full text)

"Build the evidence that makes a page believable - rank and place social proof and testimonials

## outcome (full text)

"A ranked and attributed proof stack placed against the claims it supports, a five-part case study

## quality_floor (full text)

"Every proof element is attributed and evidenced with nothing unattributed on the page, the first

## activation (full text)

"A page has claims with nothing behind them, or it is collecting testimonials, logos, case studies

## instruction (full text)

"Rank every proof element by strength and use the highest rung you can actually evidence, with a

## description (full text)

"Build the evidence that makes a page believable - rank and place social proof

## outcome (full text)

"A ranked and attributed proof stack placed against the claims it supports, a

## quality_floor (full text)

"Every proof element is attributed and evidenced with nothing unattributed on

## activation (full text)

"A page has claims with nothing behind them, or it is collecting testimonials

## instruction (full text)

"Rank every proof element by strength and use the highest rung you can actually

## description (full text)

"Build the evidence that makes a page believable - rank and place social

## outcome (full text)

"A ranked and attributed proof stack placed against the claims it supports

## quality_floor (full text)

"Every proof element is attributed and evidenced with nothing unattributed

## activation (full text)

"A page has claims with nothing behind them, or it is collecting

## instruction (full text)

"Rank every proof element by strength and use the highest rung you can

## Contract detail (full text)

- Outward, deploy, paid or public actions (publishing a customer name or logo, contacting a customer for a quote, changing a public price) need Gate-D approval from Mike before they run
- Inventory every proof element available and rank them strongest first - measured result with a number and timeframe, named customer result, attributed quote with role and company, unattributed quote, logo, badge or counter
- Structure the pricing page - tiers named for who buys, the tier you want to sell marked and placed in the middle, what is NOT included stated per tier, the full comparison table below the cards, the unit and the renewal stated
- Rank the real objections by frequency from the sales record and answer the top three inline beside the CTA, each leading with the concession, with the risk reversal next to the button
