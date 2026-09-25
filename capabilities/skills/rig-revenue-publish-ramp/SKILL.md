---
name: "rig-revenue-publish-ramp"
description: "Set and hold the publishing ramp: 1 to 5 to 10 items per week over time, never a velocity spike, with drafts-first human approval at every step. Use when the trigger is 'how much should we publish', 'publishing cadence', 'ramp up content', or before any batch publish."
---

# Publish ramp (one mechanism)

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Velocity spikes are spam signals — "don't go from one to
100 articles" (CLAIM: ntISy-GN7Gk). The corpus preaches ramping while pitching 100/day; we ship
the ramp only.

## Step 1. Set the ceiling

Cadence ladder: level 1 = 1 item/week → level 2 = 2-5/week → level 3 = 5-10/week. Raise one level
only after 3-4 clean weeks at the current level. For a new domain, start at level 1 — "new site
plus fast content equals Google assumes spam first asks later" (CLAIM: GBo1Qu82xYA).

## Step 2. Consistency over volume

A steady, sustainable cadence beats bursts. "Consistency does not mean posting daily" (CLAIM:
-UkHh5kbKEQ). Pick the cadence the firm's review capacity can sustain — the reviewing
professional's throughput IS the ceiling for YMYL firms.

## Step 3. Every item gated

Items flow drafts-first through rig-revenue-publish-gate. Batch publishes are human-approved
item-by-item or as a reviewed list — never blind auto-publish (excluded tactic). The same ramp
applies to GBP posts and social.

## Step 4. Hold the line

Pressure to spike (a campaign, a launch, a competitor) gets a scoping conversation, not a spike.
If capacity exceeds the ramp, bank approved items and schedule them along the ramp.

## done_when

- file:capabilities/skills/rig-revenue-publish-ramp/SKILL.md
- grep:capabilities/skills/rig-revenue-publish-ramp/SKILL.md:^## Step 1. Set the ceiling
- grep:capabilities/skills/rig-revenue-publish-ramp/SKILL.md:excluded tactic
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-publish-ramp/SKILL.md

## Provenance (videoIds)

ntISy-GN7Gk, -UkHh5kbKEQ, GBo1Qu82xYA, 2_Hlh4_UX5M, D8tVa_kalbg, kkwulmlubqw, DxhfqilU-7w.
