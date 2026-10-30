---
name: ds-build-ship
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for build and ship: Build it for real: Webflow, Framer or code, responsive QA, performance, handoff, and the Gate-D stop before anything goes public. 49 laws, 8
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when a design must become a served site, or handoff, responsive QA and performance are due.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides build and ship. Entered by the /design-studio command through design-studio-os, by ds-ai-design-engineer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: a served build with captures at 375/768/1440, performance and a11y results, a handoff doc, a Gate-D request for anything outward, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 ../rig-design-studio-os/tools/claims_check.py capabilities/skills/ds-build-ship/SKILL.md
  - cmd:python3 ../rig-design-studio-os/tools/check_family.py
quality_floor: 0.6
---

# Build and ship

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check code.review --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: code.review, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches build and ship. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-ai-design-engineer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "build it", "Webflow", "Framer", "handoff", "ship", "deploy". Inside a build this stage runs after the stage that feeds it and
before ds-critique.

## Inputs and output contract

Inputs: the finished design artifacts, the platform choice, the target host.
Output: a served build with captures at 375/768/1440, performance and a11y results, a handoff doc, a Gate-D request for anything outward.

## Procedure

1. Design to build handoff: Prepare a design file so a builder can consume it: auto layout, containers, naming, fonts, sizing checks (see references/design-to-build-handoff.md).
2. Builder layout construction: Stacks, grids, wrappers, containers, overflow and baseline work inside Framer/Webflow (see references/builder-layout-construction.md).
3. Components tokens variants: Component and variable discipline plus button and card construction (see references/components-tokens-variants.md).
4. Build motion and effects: Entrance animation sequencing, hover states and embedded 3D or video layers (see references/build-motion-and-effects.md).
5. Check the decision tables below for the choices this stage forces.
6. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
7. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 2 | Name every frame by its role (hero, container, nav, button) before exporting; the names become class names in the builder, and a well named file is a reusable style guide on arrival. | Flux Academy | CLAIM(xHXqj006Q2k@05:03, xHXqj006Q2k@05:12, P5H7zs0RsUM@05:51) | consensus |
| 6 | Auto layout in the design tool and flex in the builder are the same model: same properties, same job of telling the renderer how to place children. Learn the mapping once and use it in both. | Flux Academy | CLAIM(xHXqj006Q2k@01:10, P5H7zs0RsUM@04:30) | consensus |
| 12 | Give full-bleed sections 100 percent width (or 100 viewport height for a one-screen hero) and keep the content inside a centered container so the page scales and the copy stays on a readable measure. | Flux Academy | CLAIM(P5H7zs0RsUM@06:16, BNYLKuIlazA@00:16, BNYLKuIlazA@01:47) | consensus |
| 21 | Cap text width (max width or a percentage of the parent) on every long block so a wide viewport cannot stretch a paragraph into one unbroken line. | Flux Academy | CLAIM(P5H7zs0RsUM@14:48, WLDfFqnqbxI@08:47) | consensus |
| 22 | Anything reused twice (button, nav, footer, card) becomes a component the moment it is styled; edit the master and every instance follows. | Flux Academy | CLAIM(P5H7zs0RsUM@16:35, P5H7zs0RsUM@01:43, BNYLKuIlazA@03:43) | consensus |
| 28 | Reuse the project's predefined heading and paragraph styles instead of hand-setting each text block; only genuinely one-off display type gets its own class. | Flux Academy | CLAIM(P5H7zs0RsUM@14:15, WLDfFqnqbxI@07:10) | consensus |
| 32 | When a headline animates and resizes on the same element, keep the animation and the responsive size as two separate settings and test the preview at more than one width before accepting it. | Flux Academy | CLAIM(P5H7zs0RsUM@06:38, WLDfFqnqbxI@07:31) | consensus |
| 49 | Publish to a staging URL and walk the live site before calling the build done; the preview and the published page are the acceptance surface. | Jesse Showalter | CLAIM(y4Rv-vf01LY@11:07, y4Rv-vf01LY@11:13, 1xAfVDiX1ps@34:06) | consensus |
| 1 | Before touching the builder, read the design and write down the structure it implies: how many top-level groups, what grid it sits on, which elements must resize and which stay fixed. | Flux Academy | CLAIM(WLDfFqnqbxI@00:30, WLDfFqnqbxI@00:50) | single-source |
| 3 | Build the Figma file with auto layout on every container, nested the way the page is nested (page frame, navbar, section, container, columns). A design made of unlogical groups cannot be transferred. | Flux Academy | CLAIM(xHXqj006Q2k@01:34, xHXqj006Q2k@01:47, xHXqj006Q2k@02:23) | single-source |
| 4 | Set the design container to a fixed max width (1200px was used) so it lands as the builder's container width instead of a hard-coded 1440 wrapper that must be deleted after pasting. | Flux Academy | CLAIM(xHXqj006Q2k@02:05, xHXqj006Q2k@00:26) | single-source |
| 5 | Load the fonts into the builder project's settings before copying anything over, otherwise pasted text falls back and the type has to be re-set element by element. | Flux Academy | CLAIM(xHXqj006Q2k@04:32, xHXqj006Q2k@04:49) | single-source |

