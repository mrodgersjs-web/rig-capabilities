---
name: ds-imagery
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for imagery and art direction: Choose and produce imagery: art direction, photography or illustration style, AI image generation, and provenance for every asset. 50 laws, 26
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when the page needs photography, illustration, AI images or an art direction decision.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides imagery and art direction. Entered by the /design-studio command through design-studio-os, by ds-brand-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: imagery.md: art direction (subject, light, composition, treatment), asset list with sources, provenance sidecar per asset (source, license, generator), with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 ../rig-design-studio-os/tools/claims_check.py capabilities/skills/ds-imagery/SKILL.md
  - cmd:python3 ../rig-design-studio-os/tools/check_family.py
quality_floor: 0.6
---

# Imagery and art direction

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches imagery and art direction. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-brand-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "images", "photos", "illustration", "AI image", "art direction", "hero image". Inside a build this stage runs after the stage that feeds it and
before ds-conversion-copy.

## Inputs and output contract

Inputs: the story the page tells, the brand voice, the budget for real photography versus generated imagery.
Output: imagery.md: art direction (subject, light, composition, treatment), asset list with sources, provenance sidecar per asset (source, license, generator).

## Procedure

1. Isometric build: grid math, face drawing, one light, shadow, and layer naming (laws 1-10) (see references/isometric-build.md).
2. Vector crop and mask: web file setup, motif clusters, editable type masks, and crop choice (laws 11-25) (see references/vector-crop-and-mask.md).
3. Hero texture and cutout: subject-matched texture, mesh gradients, and the speed-versus-accuracy cutout ladder (laws 26-40) (see references/hero-texture-and-cutout.md).
4. Texture brush and pattern: watercolor brushes, seamless tiles, and scatter confetti (laws 41-50) (see references/texture-brush-and-pattern.md).
5. Check the decision tables below for the choices this stage forces.
6. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
7. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 17 | Trim anything that spills past the artboard with a rectangle snapped to the canvas edge, fill not stroke, used as a clipping mask. Do not manually delete overflow paths. | Satori Graphics, Envato Tuts+ | CLAIM(_iafygrxKMI@04:30, _iafygrxKMI@04:44, _iafygrxKMI@04:56, y1zR4h2aEDw@09:50, GWa3vVQXH8M@02:49) | consensus |
| 19 | Use square, rectangular, angled, and circular guides both on paper and in software. Snap-to-grid produces alignment and proportion fast enough that a simple mark can go pencil to vector without a trace. Clean a hand-drawn wordmark with guidelines before calling the logo type done. | Flux Academy, Satori Graphics | CLAIM(q3ACHGp6bFA@00:58, q3ACHGp6bFA@01:07, q3ACHGp6bFA@01:15, q3ACHGp6bFA@01:26, eFHxknDs4Mk@02:53) | consensus |
| 23 | Plan the crop on the artboard before you cut anything. Pick the crop by what you need: visual hide versus permanent delete, photo versus vector. A clipping mask or opacity mask hides and stays editable; Pathfinder crop and the eraser (alt-drag a rectangle) delete forever. | Envato Tuts+, Satori Graphics | CLAIM(GWa3vVQXH8M@00:05, GWa3vVQXH8M@00:28, GWa3vVQXH8M@03:08, GWa3vVQXH8M@03:23, GWa3vVQXH8M@04:22, _iafygrxKMI@04:30) | consensus |
| 49 | Start a scatter brush small. You can scale up; you cannot always go smaller. Circles: fixed scale, random spacing and scatter pushed high, no rotation. Stars: random scale kept modest, plus rotation, because a pointy shape shows the spin. Set colorization to tints and shades or every recolor means reopening the brush. | Every Tuesday, Envato Tuts+ | CLAIM(D3iJ_aVVJDE@01:06, D3iJ_aVVJDE@02:10, D3iJ_aVVJDE@02:52, D3iJ_aVVJDE@03:12, D3iJ_aVVJDE@06:11, APzkcH27HY0@05:47) | consensus |
| 1 | Build an isometric grid from a square rectangular grid: vertical and horizontal divisions must be the same count, rotate 45 degrees, then set height to 57.74 percent exactly. Do not record that height change as an action; the transform stores a fixed height, not a percent. | Satori Graphics | CLAIM(eFHxknDs4Mk@01:06, eFHxknDs4Mk@01:50, VPrXNNgobAY@00:34, VPrXNNgobAY@01:07) | single-source (one creator, two videos) |
| 2 | Lock the isometric grid and send it behind every object before drawing. Trace faces with the pen as stroke, then flip stroke to fill. Hold shift while scaling any face so the grid alignment survives. | Satori Graphics | CLAIM(eFHxknDs4Mk@02:19, eFHxknDs4Mk@02:53, eFHxknDs4Mk@03:39, eFHxknDs4Mk@03:49, VPrXNNgobAY@01:28, VPrXNNgobAY@01:51) | single-source (one creator, two videos) |
| 3 | Keep vertical edges the same length across a face. Use the caps-lock crosshair and toggle smart guides when the pen needs a precise vertical snap. | Satori Graphics | CLAIM(eFHxknDs4Mk@02:53, eFHxknDs4Mk@03:02) | single-source |
| 4 | Limit an isometric scene to two base hues plus one pale version of each. Cast shadows as black at 25 percent opacity, sampled and reused, not as a third hue. | Satori Graphics | CLAIM(eFHxknDs4Mk@00:37, eFHxknDs4Mk@05:21, eFHxknDs4Mk@07:09) | single-source |

