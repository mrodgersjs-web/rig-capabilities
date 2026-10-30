---
name: web-design-discovery-sitemap
description: Turn a signed brief into a page inventory, sitemap, content-first page plan, and lo-fi wireframes before any visual design starts.
outcome: "A signed structure pack: page inventory with kill list, sitemap, per-page content direction, and lo-fi wireframes."
done_when:
  - 'grep:capabilities/skills/web-design-discovery-sitemap/SKILL.md:[E]very page must justify its existence against the brief'
  - A page inventory file shows every candidate with a survive-or-kill verdict and reason, a sitemap file shows nav items and click depth, a content plan
great_example: examples/great/design-ux/web-design-discovery-sitemap.md
quality_floor: Any surviving page without a named single job fails the job. A sitemap with more than seven nav items or a page more than two clicks from home fails. A wireframe showing a real font, real color, real photo, or polished spacing fails the floor.
activation: Load when planning site pages and structure, when a client hands over a page wishlist, when a sitemap or wireframe is due, when a redesign needs its page count cut, or when someone wants to jump straight into visual design.
instruction: Classify the site type first, then write every page candidate on a card and make each prove one job before it survives. Build the sitemap from survivors only, with navigation of five to seven items and no page more than two clicks from home. Write real copy direction per page before designing it, and draw wireframes so lo-fi that no font, color, or style decision is visible. Get dated written sign-off on the sitemap before wireframes and on wireframes before any visual design.
applies_when:
  env: Structure phase of any marketing website
  runtime: web page or site rendered in a browser
  deps: the project brief and its design system
  params: "Structure phase of any marketing website: brochure and service sites, lead-gen sites, portfolios, ecommerce, SaaS marketing sites, course or membership sites. Not for app interface"
  budget: one pass per artifact
  scale: single page up to a full marketing site
permissions:
  - May read the brief
  - analytics
  - competitor sites
  - the local corpus at /Users/rig128gb/Developer/rig-design-studio/corpus/youtube
  - may write page inventories
  - sitemaps
  - wireframes
  - content plans into the project workspace. Outward actions
  - deploys
  - paid tools
  - purchases
  - publishing need Gate-D approval from Mike
flow:
  - Classify the site type and its one job;
  - List every page candidate on cards, one page per card;
  - Kill every card without a single job and a reason to exist;
  - Order survivors into a sitemap with nav of five to seven items and depth of at most two from home;
  - "Write per-page content direction: the job, the argument, the section stack, the one action;"
  - Get dated written sitemap sign-off;
  - Draw lo-fi wireframes per page with written section-intent notes;
  - Get dated written wireframe sign-off;
  - Hand the pack to visual design
out_of_scope:
  - Visual design and brand identity, production copywriting and SEO page copy, development and CMS build, migration and redirects, and pricing or scope
---
# Web Design Discovery Sitemap

## Method

Start by naming the site type, because the type decides the page set:

- Service or brochure site: one job, contact or booking. Core pages: home, services, one detail page per service that earns its own search demand, work or proof, about, contact.
- Lead-gen site: one job, the form or call booking. Core pages: home, one landing page per offer or per audience, proof, contact. Landing pages are separate pages on purpose: one audience, one promise, one form.
- Portfolio: one job, the inquiry. Core pages: home, case studies, about, contact. Case studies are the product.
- Ecommerce: one job, checkout. Core pages: home, category, product, cart, checkout, plus trust pages (shipping, returns, reviews).
- SaaS marketing site: one job, trial or demo. Core pages: home, features or use cases, pricing, comparison, docs or help, sign-up.
- Course or membership: one job, enroll. Core pages: home, curriculum, instructor, testimonials, pricing, enroll.

The page inventory comes next and it is a kill list in disguise. Write every page candidate on a card: the ones the client asked for, the ones their competitors have, the ones you think they need. Then make each card prove one job, meaning one thing the page does to a visitor and one action it asks for. A card that says "we should probably have a blog" has no job. Kill it. Expect to lose a large share of the candidates; a typical client wishlist runs about twice the site they actually need, and the cut is one of the most valuable things you sell.

Sitemap rules are few and strict:

- Navigation holds five to seven items. Everything else lives in footer, in-context links, or under a parent page.
- No page more than two clicks from home.
- One job per page, and the job names the page's action.
- Every page must justify its existence against the brief's single site action. If a page cannot say how it pushes toward that action, it is a candidate for the kill list.

The sitemap is the foundation for the whole structure, and it gets signed off before anything visual. Paige Brunton's warning is the reason: without a clear sitemap you risk a confusing layout and missing key pages, and that discovery happens far too late when it happens in the design.

Content direction before design, because the words carry the persuasion. Wes McDowell's framing: the words on the website do most of the heavy lifting when it comes to persuading people. So per page write: the job, the argument in one sentence, the section stack (for example: promise, problem, method, proof, objection, action), and the one action. Paige Brunton's build videos work copy-first before building: copy first, then layout. The design's job is to make the argument land, not to substitute for it.

Wireframes stay ruthlessly lo-fi: grey blocks, marks for text, no real fonts, no color, no photography, no polish. Add a one-line note per section describing its job ("this bar answers 'have you done this for someone like me'"). Self-Made Web Designer's reason for going as lo-fi as possible is repeated client scarring: anything concrete you show becomes a decision you have to un-sell later, like the client who fell for the placeholder font in his wireframe.

## Corpus evidence

- Self-Made Web Designer / Complete Web Design Process: What Took Me 10 Years to Learn in 12 Minutes [Free Trello Template] / T5JglDcd54A / [04:07] / A sitemap is just a really basic layout of all the pages
- Self-Made Web Designer / Complete Web Design Process: What Took Me 10 Years to Learn in 12 Minutes [Free Trello Template] / T5JglDcd54A / [04:13] / a wireframe is a really lo fi mock up of what each of
- Paige Brunton / Watch Me Redesign An Ugly Website | COMPLETE TRANSFORMATION / U3hBqQVrtco / [11:54] / how to plan your own sitemap ask
- Paige Brunton / 12 Squarespace HACKS To Build A Site FAST! / X8ghDDDIG6k / [02:18] / copy first before you go to build the
- Wes McDowell / Making a Website? Here's How to Get it Right... / QeoUzK4wlkQ / [04:09] / gonna do most of the heavy lifting
- Flux Academy / Web Design Case Study: Re-design and Migration / gyKl52YHOU0 / [01:54] / sitemap and strategy and then from there

## Anti-patterns

- Wishlist acceptance: building every page the client named without making one card prove its job.
- Nav dumping ground: a nine-item menu where five items exist to make the site "look bigger".
- Design-first page: mocking a beautiful home page and then discovering the copy cannot carry the argument.
- Wireframe cosplay: high-fidelity wireframes with real type and color that the client falls in love with before strategy is settled.
- Sitemap by committee: letting every stakeholder add a page instead of defending the single site action.

## Links

parent: web-design-discovery
children: none

## Contract detail (full text)

- A page inventory file shows every candidate with a survive-or-kill verdict and reason, a sitemap file shows nav items and click depth, a content plan names each page's job and section stack, wireframes carry no font, color, or style decision, and both the sitemap and the wireframes carry dated written sign-off
- Visual design and brand identity, production copywriting and SEO page copy, development and CMS build, migration and redirects, and pricing or scope terms (see web-design-business-pricing)
