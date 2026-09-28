---
name: ga-bidding
description: >-
  Bidding for Google Ads: manual vs smart bidding, the strategy ladder (max clicks, max conversions, tCPA, tROAS, portfolio), conversion-volume prerequisites, learning periods, bid adjustments and seasonality. USE WHEN choosing or changing a strategy, when CPA swings mid-month, or when someone wants to change bids daily. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, bidding]
outcome: "revenue-gtm: every campaign has a bidding strategy matched to its data volume and goal, with a change protocol that does not fight the learning system"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-bidding/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-bidding
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "13"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-bidding: bidding strategies and the discipline around learning

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: keep, cut or change this bid setting, is this spend justified. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check spend.continue --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `spend.continue` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after conversion tracking is proven and campaigns are built. Not for structure (ga-structure) or keyword selection (ga-keywords).

## Procedure

1. **Data first**: strategy choice follows conversion volume. Thin data (a few conversions/month) earns manual CPC or max clicks with a ceiling; consistent volume (~30+ conversions per month per campaign) earns tCPA; value-varied businesses with revenue data earn tROAS. Corpus consensus: conversion data is the fuel; smart bidding without it is guessing.
2. **Ladder up, never jump**: manual/clicks -> max conversions -> tCPA (at target or above current CPA) -> tROAS. Skipping rungs strands accounts in learning.
3. **Set targets at reality**: tCPA starts at or above the trailing actual CPA; an aspirational target strangles delivery. Raise targets only as results earn it.
4. **Learning-period discipline**: after any strategy/target/structure change, leave the campaign alone for ~1-2 weeks. Daily intervention restarts learning and manufactures volatility (corpus consensus).
5. **Bid adjustments** only where the system still allows them (device, location, time where supported); smart bidding absorbs most signals - adjust the inputs (budget, conversion quality, targets), not micro-bids.
6. **Portfolio strategies** when several campaigns share a goal and should share pacing.
7. **Jev**: any strategy change through `spend.continue` with the account evidence row; DEFERRED means no change.

## Checklist (before this stage is called done)

- [ ] Strategy per campaign matched to conversion volume
- [ ] Targets set at/above trailing actuals with basis shown
- [ ] Change protocol written (one variable, learning window)
- [ ] Portfolio vs individual strategy decided with reason
- [ ] Conversion tracking confirmed recording before any smart bidding
- [ ] Jev `spend.continue` run on each strategy change request

## Hands the next stage

