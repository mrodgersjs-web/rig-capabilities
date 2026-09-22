---
name: rig-write-substack
description: >-
  Use to WRITE or DRAFT substack (Communications OS v6 surface engine): assembles the write packet
  (voice v2 + wounds + behavior fusion + corpus + persona), scores the artifact
  through the deterministic gate stack, and records the loop.
owner: rig-intelligence
domain: Communications
status: Stable
acl: public
tags: [writing,substack,communications,surfaces]
outcome: "content-publishing: substack drafts are engine-assembled and gate-scored, never written blind"
done_when:
  - grep:capabilities/skills/rig-write-substack/SKILL.md:rig-communications-core
  - cmd:cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comms packet --surface substack --brief /dev/null > /dev/null; test $? -eq 0
quality_floor: 0.6
---

# /write substack - surface engine

**Lane:** public. **Gate-D:** BEFORE PUBLISH (public lane). **Deviation budget:** 2 candidates before convergence.

## Own it

marcus long-form drafting + eleanor editorial direction (installed skills); receipts density and argument structure carry the piece.

## Assemble (agent runs this FIRST)

```bash
cd capabilities/skills/rig-communications-core
PYTHONPATH=. python3 -m rig_comms packet --surface substack --brief <brief-file> --persona substack-operator-reader
```

The packet names the doctrine to load (core, wounds, voice v2, behavior
fusions: bx-process-miner, bx-falsifier), corpus grounding, template, and the ship gate. Draft only after.

## Score before claiming done

```bash
PYTHONPATH=. python3 -m rig_comms score --surface substack --artifact <draft-file>
# exit 0 green - exit 2 red with named blocks - fix, re-loop (max 3, then escalate)
```

