---
name: rig-write-film-scripts
description: >-
  Use to WRITE or DRAFT film-scripts (Communications OS v6 surface engine): assembles the write packet
  (voice v2 + wounds + behavior fusion + corpus + persona), scores the artifact
  through the deterministic gate stack, and records the loop.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [writing,film-scripts,communications,surfaces]
outcome: "content-publishing: film-scripts drafts are engine-assembled and gate-scored, never written blind"
done_when:
  - grep:capabilities/skills/rig-write-film-scripts/SKILL.md:rig-communications-core
  - cmd:cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comms packet --surface film-scripts --brief /dev/null > /dev/null; test $? -eq 0
quality_floor: 0.6
---

# /write film-scripts - surface engine

**Lane:** internal. **Gate-D:** before send/share (internal lane). **Deviation budget:** 3 candidates before convergence.

## Own it

Screenplay format + beat sheets; rig-film-studio treatment downstream; corpus-grounded scene craft from writing-craft/screenwriting-film transcripts.

## Assemble (agent runs this FIRST)

```bash
cd capabilities/skills/rig-communications-core
PYTHONPATH=. python3 -m rig_comms packet --surface film-scripts --brief <brief-file>
```

The packet names the doctrine to load (core, wounds, voice v2, behavior
fusions: bx-emotion-cartographer, bx-falsifier), corpus grounding, template, and the ship gate. Draft only after.

## Score before claiming done

```bash
PYTHONPATH=. python3 -m rig_comms score --surface film-scripts --artifact <draft-file>
# exit 0 green - exit 2 red with named blocks - fix, re-loop (max 3, then escalate)
```

