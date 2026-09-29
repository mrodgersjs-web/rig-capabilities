---
name: ui-pattern-recipes
tier: sub
parent: ds-ui-system
---

# Ui Pattern Recipes

Purpose: search input states, surface color derivation, radius relationships, button ripple, glass and neobrutalist recipes (laws 36-43).

Load when: the task touches this part of ui systems and components, or a ds-ui-system critique names it. Part of `ds-ui-system`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 36 | Search input carries a floating label: about 18px at rest, about 14px floated up when typing starts, so the field name never disappears | DesignCourse | CLAIM(iLWaIx7tMnU@08:00), CLAIM(iLWaIx7tMnU@08:32) | single-source | no |
| 37 | Search input ships four states: resting, focus with the float animation, typed with a suggestion list (rows with hover), and a did-you-mean row whose corrected keyword is bold and colored | DesignCourse | , CLAIM(iLWaIx7tMnU@12:41) | single-source | no |
| 38 | Derive strokes and secondary fills from the background hue darkened slightly; never drop a pure gray next to a colored surface; reserve full saturation for the focus state | DesignCourse | CLAIM(iLWaIx7tMnU@03:12), CLAIM(iLWaIx7tMnU@04:31) | single-source | no |
| 39 | Relate a nested control radius to its container (inner about half the outer) so the edges flow instead of clashing | DesignCourse | CLAIM(iLWaIx7tMnU@04:58) | single-source | no |
| 40 | For a hover ripple on a button, mask the growing shape with a copy of the button shape so the effect cannot escape the button bounds | DesignCourse | CLAIM(KWUlkXZOj4g@06:25) | single-source | no |
| 41 | Glass panels: hold one light direction and intensity across the whole site, keep glass depth low (under roughly 20-30), and raise frost to about 20 so overlaid text stays readable | Punit Chawla | CLAIM(3ERrrTcx09c@01:33), CLAIM(3ERrrTcx09c@02:30) | single-source | no |
| 42 | Neobrutalist card recipe: remove the soft shadow, add thick high-contrast strokes to container and image, then a hard shadow offset about 4/4 with zero blur at full opacity, vibrant colors, one playful graphic | DesignCourse | CLAIM(4BEEoYYDmUg@02:39), CLAIM(4BEEoYYDmUg@02:37) | single-source | no |
| 43 | Design a control inside its real layout context (grid on, target artboard) rather than in isolation on the canvas | DesignCourse | CLAIM(KWUlkXZOj4g@02:02) | single-source | no |

## Anti-patterns for this sub-topic
