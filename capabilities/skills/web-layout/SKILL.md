---
name: "web-layout"
description: "Compose page structure and visual hierarchy so the eye lands where the work needs it: use when starting, rebuilding or rescuing any web page composition."
outcome: "A hierarchy-locked page composition: a declared reading order, one focal element per viewport, and a wireframe the built page matches."
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-layout/SKILL.md
  - observable: at every breakpoint the blur-to-illegibility squint test shows one dominant element
  - observable: the declared reading path ends at the primary action
  - observable: no two elements occupy the top emphasis slot
great_example: examples/great/design-ux/web-layout.md
quality_floor: "One dominant element per viewport and a stated reading order. Three elements tied for emphasis, or a composition with no focal point, fails the job."
activation: "Load when a page, section or hero needs composition and hierarchy: a new build, a redesign critique, a page that reads flat, busy, or generic, or before any grid or motion work begins."
instruction: "Decide the reading order before the pixels. Give every viewport exactly one dominant element, one supporting tier, and quiet matter beneath it, and spend size, weight, contrast and space on that order only. Declare the reading path in a wireframe, build the page to it, then cut or demote anything that ties for first place."
applies_when:
  env: "designer or developer workstation with the project open locally"
  runtime: "HTML and CSS page or site builder canvas producing a web page"
  deps: "copy deck, brand tokens and a wireframe surface"
  params: "content order and emphasis still movable; widths 360 to 1920px"
  budget: "1 focal element and 3 emphasis tiers per viewport"
  scale: "one page or long scroll at a time, up to 12 sections"
permissions:
  - Read the brief, copy deck, brand tokens, and the target codebase or design file
  - Write layout artifacts and code inside the named project only
  - Bash for screenshot capture and file reads only
  - Outward, deploy, paid or public actions (publishing, deploys, paid assets) need Gate-D approval from Mike before they run
flow:
  - List every element the viewport must carry and rank it by job
  - Choose one focal element and set its size ratio over the next tier
  - Declare the reading path (Z for image-led heroes, F for text-dense pages) and confirm it ends at the primary action
  - Build the type and space hierarchy in wireframe and squint-test it
  - Fill real copy and re-run the squint test at every breakpoint
  - Cut or demote anything tied for first place, then hand the locked hierarchy to web-layout-grid
out_of_scope:
  - Grid arithmetic, spacing scale and reflow (see web-layout-grid)
  - Editorial whitespace voice and asymmetry (see web-layout-editorial)
  - Animation and scroll behavior (see web-motion, web-motion-narrative, web-motion-budget)
  - Copywriting, brand identity and image selection
  - Native app chrome, print spreads and logo marks
---
# Web Layout: composition and hierarchy

## Method

Hierarchy is arithmetic before it is taste. Rank every element on the screen by the job it does for
the reader, then pay for that ranking with exactly three emphasis tiers: one dominant element, one
supporting tier of two to four elements, and quiet matter. Anything in the quiet tier that still
shouts is a bug, not a style.

The emphasis ladder, strongest first: size, weight, contrast, space, position. Climb one rung at a
time. When you raise an element one tier, change one ladder variable, not three, or the tiers smear
together and the reader gets a wall of loud.

Working rules:

- One focal point per viewport. Not one per section: one per screenful, at any width.
- Size ratio between tiers at least 1.25 for interface type and 1.618 or more for display type.
  If the dominant element and its support read at similar sizes, the page has no hierarchy.
- Contrast peaks on the focal element. Body text holds at least 4.5:1 against its background; the
  focal element gets the page's strongest contrast or its only saturated color, never both from
  five different elements.
- Grouping is spacing. The gap inside a group is half to two thirds of the gap between groups. Equal
  gaps read as unrelated matter, and the reading path dies.
- Declare the reading path before building: Z for image-led heroes (headline top-left, image right,
  CTA at the return stroke), F for text-dense pages. The path must end at the action the page wants.
- Reserve the highest position in the visual order for the job, not the ego. The logo is quiet
  matter on every screen except the one where identity is the job.
- Section rhythm anchors hierarchy between screens: 96 to 128px between sections on desktop, 64 to
  80px on mobile, and the dominant section always gets the larger end of that band.

Tests while you work:

- Squint test: blur the screen to illegibility. One block must still read first. If three do, demote.
- Grayscale test: remove color. The order must survive, because color is the last rung of the ladder.
- Path trace: name the sequence of elements the eye visits out loud. If the CTA is not in it, the
  composition is decorative.
- Copy swap test: swap the headline for a competitor's. If the layout still works, it has no
  hierarchy of its own.

Numbers in this Method are studio doctrine and declared standards of this skill, not corpus
findings: corpus coverage of numeric layout specs is thin at authoring time, and auto-captions
mishear numbers, so every number here is UNVERIFIED against the corpus until checked against a
primary source.

## Corpus evidence

Format: channel / video title / videoId / [MM:SS] / quote. Every row below was read back from the
named transcript file at the named timestamp line.

- self-made-web-designer / The Only 5 Web Design Skills That Actually Matter (2026) / vbFn0C-pvis / [05:03] / "and even vertical spacing, and then visual hierarchy to guide the eye."
- self-made-web-designer / How to Be A Web Designer in 2026 (Free Resources & My Best Advice) / vYvzOyTA2z4 / [16:47] / "And this is where visual hierarchy does most of the heavy lifting,"
- self-made-web-designer / How to Be A Web Designer in 2026 (Free Resources & My Best Advice) / vYvzOyTA2z4 / [16:51] / "visual hierarchy is how you guide someone's attention with things"
- self-made-web-designer / 11 years of web design knowledge in 7 minutes / ityZtG3FMgw / [00:57] / "You use something called visual hierarchy."
- flux-academy / How to start a website layout (for complete beginners) / 5STsDYbu6Tg / [05:46] / "clear focal point there isn't a place"
- self-made-web-designer / Ultimate Website Layout Guide: 17 Swipeable Examples (Video 2) / s2DVOZ62F8w / [00:55] / "attention and keep users engaged, and that's visual hierarchy variation."

Corpus coverage is real: 659 hierarchy rows measured across the 2,399 timestamped transcripts at
authoring time, with this sample skewed to self-made-web-designer and flux-academy. The tier ratios,
contrast ratios and squint test above are studio doctrine, UNVERIFIED against the corpus at
authoring time.

## Anti-patterns

- Three-way tie: headline, badge and CTA all sitting at peak contrast, so nothing wins.
- Loudness as hierarchy: fixing emphasis with color or motion instead of size and space.
- Bottomless hero: a 100vh hero that pushes proof and the next section out of the first screen.
- Centered coma: every block centered, so the eye has no path toward the action.
- Whack-a-mole demotion: demoting one loud element only to create the next three-way tie.

## Links

parent: when-designing-websites
children: web-layout-grid, web-layout-editorial
