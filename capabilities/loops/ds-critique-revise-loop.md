---
name: ds-critique-revise-loop
tier: main
parent: ds-mission-loop
max_rounds: 3
owner_agent: ds-critic
outcome: "design-ux: turn critique findings into revisions until blockers are zero"
done_when:
  - file:studio-harness/loops/ds-critique-revise-loop.md
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
