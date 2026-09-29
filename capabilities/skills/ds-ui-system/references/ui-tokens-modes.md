---
name: ui-tokens-modes
tier: sub
parent: ds-ui-system
---

# Ui Tokens Modes

Purpose: variables as two-layer tokens, named scale levels, theme modes, boolean visibility bindings (laws 1-8).

Load when: the task touches this part of ui systems and components, or a ds-ui-system critique names it. Part of `ds-ui-system`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 1 | Store every repeated design value (color, gap, radius, spacing) as a named variable and bind the property to it, so one edit updates all usages instead of re-entering values per element | Flux Academy, Jesse Showalter | CLAIM(GUupJJC5Ac4@00:18), CLAIM(oCVG6DFCTz4@10:15) | consensus | yes |
| 2 | Build tokens in two layers: a primitives collection of raw values, then a semantic collection whose names state the role (button, link, heading, body) and reference the primitives | Flux Academy | CLAIM(GUupJJC5Ac4@04:07), CLAIM(GUupJJC5Ac4@04:07) | single-source | yes |
| 3 | Choose variables over shared styles whenever one role must recolor without touching the others: repointing the button token leaves link and logo usages intact | Flux Academy | CLAIM(GUupJJC5Ac4@05:35) | single-source | yes |
| 4 | Group variables into collections by kind (colors, numbers, booleans) and attach a short description to each naming where it applies | DesignCourse, Punit Chawla | CLAIM(Tx45NcbU6aA@02:35), CLAIM(IO30Ta7aqF0@01:06) | consensus | no |
| 5 | Name number variables as scale levels (five for 40px radius, two for a 16px gap) and bind components to the level, never to the raw pixel value | Jesse Showalter | CLAIM(oCVG6DFCTz4@10:15) | single-source | yes |
| 6 | Implement themes as one extra mode per variable (light, dark), fill each mode with its own values, then flip the frame mode from the layer panel selector | Flux Academy, DesignCourse, Punit Chawla | CLAIM(GUupJJC5Ac4@06:13), CLAIM(Tx45NcbU6aA@25:42), CLAIM(IO30Ta7aqF0@03:40) | consensus | yes |
| 7 | Keep the default mode first in the collection by dragging rows into order, so the mode picker shows it first | Jesse Showalter | CLAIM(M8msUKBSBlY@03:27) | single-source | yes |
| 8 | Bind boolean variables to layer visibility (right-click the visibility icon in the layer controls) so one click can show or hide content per state | DesignCourse, Flux Academy | CLAIM(Tx45NcbU6aA@19:26), CLAIM(vf1BZ1mG2WE@20:46) | consensus | yes |

## Anti-patterns for this sub-topic
