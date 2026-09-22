---
name: rig-communications-behavior
description: >-
  Behavioral-science fusion for the Communications OS (v4): maps each writing
  surface to the bx-* suite skills (need hierarchy, emotional journey, choice
  model, committee, influence, COM-B, measurement trust, falsifier, wren,
  council) with load order and gate contributions.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [behavioral,communications,writing,bx,gates]
outcome: "content-publishing: every high-stakes artifact carries a named need-hierarchy, emotional journey, decision prediction, and a falsifier note with a named control before it ships"
done_when:
  - grep:capabilities/skills/rig-communications-behavior/SKILL.md:bx-falsifier
  - cmd:python3 -c "import pathlib as p; d=p.Path('capabilities/skills/rig-communications-behavior/fusions'); fs=[f.name for f in d.glob('*.md')]; assert len(fs)==10, fs"; test $? -eq 0
quality_floor: 0.6
---

# RIG Communications Behavior (v4)

Fuses the installed behavioral-science suite (`bx-*`, owner Wren, all four
harness roots) into the writing pipeline. One fusion file per v4 layer under
`fusions/`, each quoting the real installed mandate and naming what it produces
for a draft and which gate consumes it.

## Surface -> fusion load order

| Surface | Load (in order) | Skip |
|---|---|---|
| emails | need-architect -> intervention-designer (CTA) -> decision-modeler -> falsifier (high-stakes only) | council |
| linkedin | emotion-cartographer -> influence-designer -> decision-modeler; flagship: + falsifier + council | committee |
| substack | process-miner -> emotion-cartographer; flagship: + falsifier + council | intervention |
| resumes | need-architect -> committee-simulator (hiring committee) -> measurement-steward (claims) | council, songs |
| specs | decision-modeler -> committee-simulator (B2B) -> falsifier (design claims) | emotion, council |
| film-scripts / novels / songs | emotion-cartographer; flagship: council | everything transactional |
| code / prompts | measurement-steward (metrics honesty) only | all persuasion lanes |
| love-notes | HUMAN ONLY — no bx run (private lane, v19.6 lock) | everything |

## Hard rules

- bx-falsifier on any artifact whose failure has a named cost: the note must
  name (a) the disconfirming evidence and (b) the control. No note = not
  high-stakes-tested = do not claim behavioral-fit.
- Every influence device states expected effect or is deleted.
- Prediction rows go to the calibration ledger (`rig-comm ledger predict`);
  unmeasured stays UNMEASURED (v11 honesty rule).
- Nothing measured on named individuals without Gate-D (wren's line).
