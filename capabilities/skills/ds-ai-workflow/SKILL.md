---
name: ds-ai-workflow
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for ai design workflow: Use AI tools inside design and build work with judgment kept human: tool stack selection, prompt-to-site flows, Figma and Framer AI features, and the checks that keep output on-quality. 46 laws, 18
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when AI tools are in the design or build path (prompt-to-site, Figma or Framer AI, Claude Design).
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides ai design workflow. Entered by the /design-studio command through design-studio-os, by ds-ai-design-engineer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: workflow.md: tool chain with per-tool role and fallback, the prompts or specs used, the human checkpoints, the quality checks run, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-ai-workflow/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# AI design workflow

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check code.review --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: code.review, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches ai design workflow. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-ai-design-engineer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "AI design", "prompt to website", "Figma AI", "Framer AI", "Claude design", "vibe coding". Inside a build this stage runs after the stage that feeds it and
before ds-build-ship, ds-critique.

## Inputs and output contract

Inputs: the job, the skill level of the operator, the budget (local-first, paid with a named fallback).
Output: workflow.md: tool chain with per-tool role and fallback, the prompts or specs used, the human checkpoints, the quality checks run.

## Procedure

1. Agent ready figma prep: turn any file into an agent-readable source (laws 1-8) (see references/agent-ready-figma-prep.md).
2. Ai build prompting: briefs, context files and prompt construction for build agents (laws 9-17) (see references/ai-build-prompting.md).
3. Reference driven visuals: references, brand kits and image-generation inputs (laws 18-27) (see references/reference-driven-visuals.md).
4. Ai iteration verification: defect loops, device testing and staging handoff (laws 28-39) (see references/ai-iteration-verification.md).
5. Template batch production: design systems, master templates and batch asset pipelines (laws 40-46) (see references/template-batch-production.md).
6. Check the decision tables below for the choices this stage forces.
7. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
8. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 1 | Apply auto layout to every container before any AI tool reads the file; without it the tool rebuilds your layout as absolute positions with frozen pixel values. | flux-academy, designcourse, jesse-showalter | CLAIM(uStjewbLoA0@01:02, yO3Wr7DEWF0@01:30, eXQQxaS0CCA@06:52) | consensus |
| 3 | Rename layers to describe content and position before handoff; arbitrary frame labels leave the agent with no semantics to read. | flux-academy, designcourse | CLAIM(uStjewbLoA0@01:39, yO3Wr7DEWF0@02:50) | consensus |
| 4 | Bind colors, font families, type sizes and spacing numbers to named styles or variables so the connection passes design-system values instead of raw hex and pixel numbers. | flux-academy, designcourse | CLAIM(uStjewbLoA0@02:03, yO3Wr7DEWF0@02:33, XftHdIqqgNM@05:33) | consensus |
| 6 | Delete or hide decorative and stray layers before you paste a frame into a generator; leftover art complicates its reading of the structure. | flux-academy, designcourse | CLAIM(qeqearWwBpg@12:12, eXQQxaS0CCA@07:18) | consensus |
| 9 | Never open with an empty prompt: seed the run with a component-library prompt, real reference screens, or a written requirements document. | adrien-ai-designer, jesse-showalter, flux-academy | CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@03:00, qeqearWwBpg@12:12) | consensus |
| 10 | Drop a markdown context file into the project folder and name it in the prompt: design brief, animation best practices, or product architecture. Without it the output drifts off what the client asked for. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@05:28, oechHZEX8PM@06:58, yRBu2jU2d1w@04:09) | consensus |
| 12 | Use a second chat model to draft the build prompt or the project guidelines file, then hand that text to the build agent. | adrien-ai-designer, jesse-showalter | CLAIM(h_CPuUpsiEg@06:10, yRBu2jU2d1w@05:00) | consensus |
| 13 | Make the first prompt exhaustive: screen list, aesthetic, exact accent colors, frame dimensions, and required layout behaviors. First-prompt thoroughness sets the floor for the whole project. | flux-academy, jesse-showalter | CLAIM(XftHdIqqgNM@01:44, XftHdIqqgNM@02:36, yRBu2jU2d1w@02:15) | consensus |
| 2 | Write the auto-layout requirement into the prompt as well as the file; when the instruction is absent the generator falls back to loose frames. | flux-academy | CLAIM(XftHdIqqgNM@02:22, qeqearWwBpg@12:27) | single-source |
| 8 | Keep component variants and properties organized; the agent mirrors your component architecture in the code it writes. | flux-academy | CLAIM(uStjewbLoA0@02:25) | single-source |
| 11 | Fill the brief by pointing the agent at the empty brief file and asking it to interview you line by line. | adrien-ai-designer | CLAIM(oechHZEX8PM@02:11) | single-source |
| 17 | On style-first generators, write the opening prompt heavy on content and light on styling: name the mood broadly and tune styling afterwards. | flux-academy | CLAIM(QKUnUrsDzk0@00:53, QKUnUrsDzk0@02:00) | single-source |

