---
name: ga-keywords
description: >-
  Keyword research and the negative keyword system: theme selection, match-type strategy in the keyword-signal era, negative lists, search-term mining, and brand/competitor term policy. USE WHEN building themes, when search terms drift off-offer, or when someone proposes match-type surgery as the fix. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, keywords]
outcome: "revenue-gtm: themes selected from real query language, a negative system that runs before spend, and a mining cadence that keeps it true"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-keywords/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-keywords
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-keywords: keywords as signals and the negative system that stays in control

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: is this theme sound, is this negative justified, which keyword option wins. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check idea.solid --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `idea.solid` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after ga-structure sets themes and before ga-campaigns fills them. Not for bidding (ga-bidding) or ad copy (ga-ads).

## Procedure

1. **Research from real language**: keyword planner volumes plus the actual query phrasing customers use (sales calls, site search, support tickets). Theme names come from the customer's words, not internal jargon.
2. **Match types are signals**: exact/phrase/broad select how far Google may stretch the meaning. Broad is defensible where negatives and multiple themed keywords per group exist; broad without negative discipline is how small budgets burn (corpus consensus).
3. **Build the negative system BEFORE spend**: account-level and campaign-level negative lists for off-offer services, jobs, free/DIY intent, geographies never served, and internal terms. The list is the control surface now.
4. **Search term mining cadence**: weekly read of the search terms report (ga-reporting); new negatives added the same session; new theme candidates logged for ga-structure rather than dumped into live ad groups.
5. **Brand policy**: brand terms in their own campaign (ga-structure); competitor terms only with a written decision on cost and message honesty.
6. **Jev**: theme and negative additions through `idea.solid` when they change serving; DEFERRED means the change waits.

## Checklist (before this stage is called done)

- [ ] Themes named in customer language with sample queries
- [ ] Match approach stated per theme, with negatives as the control story
- [ ] Account-level and campaign-level negative lists built before launch
- [ ] Brand policy documented (own campaign)
- [ ] Competitor-term policy documented or terms excluded
- [ ] Weekly search-term mining cadence on the calendar
- [ ] Jev `idea.solid` run on serving-changing additions

## Hands the next stage

