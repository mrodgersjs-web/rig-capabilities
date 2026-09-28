---
outcome: "design-ux: each spec screen goes capture -> judge -> fix until the image judge and JEV ui.design are clean, or escalates after three rounds - never passing on a DEFERRED judge"
done_when:
  - file:capabilities/loops/app-ui-judge-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/app-ui-judge-loop.md
  - cmd:python3 capabilities/skills/app-studio/scripts/validate_hierarchy.py
quality_floor: 0.7
---

# App UI Judge Loop - SUB loop of app-studio-mission-loop

Parent: `app-studio-mission-loop` (gate G6). Executor: `app-ui-judge`. Skill:
`app-ui-design`. The builder fixes; the judge never judges its own screens.

JEV first: each capture goes to `~/.rig/bin/advisor-plus judge-image` and `rig-s1gate
check ui.design` BEFORE any frontier critique. A DEFERRED judge is a named gap, not a pass.

## Loop

```
CAPTURE real screen at viewport -> JUDGE (judge-image + ui.design)
  -> clean: RECORD verdict row
  -> not clean: builder FIXES -> RE-CAPTURE (round 2, 3) -> still not clean: ESCALATE
  -> DEFERRED: RECORD as DEFERRED, retry when a vision judge answers
```

## Gates

| Gate | Pass Condition | On fail |
|---|---|---|
| G1 | the capture comes from the real running app at the target viewport or simulator | recapture; renders and source do not count |
| G2 | judge-image verdict clean and ui.design required signals above 0.9 | builder fixes, re-capture |
| G3 | clean within three rounds | ESCALATE to Mike with images and signals |
| G4 | accessibility notes recorded for the screen | run the fixing-accessibility checks |

**On-fail:** G1 with a render or mockup: HALT the round; a non-real screen is not evidence.
**On-fail:** G3 after the third round: HALT and ESCALATE with the three captures.
**On-fail:** a DEFERRED judge: HALT the screen's pass and record DEFERRED; never promote it to PASS.

## Definition of Done

The loop is done for a screen when:
1. a real capture exists for every target viewport;
2. judge-image and ui.design are clean for each capture, or the screen is escalated with evidence;
3. no DEFERRED row was counted as a pass.
