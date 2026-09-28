# ga-bidding: bidding strategies and the discipline around learning

## Laws

L1. Never move a campaign cold-turkey from any non-conversion bid strategy (manual CPC, max clicks, even plain max conversions) straight onto target CPA without testing it first; targets are introduced late and deliberately. CLAIM(lmkGyfbzZ_M, ifxob69AqEs, ZA1uCsYPjPU) | channels: 3 | status: consensus
> "to go cold turkey from manual bids, max conversions, anything uh even maximize conversions, anything that's not target CPA straight to target CPA is a bad idea" (lmkGyfbzZ_M, @paid-search-podcast)

L2. Conversion-based strategies need real conversion history to function; on an account with little history the algorithm is effectively guessing with the budget, so newer advertisers should run without a target or on click bidding first. CLAIM(ifxob69AqEs, -ch_R4WPxfw, w16T-VBCd_c) | channels: 3 | status: consensus
> "Those strategies need real conversion history to bid intelligently, without it, they're just guessing with your money" (ifxob69AqEs, @ben-heath)

L3. The corpus's working readiness check before switching from click bidding to conversion bidding is roughly 30 conversions in 30 days (an informal heuristic, never a scientific threshold), with about 50 conversions a month cited as the bar before trusting a target; below that, engaging smart bidding too early can starve the campaign of traffic. CLAIM(w16T-VBCd_c, IjqtInbHzk4, RXV8UkDld_A, 2U6svvKSHVA) | channels: 3 | status: consensus
> "And the first thing you want to be looking at is do you have at least 30 conversions in 30 days?" (w16T-VBCd_c, @aaron-young)

L4. Every bid-strategy switch, target change, or big structural edit (such as adding thousands of keywords at once) restarts the learning period, so each one is a disruptive event that resets the campaign's baseline. CLAIM(Q_fB7F-oBVs, DrIl_ykaG5k, 0KIY8kV2X6E, qSNol4PBYe0) | channels: 4 | status: consensus
> "when you do switch to maximize conversions, you're going to trigger a whole new learning period" (Q_fB7F-oBVs, @jyll-saskin-gales)

L5. Smart-bidding discipline is change restraint: change strategy or target rarely (the guidance is no more often than about 60 days apart), and wait it out when unsure rather than acting on impulse. CLAIM(NQCLCLR3NQU, w16T-VBCd_c, 0KIY8kV2X6E) | channels: 1 | status: single-source
> "the golden rule for smart bidding number two is that you don't want to be making any changes more than 60 days apart when it comes to smart bidding" (NQCLCLR3NQU, @aaron-young)

L6. A target set too tight acts as a brake: clicks, impressions and conversions fall and spend slips below budget; loosening the target buys volume, tightening it buys efficiency, and budget and target should be moved together deliberately. CLAIM(2U6svvKSHVA, qJewLxfnXHM, Z6__SrYuXjo) | channels: 2 | status: consensus
> "if we start to see the clicks and the impressions and the conversions dive, we know that that target CPA or that target ROAS is set too aggressively" (2U6svvKSHVA, @aaron-young)

L7. Max conversions with the target unchecked gives the algorithm no CPC guardrail, so on a data-less campaign with a lazy budget it will overbid; keep the budget tight until conversion data accumulates. CLAIM(5lt1rUDR6Ig, BmCaZI3JA3s) | channels: 2 | status: consensus
> "if you uncheck that and take that off and give Google max conversion bidding setting, the regulations on the CPC go out the window" (5lt1rUDR6Ig, @paid-search-podcast)

L8. Bid adjustments are ignored by the smart-bidding strategies (keyword targeting itself still applies), so under smart bidding they are wasted effort; they still take effect under manual CPC and max clicks. CLAIM(hbVWC6sXYTo, RCRPj2JmqCY, IKLR3z0dtgs) | channels: 3 | status: consensus
> "if you're utilizing some of the smart bid strategies bid adjustments don't do anything for those" (IKLR3z0dtgs, @growmyads)

