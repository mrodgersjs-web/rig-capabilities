---
name: rig-write-love-notes
description: >-
  Use to WRITE or DRAFT love-notes (Communications OS v6 surface engine): assembles the write packet
  (voice v2 + wounds + behavior fusion + corpus + persona), scores the artifact
  through the deterministic gate stack, and records the loop.
owner: rig-intelligence
domain: Communications
status: Stable
acl: private
tags: [writing,love-notes,communications,surfaces]
outcome: "content-publishing: love-notes drafts are engine-assembled and gate-scored, never written blind"
done_when:
  - grep:capabilities/skills/rig-write-love-notes/SKILL.md:rig-communications-core
  - grep:capabilities/skills/rig-write-love-notes/SKILL.md:never autonomous
quality_floor: 0.6
---

# /write love-notes - surface engine

**Lane:** private. **Gate-D:** n/a. **Deviation budget:** 1 candidates before convergence.

## Own it

Authenticity gate is HUMAN and supreme. No machine scores, no agent drafts autonomously, nothing federated. Mike writes; Mike ships.

## Assemble (agent runs this FIRST)

```bash
cd capabilities/skills/rig-communications-core
PYTHONPATH=. python3 -m rig_comms packet --surface love-notes --brief <brief-file> --persona james
```

The packet names the doctrine to load (core, wounds, voice v2, behavior
fusions: bx-emotion-cartographer), corpus grounding, template, and the ship gate. Draft only after.

## Score before claiming done

```bash
PYTHONPATH=. python3 -m rig_comms score --surface love-notes --artifact <draft-file>
# exit 0 green - exit 2 red with named blocks - fix, re-loop (max 3, then escalate)
```

The scoring stack REFUSES this surface (exit 3, privacy lock - v19.6).
That refusal is the feature. Authenticity is human; loop count, never gate score.
