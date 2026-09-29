---
name: ui-components-variants
tier: sub
parent: ds-ui-system
---

# Ui Components Variants

Purpose: component sets, variant naming, properties over variants, slots, nesting (laws 9-18).

Load when: the task touches this part of ui systems and components, or a ds-ui-system critique names it. Part of `ds-ui-system`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 9 | Convert anything reused more than once into a component and edit only the master, so every instance follows | Flux Academy, Jesse Showalter | CLAIM(aGvWDDPsjUM@00:57), CLAIM(oCVG6DFCTz4@03:30), CLAIM(1JZcMnecWHI@00:57) | consensus | yes |
| 10 | Put interchangeable items (icon types, button shapes, tab states) in one component set with one variant each, so instances swap from the properties panel | Flux Academy | CLAIM(1JZcMnecWHI@01:23), CLAIM(vf1BZ1mG2WE@03:13) | consensus (same creator, 3 videos) | yes |
| 11 | Give every variant axis a real option name (State equals default, hovered, active) and rename the property itself; never ship a set labeled with generator defaults | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(1JZcMnecWHI@02:35), CLAIM(aGvWDDPsjUM@05:21), CLAIM(iLWaIx7tMnU@17:08) | consensus | yes |
| 12 | Slash-name frames before combining them (button/default, filters/abstract) so the finished set reads as a legend | Flux Academy | CLAIM(vf1BZ1mG2WE@01:58), CLAIM(vf1BZ1mG2WE@06:22) | single-source | yes |
| 13 | Reserve variants for state and shape; express content differences with properties (text field, show/hide boolean, instance swap) or the variant count explodes | Flux Academy, Jesse Showalter, DesignCourse | CLAIM(aGvWDDPsjUM@02:57), CLAIM(oCVG6DFCTz4@03:57), CLAIM(KWUlkXZOj4g@11:38) | consensus | yes |
| 14 | On an instance-swap property, set preferred values to the few components that slot accepts, so the picker stops offering the whole library | Flux Academy | CLAIM(aGvWDDPsjUM@10:18) | single-source | yes |
| 15 | Order each component property panel as: show/hide toggle first, then the editable field it reveals | Flux Academy | CLAIM(aGvWDDPsjUM@11:25) | single-source | yes |
| 16 | Nest components on purpose (a button row holding buttons, an accordion holding panels) and make style changes at the deepest master so they propagate up through every parent | Jesse Showalter | CLAIM(Sfy5wG5ZB3A@13:20), CLAIM(Sfy5wG5ZB3A@13:58) | single-source | yes |
| 17 | For regions whose content will change later (cards, popups, dropdowns), convert an auto-layout frame inside the component into a slot, then set a preferred instance and a written note describing what belongs there | Punit Chawla | CLAIM(beUlX6L2NMg@01:21), CLAIM(beUlX6L2NMg@02:30) | single-source | no |
| 18 | Enumerate the full option set (label only, icon left, icon right, icon only) before creating the component, and build those controls in at creation time | Jesse Showalter | CLAIM(Sfy5wG5ZB3A@01:32) | single-source | yes |

## Anti-patterns for this sub-topic