The full set of 49 laws lives in the sub-skills, plus 17 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| design-to-build-handoff | references/design-to-build-handoff.md | 8 laws |
| builder-layout-construction | references/builder-layout-construction.md | 13 laws |
| components-tokens-variants | references/components-tokens-variants.md | 8 laws |
| build-motion-and-effects | references/build-motion-and-effects.md | 5 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 33 | Use the platform's form builder rather than hand-building inputs: it arrives responsive and generates the input and button components for you. | Jesse Showalter | CLAIM(FGIPeIql9d4@00:38, FGIPeIql9d4@02:16) | single-source |
| 34 | Style a form by editing the input components it created (including loading, disabled, success and hover states), not by styling the copy on the canvas. | Jesse Showalter | CLAIM(FGIPeIql9d4@01:01, FGIPeIql9d4@01:22) | single-source |
| 35 | Give every form a primary destination plus a fallback sink (sheet first, email as backup) before publishing. | Jesse Showalter | CLAIM(FGIPeIql9d4@03:11, FGIPeIql9d4@03:38) | single-source |
| 36 | Add an explicit opt-in checkbox for anything beyond the contact request, such as a newsletter subscription. | Jesse Showalter | CLAIM(FGIPeIql9d4@02:05, FGIPeIql9d4@02:11) | single-source |
| 37 | Verify a form on the published URL: submit a real value, confirm the success and redirect behavior, then confirm the row actually landed in the sink. | Jesse Showalter | CLAIM(FGIPeIql9d4@04:00, FGIPeIql9d4@04:10, FGIPeIql9d4@04:42) | single-source |
| 38 | Test before and after every optimization pass with an objective scoring tool, and read the mobile and desktop results separately; a single score is not a result. | Jesse Showalter | CLAIM(63USLByBGNM@00:47, 63USLByBGNM@01:20, 63USLByBGNM@01:22) | single-source |
| 39 | Run three questions against every image before upload: right format, right size, right compression. | Jesse Showalter | CLAIM(63USLByBGNM@02:02, 63USLByBGNM@02:07) | single-source |
| 40 | Downscale an image to the width it is actually displayed at before exporting; a 1200-pixel-wide asset on a small slot wastes most of its bytes and weakens the platform's own conversion. | Jesse Showalter | CLAIM(63USLByBGNM@03:19, 63USLByBGNM@03:31, 63USLByBGNM@02:50) | single-source |
| 41 | Pick the format by content: a lossy format when transparency is not needed, a transparency-capable format when it is, and a vector file for logos and icons. | Jesse Showalter | CLAIM(63USLByBGNM@03:43, 63USLByBGNM@03:49, 63USLByBGNM@03:57) | single-source |
| 42 | Losslessly compress each export (metadata and unreferenced data stripped) before uploading, and re-measure after the platform converts it. | Jesse Showalter | CLAIM(63USLByBGNM@04:26, 63USLByBGNM@05:00, 63USLByBGNM@05:24) | single-source |
| 43 | Decide per video whether it is hosted or embedded: a short looping clip of a person talking earns the weight, long-form content belongs on a third-party host so the page stays fast. | Jesse Showalter | CLAIM(63USLByBGNM@06:12, 63USLByBGNM@06:30, 63USLByBGNM@06:46) | single-source |
| 44 | Export video at the size and compression the slot needs and run it through a compressor; an untouched high-resolution master is the slowest asset on the page. | Jesse Showalter | CLAIM(63USLByBGNM@07:08, 63USLByBGNM@07:21, 63USLByBGNM@07:34) | single-source |
| 45 | Count the dynamic elements (tickers, slideshows, carousels, iframe embeds, 3D scenes) as a budget: each one costs bandwidth, so cut the count instead of the quality. | Jesse Showalter | CLAIM(63USLByBGNM@08:07, 63USLByBGNM@08:15, 63USLByBGNM@08:36) | single-source |
| 46 | Treat blur and heavy drop shadows as performance decisions: keep them selective, and respect the browser's limits the way print design respects paper. | Jesse Showalter | CLAIM(63USLByBGNM@08:52, 63USLByBGNM@09:12, 63USLByBGNM@09:31) | single-source |
| 47 | Reduce the render tree: split an endless one-page site into real pages, use fewer animated elements, and flatten stacks that only exist to group things visually. | Jesse Showalter | CLAIM(63USLByBGNM@10:41, 63USLByBGNM@11:07, 63USLByBGNM@11:25) | single-source |
| 48 | Depth in a layers panel understates cost: a visible list of about ten layers can still compile to more than a thousand rendered nodes, so inspect nesting, not layer count. | Jesse Showalter | CLAIM(63USLByBGNM@11:56, 63USLByBGNM@12:01) | single-source |
| 49 | Publish to a staging URL and walk the live site before calling the build done; the preview and the published page are the acceptance surface. | Jesse Showalter | CLAIM(y4Rv-vf01LY@11:07, y4Rv-vf01LY@11:13, 1xAfVDiX1ps@34:06) | consensus |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | A pasted design that arrives with responsive behavior, working buttons and named classes. | A pasted design that arrives as fixed or absolutely placed boxes. | The exporter can only transfer layout logic that was authored as layout logic. |
| 2 | A hero whose text sits in a wrapper with center alignment and cannot be moved. | A hero where an element is dragged to a spot that happens to look right. | Free placement looks right at one width and breaks at every other. |
| 3 | Content centered in a fixed container with equal side tracks on a wide screen. | Content pinned to the full canvas width of the desktop artboard. | The container is what makes one design work across screen widths. |
| 4 | One grid class shared by every aligned group, with a combo class for the single exception. | Three near-identical grids styled separately. | Separate copies must be re-tuned three times per breakpoint. |
| 5 | A card whose corner radius clips its own image via overflow hidden. | A rounded card whose square image still bleeds past the corners. | Radius applies to the container, the child image needs clipping to obey it. |
| 6 | A button reused from one master with a hover variant. | Several hand-styled button copies with slightly different padding. | Copies drift; a master keeps the system consistent. |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/build_ship/.

