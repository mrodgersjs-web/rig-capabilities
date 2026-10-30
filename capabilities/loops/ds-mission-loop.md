---
name: ds-mission-loop
tier: meta
max_rounds: 3
owner_agent: ds-director
outcome: "design-ux: one design mission from brief to Gate-D"
done_when:
  - file:capabilities/loops/ds-mission-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/ds-mission-loop.md
---

# ds-mission-loop (meta loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: one design mission from brief to Gate-D

## Steps
1. ds-director fixes mode and loads the matching main harness
2. Stage agents produce artifacts one stage at a time
3. ds-screen-capturer captures real screens
4. ds-critic plus Jev ui.design judge; run ds-critique-revise-loop on findings
5. ds-gate-ship; file Gate-D; stop

## Exit
All halt gates of the chosen harness evidenced and Gate-D request filed, or 3 rounds used.

Hard stop after 3 rounds: hand the open findings to Mike with a recommendation instead of looping.

## Definition of Done
1. Exit condition met: All halt gates of the chosen harness evidenced and Gate-D request filed, or 3 rounds used.
2. Round counter stops at max_rounds = 3; the loop never starts round 4.
3. On the hard stop, the open findings go to Mike with a recommendation and the run is recorded as stopped, not as passed.
4. A Jev DEFERRED verdict ends the round as DEFERRED and is reported as such, never as a pass.
