---
name: "web-conversion-copy"
description: "Write the copy that makes a web page do one job - decide the page's single action, order the copy to match the buyer's decision
outcome: "A page copy deck carrying one written page job, one primary action, content blocks ordered to the buyer's five-step decision
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-conversion-copy/SKILL.md
  - observable: the page job sentence exists in writing and names the buyer, the action and the reason
  - observable: the page has exactly one primary action and every block serves it or has been cut
  - observable: copy order matches the five-step decision order with one block assigned to each step
  - observable: the five-second test returns the offer, the audience and the next action from a cold reader
  - observable: every claim about conversion is labelled a recommendation and never stated as a measured result
great_example: examples/great/design-ux/web-conversion-copy.md
quality_floor: "One page job sentence naming buyer, action and reason exists before any copy; exactly one primary action survives; every claim
activation: "A page needs copy written or rewritten, or a page exists that visitors read and leave from without taking the action it was built for."
instruction: "Write the page's job as one sentence naming the buyer, the action and the reason before a word of copy exists, and cut every
applies_when:
  env: "macOS or Linux workstation with the project's copy deck or page template available locally"
  runtime: "any marketing, landing, product or pricing page rendered as HTML, or a CMS entry that produces one"
  deps: "a source of the customer's own words (sales calls, support tickets, reviews) and the offer or pricing definition"
  params: "one page carries one primary action; measure 45 to 75 characters per line; headline under 12 words, subhead under 25, CTA label 2 to 4 words"
  budget: "one page per pass, with time for two rewrite rounds after the first five-second test"
  scale: "one page at a time, up to 12 content blocks, one primary and at most one secondary action"
permissions:
  - Read the copy deck, the page template, sales call notes, support tickets and reviews
  - Write page copy into the project's copy file or CMS entry
  - Read public competitor pages to check the wording is not generic to the category
  - Bash for word counts, line-length checks and reading-time checks only
  - Outward, deploy, paid or public actions (publishing the page, sending copy to a client, running a paid test) need Gate-D approval from Mike before they run
flow:
  - Write the page job as one sentence of the form get a named buyer to take a named action because of a named reason
  - Collect the buyer's own words from calls, tickets and reviews, and put the recurring phrases in a list beside the draft
  - Lay out the decision order (what is this, is it for me, why believe it, what do I do, what if it goes wrong) and assign one block to each
  - Write feature, benefit and mechanism for each claim, then place the benefit in the headline, the feature in the visual and the mechanism in the supporting line
  - Name one primary action and give it a verb phrase the buyer would say; demote or cut every competing action
  - Run the five-second test and the read-aloud test, then rewrite the hero rather than rearranging the layout when either fails
  - Label every conversion claim as a recommendation and hand the hero block to web-conversion-copy-hero and the proof block to web-conversion-copy-proof
out_of_scope:
  - Presenting any conversion claim as a measured outcome without a controlled test (Gate-D and Mike decide on testing)
  - Pricing strategy and price setting (see web-conversion-copy-proof for the pricing page structure)
  - Brand voice, tagline and naming work outside a single page
  - Email, ad and social copy, which follow different length and context rules
  - Layout, typography and imagery (see web-imagery and when-designing-websites)
---
# Web Conversion Copy

A page that reads beautifully and does nothing is a brochure with a hosting bill. This skill
is about making the words carry one job, in the order a real buyer actually decides.

**Standing rule for this skill family.** Every claim about what converts is UNVERIFIED unless
the corpus states it AND the corpus frames it as a recommendation. A creator's opinion is
never presented here as a measured outcome. No number in this skill is an observed lift.

## Method

### 1. The page job sentence

Before any copy, one sentence in this exact shape:

> Get **[named buyer]** to **[named action]** because **[named reason]**.

"Get mid-market finance controllers to book a twenty-minute reconciliation review because
month-end close currently takes their team four days."

