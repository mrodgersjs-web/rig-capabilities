---
name: web-design-critique-taste
description: The taste pass. Judge distinctiveness, restraint, coherence and craft detail, and name exactly where taste is being faked. Use inside web-design-critique or when a page is technically fine but forgettable.
outcome: A taste verdict that says which decisions carry the design and which defaults leaked in.
done_when:
  - all four axes return a named verdict with a located example or a located absence
  - at least one small craft detail was actually inspected and reported on by name
  - no verdict rests on an adjective without a location
great_example: examples/great/design-ux/web-design-critique-taste.md
quality_floor: Every axis carries a located example or a located absence. "Feels premium" with no location is a gate failure.
activation: Load inside web-design-critique, or when the user says "this is boring", "this looks generic", "make it more premium", "it feels flat".
instruction: >
  Taste is not preference: it is the visible evidence that someone made decisions and accepted their
  cost. Score four axes - distinctiveness, restraint, coherence, detail - and for each, name the
  decision that proves it or the missing decision that gives it away. A page can fail this while
  passing every automated check.
applies_when:
  env: any context holding a web artifact
  runtime: rendered page or mock judged in a browser
  deps: the artifact, and its design system when one is declared
  params: four axes (distinctiveness, restraint, coherence, detail), each returning a located verdict
  budget: one taste pass per artifact
  scale: single page up to a full marketing site
permissions:
  - fs.read
  - fs.write
  - browser.read
flow:
  - Distinctiveness: name three decisions this page makes that a default would not.
  - Restraint: name anything on the page that exists to impress rather than to serve the buyer.
  - Coherence: check type, color, radius, spacing and motion against one declared system.
  - Detail: inspect focus rings, hover states, empty states, error copy and the 404.
  - For each axis return the evidence or the absence as a named location.
  - Fold findings into web-design-critique as major or preference per the severity rules.
out_of_scope:
  - copy effectiveness (web-conversion-copy)
  - performance measurement
  - taste in non-web media
---
# Critique: Taste

The 5% that separates made from assembled.

## Method

**Taste is evidence of decisions, not decoration.** The test for any element: would a competent
default have produced exactly this? If yes, it is not carrying design. Three such elements in one
viewport is generic.

**Distinctiveness.** Name three decisions a default would not make. If you cannot, the page has no
point of view and that is the finding. Distinctiveness must still serve the buyer: a wild layout that
obscures the ask is `[preference]` at best.

**Restraint.** Count what exists to impress rather than to serve. Motion with no job, gradients with
no material, a hero video nobody asked for. Removing is usually the highest-leverage taste move.

**Coherence.** Everything comes from one declared system: type families and weights, a palette with
roles not hex adjectives, one radius scale, one spacing scale, one motion language. Drift shows up as
"the button looks different on page 3".

**Detail.** This is where taste is actually proven, because it costs effort with no reward:
- focus rings that look designed rather than browser-default
- hover and pressed states on every interactive element
- empty states, loading states, error copy, and the 404
- the last 20px of vertical rhythm on the page

## Corpus evidence

- charlimarieTV / Design projects & life updates - Work-with-me vlog! / iDXjxu2tJ80 / [04:26] / "marketing site stand out from others"
- charlimarieTV / Dropbox rebrand - LOVE it or HATE it? (Design News) / 48Sd42c1YPA / [07:38] / "So let's try to have a proper design critique"

Standing out from other sites is the corpus's stated goal for a marketing site. The four-axis frame
and the "would a default produce exactly this" test are RIG method, `UNVERIFIED` against this corpus.

## Anti-patterns

- Calling maximalism taste. Restraint is the harder and more often failed axis.
- Award-chasing motion that makes the ask harder to find.
- Coherence claimed while three components use three different radii.
- Judging taste with no evidence beyond "I like it".
- Treating the 404 and error states as out of scope. They are the tell.

## Links

parent: when-designing-websites
children: none (sub-skill of web-design-critique)
