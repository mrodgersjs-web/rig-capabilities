---
name: ai-build-prompting
tier: sub
parent: ds-ai-workflow
---

# Ai Build Prompting

Purpose: briefs, context files and prompt construction for build agents (laws 9-17).

Load when: the task touches this part of ai design workflow, or a ds-ai-workflow critique names it. Part of `ds-ai-workflow`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 9 | Never open with an empty prompt: seed the run with a component-library prompt, real reference screens, or a written requirements document. | adrien-ai-designer, jesse-showalter, flux-academy | CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@03:00, qeqearWwBpg@12:12) | consensus | yes |
| 10 | Drop a markdown context file into the project folder and name it in the prompt: design brief, animation best practices, or product architecture. Without it the output drifts off what the client asked for. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@05:28, oechHZEX8PM@06:58, yRBu2jU2d1w@04:09) | consensus | yes |
| 11 | Fill the brief by pointing the agent at the empty brief file and asking it to interview you line by line. | adrien-ai-designer | CLAIM(oechHZEX8PM@02:11) | single-source | yes |
| 12 | Use a second chat model to draft the build prompt or the project guidelines file, then hand that text to the build agent. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@06:10, yRBu2jU2d1w@05:00) | consensus | yes |
| 13 | Make the first prompt exhaustive: screen list, aesthetic, exact accent colors, frame dimensions, and required layout behaviors. First-prompt thoroughness sets the floor for the whole project. | flux-academy, jesse-showalter | CLAIM(XftHdIqqgNM@01:44, XftHdIqqgNM@02:36, yRBu2jU2d1w@02:15) | consensus | yes |
| 14 | Name the exact model or vendor the integration must use, twice, so the agent does not silently substitute another. | designcourse | CLAIM(eXQQxaS0CCA@10:03) | single-source | no |
| 15 | Spell out what the build must not create: for a prototype, forbid databases and login persistence, or order browser-local storage instead of a full backend. | designcourse, jesse-showalter | CLAIM(eXQQxaS0CCA@11:12, yRBu2jU2d1w@06:38) | consensus | no |
| 16 | Include a step-by-step flow spec when behavior spans screens and permissions, and say which platform it runs on. | designcourse | CLAIM(eXQQxaS0CCA@10:55, eXQQxaS0CCA@10:03) | single-source | no |
| 17 | On style-first generators, write the opening prompt heavy on content and light on styling: name the mood broadly and tune styling afterwards. | flux-academy | CLAIM(QKUnUrsDzk0@00:53, QKUnUrsDzk0@02:00) | single-source | yes |

## Anti-patterns for this sub-topic
- Starting from a blank canvas and prompting from scratch: it is slow, uninspiring and returns average output. CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@00:16)
- Handing over a file with no auto layout, no variables and no styles, then blaming the tool for pixel drift. CLAIM(yO3Wr7DEWF0@01:30)
- Forgetting to demand auto layout in the prompt itself, so the generator writes loose absolute frames. CLAIM(XftHdIqqgNM@02:22)
- Feeding screenshots only, without the file's typography, color and spacing data, and expecting accurate code. CLAIM(uStjewbLoA0@04:11)
