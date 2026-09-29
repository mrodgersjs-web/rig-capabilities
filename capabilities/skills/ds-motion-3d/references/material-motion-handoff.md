---
name: material-motion-handoff
tier: sub
parent: ds-motion-3d
---

# Material Motion Handoff

Purpose: stroke-icon paths, soft materials, extruded light, atmospheric noise, and a clean send into a timeline app.

Load when: the task touches this part of motion and 3d, or a ds-motion-3d critique names it. Part of `ds-motion-3d`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 45 | Path-draw only stroke icons, not filled shapes. Pull the icon out of its frame, flatten to one outline, and ungroup a multi-part mark before you flatten each part. Export SVG for a product and a video file when the mock itself must play the icon. | Punit Chawla | CLAIM(EEj3PYjwyC0@00:40, EEj3PYjwyC0@00:48, EEj3PYjwyC0@01:00, EEj3PYjwyC0@01:09, EEj3PYjwyC0@02:26, EEj3PYjwyC0@02:35, EEj3PYjwyC0@03:05, EEj3PYjwyC0@03:22) | single-source | no |
| 46 | A soft raised control uses the page color as its fill, then two shadows: a dark one about +4, +4, blur 12, near 15 to 20 percent opacity, and a light one about -4, -4, blur 12, near 5 to 10 percent, with corner radius near 24. On hover, grow it, push the radius toward a circle, widen the light shadow, and ease-in-out near 450 ms. A drag level moves the knob and the gradient together in one smart animate near 500 ms. | Punit Chawla | CLAIM(fB7h2RxXpqA@02:00, fB7h2RxXpqA@02:02, fB7h2RxXpqA@02:37, fB7h2RxXpqA@02:41, fB7h2RxXpqA@02:46, fB7h2RxXpqA@03:22, fB7h2RxXpqA@03:42, fB7h2RxXpqA@02:53, fB7h2RxXpqA@07:17, fB7h2RxXpqA@07:25, fB7h2RxXpqA@08:36, fB7h2RxXpqA@12:00) | single-source | no |
| 47 | Extruded type needs a ground plane in the same scene, thickness set on the depth axis, a thin bevel, and two lights: one casting a soft shadow under the letters, one picking out the counters. Keep diffuse, highlight, and shadow colors in one hue. Render, stop if it is wrong, change the light or the material, and render again. | Envato Tuts+ | CLAIM(8D6b3McyhhU@00:28, 8D6b3McyhhU@00:50, 8D6b3McyhhU@01:16, 8D6b3McyhhU@01:34, 8D6b3McyhhU@01:49, 8D6b3McyhhU@02:15, 8D6b3McyhhU@02:26, 8D6b3McyhhU@02:45, 8D6b3McyhhU@03:06, 8D6b3McyhhU@03:17, 8D6b3McyhhU@03:49) | single-source | no |
| 48 | Build atmosphere from noise, not a painted puff. Raise contrast (a starting point near 75), scale width and height separately so the mass is not a square, drive a continuous loop from time, and add a second drift so it travels (sideways plus a little up). Sit it near 20 percent opacity. Mask the travel path and feather the mask until the edge disappears. | Envato Tuts+ | CLAIM(ptQ6Re6JvWM@01:47, ptQ6Re6JvWM@02:05, ptQ6Re6JvWM@02:18, ptQ6Re6JvWM@02:30, ptQ6Re6JvWM@02:44, ptQ6Re6JvWM@03:06, ptQ6Re6JvWM@04:06, ptQ6Re6JvWM@05:08, ptQ6Re6JvWM@06:14, ptQ6Re6JvWM@06:51, ptQ6Re6JvWM@07:08) | single-source | no |
| 49 | A liquid icon is a smoothed mesh (about 3 to 4 subdivisions), colored with a depth gradient, then displaced with a smoother noise at low scale (about 10 to 15) and modest strength (about 10 to 20). Use two states, start on load, cycle, and do not rewind. Ease out over about 4 to 5 seconds. Show it through a glyph by subtracting the icon from a rectangle that matches the page color. | Punit Chawla | CLAIM(K0Dh-8rHMLk@01:28, K0Dh-8rHMLk@01:36, K0Dh-8rHMLk@01:42, K0Dh-8rHMLk@02:00, K0Dh-8rHMLk@02:51, K0Dh-8rHMLk@03:03, K0Dh-8rHMLk@03:10, K0Dh-8rHMLk@03:20, K0Dh-8rHMLk@03:34, K0Dh-8rHMLk@05:23, K0Dh-8rHMLk@05:36, K0Dh-8rHMLk@08:04, K0Dh-8rHMLk@08:11) | single-source | no |
| 50 | Hand a layout to a motion app from a blank-file copy, not the team file. Ungroup auto layout before send, or accept extra precomps. Rasterize ornaments you will not animate per layer. If the plugin reference image arrives wrong, export the PNG yourself. Frame fills often do not transfer: rebuild the background as a solid sampled from the source. Keyframe the arrival first (about 30 frames), move the start, and pair position with opacity from 0 to 100. | kwoo studio | CLAIM(-QuzxYtwkyU@04:16, -QuzxYtwkyU@04:32, -QuzxYtwkyU@03:35, -QuzxYtwkyU@03:53, -QuzxYtwkyU@03:22, -QuzxYtwkyU@06:18, -QuzxYtwkyU@07:17, -QuzxYtwkyU@08:08, -QuzxYtwkyU@08:29, -QuzxYtwkyU@09:10, -QuzxYtwkyU@09:20) | single-source | yes |

## Anti-patterns for this sub-topic
