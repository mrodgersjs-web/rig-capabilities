---
name: "web-conversion-copy-hero"
description: "Write the hero block - headline, subhead and CTA hierarchy - as one promise, one proof and one action that survives the first five seconds. Use when writing
outcome: "An above-fold block of exactly one promise, one mechanism and one action, with the CTA hierarchy written out, both target viewports keeping the primary action
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-conversion-copy-hero/SKILL.md
  - observable: the hero contains one promise, one mechanism and one action and nothing else above the fold
  - observable: the five-second test returns what you get, who it is for and what to click at 3 of 3 from a cold reader
  - observable: the squint test leaves the headline and the primary CTA as the only two things that still read
  - observable: exactly one primary CTA exists above the fold and the primary CTA is visible without scrolling at 1440x900 and 390x844
  - observable: every claim in the hero has a proof element within one screen height below it
great_example: examples/great/design-ux/web-conversion-copy-hero.md
quality_floor: "One promise, one mechanism, one action and nothing else above the fold; a 3 of 3 pass on the five-second test from a cold reader; and a squint pass where the
activation: "A page needs its above-fold block written or rewritten, or a hero exists whose headline, subhead and buttons compete so that a cold visitor cannot say what
instruction: "Build the hero as exactly three things - one promise, one mechanism, one action - and nothing else above the fold. Write the headline as the outcome for the
applies_when:
  env: "macOS or Linux workstation with the page template and the approved page job sentence available"
  runtime: "any landing, marketing or product page rendered as HTML at 1440x900 desktop and 390x844 mobile"
  deps: "the page job sentence from web-conversion-copy, the type scale of the design system, and the proof element that backs the hero claim"
  params: "one H1 under 12 words, one subhead under 25 words, one primary CTA of 2 to 4 words; H1 at 3.2 to 4x body size"
  budget: "one hero per pass with two rewrite rounds against the two tests"
  scale: "one above-fold block of 3 elements plus at most one secondary action and one reassurance line"
permissions:
  - Read the page job sentence, the copy deck, the design system type scale and the sales call notes
  - Write hero copy into the project's copy file or CMS entry
  - Read public competitor heroes to confirm the promise is not category-generic
  - Bash for word counts and viewport-height layout checks only
  - Outward, deploy, paid or public actions (publishing the hero, running a headline test on live traffic) need Gate-D approval from Mike before they run
flow:
  - Take the page job sentence and extract the outcome and the named buyer
  - Write the headline as that outcome in the buyer's words, under 12 words, with no company name and no category label
  - Write the subhead as mechanism plus qualifier in under 25 words, naming who it is for and what it replaces
  - Write one primary CTA as a 2 to 4 word verb phrase the buyer would say, and add one reassurance line under it
  - Set the CTA hierarchy - one filled primary, at most one outline secondary after it, and the nav CTA repeating the primary rather than introducing a new action
  - Set the type scale and the fold - H1 at 3.2 to 4x body, subhead at 1.25 to 1.5x, and the primary CTA visible without scrolling at both target viewports
  - Run the five-second test and the squint test, then rewrite the words if either fails instead of restyling the layout
out_of_scope:
  - Claiming any headline or CTA variant converts better without a controlled test (Gate-D and Mike decide on testing)
  - The proof material itself (see web-conversion-copy-proof)
  - Brand voice, taglines and naming outside this one block
  - Hero imagery, crop and grade (see web-imagery)
  - Layout and type system design beyond the hero block's own scale
---
# Web Conversion Copy Hero

The hero is one promise, one proof, one action. Everything else above the fold is competing
with the only three things that can move a stranger.

**Standing rule for this skill family.** Every claim about what converts is UNVERIFIED unless
the corpus states it AND the corpus frames it as a recommendation. Nothing here is presented
as a measured lift.

## Method

### 1. The three elements and their exact jobs

| element | job | length | it must contain |
|---|---|---|---|
| headline | the promise | under 12 words | a noun the buyer uses and a verb of change |
| subhead | the mechanism | under 25 words | how it works plus a qualifier (who, when, what it replaces) |
| primary CTA | the action | 2 to 4 words | a verb phrase the buyer would say aloud |

Plus, optionally, one reassurance line under the button ("Twenty minutes. No card."). That is
the complete inventory of the hero. A fourth element is a second job.

### 2. Write the headline as an outcome, not a category

Bad headlines fail in three ways. "Welcome to Northwind" promises nothing. "The AI-powered
platform for finance teams" is a category label that four competitors could run unchanged.
"Revolutionise your close" is a verb with no referent.

Good ones name the change and the person it happens to, in words already in the buyer's mouth:
"Close the month in one day, not four." Nine words, a noun the buyer owns (the close), a verb
of change, and a number that makes it checkable.

### 3. The subhead carries the how

