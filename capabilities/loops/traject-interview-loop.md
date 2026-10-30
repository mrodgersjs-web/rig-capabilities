---
outcome: "interview-prep: one interview cycle runs prep -> drill -> interview -> debrief (≤2h) -> follow-up (same day) -> learn, each stage gated, with numbers-or-NONE enforced and nothing sent past Gate-D"
done_when:
  - file:capabilities/loops/traject-interview-loop.md
  - cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py
quality_floor: 0.7
---

# Traject Interview Loop - SUB loop

Parent: `traject-daily-loop`. Owner: `traject-conductor`. Harness:
`capabilities/harnesses/traject-interview-prep-session.yaml`. Sub-skills: `traject-room-build`,
`traject-drill`, `traject-debrief`, `traject-follow-up`, `traject-learn`.

JEV first: room gates (story.bank, jd.decode) and answer gates (interview.answer,
training.readiness) route to `rig-s1gate` BEFORE any frontier review. Classifier down: DEFER.

## Loop

```
PREP (room: Stage 0-8 + Run of Show/DECISIONS/debrief) -> DRILL (numbers-or-NONE)
  -> INTERVIEW (live coach) -> DEBRIEF (≤2h, 5-line CODE) -> FOLLOW-UP (same day, held at Gate-D)
  -> LEARN (lessons + gaps)
```

## Gates

| Gate | Stage | Pass Condition | On fail |
|---|---|---|---|
| G1 | prep | room built from verified claims; story.bank + jd.decode above 0.9 | rebuild; never pad |
| G2 | drill | every rep states a number or NONE; interview.answer above 0.9 | re-drill the card |
| G3 | interview | live answers carry numbers; no floor/banned claim spoken | note the gap for debrief |
| G4 | debrief | 5-line debrief saved within 2h (CODE shape) | rewrite the block |
| G5 | follow-up | thank-you drafted (150-300 words); one ask one nudge; held at Gate-D | rewrite; never send |
| G6 | learn | gaps routed to traject-learn; lessons filed | app-lesson loop |

**On-fail:** G1-G3, G6 halt-tier; G4 degrade-tier; G5 stop-tier (thank-you is outward).
An invitation is not attendance (TL-03): the interview is INVITED until confirmed.

## Definition of Done

The cycle is done when the room is built and drilled, the interview ran with numbers, the 5-line
debrief is captured, the thank-you is drafted and held at Gate-D, and the gaps reached the ledger.
