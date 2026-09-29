---
name: agent-ready-figma-prep
tier: sub
parent: ds-ai-workflow
---

# Agent Ready Figma Prep

Purpose: turn any file into an agent-readable source (laws 1-8).

Load when: the task touches this part of ai design workflow, or a ds-ai-workflow critique names it. Part of `ds-ai-workflow`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 1 | Apply auto layout to every container before any AI tool reads the file; without it the tool rebuilds your layout as absolute positions with frozen pixel values. | flux-academy, designcourse, jesse-showalter | CLAIM(uStjewbLoA0@01:02, yO3Wr7DEWF0@01:30, eXQQxaS0CCA@06:52) | consensus | yes |
| 2 | Write the auto-layout requirement into the prompt as well as the file; when the instruction is absent the generator falls back to loose frames. | flux-academy | CLAIM(XftHdIqqgNM@02:22, qeqearWwBpg@12:27) | single-source | yes |
| 3 | Rename layers to describe content and position before handoff; arbitrary frame labels leave the agent with no semantics to read. | flux-academy, designcourse | CLAIM(uStjewbLoA0@01:39, yO3Wr7DEWF0@02:50) | consensus | yes |
| 4 | Bind colors, font families, type sizes and spacing numbers to named styles or variables so the connection passes design-system values instead of raw hex and pixel numbers. | flux-academy, designcourse | CLAIM(uStjewbLoA0@02:03, yO3Wr7DEWF0@02:33, XftHdIqqgNM@05:33) | consensus | yes |
| 5 | Name grid and repeated items by their row and column when order is load-bearing; unnamed cells get scrambled on import. | designcourse | CLAIM(yO3Wr7DEWF0@02:50) | single-source | no |
| 6 | Delete or hide decorative and stray layers before you paste a frame into a generator; leftover art complicates its reading of the structure. | flux-academy, designcourse | CLAIM(qeqearWwBpg@12:12, eXQQxaS0CCA@07:18) | consensus | yes |
| 7 | Bring decorative art back as an absolutely positioned layer behind content and pin its constraints to center so resizing does not distort it. | designcourse | CLAIM(eXQQxaS0CCA@08:28, eXQQxaS0CCA@09:01) | single-source | no |
| 8 | Keep component variants and properties organized; the agent mirrors your component architecture in the code it writes. | flux-academy | CLAIM(uStjewbLoA0@02:25) | single-source | yes |

## Anti-patterns for this sub-topic
