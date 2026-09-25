---
name: "rig-revenue-title-differentiation"
description: "Fix duplicate/generic titles so each page is distinct to crawlers and clickers: keyword + benefit/value proposition + brand, verified against the site's own title set. Use when the trigger is 'titles are too similar', 'crawled but not indexed', 'title rewrite', or 'title tags audit'."
---

# Title differentiation (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. The corpus's most-cited cause of "crawled - currently not
indexed" is title sameness — Google won't index "a library of the same exact book" (CLAIM:
eRCK8qNxX1g).

## Step 1. Audit the title set

List every indexable page's title. Flag: near-duplicates across pages, truncated rewrites in the
SERP, titles missing the brand, titles that don't name the benefit.

## Step 2. The formula

keyword + benefit/value proposition + brand ("HVAC repair, 24/7 emergency services, [firm]").
Long titles (150-229 chars) can win impressions where all competitors look identical — but keyword
stuffing backfires hard (CLAIM: N7M-T2yNOj4); the default stays natural and readable, expanded
only when the category is title-identical.

## Step 3. Verify before shipping

1. Each new title is unique against the whole site set (that's the point).
2. It matches the page's real content and intent (misleading titles = the excluded
   promise-then-redirect pattern).
3. 5-7 grade reading where the brand voice allows; brand names appear in liftable snippets
   (rig-revenue-ai-overview-mirror Step 4).

## done_when

- file:capabilities/skills/rig-revenue-title-differentiation/SKILL.md
- grep:capabilities/skills/rig-revenue-title-differentiation/SKILL.md:^## Step 2. The formula
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-title-differentiation/SKILL.md

## Provenance (videoIds)

eRCK8qNxX1g, N7M-T2yNOj4, xkIqItBwGJA (promise-then-redirect risk), IdugOOOOvwk.
