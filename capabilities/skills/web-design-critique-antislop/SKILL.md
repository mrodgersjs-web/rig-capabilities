---
name: web-design-critique-antislop
description: Detect and strip AI-generated design tells. Fonts, palettes, layout cliches, empty superlatives and uncanny imagery. Use whenever a page, mock or copy is suspected of being generic AI output.
outcome: A surface that reads as deliberately designed rather than assembled, with each removed tell recorded.
done_when:
  - 'grep:capabilities/skills/web-design-critique-antislop/SKILL.md:[R]un the tell list before forming any quality opinion'
  - 'grep:capabilities/skills/web-design-critique-antislop/SKILL.md:[C]opy tells'
  - all five tell categories are either explicitly clear or reported as a located finding
  - every finding carries a concrete replacement, not just a rejection
  - the copy contains zero empty superlatives
  - a zero-finding verdict is supported by an explicit record that all five categories were checked
great_example: examples/great/design-ux/web-design-critique-antislop.md
quality_floor: A zero-finding verdict must be supported by having actually checked each of the five tell categories. Claiming "no slop" without running the checklist is a gate failure.
activation: Load inside web-design-critique, or when the user says "this looks like AI", "AI slop", "de-slop this", "this is generic", or when a surface was produced by a generative tool.
instruction: >
  Enumerate the tells mechanically before judging quality: banned default fonts, the purple-blue
  gradient palette, symmetric card grids, emoji in headings, uncanny generated faces, and empty
  superlatives in copy. Each tell found becomes a located finding with a concrete replacement.
  Detection is not the deliverable: the replacement is.
applies_when:
  env: any context holding web copy or a web surface
  runtime: live page, mock, or draft copy destined for a page
  deps: the copy and the surface under review
  params: five tell categories (type, color, layout, copy, imagery), each either clear or a located finding
  budget: one de-slop pass per artifact, with a re-check after each replacement
  scale: single component up to a full site
permissions:
  - fs.read
  - fs.write
  - browser.read
  - gate-d-required:publish
flow:
  - Type check: is the type stack a default (Inter, Roboto, system sans) with no declared reason.
  - Color check: purple-blue gradient, glassmorphism by default, or a palette with no role names.
  - Layout check: three equal feature cards with an emoji or generic icon on top, everything centered.
  - Copy check: empty superlatives, no named buyer, no numbers and no mechanism.
  - Imagery check: uncanny generated people, mismatched lighting, stock-like handshakes.
  - For each tell name it, locate it, propose the replacement, and re-check after the fix.
out_of_scope:
  - judging whether generative tools should be used at all
  - original brand identity design
---
# Critique: Anti-Slop

Mechanical detection, then a real replacement.

## Method

**Run the tell list before forming any quality opinion.** The value is in enumeration being
exhaustive, not in taste. A human can be charmed by a polished generic page; the checklist cannot.

**Type tells.** Inter / Roboto / system sans as the only face with no declared aesthetic direction. A
default stack is not a decision. Fix: choose a face for a reason (a period, a material, a voice) and
declare that reason in one sentence. If the sentence cannot be finished, the choice is still a default.

**Color tells.** The purple-to-blue gradient. Glassmorphism with no material logic. A palette named by
hex rather than by role (ink, paper, accent, warn). Fix: name roles, then pick hues.

**Layout tells.** Three equal feature cards topped with an emoji or a generic icon. Everything centered.
Equal weight given to everything (which is the same as no hierarchy). Fix: declare the priority order
and let the layout carry it asymmetrically.

**Copy tells.** Empty superlatives and their family: unlock, empower, seamless, revolutionize,
cutting-edge, robust, leverage, synergy. No named buyer. No numbers, no mechanism, no proof. Fix: use
the buyer's own words and one real number with its source.

**Imagery tells.** Uncanny generated faces (hands, ears, teeth), lighting that disagrees across a
composite, stock-like handshakes, and AI faces standing in for real customers. Fix: use typography or
real, licensed, provenance-tracked assets (`web-imagery-provenance`).

## Corpus evidence

- charlimarieTV / Design projects & life updates - Work-with-me vlog! / iDXjxu2tJ80 / [04:26] / "marketing site stand out from others"
- charlimarieTV / Dropbox rebrand - LOVE it or HATE it? (Design News) / 48Sd42c1YPA / [07:37] / "rather than a proper design critique."

Standing out is the stated goal of a marketing site, and a proper critique is explicitly contrasted
with a reaction - both support a checklist over a vibe. The specific tell list (fonts, gradient, card
grid, superlatives) is RIG method, `UNVERIFIED` against this corpus.

## Anti-patterns

- Declaring "no slop" without running all five categories.
- Removing a tell and leaving a different default in its place.
- De-slopping the copy while the layout is still three equal cards.
- Treating generative tools as the flaw. The flaw is an unexamined default.
- Softening a tell into "[preference]" when it is the actual reason the page reads as generic.

## Links

parent: when-designing-websites
children: none (sub-skill of web-design-critique)
