---
name: web-color-contrast
description: Verify and fix colour contrast to WCAG floors with the ratios recorded. Use when text is hard to read, when auditing accessibility, or before any ship.
outcome: A contrast audit with a measured ratio for every used pair, and all failures fixed at the token.
done_when:
  - every used pair has a recorded ratio
  - every pair meets 4.5:1 for body, 3:1 for large text and UI, 3:1 for non-text
  - every fix is recorded with its before and after ratio
  - zero legibility fixes were made with shadow, stroke or outline
great_example: examples/great/design-ux/web-color-contrast.md
quality_floor: Any pair below its floor fails this skill. A fix applied with shadow, stroke or outline fails this skill.
activation: Load inside web-build-ship, when the user says "I can't read this", "contrast", "WCAG", or whenever a palette is turned into UI.
instruction: Measure every text and UI pair and record the ratio against its floor. Fix by moving the hue or the token role, never by adding a shadow or a stroke to fake legibility.
applies_when:
  env: browser rendering coloured text or UI
  runtime: any web surface
  deps: web-color, web-build-ship
  params: floors are 4.5:1 body, 3:1 large text and UI, 3:1 non-text
  budget: every pair measured once per theme and recorded
  scale: one page to a full site
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Enumerate every text-on-background and UI-on-background pair actually used.
  - Compute the contrast ratio for each pair in both themes.
  - Compare each ratio to its floor and list every failure with its ratio.
  - Fix failures at the token role or the hue.
  - Re-measure and record the before and after ratios.
out_of_scope:
  - colour choices and palette construction (web-color)
  - non-colour accessibility such as keyboard and screen-reader flow (a11y-auditor)
  - print contrast
---
# Colour: Contrast

Every pair measured. Fixed at the token, never faked.

## Method

**Floors.** Body text 4.5:1. Large text (24px, or 18.7px bold) and UI components and graphical
objects 3:1. These are external standards, labelled as such rather than claimed from the corpus.

**Enumerate the pairs actually used.** Not every possible combination, the ones rendered. Include
hover and disabled states, since those are where failures hide.

**Fix at the role.** If `muted` on `paper` fails, change `muted`. Adding a drop shadow to make text
legible is a contrast failure with extra steps.

**Record ratios.** A claim of "AA compliant" without a table of ratios is an adjective.

## Corpus evidence

- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [14:29] / "have like a light mode and a dark mode"
- Flux Academy / Graphic Design Essentials: Free Course / SnxFkHqN1RA / [1:32:26] / "sort of color palettes that are going to"

The corpus discusses palette families and modes but not contrast ratios. Every floor and the fix-at-
the-token rule are UNVERIFIED against this corpus and are drawn from the WCAG standard.

## Anti-patterns

- Claiming AA with no ratio table.
- Fixing legibility with shadow, stroke or outline.
- Auditing only the default state and skipping hover and disabled.
- Measuring light mode and assuming dark passes.
- Rounding 4.49 up to a pass.

## Links

parent: when-designing-websites
children: none (sub-skill of web-color)
