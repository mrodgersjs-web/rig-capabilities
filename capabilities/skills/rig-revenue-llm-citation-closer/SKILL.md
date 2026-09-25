---
name: "rig-revenue-llm-citation-closer"
description: "Measure where a brand is absent from AI answers per model for its buyer prompts, then close each gap with one targeted governed page and re-measure. Use when the trigger is 'cited nowhere in ChatGPT', 'per-model visibility', 'citation share', or 'LLM brand monitor'."
---

# LLM Citation Closer (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Measurement is manual or client-approved tooling — the
corpus's monitor is inside a PAID ENDORSEMENT product (Arvow/Journalist AI LLM brand monitors).

## Step 1. Load the prompt set

The buyer prompts from rig-revenue-ai-faq-silo / rig-revenue-buyer-intent-screen (pricing,
comparison, trust, local, urgency groups). More prompts, not fewer — cover every service/area
(CLAIM: oyc-XSLRbBE).

## Step 2. Measure per model

For each prompt × each answer surface (ChatGPT, Perplexity, Gemini, Google AI overviews): is the
brand mentioned? positively/neutrally/negatively? which sources does the answer cite? Record the
date — the surface changes fast.

## Step 3. Close the weakest gaps first

1. Take the lowest-visibility high-buyer-intent prompts.
2. One governed page per prompt: the prompt as the H1, answer-first body, the brand's real
   differentiator stated plainly, FAQ block (rig-revenue-answer-first).
3. Route through rig-revenue-seo-council and rig-revenue-publish-gate.

## Step 4. Re-measure on a fixed cadence

Monthly: same prompts, same surfaces. Report deltas per prompt per model in
rig-revenue-monthly-report. The prompt list is the content plan for the next six months to a year
(CLAIM: vb9SMtUiAIw).

## done_when

- file:capabilities/skills/rig-revenue-llm-citation-closer/SKILL.md
- grep:capabilities/skills/rig-revenue-llm-citation-closer/SKILL.md:^## Step 2. Measure per model
- grep:capabilities/skills/rig-revenue-llm-citation-closer/SKILL.md:PAID ENDORSEMENT
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-llm-citation-closer/SKILL.md

## Provenance (videoIds)

oyc-XSLRbBE, vb9SMtUiAIw, IZyBUAkzfp8, vmQd5FG5GfM, MH6B51jrDOA.
