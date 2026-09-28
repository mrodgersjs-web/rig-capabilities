---
name: ga-strategy
description: >-
  Strategy for a Google Ads account: business goal, offer, target customer and geography, budget reality, the measurement plan and the pre-build audit. USE WHEN starting an account or a new motion, when spend is planned without a named conversion, or when Mike asks what the ads should be doing. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, strategy]
outcome: "revenue-gtm: the account leaves this stage with a named goal, a named conversion, an approved budget ceiling, and a written plan before any campaign exists"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-strategy/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-strategy
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-strategy: goals, offers and the measurement plan before any build

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: is the goal measurable, is the offer specific enough to buy, is this plan ready to execute. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check plan.readiness --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `plan.readiness` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use before the first campaign, before any budget decision, and whenever a new service or geography enters the account. Not for building campaigns (ga-structure, ga-campaigns) or writing ads (ga-ads).

## Procedure

1. **Name the business goal in money terms**: calls, booked estimates, signed deals - not impressions or clicks. State the value of one conversion so every later number has a denominator.
2. **Name the conversion actions** that prove the goal (call, form submit, purchase, booked meeting) and hand them to ga-tracking. No campaign is planned before these exist.
3. **Sharpen the offer**: what is being sold, to whom, at what entry point. A landing page and an ad both paraphrase this line (ga-landing, ga-ads).
4. **Set the budget ceiling as math**: monthly budget divided by realistic cost-per-lead, times lead-to-sale rate. If the arithmetic cannot plausibly buy one customer, the plan is not ready - say so instead of spending.
5. **Audit any existing account first** (change history, tracking state, disapprovals, past spend and results) before proposing anything new (sub-skill account-audit-first).
6. **Jev**: run the plan document through `plan.readiness`; fix the plan or record DEFERRED. DEFERRED blocks "ready to spend".
7. Hand the plan to ga-structure. Any spend or budget figure is Gate-D through Mike.

## Checklist (before this stage is called done)

- [ ] Goal and one conversion value named in money terms
- [ ] Conversion actions listed and handed to ga-tracking
- [ ] Offer line written in one sentence
- [ ] Budget ceiling math shown (budget / CPL / close rate)
- [ ] Existing account audited or explicitly new
- [ ] Jev `plan.readiness` run on the plan document; decision id recorded
- [ ] Spend and budget changes routed to Mike (Gate-D)

## Hands the next stage

