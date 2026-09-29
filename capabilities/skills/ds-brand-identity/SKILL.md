---
name: ds-brand-identity
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate
  (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict.
  Main skill of design-studio-os for brand identity: Design the identity: logo, brand system and visual voice, tested at real sizes before it ships. 50 laws, 20
  looks-like/does-not pairs distilled from the RIG design YouTube corpus (top-10 subscribed channels
  weighted), every law cited CLAIM(<videoId>@mm:ss). Use when a logo, brand system, visual voice or rebrand is the job.
tier: main
parent: design-studio-os
activation: "Load at the start of any task that decides brand identity. Entered by the /design-studio command through design-studio-os, by ds-brand-designer, or by the ds-gate-* harness that names this stage."
owner: rig-intelligence
status: Stable
acl: internal
outcome: "design-ux: brand-system.md (mark, type, color, voice, usage do and do not), logo renders at 16px, one color, reversed, with citations or labeled own reasoning on every judgment"
done_when:
  - cmd:python3 tools/claims_check.py studio-skills/skills/ds-brand-identity/SKILL.md
  - cmd:python3 tools/check_family.py
quality_floor: 0.6
---

# Brand identity

JEV FIRST, and it binds every task under this skill: an agent whose only context is this excerpt
sends semantic triage, routing and classification to the rig-s1gate Jev path BEFORE any frontier LLM call
(`~/.rig/bin/rig-s1gate check ui.design --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`;
nearest existing rubric: ui.design, advisory until calibrated). When the classifier is unavailable: DEFERRED,
never a guessed verdict. A required signal passes only above 0.9.

## Load surface

Load this skill FIRST, before any design decision, whenever the job touches brand identity. It is an
always-loaded task-start surface, not a deep reference an agent must already know about: the `/design-studio`
command loads `design-studio-os`, which names this skill in its stage routes table; `when-designing-interfaces`
and `when-designing-websites` route design work to that front door; and the meta agent `ds-director` dispatches
`ds-brand-designer`, which loads this skill before its first action. The stage's gate harness
(`ds-gate-craft`, `ds-gate-brief`, `ds-gate-critique` or `ds-gate-ship`) names these requirements, so a session
running that harness loads this file to pass its gate. Paths are relative to `~/Developer/rig-design-studio-os`.

## When to use

Trigger words: "logo", "brand", "identity", "rebrand", "visual identity". Inside a build this stage runs after the stage that feeds it and
before ds-typography, ds-color.

## Inputs and output contract

Inputs: the brief, competitive context, where the mark must work (favicon to billboard).
Output: brand-system.md (mark, type, color, voice, usage do and do not), logo renders at 16px, one color, reversed.

## Procedure

1. Brand brief lock: intake, audience over taste, noun map, 20-sketch sprint, three stylescapes before design (see references/brand-brief-lock.md).
2. Mark construction: black-and-white first, geometry plus optical correction, symbol and type match, one family, legibility over cleverness (see references/mark-construction.md).
3. Logo scale set: motion, dark mode, 16-pixel test, rebuilt reverse, clear space from an internal letter (see references/logo-scale-set.md).
4. Logo file handoff: artboard align, native plus EPS plus PDF, CMYK RGB and spot, PNG pair, zip after proof (see references/logo-file-handoff.md).
5. Check the decision tables below for the choices this stage forces.
6. Run the anti-patterns as a final sweep; each surviving one becomes a finding in `ds-critique`.
7. Cite every load-bearing choice (CLAIM copied from this file); label the rest own reasoning.

## Core laws (load-bearing subset)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 3 | Design for the audience, not the client's taste. Name who they are, what they value, where the mark will be seen, how small it must survive, and where it will be used. | Satori Graphics, Flux Academy, Will Paterson | CLAIM(T54ytwmlObg@04:56, T54ytwmlObg@05:07, 2RO44hoGdlE@03:41, 9MOuHiQWFoU@12:39, 53H8XGIp0ac@10:19) | consensus |
| 5 | Spend 20 minutes on 20 sketches, one minute each, no eraser. Each sketch is an experiment you can discard. Paper sketch first, then build the chosen one as vectors. | Will Paterson, Envato Tuts+ | CLAIM(gza5-1e0IY4@05:31, gza5-1e0IY4@05:57, gza5-1e0IY4@06:09, YycxaAK2MZ4@1:28:47) | consensus |
| 11 | Keep a duplicate of every option on the artboard. Do not overwrite the only copy. | Flux Academy | CLAIM(LBAI4ogp9C4@06:15, KV5rW93PLw8@17:45, DtxyRhd6WJU@05:11) | consensus |
| 13 | Draw in black and white, or in outline view, before color. Judge shape and construction with color stripped. A color idea can sit in research; it does not enter the drawing until the form holds. | Satori Graphics, Flux Academy, Envato Tuts+ | CLAIM(T54ytwmlObg@03:11, T54ytwmlObg@03:22, LBAI4ogp9C4@01:52, KV5rW93PLw8@14:42, YycxaAK2MZ4@19:02, YycxaAK2MZ4@34:21) | consensus |
| 15 | Keep it simple enough to remember, but stop before identity disappears. If the mark could sit on five brands, you cut too far. After you remove a piece, the idea must still hold. | Satori Graphics, Flux Academy | CLAIM(T54ytwmlObg@02:22, 2RO44hoGdlE@00:13, 2RO44hoGdlE@00:27, KV5rW93PLw8@34:12, KV5rW93PLw8@34:25) | consensus |
| 17 | Test the bare silhouette before detail. If the base shape is forgettable, effects will not save it. A plain letter with no distinction is not a logo. | Satori Graphics, Flux Academy | CLAIM(2RO44hoGdlE@01:47, 2RO44hoGdlE@01:54, DtxyRhd6WJU@12:04, DtxyRhd6WJU@14:03) | consensus |
| 19 | Match symbol geometry to wordmark geometry. A soft rounded symbol does not sit with a sharp chopped sans. Rebuild the symbol from the letter if they clash. | Satori Graphics, Flux Academy | CLAIM(T54ytwmlObg@04:33, T54ytwmlObg@04:39, LBAI4ogp9C4@00:50, LBAI4ogp9C4@01:16, KV5rW93PLw8@32:34) | consensus |
| 22 | Make the mark distinguishable from category neighbors. Reverse-image-search before you call it unique. | Satori Graphics, Will Paterson | CLAIM(T54ytwmlObg@01:37, T54ytwmlObg@01:43, gza5-1e0IY4@08:00, gza5-1e0IY4@08:08) | consensus |
| 1 | Before any sketch, send a short questionnaire: what makes the business different, who it serves, and what it offers. | Satori Graphics | CLAIM(T54ytwmlObg@01:16, T54ytwmlObg@01:26) | single-source |
| 2 | Write stance, emotion, and the thing that is unique before drawing. A prestige brief and a tech brief do not share a type system. | Satori Graphics | CLAIM(2RO44hoGdlE@02:50, 2RO44hoGdlE@03:02, 2RO44hoGdlE@03:15) | single-source |
| 6 | Run a fixed sequence: intake, research, direction choice, concepts, refinement, one solution. Do not skip to drawing. | Satori Graphics | CLAIM(T54ytwmlObg@02:47, T54ytwmlObg@02:53) | single-source |
| 7 | The mark is one part of an identity. If it disagrees with the rest of the system, the market reads confusion. | Satori Graphics | CLAIM(T54ytwmlObg@03:33, T54ytwmlObg@03:46) | single-source |

The full set of 50 laws lives in the sub-skills, plus 1 ungrouped laws below.

## Sub-skills

| sub-skill | file | owns |
|---|---|---|
| brand-brief-lock | references/brand-brief-lock.md | 13 laws |
| mark-construction | references/mark-construction.md | 23 laws |
| logo-scale-set | references/logo-scale-set.md | 10 laws |
| logo-file-handoff | references/logo-file-handoff.md | 5 laws |

## Further laws (not yet grouped into a sub-skill)

| # | law | creators | citations | consensus |
|---|---|---|---|---|
| 48 | Get a second pair of eyes, or leave the mark for a day or two, before calling it done. | Satori Graphics | CLAIM(T54ytwmlObg@03:56, T54ytwmlObg@04:22) | single-source |

## Looks like / does not (strongest pairs)

| looks like | does not | why | citation |
|---|---|---|---|
| 1 | A simple mark that still could not be swapped onto another brand | A minimal mark that could sit on five brands | Reduction that deletes identity is not simplicity |
| 2 | A non-literal recognition hook | A bulb drawn because the firm sells electricity | The mark is not a diagram of the offer |
| 3 | Construction locked in black and white, or in outline view | Color chosen first, then a shape forced to fit it | Color hides weak construction |
| 4 | A sharp symbol rebuilt from the sharp letter beside it | A round splash symbol next to a chopped modern sans | Symbol and type must share one geometry |
| 5 | Full lockup, simplified icon, dark and light variants | One detailed drawing used at every size | Tiny surfaces need a reduced mark |
| 6 | A silhouette that still reads after a blur | A mark that falls apart once detail is blurred | Memory stores shape before detail |

Full pair set: the ds-exemplars skill and studio-exemplars/pairs/brand_identity/.

## Decision tables

| decision | option A | option B | pick when |
|----------|----------|----------|-----------|
| Mark vs diagram | Suggestive or combined mark | Literal object of the trade | Default A. B only when the name is a category word and the cue is built from shapes already in the mark, not pasted on. CLAIM(T54ytwmlObg@01:55, 53H8XGIp0ac@06:51, 53H8XGIp0ac@07:09) |
| Wordmark only vs symbol plus name | Pure typographic logo | Symbol plus wordmark | If hiding the name leaves nothing, you are in A and the recognition test changes. CLAIM(2RO44hoGdlE@00:44) |
| One file vs scale set | Single full lockup | Full lockup plus simplified icon plus dark/light plus a rebuilt reverse | Pick B whenever the mark hits a favicon, avatar, app icon, or a dark UI. CLAIM(2RO44hoGdlE@02:27, DtxyRhd6WJU@07:32) |
| Print file | EPS | PDF | Send both, plus the native file saved down for an older app. CLAIM(JFai8IzN-3k@04:46, mLOUtiRt8JA@00:38) |
| Screen file | PNG-24 with transparency | JPEG | PNG when the ground is unknown. JPEG only as a lossy extra with a solid ground. CLAIM(mLOUtiRt8JA@01:51, mLOUtiRt8JA@10:15) |
| Color build | CMYK | RGB | CMYK for print, RGB for screen. Add a spot file when a printer must match a swatch book. CLAIM(mLOUtiRt8JA@01:21, YycxaAK2MZ4@1:20:40) |
| Type direction | Heritage serif | Geometric sans | Serif for prestige and trust. Geometric sans for a tech brief that must feel new. CLAIM(2RO44hoGdlE@03:15, 2RO44hoGdlE@04:02) |
| Depth | Solid gradation (taper, step, shade) | Continuous gradient fill | Solid when the mark must print, embroider, or fax as one shape. Gradient only as a digital skin on a solid master. CLAIM(DtxyRhd6WJU@07:49) |
| Secondary line | Same family, lighter weight, smaller | A second face at equal size | Same family unless the brief names two equal brands. CLAIM(KV5rW93PLw8@23:14, KV5rW93PLw8@25:36) |
| Direction choice | One mood board | Three stylescapes | Always the three. A photo pile does not force a decision. CLAIM(9MOuHiQWFoU@01:01, 9MOuHiQWFoU@02:00) |

## Anti-patterns

- Treating the logo as the whole brand. CLAIM(T54ytwmlObg@03:33)
- Skipping intake and designing from a vibe. CLAIM(T54ytwmlObg@01:16)
- Letting the client's personal taste override the audience. CLAIM(2RO44hoGdlE@03:41)
- Adding detail or effects to rescue a forgettable base shape. CLAIM(2RO44hoGdlE@01:54)
- Shipping a raster file or a JPEG as the master. CLAIM(T54ytwmlObg@05:24, JFai8IzN-3k@06:35)
- One spacing value for every size and every ground color. CLAIM(JFai8IzN-3k@07:24, DtxyRhd6WJU@03:39)
- Sending files without opening the export. CLAIM(JFai8IzN-3k@06:00)
- A concept so hidden that the name is unreadable. CLAIM(KV5rW93PLw8@02:07)
- plus 6 more in references/<sub-skill>.md files

## Creator disagreements (stated, not resolved)

- Exact circles versus nudged circles. Satori's 2018 construction tutorial requires perfect circles and exact doubles, snapped with smart guides. Will Paterson (2024) says a perfect circle looks amateur and tells you to nudge the handles slightly, because people judge width better than height. Hold the construction grid, make the optical nudge last, and record which one you shipped. CLAIM(rGmGRMXKqUQ@01:42, gza5-1e0IY4@04:49, gza5-1e0IY4@05:01)
- Literal cue versus non-literal mark. Satori says a bulb for an electrician is the wrong job. Will's noun method draws two simple icons from the business and combines them, and in a redesign he adds a keyhole to a wordmark named Vault because the name is a category word. Use a literal cue only when it is built from shapes already in the mark and still reads at small size. Do not paste a product picture on. CLAIM(T54ytwmlObg@01:55, gza5-1e0IY4@02:01, 53H8XGIp0ac@06:29, 53H8XGIp0ac@06:51)
- Gradient as craft versus gradient as risk. Satori's 2018 tutorial stacks gradient layers, including transparent stops, to add depth. Flux (2022 and 2023) says continuous gradients are a reproduction problem and that single-tone gray gradients look dated. Keep a solid master. Treat the stacked gradient as a 2018 digital skin, not the identity. CLAIM(rGmGRMXKqUQ@06:49, DtxyRhd6WJU@07:49, KV5rW93PLw8@24:16)
- How to make the white version. Every Tuesday (2015) says change the color to black and to white for limited-color print. Will Paterson (2025) and Flux (2023) say a recolor is not an inversion: holes fill in and counters shrink, so the reverse is a separate drawing. Ship a simple one-color white for one-color print, and a rebuilt negative for dark UI. CLAIM(mLOUtiRt8JA@01:07, 0JmAzciKYx0@02:34, DtxyRhd6WJU@03:39)
- Minimum versus readable. Will, redesigning a submitted mark, says ultra-minimal can fail and that a G needs enough geometry to be read. Satori and Flux still treat simplicity as the memory rule, with a floor: do not strip identity, and do not hide the name. The check is the 16-pixel read, not the stroke count. CLAIM(53H8XGIp0ac@04:37, 2RO44hoGdlE@00:27, KV5rW93PLw8@02:07)

## Creator claims (unverified)

- Simplicity breeds recognition, which breeds more business and profit. Stated as the reason a logo exists. Not measured. CLAIM(T54ytwmlObg@02:22, T54ytwmlObg@02:32)
- People see hundreds, potentially thousands, of logos a day. CLAIM(2RO44hoGdlE@01:33)
- A tagline tracking example set to 1200. Unit as spoken, not a spec. CLAIM(JFai8IzN-3k@07:16)
- Galileo saw Venus with a radiant crown that made it look 8 to 10 times larger than Jupiter, used to explain why a light mark on a dark ground looks bigger. Anecdote, not a design measurement. CLAIM(gza5-1e0IY4@00:35)
- A client project may need tens or hundreds of variations. Stated as practice, not counted. CLAIM(LBAI4ogp9C4@10:42)
- Stylescapes reduce revision requests and speed approval. Outcome claimed, not measured in the video. CLAIM(9MOuHiQWFoU@00:00, 9MOuHiQWFoU@14:44)
- Spot printing is charged by the number of colors. Pricing claim, not verified against a printer. CLAIM(mLOUtiRt8JA@07:13)
- A stock-asset subscription described as 55 million assets, half off annually, under 20 a month, with the license surviving cancellation. Sales copy inside the video. CLAIM(53H8XGIp0ac@09:15, 53H8XGIp0ac@09:26, 53H8XGIp0ac@09:43)

## Tool-specific (dated)

- Illustrator shape builder (Shift+M), smart guides, stroke-only source shapes, Alt-drag to subtract, then stacked gradients with a 0% stop for depth. Tutorial year 2018. CLAIM(rGmGRMXKqUQ@01:02, rGmGRMXKqUQ@03:43, rGmGRMXKqUQ@06:49)
- Illustrator Save As for AI, EPS (TIFF 8-bit preview), and PDF (newest Acrobat, view after save, no bleed on a logo-only file). Save for Web for PNG-8, PNG-24, and JPEG. Asset Export for multiple artboards (Illustrator CC, 2018). CLAIM(JFai8IzN-3k@01:10, JFai8IzN-3k@02:32, JFai8IzN-3k@05:17, JFai8IzN-3k@08:05)
- Save the native file compatible with Illustrator CS3 or newer so the next designer can open it (2015). CLAIM(mLOUtiRt8JA@00:38, mLOUtiRt8JA@00:54)
- Save for Web JPEG quality raised from the default 60 to 65, exported at 600 pixels so a developer can shrink it (2015). CLAIM(mLOUtiRt8JA@09:17, mLOUtiRt8JA@09:31)
- Object > Expand on a stroke, then Pathfinder Unite, to turn an outline into a fill that can take a gradient. Illustrator CS5, stated as similar in CS3 and CS4 (2011). CLAIM(RwC4cnv9IAo@02:00, RwC4cnv9IAo@02:11, RwC4cnv9IAo@05:08)
- Illustrator 2023 demo of overshoot guides, expand stroke, and a tracking plus-10 on a reversed wordmark. The plus-10 is a demo guess, not a spec. CLAIM(DtxyRhd6WJU@00:10, DtxyRhd6WJU@04:18)
- Pathfinder subtract and Object > Expand to turn a stroke cut into one shape (2022). CLAIM(LBAI4ogp9C4@04:19, LBAI4ogp9C4@04:28)
- Optical versus metric tracking for wordmarks. Metric is the type designer's reading spacing. Optical is the app's own guess (2024). CLAIM(gza5-1e0IY4@04:08, gza5-1e0IY4@04:24)
- plus 9 more in the corpus law file studio-corpus/laws/brand_identity.md

## Hand-off
- Next stage: ds-typography, ds-color. Agent: `ds-brand-designer` (sub: ds-type-pairer).
- Corpus source: studio-corpus/laws/brand_identity.md (regenerate skills with tools/build_skills.py after a corpus refresh).
- Nothing outward (deploy, publish, push) without Gate-D: `ds-pre-publish-gate-d` enforces it once wired.