If you cannot fill all three blanks, the page is not ready for words. Every block that goes
onto the page is then checked against the sentence. Two blocks in the worked example were
cut for failing it, and cutting is usually where the page gets better.

### 2. Copy order is decision order

A buyer runs the same five questions in the same order. Put the blocks in that order.

| # | the question in their head | the block that answers it |
|---|---|---|
| 1 | what is this? | headline (the promise) |
| 2 | is it for me? | subhead naming the buyer and their situation |
| 3 | why believe it? | proof stack (see web-conversion-copy-proof) |
| 4 | what do I do? | the primary action |
| 5 | what if it goes wrong? | objections answered inline, plus risk reversal |

The common failure is answering question 5 in a footer FAQ and question 3 at the very bottom,
which is answering doubts after the reader has stopped having them.

### 3. One primary action

One. Not two, not "two but one is quieter". Give it a verb phrase the buyer would say out
loud. "Book a reconciliation review", not "Get started", not "Learn more", not "Submit".

Secondary actions get outline or ghost styling, appear at most once per screen height, and
never sit beside the primary at equal weight. A navigation bar that offers a different action
introduces a second job to the page and has to be reconciled with the hero.

### 4. Feature, benefit, mechanism - write all three

For every claim, write the three parts, then place them deliberately.

- **Feature** - what it is. "Line-level matching against the ledger export."
- **Benefit** - what changes for the buyer. "Close in one day instead of four."
- **Mechanism** - why it is true. "It reads the ledger export nightly and flags only exceptions."

Placement rule: the benefit headlines, the feature lives where the product is visible, and
the mechanism sits in the supporting line for the sceptic who wants to know it is not magic.
Writing only the benefit gives you hype. Writing only the feature gives you a spec sheet.

### 5. Mirror the buyer, not the vendor

Collect the phrases from sales calls, support tickets, reviews and lost-deal notes. Those are
the words that already work on this buyer. Internal nouns ("workflow orchestration layer")
fail the read-aloud test: if a customer would not say it, rewrite it.

The same discipline removes the company as the subject. The buyer is the one taking action in
the sentence, so the sentence should be about their outcome. "We are passionate about X"
describes the vendor's mood and promises nothing.

### 6. Length and measure numbers

These are craft floors, not conversion claims.

- Headline under 12 words. Subhead under 25. CTA label 2 to 4 words as a verb phrase.
- Body paragraph under 4 lines at the target measure.
- Line measure 45 to 75 characters, which is where sustained reading sits comfortably.
- One idea per paragraph. Two ideas means two paragraphs.

UNVERIFIED - that any of these length rules lifts conversion. They are readability craft
rules and are stated as recommendations.

### 7. Two tests before you call it done

**Five-second test.** Show the page to someone cold for five seconds, hide it, ask three
questions: what do you get, who is it for, what do you click. Two wrong out of three means
rewrite the hero, not rearrange the page.

**Read-aloud test.** Read the whole deck aloud. Anywhere you stumble, the sentence is written
for the writer. Rewrite it in the words of the person who has to act on it.

## Corpus evidence

flux-academy / I Challenge You To Design a Website in 2 Hours! / lMlZ4U1MFto / [05:37] / "headline, value proposition, and CTA,"
self-made-web-designer / The Easiest Way to Build Killer Websites / O7MaPnRy5Us / [15:06] / "does the headline make sense immediately?"
self-made-web-designer / 9 Web Design Hacks I Wish I Knew Years Ago / TeMtV8BaZt0 / [08:45] / "subheading copy, and it's already starting to be easier to engage"
self-made-web-designer / How to Make a Winning Upwork Profile / PmDMg88oJXo / [07:40] / "Isn't looking for you to be the hero of their story"
self-made-web-designer / 50 Web Design Tips & Tricks to Level Up Instantly / rRFD6tENX2U / [12:14] / "You want to do things like see pricing or download the guide instead of things"
self-made-web-designer / The Easiest Way to Build Killer Websites / O7MaPnRy5Us / [09:50] / "the how of how I'm gonna deliver what I offer them in this headline"

