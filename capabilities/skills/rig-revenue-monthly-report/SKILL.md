---
name: "rig-revenue-monthly-report"
description: "Produce the governed monthly results report: measured visibility, AI-citation share, local pack and review deltas, content shipped with gate records, leads and funnel math, plus next-month plan. Use when the trigger is 'monthly report', 'reporting', 'what moved', or 'client results review'."
---

# Monthly results report

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. This report is the trust artifact: every number measured in
named tools with the measurement window stated. Corpus figures never appear as client results.

## Inputs

- Prior report (for deltas), batch logs from rig-revenue-weekly-content-run, gate records from
  rig-revenue-publish-gate, GSC/GA/GBP exports, AI-citation sample results, lead records

## Outputs

- One report: measured deltas, gate/quality record, honest non-movements, next-month plan
- Evidence appendix: tool + window + query set for every metric

## Step 1. Measure (never estimate)

1. Search: clicks, impressions, CTR, average position — window vs prior window, named query sets.
2. AI citations: the fixed prompt inventory from rig-revenue-ai-citation-gaps, re-run per model;
   report cited/not-cited per prompt and the delta.
3. Local: GBP actions (views, calls, direction requests where available), review count/score
   deltas, NAP fixes landed.
4. Content: items shipped (with gate records), items rejected in review and why.
5. Leads: sources, magnets, conversion steps that actually fired.

## Step 2. Report the gate as a deliverable

The human-approval and professional-review records ARE the compliance story — show counts (items
reviewed, changes requested, blocked claims). A month with 6 items shipped and 3 claims blocked is
a strong report, not a weak one.

## Step 3. Honest non-movement

Name what did not move and the current hypothesis. Never round up, never project history forward,
never attribute movement to RIG work without a plausible mechanism (updates happen — note them).

## Step 4. Next-month plan

Carry the open gaps (citation, decay, silo) as a ranked queue with the ramp step for next content
batch. Decisions needed from the client listed explicitly.

## done_when

- file:capabilities/skills/rig-revenue-monthly-report/SKILL.md
- grep:capabilities/skills/rig-revenue-monthly-report/SKILL.md:^## Step 3. Honest non-movement
- grep:capabilities/skills/rig-revenue-monthly-report/SKILL.md:gate
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-monthly-report/SKILL.md

## Provenance (videoIds)

oyc-XSLRbBE, vb9SMtUiAIw, dinO9tdP6lU, QeDQIcuglmw, ngoPSceYTUU, TrbM_vzts4o, guRTdN__2_c,
TKwYHHpaPBI (report presentation), 2Whv02wqoVY (GBP monitoring routine). All corpus figures are
unverified creator claims (CLAIM: per rig-revenue-meta).
