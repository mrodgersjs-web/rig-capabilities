---
name: "rig-revenue-new-client-sprint"
description: "Run the first 30 days for a new professional-service client: index/discovery fixes, local trust install, first governed content batch, review engine, and measurement setup — with publish-ramp discipline. Use when the trigger is 'first 30 days', 'new client onboarding', or 'kick off this firm'."
---

# New-client 30-day sprint

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta. Day 1-30 is foundations and proof, not volume. Publishing
starts day one at ramp level 1 (rig-revenue-publish-ramp); no spikes.

## Inputs

- Signed scope from rig-revenue-quote-scope (with exclusions), verified business facts and
  credentials, the named reviewing professional, GSC/GA/GBP access

## Outputs

- Day-by-day sprint plan with owners
- Week 1: retrievability fixed (indexation, sitemap, crawl settings) + baseline measurement
- Week 2: local trust installed (rig-revenue-local-visibility steps 1-3) + review engine live
- Week 3-4: first governed content batch (2-4 items at ramp level) + money-page fixes
- Day 30 report: what shipped, what moved, what's next (no outcome promises)

## Step 1. Days 1-3 — baseline and retrievability

1. Baseline snapshot: GSC/GA/GBP/AI-citation sample (rig-revenue-ai-citation-gaps Step 2 light).
2. Submit sitemap; request indexing for key pages; check AI-crawler blocking (Common Crawl class
   check — CLAIM: QBx3tEwwh98). Fix crawlability before writing anything.
3. Compliance intake: protected-title list, review-reply constraints (HIPAA/confidentiality),
   approved claims/data for forced variables.

## Step 2. Days 4-10 — local trust + money pages

1. Run rig-revenue-local-visibility Steps 1-3 (GBP protocol, NAP audit, review engine).
2. Money-page rebuild priority: the top 3 revenue services (rig-revenue-money-pages). Answer-first,
   pricing/where-to-start published if the firm approves (rig-revenue-meta rule 5).

## Step 3. Days 11-24 — first content batch + gaps

1. rig-revenue-weekly-content-run ×2 at ramp level 1-2. Forced variables from the firm's real
   cases; every YMYL item through the named professional.
2. Answer-first retrofit on 3-5 existing pages (rig-revenue-decay-refresh quick wins: rank 8-20
   queries first).

## Step 4. Days 25-30 — measure and plan

1. Early deltas: indexation status, review velocity, page-2 lifts, citation sample re-run.
2. 60-90 day plan: silo buildout order, authority sprint targets, next content cadence step.

## Step 5. Day 30 report

What shipped (with gate records), what moved (with numbers), what did not (honest), decisions
needed from the client. Corpus "30-day" outcome figures stay CLAIM — never quote them to the
client as expectations (e.g. CLAIM: I2JZaacF3Nw, PXThfLN-OHQ).

## done_when

- file:capabilities/skills/rig-revenue-new-client-sprint/SKILL.md
- grep:capabilities/skills/rig-revenue-new-client-sprint/SKILL.md:^## Step 1. Days 1-3
- grep:capabilities/skills/rig-revenue-new-client-sprint/SKILL.md:rig-revenue-publish-ramp
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-new-client-sprint/SKILL.md

## Provenance (videoIds)

I2JZaacF3Nw, ysu7_f0_7N8, PXThfLN-OHQ, 86bRah0t_Ko, 0l_weqm-GX4, Fy8YPDlOsdg, ntISy-GN7Gk,
QBx3tEwwh98. All corpus figures are unverified creator claims (CLAIM: per rig-revenue-meta).