**Corpus coverage is real on structure and absent on outcomes.** The corpus supports the
headline-value-proposition-CTA decomposition, the idea that the headline has to make sense
immediately, the subhead carrying the how, the buyer as the hero of the story rather than the
vendor, and action labels written as concrete destinations ("see pricing", "download the
guide") rather than abstractions. It reports no conversion measurements at all.

UNVERIFIED against this corpus - the five-step decision-order table, the page job sentence
pattern, the one-primary-action rule, the feature-benefit-mechanism triplet, the mirror-the-buyer
rule, the read-aloud and five-second tests as pass criteria, and every length and measure
number. Per the standing rule above, nothing here is claimed to lift conversion; each is a
recommendation. All caption tracks in the corpus are automatic.

## Anti-patterns

- Brochure page: no single action named anywhere, so every visitor leaves having read.
- Two primary CTAs: equally weighted buttons for different actions in one screen height.
- Feature dumping: a list of what it is with no line about what changes for the buyer.
- Vendor dialect: internal nouns the customer never says out loud.
- Clever with no referent: a headline that means nothing after five seconds.

## Links

- parent: when-designing-websites
- children: web-conversion-copy-hero, web-conversion-copy-proof

## description (full text)

"Write the copy that makes a web page do one job - decide the page's single action, order the copy to match the buyer's decision order, and write headlines, mechanisms and CTAs in the buyer's own words. Use when writing or rewriting page copy, defining a page's call to action, or diagnosing a page that reads well and does nothing."

## outcome (full text)

"A page copy deck carrying one written page job, one primary action, content blocks ordered to the buyer's five-step decision order with feature, benefit and mechanism written for each claim, and every conversion claim labelled as a recommendation."

## quality_floor (full text)

"One page job sentence naming buyer, action and reason exists before any copy; exactly one primary action survives; every claim carries a benefit and a mechanism; and no conversion claim is presented as a measured result. A page with two competing primary actions or an unlabelled conversion claim fails the job."

## instruction (full text)

"Write the page's job as one sentence naming the buyer, the action and the reason before a word of copy exists, and cut every block that does not serve it. Order the copy in the buyer's decision order - what is this, is it for me, why believe it, what do I do, what if it goes wrong - and give the page exactly one primary action. Mirror the customer's own words from calls, tickets and reviews rather than the vendor's internal nouns, and write the feature, the benefit and the mechanism for every claim before deciding where each one sits. Label every conversion claim as a recommendation, never as a measured result."

## description (full text)

"Write the copy that makes a web page do one job - decide the page's single action, order the copy to match the buyer's decision order, and write headlines, mechanisms and CTAs in the

## outcome (full text)

"A page copy deck carrying one written page job, one primary action, content blocks ordered to the buyer's five-step decision order with feature, benefit and mechanism written for each

## quality_floor (full text)

"One page job sentence naming buyer, action and reason exists before any copy; exactly one primary action survives; every claim carries a benefit and a mechanism; and no conversion claim is

## instruction (full text)

"Write the page's job as one sentence naming the buyer, the action and the reason before a word of copy exists, and cut every block that does not serve it. Order the copy in the buyer's

## description (full text)

"Write the copy that makes a web page do one job - decide the page's single action, order the copy to match the buyer's decision order, and write headlines

## outcome (full text)

"A page copy deck carrying one written page job, one primary action, content blocks ordered to the buyer's five-step decision order with feature, benefit and

## quality_floor (full text)

"One page job sentence naming buyer, action and reason exists before any copy; exactly one primary action survives; every claim carries a benefit and a

## instruction (full text)

"Write the page's job as one sentence naming the buyer, the action and the reason before a word of copy exists, and cut every block that does not serve it.
