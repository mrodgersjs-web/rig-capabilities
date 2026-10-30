---
name: "rig-revenue-gsc-refresh"
description: "Mine Google Search Console for cheap wins: query-gap H2 injection on top pages and average-position 3-20 near-winner sweeps. Use when the trigger is 'GSC has data', 'query gaps', 'low-hanging fruit', or 'we rank but underperform'."
done_when:
  - 'grep:capabilities/skills/rig-revenue-gsc-refresh/SKILL.md:^## Step 3. Near-winner sweep'
  - 'grep:capabilities/skills/rig-revenue-gsc-refresh/SKILL.md:^## Step 2. Query-gap H2 injection'
---

# GSC refresh (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. The fastest wins are queries you already rank for
(CLAIM: dinO9tdP6lU — the corpus calls its own position filter trick "gaming the system"; we use
the legitimate version: improve the page to deserve the position).

## Step 1. Export and slice

GSC Performance → full export (queries and pages tabs): clicks, impressions, CTR, average
position. Slice A: pages sorted by clicks. Slice B: queries at positions 3-20 with buyer intent.

## Step 2. Query-gap H2 injection (Slice A)

1. Pick the top page; export its queries CSV.
2. Find clusters with meaningful impressions the page doesn't cover (CLAIM: QeDQIcuglmw).
3. Add ONE new H2 at a time — insertion point stated, then a full section written with sourced
   material (rig-revenue-forced-variables), answer-first (rig-revenue-answer-first).
4. Substantial update → update the displayed date and the intro.

## Step 3. Near-winner sweep (Slice B)

Per query at 3-20: open its ranking page → forensic check (query in title/H1/first 100 words?
coverage vs top 5? internal links from siblings? meta? answer-first?) → apply the smallest fix
that addresses the gap (usually rig-revenue-decay-refresh Step 3).

## Step 4. Re-measure

2-4 week position/CTR deltas per query in the change log (rig-revenue-monthly-report). AI-mode
data appears under search type "web" and can't be filtered separately (CLAIM: wucftf8lH4A) —
report it with that caveat.

## done_when

- file:capabilities/skills/rig-revenue-gsc-refresh/SKILL.md
- grep:capabilities/skills/rig-revenue-gsc-refresh/SKILL.md:^## Step 2. Query-gap H2 injection
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-gsc-refresh/SKILL.md

## Provenance (videoIds)

QeDQIcuglmw, dinO9tdP6lU, Hc2Q4BH4G6k, Fy8YPDlOsdg, wucftf8lH4A, 0l_weqm-GX4.
