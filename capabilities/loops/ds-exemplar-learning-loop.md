---
name: ds-exemplar-learning-loop
tier: main
parent: ds-mission-loop
max_rounds: 1
owner_agent: ds-critic
outcome: "design-ux: turn every critique into new looks-like / does-not exemplar cards"
done_when:
  - file:studio-harness/loops/ds-exemplar-learning-loop.md
---

# ds-exemplar-learning-loop (main loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: turn every critique into new looks-like / does-not exemplar cards

## Steps
1. Collect critique findings with before/after captures
2. Write a pair card in studio-exemplars/pairs/
3. Jev ui.design on both images; keep only pairs where the good one outscores the bad one

## Exit
New pair cards pass the exemplar gate.

Hard stop after 1 rounds: hand the open findings to Mike with a recommendation instead of looping.
