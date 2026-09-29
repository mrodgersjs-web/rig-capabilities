---
name: scroll-scrub-and-3d
tier: sub
parent: ds-motion-3d
---

# Scroll Scrub And 3D

Purpose: sticky gaps, a scrubbed product clip, and transforms or meshes that do not reflow the page.

Load when: the task touches this part of motion and 3d, or a ds-motion-3d critique names it. Part of `ds-motion-3d`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 28 | Hijack scroll with one sticky block plus invisible gap frames under it, then release back to normal scrolling. Gap height is the duration: shorter passes faster, taller holds longer. | Jesse Showalter | CLAIM(P8hh8K1EuWE@00:22, P8hh8K1EuWE@00:35, P8hh8K1EuWE@03:51, P8hh8K1EuWE@04:34, P8hh8K1EuWE@04:42, P8hh8K1EuWE@07:56) | single-source | yes |
| 29 | Sticky fails unless every parent overflow is visible. The sticky layer itself may stay overflow hidden. Without empty space below the block, nothing sticks. | Jesse Showalter | CLAIM(P8hh8K1EuWE@02:18, P8hh8K1EuWE@02:30, P8hh8K1EuWE@02:46, P8hh8K1EuWE@03:14) | single-source | yes |
| 30 | Drive a scroll-variant effect from named scroll sections entering view, and replay it in both directions. Match section names to layer names. The effect only exists on a component that already has variants. | Jesse Showalter | CLAIM(P8hh8K1EuWE@05:01, P8hh8K1EuWE@05:04, P8hh8K1EuWE@05:09, P8hh8K1EuWE@05:30, P8hh8K1EuWE@05:43, P8hh8K1EuWE@06:08, P8hh8K1EuWE@06:22) | single-source | yes |
| 31 | Before scroll motion, strip the page: one body face, at most one accent face, a near-monochrome palette, and deliberate empty space. A cramped page will not look costly just because something moves. | Self-Made Web Designer | CLAIM(q5UFK4ziDuE@00:53, q5UFK4ziDuE@01:01, q5UFK4ziDuE@01:06, q5UFK4ziDuE@02:13, q5UFK4ziDuE@02:18, q5UFK4ziDuE@02:35) | single-source | yes |
| 32 | Treat a product scroll shot as a video scrubbed by scroll position, like stop motion, not a model redrawn on every pixel. Generate it from a first frame and a last frame, then lock the closest still as the reference for the rest. | Self-Made Web Designer | CLAIM(q5UFK4ziDuE@02:55, q5UFK4ziDuE@03:00, q5UFK4ziDuE@03:59, q5UFK4ziDuE@04:03, q5UFK4ziDuE@04:05, q5UFK4ziDuE@04:53) | single-source | yes |
| 33 | The clip must play cleanly forward and backward and stay one object. If the generator keeps a wrong part, mark the still (arrows, what moves where) instead of restating the prompt. | Self-Made Web Designer | CLAIM(q5UFK4ziDuE@05:36, q5UFK4ziDuE@05:45, q5UFK4ziDuE@06:06, q5UFK4ziDuE@06:10) | single-source | yes |
| 34 | Do not scrub a raw video in the browser; precompute frames or the playhead stutters. Fade the clip edges so a background that misses the page color does not draw a hard rectangle on other monitors. | Self-Made Web Designer | CLAIM(q5UFK4ziDuE@06:48, q5UFK4ziDuE@06:53, q5UFK4ziDuE@07:00, q5UFK4ziDuE@07:02, q5UFK4ziDuE@07:50, q5UFK4ziDuE@08:39) | single-source | yes |
| 35 | Kill hard edges on soft effects. Feather a smoke mask by hundreds of pixels, fade a scrubbed clip into the page, and build soft shadow with blur rather than a crisp stroke. | Envato Tuts+, Self-Made Web Designer, Punit Chawla | CLAIM(ptQ6Re6JvWM@07:45, ptQ6Re6JvWM@07:51, ptQ6Re6JvWM@08:01, q5UFK4ziDuE@08:39, fB7h2RxXpqA@02:29, fB7h2RxXpqA@02:41) | consensus | yes |
| 36 | Scale, rotate, skew, and push depth with transforms, not by changing width and height. A layout-size change shoves the neighbors; a transform does not. | Jesse Showalter | CLAIM(gXOY8Ts44dA@00:49, gXOY8Ts44dA@01:00, gXOY8Ts44dA@01:05, gXOY8Ts44dA@02:57) | single-source | yes |
| 37 | A flat rotate reads as a sticker. Turn on 3D rotation and set perspective so the axes share one vanishing point. Set the origin if the pivot should not be the center. Hide the back face only when the reverse side should vanish. Drop skew if the card looks broken. | Jesse Showalter | CLAIM(gXOY8Ts44dA@01:30, gXOY8Ts44dA@01:39, gXOY8Ts44dA@01:56, gXOY8Ts44dA@02:00, gXOY8Ts44dA@02:33, gXOY8Ts44dA@02:45, gXOY8Ts44dA@03:10, gXOY8Ts44dA@03:45) | single-source | yes |
| 38 | For a 3D hover, wrap the card in a frame so transform controls exist, absolutely position the inner pieces, set overflow to visible, and round the container (about 30). Put base transforms on the closed variant and the offset on the open variant. Trigger on mouse enter and mouse leave, and preserve 3D on parent and children. | Jesse Showalter | CLAIM(gXOY8Ts44dA@04:36, gXOY8Ts44dA@04:42, gXOY8Ts44dA@04:54, gXOY8Ts44dA@05:18, gXOY8Ts44dA@06:00, gXOY8Ts44dA@06:15, gXOY8Ts44dA@06:42, gXOY8Ts44dA@06:50, gXOY8Ts44dA@07:58) | single-source | yes |

## Anti-patterns for this sub-topic
- Deleting a layer in the start state and expecting a fade or a travel. CLAIM(hHp4FGVcHjY@02:45, 20IfkyJigKg@16:45)
- Animating stroke radius and opacity together on an expanding panel. CLAIM(hHp4FGVcHjY@17:03)
- Building a frame per hover-and-active combination. CLAIM(20IfkyJigKg@03:27)
- Putting a scroll-variant effect on text that has no variants. CLAIM(P8hh8K1EuWE@05:09)
