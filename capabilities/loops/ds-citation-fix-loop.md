---
name: ds-citation-fix-loop
tier: sub
parent: ds-corpus-refresh-loop
max_rounds: 3
owner_agent: ds-citation-verifier
outcome: "design-ux: repair unresolved or copied citations"
done_when:
  - file:capabilities/loops/ds-citation-fix-loop.md
  - cmd:python3 scripts/assert_loop_termination.py capabilities/loops/ds-citation-fix-loop.md
---

# ds-citation-fix-loop (sub loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: repair unresolved or copied citations

## Steps
1. claims_check.py lists findings
2. Re-find the timestamp in the transcript or drop the claim
3. Re-run

## Exit
claims_check.py exit 0.

Hard stop after 3 rounds: hand the open findings to Mike with a recommendation instead of looping.

## Definition of Done
1. Exit condition met: claims_check.py exit 0.
2. Round counter stops at max_rounds = 3; the loop never starts round 4.
3. On the hard stop, the open findings go to Mike with a recommendation and the run is recorded as stopped, not as passed.
4. A Jev DEFERRED verdict ends the round as DEFERRED and is reported as such, never as a pass.
