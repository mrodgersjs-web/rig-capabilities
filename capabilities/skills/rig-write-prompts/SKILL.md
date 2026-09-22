---
name: rig-write-prompts
description: >-
  Use to WRITE or DRAFT prompts (Communications OS v6 surface engine): assembles the write packet
  (voice v2 + wounds + behavior fusion + corpus + persona), scores the artifact
  through the deterministic gate stack, and records the loop.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [writing,prompts,communications,surfaces]
outcome: "content-publishing: prompts drafts are engine-assembled and gate-scored, never written blind"
done_when:
  - grep:capabilities/skills/rig-write-prompts/SKILL.md:rig-communications-core
  - cmd:cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comms packet --surface prompts --brief /dev/null > /dev/null; test $? -eq 0
quality_floor: 0.6
---

# /write prompts - surface engine

**Lane:** internal. **Gate-D:** before send/share (internal lane). **Deviation budget:** 1 candidates before convergence.

## Own it

CO-STAR + tac-v2/v3 prompt doctrine + rig-ai-engineering 4-axis rubric. Path is chosen at runtime, never narrated.

## Assemble (agent runs this FIRST)

```bash
cd capabilities/skills/rig-communications-core
PYTHONPATH=. python3 -m rig_comms packet --surface prompts --brief <brief-file>
```

The packet names the doctrine to load (core, wounds, voice v2, behavior
fusions: bx-measurement-steward), corpus grounding, template, and the ship gate. Draft only after.

## Score before claiming done

```bash
PYTHONPATH=. python3 -m rig_comms score --surface prompts --artifact <draft-file>
# exit 0 green - exit 2 red with named blocks - fix, re-loop (max 3, then escalate)
```