The full set of 50 laws lives in the sub-skills.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| isometric-build | references/isometric-build.md | 10 laws |
| vector-crop-and-mask | references/vector-crop-and-mask.md | 15 laws |
| hero-texture-and-cutout | references/hero-texture-and-cutout.md | 15 laws |
| texture-brush-and-pattern | references/texture-brush-and-pattern.md | 10 laws |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | Grid rotated 45 degrees, then height set to 57.74 percent, locked behind the art | A 45-degree square grid used as if it were already isometric | The second transform is what makes the angles isometric; the first alone is just a diamond grid |
| 2 | Two base hues, each with a pale version, plus black at 25 percent for shadow | A new hue invented for every face and every shadow | The pale pair keeps the scene in one family; the black shadow is the depth, not a third brand color |
| 3 | Rear face darker than the front, original outline brought forward | Both faces the same value, copy left in front | The value step and the stacking order are what read as thickness |
| 4 | Light in one chosen corner, matched by highlights and by the ground shadow | Highlights from one side and a shadow from another | One light source is what makes the object and the ground agree |
| 5 | Named, labeled layers you can hide | An unlabeled stack you regret by the end of the piece | Finding one part of a multi-face object without names costs more than labeling as you go |
| 6 | Motifs on a locked gradient, corners rounded, cluster rotated 45 degrees, clipped to the artboard | Rectangles left square, unrotated, spilling off the canvas | Rounding plus rotation turns a box stack into a graphic; the mask is what makes the crop clean |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/imagery/.

## Decision tables

| decision | option A | option B | pick A when | pick B when | citation |
|---|---|---|---|---|---|
| Crop method | Clipping mask or opacity mask | Pathfinder crop or eraser | You may still edit the hidden art, or the file is a complex vector | The cut must be gone forever and the shape is simple | CLAIM(GWa3vVQXH8M@03:08, GWa3vVQXH8M@04:22, GWa3vVQXH8M@04:05) |
| Mesh gradient | Noisy Gradients plugin PNG | Hand-built blurred shapes | You need a library fast and will not animate | You must move shapes, match a photo, or loop the gradient | CLAIM(fkvB1PrII2E@00:22, fkvB1PrII2E@01:20) |
| Cutout start | Select Subject or Remove Background | Pen, then brush on the mask | The edge can be approximate, or the image is short-lived | The edge is the product (cover, gallery, retouch) | CLAIM(ntk3IVzfIYs@03:54, ntk3IVzfIYs@17:45, ntk3IVzfIYs@19:15) |
| Color-based select | Focus Area | Color Range | The ground is blurred by a shallow depth of field | Subject and ground are different hues | CLAIM(ntk3IVzfIYs@04:47, ntk3IVzfIYs@09:19) |
| Edge cleanup | Pen path turned into a mask | Brush on an existing mask | The whole silhouette must be smooth | An automatic mask is close and only needs tidying | CLAIM(ntk3IVzfIYs@19:36, ntk3IVzfIYs@23:56) |
| Watercolor brush | Bristle brush with low density and stiffness | Traced scan as an art brush, tints and shades | You are drawing new strokes and can live with brush options | You need a real painted edge and must recolor it | CLAIM(APzkcH27HY0@00:45, APzkcH27HY0@05:47) |
| Pattern background | Two squares: fill plus mask, then crop a duplicate | One square used as both fill and mask | You need a colored ground and a still-editable original | The pattern must stay transparent | CLAIM(ITRZ75OKrG0@07:32, ITRZ75OKrG0@09:13) |
| Scatter shape | Fixed scale, no rotation | Random scale plus rotation | The motif is a circle | The motif has points that should spin (stars) | CLAIM(D3iJ_aVVJDE@01:51, D3iJ_aVVJDE@06:11) |
| Hero imagery | Subject-matched texture and depth objects | A photo behind the type | The layout is already sound and only feels generic | The photo is the content, and type contrast is solved first | CLAIM(TaGO9l4EYOk@00:43, TaGO9l4EYOk@10:00) |

## Anti-patterns

