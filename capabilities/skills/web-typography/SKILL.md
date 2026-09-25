---
name: web-typography
description: Type craft for web. Choose and structure type so the page reads as decided rather than defaulted. Use on any page with text.
outcome: A type system with a stated reason, a derived scale, and a measured font budget.
done_when:
  - the reason sentence exists and names a material, period or voice
  - no default stack ships without that sentence
  - body measure sits between 45ch and 75ch at every breakpoint
  - total font payload is under 180KB and at most two weights per family load
great_example: examples/great/design-ux/web-typography.md
quality_floor: A page that ships Inter at four weights with no reason sentence fails this skill regardless of how it looks.
activation: Load for any page carrying text, when the user says "the type feels off", "pick a font", or when a page is being set from a blank canvas.
instruction: Choose type for a reason you can say in one sentence, then build a scale and a measure from it. Two families and two weights is the working set. Never ship a default stack with no declared reason.
applies_when:
  env: browser rendering web text
  runtime: static or dynamic web page with live text (not text baked into images)
  deps: web-typography-scale, web-typography-pairing, the project's type tokens
  params: one or two families, at most two weights each, a declared scale ratio
  budget: two woff2 families, subsetted, under 180KB total
  scale: single page up to a full site
permissions:
  - fs.read
  - fs.write
flow:
  - Write one sentence naming why this type belongs to this brand and buyer.
  - Pick the display face from that sentence, then the text face against it.
  - Set the scale via web-typography-scale and the pairing via web-typography-pairing.
  - Set measure to 45-75ch for body and check line-height at the real body size.
  - Load fonts subsetted with font-display swap and preload only the display face.
out_of_scope:
  - brand logo drawing and wordmark construction
  - type baked into imagery
  - print and packaging typography
---
# Web Typography

Type is the fastest signal that someone decided something.

## Method

**Reason before face.** "It looks clean" is not a reason. A reason names a material, a period or a
voice: an instrument panel, a 1970s editorial page, a technical datasheet. If the sentence cannot be
finished, the choice is still a default.

**Two families, two weights.** A display face and a text face. More weights are almost always a
symptom of solving hierarchy with weight instead of with size and space.

**Hierarchy comes from the scale, not from bold.** Build the scale first (`web-typography-scale`),
then earn emphasis with size, space and colour before reaching for weight.

**Measure is the reading contract.** 45-75ch for body. Wider is measurably harder to read and is the
single most common type failure on marketing pages.

## Corpus evidence

- Flux Academy / We Redesigned Hacksmith! (StudioXperience Ep.) / 5rTKCrqxkrQ / [10:19] / "typography guidelines logo imagery"
- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [06:24] / "around with what fonts and typography"
- Flux Academy / I built a portfolio in 1-hour, 10-hours, 100-hours! / yVaxwg6RYDw / [12:34] / "color and typography and the content"

The corpus treats typography as a named deliverable of a brand toolkit, alongside logo and imagery.
The reason-sentence rule, the two-family limit and the 45-75ch measure are UNVERIFIED against this
corpus.

## Anti-patterns

- A default sans with no declared reason.
- Four weights where two would do.
- Emphasis by bolding inside a broken scale.
- Body copy at 100ch+ because the container is wide.
- Substituting a display face for a text face at body size.

## Links

parent: when-designing-websites
children: web-typography-scale, web-typography-pairing
