---
name: ds-typography
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for typography: Choose and set type: family selection and pairing, text mechanics (measure, leading, scale, tracking, kerning, casing, emphasis), and hierarchy or mood inside one system. 35 laws, 20
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the task names fonts, type, readability, text hierarchy, pairing, scale, leading or kerning.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides typography. Entered by the /design-studio command through design-studio-os, by ds-brand-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: type.md: chosen faces with licenses, base body size and ratio, full scale, leading/tracking/kerning rules, casing and emphasis rules, measure cap, contrast check, mood rationale, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 ../rig-design-studio-os/tools/claims_check.py capabilities/skills/ds-typography/SKILL.md
  - cmd:python3 ../rig-design-studio-os/tools/check_family.py
quality_floor: 0.6
---

# Typography

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches typography. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-brand-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "font", "type", "typography", "readable", "heading hierarchy", "kerning". Inside a build this stage runs after the stage that feeds it and
before ds-color.

## Inputs and output contract

Inputs: brief mood keywords, the text roles (headings, body, captions), the real content sample, target screens.
Output: type.md: chosen faces with licenses, base body size and ratio, full scale, leading/tracking/kerning rules, casing and emphasis rules, measure cap, contrast check, mood rationale.

## Procedure

1. Font selection and pairing: brief to classification, go-to list, anchor choice, contrast pairing, license and test protocol (see references/font-selection-and-pairing.md).
2. Type setting mechanics: alignment, measure, leading, size ratios, tracking, kerning, casing, emphasis, widows, contrast, live text (see references/type-setting-mechanics.md).
3. Type hierarchy and mood: mood levers inside one family, opacity tiers, scale dominance, one attention anchor (see references/type-hierarchy-and-mood.md).
4. Web type systems: type scale setup, grid and spacing systems, responsive verification (see references/web-type-systems.md).
5. Display type effects: outlined display treatment, effects stacks and their tool recipes, with the tool-specific table as its reference (see references/display-type-effects.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 2 | Maintain a personal go-to font list of roughly 20 to 60 reliable faces, sorted by classification (old style, transitional, modern, humanist grotesque, geometric, slab, mono), and start every selection there instead of scrolling full libraries. | Flux Academy, The Futur | CLAIM(WTUM2Y11oJo@04:30, WTUM2Y11oJo@05:30, QrNi9FmdlxY@01:28) | consensus |
| 3 | Choose one anchor face first and derive the rest of the system from it; the anchor must match the brand's mood before anything else is picked. | Self-Made Web Designer, Flux Academy | CLAIM(pbhLsV-Dyho@00:59, pbhLsV-Dyho@01:28, WTUM2Y11oJo@40:00) | consensus |
| 4 | Pair faces of different classifications and clear contrast (serif with sans, wide with condensed, heavy with light), and reject pairs that are near-duplicates because closeness without identity reads as an error. | Flux Academy, Self-Made Web Designer, The Futur | CLAIM(WTUM2Y11oJo@34:31, pbhLsV-Dyho@02:02, QrNi9FmdlxY@00:30) | consensus |
| 13 | Set any text block longer than two lines flush left with a ragged right edge; reserve centered setting for short blocks, and never center a paragraph with a rag on both sides. | The Futur, Flux Academy | CLAIM(QrNi9FmdlxY@00:00, aOPGqOOi__4@01:29) | consensus |
| 14 | Hold the measure to about 50 to 70 characters (roughly 7 to 12 words) per line, and cap the column width on wide screens instead of letting type fill the viewport. | Flux Academy, Will Paterson | CLAIM(aOPGqOOi__4@04:30, 9ut7EmnYG7I@08:30, y2Tn9DS4ROs@05:30) | consensus |
| 15 | Set body line height between 120 and 150 percent of the type size (start near 130), and tighten leading as text grows so headings stay a single visual unit. | Flux Academy, Self-Made Web Designer, Will Paterson | CLAIM(9ut7EmnYG7I@09:59, vbFn0C-pvis@03:50, MFUXBlnTS5Y@00:30) | consensus |
| 16 | Derive every text size from one base body size by a fixed ratio (1.25 major third, 1.618 golden, or simple doubling), and never invent one-off point sizes. | Will Paterson, The Futur, Self-Made Web Designer | CLAIM(MFUXBlnTS5Y@02:01, QrNi9FmdlxY@00:30, vbFn0C-pvis@02:41) | consensus |
| 17 | Leave tracking at zero for body text and never track lowercase body wide; as type gets larger, pull tracking in, and use wide tracking only on uppercase display or logotypes. | Flux Academy, Self-Made Web Designer | CLAIM(9ut7EmnYG7I@06:30, 9ut7EmnYG7I@06:59, vbFn0C-pvis@03:32) | consensus |
| 1 | Write the brief's mood keywords (playful vs serious, restrained vs expressive, familiar vs unusual) and list the text roles you need (headings, body, captions) on paper before opening any font library. | Flux Academy | CLAIM(WTUM2Y11oJo@00:32, WTUM2Y11oJo@02:29) | single-source |
| 5 | When two faces must coexist, match their anatomy (similar x-height, curve shapes, era feel) even while they contrast in class, so the pair reads as one family of intent. | Flux Academy | CLAIM(WTUM2Y11oJo@37:30, WTUM2Y11oJo@38:59) | single-source |
| 6 | Cap a layout at two or three typefaces and at most one decorative face, used only for headings or a large graphic element; count styles and weights, not just family names. | Flux Academy | CLAIM(9ut7EmnYG7I@12:29, 9ut7EmnYG7I@13:30, WTUM2Y11oJo@36:00) | single-source |
| 7 | Work brief keyword to classification: nostalgic or heritage briefs take old-style serifs, mass-market accessibility briefs avoid high-contrast serifs, technical briefs take grotesques or mono; do not assume modern means sans. | Flux Academy | CLAIM(WTUM2Y11oJo@07:01, WTUM2Y11oJo@10:30) | single-source |

The full set of 35 laws lives in the sub-skills.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| font-selection-and-pairing | references/font-selection-and-pairing.md | 12 laws |
| type-setting-mechanics | references/type-setting-mechanics.md | 15 laws |
| type-hierarchy-and-mood | references/type-hierarchy-and-mood.md | 6 laws |
| web-type-systems | references/web-type-systems.md | 2 laws |
| display-type-effects | references/display-type-effects.md | 1 laws |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Long copy flush left with a one-sided rag | A centered paragraph whose rag breaks on both sides | The eye can return to a fixed left edge each line |
| 2 | A capped column of 50 to 70 characters | Full-width lines stretched across a large monitor | Excess length forces head movement while reading |
| 3 | One dominant headline with small supporting type | A page of equally medium blocks | Scale contrast is what creates a reading order |
| 4 | A serif and a sans matched on x-height and era | Two geometric sans faces that are almost identical | Near-duplicates read as a rendering bug, not a pairing |
| 5 | Two typefaces with restrained UI text around a complex logo | A different font on every element of one page | Fewer faces keep the page legible and the brand coherent |
| 6 | Type on a solid color or a flattened photo area | Dark type dropped on a busy, high-detail photograph | Contrast collapses where the photo is busy |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/typography/.

## Decision tables

### Scale ratio for the type system
| Option | Pick when | Citation |
|--------|-----------|----------|
| Multiply by 1.25 (major third) | Dense web UI with many levels from H6 up to H1 | CLAIM(vbFn0C-pvis@02:59) |
| Multiply by 1.618 (golden) | Editorial or poster work where H1, H2, H3, title need a strong jump | CLAIM(MFUXBlnTS5Y@02:01, y2Tn9DS4ROs@07:00) |
| Double or half the point size | Print or bold display work needing obvious contrast | CLAIM(QrNi9FmdlxY@00:30) |

### Kerning mode
| Option | Pick when | Citation |
|--------|-----------|----------|
| Metric (designer's values) | Any running body text | CLAIM(y2Tn9DS4ROs@03:29, 9ut7EmnYG7I@07:29) |
| Optical then hand-adjust | Logotypes and one-line display, or a face whose metrics are weak | CLAIM(y2Tn9DS4ROs@03:59, 9ut7EmnYG7I@07:58) |
| Flip-to-shape check | Before signing off any logotype or headline | CLAIM(y2Tn9DS4ROs@01:30, MFUXBlnTS5Y@04:58) |

### Alignment of a text block
| Option | Pick when | Citation |
|--------|-----------|----------|
| Flush left, rag right | Anything a reader must actually read (paragraphs, articles, addresses) | CLAIM(QrNi9FmdlxY@00:00, aOPGqOOi__4@01:29) |
| Centered | Short blocks: a hero line, a two-line invitation, an occasional stylistic break | CLAIM(aOPGqOOi__4@10:01) |

### Mood levers inside one family
| Target mood | Settings | Citation |
|-------------|----------|----------|
| Premium | Uppercase, wide tracking, small size, centered, generous white space, dark ground | CLAIM(Yfd5kW1ZMgQ@03:09) |
| Serious | Left aligned on a grid, bold heading weight, equal spacing, thin rules | CLAIM(Yfd5kW1ZMgQ@04:29) |
| Playful | Lowercase, letters offset and rotated in the heading only | CLAIM(Yfd5kW1ZMgQ@07:31, Yfd5kW1ZMgQ@11:01) |
| Aggressive | Oversized bold uppercase, negative tracking, black blocks framing the type | CLAIM(Yfd5kW1ZMgQ@11:30, Yfd5kW1ZMgQ@12:29) |
| Quiet or somber | Light weight, small size, corner placement, empty field around it | CLAIM(Yfd5kW1ZMgQ@14:58) |

### Pairing strategy
| Option | Pick when | Citation |
|--------|-----------|----------|
| One font, multiple weights | Beginner, or brand needs restraint | CLAIM(QrNi9FmdlxY@00:30) |
| Super family (sans + serif + mono from one family) | You want contrast without pairing risk | CLAIM(pbhLsV-Dyho@00:32) |
| Two faces from different foundries, anchored on one | The brand needs personality the defaults cannot carry | CLAIM(pbhLsV-Dyho@00:59, WTUM2Y11oJo@40:00) |

## Anti-patterns

- Stretching one width of a family to imitate another width; stems and stroke contrast break. CLAIM(9ut7EmnYG7I@00:00)
- Using a good face in the wrong category (display serif on a technical product, script on signage). CLAIM(9ut7EmnYG7I@03:30, 9ut7EmnYG7I@03:59)
- Insufficient contrast: hairline weights in body copy, or type over a busy photo. CLAIM(9ut7EmnYG7I@03:59, aOPGqOOi__4@01:00)
- Invented point sizes with no relationship between them. CLAIM(9ut7EmnYG7I@05:30)
- Wide tracking on lowercase body copy. CLAIM(9ut7EmnYG7I@06:30)
- Optical kerning applied to whole body blocks. CLAIM(y2Tn9DS4ROs@03:29)
- Measures far too long (reading like watching a tennis match) or four words per line. CLAIM(9ut7EmnYG7I@08:30, aOPGqOOi__4@19:30)
- 100 percent leading that packs lines, or 200 percent that loses paragraph grouping. CLAIM(9ut7EmnYG7I@09:59)
- plus 8 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Which font is the anchor. Self-Made Web Designer (2026) starts from the headline and finds support faces after it, because the headline sets the page personality. Flux Academy (2022) says pick whichever face works best first, often the body face and then an accent. Will Paterson (2025) sizes everything from the body text upward. CLAIM(pbhLsV-Dyho@00:59, WTUM2Y11oJo@40:00, MFUXBlnTS5Y@02:59)
- Whether one font is enough. The Futur (2016) tells learners to stay on one font until they master it and to avoid two faces of the same class. Self-Made Web Designer (2026) calls one font level one of three and pushes toward cross-foundry pairs for personality. Both still require contrast between faces. CLAIM(QrNi9FmdlxY@00:30, pbhLsV-Dyho@00:00)
- Words per line. Will Paterson (2024) sets 7 to 10 words per column; Flux Academy (2024) names 8 to 12 words and 50 to 70 characters; Flux Academy (2023) allows pushing toward 15 depending on context. CLAIM(y2Tn9DS4ROs@05:30, aOPGqOOi__4@04:30, 9ut7EmnYG7I@09:00)
- Body line height starting point. Flux Academy (2023) starts body leading near 120 to 130 percent; Self-Made Web Designer (2025) prescribes 150 percent for web paragraphs. Both agree headings tighten as they grow. CLAIM(9ut7EmnYG7I@09:59, vbFn0C-pvis@03:50)
- Serif equals old and sans equals modern. Flux Academy (2022) rejects the shortcut, showing a modern phone brand and a digital publication both running serif headlines, and argues the pairing and the anatomy decide the era instead. CLAIM(WTUM2Y11oJo@09:59, WTUM2Y11oJo@12:00)
- Wide tracking. Flux Academy (2023) permits it mainly for uppercase logotypes and certain headlines; Flux Academy (2022) uses wide tracking on uppercase as a deliberate premium signal. The two agree it never belongs on lowercase body copy. CLAIM(9ut7EmnYG7I@06:59, Yfd5kW1ZMgQ@02:29)
- Centered type. Flux Academy (2024) allows occasional centered setting for very short blocks; Will Paterson (2022) uses centered composition as a premium treatment with tiny uppercase copy. Neither defends centering running text. CLAIM(aOPGqOOi__4@10:01, Yfd5kW1ZMgQ@03:31)

## Creator claims (unverified)

- A Flux Academy host offers that good typography alone puts a site ahead of roughly 80 percent of websites, then states he invented the figure. CLAIM(aOPGqOOi__4@00:00)
- Self-Made Web Designer asserts 99 percent of web designers cannot distinguish good type choices from bad ones. CLAIM(vbFn0C-pvis@00:30)
- The same channel frames the two typography questions as a route to the top 1 percent of web designers. CLAIM(vbFn0C-pvis@01:01)
- The video title claims six tips can multiply a site's design quality tenfold. CLAIM(pbhLsV-Dyho@00:00)
- Will Paterson presents the 1.618 multiplier as producing a beautiful, harmonious type system. CLAIM(MFUXBlnTS5Y@02:59)
- Flux Academy estimates a designer draws on a small favorite set for about 80 percent of projects. CLAIM(WTUM2Y11oJo@04:30)
- The Futur states that contrast is the key to great design. CLAIM(QrNi9FmdlxY@00:30)
- Will Paterson recommends 7 to 10 words per column as the fatigue threshold, citing a book on grid systems. CLAIM(y2Tn9DS4ROs@05:30)

## Tool-specific (dated)

- Illustrator (2017): cut text into a shape over a photo by converting type to outlines and subtracting the shape in Pathfinder. CLAIM(8A3JaGxU9o0@01:02)
- Illustrator (2017): build a double-stroke text effect through the Appearance panel by stacking a new fill with strokes beneath it. CLAIM(8A3JaGxU9o0@03:18)
- Illustrator (2017): reflected gradient text by duplicating, reflecting horizontally, and shading the lower copy. CLAIM(8A3JaGxU9o0@04:30)
- Illustrator (2017): manual highlight and shadow on outlined type using the pencil for filled highlight shapes. CLAIM(8A3JaGxU9o0@05:59)
- Photoshop (2016): neon type from two duplicated layers, inner glow on the top layer and outer glow with a vivid-light blend on the bottom, over a textured background photo. CLAIM(nH9hECxwpyA@01:30, nH9hECxwpyA@01:56)
- Illustrator (2018): one-click perspective type by dragging text onto the perspective grid with the plane-switching widget selecting the grid face. CLAIM(i1gJRhPL1yk@01:31, i1gJRhPL1yk@02:29)
- Illustrator (2018): gradient-filled display letters built from outlined type, a two-color gradient sampled by hex code in RGB mode, and pen-drawn sections intersected in Pathfinder. CLAIM(gjwXBmb5fZ4@01:01, gjwXBmb5fZ4@03:01)
- Procreate (2019): text added from the wrench menu, tracked in the Edit Style panel, textured with a transparent PNG as a clipping mask, and interwoven with lettering via a layer mask painted only inside a selection of the type. CLAIM(vLcroxhTals@00:30, vLcroxhTals@03:00, vLcroxhTals@05:00)
- plus 7 more in the corpus law file studio-corpus/laws/typography.md

## Hand-off
- Next stage: ds-color. Agent: `ds-brand-designer` (sub: ds-type-pairer).
- Corpus source: studio-corpus/laws/typography.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