## Decision tables

| Decision | Pick A when | Pick B when | citation |
|---|---|---|---|
| Hand-build the site vs import the design | Import: standard layout blocks and a well structured design file (the estimate is minutes rather than an hour). | Hand-build: first time on the platform, or a bespoke layout the exporter cannot express (sliders, custom interaction logic). | CLAIM(xHXqj006Q2k@06:32, xHXqj006Q2k@07:02, P5H7zs0RsUM@00:25) |
| One big grid vs several grouped grids | One grid: everything on the screen truly shares one column rhythm and no breakpoint work is expected. | Grouped grids under one parent: a bento or dashboard page that must restack per breakpoint. | CLAIM(WLDfFqnqbxI@01:37, WLDfFqnqbxI@14:47) |
| Pixels vs viewport units for type | Pixels: body and UI text that must stay legible at a floor size. | Viewport units: a single display headline that must fit one line at every width. | CLAIM(WLDfFqnqbxI@07:23, WLDfFqnqbxI@16:03) |
| Absolute positioning | Decoration and backdrops that must sit behind content. | Never for content; it is what makes an export unmaintainable. | CLAIM(BNYLKuIlazA@06:14, xHXqj006Q2k@02:49) |

## Anti-patterns


## Hand-off
- Next stage: ds-critique. Agent: `ds-ai-design-engineer`.
- Corpus source: studio-corpus/laws/build_ship.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