`keyword-map.md`: themes with sample queries and match approach; negative lists by level; brand/competitor policy; mining cadence. ga-campaigns and ga-ads consume the themes.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-keywords.md` (local corpus, not republished).

- L1. Negative keyword match types work literally, unlike positive keywords whose meanings have drifted: a broad negative blocks any query containing each word you entered, a phrase negative blocks the contiguous phrase, and an exact negative blocks only that exact query. CLAIM(ggxbQ55LI1A, HvxLB3w7Sb8, 9oF65LaxWCQ) | channels: 3 | status: consensus
- L2. Reserve broad negatives for single words: a one-word broad negative sweeps an entire category of irrelevant queries, while a multi-word broad negative excludes each of its words independently and can silently remove unrelated future searches. CLAIM(lbROeogoN3g, 2hHxA9hzI2U, b3AJlS3AVtQ) | channels: 2 | status: consensus
- L3. Hold terms you never want to buy in an account-level negative keyword list and apply that one list across campaigns, instead of re-entering the same negatives campaign by campaign. CLAIM(ggxbQ55LI1A, 5vG9ma30Vr0, 2SjTOd-tS2I) | channels: 3 | status: consensus
- L4. Separate brand from non-brand: keep brand terms on a negative list inside non-brand campaigns so brand queries funnel into the brand campaign instead of spending non-brand budget. CLAIM(HvxLB3w7Sb8, 4uGrZIy7-GQ) | channels: 2 | status: consensus
- L5. Keyword research is also negative research: while selecting keywords, explicitly collect the searches and phrases you do not want to pay for. CLAIM(6JI0fjrV1Io, LkM4kqidwu4) | channels: 1 | status: single-source
- L6. Launch tight: start a new campaign on exact or phrase keywords plus a batch of negatives you already know are wasted, then open up only after real search data shows what converts. CLAIM(Wj4af7IwRFI, ARR-wcgFC1s, gsc83TyoUtQ) | channels: 3 | status: consensus
- L7. Treat match types as a risk ladder rather than a guarantee: exact match now matches meaning instead of the literal query, so even exact campaigns will serve on close variations. CLAIM(mQpfjvJHp8A, fWp50oOJmVA, pfB5ZdZKZzg, NxLPIA8Av6U) | channels: 4 | status: consensus
- L8. Keywords are added as broad match by default: unless you set the match type yourself, the platform starts you on the loosest setting. CLAIM(JBQXOv-f2qQ, U1pa1Pyf5_g, ZM5PkgMKbM8) | channels: 2 | status: consensus
- L9. Small budgets and beginners should start with a handful of exact-match keywords: broad match needs enough budget and conversion volume before the system can learn which queries are right. CLAIM(Tg1v9bO6lp0, 16X5a0Ii7kg, d-t96YZuYTw) | channels: 3 | status: consensus
- L10. After launch, ongoing keyword research moves from the planner to your own search-terms report: harvest both new keyword ideas and new negatives from the queries actually triggering ads, and negate your own keywords that burned budget with nothing to show. CLAIM(LkM4kqidwu4, 5vG9ma30Vr0, 2SjTOd-tS2I) | channels: 3 | status: consensus
- L11. Use negatives to stop funnel layers from bidding against each other: exclude the category term in mid-funnel campaigns so the exact-match bottom-of-funnel campaigns own those queries. CLAIM(ycJzp9qws74) | channels: 1 | status: single-source
- L12. A brand campaign needs very few keywords, often a single broad keyword when the brand name is distinctive, because the audience is already searching for you. CLAIM(NTdQpENDQ7g) | channels: 1 | status: single-source
- L13. Broad match is targeted by more than the keyword: it reads the landing page and the other keywords in the same ad group, so page and ad-group composition decide what it pulls in. CLAIM(3ok2qX3Iock, IWfM94UfA4o) | channels: 2 | status: consensus
- L14. When irrelevant queries appear, fix the root cause first, the wrong keyword or the wrong match type, before liberally negating; and review the search terms report on a set cadence. CLAIM(Tg1v9bO6lp0) | channels: 1 | status: single-source

## Where the creators disagree

Phrase match's standing splits three ways. One camp has abandoned it outright (PDmyFNEMyX0, @aaron-young):


Echoed twice from the Optmyzr side, which reads phrase match as declining and sees only two match types that matter anymore (-EI4g8CnsLY, @optmyzr; QplC-zjbu_E, @optmyzr):



Another camp still leads with phrase match (O3QZLz21V3k, @surfsideppc; 5vJqah8IZTg, @paid-search-podcast):



Starting match type is therefore disputed: exact-first (Wj4af7IwRFI, @surfsideppc; ARR-wcgFC1s, @aaron-young) versus phrase-first (5vJqah8IZTg, @paid-search-podcast).

Broad match posture is disputed. Pro side (ohXNz-iiAnk, @growmyads; h7xOSw1i7Jw, @aaron-young):



Con side (d-t96YZuYTw, @ben-heath), with the small-budget caution argued separately in Tg1v9bO6lp0 (@jyll-saskin-gales):


How clean a search-terms report should be is disputed. For broad match, cleanliness is explicitly not the aim (amlH9oNtS-M, @jyll-saskin-gales), while the deliberate-over-tightening side favors erring heavy and reopening later (gsc83TyoUtQ, @ben-heath):



Competitor-term doctrine is thin in this dossier: only two windows touch it, treating a competitor name as a single-word broad negative (lbROeogoN3g, @solutions8) and observing competitor queries arriving inside a brand campaign as versus searches (LkM4kqidwu4, @jyll-saskin-gales). No corpus consensus on bidding versus negating competitor terms.

## Dated advice (platform mechanics change; re-verify before relying)

Set-per-match-type ad groups, the old structure of one exact, one phrase and one broad ad group holding the same keywords, is named in that video as no longer working after Google moved to meaning-based matching; video date context: undated in dossier, describes a pre-meaning-matching era (nvEZo_P_p1Q, @ben-heath):



Broad match modifier is retired syntax; the creator now runs only exact and broad. Video date context: titled Outdated Google Ads Strategies (NxLPIA8Av6U, @aaron-young):


Match-type definitions taught earlier in the podcast's run no longer hold; the speaker contrasts a precise definition from roughly five years prior with current meaning-based behavior. Video date context: Episode #374, undated in dossier (8Cn6AR2n4-s, @paid-search-podcast):


The blanket historical rule against broad match is explicitly framed as history by this tutorial, which now recommends exact plus broad. Video date context: titled Updated for 2026 (h7xOSw1i7Jw, @aaron-young):

## Creator result claims (UNVERIFIED, never repeat as fact)

@aaron-young reports exact-match clicks running over $11 while broad match ran at $6.50 in the account shown (OtGKmt5pbys). UNVERIFIED

@paid-search-podcast reports 525 negative keywords, most one-word broad match, plus 172 phrase match keywords in his own successful campaign (2hHxA9hzI2U). UNVERIFIED

@solutions8 reports adding 400 negative keywords around day four of a negative-keyword push on a segmented shopping account (TUH53r8Wp0s). UNVERIFIED

@jyll-saskin-gales reports taking a client down to 18 exact-match keywords as part of a $20/day strategy (6JI0fjrV1Io). UNVERIFIED

## Platform mechanics notes

Broad match is the default match type assigned when a keyword is added without one (JBQXOv-f2qQ, @paid-search-podcast; U1pa1Pyf5_g, @ben-heath). re-verify in the live product

A negative added from the search-terms report defaults to the entire term as an exact match negative (5vG9ma30Vr0, @ben-heath). re-verify in the live product

The search-terms report shows a match-type column including phrase-match and exact-match close variants (eNcwcrVogxc, @paid-search-podcast). re-verify in the live product

Google withholds some queries as hidden other search terms and shows fewer search terms over time (amlH9oNtS-M, @jyll-saskin-gales; 2736aI4wjM4, @aaron-young). re-verify in the live product

Native automated rules cannot both analyze search queries and add negatives after review; scripts or third-party tooling are required (XUSG4eEyY6A, @optmyzr). re-verify in the live product

Broad match keywords are required for ads to appear within AI overviews, with exact match prioritized above or below them (5GkO2fzQYxk, @jyll-saskin-gales; zJ1kD9bHBUo, @jyll-saskin-gales). re-verify in the live product

Keyword prioritization puts an exactly matching search keyword ahead of a Performance Max search theme in theory (Ko-uIvLXntM, @jyll-saskin-gales). re-verify in the live product

Turning on AI Max surfaces a warning that you should not run broad match alongside it (rcTtEhzTIk4, @aaron-young). re-verify in the live product

Shopping and Performance Max campaigns accept only negative keywords, never positive keywords (lbROeogoN3g, @solutions8). re-verify in the live product

Google reps have recommended deleting exact-match duplicates of phrase keywords as redundant (1MRDIlKuLrQ, @paid-search-podcast). re-verify in the live product

## RIG application (RIG synthesis, not corpus claims)

RIG runs small budgets against local B2B intent, so L9 and L6 are the default posture: a dozen exact-match service keywords, calls-and-forms tracking proven first, and a starter batch of negatives before the first click spends.

One account-level negative list (L3) carries the never-buy vocabulary for every campaign, brand terms (L4) are negated out of service campaigns so mikerodgers.tech searches land in a brand campaign, and competitor names follow the single-word broad rule (L2) as a deliberate RIG decision, not a default.

Search-term mining (L10, L14) is cheap at RIG's spend level: a weekly pass promotes converting queries to exact match and fixes the root cause, wrong keyword or match type, before adding a negative.

Broad match (L13) stays off until conversion volume and tracking truth justify it, since Gate-D governs spend and an unproven broad campaign is money out the door; funnel-layer negatives (L11) keep any future mid-funnel test from fighting the exact bottom-funnel campaigns.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/negative-keyword-system.md` | building and maintaining the negative keyword system |
| `references/search-term-mining.md` | the weekly search-term read and what to do with each finding |

## Hard rules

- No campaign goes live without its negative lists in place (corpus consensus).
- Never add a negative from a single bad click without reading the pattern; one-off negatives pile up into a strangled account.
- Never stuff competitor names into ad copy as keywords without a policy decision; trademark and trust costs are real.
- Every keyword change that affects serving goes through Gate-D when it changes spend exposure.
- Dated-match-era advice (SKAGs, heavy exact-match surgery) is flagged as dated in the doctrine and never executed as current practice.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-keywords/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-keywords` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
