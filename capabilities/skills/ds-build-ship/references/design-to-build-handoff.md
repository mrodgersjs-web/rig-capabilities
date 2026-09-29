---
name: design-to-build-handoff
tier: sub
parent: ds-build-ship
---

# Design To Build Handoff

Purpose: Prepare a design file so a builder can consume it: auto layout, containers, naming, fonts, sizing checks.

Load when: the task touches this part of build and ship, or a ds-build-ship critique names it. Part of `ds-build-ship`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 1 | Before touching the builder, read the design and write down the structure it implies: how many top-level groups, what grid it sits on, which elements must resize and which stay fixed. | Flux Academy | CLAIM(WLDfFqnqbxI@00:30, WLDfFqnqbxI@00:50) | single-source | yes |
| 2 | Name every frame by its role (hero, container, nav, button) before exporting; the names become class names in the builder, and a well named file is a reusable style guide on arrival. | Flux Academy | CLAIM(xHXqj006Q2k@05:03, xHXqj006Q2k@05:12, P5H7zs0RsUM@05:51) | consensus | yes |
| 3 | Build the Figma file with auto layout on every container, nested the way the page is nested (page frame, navbar, section, container, columns). A design made of unlogical groups cannot be transferred. | Flux Academy | CLAIM(xHXqj006Q2k@01:34, xHXqj006Q2k@01:47, xHXqj006Q2k@02:23) | single-source | yes |
| 4 | Set the design container to a fixed max width (1200px was used) so it lands as the builder's container width instead of a hard-coded 1440 wrapper that must be deleted after pasting. | Flux Academy | CLAIM(xHXqj006Q2k@02:05, xHXqj006Q2k@00:26) | single-source | yes |
| 5 | Load the fonts into the builder project's settings before copying anything over, otherwise pasted text falls back and the type has to be re-set element by element. | Flux Academy | CLAIM(xHXqj006Q2k@04:32, xHXqj006Q2k@04:49) | single-source | yes |
| 6 | Auto layout in the design tool and flex in the builder are the same model: same properties, same job of telling the renderer how to place children. Learn the mapping once and use it in both. | Flux Academy | CLAIM(xHXqj006Q2k@01:10, P5H7zs0RsUM@04:30) | consensus | yes |
| 7 | Importing a design with one click is fine for speed, but build the first version by hand so you can fix anything the import produces badly. | Flux Academy | CLAIM(P5H7zs0RsUM@00:25, P5H7zs0RsUM@00:33) | single-source | yes |
| 8 | Check fill and hug settings on every frame before an import: the design tool's fill/hug choices become the builder's flex sizing, and a wrong one silently breaks the layout. | Flux Academy | CLAIM(xHXqj006Q2k@07:59, xHXqj006Q2k@08:14) | single-source | yes |

## Anti-patterns for this sub-topic