`ads-plan.md`: goal, conversion actions, offer line, customer/geography, budget ceiling with arithmetic, audit findings. ga-structure designs the account from it; ga-tracking builds the conversions.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-strategy.md` (local corpus, not republished).

- L1. Pick exactly one primary goal for the account (revenue, ROAS, or cost per conversion) and manage for it; the bid strategy, not the campaign goal setting, is how that goal is actually communicated to Google. CLAIM(X9xCF5lCzuU, 6nIJkdJHtmc) | channels: 2 | status: consensus
- L2. State the governing constraint before anything else: a fixed budget to earn the most return within, or a target cost/return to hit first — maximize strategies encode the first, target strategies the second. CLAIM(0NUtkT9ulJM, iMyrQVNiTLQ) | channels: 2 | status: consensus
- L3. A goal must be realistic and grounded in unit economics — margin and researched CPCs — before launch, or the account is set up to fail regardless of tactics. CLAIM(WhaVp5efaFs, D6NEli3TwDU) | channels: 2 | status: consensus
- L4. The offer and the honesty of the ad copy are the first strategy levers, especially on a small budget: a sharper offer beats more spend, and clear copy pre-filters people who were never going to buy so they never click. CLAIM(3g_9oT1CrJE, 2U6svvKSHVA) | channels: 2 | status: consensus
- L5. Plan money monthly, not daily: the daily budget you type is multiplied by 30.4 to become the campaign's monthly spend, so the monthly number is the real planning unit. CLAIM(uKxPAHGmXpQ, JKGDSM9p6GA, 0KIY8kV2X6E) | channels: 3 | status: consensus
- L6. The average daily budget is not a per-day allowance: Google may spend up to twice it on a single day and up to 30.4 times it across the month, so campaign pacing must be judged on the monthly total. CLAIM(Aek3074JonM, uKxPAHGmXpQ) | channels: 2 | status: consensus
- L7. Whether a budget is "small" is a data question, not a dollar question: it depends on whether the spend is enough to gather usable conversion data in your niche, so define that threshold before planning. CLAIM(O0ujCXXkYmg, w_5b2tGUpxg) | channels: 2 | status: consensus
- L8. New campaigns should start at the lowest spend that still pulls conversion data into the account, then work up toward the target budget rather than launching at full spend. CLAIM(Lpggz_F6RRo, ZrPyI1FIESM) | channels: 2 | status: consensus
- L9. More spend is not a strategy: doubling budget can destabilize smart bidding, ROAS normally falls as spend rises, and the platform's "limited by budget" nudge exists partly to make you spend more. CLAIM(guosUGMayEk, 5M_qGNTw8ag, B-jRuc2RLZk) | channels: 3 | status: consensus
- L10. Treat a genuine limited-by-budget state as a deliberate decision, not a banner to ignore: either fund it or narrow what the budget is being asked to cover — fewer keywords, locations, or audiences. CLAIM(CdHzEz0j3GQ, B-jRuc2RLZk, e5hJwbHi_Ng) | channels: 3 | status: consensus
- L11. On a limited budget, do not fragment the money into tiny per-campaign budgets; pool it with shared budgets so campaigns can still bid at the decisive moment, while keeping bid targets under per-campaign control rather than sharing a portfolio bid. CLAIM(ycJzp9qws74) | channels: 1 | status: single-source
- L12. The measurement plan is part of the strategy: you must tell Google which conversions are real business outcomes (including offline conversions for lead gen) because the platform does not know your goal or your margins. CLAIM(lg9ixk2KOWQ, 8DgOX5aizyE, RBvD5Z0ucTk) | channels: 2 | status: consensus
- L13. Know what an audit is for before buying one: free, paid, and AI audits each answer different questions, and each has things it should not be trusted to answer. CLAIM(b_9QZZZyMlo) | channels: 1 | status: single-source
- L14. Expand targeting (new locations, broader audiences) only once the core targeting is easily spending its daily budget — use spare budget to widen, not the budget that feeds the proven areas. CLAIM(tbCCXR_qwWQ, PYp7d9elMkQ) | channels: 2 | status: consensus

## Where the creators disagree

Shared budgets: one source argues a limited budget should be pooled so campaigns don't run out at the hot moment — [quote in corpus notes] (ycJzp9qws74, @solutions8) — while another argues pooling backfires because [quote in corpus notes] (KGA35rQ_0fM, @optmyzr). Both hold: pool for breadth, but watch for starvation of specific campaigns.

What limited-by-budget means: one reading treats the red status as a platform growth nudge — [quote in corpus notes] (B-jRuc2RLZk, @growmyads) — while another points out that on maximize strategies it is simply normal operation: [quote in corpus notes] (CdHzEz0j3GQ, @jyll-saskin-gales). So the banner is actionable only on manual or target strategies.

New-campaign starting bid strategy: one episode is built on starting new campaigns on maximize conversions (title of Q_fB7F-oBVs, @jyll-saskin-gales), while another recommends applying a Target ROAS strategy to a brand-new search campaign — [quote in corpus notes] (QQwRWqu3EYo, @surfsideppc).

## Dated advice (platform mechanics change; re-verify before relying)

Budget-ramp advice tied to the 2025 holiday season: [quote in corpus notes] (mWPin1D7cLo, @aaron-young, [quote in corpus notes]) — the 20%-increment/3-to-6-weeks cadence is seasonal Black Friday play, not a year-round rule; re-check against the current season's dates before reuse.

Google Ads intro ad-credit offers ([quote in corpus notes] tiers, i3-Dvy4Wjb4, @ben-heath) are explicitly time- and country-variant: [quote in corpus notes] — treat the specific credit amounts as dated and re-check current offers.

Sizing budget increases from search impression share lost due to budget (e5hJwbHi_Ng, @paid-search-podcast, Ep 368) is era-limited: per Google documentation quoted later, [quote in corpus notes] (Q_fB7F-oBVs, @jyll-saskin-gales) — the sizing method only works on manual/target strategies, not maximize strategies.

## Creator result claims (UNVERIFIED, never repeat as fact)

[quote in corpus notes] (57dmkmi9vmE, @growmyads) UNVERIFIED

Client example scaled from $15,000/month to $46,000/month with a stated path toward $200,000/month (F3O5b7FFxDI, @aaron-young) UNVERIFIED

Standard shopping campaign [quote in corpus notes] after a strategy change; reported ROAS moved from 90% to about 75-77% while PMax started at 200% ROAS (u2jJH6wrbAY, @solutions8) UNVERIFIED

Account case where budget was raised 133% in July, 23% in August, and 10% in September while profit rose (i8nCc7Wls7Y, @solutions8) UNVERIFIED

## Platform mechanics notes

Average daily budget mechanics: daily spending limit is 2x the average daily budget, monthly limit is 30.4x (Aek3074JonM, @jyll-saskin-gales) — re-verify in the live product.

Campaign total budgets: [quote in corpus notes] (Aek3074JonM, @jyll-saskin-gales) — re-verify in the live product; this is a moving rollout.

Budgets are set at campaign level: [quote in corpus notes] (F3O5b7FFxDI, @aaron-young); shared budgets pool one daily budget across campaigns (ycJzp9qws74, @solutions8; JKGDSM9p6GA, @surfsideppc) — re-verify in the live product.

Bid-strategy learning status: [quote in corpus notes] (amlH9oNtS-M, @jyll-saskin-gales) — re-verify in the live product.

Maximize conversion value default target: per a conversation with Google reps, [quote in corpus notes] — the source itself adds [quote in corpus notes] (QQwRWqu3EYo, @surfsideppc) — re-verify in the live product.

Auto-apply recommendations can push lowering your target ROAS: [quote in corpus notes] (RBvD5Z0ucTk, @growmyads) — re-verify in the live product.

Third-party tooling (Optmyzr): budget control center, budget simulator showing projected KPI impact [quote in corpus notes] (eDCiBtuiohQ), portfolio-level KPI alerts (ZXdk908xdk0), and pausing a campaign group the moment its budget is hit (-eS9MLvlon0), all @optmyzr — re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

RIG locks one primary goal per account (qualified calls plus form leads) and a hard monthly cap in writing before any build; the cap is Gate-D approved and any raise is a new approval, never a reaction to a red banner.
Convert the monthly cap first, divide by 30.4 to get the daily number, and judge pacing on the monthly total — small local budgets die from daily whiplash, not from the monthly math.
Win the offer and the ad copy before spending: local B2B traffic is expensive and every non-fit click is pure loss, so the copy must disqualify tire-kickers on the SERP.
The measurement plan is call tracking plus form conversions plus offline CRM feedback of which leads actually closed, so tCPA optimizes toward booked qualified conversations instead of form spam.
Start at the minimum spend that collects real conversion data, ramp only with evidence (impression share, sustained limited-by-budget on a target strategy), and expand targeting only after the core geography is fully spent.
Audit against the written goal first — free/AI audit output is a hypothesis, not a verdict — and treat every creator result number in this corpus as marketing until reproduced in our own account.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/offer-and-goal-card.md` | writing the one-line offer and the goal card that every later stage cites |
| `references/account-audit-first.md` | auditing an existing account before proposing any change |

## Hard rules

- No budget number changes, campaign enablement or spend action ever happens without Mike's explicit approval (Gate-D). Sub-agents draft; the parent operator acts.
- Every number in the plan is a sourced receipt (account data, keyword planner range, client CRM figure) or is labelled as an assumption.
- A plan without a named conversion action is not a plan; it is a wish. Return it to step 2.
- Creator case-study numbers from the corpus are UNVERIFIED and never appear in a plan as expected results.
- Platform mechanics cited from the corpus are dated; re-verify in the live account before relying on them.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-strategy/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-strategy` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
