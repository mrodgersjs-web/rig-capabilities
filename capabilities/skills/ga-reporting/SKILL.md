---
name: ga-reporting
description: >-
  Reporting and optimization for Google Ads: the weekly cadence, search-term and asset reads, change-history forensics, attribution honesty, lead-quality feedback and flop diagnosis. USE WHEN running the weekly or monthly review, when numbers disagree with the CRM, or when a campaign underperforms. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, reporting]
outcome: "revenue-gtm: every report is a live read with a date, every optimization has a recorded reason, and every result claim survives the attribution honesty check"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-reporting/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-reporting
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "13"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-reporting: reporting, optimization cadence and honest reads

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: is this performance signal real, what caused this result. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check signal.performance --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `signal.performance` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use weekly (serving health + mining) and monthly (money decisions). Not for setting strategy (ga-strategy) or building tests (ga-budget).

## Procedure

1. **Weekly cadence** (one session, recorded): serving status and disapprovals; search terms mining (ga-keywords); ad and asset health; budgets/caps; conversions recording check. Same day fixes for anything blocking.
2. **Monthly money review**: spend, cost per qualified lead, lead quality from the CRM, by campaign. Each row gets keep/cut/pause via Jev `spend.continue` (ga-budget owns the decision, this stage owns the evidence).
3. **Live reads only**: numbers are read from the account (or the live dashboard) with the date stamped. Never copy a figure from an old report into a new one (prior skill lesson: written records disagreed; only the live read was right).
4. **Attribution honesty**: name the attribution model and window whenever comparing periods; a model change makes before/after comparisons dishonest until restated.
5. **Change history forensics**: when results move, the first suspect is the change log (including Google's own auto-applied changes). Correlate before theorising about the market.
6. **Flop diagnosis**: classify each miss (tracking, message match, offer, bid/data volume, competition, budget) through Jev `signal.performance`; DEFERRED goes to the human review list.
7. **Lead quality feedback loop**: closed-won/lost outcomes flow back to keyword and geo decisions (ga-local-b2b).

## Checklist (before this stage is called done)

- [ ] Weekly session done and logged with date
- [ ] Search-term mining completed with actions recorded
- [ ] Conversions recording verified live
- [ ] Monthly review rows prepared for Jev `spend.continue`
- [ ] Attribution model/window stated on every comparison
- [ ] Change history checked for every material swing
- [ ] Lead-quality feedback loop updated from the CRM

## Hands the next stage

`report-<week>.md` / `review-<month>.md`: live-read numbers with dates, fixes made, open items, decisions requested from Mike. ga-budget's monthly row depends on this evidence.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-reporting.md` (local corpus, not republished).

- L1. Work the search-terms report on a fixed weekly rhythm (twice a week for a brand-new campaign) instead of daily, and treat it as the place where nearly all the negatives you need are found — and, once volume exists, the source of queries worth adding as keywords. CLAIM(yzJc_pFwiLc, ggxbQ55LI1A, RCRPj2JmqCY, 8IowO33k8N8) | channels: 3 | status: consensus
- L2. Optimization tempo must be gated by data volume: in a campaign's first days there is too little click and conversion data to learn anything, so changes made faster than the data accumulates are guesswork rather than decisions. CLAIM(1c8IwLrWuDY, 8IowO33k8N8) | channels: 2 | status: consensus
- L3. Change history is the audit trail of an optimization routine: it is where you look — and where you can walk back — when a run of search-term pruning or bid edits went too far, which is one reason not to churn daily. CLAIM(RCRPj2JmqCY) | channels: 1 | status: single-source
- L4. Reporting runs on stacked cadences — daily monitoring of a headline metric, monthly client-facing reports, and an annual review whose job is to lift above day-to-day fluctuations and read seasonality and market context. CLAIM(JUN76t0iAdU, KhZTbq871DY, b-IVWSNVx9M) | channels: 2 | status: consensus
- L5. Decide on the primary economic metric — cost per conversion or return on ad spend. Every other metric (CTR, CPC, impression share) is diagnostic: useful for explaining why the primary moved, never the success score itself. CLAIM(LmUFgCe3bms, oHcX91DKAY4, Gjl3zi9HoNg) | channels: 2 | status: consensus
- L6. A ratio can improve while the business outcome shrinks: conversion rate or ROAS can double simply because volume collapsed, so read every rate alongside an absolute count — and know what a flattering ratio may be hiding, such as new-customer economics behind a strong PMax ROAS. CLAIM(QplC-zjbu_E, hHXYlxnDu44) | channels: 2 | status: consensus
- L7. Metrics are read in pairs: an extreme CTR paired with an extreme conversion rate in either direction is a red flag, and when a headline KPI moves you diagnose by tracing the underlying metrics that moved with it rather than reacting to the headline alone. CLAIM(VQF7GfwSnvU, HAqVhZDTpVY) | channels: 2 | status: consensus
- L8. Keep the routine review small and fixed: pick one reach metric (how much you got) and one efficiency metric (how well it converted) as the KPIs, and build the saved column set around those instead of watching hundreds of columns. CLAIM(1c8IwLrWuDY, uOoa066Ui4M, uZJ40rGgO4c) | channels: 2 | status: consensus
- L9. Cost per conversion decomposes into cost per click times conversion rate, so any CPA improvement has to come from cheaper clicks, better post-click conversion, or both — decompose the number into its two levers before choosing a change. CLAIM(uZJ40rGgO4c, suxl4IjPniQ, 2SjTOd-tS2I) | channels: 3 | status: consensus
- L10. There is no universal good CTR: benchmark it against the campaign type (search vs shopping vs branded), and treat an extreme CTR as a likely brand- or competitor-query click-mix warning rather than as a win. CLAIM(jKyJt4wcfjw, u-Uctl-VL-M, VZOOZGSmB3Y) | channels: 3 | status: consensus
- L11. Impression share is a headroom tool, not a score: only after conversion economics are proven do you read impression share — and its lost-to-budget vs lost-to-rank split — to decide whether more budget or better rank is the lever; before that, ignore it. CLAIM(Q6wDxDfyFSs, 4ntMYTYW99E, doalS2uxXdc) | channels: 3 | status: consensus
- L12. Base optimization decisions on conversions or conversion value, not on clicks or impressions: click-level wins are easy for the platform to hand you and do not imply the business outcome, and a clicks objective makes the system optimize literally for clicks. CLAIM(ty_v5P7TSzs, Enzbe0A_9iM, sUQi-ErCkTo, O3QZLz21V3k, 12WcVma-rSA) | channels: 3 | status: consensus
- L13. Dashboard numbers are model-dependent: attribution mode, lookback windows and platform counting rules (click-through vs view-through) change what a report says, so cost-per-acquisition figures from different platforms are not the same measurement and should not be compared as if they were. CLAIM(c9GlBFTOtMg, EUu22EoSn9c) | channels: 1 | status: single-source

## Where the creators disagree

Whether a higher CTR is always better. @aaron-young treats raising CTR as a standing goal (hLFYOS_lGOE):

@ben-heath describes deliberately lowering it to filter unqualified traffic, accepting the CTR drop as the price of better-qualified clicks (Kmm3XGbYkj8):

Whether ROAS is an acceptable primary goal. @ben-heath lists return on ad spend alongside cost per conversion as the decision metric (LmUFgCe3bms):

@solutions8 refuses ROAS as a client goal outright, arguing a great-looking PMax ROAS can hide weak new-customer acquisition that the platform cannot show you (hHXYlxnDu44):

What a new campaign's KPI should be. @growmyads says month one is only about click delivery volume (8IowO33k8N8):

@ben-heath warns that a clicks objective teaches the platform to deliver exactly clicks, regardless of downstream value (Enzbe0A_9iM):

The dossier is thin on one topic: nobody in these windows gives a single agreed reporting cadence for account-level review beyond the search-terms weekly rhythm and the daily/monthly/annual layering in L1/L4; there is no corpus consensus on a fixed [quote in corpus notes] number.

## Dated advice (platform mechanics change; re-verify before relying)

Click-era optimization: advice that treats clicks, CTR or CPC as the campaign objective belongs to the pre-smart-bidding era. The corpus dates the shift itself as a 10-to-15-year move from paying for clicks to paying for conversions (c1Caq920TSs, @surfsideppc, no date in title), and @ben-heath's sUQi-ErCkTo (no date in title) describes advertisers still running click optimization as having learned it in that earlier era and never updated. Any doctrine that scores a campaign on click volume or CPC alone is pre-conversion-bidding advice.

[quote in corpus notes]: pre-2025 PMax state. jQr_UYNIZ_E (@aaron-young, title dated 2026, discussing 2025 platform updates) says 2025 shipped channel reporting, asset-level data, search-term visibility and negative keywords for PMax, so older PMax-era guidance on reporting blind spots is stale.

Judging PMax ad assets by Google's Good/Low performance labels: pre-asset-metrics era. Kj8o7Yodu6c (@growmyads, no date in title) frames labels as the prior state that is being replaced by asset-level clicks, cost, impressions and conversion metrics, so advice to swap assets based only on the label is dated.

Pinned attribution recipes: EUu22EoSn9c (@solutions8, no date in title) states a specific Meta configuration (one-day lookback, click-attributed, first-click) chosen because the platform's own attribution definitions keep flipping. Any hard-coded lookback/click-vs-view recipe — on Meta or Google — should be treated as expiring advice and re-checked against current defaults rather than carried forward as doctrine.

## Creator result claims (UNVERIFIED, never repeat as fact)

@solutions8 reports a client month-over-month jump: ROAS up about 54% while cost stayed roughly flat (about 3% difference), CPC up about 25%, conversion rate up about 267% (2SjTOd-tS2I, @solutions8) UNVERIFIED

@surfsideppc reports a Performance Max asset group served [quote in corpus notes] at 16 clicks and $0.52 per click (ggxbQ55LI1A, @surfsideppc) UNVERIFIED

@solutions8 reports an email account with roughly an 8% click rate against a stated 1.2 floor (b-IVWSNVx9M, @solutions8) UNVERIFIED

@surfsideppc recounts an account where the first two clicks cost about $750 against a stated $400/day budget (JKGDSM9p6GA, @surfsideppc) UNVERIFIED

## Platform mechanics notes

The segment control in the campaigns view can break clicks out by click type, separating phone-number, sitelink and headline clicks (b3AJlS3AVtQ, @paid-search-podcast) — re-verify in the live product.

In that click-type breakout, image clicks are counted but still land on the ad headline, unlike phone or get-directions clicks, which makes the segment misleading if read naively (GfFRhp-mEz4, @paid-search-podcast) — re-verify in the live product.

Invalid clicks are filtered out of general reporting and not charged; refunds can be requested for invalid clicks Google missed (10dXPaNQbO8, @paid-search-podcast) — re-verify in the live product.

Search terms live under Insights and reports → search terms; PMax received search terms plus negative-keyword support in the 2025 updates (ggxbQ55LI1A @surfsideppc; jQr_UYNIZ_E @aaron-young) — re-verify in the live product.

PMax channel-level spend appears in the channel performance report under Insights and reports, while PMax placements come from Report Editor and show impressions only (BmQ706_9wlQ @aaron-young; edIEWldBkOw @jyll-saskin-gales) — re-verify in the live product.

Conversions-by-time and CPA-by-time columns are custom columns you must build yourself; impression share columns sit under the competitive metrics section of modify-columns (uOoa066Ui4M, 4ntMYTYW99E, @growmyads) — re-verify in the live product.

Quality Score is keyword-level and requires adding columns to the keyword report; expected CTR has no published pass/fail threshold (DPOqrGqX0Rs @jyll-saskin-gales; SFbHl80f9ds @paid-search-podcast) — re-verify in the live product.

Change history is reachable from the account, and a narrow date range (e.g. last 30 days) can hide earlier entries when you go looking for them (RCRPj2JmqCY, @aaron-young) — re-verify in the live product.

Even practitioners cannot fully reconcile search impression share with click share (qPoxNhB6Ia8, @solutions8), so treat the exact semantics of these competitive metrics as unsettled — re-verify in the live product.

Third-party (Optmyzr) mechanics in this dossier — annual PPC reports, portfolio-level KPI alerts, a daily-running primary account audit, in-report editing of audit findings — are tool features that ship monthly (JUN76t0iAdU, ZXdk908xdk0, eDCiBtuiohQ, @optmyzr) — re-verify in the live product.

On Gmail ads surfaces, impressions, engagements and clicks are three different counts, with engagement covering interactions inside the ad and click meaning navigation to the site (z6hF9AlfXBM, @jyll-saskin-gales) — re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

Fixed weekly search-terms sweep (twice weekly in month one), every negative and bid change written down against change history so a bad week is attributable — Gate-D before any bid or budget increase, so spend raises are typed approvals, not reflexes.
Keep the RIG dashboard to one reach KPI (qualified calls + form fills, logged server-side to our own call/form truth) and one efficiency KPI (cost per qualified lead); CPC, CTR and impression share only ever answer "why did it move".
On small budgets, ignore impression share until cost per qualified lead is proven; then use the lost-to-budget vs lost-to-rank split to decide whether a Gate-D budget raise is the actual lever.
Judge outcomes against our own call log and CRM, never platform ROAS alone — attribution models differ across platforms and periods, so pair every rate with an absolute count of qualified leads.
With roughly ten clicks a day, change one variable per data window and wait; resist the daily optimization churn the corpus warns produces no learning.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/weekly-optimization-cadence.md` | the one-hour weekly account session |
| `references/change-history-and-forensics.md` | reading the account's history before theorising |

## Hard rules

- Every reported number carries its source (account view, CRM, dashboard) and read date. A number without provenance does not ship.
- Never report intent as state: "we ran ads" claims must match account state (enabled, serving, spend).
- Result claims are classified (attributable? sample size?) before they enter any Mike-facing summary or client report.
- Optimization changes are recorded the same session with reasons; unrecorded changes make forensics impossible.
- Auto-applied recommendations are reviewed, not blindly accepted; note which are on.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-reporting/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-reporting` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