The full set of 46 laws lives in the sub-skills.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| agent-ready-figma-prep | references/agent-ready-figma-prep.md | 8 laws |
| ai-build-prompting | references/ai-build-prompting.md | 9 laws |
| reference-driven-visuals | references/reference-driven-visuals.md | 10 laws |
| ai-iteration-verification | references/ai-iteration-verification.md | 12 laws |
| template-batch-production | references/template-batch-production.md | 7 laws |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | A file where every section is a named auto-layout container | A file of loosely placed frames the agent re-measures as fixed pixels | Structure is the only layout information the agent gets |
| 2 | Layer names that read as content and position | Layers still called by default frame numbers | Names supply the semantics the code copies |
| 3 | Colors and type bound to named styles | Hex values and pixel numbers scattered through the file | Styles survive into code as a design system; numbers do not |
| 4 | First prompt with screens, palette, frame size and layout rules named | First prompt that just asks for a nice app | Thoroughness of prompt one caps the quality floor |
| 5 | Prompt plus a screenshot of a reference screen worth matching | Prompt alone, hoping for taste to appear | The model reproduces averages without a target |
| 6 | Custom brand assets generated from a kit | Stock photos dropped into the same layout | Assets are what removes the generated look |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/ai_workflow/.

## Decision tables

| Choice | Pick A when | Pick B when | citation |
|--------|-------------|-------------|----------|
| A: coding agent plus design-file connection / B: in-tool prototype generator | You need production-grade code, a repo, and deploy control | You need a clickable prototype today for buy-in or developer context | CLAIM(uStjewbLoA0@02:50, EUPbdk972JI@01:29) |
| A: paste existing frames / B: paste a written requirements doc | You already have approved screens to convert | You have direction but no pixels yet, or the last frame build came back with layout damage | CLAIM(EUPbdk972JI@01:29, EUPbdk972JI@04:07) |
| A: browser-local storage in the prompt / B: real backend integration | It is a prototype or demo | It must survive logins and multi-user data for real | CLAIM(yRBu2jU2d1w@06:38, uStjewbLoA0@07:32) |
| A: parallel agent windows / B: one long session | Directions or screens are independent and can be compared | One coherent file must stay consistent across many dependent edits | CLAIM(oechHZEX8PM@04:00, XftHdIqqgNM@02:51) |
| A: reference screenshot in the prompt / B: written styling spec only | You can point at a layout worth matching | The direction is genuinely new and no reference exists | CLAIM(5lDUy7JFNrg@01:52, XftHdIqqgNM@01:44) |
| A: paid all-in-one asset tool / B: free image tool plus manual cleanup | Brand consistency across many assets is the requirement | Budget is zero and you will clean each asset by hand | CLAIM(a_mZ4Kp3lTM@02:20, IIXupZAGvDk@01:57) |

## Anti-patterns

- Starting from a blank canvas and prompting from scratch: it is slow, uninspiring and returns average output. CLAIM(a_mZ4Kp3lTM@00:54, EUPbdk972JI@00:16)
- Handing over a file with no auto layout, no variables and no styles, then blaming the tool for pixel drift. CLAIM(yO3Wr7DEWF0@01:30)
- Forgetting to demand auto layout in the prompt itself, so the generator writes loose absolute frames. CLAIM(XftHdIqqgNM@02:22)
- Feeding screenshots only, without the file's typography, color and spacing data, and expecting accurate code. CLAIM(uStjewbLoA0@04:11)
- Shipping stock photography in a generated layout and wondering why it reads generic. CLAIM(5lDUy7JFNrg@02:46)
- Pasting model-written copy straight into a layout without editing it. CLAIM(xmL99KEycU0@03:18)
- Adding large decorative animation, which hurts performance and distracts from the goal. CLAIM(5lDUy7JFNrg@05:47)
- Treating the editor preview as proof: layouts squash and device-only features never trigger there. CLAIM(eXQQxaS0CCA@12:00, eXQQxaS0CCA@13:45)
- plus 3 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- How specific the first prompt should be. Flux Academy (2026) tells you to be thorough: frame size, exact colors, explicit layout rules, because prompt one sets the foundation. CLAIM(XftHdIqqgNM@02:36) Flux Academy's own earlier Framer video (2023) says the opposite for its site generator: describe content richly, keep styling broad, and adjust style later. CLAIM(QKUnUrsDzk0@00:53) DesignCourse (2025) sits between them: the prompt need not be long if the file is well prepared. CLAIM(yO3Wr7DEWF0@04:04) Resolution: specificity belongs where the tool cannot infer it; a structured file lets the prompt stay short, a blank canvas demands detail.
- Whether generated work can return to the design file. Flux Academy (2025-09) reports no route back from the prototyping generator to design layers. CLAIM(qeqearWwBpg@16:52) Jesse Showalter (2025-10, 2026-01) demonstrates copying the whole generated design out as editable layers. CLAIM(EUPbdk972JI@05:37, yRBu2jU2d1w@09:07) Treat as a dated capability change, not a contradiction.
- Attach a design system or not. Jesse Showalter deliberately skips attaching a published design system on the first prototype run to get moving. CLAIM(yRBu2jU2d1w@02:06) Flux Academy instead generates the design system from the finished screens and applies it back. CLAIM(XftHdIqqgNM@05:00) Both agree the system matters; they disagree on when to introduce it.
- Who holds creative direction. Flux Academy frames the agent as a fast literal junior designer you brief and review. CLAIM(XftHdIqqgNM@07:29) Jesse Showalter frames the designer as a creative director whose thought work lives in the requirements doc. CLAIM(EUPbdk972JI@06:15) Adrien frames it as the end of design effort once research and architecture are done. CLAIM(oechHZEX8PM@07:31) Practically: the more the brief carries, the less the generation step decides.

