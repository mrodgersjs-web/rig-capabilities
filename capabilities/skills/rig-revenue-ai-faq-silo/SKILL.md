---
name: "rig-revenue-ai-faq-silo"
description: "Build a local-service FAQ silo: 60 buyer questions in 6 categories, flag the 10 gap questions, wire FAQ hub to category pages to money pages, and feed the question set to content and monitoring. Use when the trigger is 'FAQ strategy', 'question topics', 'build the FAQ silo', or 'what should we answer'."
done_when:
  - grep:capabilities/skills/rig-revenue-ai-faq-silo/SKILL.md:## Step 1. Generate the 60
  - grep:capabilities/skills/rig-revenue-ai-faq-silo/SKILL.md:## Step 2. Flag the 10 gaps
---

# AI FAQ silo (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Questions come from real buyer language — conversational,
local, specific — because that is the assistant query surface (CLAIM: 5it1VVQjya0).

## Step 1. Generate the 60

Six categories: pricing/financing, process/timeline, scope/fit/comparisons, service
area/availability, credentials/ethics-of-hiring, urgent scenarios. Write each question the way a
person types to an assistant ("who should I call when..."), mixing awareness stages.

## Step 2. Flag the 10 gaps

Mark the ~10 questions competitors answer poorly or not at all — these are gold. Rank by buyer
intent (rig-revenue-buyer-intent-screen). Add 3 blog/answer-page ideas per gap cluster.

## Step 3. Wire the silo

FAQ index → category pages → money pages, with circular internal links (every answer links up to
its service page; the service page links back to its best answers). Submit to GSC.

## Step 4. Feed everything downstream

- Gap questions → rig-revenue-weekly-content-run briefs
- Question set → rig-revenue-llm-citation-closer monitoring
- FAQ block → rig-revenue-answer-first on every new page

## done_when

- file:capabilities/skills/rig-revenue-ai-faq-silo/SKILL.md
- grep:capabilities/skills/rig-revenue-ai-faq-silo/SKILL.md:^## Step 2. Flag the 10 gaps
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-ai-faq-silo/SKILL.md

## Provenance (videoIds)

5it1VVQjya0, vb9SMtUiAIw, K59PbDhBY5M (voice/FAQ phrasing), ONPusps0wjk (question mining),
Hc2Q4BH4G6k.