L9. Smart bidding bids per query and per signal, so one keyword's close variants can get different bids, while manual bidding prices every variant the same — which is why the two approaches can deliver different traffic and conversion rates from an identical keyword. CLAIM(Q_fB7F-oBVs, TQ51h4ettNE, X9xCF5lCzuU) | channels: 2 | status: consensus
> "On manual bidding, you are treating all those variants exactly the same." (Q_fB7F-oBVs, @jyll-saskin-gales)

L10. Manual CPC and max clicks belong with exact and phrase match plus keyword-level control; broad match should wait until conversion volume is high enough to move over to smart bidding. CLAIM(v_71WbuyggI, BmCaZI3JA3s) | channels: 2 | status: consensus
> "broad match is not being used yet cuz broad match does not fit well at this stage" (v_71WbuyggI, @growmyads)

L11. Optimizing on a metric the account does not actually track is destructive: value-based and tROAS bidding require genuine conversion values (ideally fed back from the CRM), and only primary conversion actions are used by smart bidding. CLAIM(DrIl_ykaG5k, HTeUwUGRCus, jqhCN63n5o0, QQwRWqu3EYo) | channels: 4 | status: consensus
> "it could be absolutely a destructive thing to allow the Google ad system to change your bidding strategy your bidding performance on a metric that you do not account for in your account" (DrIl_ykaG5k, @paid-search-podcast)

L12. Learning lives at the bid-strategy level, so portfolio bid strategies pool conversion data across campaigns and reach usable volume faster than a strategy attached to a single campaign. CLAIM(X9xCF5lCzuU, 4uGrZIy7-GQ, JKGDSM9p6GA) | channels: 3 | status: consensus
> "bidding learns at the bid strategy level. So, like if a campaign has its own bid strategy, then that bidding learning is just there." (X9xCF5lCzuU, @jyll-saskin-gales)

L13. Manual CPC and max clicks are starting-out positions, not the destination: the mainstream path in this corpus is to begin click-bidding for control, then move to max conversions and only afterwards add a target, once volume proves the campaign out. CLAIM(uyXOzCXO5KY, BmCaZI3JA3s, ZA1uCsYPjPU, 8IowO33k8N8) | channels: 3 | status: consensus
> "I only recommend manual CPC or Max click bidding when you're just starting out not that's not the ultimate goal of bidding but only when you're starting out" (uyXOzCXO5KY, @growmyads)

## Contested

Start manual-first or start smart? @paid-search-podcast argues for a slow, manual-leaning path and treats smart bidding as a late-stage tool:
> "the best road forward is a slow and steady method. Um, so for that reason, I prefer manual bidding." (2hHxA9hzI2U, @paid-search-podcast)

while @jyll-saskin-gales says manual has almost no remaining use cases, and @ben-heath recommends starting straight on max conversions:
> "there are very, very few use cases for manual bidding in 2025" (iMyrQVNiTLQ, @jyll-saskin-gales)
> "So start with maximize conversions instead" (ifxob69AqEs, @ben-heath)

Are bid adjustments truly dead under smart bidding? @paid-search-podcast answers a listener with a flat no, but @jyll-saskin-gales and @growmyads describe target-adjustment behaviour that still does something under tCPA:
> "the bid adjustments do not matter on automated bidding" (hbVWC6sXYTo, @paid-search-podcast)
> "if you put in a device bid adjustment it adjusts your target CPA for that device" (X9xCF5lCzuU, @jyll-saskin-gales)
> "if you're running manual CPC bidding or even target CPA, a bid adjustment will actually do something for you" (ngNw8xJ8Rq8, @growmyads)

Brand campaigns: does smart bidding help or hurt? @growmyads reports CPC inflation with no incremental gain when brand terms are already near full impression share, while @jyll-saskin-gales reports the opposite swing moving from manual CPC to tROAS:
> "smart bidding Jacks my CPC up and I get zero additional lift in Impressions or clicks" (B27snHfuuW8, @growmyads)
> "search campaigns on exact match keywords do a complete 180 in performance just by switching from manual CPC to target rorowaz" (A-imIrb7DKI, @jyll-saskin-gales)

