---
name: ds-slop-rewrite-loop
tier: sub
parent: ds-critique-revise-loop
max_rounds: 3
owner_agent: ds-slop-linter
outcome: "design-ux: rewrite copy until the anti-slop lint is clean"
done_when:
  - file:capabilities/loops/ds-slop-rewrite-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/ds-slop-rewrite-loop.md
---

# ds-slop-rewrite-loop (sub loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: rewrite copy until the anti-slop lint is clean

## Steps
1. ds-slop-linter flags AI tells
2. ds-copywriter rewrites flagged lines only
3. Re-lint

## Exit
Zero blocker-level tells.

Hard stop after 3 rounds: hand the open findings to Mike with a recommendation instead of looping.

## Definition of Done
1. Exit condition met: Zero blocker-level tells.
2. Round counter stops at max_rounds = 3; the loop never starts round 4.
3. On the hard stop, the open findings go to Mike with a recommendation and the run is recorded as stopped, not as passed.
4. A Jev DEFERRED verdict ends the round as DEFERRED and is reported as such, never as a pass.
