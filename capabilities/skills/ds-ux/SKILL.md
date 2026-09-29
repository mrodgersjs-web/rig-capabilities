---
name: ds-ux
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for ux: flows, forms and accessibility: Design the task: navigation and wayfinding, forms and inputs, accessibility, the psychology of visual hierarchy, and the research that grounds it. 60 laws, 30
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the job is flows, navigation, forms, onboarding, usability or accessibility of a task.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides ux: flows, forms and accessibility. Entered by the /design-studio command through design-studio-os, by ds-ui-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: ux.md: flows and IA, form and input spec with error states, a11y checklist results (keyboard, focus, contrast, screen reader), hierarchy rationale, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-ux/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# UX: flows, forms and accessibility

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches ux: flows, forms and accessibility. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-ui-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "user flow", "form", "onboarding", "navigation", "usability", "accessibility". Inside a build this stage runs after the stage that feeds it and
before ds-motion-3d, ds-critique.

## Inputs and output contract

Inputs: the user and their job to be done, the task list, any research notes.
Output: ux.md: flows and IA, form and input spec with error states, a11y checklist results (keyboard, focus, contrast, screen reader), hierarchy rationale.

## Procedure

1. Navigation wayfinding: nav structure, states, placement, and keyboard paths (see references/navigation-wayfinding.md).
2. Form input design: field anatomy, states, error handling, and CTA emphasis (see references/form-input-design.md).
3. Accessibility audit: contrast, alt text, media alternatives, keyboard, and assistive-user tuning (see references/accessibility-audit.md).
4. Psychology visual hierarchy: mental models, chunking, isolation, Gestalt grouping, color and type personality (see references/psychology-visual-hierarchy.md).
5. Research flows process: research, wireframe fidelity, storyboards, scenario mapping, usability passes, table design, handoff (see references/research-flows-process.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 6 | Place logo top-left and nav top-right; treat any other placement as a redesign risk and test it against user expectations before shipping. | DesignCourse, Self-Made Web Designer | CLAIM(D29KL52Srtw@05:40), CLAIM(d-IaU9qcDGg@02:52) | consensus |
| 8 | Size nav items and icons so they are easy to hit on touch, with clear space around each (at least 44px for icon-only controls), and keep frequently tapped primary controls apart from destructive or secondary ones so mis-taps do not fire them. | Flux Academy, DesignCourse | CLAIM(D29KL52Srtw@06:37), CLAIM(EDtgsIn1meM@09:05), CLAIM(TKZl_UlXhYk@05:01) | consensus |
| 9 | Keep a visible keyboard focus state on every interactive element; if the default outline is removed, design a replacement. | Flux Academy, DesignCourse | CLAIM(D29KL52Srtw@05:58), CLAIM(EDtgsIn1meM@09:19) | consensus |
| 13 | Give every input a persistent visible label; a placeholder is never the label. | DesignCourse, Flux Academy | CLAIM(5-caRWzSQd4@04:02), CLAIM(EDtgsIn1meM@09:51) | consensus |
| 21 | Write error copy that states what happened in plain language and how to fix it, naming the rule that failed (for example a banned character), and color the failing field outline and its message with the error color so label, field, and message read as one problem. | NNgroup, DesignCourse | CLAIM(cCun-ReLTFI@00:41), CLAIM(5-caRWzSQd4@08:36), CLAIM(5-caRWzSQd4@09:32), CLAIM(EKjCC4PwjFo@07:06) | consensus |
| 25 | Make the form primary submit button the strongest-colored element in the form, using the theme primary color. | DesignCourse, Satori Graphics | CLAIM(5-caRWzSQd4@21:40), CLAIM(-5jSCHZIHlg@01:08) | consensus |
| 29 | Hold text contrast at 4.5:1 or better against its background, and verify it with a contrast checker rather than by eye. | Flux Academy, DesignCourse | CLAIM(EDtgsIn1meM@04:23), CLAIM(D29KL52Srtw@03:40) | consensus |
| 34 | Test the whole site with the keyboard alone (tab, arrows, enter, escape) before calling it done. | Flux Academy, DesignCourse | CLAIM(EDtgsIn1meM@09:19), CLAIM(D29KL52Srtw@05:58) | consensus |
| 10 | Write link text that names the destination or action; never ship a link whose text is a generic call like click-through wording. | Flux Academy | CLAIM(EDtgsIn1meM@07:45) | single-source |
| 11 | Use real heading tags (H1, H2, H3) for page structure so screen-reader users and scanners can navigate the outline. | Flux Academy | CLAIM(EDtgsIn1meM@06:57) | single-source |
| 12 | Never convey an instruction or a state through color or shape alone, and when an icon meaning is unclear, replace the icon with a plain word that matches platform conventions users already know. | Flux Academy | CLAIM(EDtgsIn1meM@08:26), CLAIM(TKZl_UlXhYk@04:43), CLAIM(TKZl_UlXhYk@04:50) | single-source |
| 30 | Write alt text that describes the image content; for a linked image, describe its function (home, search) instead of its artwork. | Flux Academy | CLAIM(EDtgsIn1meM@00:43), CLAIM(EDtgsIn1meM@01:12) | single-source |

The full set of 60 laws lives in the sub-skills.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| navigation-wayfinding | references/navigation-wayfinding.md | 12 laws |
| form-input-design | references/form-input-design.md | 16 laws |
| accessibility-audit | references/accessibility-audit.md | 9 laws |
| psychology-visual-hierarchy | references/psychology-visual-hierarchy.md | 11 laws |
| research-flows-process | references/research-flows-process.md | 12 laws |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Current nav item marked with color, weight, or a background | Every nav item identical with nothing showing where you are | Orientation costs less than guessing |
| 2 | A labeled Home item in the nav | Logo as the only way back to home | Not every user knows the logo convention |
| 3 | Secondary nav visibly lighter or smaller than primary nav | Primary and secondary items styled the same | Hierarchy tells the user which set matters |
| 4 | Dropdown parents and their children at different weights | All menu items bold and equally strong | Equal emphasis hides the structure |
| 5 | Hover state that highlights the link under the cursor | Links that do not react to the pointer | Confirmation prevents mis-clicks |
| 6 | Logo left, nav right, footer at the bottom | Nav moved to the bottom or side for novelty | Visitors arrive with a learned blueprint; one site moved its menu to the thumb zone and had to revert |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/ux/.

## Decision tables

### Where to innovate

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Follow the standard placement (logo left, nav right, footer bottom) | Deviate for concept or brand reasons | A for any task-driven or client site; B only with a testable reason and a usability check, because the visitor's mental model punishes novelty in structure (CLAIM(D29KL52Srtw@05:40), CLAIM(d-IaU9qcDGg@02:52)) |
| Total predictability everywhere | Small pattern breaks inside a predictable frame | The frame is settled and the delight lives in micro-interactions; drastic motion drives away the safety-first visitor (CLAIM(d-IaU9qcDGg@04:29), CLAIM(d-IaU9qcDGg@04:47)) |
| Hamburger menu | Inline links | Links fit the viewport: inline. Space runs out: collapse (CLAIM(D29KL52Srtw@04:33)) |

### Form error handling

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Inline message under the field | Summary message near submit | Inline for field-level problems; a summary only as a supplement (CLAIM(EKjCC4PwjFo@06:15)) |
| Explain the rule in text | One-click fix in the message | Prefer the click-able fix; keep the explanation when no shortcut is possible (CLAIM(cCun-ReLTFI@01:06)) |
| Block the invalid submit | Allow and offer undo | Block when data quality matters; allow plus undo when the action is cheap to reverse (CLAIM(cCun-ReLTFI@01:34)) |

### Color and emphasis

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| One brand color plus neutrals | Multiple brand colors | Beginners and most projects: one or two. Multi-color only with a designer who can defend every hue (CLAIM(-5jSCHZIHlg@15:33)) |
| Match the sector's palette | Break the sector palette | Break it only when the new color still fits the industry and the category is a sea of the same hue (CLAIM(-5jSCHZIHlg@04:20)) |
| One strong isolated CTA | Several equally strong elements | Isolate when a single action matters; several strong spots cancel each other (CLAIM(-5jSCHZIHlg@00:36), CLAIM(-5jSCHZIHlg@05:02)) |

### Research artifact choice

| Choice A | Choice B | Pick when |
|----------|----------|-----------|
| Stick-figure storyboard | Polished illustrated storyboard | Low-fi for ideation and feedback; polished only for a client deliverable or a wide audience (CLAIM(bNh54LNUtv8@01:37)) |
| Scenario mapping workshop | Solo flow sketch | Cross-role uncertainty: workshop with four to six people early in the project (CLAIM(dmlFRCZI9gQ@00:36), CLAIM(dmlFRCZI9gQ@02:36)) |
| Five-minute family usability pass | Formal recruited test | Personal projects and portfolio work: the five-minute pass; funded client work: recruit testers including people with disabilities (CLAIM(9viTvO0Okoo@00:24), CLAIM(EDtgsIn1meM@12:04)) |

## Anti-patterns

- Generic link text on buttons and inline links: describe the destination instead (CLAIM(EDtgsIn1meM@07:45)).
- Text baked into images where the words matter (CLAIM(EDtgsIn1meM@02:35)).
- Instructions that rely on color or shape alone (CLAIM(EDtgsIn1meM@08:26)).
- Nav with no active state and no Home item (CLAIM(D29KL52Srtw@00:40), CLAIM(D29KL52Srtw@01:12)).
- Hamburger menu used on a roomy desktop layout (CLAIM(D29KL52Srtw@04:33)).
- Nav placed at the bottom or the side for the sake of being original (CLAIM(D29KL52Srtw@05:40)).
- Text fields that are barely visible against the page (CLAIM(EKjCC4PwjFo@03:28)).
- Placeholder used as the only label (CLAIM(5-caRWzSQd4@04:02)).
- plus 11 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- How far to push originality: DesignCourse tells designers not to be original with nav and logo placement (CLAIM(D29KL52Srtw@05:40)), while Satori Graphics pushes breaking the sector's color convention to stand out (CLAIM(-5jSCHZIHlg@04:20)). Reading: structure stays conventional, brand color may break convention; the two rules operate on different layers.
- Hover intensity: DesignCourse's nav lesson allows bold, underline, icon, or border changes on hover (CLAIM(D29KL52Srtw@03:07)), while its forms lesson insists button hover stay a subtle lightening (CLAIM(5-caRWzSQd4@23:13)). Reading: link hover may add emphasis; a filled button should barely move.
- Testing protocol: Mike Locke has the tester narrate their intended taps rather than perform them (CLAIM(9viTvO0Okoo@03:05)), while DesignSense has users try the shipped app and report what happened (CLAIM(P2W2AnK5aDE@14:10)). Reading: narrated intent is fast and cheap for a personal project; observed use plus feedback is the stronger evidence when the product is real.
- Delight versus safety: Self-Made Web Designer warns that an all-safe design bores the visitor and prescribes small surprises (CLAIM(d-IaU9qcDGg@04:29)), while Satori Graphics warns that any strong contrast point drains attention from the rest of the design (CLAIM(-5jSCHZIHlg@05:02)). Reading: micro-interactions and single-point emphasis are compatible if only one element is isolated and the delight stays small.

## Creator claims (unverified)

- Roughly a billion bits of sensory information per second with only about ten reaching awareness (CLAIM(d-IaU9qcDGg@00:50)).
- Working memory holds about three or four items at once (CLAIM(d-IaU9qcDGg@06:13)).
- Knowing this psychology makes a designer worth a five-figure fee on a project (CLAIM(d-IaU9qcDGg@07:38)).
- Studies reportedly show navigation is easier when a separate Home button exists (CLAIM(D29KL52Srtw@01:17)).
- A 2015 study of top brands reportedly found circles as the main shape in about twenty of fifty logos (CLAIM(-5jSCHZIHlg@06:33)).
- Reported audience data: a large majority of a chocolate brand's social audience was female, which its purple branding targets (CLAIM(-5jSCHZIHlg@14:15)).
- Viewer attention spans can be only a few seconds (CLAIM(-5jSCHZIHlg@05:18)).
- The chat app under redesign was reportedly made confusing on purpose to reward its teenage audience (CLAIM(TKZl_UlXhYk@01:42)).

## Tool-specific (dated)

- Sketch 49 (2018) added native prototyping: hotspots, per-object links, transition direction, and a starting-point artboard (CLAIM(470go6su3Ys@00:09), CLAIM(470go6su3Ys@01:52)).
- Figma component variants (2022 and 2024 workflows) carry form states as variant properties wired with on-tap change-to interactions; instant for state swaps, smart animate around 300ms when something physically moves (CLAIM(5-caRWzSQd4@15:04), CLAIM(5-caRWzSQd4@20:12), CLAIM(EKjCC4PwjFo@08:57)).
- FigJam (2022) supplies a brainstorming toolkit distinct from Figma: stickers with authorship, sections that move as a group, stamp voting, cursor chat, and in-file audio (CLAIM(HGsMNYq889U@01:09), CLAIM(HGsMNYq889U@04:43), CLAIM(HGsMNYq889U@05:58), CLAIM(HGsMNYq889U@06:58)).
- Contrast checking via the Stark plugin for Figma and XD, plus browser devtools accessibility panels (2021) (CLAIM(D29KL52Srtw@03:59)).
- Iconify plugin (2022, 2024) for pulling icons and checkmarks into Figma designs (CLAIM(5-caRWzSQd4@09:45), CLAIM(EKjCC4PwjFo@20:42)).
- Coolors contrast checker and the Webflow accessibility checklist as the referenced audit aids (2024) (CLAIM(EDtgsIn1meM@04:35)).
- Recraft AI (2024) for themed raster and vector imagery that matches the app palette (CLAIM(P2W2AnK5aDE@07:37)).
- Showit cited (2026) as a drag-and-drop builder where size changes do not break the layout (CLAIM(d-IaU9qcDGg@05:15)).

## Hand-off
- Next stage: ds-motion-3d, ds-critique. Agent: `ds-ui-designer`.
- Corpus source: studio-corpus/laws/ux.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
