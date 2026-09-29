---
name: ds-corpus-refresh-loop
tier: main
parent: ds-mission-loop
max_rounds: 1
owner_agent: ds-citation-verifier
outcome: "design-ux: pull new uploads from the top-10 channels and fold new laws into the stage files"
done_when:
  - file:studio-harness/loops/ds-corpus-refresh-loop.md
---

# ds-corpus-refresh-loop (main loop)

JEV FIRST: every round's pass/fail judgment goes to rig-s1gate (Jev) before any frontier LLM call; DEFERRED ends the round as DEFERRED, never as pass.

Purpose: pull new uploads from the top-10 channels and fold new laws into the stage files

## Steps
1. harvest.sh inventory + transcripts for top-10 slugs
2. build_manifest.py, tag_stages.py
3. Distill only new dense how-to videos into studio-corpus/laws/<stage>.md
4. claims_check.py on changed files

## Exit
Manifest rebuilt, new videos tagged, changed law files pass claims_check.

Hard stop after 1 rounds: hand the open findings to Mike with a recommendation instead of looping.
