---
name: rig-write-linkedin
description: >-
  Use to WRITE or DRAFT linkedin (Communications OS v6 surface engine): assembles the write packet
  (voice v2 + wounds + behavior fusion + corpus + persona), scores the artifact
  through the deterministic gate stack, and records the loop.
owner: rig-intelligence
domain: Communications
status: Stable
acl: public
tags: [writing,linkedin,communications,surfaces]
outcome: "content-publishing: linkedin drafts are engine-assembled and gate-scored, never written blind"
done_when:
  - grep:capabilities/skills/rig-write-linkedin/SKILL.md:rig-communications-core
  - cmd:cd capabilities/skills/rig-communications-core && PYTHONPATH=. python3 -m rig_comms packet --surface linkedin --brief /dev/null > /dev/null; test $? -eq 0
quality_floor: 0.6
---

# /write linkedin - surface engine

**Lane:** public. **Gate-D:** BEFORE PUBLISH (public lane). **Deviation budget:** 2 candidates before convergence.

## Own it

The alfred suite (chaos pipeline, drafter, publisher) stays BEHAVIOR-UNCHANGED; this engine supplies voice v2 + gates + wound layer it scores against.

## Assemble (agent runs this FIRST)

```bash
cd capabilities/skills/rig-communications-core
PYTHONPATH=. python3 -m rig_comms packet --surface linkedin --brief <brief-file> --persona icp-pe-operator
```

The packet names the doctrine to load (core, wounds, voice v2, behavior
fusions: bx-emotion-cartographer, bx-influence-designer, bx-falsifier), corpus grounding, template, and the ship gate. Draft only after.

## Score before claiming done

```bash
PYTHONPATH=. python3 -m rig_comms score --surface linkedin --artifact <draft-file>
# exit 0 green - exit 2 red with named blocks - fix, re-loop (max 3, then escalate)
```

