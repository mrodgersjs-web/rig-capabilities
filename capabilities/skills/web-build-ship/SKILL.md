---
name: web-build-ship
description: Take a designed web surface from local to live without losing the design. Performance, responsiveness, accessibility, SEO and deploy gates in one pass. Use before anything leaves the machine.
outcome: A shipped or ship-ready web surface with a recorded audit receipt containing real measured numbers and named failures fixed at source.
done_when:
  - LCP <= 2.5s, CLS <= 0.1 and INP <= 200ms recorded on throttled hardware
  - zero axe critical and zero axe serious violations
  - all four viewports render with no horizontal overflow
  - every measured number recorded with its before and after values
  - deploy is either executed under an approved Gate-D run id or explicitly recorded as held
great_example: examples/great/design-ux/web-build-ship.md
quality_floor: No ship claim without measured numbers. No "looks fine on mobile" without having rendered 390px. No deploy without Gate-D.
activation: Load when a designed page or site is about to be shown to a client, deployed, submitted, or when the job says "ship it" / "make it live".
instruction: >
  Run the four gates in order: responsive, performance, accessibility, discoverability. Each gate
  produces a measured number or a named failure, never an adjective. Fix failures at the source
  (the component or token), not with local patches. Anything that spends money or publishes publicly
  stops at Gate-D and waits for Mike.
applies_when:
  env: local repo or local build server
  runtime: web page or site intended for a browser
  deps: local build toolchain, Lighthouse, axe or equivalent audit tooling
  params: viewports 390px, 768px, 1280px, 1536px; throttled hardware for perf measurement
  budget: one audit pass per ship, fixes landed at component or token level
  scale: single page up to a full marketing site
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
  - gate-d-required:deploy
  - gate-d-required:publish
  - gate-d-required:purchase
flow:
  - Build locally and confirm the page renders at 390px, 768px, 1280px and 1536px.
  - Run web-build-ship-responsive and fix reflow, overflow and touch-target failures.
  - Run web-build-ship-performance and record LCP, CLS, INP and bundle size as numbers.
  - Run an accessibility sweep (axe plus keyboard plus reduced-motion) and record failures by rule id.
  - Check discoverability: one h1, title, meta description, canonical, OG/Twitter, JSON-LD, sitemap, robots, noscript floor.
  - Re-measure after fixes and record before and after numbers.
  - Stop before deploy or publish and request Gate-D.
out_of_scope:
  - backend architecture and database design
  - native mobile application builds
  - paid advertising spend
  - any public action taken without Gate-D approval
---
# Web Build & Ship

The gate between "designed" and "live". It measures, it does not opine.

## Method

**Responsive.** Design to breakpoints, not devices: 390 / 768 / 1280 / 1536. Test reflow order at each:
which block moves first, what stacks, what is hidden (hiding content on mobile is usually a content
failure, not a layout fix). Touch targets >= 44px. No horizontal overflow at any width: assert it,
`document.scrollingElement.scrollWidth <= innerWidth`.

**Performance.** Three numbers and a size:
- LCP <= 2.5s (hero: preload the LCP font/image, do not lazy-load above-fold media)
- CLS <= 0.1 (always reserve media dimensions; never insert content above existing content)
- INP <= 200ms (keep long tasks off the main thread)
- JS payload: justify every framework byte on a marketing page. A static page that ships 300KB of JS
  to render text has a design problem, not just a performance one.

Font loading is the silent LCP killer: subset, `font-display: swap`, preload only the display face.

**Accessibility.** WCAG AA is the floor. Contrast 4.5:1 body, 3:1 large text and UI. Keyboard-only
pass through every interactive element with a visible focus ring. `prefers-reduced-motion` collapses
motion to opacity or nothing. Meaningful `alt`; empty `alt` only for decoration. One `h1`, headings
in order, forms with labels.

**Discoverability.** One `h1`. Unique title + meta description per page. Canonical URL. Open Graph and
Twitter card. JSON-LD `@graph`. `sitemap.xml`, `robots.txt`. A `noscript` floor so the content is
crawlable without JS.

**The design-preserving rule.** Every fix lands at the component or token level. If a performance fix
changes how the page looks, that is a design change and goes back through `web-design-critique`.

## Corpus evidence

- Flux Academy / Learn Web Design For Beginners - Full Course / j6Ule7GXaRs / [1:57:42] / "font files into your website slows down"
- Flux Academy / Build a custom website with no code! (Relume & Webflow) / 8bm1Pl5ecEI / [53:01] / "should have compressed the images before"
- Flux Academy / Build a custom website with no code! (Relume & Webflow) / 8bm1Pl5ecEI / [53:18] / "compress them for me and turn them into"
- Flux Academy / Learn Web Design For Beginners - Full Course / j6Ule7GXaRs / [04:37] / "accessible. It will also include"

The numeric thresholds above (LCP/CLS/INP, 44px, 4.5:1) are `UNVERIFIED` against this corpus: they
come from the published Web Vitals and WCAG specifications, not from a creator's recommendation. Keep
them as gates because they are external standards, and label them as such.

## Anti-patterns

- Reporting "it passed" with no number attached.
- Lazy-loading the LCP element to make a metric move.
- Fixing contrast by eye instead of measuring the ratio.
- Hiding content on mobile to make overflow go away.
- Declaring a ship done when deploy is actually held at Gate-D. Say "ship-ready, deploy held".

## Links

parent: when-designing-websites
children: web-build-ship-responsive, web-build-ship-performance
