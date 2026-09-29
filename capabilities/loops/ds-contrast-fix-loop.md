---
name: ds-contrast-fix-loop
tier: sub
parent: ds-critique-revise-loop
max_rounds: 3
owner_agent: ds-contrast-checker
outcome: "design-ux: fix failing color pairs until contrast passes"
done_when:
  - file:studio-harness/loops/ds-contrast-fix-loop.md
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
