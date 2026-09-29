---
name: ds-slop-rewrite-loop
tier: sub
parent: ds-critique-revise-loop
max_rounds: 3
owner_agent: ds-slop-linter
outcome: "design-ux: rewrite copy until the anti-slop lint is clean"
done_when:
  - file:studio-harness/loops/ds-slop-rewrite-loop.md
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