Set a target at all? @ben-heath and @paid-search-podcast prefer running max conversions with no target until results are consistent, while @solutions8 and @aaron-young treat a tCPA as a protective control that should be in place:
> "I would much rather most Google advertisers not set up a target CPA or a target ROAS" (1Gpk704s5XU, @ben-heath)
> "I'm running a larger percentage of those on Max conversions without a Target CPA" (RXV8UkDld_A, @paid-search-podcast)
> "we're using TCPA as like a control over here to mitigate it so it doesn't go crazy" (qSNol4PBYe0, @solutions8)

## Dated advice

- Enhanced CPC is discussed as being on the way out (IH2AieFzqNM, @paid-search-podcast, "Enhanced CPC is Going Away!" episode) and as a past-tense setup choice (O3QZLz21V3k, @surfsideppc, "I've used enhanced CPC in the past"). Enhanced CPC has since been removed from Google Ads entirely; any guidance that offers toggling it is obsolete. Manual CPC survives, but its UI location has moved (see Platform mechanics).
- The manual-vs-smart verdicts dated 2025 — iMyrQVNiTLQ (stated in-window as "in 2025") and B27snHfuuW8 (title: "in 2025") — predate the 2026-era options that appear elsewhere in this corpus (AI Max per uLl5vNj2pzA, journey aware bidding per 8Vjo2swEEOE, new-customer acquisition bidding per UN2HRw0jRFQ), so treat them as era-bound rather than current platform law.
- The July 2024 AMA window (IjqtInbHzk4, @growmyads) gives a "30 to 45 conversions" trigger for adding tCPA; later windows restate different numbers (e.g. 50 a month in 2U6svvKSHVA, @aaron-young). These creator thresholds are heuristics that shift over time, not platform rules.

## Creator result claims

- @paid-search-podcast reports a client's cost per acquisition falling from $50 under manual bidding to $35 after moving to max conversions with a tCPA target (K5DF8kBNvo8). UNVERIFIED
- @paid-search-podcast reports a client's CPCs spiking to roughly $10-$20 per click within days of removing the target from max conversions (5lt1rUDR6Ig). UNVERIFIED
- @solutions8 claims running max clicks alongside a high tCPA in parallel roughly doubled volume for 20% more spend and cut overall CPC by about 40% on a new campaign (2xgITKy8pYc). UNVERIFIED
- @solutions8 claims new customers rose 112% in the week after switching to tROAS, self-described as anecdotal for one use case (_iDnkCxIJKk). UNVERIFIED
- @optmyzr claims a portfolio-bid tactic of repeatedly challenging the algorithm for about 1% higher ROAS consistently improved return (QplC-zjbu_E). UNVERIFIED

## Platform mechanics

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
- Lead-gen conversion actions should count "one" per interaction rather than "every", and only primary goals feed smart bidding (HTeUwUGRCus, @aaron-young). re-verify in the live product
- The optimization-score recommendation to hand over to automated bidding promises a 15-20 point (or higher) score improvement (pVJPb9_fX_U, @paid-search-podcast). re-verify in the live product

## RIG application

- RIG's local B2B accounts run on calls and forms with small budgets, so clearing 30 conversions in 30 days is unlikely early on: stay on manual CPC or max clicks with exact match and aggressive negatives until volume proves itself; no tCPA/tROAS on day one.
- One bid-strategy or target change per roughly 60-day window, each one approved through Gate-D and logged, because every change restarts learning and wipes the prior baseline.
- Treat bid adjustments as no-ops under smart bidding — express device, geo and schedule preferences through negatives, audiences and campaign splits instead.
- Never run max conversions with no target on an unproven campaign; cap the daily budget first, since small budgets are exactly where the no-guardrail CPC blowup does its damage.
- Move to value-based bidding only once the CRM return path supplies real conversion values; until then optimize for conversions, not conversion value.
- Platform mechanics from this corpus go stale within a release cycle — every UI or policy claim above is re-verified live before RIG acts on it.
