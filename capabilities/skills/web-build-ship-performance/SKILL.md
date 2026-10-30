---
name: web-build-ship-performance
description: Hit Core Web Vitals without gutting the design. Fonts, media, JS weight and layout stability as measured budgets. Use when a page is slow, janks, or a metric needs to move.
outcome: A page that meets its performance budgets with a recorded before/after receipt and no unacknowledged design change.
done_when:
  - 'grep:capabilities/skills/web-build-ship-performance/SKILL.md:[N]ame the LCP element first'
  - 'grep:capabilities/skills/web-build-ship-performance/SKILL.md:[E]very .img. and .video. carries'
  - LCP <= 2.5s measured on throttled hardware
  - CLS <= 0.1 measured over a real load
  - INP <= 200ms with no main-thread task over 50ms during interaction
  - before and after numbers recorded for every change
great_example: examples/great/design-ux/web-build-ship-performance.md
quality_floor: No performance claim without a measured number and its measurement conditions. No metric moved by hiding or deferring the thing the user actually came to see.
activation: Load during web-build-ship, when the user says "it's slow", "it janks", "LCP", "Lighthouse", or before any deploy.
instruction: >
  Measure first, then attack the largest contributor. Budgets: LCP <= 2.5s, CLS <= 0.1, INP <= 200ms
  on throttled hardware. Fonts and unreserved media are the two most common causes and both are
  design-visible, so fix them at the design layer rather than masking them.
applies_when:
  env: local repo and a throttled browser profile
  runtime: web page loading over a constrained network
  deps: Lighthouse or equivalent, a local build, image and font assets
  params: mid-range hardware, throttled CPU and network, LCP/CLS/INP measurement window
  budget: LCP <= 2.5s, CLS <= 0.1, INP <= 200ms, hero image <= 200KB, card image <= 60KB
  scale: single page up to a full marketing site
permissions:
  - fs.read
  - fs.write
  - bash
  - gate-d-required:deploy
  - gate-d-required:purchase
flow:
  - Measure the baseline with Lighthouse and a throttled load; record LCP, CLS, INP and transfer size.
  - Identify the LCP element explicitly and name which DOM node it is.
  - Fix in this order: LCP resource loading, layout stability, main-thread work, transfer size.
  - Re-measure and record before and after in one line each.
  - If a fix changes the visual design, route it back through web-design-critique.
out_of_scope:
  - server capacity planning and CDN procurement
  - backend query tuning
  - third-party tag governance
---
# Build & Ship: Performance

Budgets as design constraints, not an afterthought.

## Method

**Name the LCP element first.** Until you can say which DOM node is the LCP, you are guessing. Then:
preload it, do not lazy-load it, and keep it out of a client-rendered branch.

**Fonts.** The highest-leverage and most design-visible fix:
- Subset to the glyphs used; convert to woff2.
- `font-display: swap` (or `optional` if the type can tolerate a fallback frame).
- Preload only the display face, never every weight. Two families and two weights is usually the
  whole working set. Loading 6 weights to use 2 is the common failure.

**Layout stability.** Every `img` and `video` carries `width`/`height` or `aspect-ratio`. Never insert
banner or promo content above content already on screen. Font swaps that change metrics cause CLS:
prefer metric-matched fallbacks or `size-adjust` on the fallback.

**Main thread (INP).** Long tasks > 50ms are what users feel. Break them up, defer non-critical JS,
and prefer CSS for anything the compositor can animate (`transform`, `opacity`).

**Transfer size.** Justify every framework byte on a marketing page. An image budget is set per slot
(hero <= 200KB, card <= 60KB) and enforced at build. AVIF/WebP with explicit sizes, and a real
`srcset` rather than a 3000px image scaled to 300px.

## Corpus evidence

- Flux Academy / Learn Web Design For Beginners - Full Course / j6Ule7GXaRs / [1:57:42] / "font files into your website slows down"
- Flux Academy / Build a custom website with no code! (Relume & Webflow) / 8bm1Pl5ecEI / [53:01] / "should have compressed the images before"
- Flux Academy / Build a custom website with no code! (Relume & Webflow) / 8bm1Pl5ecEI / [53:18] / "compress them for me and turn them into"

The corpus directly supports the two claims that matter most here: font payload slows the site, and
images must be compressed before delivery. The numeric budgets (2.5s / 0.1 / 200ms, the per-slot image
budgets) are `UNVERIFIED` against this corpus: they come from Core Web Vitals and internal practice.

## Anti-patterns

- Moving LCP by lazy-loading the hero so something else wins.
- Preloading every font weight and the whole icon set.
- Reporting a Lighthouse score from an unthrottled local run as if it were field data.
- Buying a performance plugin instead of deleting 200KB of unused JS.
- Claiming a win with no before number.

## Links

parent: when-designing-websites
children: none (sub-skill of web-build-ship)