- Recording the isometric height change as an action. The action stores a fixed height, not 57.74 percent. CLAIM(eFHxknDs4Mk@01:16, eFHxknDs4Mk@01:56)
- Leaving snap-to-grid on for a free vector background when you do not use it. CLAIM(y1zR4h2aEDw@01:02)
- Shipping stock illustration unchanged. CLAIM(q3ACHGp6bFA@03:20)
- Filling a correct but boring layout with a background photo. CLAIM(TaGO9l4EYOk@00:43)
- Leaving a texture at full opacity after it kills contrast. CLAIM(TaGO9l4EYOk@03:50)
- Pathfinder-cropping a complex vector and keeping the artifacts. CLAIM(GWa3vVQXH8M@04:05)
- Accepting the first Remove Background pass. It missed the beak and part of the branch in the demo. CLAIM(ntk3IVzfIYs@02:09, ntk3IVzfIYs@02:16)
- Using the magic wand on a close-value edge. CLAIM(ntk3IVzfIYs@11:22)
- plus 6 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Depth in a flat layout. Satori builds isometric depth with a pen, a grid, and a darker rear face. Flux (2024) builds depth by inflating a 3D material and stacking objects in front of and behind type. Different jobs, not a contradiction: illustration versus a web hero. CLAIM(VPrXNNgobAY@02:53, TaGO9l4EYOk@05:21)
- How hard to crop. Satori and Envato both end a vector background with a clipping mask. Envato adds: if the trim must be permanent, use the eraser or Pathfinder crop, and do not use Pathfinder crop on a complex file. CLAIM(_iafygrxKMI@04:30, GWa3vVQXH8M@04:05, GWa3vVQXH8M@04:22)
- Automatic versus drawn cutouts. Flux treats Remove Background as a start that often fails on fine edges, and spends the rest of the video on manual tools. No other creator in this set defends the one-click pass as final. CLAIM(ntk3IVzfIYs@02:16, ntk3IVzfIYs@26:25)
- Recoloring a painted stroke. Envato says a placed scan cannot change color, so trace it. Every Tuesday stamps a desaturated brush and recolors with a gradient overlay, which keeps the texture raster. Both work; they are not the same asset. CLAIM(APzkcH27HY0@04:27, dBmUQ1IWqX4@06:38)

## Creator claims (unverified)

- Flux Academy scored Photoshop Remove Background a solid 5 out of 10 on one parrot photo in 2022. That is a creator grade of one image, not a measured accuracy rate. CLAIM(ntk3IVzfIYs@02:20)
- Flux Academy said Photoshop had been the industry-standard photo application for 25 years, as a reason to teach it rather than an online remover. Not verified here. CLAIM(ntk3IVzfIYs@01:04)

## Tool-specific (dated)

- Illustrator CC live corners versus the round-corners effect on CS. Satori uses both paths in 2018-2019. CLAIM(eFHxknDs4Mk@09:09, VPrXNNgobAY@02:14, y1zR4h2aEDw@04:28)
- Illustrator CC freeform gradient versus a gradient mesh on older builds, 2018. CLAIM(VPrXNNgobAY@16:48)
- Illustrator 3D materials, inflate, and ray-traced render, shown 2024. Match material repeat (200 percent in the demo), light from top left, render high with ray tracing on. CLAIM(TaGO9l4EYOk@01:42, TaGO9l4EYOk@02:58, TaGO9l4EYOk@05:21)
- Photoshop sketch stack, 2019: photocopy base, cutout plus find edges, angled strokes, crosshatch, high pass on hard light. Opacity steps are part of the look (14 percent drafts, shading 12 then 5 percent, sharpen 76 percent). CLAIM(VM4KdeTcwhw@01:33, VM4KdeTcwhw@06:18)
- Photoshop rubber stamp, 2019: Filter Gallery sketch stamp at light/dark balance 4 and smoothness 1; circle strokes 6 px and 4 px; scales 95, 75, and 70 percent. Grunge brushes are an installed asset, not a default. CLAIM(scG966JJfJk@03:30, scG966JJfJk@01:17)
- Illustrator Crop Image is CC-only (2020 demo). Older builds use Mask in the control bar, which hides rather than deletes. CLAIM(GWa3vVQXH8M@00:50, GWa3vVQXH8M@01:47)
- Figma mesh gradient, 2023: Noisy Gradients plugin, or pen shapes plus layer blur (about 450 on a 2000 px frame) and a grain file on soft light. Smart animate at 6000 to 7000 ms. CLAIM(fkvB1PrII2E@00:22, fkvB1PrII2E@03:26, fkvB1PrII2E@06:37)
- Photoshop Remove Background, Select Subject, Focus Area, Object Selection, 2022. The one-click remover is Select Subject plus a mask. CLAIM(ntk3IVzfIYs@01:31, ntk3IVzfIYs@03:54, ntk3IVzfIYs@11:49)
- plus 3 more in the corpus law file studio-corpus/laws/imagery.md

## Hand-off
- Next stage: ds-conversion-copy. Agent: `ds-brand-designer`.
- Corpus source: studio-corpus/laws/imagery.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
