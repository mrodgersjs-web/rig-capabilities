---
name: "web-layout-grid"
description: "Set the grid, spacing scale, density and responsive reflow so a page holds together at every width: use for columns, gutters, vertical rhythm, measure and breakpoints."
outcome: "A tokenized spacing scale, a breakpoint and column table, and a layout proven to reflow at 360, 768, 1024 and 1440 pixels."
done_when:
  - cmd:python3 -m rig_capabilities.skill_contract capabilities/skills/web-layout-grid/SKILL.md
  - observable: every gap and padding resolves to a scale value, with no arbitrary pixel literals outside the token file
  - observable: the column count matches the declared breakpoint table at each width
  - observable: body measure lands between 45 and 75 characters
  - observable: screenshots at 360, 768, 1024 and 1440 show no overflow and no orphaned column
great_example: examples/great/design-ux/web-layout-grid.md
quality_floor: "No dimension outside the declared scale, one column count per breakpoint, and a reflow proven at 360 and 1440. A magic-number gap, or a desktop design merely scaled down, fails the job."
activation: "Load when a layout needs its underlying system: choosing columns and gutters, fixing ragged or inconsistent spacing, defining breakpoints, setting content width and line measure, or reflowing a desktop design to tablet and mobile."
instruction: "Put every dimension on one spacing scale and one column count per breakpoint before styling anything. Choose the grid from the content's measure rather than from habit, and reflow by re-deciding the layout at each width instead of scaling the desktop down. Reject any value that is not on the scale, and prove the reflow with screenshots at each named breakpoint."
applies_when:
  env: "designer or developer workstation with tokens under version control"
  runtime: "CSS Grid, Flexbox or a builder column model producing a responsive web page"
  deps: "a token file, the content deck and screenshot tooling for 4 widths"
  params: "content must survive 360px to 1920px; body measure 45 to 75 characters"
  budget: "1 spacing scale, 1 column count per breakpoint, 1 density per page"
  scale: "one page or template at a time, up to 12 sections and 4 breakpoints"
permissions:
  - Read the design file, design tokens and page code
  - Write CSS, layout components and one spacing token file in the named project
  - Bash for screenshot capture and stylesheet greps only
  - Outward, deploy, paid or public actions (publishing, deploys, paid assets) need Gate-D approval from Mike before they run
flow:
  - Set the base unit and publish the spacing scale as tokens
  - Declare the breakpoint table with a column count and gutter per breakpoint
  - Set max content width and the body measure target
  - Assign every gap and padding a scale value and every block a column span
  - Reflow each breakpoint as its own layout, stacking in reading order
  - Verify with screenshots at 360, 768, 1024 and 1440 and fix every overflow and orphan
out_of_scope:
  - Hierarchy and focal decisions (see web-layout)
  - Editorial voice and asymmetry (see web-layout-editorial)
  - Motion and animation (see web-motion family)
  - Color and typeface selection, and copywriting
  - Fixed-canvas posters, native app layouts and self-scrolling data grids
---
# Web Layout Grid: system, spacing, density, reflow

## Method

A grid is a promise that the same relationship repeats. Break the promise once and the page reads as
sloppy; break it with intent and it belongs to web-layout-editorial. This skill keeps the promise.

Spacing scale:

- Base unit 8px, with a 4px sub-unit allowed only inside dense controls (inputs, chips, table cells).
- Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Roughly 1.5x steps at the top end so large gaps
  stay distinguishable. If you need 20px, you are telling yourself the answer is 16 or 24.
- Vertical rhythm on the same scale: sections at 96 to 128px on desktop, 64 to 80px on mobile.
- Grouping ratio: the gap inside a group is half to two thirds of the gap between groups. Adjacent
  label-to-field pairs at 8px with 24px between fields is the canonical example.
- Density is one setting per page, applied as a multiplier to vertical spacing only: comfortable
  1.0, standard 0.75, compact 0.5. Never mix densities between sections.

Column model:

- Desktop: 12 columns, 24px gutters, 32 to 48px page margins, max content width 1120 to 1280px.
- Tablet: 8 columns, 20px gutters, 24 to 32px margins.
- Mobile: 4 columns, 16px gutters and margins.
- Column counts per breakpoint come from the corpus tradition this skill adopts (see evidence), and
  the exact gutter numbers are studio doctrine, UNVERIFIED against the corpus at authoring time.
- Measure (line length) is the reason the grid exists: 45 to 75 characters, target 60 to 70. Long
  measures kill reading; narrow measures shred rhythm. Set the content column from the measure
  first, then divide it into columns.

Breakpoints and reflow:

- Breakpoints fire where the content fails, not where a phone model lives. Defaults: 640, 768,
  1024, 1280, 1440 (UNVERIFIED - studio doctrine, adjust to where the composition breaks).
- Reflow is a new decision at each width: re-rank what stacks first, keep reading order in the DOM,
  and collapse 12 to 8 to 4 columns rather than shrinking spans.
- Body type never drops below 16px to solve overflow. Tap targets never below 44x44px.
- Gutters compress before margins do: 24 to 20 to 16. Never let gutters fall below 12px.

Numbers in this Method are studio doctrine and declared standards of this skill unless a corpus row
below says otherwise: numeric coverage in the corpus is thin at authoring time and auto-captions
mishear numbers, so each is UNVERIFIED against the corpus until checked against a primary source.

## Corpus evidence

Format: channel / video title / videoId / [MM:SS] / quote.

- self-made-web-designer / Master Website Layouts in Under 10 Minutes (Video 1) / EF_ucfA3CJs / [03:12] / "That's why most responsive design systems start with a 12 column."
- self-made-web-designer / Master Website Layouts in Under 10 Minutes (Video 1) / EF_ucfA3CJs / [03:54] / "12 columns gives you flexibility, but as you scan down or go to"
- self-made-web-designer / 50 Web Design Tips & Tricks to Level Up Instantly / rRFD6tENX2U / [02:45] / "Most websites use a 12 column grid system and that helps to keep things."
- self-made-web-designer / The Only 5 Web Design Skills That Actually Matter (2026) / vbFn0C-pvis / [05:15] / "Eight columns on tablets and then four columns on mobile."
- charlimarie-tv / How to convert a Figma design to Webflow / NqKcO-ejvxQ / [00:54] / "I've set up a 12 column grid and this"
- self-made-web-designer / This is boring but it'll get even beginner web designers more clients / syLf0ypxfQI / [03:48] / "your spacing is all uniform and divisible by a factor"

Corpus coverage for the 12-column and 8/4 reflow tradition is real: 2,319 grid rows, 1,288 spacing
rows and 1,279 responsive rows measured across the 2,399 timestamped transcripts at authoring time.
Exact numeric specs (scale values, gutters, breakpoint numbers) stay thin and are marked UNVERIFIED
above.

## Anti-patterns

- Magic-number gap: a 17px margin that exists nowhere else in the stylesheet.
- Device cosplay: breakpoints named after phones and chosen before the content actually fails.
- Squeeze-down reflow: the desktop grid scaled to fit mobile instead of re-decided at that width.
- Density flip: compact spacing in the hero and comfortable in the body on one page.
- Orphan column: a twelve-column layout whose last row leaves a single column stranded.

## Links

parent: when-designing-websites
children: none (leaf skill under web-layout)