`bidding-plan.md`: strategy per campaign with data-volume rationale, targets and their basis, change protocol. ga-budget uses the plan to set scaling rules.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-bidding.md` (local corpus, not republished).

- L1. Never move a campaign cold-turkey from any non-conversion bid strategy (manual CPC, max clicks, even plain max conversions) straight onto target CPA without testing it first; targets are introduced late and deliberately. CLAIM(lmkGyfbzZ_M, ifxob69AqEs, ZA1uCsYPjPU) | channels: 3 | status: consensus
- L2. Conversion-based strategies need real conversion history to function; on an account with little history the algorithm is effectively guessing with the budget, so newer advertisers should run without a target or on click bidding first. CLAIM(ifxob69AqEs, -ch_R4WPxfw, w16T-VBCd_c) | channels: 3 | status: consensus
- L3. The corpus's working readiness check before switching from click bidding to conversion bidding is roughly 30 conversions in 30 days (an informal heuristic, never a scientific threshold), with about 50 conversions a month cited as the bar before trusting a target; below that, engaging smart bidding too early can starve the campaign of traffic. CLAIM(w16T-VBCd_c, IjqtInbHzk4, RXV8UkDld_A, 2U6svvKSHVA) | channels: 3 | status: consensus
- L4. Every bid-strategy switch, target change, or big structural edit (such as adding thousands of keywords at once) restarts the learning period, so each one is a disruptive event that resets the campaign's baseline. CLAIM(Q_fB7F-oBVs, DrIl_ykaG5k, 0KIY8kV2X6E, qSNol4PBYe0) | channels: 4 | status: consensus
- L5. Smart-bidding discipline is change restraint: change strategy or target rarely (the guidance is no more often than about 60 days apart), and wait it out when unsure rather than acting on impulse. CLAIM(NQCLCLR3NQU, w16T-VBCd_c, 0KIY8kV2X6E) | channels: 1 | status: single-source
- L6. A target set too tight acts as a brake: clicks, impressions and conversions fall and spend slips below budget; loosening the target buys volume, tightening it buys efficiency, and budget and target should be moved together deliberately. CLAIM(2U6svvKSHVA, qJewLxfnXHM, Z6__SrYuXjo) | channels: 2 | status: consensus
- L7. Max conversions with the target unchecked gives the algorithm no CPC guardrail, so on a data-less campaign with a lazy budget it will overbid; keep the budget tight until conversion data accumulates. CLAIM(5lt1rUDR6Ig, BmCaZI3JA3s) | channels: 2 | status: consensus
- L8. Bid adjustments are ignored by the smart-bidding strategies (keyword targeting itself still applies), so under smart bidding they are wasted effort; they still take effect under manual CPC and max clicks. CLAIM(hbVWC6sXYTo, RCRPj2JmqCY, IKLR3z0dtgs) | channels: 3 | status: consensus
- L9. Smart bidding bids per query and per signal, so one keyword's close variants can get different bids, while manual bidding prices every variant the same — which is why the two approaches can deliver different traffic and conversion rates from an identical keyword. CLAIM(Q_fB7F-oBVs, TQ51h4ettNE, X9xCF5lCzuU) | channels: 2 | status: consensus
- L10. Manual CPC and max clicks belong with exact and phrase match plus keyword-level control; broad match should wait until conversion volume is high enough to move over to smart bidding. CLAIM(v_71WbuyggI, BmCaZI3JA3s) | channels: 2 | status: consensus
- L11. Optimizing on a metric the account does not actually track is destructive: value-based and tROAS bidding require genuine conversion values (ideally fed back from the CRM), and only primary conversion actions are used by smart bidding. CLAIM(DrIl_ykaG5k, HTeUwUGRCus, jqhCN63n5o0, QQwRWqu3EYo) | channels: 4 | status: consensus
- L12. Learning lives at the bid-strategy level, so portfolio bid strategies pool conversion data across campaigns and reach usable volume faster than a strategy attached to a single campaign. CLAIM(X9xCF5lCzuU, 4uGrZIy7-GQ, JKGDSM9p6GA) | channels: 3 | status: consensus
- L13. Manual CPC and max clicks are starting-out positions, not the destination: the mainstream path in this corpus is to begin click-bidding for control, then move to max conversions and only afterwards add a target, once volume proves the campaign out. CLAIM(uyXOzCXO5KY, BmCaZI3JA3s, ZA1uCsYPjPU, 8IowO33k8N8) | channels: 3 | status: consensus

## Where the creators disagree

Start manual-first or start smart? @paid-search-podcast argues for a slow, manual-leaning path and treats smart bidding as a late-stage tool:

while @jyll-saskin-gales says manual has almost no remaining use cases, and @ben-heath recommends starting straight on max conversions:

Are bid adjustments truly dead under smart bidding? @paid-search-podcast answers a listener with a flat no, but @jyll-saskin-gales and @growmyads describe target-adjustment behaviour that still does something under tCPA:

Brand campaigns: does smart bidding help or hurt? @growmyads reports CPC inflation with no incremental gain when brand terms are already near full impression share, while @jyll-saskin-gales reports the opposite swing moving from manual CPC to tROAS:

Set a target at all? @ben-heath and @paid-search-podcast prefer running max conversions with no target until results are consistent, while @solutions8 and @aaron-young treat a tCPA as a protective control that should be in place:

## Dated advice (platform mechanics change; re-verify before relying)

- Enhanced CPC is discussed as being on the way out (IH2AieFzqNM, @paid-search-podcast, [quote in corpus notes] episode) and as a past-tense setup choice (O3QZLz21V3k, @surfsideppc, [quote in corpus notes]). Enhanced CPC has since been removed from Google Ads entirely; any guidance that offers toggling it is obsolete. Manual CPC survives, but its UI location has moved (see Platform mechanics).
- The manual-vs-smart verdicts dated 2025 — iMyrQVNiTLQ (stated in-window as "in 2025[quote in corpus notes]in 2025") — predate the 2026-era options that appear elsewhere in this corpus (AI Max per uLl5vNj2pzA, journey aware bidding per 8Vjo2swEEOE, new-customer acquisition bidding per UN2HRw0jRFQ), so treat them as era-bound rather than current platform law.
- The July 2024 AMA window (IjqtInbHzk4, @growmyads) gives a [quote in corpus notes] trigger for adding tCPA; later windows restate different numbers (e.g. 50 a month in 2U6svvKSHVA, @aaron-young). These creator thresholds are heuristics that shift over time, not platform rules.

## Creator result claims (UNVERIFIED, never repeat as fact)

- @paid-search-podcast reports a client's cost per acquisition falling from $50 under manual bidding to $35 after moving to max conversions with a tCPA target (K5DF8kBNvo8). UNVERIFIED
- @paid-search-podcast reports a client's CPCs spiking to roughly $10-$20 per click within days of removing the target from max conversions (5lt1rUDR6Ig). UNVERIFIED
- @solutions8 claims running max clicks alongside a high tCPA in parallel roughly doubled volume for 20% more spend and cut overall CPC by about 40% on a new campaign (2xgITKy8pYc). UNVERIFIED
- @solutions8 claims new customers rose 112% in the week after switching to tROAS, self-described as anecdotal for one use case (_iDnkCxIJKk). UNVERIFIED
- @optmyzr claims a portfolio-bid tactic of repeatedly challenging the algorithm for about 1% higher ROAS consistently improved return (QplC-zjbu_E). UNVERIFIED

## Platform mechanics notes

- Manual CPC is de-emphasized in the campaign UI; you must bypass the recommendation and select the bid strategy directly to get back onto it (uyXOzCXO5KY, @growmyads). re-verify in the live product
- Enhanced CPC is gone while manual CPC remains as a fully manual island (IH2AieFzqNM, @paid-search-podcast; O3QZLz21V3k, @surfsideppc). re-verify in the live product
- Smart-bidding strategies ignore some settings including bid adjustments while keyword targeting is retained (RCRPj2JmqCY, @aaron-young). re-verify in the live product
- Under tCPA a device bid adjustment adjusts the target for that device, and a -100% device adjustment excludes the device under max clicks (X9xCF5lCzuU, @jyll-saskin-gales). re-verify in the live product
- Brand-new accounts are often not permitted to select tROAS because there is insufficient conversion data (-ch_R4WPxfw, @growmyads). re-verify in the live product
- Standard Shopping campaigns cannot use maximize conversions (Q_fB7F-oBVs, @jyll-saskin-gales). re-verify in the live product
- Target CPC exists for Demand Gen but not for search campaigns (iMyrQVNiTLQ, @jyll-saskin-gales). re-verify in the live product
- Journey aware bidding currently works only on search campaigns using target CPA (8Vjo2swEEOE, @jyll-saskin-gales). re-verify in the live product
- Portfolio bid strategies and shared budgets are created under Tools > Budgets and bidding (JKGDSM9p6GA, QQwRWqu3EYo, @surfsideppc). re-verify in the live product
- Campaign setup offers a custom acquisition option that adjusts bidding to gain new customers (NoNWbKzVBnU, UN2HRw0jRFQ, @ben-heath). re-verify in the live product
- Optimized targeting is only usable with conversion-based strategies: conversions, conversions value, tCPA, tROAS (-SYWDPiCDqk, @ben-heath). re-verify in the live product
- Lead-gen conversion actions should count "one[quote in corpus notes]every", and only primary goals feed smart bidding (HTeUwUGRCus, @aaron-young). re-verify in the live product
- The optimization-score recommendation to hand over to automated bidding promises a 15-20 point (or higher) score improvement (pVJPb9_fX_U, @paid-search-podcast). re-verify in the live product

## RIG application (RIG synthesis, not corpus claims)

- RIG's local B2B accounts run on calls and forms with small budgets, so clearing 30 conversions in 30 days is unlikely early on: stay on manual CPC or max clicks with exact match and aggressive negatives until volume proves itself; no tCPA/tROAS on day one.
- One bid-strategy or target change per roughly 60-day window, each one approved through Gate-D and logged, because every change restarts learning and wipes the prior baseline.
- Treat bid adjustments as no-ops under smart bidding — express device, geo and schedule preferences through negatives, audiences and campaign splits instead.
- Never run max conversions with no target on an unproven campaign; cap the daily budget first, since small budgets are exactly where the no-guardrail CPC blowup does its damage.
- Move to value-based bidding only once the CRM return path supplies real conversion values; until then optimize for conversions, not conversion value.
- Platform mechanics from this corpus go stale within a release cycle — every UI or policy claim above is re-verified live before RIG acts on it.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/bid-strategy-ladder.md` | choosing and moving up the bidding ladder |
| `references/learning-periods-and-changes.md` | the change protocol that stops fighting the learning system |

## Hard rules

- Never change strategy, targets and budget in the same week; one variable at a time or the learning data is garbage.
- Never chase daily CPA noise; read at the decision cadence (ga-reporting weekly, plan monthly).
- Bid changes that alter spend exposure are Gate-D.
- If conversions are not recording, the bidding conversation is postponed - fix ga-tracking first (corpus consensus).
- Dated manual-bid-era tactics are flagged as dated and not re-imported.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-bidding/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-bidding` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
