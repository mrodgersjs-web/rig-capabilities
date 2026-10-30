---
name: ds-ui-judge-loop
tier: main
parent: ds-mission-loop
max_rounds: 2
owner_agent: ds-image-judge
outcome: "design-ux: judge every screen at every viewport from real captures (reuses app-ui-judge-loop in rig-capabilities)"
done_when:
  - file:capabilities/loops/ds-ui-judge-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/ds-ui-judge-loop.md
---

# ds-ui-judge-loop (main loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: judge every screen at every viewport from real captures (reuses app-ui-judge-loop in rig-capabilities)

## Steps
1. Capture 375/768/1440
2. advisor-plus judge-image with the brief
3. Jev ui.design
4. Record verdict rows

## Exit
Every screen has a verdict row with image path and decision id.

Hard stop after 2 rounds: hand the open findings to Mike with a recommendation instead of looping.

## Definition of Done
1. Exit condition met: Every screen has a verdict row with image path and decision id.
2. Round counter stops at max_rounds = 2; the loop never starts round 3.
3. On the hard stop, the open findings go to Mike with a recommendation and the run is recorded as stopped, not as passed.
4. A Jev DEFERRED verdict ends the round as DEFERRED and is reported as such, never as a pass.
