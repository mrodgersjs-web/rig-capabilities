---
name: ds-ui-judge-loop
tier: main
parent: ds-mission-loop
max_rounds: 2
owner_agent: ds-image-judge
outcome: "design-ux: judge every screen at every viewport from real captures (reuses app-ui-judge-loop in rig-capabilities)"
done_when:
  - file:studio-harness/loops/ds-ui-judge-loop.md
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
