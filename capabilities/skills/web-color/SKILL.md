---
name: web-color
description: Colour craft for web. Build palettes with roles, hold contrast, and keep hue discipline. Use on any page with colour or when a page feels off in colour.
outcome: A role-based palette resolved for light and dark, with every contrast ratio measured.
done_when:
  - every colour on the surface resolves to a named role
  - the brand's banned hues appear nowhere
  - light and dark both resolve from the same role names
  - every text and UI pair passes its contrast floor with the ratio recorded
great_example: examples/great/design-ux/web-color.md
quality_floor: A palette named by hex with no roles fails this skill. A pair below its contrast floor fails this skill even if it looks right.
activation: Load for any surface with colour, when the user says "the colours are wrong", "make a palette", "dark mode", or when a brand palette has to become UI.
instruction: Name roles before picking hues. Build one palette that serves the buyer and the brand's banned hues, verify every pair against contrast floors, and never choose a palette by vibe.
applies_when:
  env: browser rendering colour
  runtime: any web surface with a colour system
  deps: web-color-tokens, web-color-contrast, brand docs for banned hues
  params: one palette with named roles, light and dark resolved from the same roles
  budget: one palette, role names not hex adjectives
  scale: one page to a full site
permissions:
  - fs.read
  - fs.write
flow:
  - List the roles the surface needs (ink, paper, accent, muted, warn) before any hue.
  - Pick hues against the brand's declared palette and its banned hues.
  - Resolve the roles for dark mode from the same role names, not a second palette.
  - Verify every text/background pair against the contrast floor (web-color-contrast).
  - Record the palette as tokens with role names.
out_of_scope:
  - logo and brand identity colour creation
  - photographic colour grading
  - print and physical colour matching
---
# Web Colour

Roles before hues. Ratios before opinions.

## Method

**Roles first.** A palette named by hex is not a system. Name the jobs (ink, paper, accent, muted,
warn) and then assign hues. That is what makes dark mode a resolution rather than a second design.

**Hue discipline.** Honour the brand's banned hues. If the brand bans teal and blue, a blue-grey
"neutral" is a violation, not a compromise.

**Contrast is measured, not felt.** Body text 4.5:1 minimum, large text and UI 3:1. Every pair gets a
number (`web-color-contrast`).

**Dark is a resolution, not a repaint.** Invert paper and ink within the same roles and re-check
contrast; accent hues usually need a lighter tint in dark.

## Corpus evidence

- Flux Academy / We Redesigned Hacksmith! (StudioXperience Ep.) / 5rTKCrqxkrQ / [10:18] / "brand toolkit with a color palette"
- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [14:29] / "have like a light mode and a dark mode"
- Flux Academy / Graphic Design Essentials: Free Course / SnxFkHqN1RA / [1:38:26] / "of um it's an analogous color palette"

The corpus supports the palette as a brand-toolkit deliverable, light and dark as a real pair of
modes, and named palette families (analogous). The role-first method and the contrast floors are
UNVERIFIED against this corpus.

## Anti-patterns

- A palette of hex values with no role names.
- Dark mode built as a separate design.
- A banned hue smuggled in as a neutral.
- Contrast judged by eye.
- Gradients standing in for a palette.

## Links

parent: when-designing-websites
children: web-color-tokens, web-color-contrast
