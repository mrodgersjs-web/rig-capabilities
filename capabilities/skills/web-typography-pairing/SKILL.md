---
name: web-typography-pairing
description: Pair typefaces by contrast of voice, pick variable or static, and load them without hurting performance. Use when choosing two fonts or when font loading is slowing the page.
outcome: A two-face pairing with a stated contrast of voice and a measured font budget.
done_when:
  - the pairing rests on a stated contrast of voice
  - total font payload is under 180KB and measured
  - at most two weights per family are loaded
  - the fallback is metric-matched so the swap does not move layout
great_example: examples/great/design-ux/web-typography-pairing.md
quality_floor: A pairing justified only by "they look nice together" fails this skill. A payload with no measured number fails this skill.
activation: Load when a second typeface is being chosen, when a page has one flat voice, or when the user says "these fonts don't work together" or "fonts are slowing the site".
instruction: Pair by contrast of voice, not by category labels. Keep it to two families and at most two weights each, subset to used glyphs, and load woff2 with font-display swap preloading only the display face.
applies_when:
  env: browser with webfont loading
  runtime: any page using self-hosted or hosted webfonts
  deps: web-typography, web-build-ship-performance
  params: two families max, two weights each max, one display face preloaded
  budget: under 180KB total font payload
  scale: one page to a full site
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Name the voice of the display face in one adjective.
  - Choose the text face by contrast against that adjective (austere against ornate, warm against technical).
  - Decide variable versus static: variable only when you will use more than two weights or need fluid axes.
  - Subset to used glyphs and convert to woff2.
  - Set font-display swap, preload only the display face, and metric-match the fallback.
  - Measure the payload and record it against the 180KB budget.
out_of_scope:
  - drawing or commissioning a custom face
  - licensing negotiation for a commercial foundry
  - variable font engineering (producing axes)
---
# Typography: Pairing

Contrast of voice, not category labels.

## Method

**Pair by voice contrast.** "A serif with a sans" is a category rule and produces the same page
everybody else ships. Name the adjective for the display face (ornate, austere, technical, warm) and
choose the text face as its counterweight.

**Two families, two weights.** Anything more needs a written justification.

**Variable only when earned.** Use a variable font when you need more than two weights or a fluid
axis such as optical size. Otherwise static woff2 subsets are smaller and simpler.

**Load like performance depends on it, because it does.** Subset to used glyphs, woff2,
`font-display: swap`, preload only the display face, and metric-match the fallback (`size-adjust`,
`ascent-override`) so the swap does not shift layout.

## Corpus evidence

- Flux Academy / We Redesigned Hacksmith! (StudioXperience Ep.) / 5rTKCrqxkrQ / [10:19] / "typography guidelines logo imagery"
- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [06:24] / "around with what fonts and typography"

The corpus has typography guidance but nothing on pairing method or font loading. The voice-contrast
rule and every loading and budget figure here are UNVERIFIED against this corpus.

## Anti-patterns

- Category pairing (serif plus sans) with no voice argument.
- Loading six weights to use two.
- Preloading every face in the stack.
- A fallback that shifts layout on swap.
- A variable font with one static weight actually used.

## Links

parent: when-designing-websites
children: none (sub-skill of web-typography)
