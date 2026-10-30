---
name: "rig-revenue-competitor-teardown"
description: "Reverse-engineer a niche or a named competitor's search strategy from public data — ranking pages, content clusters, keyword gaps, link sources — and produce a counter-strategy plan. Use when the trigger is 'entering this niche', 'losing to competitor X', 'why do they outrank us', or 'steal their strategy' (public data only)."
done_when:
  - grep:capabilities/skills/rig-revenue-competitor-teardown/SKILL.md:never copy link schemes
  - grep:capabilities/skills/rig-revenue-competitor-teardown/SKILL.md:## Step 1. Gather \(public only\)
---

# Competitor teardown

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Public data only — sitemaps, published pages, public link
indexes. "Replicate the strategy, not just content" (CLAIM: D8tVa_kalbg). Copying a competitor's
copy is refused (rig-revenue-forced-variables makes output non-commodity instead).

## Inputs

- Market/area, the firm's services and personas, 3-5 named competitors (or the top ranking
  results for the head terms)

## Outputs

- Competitor content map: page types, clusters, what pulls their traffic, what they publish and
  how often
- Keyword/gap matrix: shared terms, gaps nobody answers, buyer-intent terms owned by competitors
- Link-source list (where their authority comes from — feeding rig-revenue-authority-outreach)
- Counter-plan: what to build, in what order, with which forced variables

## Step 1. Gather (public only)

1. Competitor blog sitemaps (sitemap_index.xml) → full URL inventory.
2. Public backlink index for each competitor: which sources link to them and why.
3. Live SERPs + AI-answer surfaces for the head buyer prompts: who is cited, in what format.

## Step 2. Analyze

1. Cluster their URLs into page types (money, comparison, location, question/FAQ, editorial).
   The page type is the reusable insight (CLAIM: ffn0NsYgOek).
2. Rank clusters by buyer intent (rig-revenue-buyer-intent-screen), not by raw traffic.
3. Gap matrix: questions nobody answers well ("niche understanding questions that competitors are
   not answering could be gold" — CLAIM: 5it1VVQjya0).
4. Note their format per query (video? calculator? comparison table?) — match content format to
   what actually surfaces (CLAIM: drbVubTciUw).

## Step 3. Counter-plan

1. Counter with BETTER pages carrying the firm's forced variables and named expertise — never
   spun or near-duplicate copies (doorway/spam risk + it is the excluded commodity path).
2. Order: buyer-intent gaps first, then money-page rebuilds (rig-revenue-money-pages), then
   answer/citation gaps (rig-revenue-ai-citation-gaps).
3. Their link sources become the target list for rig-revenue-authority-outreach (earn the same
   links legitimately — never copy link schemes found in their profile; flag those as risks).

## Step 4. Report

One teardown report per engagement: map, gaps, counter-plan, risks spotted in the competitor's own
profile (negative SEO exposure, spam patterns — useful defensively). Log it for
rig-revenue-monthly-report deltas.

## done_when

- file:capabilities/skills/rig-revenue-competitor-teardown/SKILL.md
- grep:capabilities/skills/rig-revenue-competitor-teardown/SKILL.md:^## Step 2. Analyze
- grep:capabilities/skills/rig-revenue-competitor-teardown/SKILL.md:public
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-competitor-teardown/SKILL.md

## Provenance (videoIds)

ffn0NsYgOek, FECWlT10t80, 88LK9zduAIs, qQa_I3d-CH4, hTNku0myOU0, MjQYcQQxXJA, lTcwNdoTdUk,
drbVubTciUw, 5it1VVQjya0, D8tVa_kalbg. All corpus figures are unverified creator claims (CLAIM:
per rig-revenue-meta).
