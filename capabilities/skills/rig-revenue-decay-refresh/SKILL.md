---
name: "rig-revenue-decay-refresh"
description: "Repair content decay and lift near-winners: GSC query-gap injection, rank 8-20 rewrite sweep, answer-first retrofit, title differentiation, and dated refreshes. Use when the trigger is 'page stuck on page 2', 'traffic decaying', 'refresh old content', or 'lift these rankings'."
done_when:
  - grep:capabilities/skills/rig-revenue-decay-refresh/SKILL.md:link or consolidate, never orphan
  - grep:capabilities/skills/rig-revenue-decay-refresh/SKILL.md:## Step 3. Rewrite .rank 8-20 stallers.
---

# Decay refresh and near-winner lift

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Fix what Google already understands before creating
anything new; the fastest wins are queries already ranking 3-20 (CLAIM: dinO9tdP6lU,
Hc2Q4BH4G6k).

## Inputs

- GSC export (queries + pages: clicks, impressions, CTR, position) for the last 3-6 months
- The pages themselves, their current titles/meta, and the firm's approved update material

## Outputs

- Prioritized worklist: page × action (refresh / rewrite / consolidate / retire)
- Updated pages with recorded changes (what changed, why, date)
- Re-measurement at 2-4 weeks and 8 weeks

## Step 1. Find the work

1. GSC: filter queries at average position 8-20 with impressions and buyer intent
   (rig-revenue-buyer-intent-screen). One row per page.
2. Query-gap scan: export a top page's query CSV; find keyword clusters with impressions the page
   doesn't cover (CLAIM: QeDQIcuglmw).
3. Decay scan: pages whose clicks have trended down across consecutive periods → refresh queue.

## Step 2. Refresh (light decay)

1. Update facts, figures, dates ("content decay is real and fixable" — CLAIM: ONPusps0wjk). Show
   the updated date only for substantial updates.
2. Add one new H2 at a time for uncovered query clusters — insertion point stated, then rewritten
   in the firm's voice with sourced data (rig-revenue-evidence rules in rig-revenue-meta).
3. Keep the silo links to money pages intact (rig-revenue-silo-architecture).

## Step 3. Rewrite (rank 8-20 stallers)

1. Answer-first retrofit: question headings, 1-2 sentence standalone answers, detail below
   (rig-revenue-answer-first).
2. Title differentiation if titles are near-duplicates across the site: keyword + benefit +
   brand (rig-revenue-title-differentiation). Distinctive titles are an indexing requirement.
3. Out-answer the result above: better, faster, more persuasive than both the competitor snippet
   and the AI summary above it.

## Step 4. Consolidate or retire

Thin/overlapping pages: merge into the strongest page with redirects; retire what can't be saved.
Unlinked pages decay fastest — link or consolidate, never orphan.

## Step 5. Measure and log

2-4 week and 8-week position/CTR deltas per page in the change log. No page-level promises; report
movement or non-movement honestly. Feed rig-revenue-monthly-report.

## done_when

- file:capabilities/skills/rig-revenue-decay-refresh/SKILL.md
- grep:capabilities/skills/rig-revenue-decay-refresh/SKILL.md:^## Step 3. Rewrite
- grep:capabilities/skills/rig-revenue-decay-refresh/SKILL.md:rig-revenue-answer-first
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-decay-refresh/SKILL.md

## Provenance (videoIds)

QeDQIcuglmw, dinO9tdP6lU, Hc2Q4BH4G6k, ONPusps0wjk, eRCK8qNxX1g, Fy8YPDlOsdg, xsB-oSb8YNE,
Fv7uVNn5oiI, IdugOOOOvwk. All corpus figures are unverified creator claims (CLAIM: per
rig-revenue-meta).
