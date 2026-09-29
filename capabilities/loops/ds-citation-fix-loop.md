---
name: ds-citation-fix-loop
tier: sub
parent: ds-corpus-refresh-loop
max_rounds: 3
owner_agent: ds-citation-verifier
outcome: "design-ux: repair unresolved or copied citations"
done_when:
  - file:studio-harness/loops/ds-citation-fix-loop.md
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
