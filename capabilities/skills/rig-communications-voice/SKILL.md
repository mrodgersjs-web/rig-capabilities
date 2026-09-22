---
name: rig-communications-voice
description: >-
  Voice Fingerprint v2 for the Communications OS (v5): locked fingerprint,
  12-surface register map, drift detector, and the sample-extraction procedure.
  Deterministic scoring runs in rig-communications-core/rig_comms/voice.py.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [voice,fingerprint,communications,writing,gates]
outcome: "content-publishing: every artifact is scored against fingerprint v2 and drift-checked against the last approved draft before ship"
done_when:
  - grep:capabilities/skills/rig-communications-voice/SKILL.md:fingerprint v2
  - file:capabilities/skills/rig-communications-voice/references/fingerprint-v2.md
  - cmd:python3 -c "import pathlib as p; d=p.Path('capabilities/skills/rig-communications-voice'); fs=['references/fingerprint-v2.md','references/surface-register.md','references/drift-detector.md','samples/README.md']; missing=[f for f in fs if not (d/f).exists()]; assert not missing, missing"; test $? -eq 0
quality_floor: 0.6
---

# RIG Communications Voice (v5)

One fingerprint, twelve registers. The merge: rig-voice-engineering's 7-axis
scorecard + content-voice-fingerprint-extractor's quantification +
voice-builder's interview schema, now enforced as code.

## Deterministic core (canonical)

`../rig-communications-core/rig_comms/voice.py` — `FINGERPRINT`, `score_voice`,
`drift`. From the core skill dir:

```bash
PYTHONPATH=. python3 -m rig_comms voice-check --artifact draft.md
# exit 0 = deterministic axes clean (agent axes 6/7 still pending)
# exit 2 = REVISE or BLOCK (banned words / 5-sentence paragraph)
```

## Files

| File | Use when |
|---|---|
| references/fingerprint-v2.md | any draft — the locked axes, banned list, vocab windows, wound-authenticity rule |
| references/surface-register.md | choosing the register an artifact wears; intimate/James is private-only |
| references/drift-detector.md | comparing a draft to the last approved artifact per surface |
| samples/README.md | extracting real writing samples per surface (DATA GAP until the floor is met) |

## Rules

- Axes 1/4 violations and forbidden wounds are BLOCKs, not suggestions.
- Axes 6–7 (manifesto fit, cadence) are agent calls; this stack refuses to fake PASS on them.
- Repeated corrections land in the fingerprint (correction-to-memory), not in chat.
- The intimate register never appears in federated/public surfaces, corpus, or exemplar library.
