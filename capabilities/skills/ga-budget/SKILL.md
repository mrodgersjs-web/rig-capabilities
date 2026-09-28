---
name: ga-budget
description: >-
  Budget and testing for Google Ads: daily budget math, limited-by-budget reads, scaling rules, shared budgets, campaign experiments, and the review loop that keeps or cuts spend. USE WHEN setting or changing budgets, when scaling a working campaign, or when designing a test. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, budget]
outcome: "revenue-gtm: every budget has arithmetic behind it, every scale-up has a trigger, and every experiment has a pre-registered read and a kill criterion"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-budget/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-budget
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-budget: budget discipline, scaling and real experiments

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: keep, cut or change this spend, is this test worth running. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check spend.continue --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `spend.continue` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use whenever money is allocated or moved and before any experiment. Not for bid mechanics (ga-bidding) or creative (ga-ads).

## Procedure

1. **Budget as math**: monthly ceiling / 30.4 = daily; daily x expected CPC = expected clicks; clicks x conversion rate x close rate = expected deals. If the chain cannot plausibly reach one customer, the budget is a donation - fix the plan (ga-strategy) first.
2. **Limited-by-budget is information**: a campaign capped daily is telling you demand exceeds funding. Decide deliberately: raise budget (with the arithmetic), narrow targeting, or accept the cap - never ignore the flag.
3. **Scaling rules**: raise budgets in steps (corpus practice: ~10-20% at a time, wait out the learning window), only when CPA/ROAS beats target for a sustained window; one change at a time.
4. **Shared budgets** only for campaigns with one goal and one pacing need; never across brand and prospecting.
5. **Experiments are pre- drafts**: hypothesis, metric, minimum read window, sample-size reality check (small budgets can't reach significance - use directional reads and say so), kill criterion, and the exact decision rule before launch. Experiments run as Google Ads experiments/drafts where possible, not as live A/B chaos.
6. **Monthly spend review**: each campaign gets keep/cut/pause through Jev `spend.continue` on its evidence row; DEFERRED keeps last month's state and escalates.
7. Every budget move is Gate-D: Mike approves; the parent operator acts.

## Checklist (before this stage is called done)

- [ ] Daily/monthly figures with the arithmetic shown
- [ ] Limited-by-budget flags decided (raise / narrow / accept)
- [ ] Scaling steps and triggers written
- [ ] Shared budgets only within one goal
- [ ] Experiment register entries complete: hypothesis, metric, read window, kill criterion
- [ ] Monthly keep/cut review scheduled with Jev `spend.continue` rows
- [ ] All spend moves routed to Mike (Gate-D)

## Hands the next stage

`budget-plan.md`: per-campaign daily/monthly with arithmetic, scaling triggers and steps, experiment register with kill criteria. ga-reporting feeds the monthly review.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-budget.md` (local corpus, not republished).

- L1. Scaling in Google Ads has only two mechanisms — vertical (spend more where results are already best) and horizontal (broaden beyond exhausted high-intent reach); the rest is packaging. CLAIM(NKhRUqMXy3c, cNbHUS-r1Ec) | channels: 1 | status: single-source
- L2. Budget headroom must be proven with impression-share data: performance at or near goal plus low search impression share (especially impression share lost due to budget) means there is genuine room to spend more, and that is when budget gets raised or reallocated. CLAIM(uOoa066Ui4M, uZJ40rGgO4c, doalS2uxXdc) | channels: 2 | status: consensus
- L3. The limited-by-budget warning is good news when it appears: Google shows it only when the campaign is at or near its CPA/ROAS goal and impression share has been lost due to budget, and a campaign on a maximize strategy cannot show it at all. CLAIM(Aek3074JonM, 6_yTCeIFsYs) | channels: 1 | status: single-source
- L4. Impression share lost due to budget is only meaningful under manual and target bid strategies; under maximize strategies the column is incompatible because those campaigns are built to spend the full daily budget. CLAIM(Q_fB7F-oBVs, iMyrQVNiTLQ, 6_yTCeIFsYs) | channels: 1 | status: single-source
- L5. Budget and target CPA are the two volume dials: raising both is a volume play, lowering both is an efficiency play, and which moves first depends on which constraint is binding — limited by budget means move the budget, at goal with low impression share means move the target. CLAIM(qJewLxfnXHM, SkK1vwNrJyQ, uZJ40rGgO4c) | channels: 2 | status: consensus
- L6. The most common budget sin is misallocation: accounts pile the majority of spend onto campaigns they want to work while proven winners sit starved and limited by budget — move budget to what is actually converting. CLAIM(Oors-OKmg2Y, uOoa066Ui4M) | channels: 2 | status: consensus
- L7. Cost per conversion is algebra: it is driven by cost per click and conversion rate, so any CPA improvement has to come from moving click price or conversion rate, not from the target setting itself. CLAIM(suxl4IjPniQ) | channels: 1 | status: single-source
- L8. Set the target CPA from unit economics — what you can profitably afford per lead after factoring in lead-to-client rate and client value — not from whatever the platform suggests. CLAIM(FR4OsXrKJBs, Lpggz_F6RRo, a2qrHdu4vRM) | channels: 3 | status: consensus
- L9. Size the starting daily budget relative to the CPA goal instead of starting tiny: the cited guidance is a daily budget of at least about 10 times average cost per conversion (at minimum, enough to cover roughly one CPA per day), because a budget that buys only one or two clicks a day can never generate the data to judge. CLAIM(eS9jPqC2xY8, -7CdMDUh3bI) | channels: 2 | status: consensus
- L10. Don't install a target too early: wait until results are stable (about 50 conversions a month at campaign level is the cited base for tCPA/tROAS), because a target set before that acts as a brake that stops the campaign spending its budget. CLAIM(F3O5b7FFxDI, 2U6svvKSHVA, 1Gpk704s5XU, IKLR3z0dtgs, ZA1uCsYPjPU) | channels: 3 | status: consensus
- L11. Bidding and budget strategy changes (manual to automated, max clicks to tCPA, creative swaps) should run through Google's formal experiment tool as control versus test — not by swapping cold turkey or launching a duplicate campaign and hoping. CLAIM(kw2EEFjjzh8, rmZ4324SL3c, KSTNzbQzPBQ, C-vE6IR7IfI, mhDG82Mg1TU, YdWyP7IuG-0) | channels: 3 | status: consensus
- L12. A shared budget pools one daily amount across several campaigns as an alternative to setting a budget campaign by campaign. CLAIM(JKGDSM9p6GA, NG7xbNA5FP8) | channels: 2 | status: consensus
- L13. Impression share is a diagnostic, not a goal: use it to locate headroom, but higher impression share by itself does not mean better results. CLAIM(sq2N0NoFTRY) | channels: 1 | status: single-source
- L14. Automated scaling should move in small repeated increments and be judged on a recent lookback window, because stale all-time averages from cheaper early budget levels can justify overspending once the current cost per lead is already above target. CLAIM(4uGrZIy7-GQ, FR4OsXrKJBs, Y-w8ZFyS9ww) | channels: 2 | status: consensus

## Where the creators disagree

Formal experiment or just turn it on? @paid-search-podcast treats the formal experiment tool as the only safe route for a bid-strategy jump, while @jyll-saskin-gales says that for a small-budget account enabling AI Max and reading the search-terms report is enough:

Which lever first when limited by budget? @growmyads goes to the daily budget, @surfsideppc's default when you don't want to spend more is to drop the target:

Start on a target or not? @ben-heath wants no target until results are consistently coming in; @surfsideppc launches using Google's recommended target or slightly above it:

## Dated advice (platform mechanics change; re-verify before relying)

- @surfsideppc's [quote in corpus notes] window (Z6__SrYuXjo) is organized around a pre-rollout deadline — [quote in corpus notes] — so its checklist and its claims about how targets behave are tied to that specific 2026 platform change; whatever it advises must be re-checked against post-rollout behavior before use.
- @solutions8's hypersegmentation tactic (TUH53r8Wp0s, window carries no publication date) of running many single-product campaigns in one account that all enter the same auctions to earn multiple placements ([quote in corpus notes]) is era-bound: the corpus itself treats same-account duplicate serving as a problem to examine (sq2N0NoFTRY, @jyll-saskin-gales, [quote in corpus notes]), so this advice conflicts with the rest of the dossier and must be re-checked against current policy before replicating.
- Cost-level benchmarks quoted as context in BmCaZI3JA3s (@surfsideppc) — cost per conversion of $35 a few years earlier versus $80 in-window — are era-specific; budget math anchored on older CPC/CPL levels understates what today's auctions require.

## Creator result claims (UNVERIFIED, never repeat as fact)

- @ben-heath claims he has spent more than $20 million on Google Ads and scaled hundreds of campaigns (FR4OsXrKJBs). UNVERIFIED
- @solutions8 claims running a high tCPA alongside max clicks on a new campaign doubles volume for 20% more spend and drops overall CPC by about 40% (2xgITKy8pYc). UNVERIFIED
- @optmyzr claims gradual rule-engine pushes (about 1% at a time) delivered more than 600% ROAS against a 500% goal without conversion volume falling (4uGrZIy7-GQ). UNVERIFIED
- @solutions8 claims moving customers off Performance Max produced $359,000 in conversion value on $50,000 spend (a 6x MER) with in-app cost per conversion reduced by 70% and new customers unaffected (qfjooXNXVAQ). UNVERIFIED
- @solutions8's video title claims an 85% lead increase year-over-year for Cable Bullet with Google Ads (04zpePbZcvY). UNVERIFIED
- @solutions8 claims making $2,000 the previous day on a $50-a-day hypersegmented Standard Shopping setup (TUH53r8Wp0s). UNVERIFIED

## Platform mechanics notes

- The formal experiment tool sits under the campaigns/expansions area behind an experiments button, with a plus button to create a campaign experiment (C-vE6IR7IfI, @paid-search-podcast). re-verify in the live product
- Campaign experiments are built at campaign level with a control and a test, allow selecting up to two goals, auto-sync base-campaign changes to the trial campaign, and show up labeled at account level (C-vE6IR7IfI, YdWyP7IuG-0). re-verify in the live product
- Experiments run on search and Performance Max but not at product level in shopping (pkMH0xCrSVw, @solutions8). re-verify in the live product
- A daily budget is an average daily budget, not a maximum, and Google often recommends a very high daily budget at setup (z6hF9AlfXBM, @jyll-saskin-gales). re-verify in the live product
- Google recommends a starting daily budget of at least 10 times average cost per conversion (eS9jPqC2xY8, @ben-heath). re-verify in the live product
- Shared budgets pool one budget across multiple campaigns and can be created alongside portfolio bid strategies (JKGDSM9p6GA, NG7xbNA5FP8). re-verify in the live product
- Google's documentation states the impression-share-lost-due-to-budget column is incompatible with maximize bid strategies, which are designed to spend the full daily budget (Q_fB7F-oBVs, @jyll-saskin-gales). re-verify in the live product
- Smart bidding exploration requires a campaign that is not already limited by budget; a limited-by-budget campaign is told to just increase the budget first (fJjT5FZrxLc, @growmyads). re-verify in the live product
- Target impression share can bid specifically for top-of-page or absolute-top positions (sq2N0NoFTRY, @jyll-saskin-gales). re-verify in the live product
- A maximum bid limit can be set alongside a target CPA, and it can price the campaign out of valuable auctions (QQwRWqu3EYo, @surfsideppc). re-verify in the live product
- Google's auto-recommendations can silently rewrite a target CPA downward and cut volume as a result (DrIl_ykaG5k, @paid-search-podcast). re-verify in the live product
- The limited-by-budget warning is shown when at/near target with impression share lost due to budget; campaigns on maximize strategies can't be flagged limited by budget (Aek3074JonM, 6_yTCeIFsYs, @jyll-saskin-gales). re-verify in the live product

## RIG application (RIG synthesis, not corpus claims)

- RIG's local B2B accounts run small budgets against calls and forms, so treat limited-by-budget plus CPL at goal as the only green light for a budget raise: verify call/form tracking first, then raise in small steps through Gate-D; never raise while CPL is above goal.
- Size budgets to the CPA math: at a $150 CPL goal a $20/day budget is noise — consolidate into fewer campaigns or one shared budget instead of starving five campaigns.
- No tCPA/tROAS until roughly 50 conversions a month or a stable 30-day CPL; run manual CPC or max clicks with exact match and tight negatives until then (pair with the ga-bidding laws).
- Every bid/budget strategy change runs as a formal experiment or staged control-vs-test before the full-budget commit; Gate-D approval covers the spend increase itself.
- Budget reviews reallocate from "hope" campaigns to proven winners that are limited, judge scale-up against unit economics, and use impression share only as a headroom diagnostic — never as a target.
- When scaling by rule, evaluate on a recent window (last 7 days), never all-time, so early cheap results can't justify overspend.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/budget-limits-and-scaling.md` | reading budget caps and scaling without wrecking delivery |
| `references/experiment-playbook.md` | designing Google Ads experiments that can actually answer |

## Hard rules

- No spend action (enable, raise budget, extend flight) without Mike's explicit approval (Gate-D). Staging is free; spending is not.
- Never run a test without its written decision rule and kill criterion.
- Budget changes and bidding changes never ship the same week (one variable).
- With small budgets, honest reporting includes the sample-size limit; directional reads are labelled directional.
- Never let a flight reach its end date at $0 and report it as a test (prior skill lesson; live reads settle state, not intent).

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-budget/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-budget` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
