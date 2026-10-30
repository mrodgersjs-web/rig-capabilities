---
name: "rig-revenue-ai-overview-mirror"
description: "Mirror the live AI Overview's own structure in an article's headings so the page competes with (and can replace) the summarized answer: read the overview's sub-answers and PAA phrasings, build H1=question, H2s=their words. Use when the trigger is 'there's an AI Overview on this query', 'mirror the overview', or 'beat the AI box'."
done_when:
  - grep:capabilities/skills/rig-revenue-ai-overview-mirror/SKILL.md:## Step 3. Out-answer each section
  - grep:capabilities/skills/rig-revenue-ai-overview-mirror/SKILL.md:Run rig-revenue-answer-first on every section
---

# AI-Overview mirror (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. This is structure-matching to real queries — not answer
manipulation. No seeding fake sources (that play is excluded).

## Step 1. Read the live answer

Google the target question. Copy down (a) the AI Overview's sub-answers in its own phrasing and
(b) the "people also search for" queries below it.

## Step 2. Map the question set

H1 = the question itself. Each H2 = one sub-answer of the overview, phrased as the question a
buyer would ask about it. Add the PAA queries as further H2/FAQ items.

## Step 3. Out-answer each section

Run rig-revenue-answer-first on every section: the page's answer must be better, faster, and more
persuasive than the summary above it — concrete numbers, named expertise, honest caveats
(rig-revenue-meta evidence rule).

## Step 4. Brand the snippet

Include the firm's name in the concise factual sections most likely to be lifted, so a lifted
answer still attributes ("make sure your brand name appears right there in the text" — CLAIM:
IdugOOOOvwk).

## done_when

- file:capabilities/skills/rig-revenue-ai-overview-mirror/SKILL.md
- grep:capabilities/skills/rig-revenue-ai-overview-mirror/SKILL.md:^## Step 2. Map the question set
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-ai-overview-mirror/SKILL.md

## Provenance (videoIds)

bckxn4Jfkgk, IdugOOOOvwk, 5Fw4QFt1lts, wucftf8lH4A.
