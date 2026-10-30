---
name: web-design-business-pricing
description: "Price web design work with a defensible model: fixed project fees, day rates for open-ended work, and retainers only after a shipped first project, with scope control and value framing."
outcome: "A defensible quote and proposal: named model, written deliverable list, anchor price with reason, value framing tied to the client's problem, and scope-control clauses."
done_when:
  - 'grep:capabilities/skills/web-design-business-pricing/SKILL.md:[R]etainer only after a shipped first project'
  - 'grep:capabilities/skills/web-design-business-pricing/SKILL.md:[F]ixed project fee scoped to a written deliverable list'
  - A written quote exists that names the pricing model, lists every deliverable the fee buys, states the out-of-scope change fee, shows the anchor price
great_example: examples/great/design-ux/web-design-business-pricing.md
quality_floor: Any price without a written deliverable list fails the job. Any quote that explains the number in hours to the client fails. Any deal that can grow scope without a written change and its own fee fails the floor.
activation: Load when quoting a project, when a client asks "what do you charge", when a proposal needs a number, when a deal stalls on price, when scope starts creeping, or when converting a project client into recurring work.
instruction: "Use three pricing models and no others: a fixed project fee scoped to a written deliverable list, a day rate for open-ended work, and a retainer only after a shipped first project. Never price on hours to the client: hours are your internal cost check only. Ask the budget question directly in discovery, quote a range first, then anchor on the top of that range with the specific reason, and price against the cost of the client's problem rather than your cost of delivery. Control scope with a written deliverable list and a written fee for every change."
applies_when:
  env: Putting a price on web design, brand-for-web, or ongoing web work for an external client
  runtime: web page or site rendered in a browser
  deps: the project brief and its design system
  params: Putting a price on web design, brand-for-web, or ongoing web work for an external client. Applies at quote, proposal, negotiation, and scope-change moments. Does not apply to emplo
  budget: one pass per artifact
  scale: single page up to a full marketing site
permissions:
  - May read proposals
  - invoices
  - competitor pricing pages
  - the local corpus at /Users/rig128gb/Developer/rig-design-studio/corpus/youtube
  - may write quotes
  - proposals
  - pricing tables
  - scope documents into the business workspace. Outward sends of proposals or invoices
  - deposits
  - purchases
  - anything that binds money need Gate-D approval from Mike
flow:
  - Ask the budget question in discovery and record the answer verbatim;
  - Choose one of the three models based on how defined the scope is;
  - Write the deliverable list the fee buys, item by item;
  - Compare against similar providers in the same business model and geography to sanity-check the band;
  - Frame value against the cost of the client's problem and their proof of outcomes;
  - Quote a range, then anchor at the top with a named reason;
  - Put the out-of-scope change fee in the same document as the price;
  - Convert to retainer only after the first project ships and the client has seen results
out_of_scope:
  - Discovery and structure work (see web-design-discovery), client delivery and revision handling (see web-design-business-client), discount approval
---
# Web Design Business Pricing

## Method

Three models, chosen by how defined the work is:

1. Fixed project fee scoped to a written deliverable list. The default for sites with a known page set. The fee buys a list of items, not a duration: "six pages, one booking integration, two revision rounds, launch support". If it is not on the list, it is not in the price.
2. Day rate for open-ended work: ongoing design support, retainer-adjacent work, discovery-heavy projects. Self-Made Web Designer's upgrade on the raw day rate is to package it as a productized service: a fixed outcome, a fixed deadline, and a fixed price rather than an open meter.
3. Retainer only after a shipped first project. Sell recurring work to someone who has already seen you deliver. Before that, a retainer is a promise with no evidence behind it. Note the vocabulary point from the corpus: hourly, daily, weekly, and monthly arrangements are the same family, with the recurring ones usually called retainers.

Never price on hours to the client. Hours tell you whether a job is worth taking; they are a terrible way to explain value, because they make the client audit your speed instead of their outcome.

Ask the budget before you quote. Self-Made Web Designer is blunt about the method: the easiest way to get the client's budget is to ask the client the budget on the discovery call, as "how much are you wanting to invest in this project". Also ask what happens if this project does not exist this year: that answer is the cost of the problem you are pricing against.

Sanity-check the band against similar providers. The corpus frames this as a market-rate comparison that is business-model agnostic: compare what you do with those who are similar to you. Two traps it names: geography moves rates (the Houston versus San Francisco example), and business model moves rates (a high-volume studio and a bespoke studio are not price competitors). Compare like with like, then decide which side of the band you sit on and why.

Value framing: price against the cost of the problem. A clinic losing calls to a competitor's better site is not buying pages, it is buying booked consultations. Self-Made Web Designer's framing is about moving the client toward being a value-based decision maker rather than a price-comparison shopper. Your evidence inventory from the brief is the raw material here: named outcomes beat adjectives.

Quote mechanics: give a range first ("options land between X and Y"), then anchor on the top of it with the specific reason this project sits there: integration risk, number of stakeholders, launch support, or the outcome it carries. The anchor is not a trick, it is your honest read of the work; if you cannot name the reason, the price is made up.

Scope control lives in the same document as the price. The deliverable list is the boundary. Anything outside it is a written change order with its own fee and its own timeline extension. Every number in this paragraph is a structure, not a market fact: any specific figure quoted in the corpus is UNVERIFIED numeric until checked against the video, including the corpus examples of flat fees around 1500 (videoId jVtIzLoQIxM at [34:15]), low-volume site pricing from about 1000 to 3000 (videoId dnBelEJ9m8o at [04:41]), and five-figure project wins (videoId CWIlmDd6I50). Creator pricing advice is a recommendation, not a market rate.

## Corpus evidence

- Self-Made Web Designer / Know EXACTLY What to Charge for Websites (Data Based Pricing) / dnBelEJ9m8o / [00:33] / and there's this whole value-based pricing system that gets out of hand a little bit
- Self-Made Web Designer / Know EXACTLY What to Charge for Websites (Data Based Pricing) / dnBelEJ9m8o / [05:40] / those who are similar to you
- Self-Made Web Designer / Scale a 1 to 1 Web Design Business with Productized Services / jVtIzLoQIxM / [31:12] / you're going to charge a flat fee of
- Self-Made Web Designer / Scale a 1 to 1 Web Design Business with Productized Services / jVtIzLoQIxM / [33:47] / a fixed deadline and a fixed price so
- Self-Made Web Designer / How to Effectively Price Your Services as a Freelancer and Make More Money / P6uUsn7ogsw / [24:14] / into a value-based decision maker
- Will Paterson / How To Charge More as a Graphic Designer (3 methods) / A6yeVORXODs / [10:14] / price is something called value based

## Anti-patterns

- Hourly confession: sending a proposal where the number is justified by your hours, inviting the client to negotiate your speed.
- Range anchor at the bottom: quoting 10 to 15 and hoping they pick 15, then feeling lucky at 10.
- Scope by goodwill: "sure, we can add a shop" with no change order, which teaches the client the boundary was fiction.
- Retainer on trust: selling recurring work before the first project shipped, so every month becomes a re-pitch.
- Price without a list: a single number with no deliverables, so every disagreement is about what was included.

## Links

parent: web-design-business
children: none

## Contract detail (full text)

- A written quote exists that names the pricing model, lists every deliverable the fee buys, states the out-of-scope change fee, shows the anchor price with its stated reason, and records the client's stated budget from discovery
- Discovery and structure work (see web-design-discovery), client delivery and revision handling (see web-design-business-client), discount approval policy, taxes and invoicing setup, and legal terms (have a lawyer-grade contract reviewed separately)
