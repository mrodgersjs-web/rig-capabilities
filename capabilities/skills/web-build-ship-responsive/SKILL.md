---
name: web-build-ship-responsive
description: Make one design hold its intent across phone, tablet, laptop and wide desktop. Reflow order, fluid type and space, touch targets, and overflow assertion. Use when a page breaks, crowds or wastes space at some width.
outcome: One layout that reads as the same design at 390px and 1536px, with an assertion that nothing overflows.
done_when:
  - scrollWidth <= clientWidth holds at 390, 768, 1280 and 1536 (asserted by a check, not by eye)
  - the rendered reflow order equals the written reflow order
  - every interactive target measures at least 44x44px with at least 8px separation
  - body text measure stays between 45ch and 75ch at every width
great_example: examples/great/design-ux/web-build-ship-responsive.md
quality_floor: No responsive claim without having rendered the four widths. No media query whose purpose cannot be stated in one line. No overflow solved by hiding content.
activation: Load when a layout is being built responsively, when the user says "mobile", "it breaks on phone", "it looks cramped", or as the first gate of web-build-ship.
instruction: >
  Establish reflow order before writing media queries. Use fluid type and space with clamp() so
  breakpoints correct intent rather than fight pixels. Assert no horizontal overflow at every
  width. Never hide content to solve overflow: that is a content or hierarchy failure.
applies_when:
  env: browser (local dev server or static preview)
  runtime: static HTML/CSS/JS or SSR web page rendered in a viewport
  deps: none beyond the page's own CSS and JS
  params: viewport widths 390px, 768px, 1280px, 1536px
  budget: one layout system and one fluid scale for the whole surface, no per-page overrides
  scale: single page up to a full marketing site
permissions:
  - fs.read
  - fs.write
  - browser.read
flow:
  - Write the reflow order in one line (e.g. hero > proof > features 2-col > CTA stacks).
  - Set a fluid type scale with clamp() and a fluid space scale.
  - Build single-column first, then add columns where the content genuinely has columns.
  - Render 390 / 768 / 1280 / 1536 and note what moved, what stacked, what re-scaled.
  - Assert zero horizontal overflow at each width.
  - Check every interactive target >= 44px and body measure 45-75 characters at every width.
out_of_scope:
  - native mobile app layout
  - email HTML layout
  - print stylesheets
---
# Responsive

One design, four widths, same intent.

## Method

**Reflow order first.** Before a single media query, write the priority order of the page in one line.
Every breakpoint decision then answers "does this preserve the order?" instead of "does this fit?".

**Fluid before fixed.** Prefer continuous scaling over breakpoint jumps for type and space:

```
--step-0: clamp(1rem,      0.94rem + 0.30vw, 1.125rem);   /* body */
--step-2: clamp(1.5rem,    1.25rem + 1.25vw, 2.25rem);    /* h3 */
--step-4: clamp(2.25rem,   1.55rem + 3.5vw,  4.5rem);     /* display */
--space:  clamp(1rem,      0.8rem  + 1vw,    2rem);       /* gutter */
```

Use a type ratio (1.25 content, 1.333 marketing) and derive steps from it. Body measure 45-75ch:
wider is measurably harder to read.

**Breakpoints correct intent, they do not create it.** If a breakpoint exists only to make something
fit, the component is wrong. Typical intervention points: 640 (nav collapses), 768 (1-col to 2-col),
1024 (2-col to 3-col, hero gains its second column), 1280 (container caps, whitespace grows).

**Touch and hit area.** Interactive targets >= 44x44px with >= 8px separation. Hover-only affordances
are invisible on touch: always pair with a persistent visual state.

**Overflow is asserted.** `document.scrollingElement.scrollWidth <= document.documentElement.clientWidth`
at each width. Any failure names the offending element.

## Corpus evidence

- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [05:00] / "fully responsive so basically I'm done"
- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [05:20] / "responsive um and that is great is this"
- Flux Academy / Learn Web Design For Beginners - Full Course / j6Ule7GXaRs / [25:22] / "responsive layouts but each screen size"

Corpus coverage here is **thin at authoring time**. The specific clamp() values, the 1.25/1.333 ratios,
the 45-75ch measure and the 44px target are `UNVERIFIED` against this corpus. The 45-75ch measure and
44px target are drawn from established readability and touch-guidance practice, not from a
recommendation in these videos. Treat them as the floor, and re-derive from the corpus once more
transcripts land.

## Anti-patterns

- Media queries that exist only to make a too-wide element fit.
- `display: none` on content to fix overflow.
- Designing at 1440px and "checking mobile" at the end.
- Fixed px type and space that ignores the fluid scale.
- Claiming responsive from a screenshot of one width.

## Links

parent: when-designing-websites
children: none (sub-skill of web-build-ship)
