---
name: web-typography-scale
description: Build a type scale, a fluid ramp and a readable measure. Use when setting type sizes, fixing hierarchy, or when a page's text feels flat or crowded.
outcome: A fluid type scale with a stated ratio and base, and a measure that holds across widths.
done_when:
  - every text size on the surface is a step of the declared scale
  - body measure stays between 45ch and 75ch at all four widths
  - the scale renders fluidly with no per-breakpoint size override
  - no emphasis relies on weight alone inside a broken scale
great_example: examples/great/design-ux/web-typography-scale.md
quality_floor: A hand-picked size that is not a scale step fails this skill. A measure outside 45-75ch fails this skill.
activation: Load when type sizes are being chosen, when headings have no relationship to body, or when the user says "the hierarchy is wrong" or "make the headings pop".
instruction: Derive every size from one ratio and one base. Use clamp() so the ramp is fluid. Earn emphasis with size and space before weight, and hold body measure at 45-75ch.
applies_when:
  env: browser at 390px to 1536px
  runtime: web page with live text
  deps: web-typography, the project's type tokens
  params: one base size, one ratio (1.25 content, 1.333 marketing), steps derived not hand-picked
  budget: one scale for the whole surface, no per-page size overrides
  scale: one page to a full site
permissions:
  - fs.read
  - fs.write
flow:
  - Pick the base body size at the real reading size (16-18px).
  - Pick the ratio: 1.25 for content-dense, 1.333 for marketing display.
  - Derive the steps from base and ratio; no hand-picked in-between sizes.
  - Convert steps to fluid clamp() values that interpolate across the viewport.
  - Set measure 45-75ch and check line-height at the real body size.
  - Verify hierarchy survives at 390px and at 1536px without a size override.
out_of_scope:
  - font selection and pairing (web-typography-pairing)
  - text in imagery
  - print type ramps
---
# Typography: Scale

One ratio, one base, no in-between sizes.

## Method

**Derive, do not pick.** Hand-picked sizes are how a page ends up with 17, 18, 20, 24 and 32 with
no relationship. Choose base and ratio and compute the steps.

**Fluid beats breakpoint jumps** for type:

```
--step-0: clamp(1rem,    0.94rem + 0.30vw, 1.125rem);   /* body   */
--step-2: clamp(1.5rem,  1.25rem + 1.25vw, 2.25rem);    /* h3     */
--step-4: clamp(2.25rem, 1.55rem + 3.5vw,  4.5rem);     /* display */
```

**Ratio by job.** 1.25 for content-dense pages where text carries the work. 1.333 and above for
marketing and display where the headline must dominate.

**Measure before size.** Body at 45-75ch. If the line is too long the fix is measure and column, not
a bigger font.

## Corpus evidence

- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [12:34] / "color and typography and the content"
- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [09:18] / "typography I still got a lot of time"

The corpus groups typography with colour and content as the set of decisions that make up the look.
The ratio values, the step derivations and the 45-75ch measure are UNVERIFIED against this corpus.

## Anti-patterns

- Sizes chosen one at a time with no scale.
- A breakpoint that only exists to shrink a heading.
- Bumping weight to fix a hierarchy problem.
- Body measure driven by the container width.
- A display step used at body size.

## Links

parent: when-designing-websites
children: none (sub-skill of web-typography)