The headline promises; the subhead shows the mechanism and adds the qualifier that answers
"is it for me". Two clauses do this. First the mechanism ("matches every invoice against your
ledger export nightly and hands you only the exceptions"), then the qualifier ("so the close
stops being a four-day fire drill"). Under 25 words, and never a restatement of the headline.

### 4. CTA hierarchy, enforced

- Exactly **one primary**, filled, in the accent colour, the only saturated element above the fold.
- At most **one secondary**, outline or ghost, placed after the primary, and none at all is better.
- **No third competing control** above the fold. A chat widget is a third action.
- The **navigation CTA repeats the primary**. It does not introduce "Book a demo" while the hero
  says "Start free".

The label is the buyer's verb phrase: "Book a reconciliation review", "See pricing", "Get the
2026 benchmark". Two to four words. "Submit", "Get started" and "Learn more" name no action and
no outcome.

### 5. The type scale is numeric, use it

At 18px body on desktop:

| element | size | ratio | line height |
|---|---|---|---|
| H1 | 58px | 3.2x | 1.08 |
| subhead | 24px | 1.33x | 1.35 |
| CTA label | 19px bold | 1.05x | 1.2 |
| body | 18px | 1x | 1.6 |

H1 stays inside 3.2 to 4x and 48 to 64px. Below 3x the promise loses the squint test; above 4x
it wraps into a paragraph.

### 6. The fold is a hard constraint at both viewports

The primary CTA must be visible without scrolling at **1440x900** and at **390x844**. On mobile,
the hero image goes behind the copy at low opacity or above it cropped short, and the button
sits at or above 80% of the viewport height. Set `aspect-ratio` on the image so nothing pushes
the button down on load.

### 7. Two tests, and the fix is always the words

**Five-second test.** Five seconds, then hide the page. Ask: what do you get, who is it for,
what do you click. Score 3/3 or rewrite.

**Squint test.** Blur the screen to roughly 8px. The H1 and the primary button must be the two
things that still read. If the wordmark or the hero image wins, the type scale is wrong or the
accent colour is spent on the wrong element.

When either fails, rewrite the headline. Rearranging the layout hides the problem and the next
visitor still cannot tell what the page is for.

## Corpus evidence

self-made-web-designer / The Easiest Way to Build Killer Websites / O7MaPnRy5Us / [07:33] / "The Hero is arguably the most important section of your website"
self-made-web-designer / The Easiest Way to Build Killer Websites / O7MaPnRy5Us / [07:49] / "It needs a motivating header, a clarifying subheader, and then a crystal clear"
self-made-web-designer / The Easiest Way to Build Killer Websites / O7MaPnRy5Us / [10:30] / "After the subheadings done, you need a crystal clear next step,"
self-made-web-designer / 9 Web Design Hacks I Wish I Knew Years Ago / TeMtV8BaZt0 / [00:20] / "It's a hero section that I mocked up, and it's fine,"
self-made-web-designer / 9 Web Design Hacks I Wish I Knew Years Ago / TeMtV8BaZt0 / [19:32] / "Squinted because if your headlines or your call to action don't jump out from"
self-made-web-designer / The Only 5 Web Design Skills That Actually Matter (2026) / vbFn0C-pvis / [13:07] / "I like to include a clear CTA in the hero section, one in the"

**Corpus coverage is real on the three-element shape.** The corpus states the hero as header
plus subheader plus a clear next step, states that the subhead clarifies while the header
motivates, states that the next step must be crystal clear, and names the squint idea directly
by saying headlines and the call to action have to jump out. It also shows a hero that is fine
but does not grab, which is the exact failure this skill exists to prevent.

UNVERIFIED against this corpus - the word counts and their limits, the type scale table and
every ratio in it, the CTA hierarchy rules including the nav-repeats-primary rule, the
five-second test and its 3 of 3 scoring, the 8px squint method, and the fold requirement at
both named viewports. Per the standing rule, none of these is claimed to lift conversion. All
caption tracks in the corpus are automatic.

## Anti-patterns

- Welcome mat: "Welcome to X" as the H1, which promises nothing and wastes the loudest line on the page.
- Category label: a headline four competitors could run unchanged.
- The four-control drawer: primary, secondary, nav item and a chat widget all competing for the first click.
- Logo beats promise: a wordmark larger and louder than the thing the page is selling.
- Below-fold CTA: the one action pushed out of the mobile viewport by a tall hero image.

## Links

- parent: when-designing-websites
- parent: web-conversion-copy
- children: none (leaf skill)

## description (full text)

"Write the hero block - headline, subhead and CTA hierarchy - as one promise, one proof and one action that survives the first five seconds. Use when writing or rewriting an above-fold block, when a headline has to name an outcome for a named buyer, or when the top of a page fails the squint or five-second test."

## outcome (full text)

"An above-fold block of exactly one promise, one mechanism and one action, with the CTA hierarchy written out, both target viewports keeping the primary action visible without scrolling, and recorded passes on the five-second and squint tests."

## quality_floor (full text)

"One promise, one mechanism, one action and nothing else above the fold; a 3 of 3 pass on the five-second test from a cold reader; and a squint pass where the headline and the primary CTA are the only two things that still read. A hero with two competing primary actions fails the job."

## instruction (full text)

"Build the hero as exactly three things - one promise, one mechanism, one action - and nothing else above the fold. Write the headline as the outcome for the named buyer in their own words under twelve words, the subhead as the mechanism and the qualifier under twenty-five, and the CTA as a two-to-four word verb phrase the buyer would say aloud. Give the block exactly one primary action with at most one secondary placed after it, then prove it against the five-second test and the squint test and rewrite rather than rearrange when either fails."

## description (full text)

"Write the hero block - headline, subhead and CTA hierarchy - as one promise, one proof and one action that survives the first five seconds. Use when writing or rewriting an above-fold

## outcome (full text)

"An above-fold block of exactly one promise, one mechanism and one action, with the CTA hierarchy written out, both target viewports keeping the primary action visible without scrolling

## quality_floor (full text)

"One promise, one mechanism, one action and nothing else above the fold; a 3 of 3 pass on the five-second test from a cold reader; and a squint pass where the headline and the primary CTA

## activation (full text)

"A page needs its above-fold block written or rewritten, or a hero exists whose headline, subhead and buttons compete so that a cold visitor cannot say what the page offers or what to click."

## instruction (full text)

"Build the hero as exactly three things - one promise, one mechanism, one action - and nothing else above the fold. Write the headline as the outcome for the named buyer in their own words
