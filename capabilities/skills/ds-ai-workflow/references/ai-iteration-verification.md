---
name: ai-iteration-verification
tier: sub
parent: ds-ai-workflow
---

# Ai Iteration Verification

Purpose: defect loops, device testing and staging handoff (laws 28-39).

Load when: the task touches this part of ai design workflow, or a ds-ai-workflow critique names it. Part of `ds-ai-workflow`.

## Checklist
1. Work through every law below against the current artifact before calling the sub-topic done.
2. Cite the CLAIM when a law drives a decision; a law you cannot cite is labeled own reasoning.
3. Where creators disagree (see the SKILL.md), state both positions and test rather than assume.

## Laws owned here
| # | law | creators | citations | consensus | top-10 source |
|---|---|---|---|---|---|
| 28 | Second prompt lists every defect you observed and adds an open clause letting the agent implement the functionality the design implies but never drew. | flux-academy | CLAIM(uStjewbLoA0@05:48, uStjewbLoA0@06:52) | single-source | yes |
| 29 | Re-inspect the build after every prompt: later passes that add function routinely break earlier spacing and styling. | flux-academy, designcourse | CLAIM(uStjewbLoA0@07:13, eXQQxaS0CCA@12:26) | consensus | yes |
| 30 | When output comes back broken, send a screenshot of the defect plus a concrete diagnosis of the cause, not a bare complaint. | designcourse | CLAIM(eXQQxaS0CCA@12:26, eXQQxaS0CCA@12:55) | single-source | no |
| 31 | Verify on the real delivery path: publish to a URL and run the flow on the target device instead of trusting the editor preview. | designcourse | CLAIM(eXQQxaS0CCA@13:45, eXQQxaS0CCA@17:14) | single-source | no |
| 32 | Publish a staging link and send it to stakeholders or developers so they can operate the thing rather than read static mockups. | jesse-showalter, adrien-ai-designer | CLAIM(EUPbdk972JI@05:04, yRBu2jU2d1w@10:00, h_CPuUpsiEg@07:57) | consensus | yes |
| 33 | Run parallel agent sessions while one works: separate windows for separate directions or screens. | adrien-ai-designer, flux-academy | CLAIM(oechHZEX8PM@04:00, XftHdIqqgNM@02:51) | consensus | yes |
| 34 | Generate two or three full directions from different references before committing, and send the set to the client to choose. | adrien-ai-designer | CLAIM(oechHZEX8PM@05:24, oechHZEX8PM@06:10) | single-source | yes |
| 35 | Once a direction is chosen, order every later screen to hold that exact visual direction. | adrien-ai-designer | CLAIM(oechHZEX8PM@06:27) | single-source | yes |
| 36 | Sequence animations by prompting an explicit delay value instead of hand-writing timing code. | flux-academy, designcourse | CLAIM(qeqearWwBpg@08:14, eXQQxaS0CCA@15:00) | consensus | yes |
| 37 | Keep motion subtle and short; heavy animation costs performance and pulls attention off the task. | adrien-ai-designer | CLAIM(5lDUy7JFNrg@05:47) | single-source | yes |
| 38 | Install a design or motion skill into the coding agent with its install command so aesthetics and animation conventions are enforced by the agent, not by you. | adrien-ai-designer, flux-academy | CLAIM(XftHdIqqgNM@03:46, 5lDUy7JFNrg@02:09, a_mZ4Kp3lTM@05:12) | consensus | yes |
| 39 | Keep the edits loop on version control: the agent edits, you approve, the agent pushes, you approve upstream, and only then does the live site change. | adrien-ai-designer | CLAIM(h_CPuUpsiEg@09:00) | single-source | yes |

## Anti-patterns for this sub-topic
- Starting from a blank canvas and prompting from scratch: it is slow, uninspiring and returns average output. CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@00:16)
- Handing over a file with no auto layout, no variables and no styles, then blaming the tool for pixel drift. CLAIM(yO3Wr7DEWF0@01:30)
- Forgetting to demand auto layout in the prompt itself, so the generator writes loose absolute frames. CLAIM(XftHdIqqgNM@02:22)
- Feeding screenshots only, without the file's typography, color and spacing data, and expecting accurate code. CLAIM(uStjewbLoA0@04:11)
