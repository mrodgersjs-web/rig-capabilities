---
name: ui-prototype-states
tier: sub
parent: ds-ui-system
---

# Ui Prototype States

Purpose: state matrices, component-level prototype links, timing standards, set-variable interactions, failure diagnosis (laws 27-35).

Load when: the task touches this part of ui systems and components, or a ds-ui-system critique names it. Part of `ds-ui-system`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 27 | Ship every interactive element as a state matrix: default, hover or focus, active or typed, plus any popup or suggestion row, each as its own variant | DesignCourse | CLAIM(iLWaIx7tMnU@07:43), CLAIM(iLWaIx7tMnU@14:23) | single-source | no |
| 28 | Wire prototype links on the component set rather than on instances, so every placement inherits the behavior | Flux Academy, Jesse Showalter | CLAIM(1JZcMnecWHI@07:03), CLAIM(Sfy5wG5ZB3A@06:25) | consensus | yes |
| 29 | Standard timing set: smart animate around 300ms for small hover feedback, 500ms ease-in-out for card and theme changes, and an after-delay trigger near 500ms for content that appears while typing | Flux Academy, DesignCourse | CLAIM(1JZcMnecWHI@06:22), CLAIM(vf1BZ1mG2WE@21:50), CLAIM(iLWaIx7tMnU@17:41) | consensus | yes |
| 30 | Drive state changes with a click interaction that both swaps the variant and writes variables through set-variable actions | DesignCourse, Flux Academy | CLAIM(Tx45NcbU6aA@04:40), CLAIM(vf1BZ1mG2WE@25:35) | consensus | yes |
| 31 | Wrap any decrement or bounded counter in a conditional so the value cannot cross its floor | DesignCourse | CLAIM(Tx45NcbU6aA@11:25) | single-source | no |
| 32 | Every filter or tab click sets the chosen variable true and all sibling variables false in the same interaction; the all-option sets every variable true | Flux Academy | CLAIM(vf1BZ1mG2WE@26:23), CLAIM(vf1BZ1mG2WE@27:53) | single-source | yes |
| 33 | Name the animated layer identically in every variant (the highlight layer on all states) or smart animate will not interpolate it | Flux Academy | CLAIM(1JZcMnecWHI@05:29) | single-source | yes |
| 34 | Zero the pass-through of inactive layers before combining states into one component set | DesignCourse | CLAIM(iLWaIx7tMnU@13:25) | single-source | no |
| 35 | When a prototype link does nothing, check first whether the variable already held the target value and whether the transition is instant; if the layer still will not move, rebuild the variant pair rather than debug it | DesignCourse, Flux Academy | CLAIM(Tx45NcbU6aA@23:00), CLAIM(vf1BZ1mG2WE@22:40) | consensus | yes |

## Anti-patterns for this sub-topic
