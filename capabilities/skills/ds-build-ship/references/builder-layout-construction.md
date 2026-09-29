---
name: builder-layout-construction
tier: sub
parent: ds-build-ship
---

# Builder Layout Construction

Purpose: Stacks, grids, wrappers, containers, overflow and baseline work inside Framer/Webflow.

Load when: the task touches this part of build and ship, or a ds-build-ship critique names it. Part of `ds-build-ship`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 9 | Define shared colors as named styles at the start of the build, before placing elements, so reuse costs one click instead of a re-picked hex. | Flux Academy | CLAIM(P5H7zs0RsUM@00:46, P5H7zs0RsUM@01:00) | single-source | yes |
| 10 | Take the platform's own navigation component instead of drawing one; it arrives with the mobile collapse already handled. | Flux Academy | CLAIM(P5H7zs0RsUM@01:08, P5H7zs0RsUM@01:19) | single-source | yes |
| 11 | A web layout is never free-positioned: every element lives inside a stack (or wrapper) whose alignment controls it, so nothing can be dragged off its line. | Flux Academy | CLAIM(P5H7zs0RsUM@07:37, P5H7zs0RsUM@07:50) | single-source | yes |
| 12 | Give full-bleed sections 100 percent width (or 100 viewport height for a one-screen hero) and keep the content inside a centered container so the page scales and the copy stays on a readable measure. | Flux Academy | CLAIM(P5H7zs0RsUM@06:16, BNYLKuIlazA@00:16, BNYLKuIlazA@01:47) | consensus | yes |
| 13 | Split a single-screen composition into separate top-level groups (nav, text block, card area) rather than one giant grid, so each part can be restacked at tablet and mobile without breaking the others. | Flux Academy | CLAIM(WLDfFqnqbxI@01:20, WLDfFqnqbxI@14:47) | single-source | yes |
| 14 | Define one grid class (column count plus gap) and reapply it to every group that shares the grid; use a combo class when a single group needs a local override. | Flux Academy | CLAIM(WLDfFqnqbxI@03:30, WLDfFqnqbxI@04:40) | single-source | yes |
| 15 | Wrap a section's children in a vertical flex parent when you need controlled gaps and one child that grows to fill the remaining height. | Flux Academy | CLAIM(WLDfFqnqbxI@04:21, WLDfFqnqbxI@04:34) | single-source | yes |
| 16 | Pull an element out of normal grid flow with absolute positioning when it is decoration rather than content (a 3D or image backdrop), and size it to 100 percent of its frame so it stays behind the copy. | Flux Academy | CLAIM(BNYLKuIlazA@05:58, BNYLKuIlazA@06:14) | single-source | yes |
| 17 | Set any image that could exceed its cell to fill its box and clip the parent with overflow hidden, otherwise one oversized asset pushes the next row below the fold. | Flux Academy | CLAIM(WLDfFqnqbxI@10:01, WLDfFqnqbxI@11:49) | single-source | yes |
| 18 | Use space-between on a card's vertical flex to pin one element to the top and one to the bottom instead of hard-coding margins. | Flux Academy | CLAIM(WLDfFqnqbxI@13:04, WLDfFqnqbxI@13:18) | single-source | yes |
| 19 | Size a display headline in viewport units (13 viewport width was used) when it must scale with the screen, then set line height from the text and cap its width. | Flux Academy | CLAIM(WLDfFqnqbxI@06:47, WLDfFqnqbxI@07:23, WLDfFqnqbxI@07:50) | single-source | yes |
| 20 | Align to type baselines, not to bounding boxes: when a bottom-aligned block lands visually short, nudge its margin until the baselines read level. | Flux Academy | CLAIM(WLDfFqnqbxI@08:25, WLDfFqnqbxI@08:52) | single-source | yes |
| 21 | Cap text width (max width or a percentage of the parent) on every long block so a wide viewport cannot stretch a paragraph into one unbroken line. | Flux Academy | CLAIM(P5H7zs0RsUM@14:48, WLDfFqnqbxI@08:47) | consensus | yes |

## Anti-patterns for this sub-topic
