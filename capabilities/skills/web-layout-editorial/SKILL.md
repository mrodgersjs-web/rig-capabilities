---
name: "web-layout-editorial"
description: "Compose magazine-grade pages where whitespace and asymmetry carry the voice: use for editorial, portfolio, manifesto and long-form layouts that must feel art-directed."
outcome: "An art-directed page with a counted whitespace budget, one declared asymmetry per screen, editorial type contrast, and a reading rhythm that feels composed."
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-layout-editorial/SKILL.md
  - observable: whitespace measures 40 to 60 percent of the first two viewports
  - observable: exactly one alignment break exists per screen and it lands on a grid edge
  - observable: body copy holds 45 to 75 characters at 1.5 to 1.7 line height
  - observable: the spread reads art-directed rather than filled, and survives a copy swap
great_example: examples/great/design-ux/web-layout-editorial.md
quality_floor: "Whitespace is deliberate and counted, the one asymmetry per screen is aligned to the grid, and the page survives the copy-swap test so it reads art-directed with any text. Centered-everything or clutter-to-fill fails the job."
activation: "Load when a page must read like an art-directed spread rather than a template: editorial homepages, case studies, portfolios, manifestos and reports, or any layout called flat, templated, corporate or generic."
instruction: "Treat whitespace as the loudest element on the page and spend it deliberately, keeping 40 to 60 percent of the opening viewports intentionally empty. Break exactly one alignment per screen and land that break on a real grid edge so the asymmetry reads as a decision. Hold long-form measure and leading at reading standards, and let oversized type or one full-bleed image act as the page's art."
applies_when:
  env: "designer workstation with the copy deck and art direction in hand"
  runtime: "HTML and CSS editorial page, portfolio, case study or manifesto build"
  deps: "a real grid underneath, display and body typefaces, and the final copy length"
  params: "brand tone may be unconventional; content length varies page to page"
  budget: "40 to 60 percent intentional whitespace in the opening viewports, 1 alignment break per screen"
  scale: "one spread or one long scroll at a time, up to 10 screens"
permissions:
  - Read the copy deck, art direction notes and page code
  - Write layout code and type specimens in the named project
  - Bash for screenshot capture and measurement only
  - Outward, deploy, paid or public actions (publishing, deploys, paid fonts or assets) need Gate-D approval from Mike before they run
flow:
  - Lay the grid first, including the edges the break will align to
  - Name the page voice (quiet, bold, ceremonial) and choose one typographic contrast to carry it
  - Set the whitespace budget for the opening viewports and carve the voids before adding matter
  - Break exactly one alignment per screen and align the break to a grid edge
  - Build the type contrast: display against body, one drop cap or pull quote maximum per spread
  - Squint-test and copy-swap test, then hand the rhythm to web-layout-grid for implementation
out_of_scope:
  - Grid arithmetic and breakpoints (see web-layout-grid)
  - Motion and animation (see web-motion family)
  - Copywriting and voice strategy
  - Print layout, prepress and brand mark design
  - Forms, dashboards and checkout flows where convention earns its keep
---
# Web Layout Editorial: whitespace as voice

## Method

Whitespace is not what is left over. It is the element the reader feels first and reads last, so it
gets a budget and a place on the grid like anything else.

Voice and contrast:

- Pick one voice and pay for it. Quiet means type contrast at 1.5x between display and body with
  generous leading. Bold means 2.5x to 4x display-to-body contrast with tight display leading.
  Ceremonial means symmetry and centered axis, and that is the one mode where asymmetry is banned.
- Display type: leading 0.95 to 1.15, tracking -2 to 0 percent, size 48 to 96px desktop and 32 to
  48px mobile. Body: 18 to 21px at 1.5 to 1.7 line height, measure 45 to 75 characters.
- One typographic contrast per spread: display against body. A drop cap spans 3 to 4 body lines; a
  pull quote sits at 1.5 to 2x body size. Both at once is one too many.

Whitespace budget:

- 40 to 60 percent of the first two viewports intentionally empty. Count it: take the screenshot,
  mask the matter, and look at the ratio.
- Voids are placed, not leftover. A breathing gap runs at 2x the section rhythm, 192 to 256px on
  desktop, and it belongs next to the element that needs to feel important.
- Marginalia (folios, running heads, small notes) can carry a void: quiet matter at the edges keeps
  emptiness from reading as an unfinished page.

Asymmetry with intent:

- Break exactly one alignment per screen: one element off the text block, one full bleed, one
  hanging figure, or one oversized numeral. Two breaks per screen read as accident.
- Every break aligns to something real: a grid edge, the opposite margin, or the baseline of a
  neighbor. An element that aligns to nothing is noise dressed as style.
- Alternate full-bleed and inset at least every three screens to reset the eye, and let the break
  points carry the story beats.

Numbers in this Method are studio doctrine and declared standards of this skill: corpus coverage of
whitespace ratios and editorial type specs is thin at authoring time, and auto-captions mishear
numbers, so each is UNVERIFIED against the corpus until checked against a primary source.

## Corpus evidence

Format: channel / video title / videoId / [MM:SS] / quote.

- self-made-web-designer / The ONLY 6 Web Design Styles that Matter (2026) / N1Cl5cYmegE / [01:49] / "you can't be afraid of white space."
- self-made-web-designer / Steal These Web Design Trends 2026 / waHuVF3XuMA / [01:38] / "And of course, dial up the white space."
- self-made-web-designer / Steal These Web Design Trends 2026 / waHuVF3XuMA / [04:32] / "a scribble a, a rough icon, a little asymmetry"
- punit-chawla / Google's Biggest UX/UI Mistakes (Controversial) | That Looks Terrible - Episode 1 / tWgJfrkWX9o / [03:34] / "called asymmetrical following model. And"
- self-made-web-designer / The ONLY 6 Web Design Styles that Matter (2026) / N1Cl5cYmegE / [07:26] / "carry a high fashion editorial type feel."
- mike-locke / Web Typography Best Practices for Beginners / bIjzh_I8L0M / [07:01] / "I have a lot of space called White space"

Whitespace as a deliberate move has real corpus support: 1,251 whitespace and negative-space rows
measured across the 2,399 timestamped transcripts at authoring time. Asymmetry and editorial
phrasing is thinner at 165 rows and carries no numeric specs. The whitespace percentage, void and
type numbers above are studio doctrine, UNVERIFIED against the corpus at authoring time.

## Anti-patterns

- Centered coma: every block centered on the axis so whitespace happens by accident.
- Whitespace charity: emptiness left over at the bottom of a section instead of spent next to a focal.
- Asymmetry by accident: elements off-grid with nothing to align to, so the break reads as slippage.
- Template cosplay: a magazine grid carrying generic feature-card content, so the frame out-dresses it.
- Six voices: three type pairings and two grids arguing across one spread.

## Links

parent: when-designing-websites
children: none (leaf skill under web-layout)