## Creator claims (unverified)

- A three-clip scroll-animation site with deploy was built in about 30 minutes end to end. CLAIM(h_CPuUpsiEg@00:00)
- A branded animated dashboard can be built in under 10 minutes on the three-step workflow. CLAIM(a_mZ4Kp3lTM@00:15)
- Three complete design directions can be produced in about 3 minutes once the brief is filled. CLAIM(oechHZEX8PM@05:24)
- A three-screen first draft takes about 15 minutes through the design-file connection. CLAIM(XftHdIqqgNM@04:50)
- A full landing page can be generated from one prompt in roughly 30 seconds. CLAIM(QKUnUrsDzk0@02:26)
- The referenced image model was described as the best available at the time of recording. CLAIM(h_CPuUpsiEg@01:15)
- The 2024 image model release was described as far ahead of competitors in the creator's opinion. CLAIM(Rkq_eDeGIMw@00:13)
- A free-ebook funnel was presented as the creator's plan to make $100,000 in a calendar year. CLAIM(xmL99KEycU0@00:00)

## Tool-specific (dated)

- 2025-06 (designcourse): the design-file connection was set up in two places: add the server URL in the code editor's MCP settings, and enable the dev-mode server inside the design tool's preferences. CLAIM(yO3Wr7DEWF0@00:22)
- 2026-04 (flux-academy): the same capability is installed from a connectors panel, choosing the listing described as the design-tool MCP server and authorizing the account; two similar listings exist. CLAIM(XftHdIqqgNM@01:11)
- 2026-03 (adrien-ai-designer): the coding agent runs inside a code editor, and MCP installation is done by a terminal command followed by a check of the MCP panel. CLAIM(oechHZEX8PM@00:27)
- 2025-09 (flux-academy): the in-tool prototyping generator offered a code-from-design entry on selected layers, split code/preview view, and converted elements into code layers that land in the document grid. CLAIM(qeqearWwBpg@00:58, qeqearWwBpg@04:02)
- 2025-09 (flux-academy): that generator had no path back into a design file, and non-default fonts did not preview or publish in its site product. CLAIM(qeqearWwBpg@09:13, qeqearWwBpg@16:52)
- 2025-10 and 2026-01 (jesse-showalter): the same tool had gained copy-out of the whole design as layers with auto layout, point-and-edit on elements, a per-project guidelines markdown file, and staging publishes. CLAIM(EUPbdk972JI@05:37, yRBu2jU2d1w@04:09)
- 2025-12 (designcourse): the prototyping generator defaulted to adding a hosted database, required an API key pasted manually when it forgot to ask, and published testable URLs for on-device checks. CLAIM(eXQQxaS0CCA@11:12, eXQQxaS0CCA@12:26, eXQQxaS0CCA@13:45)
- 2023-06 (flux-academy): the site builder's AI entry point was a start-with-AI button with a prompt box, theme shuffle, per-section themes, inline copy rewriting on text layers, and context carried across generated pages. CLAIM(QKUnUrsDzk0@00:32, QKUnUrsDzk0@04:06, QKUnUrsDzk0@05:43)
- plus 4 more in the corpus law file studio-corpus/laws/ai_workflow.md

## Hand-off
- Next stage: ds-build-ship, ds-critique. Agent: `ds-ai-design-engineer`.
- Corpus source: studio-corpus/laws/ai_workflow.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
