---
name: rig-write-code
description: >-
  Use to WRITE or DRAFT code (Communications OS v6 surface engine): assembles the write packet
  (voice v2 + wounds + behavior fusion + corpus + persona), scores the artifact
  through the deterministic gate stack, and records the loop.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [writing,code,communications,surfaces]
outcome: "content-publishing: code drafts are engine-assembled and gate-scored, never written blind"
done_when:
  - grep:capabilities/skills/rig-write-code/SKILL.md:rig-communications-core
  - cmd:cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comms packet --surface code --brief /dev/null > /dev/null; test $? -eq 0
quality_floor: 0.6
---

# /write code - surface engine

**Lane:** internal. **Gate-D:** before send/share (internal lane). **Deviation budget:** 0 candidates before convergence.

## Own it

Code-as-writing: naming, comments say why, commit messages imperative-what-why; docstrings as interface prose.

## Assemble (agent runs this FIRST)

```bash
cd capabilities/skills/rig-communications-core
PYTHONPATH=. python3 -m rig_comms packet --surface code --brief <brief-file>
```

The packet names the doctrine to load (core, wounds, voice v2, behavior
fusions: bx-measurement-steward), corpus grounding, template, and the ship gate. Draft only after.

## Score before claiming done

```bash
PYTHONPATH=. python3 -m rig_comms score --surface code --artifact <draft-file>
# exit 0 green - exit 2 red with named blocks - fix, re-loop (max 3, then escalate)
```

