---
name: web-design-discovery
description: Run web design discovery so the brief, the buyer, and the site structure are settled and signed off before any pixels, on any paid website project.
outcome: "A signed-off discovery pack: one-page brief, buyer wound and objection map, page inventory, sitemap, and lo-fi wireframes."
done_when:
  - 'grep:capabilities/skills/web-design-discovery/SKILL.md:[T]hree artifacts gate the design'
  - 'grep:capabilities/skills/web-design-discovery/SKILL.md:[T]he one-page brief. Exactly one business goal'
  - A brief, an objection map, a page inventory, a sitemap, and wireframes exist as files, each carries a dated written client sign-off, and no visual
great_example: examples/great/design-ux/web-design-discovery.md
quality_floor: If any of the three artifacts is missing, unreviewed, or signed off only verbally, the job fails regardless of how good the pixels look. A wireframe that communicates a font, color, or style decision also fails the floor.
activation: Load when scoping a client website, before a design kickoff, when someone asks "how much and how long" with no brief in hand, or when a design is about to start from a mood board or a reference screenshot.
instruction: "Refuse to open a design tool until three artifacts exist with dated written sign-off: a one-page brief naming one business goal and one site action, a buyer wound written in the customer's own words with objections mapped to rebuttal evidence, and a page inventory plus sitemap plus lo-fi wireframes. Sequence the work as setup, questionnaire, research, kickoff call, then structure. Put a deadline with a consequence on every client feedback round so the project cannot stall on their side."
applies_when:
  env: Someone is paying for a website
  runtime: web page or site rendered in a browser
  deps: the project brief and its design system
  params: "Someone is paying for a website: service and brochure sites, lead-gen sites, portfolios, ecommerce, SaaS marketing sites, and redesign or migration work. Applies to the discovery a"
  budget: one pass per artifact
  scale: single page up to a full marketing site
permissions:
  - May read client briefs
  - questionnaires
  - competitor sites
  - analytics
  - reviews
  - the local corpus at /Users/rig128gb/Developer/rig-design-studio/corpus/youtube
  - may write briefs
  - questionnaires
  - page inventories
  - sitemaps
  - wireframes into the project workspace. Outward actions
  - deploys
  - paid tools
  - purchases
  - publishing need Gate-D approval from Mike
flow:
  - Send the questionnaire and warn the client it is long;
  - Review answers and research the market and three competitor sites;
  - Run the kickoff call against their answers;
  - Write the one-page brief with one goal, one site action, one audience;
  - Mine customer language and map each objection to rebuttal evidence;
  - Write the page inventory and sitemap and collect written sign-off;
  - Draw lo-fi wireframes with zero design decisions and collect written sign-off;
  - Only then open the visual design file
out_of_scope:
  - Visual design and branding, full copywriting execution beyond headline and section direction, development and build, SEO campaigns, ad buying, and
---
# Web Design Discovery

## Method

Discovery is not ceremony, it is where the expensive mistakes are still cheap. A page moved in a sitemap costs a minute; the same page moved after the build costs a week. Self-Made Web Designer's blunt version: by the time you are doing revisions, it is already too late to fix the problem. So fix it in the brief.

Order of operations, and it does not bend: setup, questionnaire, research, kickoff call, then structure, then pixels. The questionnaire goes out before the call, and you warn the client in advance that it is long. Answers you get in writing are better than answers you half-remember from a call, and they give you the client's own words to work with.

Three artifacts gate the design. All three, in writing, signed off.

1. The one-page brief. Exactly one business goal (if the client names two, make them kill one), exactly one site action that counts as a conversion (book a call, buy, apply), one audience described as a person with a problem rather than a demographic, three competitor or reference sites they envy and one line on why, and the metric that proves the site worked. One page. If it needs two, you do not know what the project is yet.

2. The buyer wound and objection map. The wound is the sentence the buyer says when they are frustrated, in their words, not "they need more leads". Mine it from reviews, sales calls, support email, and forum threads (see web-design-discovery-brief for the method). Then list their top objections in their words, and for each one: the rebuttal, the proof behind it (statistic, case, guarantee), and the section of the site where that rebuttal will live. An objection with no proof is a hope, not a rebuttal.

3. The structure pack. Page inventory first (one job per page, no exceptions), then the sitemap, then wireframes. Paige Brunton's line is the standard: a sitemap is the foundation for the site's structure. Sign off the sitemap before wireframes, sign off wireframes before design.

Wireframes stay lo-fi on purpose. Self-Made Web Designer tells you to go as lo-fi as you can, and his reason is a scar: he once wireframed with a boilerplate font, the client approved, and later asked to keep that font in the real design. Any concrete detail you show early becomes a client decision you now have to argue out of. Wireframes carry layout and hierarchy only: rectangles for images, marks for text, and a written note of each section's job.

Feedback rounds carry deadlines with consequences. Self-Made Web Designer gives clients a fixed window to respond (his stated window is 24 hours: UNVERIFIED numeric, auto-captions mishear numbers) and treats silence as approval so the project keeps moving. Put the rule in the onboarding doc, not in an email you send when you are already annoyed.

Kickoff call agenda: who they are, what they do, what they sell, why they are different from the two competitors they fear, and where they want the business to go. Will Paterson walks a question series like that before any design work. Write their answers down verbatim; the best headline on the site is usually hiding in one of them.

## Corpus evidence

- Self-Made Web Designer / Complete Web Design Process: What Took Me 10 Years to Learn in 12 Minutes [Free Trello Template] / T5JglDcd54A / [05:52] / Once I get the sitemap and wireframes all kind of signed off on
- Self-Made Web Designer / Complete Web Design Process: What Took Me 10 Years to Learn in 12 Minutes [Free Trello Template] / T5JglDcd54A / [05:34] / my encouragement to you is to go as lo fi as you can
- Self-Made Web Designer / This Web Design Process Cut My Project Times in Half / O96t2rfwmak / [02:04] / By the time you're doing revisions, it's already too late to fix the problem
- Self-Made Web Designer / This Web Design Process Cut My Project Times in Half / O96t2rfwmak / [03:27] / There's the setup, the questionnaire
- Paige Brunton / Watch Me Redesign An Ugly Website | COMPLETE TRANSFORMATION / U3hBqQVrtco / [07:45] / sitemap is the foundation for your
- Will Paterson / How I Design a Brand Identity in Affinity (Full Workflow) / V3pQ2BXblUE / [00:48] / walk through a series of questions like

## Anti-patterns

- Pixel-first panic: opening Figma before the sitemap is signed because the client is "excited to see something".
- Mood board as brief: treating three reference screenshots as a strategy document.
- Verbal sign-off: accepting "looks great!" on a call as approval and then defending every later change for free.
- Design-decision wireframes: real fonts, real colors, and real photos in a wireframe that you will have to un-approve later.
- Kitchen-sink brief: a brief with five goals and four audiences, which is a decision you refused to make.

## Links

parent: when-designing-websites
children: web-design-discovery-brief, web-design-discovery-sitemap

## Contract detail (full text)

- A brief, an objection map, a page inventory, a sitemap, and wireframes exist as files, each carries a dated written client sign-off, and no visual design file was created before the latest of those sign-off dates
- Visual design and branding, full copywriting execution beyond headline and section direction, development and build, SEO campaigns, ad buying, and pricing or contract terms (see web-design-business)
