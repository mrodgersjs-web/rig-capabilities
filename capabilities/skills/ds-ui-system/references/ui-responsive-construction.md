---
name: ui-responsive-construction
tier: sub
parent: ds-ui-system
---

# Ui Responsive Construction

Purpose: inside-out auto layout, explicit child sizing, constraints, min/max wrap, breakpoint variants, 8px grid (laws 19-26).

Load when: the task touches this part of ui systems and components, or a ds-ui-system critique names it. Part of `ds-ui-system`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 8 | Bind boolean variables to layer visibility (right-click the visibility icon in the layer controls) so one click can show or hide content per state | DesignCourse, Flux Academy | CLAIM(Tx45NcbU6aA@19:26), CLAIM(vf1BZ1mG2WE@20:46) | consensus | yes |
| 19 | Construct from the inside out: auto-layout the smallest group, then wrap groups in another auto layout, instead of dropping loose layers into one outer frame | Jesse Showalter | CLAIM(oXDAmwEWlDc@02:42), CLAIM(oXDAmwEWlDc@07:48) | single-source | yes |
| 20 | After wrapping, set each child explicitly to hug contents or fill container; children left on defaults break the moment the parent stretches | Jesse Showalter, DesignCourse | CLAIM(oXDAmwEWlDc@08:23), CLAIM(iLWaIx7tMnU@06:58) | consensus | yes |
| 21 | Anchor fixed decorations with constraints first (avatar top-right, caption bottom-left), then add auto layout on top | Jesse Showalter | CLAIM(oXDAmwEWlDc@02:32) | single-source | yes |
| 22 | Design one layout that stretches until it breaks, and add a breakpoint variant (desktop, tablet, mobile) only at the size where it fails; do not design each device separately | Jesse Showalter | CLAIM(oXDAmwEWlDc@22:48) | single-source | yes |
| 23 | Give fill-container children a min and a max width and turn on wrap so rows reflow; fixed-width children under wrap leave dead space at the row end | Jesse Showalter | CLAIM(oXDAmwEWlDc@20:25), CLAIM(oXDAmwEWlDc@21:04) | single-source | yes |
| 24 | When hiding a child changes a bar's height, set the bar height explicitly so sibling screens stay aligned | Jesse Showalter | CLAIM(oXDAmwEWlDc@14:32) | single-source | yes |
| 25 | Stretch-test the element on the canvas before componentizing, and fix constraints and auto layout until the stretch behaves | Jesse Showalter, DesignCourse | CLAIM(oXDAmwEWlDc@06:29), CLAIM(KWUlkXZOj4g@03:55) | consensus | yes |
| 26 | Keep padding, gaps, and margins on an 8px grid, choosing values divisible by eight | Flux Academy, Jesse Showalter | CLAIM(vf1BZ1mG2WE@16:54), | consensus | yes |

## Anti-patterns for this sub-topic
