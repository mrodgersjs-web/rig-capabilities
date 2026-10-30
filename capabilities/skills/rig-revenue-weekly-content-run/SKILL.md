---
name: "rig-revenue-weekly-content-run"
description: "Run the weekly content production cycle for a client site: competitor-gap brief, forced-variable article production, silo linking, drafts-first publishing with a human approval gate, and RSS-derived social copy. Use when the trigger is 'weekly content run', 'this week's content', 'run the content engine', or a standing content cadence for a law/CPA/clinic/consulting firm."
done_when:
  - 'grep:capabilities/skills/rig-revenue-weekly-content-run/SKILL.md:[U]nreviewed YMYL claims do not ship'
  - 'grep:capabilities/skills/rig-revenue-weekly-content-run/SKILL.md:^## Step 3. Review gates'
---

# Weekly content run

## CRITICAL: Auto-start on load

When this skill triggers, go straight to Step 1. Do not summarise.

Governing contracts: rig-revenue-meta (claim hygiene, PAID ENDORSEMENT labels, risk register,
human publish gate). Every tool named below follows those contracts.

## Inputs

- Client facts: services, cities, buyer personas, credentials (verify before use — protected
  titles escalate per rig-revenue-meta), differentiators, own data/case material
- Baseline: sitemap, GSC access or export, competitor list (3-5)
- Prior run's batch log (dedupe against published topics)

## Outputs

- Brief pack: 3-7 article briefs (buyer-intent keywords, forced variables, gap labels per section)
- Draft articles with answer-first structure, silo internal links to money pages, FAQ block,
  named-expert review slots
- Social copy derived from the published RSS items (not invented topics)
- Batch log: what shipped, what awaits human approval, what was skipped and why

## Step 1. Refresh the gap brief

1. Re-read the competitor content map (rig-revenue-competitor-teardown supplies it cold).
2. Pull GSC queries with impressions for the site; flag clusters with impressions but weak
   coverage (rig-revenue-gsc-refresh mechanics).
3. Screen every candidate keyword through rig-revenue-buyer-intent-screen. "Where/how much/hire"
   terms first; DIY "how" terms only as deliberate top-of-funnel with a named purpose.
4. Output 3-7 briefs. Each brief: target query, search intent, forced variables (from client
   data), gap labels (what each section adds that page-1 results lack), money page to link to.

## Step 2. Produce with forced variables

1. Per brief run rig-revenue-forced-variables — inject the firm's own numbers, cases (approved),
   tests, and first-hand observations. No brief advances without at least one non-commodity
   variable.
2. Structure per rig-revenue-answer-first: question headings, 1-2 sentence standalone answers
   (link-free), detail below, FAQ block at the end.
3. Money pages: link each article to its service/money page and back (rig-revenue-silo-architecture).

## Step 3. Review gates (two, in order)

1. rig-revenue-seo-council: adversarial pass (intent, competitor, on-page, contrarian, searcher
   roles) → verdict + fixes. Fix before proceeding.
2. Professional review slot: YMYL claims, credentials, and any pricing/legal statements go to the
   licensed professional. Unreviewed YMYL claims do not ship. Ever.

## Step 4. Publish drafts-first

1. Land every article as a DRAFT. rig-revenue-publish-gate collects the human approval record.
2. Only approved items publish. On approval, run rig-revenue-publish-ramp — the batch sits inside
   the ramp ceiling; never spike.
3. Derive social copy from the published RSS items (one asset, many surfaces) — but the social
   posts are also drafts behind the same gate.

## Step 5. Log and hand off

Write the batch log (topics, variables used, gate records, links placed). Feed the log to
rig-revenue-monthly-report and to next week's Step 1 dedupe.

## Tools

- Client CMS / GSC / Analytics — neutral tooling (n)
- Any AI writer or generator mentioned in corpus-derived guidance (Arvow, Blotato, Journalist AI)
  — PAID ENDORSEMENT (source channel affiliate); use only on client-approved tooling decisions
- Claude/ChatGPT-class models for drafting — neutral tools; drafts are never published unreviewed

## done_when

- file:capabilities/skills/rig-revenue-weekly-content-run/SKILL.md
- grep:capabilities/skills/rig-revenue-weekly-content-run/SKILL.md:^## Step 3. Review gates
- grep:capabilities/skills/rig-revenue-weekly-content-run/SKILL.md:PAID ENDORSEMENT
- cmd:node /Users/rig128gb/.aside/u/0/skills/builtin/skill-creator/scripts/validate-frontmatter.mjs /Users/rig128gb/Developer/rig-capabilities/capabilities/skills/rig-revenue-weekly-content-run/SKILL.md

## Provenance (videoIds)

TzrFZs_zte4, dytgLiNELY4, ffn0NsYgOek, MjQYcQQxXJA, kkwulmlubqw, q0wr137QFEk, ozcRBQ0TVOs,
BAB4lqxBZ6Y, Hc2Q4BH4G6k, QeDQIcuglmw, DxhfqilU-7w, -UkHh5kbKEQ. All corpus figures are
unverified creator claims (CLAIM: per rig-revenue-meta).
