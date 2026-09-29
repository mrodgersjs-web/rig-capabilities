---
name: ds-layout
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for layout and composition: Set the grid, spacing scale, hierarchy and section composition for every breakpoint. 60 laws, 25
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the task names grids, spacing, section composition, hierarchy or responsive behaviour.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides layout and composition. Entered by the /design-studio command through design-studio-os, by ds-ui-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: layout.md: grid (12/8/4 by breakpoint), spacing scale, section order with hierarchy reasoning, wireframe or layout notes per breakpoint, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-layout/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# Layout and composition

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches layout and composition. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-ui-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "layout", "grid", "spacing", "hierarchy", "sections", "responsive". Inside a build this stage runs after the stage that feeds it and
before ds-ui-system, ds-conversion-copy.

## Inputs and output contract

Inputs: the page content list and priority, the type scale and palette from earlier stages.
Output: layout.md: grid (12/8/4 by breakpoint), spacing scale, section order with hierarchy reasoning, wireframe or layout notes per breakpoint.

## Procedure

1. Layout space and grouping: empty space, proximity, one focal point, edit-before-decorate. Owns 1, 2, 3, 7, 10, 11, 12 (see references/layout-space-and-grouping.md).
2. Layout spacing scale: 8 px base, inside vs between, outside-in steps, 6 px floor. Owns 25, 26, 27, 28, 29, 30 (see references/layout-spacing-scale.md).
3. Layout web hierarchy: scan order, measure, bullets, button contrast, squint test, subordinate ornaments. Owns 13, 14, 15, 16, 17, 18, 19, 23, 24 (see references/layout-web-hierarchy.md).
4. Layout grid pick: baseline, 12-column web, section column cap, column, modular, bento spans, fractional tracks, manuscript, hierarchy, asymmetric, square, thirds, compound, print margins, booklet mirror and rest spreads. Owns 31-40, 48-53, 58-60, plus the print rows in Tool-specific (see references/layout-grid-pick.md).
5. Layout auto layout: nested groups, hug/fixed/fill, pins, wrap gaps, responsive rows, phone stack. Owns 44-47, 56, 57, plus the Figma rows in Tool-specific (see references/layout-auto-layout.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Treat empty space as a layout material: use it to separate sections, define zones, and keep the page readable. Audit the gaps as carefully as the marks. Use more of it than the first draft suggests. | Satori Graphics, Jesse Showalter, Flux Academy, Self-Made Web Designer | CLAIM(EFf9jBs2yfU@00:20, EFf9jBs2yfU@02:09, cf95Z7Ngg8k@02:49, 9eJYjNGeIOM@02:30, rRFD6tENX2U@03:31, rRFD6tENX2U@03:34) | consensus |
| 3 | Group items that share a job, and give a call to action its own pocket of space. Do not glue unrelated items into one cluster, and do not space related items so far apart that the relationship dies. | Satori Graphics, Flux Academy, Jesse Showalter | CLAIM(EFf9jBs2yfU@02:43, EFf9jBs2yfU@03:45, 9eJYjNGeIOM@02:00, cf95Z7Ngg8k@02:52) | consensus |
| 5 | Build contrast on purpose with color, weight, shape, or size so one element becomes the focal point. A thicker word against a thinner word, a circle against straight edges, or a tilted photo against level rules all count. | Satori Graphics, Flux Academy | CLAIM(EFf9jBs2yfU@05:51, EFf9jBs2yfU@06:02, 9eJYjNGeIOM@03:02) | consensus |
| 7 | Place one focal point that starts the viewing path. Make the key image the largest and most contrasted object, the headline medium, and the supporting information small. A field of medium-sized, medium-contrast objects has no entry. | Satori Graphics, Flux Academy, Self-Made Web Designer | CLAIM(EFf9jBs2yfU@09:14, EFf9jBs2yfU@10:21, 9eJYjNGeIOM@03:08, 9eJYjNGeIOM@03:19, 1NTKwpAVcHg@01:26) | consensus |
| 25 | Pick one spacing base and use it for gaps, radii, and type sizes. An 8 px grid is the default in this corpus. A column grid places objects; it does not tell you the gap. | Self-Made Web Designer, Jesse Showalter | CLAIM(TeMtV8BaZt0@03:44, TeMtV8BaZt0@03:55, cf95Z7Ngg8k@00:23, cf95Z7Ngg8k@01:12) | consensus |
| 30 | A heading belongs closer to the cards it names than to the label of the previous section. That gap difference is how the group is read. | Jesse Showalter, Self-Made Web Designer | CLAIM(cf95Z7Ngg8k@08:09, cf95Z7Ngg8k@05:52, TeMtV8BaZt0@04:03) | consensus |
| 36 | Start proportions, including a type scale, from the golden ratio (about 1 to 1.618), then adjust. Do not lock a logo, a layout, or the next size up to the ratio if the result feels wrong. | Satori Graphics, Self-Made Web Designer | CLAIM(gUzkRue28VI@03:17, gUzkRue28VI@03:37, rRFD6tENX2U@05:46, rRFD6tENX2U@06:14) | consensus |
| 39 | Place key subjects on a rule-of-thirds grid for the first layout, including a crop of a face, a product, or a detail, then shift the subject off an intersection when you want tension. | Satori Graphics, Self-Made Web Designer | CLAIM(gUzkRue28VI@05:33, gUzkRue28VI@05:44, rRFD6tENX2U@09:39, rRFD6tENX2U@09:42) | consensus |
| 2 | Do not rescue a sparse layout by enlarging type or pouring a texture into the empty half. Leave a clear split between zones and keep the mark small so it does not compete. | Satori Graphics | CLAIM(EFf9jBs2yfU@00:43, EFf9jBs2yfU@01:17) | single-source |
| 4 | Repeat one color set, one illustration style, and one type family across the piece. Do not drop a gradient or a 3D render into a flat system. | Satori Graphics | CLAIM(EFf9jBs2yfU@04:22, EFf9jBs2yfU@05:12, EFf9jBs2yfU@05:25) | single-source |
| 6 | Align text, images, and rules to shared axes, and keep content a clear distance from the trim or the screen edge. Break alignment on one deliberate outlier only when the rest is locked, and treat that break as contrast. | Satori Graphics | CLAIM(EFf9jBs2yfU@07:44, EFf9jBs2yfU@08:17, EFf9jBs2yfU@08:47) | single-source |
| 8 | Carry one theme from the brand onto both sides of a small print piece. Lay front and back side by side and check that they complement, often by inverting the field. | Satori Graphics | CLAIM(5zS-5XDo4WQ@00:39, 5zS-5XDo4WQ@01:11) | single-source |

The full set of 60 laws lives in the sub-skills, plus 11 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| layout-space-and-grouping | references/layout-space-and-grouping.md | 7 laws |
| layout-spacing-scale | references/layout-spacing-scale.md | 8 laws |
| layout-web-hierarchy | references/layout-web-hierarchy.md | 9 laws |
| layout-grid-pick | references/layout-grid-pick.md | 20 laws |
| layout-auto-layout | references/layout-auto-layout.md | 6 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 4 | Repeat one color set, one illustration style, and one type family across the piece. Do not drop a gradient or a 3D render into a flat system. | Satori Graphics | CLAIM(EFf9jBs2yfU@04:22, EFf9jBs2yfU@05:12, EFf9jBs2yfU@05:25) | single-source |
| 5 | Build contrast on purpose with color, weight, shape, or size so one element becomes the focal point. A thicker word against a thinner word, a circle against straight edges, or a tilted photo against level rules all count. | Satori Graphics, Flux Academy | CLAIM(EFf9jBs2yfU@05:51, EFf9jBs2yfU@06:02, 9eJYjNGeIOM@03:02) | consensus |
| 9 | On a card, size name and role so they outrank phone, email, and address. Hierarchy is what makes the card look finished. | Satori Graphics | CLAIM(5zS-5XDo4WQ@03:23, 5zS-5XDo4WQ@03:33) | single-source |
| 20 | Set heading line-height at 1:1 with the font size, and paragraph line-height near 1:1.5, as a start. Tighten or loosen after you read it, but do not leave body leading at 1:1. | Self-Made Web Designer | CLAIM(TeMtV8BaZt0@06:05, TeMtV8BaZt0@06:50, TeMtV8BaZt0@08:31) | single-source |
| 21 | Tighten display letter-spacing (about -1 to -3 px) so headlines scan as one unit, leave body at 0, and open CTA letter-spacing (about +1 to +3 px) so the action is read more slowly. | Self-Made Web Designer | CLAIM(TeMtV8BaZt0@09:22, TeMtV8BaZt0@09:28, TeMtV8BaZt0@09:41) | single-source |
| 22 | When pairing is hard, use a superfamily (serif, sans, and mono cut by the same foundry) so sizes and spacing already agree. Mismatched x-heights make the eye jump. | Self-Made Web Designer | CLAIM(TeMtV8BaZt0@11:23, TeMtV8BaZt0@11:40, TeMtV8BaZt0@11:52) | single-source |
| 41 | For each section, name what the eye hits first, what it hits second, and what it misses. Show the frame to someone for a few seconds and ask for recall order. If the important item is missed, redo the hierarchy. | Self-Made Web Designer | CLAIM(ityZtG3FMgw@01:14, ityZtG3FMgw@01:24) | single-source |
| 42 | Cap a site at one or two typefaces, and prefer faces that have already proved themselves. A long career can run on a handful of faces; a library of thousands is noise, not a system. | Self-Made Web Designer | CLAIM(ityZtG3FMgw@03:24, ityZtG3FMgw@03:46) | single-source |
| 43 | Every image needs a job: make the viewer feel something, or earn trust. Do not drop in random smiling stock. Match the photo's colors to the site palette, or the page reads as unfinished. A loud hue on a black-and-white page is the failure case. | Self-Made Web Designer, Flux Academy | CLAIM(ityZtG3FMgw@04:30, ityZtG3FMgw@04:51, 9eJYjNGeIOM@02:09, rRFD6tENX2U@07:31, rRFD6tENX2U@07:50) | consensus |
| 54 | Reuse a known band (picture on one side, copy on the other), then flip the sides and change the band's background on the next section. A page of identical bands loses the scanner. | Self-Made Web Designer | CLAIM(rRFD6tENX2U@03:14, rRFD6tENX2U@03:20, rRFD6tENX2U@03:42) | single-source |
| 55 | Aim faces in photos at the headline or the action. Gaze is a pointer. Do not leave the subject looking off the offer. | Self-Made Web Designer | CLAIM(rRFD6tENX2U@07:58, rRFD6tENX2U@08:09, rRFD6tENX2U@08:15) | single-source |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | A quiet field, a small corner mark, type that still reads with room at the lower right | Type scaled up and a texture poured in to kill the empty half | Empty space is what lets the viewer sort the information |
| 2 | Headline with body, the button alone, icons in a third cluster | A button jammed against body copy, or related cards spaced so far they no longer group | Proximity is the cue; too much gap kills it as surely as too little |
| 3 | Most edges on shared axes, one price badge deliberately off-grid | Every element nudged by eye | A single break reads as emphasis only if the rest is aligned |
| 4 | Largest contrasted image, medium headline, small supporting type | A field of medium-sized, medium-contrast objects | Without a size jump there is no entry point |
| 5 | Front and back sharing type and layout, one side dark and one light | Two sides that do not look like the same brand | A card is one object seen twice |
| 6 | Important type held inside a margin | Type running into the cut | Edge-hugging type looks unfinished after the cutter moves |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/layout/.

## Decision tables

| decision | option A | option B | pick A when | pick B when | citation |
|----------|----------|----------|-------------|-------------|----------|
| Reading-order model | Force an F path | Set hierarchy and let scan patterns vary | Do not. This corpus treats the F path as outdated | Always, for web sections | CLAIM(1NTKwpAVcHg@00:38, 1NTKwpAVcHg@01:05) |
| Grid rigidity | Stay inside the grid | Break the grid a little | Long reading, galleries, anything that must look uniform | A feature image, a hero, or one badge that must win, and only after the rest is aligned | CLAIM(EFf9jBs2yfU@08:47, gUzkRue28VI@01:05) |
| Proportion system | Golden ratio as a lock | Golden ratio as a start, then adjust | Never as a lock in this corpus | Any logo or layout where the ratio is only a first guide | CLAIM(gUzkRue28VI@03:37) |
| Spacing step | One gap everywhere (8 px) | Outside-in steps that shrink inward | Never for a full screen | Mobile and web UI with sections, cards, and controls | CLAIM(cf95Z7Ngg8k@04:37, cf95Z7Ngg8k@07:30) |
| Within-group vs between-group | Base step inside, double between | Same step for both | Groups that must read as one unit | Do not use the same step; it flattens the groups | CLAIM(TeMtV8BaZt0@04:03, TeMtV8BaZt0@04:49) |
| Screen inset | 24 px | 30 px | You are on an 8 px grid and want the inset to divide cleanly | You want more air and 30 still clears the edge; both are accepted | CLAIM(cf95Z7Ngg8k@04:56, cf95Z7Ngg8k@07:14) |
| Button style | Filled, high contrast | Outline only | Primary action | Not for the primary action; outline-only gets missed | CLAIM(1NTKwpAVcHg@01:53) |
| Copy shape | Paragraph | Bullets, ideally with icons | Two or three short sentences already inside the measure | Any block the scanner would have to dig through | CLAIM(TeMtV8BaZt0@01:28, TeMtV8BaZt0@01:51) |
| Grid family | Manuscript, one column | Column, modular, asymmetric, or compound | A book or long text that must not compete with objects | Magazines, product grids, heroes, or a listing plus a detail view | CLAIM(gUzkRue28VI@02:13, gUzkRue28VI@06:00, wIabVp0Hh8U@00:51) |
| Web column count | 12 columns | 4, 5, or 6 columns | A site that must hold 2-up, 3-up, 4-up, and 6-up from one system | An editorial spread where you sketch the count against the content, then lock one | CLAIM(wIabVp0Hh8U@05:07, wIabVp0Hh8U@18:46) |
| Child sizing | Hug | Fill, or fixed | The frame should shrink to the content (a button, an icon) | The child must track the parent, or one column must stay a set width so rows align | CLAIM(2UbxHkiPwxg@05:25, 2UbxHkiPwxg@07:43, 2UbxHkiPwxg@16:20, QjK56pv9Qe4@03:16) |
| Wide frame vs phone frame | Keep the row, children fill, chrome pinned | Duplicate the frame, drop the column count, stack the cards, swap in a compact menu | The type still fits and nothing overlaps as you drag the frame in | The links collide or a three-up has become a smear. 2021 demo: 8 columns on tablet, 4 on phone | CLAIM(QjK56pv9Qe4@02:19, QjK56pv9Qe4@06:00, QjK56pv9Qe4@08:13, QjK56pv9Qe4@09:26) |
| Row tool vs span tool | Auto layout / flex, one direction | A real grid with row and column spans | The job is a nav, a card row, or a stack | A bento, a sidebar plus fluid tracks, or any item that must cross two cells | CLAIM(guYN5LaAcS8@01:10, k5AZoQC-OZk@00:07, k5AZoQC-OZk@10:43) |
| Flexible track size | Fractions | Percents | You may add or remove a column later | Do not. A three-way percent split has to be rewritten by hand | CLAIM(k5AZoQC-OZk@06:22, k5AZoQC-OZk@06:36) |
| Next booklet spread | Mirror the locked spread, then vary once | Invent a new structure on every pair | Interior pages that should feel like one publication | A rest spread or an interview spread, after the base exists | CLAIM(SbEy7hdIJpc@12:55, SbEy7hdIJpc@15:54, SbEy7hdIJpc@16:57) |
| Print margins | All four equal | Bottom larger than top, inside larger than outside | Only if a template demo locked them equal and you have not checked the visual weight. Flux treats that as the default failure | Facing pages, as a start (worked example 10 / 20 / 15 / 10 mm). Envato's 2022 booklet sets 0.75 in on every side; do not treat that click-path as a visual rule | CLAIM(wIabVp0Hh8U@09:56, wIabVp0Hh8U@10:19, SbEy7hdIJpc@01:16) |

## Anti-patterns

- Filling negative space by scaling type or laying a texture across the empty half. CLAIM(EFf9jBs2yfU@00:43)
- Clustering a button with body copy, or spacing related items so far the group breaks. CLAIM(EFf9jBs2yfU@03:45, cf95Z7Ngg8k@02:52)
- Mixing illustration styles inside one piece. CLAIM(EFf9jBs2yfU@05:12)
- Breaking alignment on more than one element. CLAIM(EFf9jBs2yfU@08:47)
- Running type into the trim. CLAIM(5zS-5XDo4WQ@03:10)
- Designing to an F-pattern. CLAIM(1NTKwpAVcHg@00:38)
- Ghost buttons. CLAIM(1NTKwpAVcHg@01:53)
- Decorative type in paragraphs, and client copy pasted as a wall. CLAIM(1NTKwpAVcHg@04:22, TeMtV8BaZt0@00:58)
- plus 17 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Screen inset: Jesse accepts 24 or 30 px and prefers 24 because it divides by 8. Self-Made Web Designer, on a marketing hero, uses 104 px between the nav, the text block, and the image. That is a different object (major regions of a hero, not the screen inset of an app). Do not copy 104 into a mobile wrapper, and do not copy 24 into the gap between a hero's text and its image. CLAIM(cf95Z7Ngg8k@04:56, cf95Z7Ngg8k@07:16, TeMtV8BaZt0@05:30)
- Minimum gap: Jesse sets a 6 px floor between ordinary elements and allows 4 px only as a rare small step on the 8 px grid. Self-Made Web Designer's worked system starts at 8 and jumps by 8, with no 6 px floor. Use 8 when you are on that scale; use 6 only as Jesse's floor for icon-to-label, not as a new base. CLAIM(cf95Z7Ngg8k@01:43, cf95Z7Ngg8k@02:00, TeMtV8BaZt0@03:55)
- No creator in the videos read so far defends the F-pattern or ghost buttons. The rejection is repeated in a second Self-Made Web Designer video, still one creator. CLAIM(1NTKwpAVcHg@00:38, ityZtG3FMgw@00:35, ityZtG3FMgw@01:47)
- 60/30/10, same creator, three cuts. Two 2025 cuts: 60 percent neutral or dominant, 30 percent brand, 10 percent accent kept for buttons, one button color. 2026: 60 percent background, 30 percent text and cards, 10 percent accent. The 10 percent on actions holds. The 30 percent bucket does not. CLAIM(1NTKwpAVcHg@03:02, rRFD6tENX2U@06:53, rRFD6tENX2U@07:17, ityZtG3FMgw@02:48)
- Facing-page margins. Flux (2022) rejects four equal margins and starts at 10 mm top, 20 mm bottom, 15 mm inside, 10 mm outside, because an equal box feels like it falls off the page. Envato Tuts+ (2022) sets 0.75 in on every side and turns on "make all settings the same" for a letter booklet. Use Flux when you are judging visual weight. Treat the Envato number as a file-setup demo, not a rebuttal, unless you have checked the printed sheet. CLAIM(wIabVp0Hh8U@09:56, wIabVp0Hh8U@10:19, SbEy7hdIJpc@01:16, SbEy7hdIJpc@01:25)
- One-direction rows vs a span grid. Flux and DesignCourse build responsive rows with auto layout (flex): pin, fill, then stack when the frame is narrow. Jesse (2024) uses a CSS grid when the item must cross rows and columns, and sizes those tracks in fractions. Do not pick one tool for both jobs. CLAIM(QjK56pv9Qe4@02:43, QjK56pv9Qe4@08:13, k5AZoQC-OZk@00:07, k5AZoQC-OZk@06:05)
- Baseline grids. Satori (2024) hangs body, headlines, and captions on one baseline and sets headline size as a multiple of leading. Flux (2022) says a baseline is hard on the web, worth knowing, and not required in every document. Use it in print and in multi-column editorial. Do not block a web ship on it. CLAIM(gUzkRue28VI@00:11, wIabVp0Hh8U@01:34, wIabVp0Hh8U@01:45)
- Golden ratio. Satori and Self-Made Web Designer agree it is a start, including a type step of about 1.618, and both refuse to lock it when the result looks wrong. No creator in this set defends the ratio as a finish line. CLAIM(gUzkRue28VI@03:37, rRFD6tENX2U@05:55, rRFD6tENX2U@06:14)

## Creator claims (unverified)

- A redesigned site looked cleaner, then sales dropped, blamed on pretty layout over conversion practice. No numbers. CLAIM(1NTKwpAVcHg@04:34, 1NTKwpAVcHg@04:44)
- Nielsen is cited for scanners leaving at a big block. No study id, sample, or year is given. CLAIM(TeMtV8BaZt0@00:58)
- Restructuring copy is framed as the difference between a 500 dollar site and a 5,000 dollar site. No client sample. CLAIM(TeMtV8BaZt0@03:14)
- Namecheap prices in the card video, and Mobbin screen counts in the spacing video, are sponsor copy. CLAIM(5zS-5XDo4WQ@00:28, cf95Z7Ngg8k@03:19)
- A live Spotify header is shown at a 1:1 size-to-leading ratio, and a paragraph there is 24 on 30, not 1.5. That is one site on one day, not a standard. CLAIM(TeMtV8BaZt0@08:02, TeMtV8BaZt0@08:15)
- Only about 20 percent of people get past the first screen. No study, sample, or year is given. CLAIM(rRFD6tENX2U@10:50)
- Oversized images are called the main cause of slow sites, with a personal cap near 300 kilobytes. No measurement set. CLAIM(rRFD6tENX2U@09:28, rRFD6tENX2U@09:32)
- Envato Elements "millions of assets" and the Penpot "always free" line are sponsor or product copy, not layout findings. CLAIM(SbEy7hdIJpc@00:37, k5AZoQC-OZk@00:32)

## Tool-specific (dated)

- Print cards at 300 ppi in CMYK. 2019. CLAIM(5zS-5XDo4WQ@02:05)
- Card bleed and content margin of 5 mm, artwork past the bleed. Illustrator named. 2019. CLAIM(5zS-5XDo4WQ@02:29, 5zS-5XDo4WQ@03:04)
- Test-print the card and hold it at viewing distance before locking type size. 2019. CLAIM(5zS-5XDo4WQ@01:41)
- Check brand pairs in Coolors contrast view. 2025. CLAIM(1NTKwpAVcHg@02:38)
- Headline size as a multiple of body leading (28 pt on 14 pt) is a 2024 print-grid example, not a web pixel spec. CLAIM(gUzkRue28VI@00:34)
- InDesign CC 2018 booklet: print intent, about 260 by 216 mm, 3 mm bleed linked on all sides, images 300 ppi CMYK JPEG at the page size or larger, frame drawn through the bleed, preview with bleed hidden so you can see the cut. CLAIM(wPFEzHXOdCs@00:48, wPFEzHXOdCs@01:16, wPFEzHXOdCs@02:15, wPFEzHXOdCs@04:11)
- Repeating page numbers live on the master spread; override the cover with a modifier-click so the cover has no number. Export PDF print with document bleed settings. 2018. CLAIM(wPFEzHXOdCs@05:05, wPFEzHXOdCs@05:22, wPFEzHXOdCs@06:50, wPFEzHXOdCs@09:49)
- Pull a site palette from the browser CSS overview panel, not by sampling one screenshot, then drop the colors into Coolors and export. 2025. CLAIM(TeMtV8BaZt0@13:06, TeMtV8BaZt0@14:36)
- plus 9 more in the corpus law file studio-corpus/laws/layout.md

## Hand-off
- Next stage: ds-ui-system, ds-conversion-copy. Agent: `ds-ui-designer`.
- Corpus source: studio-corpus/laws/layout.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
