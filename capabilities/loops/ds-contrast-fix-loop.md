---
name: ds-contrast-fix-loop
tier: sub
parent: ds-critique-revise-loop
max_rounds: 3
owner_agent: ds-contrast-checker
outcome: "design-ux: fix failing color pairs until contrast passes"
done_when:
  - file:capabilities/loops/ds-contrast-fix-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/ds-contrast-fix-loop.md
---

# ds-contrast-fix-loop (sub loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: fix failing color pairs until contrast passes

## Steps
1. ds-contrast-checker lists failing pairs
2. Adjust lightness only, keep hue
3. Re-check

## Exit
All pairs at or above 4.5:1 body, 3:1 large/UI.

Hard stop after 3 rounds: hand the open findings to Mike with a recommendation instead of looping.

## Definition of Done
1. Exit condition met: All pairs at or above 4.5:1 body, 3:1 large/UI.
2. Round counter stops at max_rounds = 3; the loop never starts round 4.
3. On the hard stop, the open findings go to Mike with a recommendation and the run is recorded as stopped, not as passed.
4. A Jev DEFERRED verdict ends the round as DEFERRED and is reported as such, never as a pass.
