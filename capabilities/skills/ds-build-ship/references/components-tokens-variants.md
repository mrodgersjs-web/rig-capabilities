---
name: components-tokens-variants
tier: sub
parent: ds-build-ship
---

# Components Tokens Variants

Purpose: Component and variable discipline plus button and card construction.

Load when: the task touches this part of build and ship, or a ds-build-ship critique names it. Part of `ds-build-ship`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 22 | Anything reused twice (button, nav, footer, card) becomes a component the moment it is styled; edit the master and every instance follows. | Flux Academy | CLAIM(P5H7zs0RsUM@16:35, P5H7zs0RsUM@01:43, BNYLKuIlazA@03:43) | consensus | yes |
| 23 | Put state differences into variants on the same component (main, hover) rather than into a second copy, so the styles cannot drift apart. | Flux Academy | CLAIM(P5H7zs0RsUM@18:14, P5H7zs0RsUM@18:20) | single-source | yes |
| 24 | A press-feel hover is built by changing the fill and collapsing the shadow offset to zero in the hover variant. | Flux Academy | CLAIM(P5H7zs0RsUM@18:23, P5H7zs0RsUM@18:35) | single-source | yes |
| 25 | A hard-edged shadow is zero blur with a small spread and a small offset; blur is what makes a shadow look soft and generic. | Flux Academy | CLAIM(P5H7zs0RsUM@17:52, P5H7zs0RsUM@18:03) | single-source | yes |
| 26 | Build a button as a hug-sized frame with text inside, more horizontal than vertical padding and a small radius, then componentize it. | Flux Academy | CLAIM(BNYLKuIlazA@02:36, BNYLKuIlazA@03:02, BNYLKuIlazA@03:13) | single-source | yes |
| 27 | Any value repeated in two or more places (corner radius, color) becomes a variable so a later change lands everywhere at once. | Flux Academy | CLAIM(WLDfFqnqbxI@11:09, WLDfFqnqbxI@11:20) | single-source | yes |
| 28 | Reuse the project's predefined heading and paragraph styles instead of hand-setting each text block; only genuinely one-off display type gets its own class. | Flux Academy | CLAIM(P5H7zs0RsUM@14:15, WLDfFqnqbxI@07:10) | consensus | yes |
| 29 | Set the base type once on the body/all-pages class and let it cascade to everything below. | Flux Academy | CLAIM(WLDfFqnqbxI@02:25, WLDfFqnqbxI@02:33) | single-source | yes |

## Anti-patterns for this sub-topic
