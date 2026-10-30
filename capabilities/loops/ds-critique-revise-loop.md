---
name: ds-critique-revise-loop
tier: main
parent: ds-mission-loop
max_rounds: 3
owner_agent: ds-critic
outcome: "design-ux: turn critique findings into revisions until blockers are zero"
done_when:
  - file:capabilities/loops/ds-critique-revise-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/ds-critique-revise-loop.md
---

# ds-critique-revise-loop (main loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: turn critique findings into revisions until blockers are zero

## Steps
1. Critic lists findings with severity and cited law
2. Owner agent revises only what findings name
3. Recapture and re-judge

## Exit
Zero blocker findings and Jev ui.design PASS (or DEFERRED reported as such).

Hard stop after 3 rounds: hand the open findings to Mike with a recommendation instead of looping.

## Definition of Done
1. Exit condition met: Zero blocker findings and Jev ui.design PASS (or DEFERRED reported as such).
2. Round counter stops at max_rounds = 3; the loop never starts round 4.
3. On the hard stop, the open findings go to Mike with a recommendation and the run is recorded as stopped, not as passed.
4. A Jev DEFERRED verdict ends the round as DEFERRED and is reported as such, never as a pass.
