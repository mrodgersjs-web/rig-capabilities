---
name: ds-ui-system
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for ui systems and components: Design reusable components: token architecture, component anatomy and props, responsive construction, interactive states, pattern recipes. 42 laws, 20
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the job is a component library, design system, tokens, app or dashboard UI, or component states.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides ui systems and components. Entered by the /design-studio command through design-studio-os, by ds-ui-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: system.md: token file (color, type, spacing, radius, shadow), component inventory with anatomy and states, state matrix, responsive rules, a design.md the build can read, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-ui-system/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# UI systems and components

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches ui systems and components. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-ui-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "design system", "components", "component states", "tokens", "dashboard", "app UI". Inside a build this stage runs after the stage that feeds it and
before ds-ux, ds-build-ship.

## Inputs and output contract

Inputs: the feature or screen list, the token source, the platform (web, iOS, Android).
Output: system.md: token file (color, type, spacing, radius, shadow), component inventory with anatomy and states, state matrix, responsive rules, a design.md the build can read.

## Procedure

1. Ui tokens modes: variables as two-layer tokens, named scale levels, theme modes, boolean visibility bindings (laws 1-8) (see references/ui-tokens-modes.md).
2. Ui components variants: component sets, variant naming, properties over variants, slots, nesting (laws 9-18) (see references/ui-components-variants.md).
3. Ui responsive construction: inside-out auto layout, explicit child sizing, constraints, min/max wrap, breakpoint variants, 8px grid (laws 19-26) (see references/ui-responsive-construction.md).
4. Ui prototype states: state matrices, component-level prototype links, timing standards, set-variable interactions, failure diagnosis (laws 27-35) (see references/ui-prototype-states.md).
5. Ui pattern recipes: search input states, surface color derivation, radius relationships, button ripple, glass and neobrutalist recipes (laws 36-43) (see references/ui-pattern-recipes.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Store every repeated design value (color, gap, radius, spacing) as a named variable and bind the property to it, so one edit updates all usages instead of re-entering values per element | Flux Academy, Jesse Showalter | CLAIM(GUupJJC5Ac4@00:18), CLAIM(oCVG6DFCTz4@10:15) | consensus |
| 4 | Group variables into collections by kind (colors, numbers, booleans) and attach a short description to each naming where it applies | DesignCourse, Punit Chawla | CLAIM(Tx45NcbU6aA@02:35), CLAIM(IO30Ta7aqF0@01:06) | consensus |
| 6 | Implement themes as one extra mode per variable (light, dark), fill each mode with its own values, then flip the frame mode from the layer panel selector | Flux Academy, DesignCourse, Punit Chawla | CLAIM(GUupJJC5Ac4@06:13), CLAIM(Tx45NcbU6aA@25:42), CLAIM(IO30Ta7aqF0@03:40) | consensus |
| 8 | Bind boolean variables to layer visibility (right-click the visibility icon in the layer controls) so one click can show or hide content per state | DesignCourse, Flux Academy | CLAIM(Tx45NcbU6aA@19:26), CLAIM(vf1BZ1mG2WE@20:46) | consensus |
| 9 | Convert anything reused more than once into a component and edit only the master, so every instance follows | Flux Academy, Jesse Showalter | CLAIM(aGvWDDPsjUM@00:57), CLAIM(oCVG6DFCTz4@03:30), CLAIM(1JZcMnecWHI@00:57) | consensus |
| 10 | Put interchangeable items (icon types, button shapes, tab states) in one component set with one variant each, so instances swap from the properties panel | Flux Academy | CLAIM(1JZcMnecWHI@01:23), CLAIM(vf1BZ1mG2WE@03:13) | consensus (same creator, 3 videos) |
| 11 | Give every variant axis a real option name (State equals default, hovered, active) and rename the property itself; never ship a set labeled with generator defaults | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(1JZcMnecWHI@02:35), CLAIM(aGvWDDPsjUM@05:21), CLAIM(iLWaIx7tMnU@17:08) | consensus |
| 13 | Reserve variants for state and shape; express content differences with properties (text field, show/hide boolean, instance swap) or the variant count explodes | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(aGvWDDPsjUM@02:57), CLAIM(oCVG6DFCTz4@03:57), CLAIM(KWUlkXZOj4g@11:38) | consensus |
| 2 | Build tokens in two layers: a primitives collection of raw values, then a semantic collection whose names state the role (button, link, heading, body) and reference the primitives | Flux Academy | CLAIM(GUupJJC5Ac4@04:07), CLAIM(GUupJJC5Ac4@04:07) | single-source |
| 3 | Choose variables over shared styles whenever one role must recolor without touching the others: repointing the button token leaves link and logo usages intact | Flux Academy | CLAIM(GUupJJC5Ac4@05:35) | single-source |
| 5 | Name number variables as scale levels (five for 40px radius, two for a 16px gap) and bind components to the level, never to the raw pixel value | Jesse Showalter | CLAIM(oCVG6DFCTz4@10:15) | single-source |
| 7 | Keep the default mode first in the collection by dragging rows into order, so the mode picker shows it first | Jesse Showalter | CLAIM(M8msUKBSBlY@03:27) | single-source |

The full set of 42 laws lives in the sub-skills.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| ui-tokens-modes | references/ui-tokens-modes.md | 8 laws |
| ui-components-variants | references/ui-components-variants.md | 10 laws |
| ui-responsive-construction | references/ui-responsive-construction.md | 9 laws |
| ui-prototype-states | references/ui-prototype-states.md | 8 laws |
| ui-pattern-recipes | references/ui-pattern-recipes.md | 8 laws |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Every repeated color and radius bound to a named variable | Raw values retyped into each element | One edit propagates; drift is impossible |
| 2 | Button recolor done by repointing its semantic token | Editing one shared style that also repaints links and the logo | Semantic tokens isolate roles |
| 3 | Variant set whose axis reads State equals default, hovered | Set labeled property 1 with variant 2 inside | Readable sets survive handoff |
| 4 | Icon swap through an instance-swap property with preferred values | Scrolling a full icon library on every instance | Preferred values constrain the picker |
| 5 | Nested auto layouts built inner group first | One basket frame stuffed with loose layers | Nesting survives resizing |
| 6 | Each child told to fill the container or hug | Children left on defaults so the stretch scatters them | Parent control needs explicit child sizing |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/ui_system/.

## Decision tables

| choice | pick A when | pick B when | citation |
|--------|-------------|-------------|----------|
| Variables vs styles | A role must be recolored or resized without touching other roles; spacing, radius, counts need binding | You only need a single shared type or color definition with no role separation | CLAIM(GUupJJC5Ac4@00:44) |
| Variant vs component property | The difference is state or shape (hover, pill versus rounded, horizontal versus vertical) | The difference is content or presence (label text, icon shown, which icon) | CLAIM(aGvWDDPsjUM@02:57) |
| Auto layout vs constraints | Children must reflow with content size and container growth | An element is a fixed decoration anchored to one corner | CLAIM(oXDAmwEWlDc@01:42) |
| Stretch vs breakpoint variant | The layout still reads at the smaller size | Elements crowd or collide; then swap to a purpose-built variant | CLAIM(oXDAmwEWlDc@22:48) |
| Fill vs hug vs fixed width | Row items should share available space (fill), size to their content (hug) | A spec mandates one exact width, and wrap plus min/max cannot express it | CLAIM(oXDAmwEWlDc@06:08) |
| Boolean filter vs variable mode vs page copy | Filtering visible items (booleans); theme swaps (modes) | Never use page copies; they are the rejected path | CLAIM(vf1BZ1mG2WE@19:42) |
| Hover trigger vs click trigger vs after-delay | Hover for passive feedback, click for committed state change, after-delay for progressive disclosure like suggestions | Mixing them: do not use click where hover feedback is enough | CLAIM(iLWaIx7tMnU@17:41) |
| Component slot vs nested component | The region will hold swappable content decided later by other designers | The region content is fixed and just needs reuse | CLAIM(beUlX6L2NMg@02:30) |

## Anti-patterns

- Duplicating one page per filter state and wiring a switcher between the copies (CLAIM(vf1BZ1mG2WE@18:46)).
- Duplicating an element and editing each copy every time the design changes (CLAIM(aGvWDDPsjUM@00:02)).
- Designing a button in isolation on an empty canvas, then dropping it into layouts (CLAIM(KWUlkXZOj4g@02:02)).
- One outer frame holding loose children with no nested auto layout (CLAIM(oXDAmwEWlDc@02:53)).
- Placeholder text as the only field label (CLAIM(iLWaIx7tMnU@08:00)).
- Pure neutral gray fills placed next to colored surfaces (CLAIM(iLWaIx7tMnU@04:31)).
- Rounded control inside a square container with no radius relationship (CLAIM(iLWaIx7tMnU@04:58)).
- A quantity control that can decrement past its floor (CLAIM(Tx45NcbU6aA@10:55)).
- plus 6 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Swapping icons inside a component: DesignCourse (2021) stacks several icons in the master and toggles visibility per instance, calling direct swap unworkable (); Flux Academy (2023) uses an instance-swap property with preferred values (CLAIM(aGvWDDPsjUM@10:00)). Later method supersedes.
- Hover feedback mechanism: DesignCourse (2021) grows a masked ripple shape (CLAIM(KWUlkXZOj4g@05:36)); Flux Academy (2023) changes opacity on the hovered variant (); DesignCourse (2022) darkens the fill one step (CLAIM(iLWaIx7tMnU@05:50)). No consensus on the mechanism, only that a hover state must exist.
- One-frame-per-state: Flux Academy (2024) rejects duplicated pages for filter states in favor of variables (CLAIM(vf1BZ1mG2WE@18:46)), while Jesse Showalter (2023) builds one frame per responsive width and switches between them at breakpoints (CLAIM(oXDAmwEWlDc@13:45)). Different problems: content filtering versus breakpoint demonstration; variables are still the wrong tool for showing three layout widths to a stakeholder.
- Button aesthetic: Mike Locke (2009) builds a skeuomorphic engraved gradient button with layered shadows (CLAIM(_NTvNAaetCM@04:38)); DesignCourse (2022) removes soft shadows and uses flat high-contrast strokes and hard offset shadows (CLAIM(4BEEoYYDmUg@01:35)). Era disagreement, not a factual conflict; both recipes are checkable and the choice is stylistic.

## Creator claims (unverified)

- Jesse Showalter says his tips multiply design speed and beat 90 percent of designers (CLAIM(oCVG6DFCTz4@00:05)); no measurement given.
- Jesse Showalter advertises a 30-day program with over 150 lessons and 35 hours of curriculum (CLAIM(oXDAmwEWlDc@11:38)).
- Gary Simon claims his course lifts layouts he would rate four or five up to eight and beyond (CLAIM(iLWaIx7tMnU@00:48)).
- Punit Chawla expects slots to save substantial time on large projects with many swappable elements (CLAIM(beUlX6L2NMg@03:17)).
- Mike Locke calls the silver gradient button neutral enough to work on any background (CLAIM(_NTvNAaetCM@06:08)).
- Jesse Showalter calls Mobbin the premier inspiration library for interface designers (CLAIM(M8msUKBSBlY@01:41)).
- Gary Simon dates neobrutalism as the most popular trend of 2022, continuing into 2023 (CLAIM(4BEEoYYDmUg@00:05)).

## Tool-specific (dated)

- Figma variables, collections, and modes, 2023: variables were in beta on desktop; set-variable prototype actions and extra modes required the file to live in a team (CLAIM(Tx45NcbU6aA@04:26), CLAIM(Tx45NcbU6aA@04:23)).
- Figma variables, 2023 limitation: modes could not be switched by a prototype interaction, only manually per frame (CLAIM(Tx45NcbU6aA@25:50)).
- Figma Slots, public beta 2026: a frame inside a component can be converted to a slot; dev mode emits a slot tag in generated code (CLAIM(beUlX6L2NMg@00:30), CLAIM(beUlX6L2NMg@01:21)).
- Figma glass effect, beta 2025: applies to frames only, not bare shapes or rectangles; lighting and refraction are adjustable per panel (CLAIM(3ERrrTcx09c@00:40), CLAIM(3ERrrTcx09c@01:00)).
- Figma 2024-2025 updates: aspect-ratio lock replacing constrain proportions (CLAIM(M8msUKBSBlY@00:23)), a collapse-all-layers control in the layers panel (CLAIM(M8msUKBSBlY@00:30)), drag-to-reorder of modes and collections (CLAIM(M8msUKBSBlY@02:56)), contrast readout inside the color picker (CLAIM(M8msUKBSBlY@03:55)), copy and paste of text/color/effect styles between files (CLAIM(M8msUKBSBlY@04:50)).
- Framer components 2024: text, color, and visibility variables attach to main-component layers and appear on every variant; interactions between variants auto-wire a transition you can edit per instance (CLAIM(Sfy5wG5ZB3A@08:33), CLAIM(Sfy5wG5ZB3A@06:25)).
- Adobe Fireworks 2009 button recipe: pill rectangle with white-to-dark gray linear gradient, larger backing shape at 30 percent opacity as a shadow plate, drop shadow near 3/4/80, dark gray label with a white 2px softness-1 shadow to fake engraving (CLAIM(_NTvNAaetCM@02:14), CLAIM(_NTvNAaetCM@03:25)).
- Figma community Breakpoints plugin (paid, 2023) drives multi-width responsive preview; without it, breakpoint behavior is documented as separate frames (CLAIM(oXDAmwEWlDc@17:34)).
- plus 1 more in the corpus law file studio-corpus/laws/ui_system.md

## Hand-off
- Next stage: ds-ux, ds-build-ship. Agent: `ds-ui-designer`.
- Corpus source: studio-corpus/laws/ui_system.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
