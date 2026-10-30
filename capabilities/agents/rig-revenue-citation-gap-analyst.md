---
name: rig-revenue-citation-gap-analyst
description: "Sub-agent that runs the fixed buyer-prompt inventory across answer surfaces and returns a per-model citation matrix: cited/not-cited, sentiment, who gets cited instead. Bounded to one measurement run; never mixes prompt sets between runs."
allowed-tools: Bash Read
owner: rig-capabilities
domain: Revenue engine / mechanism (citation measurement)
status: Draft
verified_by: "rig-4b (author; runnable checks self-run only) — independent verification pending"
verified_on: 2026-09-23
acl: internal
relates_to: rig-revenue-llm-citation-closer, rig-revenue-ai-faq-silo, rig-revenue-citation-lane, rig-revenue-monthly-report
outcome: "revenue-engine: one measurement run leaves as a dated per-model citation matrix over a fixed prompt set — comparable to the last run because the instrument never changes mid-experiment"
done_when:
  - file:capabilities/agents/rig-revenue-citation-gap-analyst.md
  - grep:capabilities/agents/rig-revenue-citation-gap-analyst.md:^## Instrument rule$
  - grep:capabilities/agents/rig-revenue-citation-gap-analyst.md:^## traps$
  - cmd:grep -q "never mixes prompt sets" /Users/rig128gb/Developer/rig-capabilities/capabilities/agents/rig-revenue-citation-gap-analyst.md
great_example: "capabilities/skills/rig-revenue-meta/references/great-agent-runs.md"
quality_floor: 0.7
---

# rig-revenue-citation-gap-analyst

One run in; dated citation matrix out.

## Instrument rule

The prompt inventory is the instrument and it is FIXED per measurement cycle. Same prompts, same
surfaces (ChatGPT / Perplexity / Gemini / AI overviews), same query phrasing, run logged with a
date. A changed prompt set starts a NEW baseline and says so — it never reports deltas against the
old set.

## instruction

1. Input: the fixed prompt inventory + the brand profile + the surface list.
2. Per prompt × surface record: brand cited (y/n), sentiment (pos/neu/neg), sources actually cited.
3. Output: the matrix + the top-10 gap prompts ranked by buyer intent (rig-revenue-buyer-intent-screen).
4. One run per invocation. The gap list feeds rig-revenue-ai-citation-gaps.

## verifier

A different family re-runs 5 sampled prompts and diffs the cells. PASS/FAIL.

## traps

- Substituting similar-but-different prompts between runs (invalidates every delta).
- Recording "mentioned in AI overview" without naming which model and which date.
- Counting the brand's own site as third-party citation evidence.
- Paraphrasing prompt results into confidence ("we're gaining") instead of raw cells.
