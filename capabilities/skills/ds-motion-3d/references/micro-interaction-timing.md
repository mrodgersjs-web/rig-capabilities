---
name: micro-interaction-timing
tier: sub
parent: ds-motion-3d
---

# Micro Interaction Timing

Purpose: pick duration, easing, and one signal per beat, then preview until the overshoot and the simultaneous start are gone.

Load when: the task touches this part of motion and 3d, or a ds-motion-3d critique names it. Part of `ds-motion-3d`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 13 | Keep a tap or a card drag near 100 to 300 ms. A hover grow can run near 450 ms, a drag that also shifts a gradient near 500 ms. Stretch past that only when the path is the content: a line draw near 3 seconds, a readable text slider near 800 ms, a liquid fill near 4 to 5 seconds, or a scroll gap tall enough to hold the beat. | Flux Academy, Punit Chawla, Jesse Showalter | CLAIM(hHp4FGVcHjY@04:00, hHp4FGVcHjY@04:42, vCru1T5ajF8@11:07, vCru1T5ajF8@04:08, vCru1T5ajF8@17:10, fB7h2RxXpqA@08:44, fB7h2RxXpqA@12:23, EEj3PYjwyC0@05:15, K0Dh-8rHMLk@05:38, P8hh8K1EuWE@04:34) | consensus | yes |
| 14 | Hold a cycling headline on each word about 1 to 1.5 seconds, then swap in about 200 ms ease-out. Mix short and long words. A cycle that only grows then shrinks feels mechanical. | Flux Academy | CLAIM(vCru1T5ajF8@24:14, vCru1T5ajF8@24:47, vCru1T5ajF8@25:32, vCru1T5ajF8@25:34) | single-source | yes |
| 15 | Do not ship linear motion. Use ease-out on a drag or an arrival, ease-in-out on a tap or a loop, and a spring only on a physical knob. If the spring leaves the track, shrink the knob and lower the damping until it kisses the edge and settles inside. | Flux Academy, Jesse Showalter, kwoo studio, Punit Chawla | CLAIM(4YFRYho3vuM@03:04, hHp4FGVcHjY@07:43, hHp4FGVcHjY@09:17, hHp4FGVcHjY@10:08, gXOY8Ts44dA@09:00, gXOY8Ts44dA@09:07, -QuzxYtwkyU@09:46, -QuzxYtwkyU@10:08, K0Dh-8rHMLk@05:25, K0Dh-8rHMLk@05:31, fB7h2RxXpqA@08:36) | consensus | yes |
| 16 | Change one signal per beat. If an icon already rotates from plus to minus, do not recolor it in the same 300 ms. If a fill is fading, do not also animate stroke radius. | Flux Academy | CLAIM(hHp4FGVcHjY@15:46, hHp4FGVcHjY@17:03, hHp4FGVcHjY@18:10) | single-source | yes |
| 17 | Shape the curve on purpose. An S-curve eases in and out. A handle pulled past the baseline bounces at that end. A straight path accelerates. Trial it; do not accept the default. | Flux Academy | CLAIM(20IfkyJigKg@08:18, 20IfkyJigKg@08:26, 20IfkyJigKg@08:56) | single-source | yes |
| 18 | Make the selected card the only full-opacity, stroked, unrotated item. Park neighbors near 70 percent opacity and a small tilt (about 8 degrees) so depth reads without hiding the choice. | Flux Academy | CLAIM(vCru1T5ajF8@06:22, vCru1T5ajF8@06:52, vCru1T5ajF8@07:00, vCru1T5ajF8@09:16) | single-source | yes |
| 19 | Stagger the start. Offset layer timing so the group does not depart on one frame, and give inner chips of a 3D hover different loop offsets so they do not move as one slab. | kwoo studio, Jesse Showalter | CLAIM(-QuzxYtwkyU@10:47, -QuzxYtwkyU@10:54, -QuzxYtwkyU@11:00, gXOY8Ts44dA@04:10, gXOY8Ts44dA@08:22, gXOY8Ts44dA@08:32) | consensus | yes |

## Anti-patterns for this sub-topic
