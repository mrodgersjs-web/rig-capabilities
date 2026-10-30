---
name: web-design-discovery-brief
description: "Write the client brief before pixels: the buyer's wound in customer words, objection mapping with proof, and language mining from real buyer language."
outcome: A signed one-page brief with a customer-worded wound, a mapped objection table, and a language swipe file.
done_when:
  - 'grep:capabilities/skills/web-design-discovery-brief/SKILL.md:[T]he buyer.s wound comes from mining, never from brainstorming'
  - 'grep:capabilities/skills/web-design-discovery-brief/SKILL.md:[O]ne site action'
  - The one-page brief file contains all seven fields with no empty field, the wound sentence is quoted from mined buyer language with its source noted,
great_example: examples/great/design-ux/web-design-discovery-brief.md
quality_floor: A brief whose wound sentence could describe any business in any industry fails the job. An objection with a rebuttal but no named proof is a gap and must be labeled as one. Any phrase in the brief that does not appear in the swipe file or the client's own words is agency filler and fails the floor.
activation: Load when writing or reviewing a web design brief, when a client says "we want a new site" with no written brief, when copy feels like agency filler, or when preparing discovery questions for a kickoff call.
instruction: "Produce one page with seven fields: one business goal, one site action, one audience written as a person with a wound, three envy sites with a reason, top objections mapped to rebuttal plus proof plus page section, the proof inventory the client actually owns, and the constraints. Mine at least thirty real buyer phrases from reviews, calls, and forums before writing a single headline, and write the wound in the customer's own words. Ask the budget question out loud on the call: how much are you wanting to invest in this project."
applies_when:
  env: Any paid web design project with a real buyer on the other end
  runtime: web page or site rendered in a browser
  deps: the project brief and its design system
  params: "Any paid web design project with a real buyer on the other end: service businesses, lead-gen sites, ecommerce, SaaS marketing sites. Does not apply to internal tools, portfolio sit"
  budget: one pass per artifact
  scale: single page up to a full marketing site
permissions:
  - May read client documents
  - reviews
  - competitor sites
  - sales call notes
  - the local corpus at /Users/rig128gb/Developer/rig-design-studio/corpus/youtube
  - may write briefs
  - questionnaires
  - objection maps
  - language swipe files into the project workspace. Outward actions
  - deploys
  - paid tools
  - purchases
  - publishing need Gate-D approval from Mike
flow:
  - Send the intake questionnaire and warm the client that it is substantial;
  - Collect thirty real buyer phrases from reviews, forums, support email, and call notes;
  - Cluster the phrases into three candidate wounds and pick the one with the most specific language;
  - List objections in buyer words and map each to rebuttal, proof, and the page section that will carry it;
  - Inventory the proof the client owns (cases, numbers, guarantees, reviews);
  - Write the seven-field one-page brief;
  - Read it back to the client on the kickoff call and get dated written sign-off
out_of_scope:
  - Sitemap and wireframing (see web-design-discovery-sitemap), visual design, full copywriting and page builds, pricing and contract terms (see
---
# Web Design Discovery Brief

## Method

The brief is one page and the discipline is subtraction. Seven fields, no empty field, no second page.

1. One business goal. Not "grow the business": a measurable outcome like "book twenty qualified calls a month". If the client hands you two goals, you hand them back one choice.
2. One site action. The single act that counts as a conversion. Everything on the site either drives that act or supports it.
3. One audience, written as a person with a wound. "Small business owners aged 25 to 45" is a database filter, not an audience. "A clinic owner who lost two months of new patient calls to a competitor with a worse clinic but a better site" is an audience.
4. Three envy sites with a reason per site. What they envy is a positioning signal: speed, authority, warmth, price clarity.
5. Objection map: objections in buyer words, each with rebuttal, proof, and the page section that will carry it.
6. Proof inventory: the cases, numbers, reviews, guarantees, and named results the client actually owns. This is your ammunition and most clients under-count it.
7. Constraints: budget band, deadline, platform, legal limits on claims, and who signs off.

The buyer's wound comes from mining, never from brainstorming. Collect at least thirty real phrases from Google and Yelp reviews of the client and their competitors, sales call notes, support email, forum threads where their buyers complain, and the client's own "why customers leave" story. Then cluster: three candidate wounds, pick the one with the most specific and most repeated language. Wes McDowell's case study is the shape of it: customers were using phrases like "tired of posting and getting crickets", and when the site changed to match those exact phrases the sales followed. Note the discipline: the phrases come from where ideal clients are already talking about their problems, not from a persona workshop.

Objection mapping is a table, not a vibe. Rows in the buyer's words: "it costs more than the other quote", "we tried an agency before", "we need to think about it", "why can't we just do this ourselves". Columns: rebuttal, proof (statistic, case, guarantee), and the section of the site where it lives. Wes McDowell's instruction is literal: take the most common objection you get and give it a dedicated section on the homepage to rebut it, through stats or your unique approach. The brief is where you decide which objection gets that section.

Language mining has one rule that most designers break: verbatim beats well-written. A slightly clumsy sentence the buyer actually said will out-pull a polished line you invented. Keep a swipe file of the thirty phrases with sources and dates, and mark which ones are strong enough to become headlines.

Ask the budget out loud. Self-Made Web Designer's line is direct: the easiest way to get the client's budget is to ask the client the budget, on the discovery call, as "how much are you wanting to invest in this project". Paige Brunton's guest puts the budget question in the intake form instead, and notes the failure mode: clients type unrealistically small numbers and then get filtered out. Either placement works; silence about money does not.

## Corpus evidence

- Wes McDowell / Give me 12 mins, and I'll improve your marketing by 125% / rByridDOAKM / [02:33] / talking about their problems online
- Wes McDowell / Give me 12 mins, and I'll improve your marketing by 125% / rByridDOAKM / [01:52] / crickets and I just want to be seen by
- Wes McDowell / 7 Priceless Website Lessons I Normally Charge $$$ For / hDgjahAAi0g / [08:04] / section on your home page to rebut it so
- Self-Made Web Designer / How to Effectively Price Your Services as a Freelancer and Make More Money / P6uUsn7ogsw / [14:00] / easiest way to get the client's budget
- Paige Brunton / Where to find clients who actually pay $25k for a website / RaK0QiHpK0o / [05:04] / know in my intake form like what's your
- Self-Made Web Designer / This Web Design Process Cut My Project Times in Half / O96t2rfwmak / [05:35] / Phase and during this phase, I send the client a pretty comprehensive intake

## Anti-patterns

- Persona theater: invented demographics with stock-photo names instead of mined buyer language.
- Universal wound: a pain sentence that fits a plumber, a law firm, and a SaaS equally, so it sells none of them.
- Objection dodging: listing only friendly questions ("what is your budget") and never the real "why are you so expensive".
- Rebuttal without proof: a confident sentence with no statistic, case, or guarantee behind it, which is a hope in a suit.
- Agency filler: swapping the client's phrase "I keep getting ghosted after quotes" for "streamline your sales funnel".

## Links

parent: web-design-discovery
children: none

## Contract detail (full text)

- The one-page brief file contains all seven fields with no empty field, the wound sentence is quoted from mined buyer language with its source noted, every objection row has a rebuttal and a named proof or is marked as a gap, and the client's dated written approval is recorded
- Sitemap and wireframing (see web-design-discovery-sitemap), visual design, full copywriting and page builds, pricing and contract terms (see web-design-business-pricing), and legal review of claims used as proof
