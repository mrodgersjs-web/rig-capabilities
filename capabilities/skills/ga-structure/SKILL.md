---
name: ga-structure
description: >-
  Account structure for Google Ads: campaign purpose, theme-based ad groups, brand vs non-brand separation, geo and language splits, naming, and shared-budget rules. USE WHEN building a new account, when an account has grown by accretion, or when structure questions (SKAGs, match control, single-keyword themes) come up. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, structure]
outcome: "revenue-gtm: a written account architecture where every campaign has one stated job, every ad group one theme, and every split exists because bidding or budgets differ"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-structure/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-structure
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-structure: account structure in the keyword-signal era

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: is this structure sound for the goal, does this theme deserve its own ad group, which architecture option wins. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check idea.solid --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `idea.solid` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after ga-strategy and before ga-campaigns builds anything. Not for keyword selection itself (ga-keywords) or campaign-type mechanics (ga-campaigns).

## Procedure

1. **One job per campaign**: name each campaign's job (brand defence, inbound search, outbound/display, PMax for feed-driven reach, local). A campaign with two jobs gets split.
2. **Theme-based ad groups**: each ad group holds one theme (service x intent), with keywords, ads and landing page all saying the same thing. SKAG thinking is dead (corpus consensus); rebuilds of single-keyword ad groups add maintenance without control.
3. **Brand separated**: brand defence runs in its own campaign so its cheap, certain conversions never inflate or subsidise prospecting metrics.
4. **Split only where money differs**: geo, language, device or daypart splits are justified only when bids or budgets must differ. Structural purity is not a reason to split.
5. **Match philosophy**: keywords are signals to Google's meaning matching, not exact control. Structure for intent and message match; the negative system (ga-keywords) is the control surface.
6. **Naming convention**: `<goal>-<geo>-<theme>-<type>` so any report, script or 3am incident sorts correctly.
7. **Jev**: run the architecture doc through `idea.solid`; record or DEFERRED. Hand to ga-campaigns.

## Checklist (before this stage is called done)

- [ ] Every campaign has one stated job in `architecture.md`
- [ ] Every ad group is one theme, and its ad and landing page agree
- [ ] Brand is its own campaign
- [ ] Each split states its money reason (different bids/budgets) or is removed
- [ ] Naming convention documented and applied
- [ ] No SKAG rebuilds anywhere in the plan
- [ ] Jev `idea.solid` run on the architecture doc

## Hands the next stage

`architecture.md`: campaign jobs table, ad group themes, split rationale, naming convention. ga-campaigns instantiates each campaign type; ga-keywords fills the themes.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-structure.md` (local corpus, not republished).

- L1. Relevance is engineered one level below the campaign: the campaign is a container that holds ad groups, while the ad group is where a single topic, its keywords and its ad copy are unified — build themes there, not at campaign level. CLAIM(jkfuN8i3eEs, _RTd76T6LnE, ngNw8xJ8Rq8) | channels: 3 | status: consensus
- L2. Modern accounts consolidate: carving structure up by match type, device or geography is a legacy pattern that adds complexity without adding control, and over-complicated campaign layouts just create chaos. CLAIM(SoX8Fz8ECV4, ngNw8xJ8Rq8, viaUh_DGRxk, -EI4g8CnsLY) | channels: 3 | status: consensus
- L3. Every ad group expresses exactly one theme; keywords that belong to the same topic live together, and structure is built theme-first rather than keyword-first. CLAIM(viaUh_DGRxk, ZA1uCsYPjPU, SoX8Fz8ECV4, ZM5PkgMKbM8) | channels: 4 | status: consensus
- L4. Single-keyword ad groups (SKAGs) are a historical strategy: because match types no longer isolate queries, one-keyword-per-group structure is universally treated as obsolete in favour of theme-based groups. CLAIM(2736aI4wjM4, ZA1uCsYPjPU, 8g3IVte6uvE, SoX8Fz8ECV4, LkM4kqidwu4, yLJI1TN4DQI) | channels: 5 | status: consensus
- L5. Fragmenting a theme into one-keyword groups starves most of those groups of volume while the queries concentrate in the few larger groups, and it multiplies the optimization surface to hundreds or thousands of ad groups. CLAIM(NxLPIA8Av6U, yLJI1TN4DQI) | channels: 2 | status: consensus
- L6. The corpus shares one naming convention — STAG, the single-themed ad group — which its practitioners explicitly say they did not invent; worked examples name groups by theme modifier (general, emergency, affordable) rather than by keyword. CLAIM(h2C5OxFNLr8, ngNw8xJ8Rq8, LkM4kqidwu4) | channels: 2 | status: consensus
- L7. Ad groups stay small and theme-tight: a handful of well-matched keywords per group is the working norm (commonly cited in the 5–15 range, with stricter advisors capping at five or six), and padding groups with extra keywords is discouraged. CLAIM(LkM4kqidwu4, Tg1v9bO6lp0, c2RJdGLVAfQ, ARqItjB9zlc, b3AJlS3AVtQ) | channels: 3 | status: consensus
- L8. Tie ad groups to landing pages or offers — roughly one group per landing page or per service — so the ad and the page it sends clickers to carry the same message. CLAIM(ngNw8xJ8Rq8, c2RJdGLVAfQ, LoyJP3qxJyY) | channels: 3 | status: consensus
- L9. When two ad groups can trigger the same queries they compete against each other, so overlapping intents get merged into one themed group instead of being split across groups. CLAIM(ZA1uCsYPjPU, RXV8UkDld_A) | channels: 2 | status: consensus
- L10. Isolate brand demand: run brand terms in a dedicated campaign and add the brand terms as negatives to non-brand campaigns so branded queries funnel into the brand campaign instead of competing with it. CLAIM(HvxLB3w7Sb8, yzJc_pFwiLc, NTdQpENDQ7g) | channels: 3 | status: consensus
- L11. Keep the brand campaign pure — brand terms only; letting non-brand keywords into it corrupts the clean brand performance data the campaign exists to produce. CLAIM(D0aOHgSbOi8, NTdQpENDQ7g) | channels: 2 | status: consensus
- L12. Match types are intent signals, not literal gates: exact and phrase now key off the meaning of a query rather than its literal words, so every match type has widened relative to its original definition. CLAIM(nvEZo_P_p1Q, NxLPIA8Av6U, 16X5a0Ii7kg) | channels: 3 | status: consensus
- L13. Broad match reads its surroundings as targeting input — sibling keywords in the same ad group and the landing page content both steer which queries it serves — so ad group composition must be curated deliberately. CLAIM(3ok2qX3Iock, OtGKmt5pbys, IWfM94UfA4o) | channels: 2 | status: consensus
- L14. Broad match is an expansion move, not a starting point: layer it in only once conversion data and smart bidding are working, then let it widen reach under a targets-based bid strategy. CLAIM(ohXNz-iiAnk, Wj4af7IwRFI, mwHtA1iNg-0) | channels: 3 | status: consensus

## Where the creators disagree

Phrase match's role in a modern match-type roster is genuinely split — one camp still starts new accounts on phrase match, the other retires it in favour of broad plus exact:

Alpha/Beta match-type campaign segmentation: one side writes the method off as obsolete, the other still runs a version of it — promoting profitable broad keywords to exact inside the ad group that triggered them, then reshaping structure monthly around a top-keyword campaign:

Broad match stance ranges from never to required. The cautious side treats it as a budget leak, especially for advertisers who do not know what they are doing; the expansion side treats it as the reach engine and points at AI-search placement rules:
The corpus does not converge beyond a shared floor: unsuitable as a starting point, usable only once conversion data and a targets-based bid strategy exist.

Where geographic segmentation belongs — campaign or ad group:

Ad group size ceiling is inconsistent, even inside one channel: one episode caps each group at five keywords while another allows ten to fifteen broad terms, and the 5–15 band is the most repeated figure across the corpus (LkM4kqidwu4, @jyll-saskin-gales; Tg1v9bO6lp0, @jyll-saskin-gales; c2RJdGLVAfQ, @ben-heath):

## Dated advice (platform mechanics change; re-verify before relying)

SKAGs — the one-keyword-per-ad-group playbook early winners were built on — are dated by the corpus's own account, because exact match now targets query meaning rather than the literal keyword, so one keyword no longer fences off one query set (2736aI4wjM4, @aaron-young; ZA1uCsYPjPU, @aaron-young, titled for 2026):

Campaigns split by match type, device, or Alpha/Beta keyword tiers are treated as a bygone-era method and explicitly retired in a video titled The BEST Google Ads Campaign Structure in 2025:

Broad match modifier was beloved and then removed from the platform (video: Outdated Google Ads Strategies), so any structure document with a BMM layer refers to a retired match type:

Ad groups split by match type — the same keywords parked in a separate exact group, phrase group and broad group — stopped working once all match types went meaning-based; Google now also recommends treating duplicated exact/phrase pairs as redundant (1MRDIlKuLrQ, @paid-search-podcast):

PMax custom search-term audience signals were replaced by search themes in a rollout the video dates to 2024; verify what replaced what in a live account:

Naming caution: one 2026 walkthrough applies the STAG acronym to the old single-keyword structure while the rest of the corpus uses it for the single themed ad group, so the acronym is ambiguous across videos:

## Creator result claims (UNVERIFIED, never repeat as fact)

- Revenue up $290k+ and ROAS doubled in 120 days on a client account — (D0aOHgSbOi8, @growmyads) UNVERIFIED
- Example account showing exact-match clicks at over $11 versus broad-match at $6.50 — (OtGKmt5pbys, @aaron-young) UNVERIFIED
- Own account holds 172 phrase-match keywords, 171 of them three words or longer — (2hHxA9hzI2U, @paid-search-podcast) UNVERIFIED
- Keyword Planner forecast (a tool projection, not observed performance) of 46 conversions for $6,000 at $200/day — (rU8lbqJ4UWU, @surfsideppc) UNVERIFIED
- Internal study finding exact match clearly outperforming broad, no figures given in the window — (QplC-zjbu_E, @optmyzr) UNVERIFIED

## Platform mechanics notes

- Keywords entered without match-type syntax are added as broad match by default, and the interface nudges advertisers toward broad — (U1pa1Pyf5_g, @ben-heath; ZM5PkgMKbM8, @ben-heath) re-verify in the live product.
- Google's support documentation describes exact match as same-meaning queries and phrase match as including the keyword's meaning — (nvEZo_P_p1Q, @ben-heath; 16X5a0Ii7kg, @growmyads) re-verify in the live product.
- Broad match keywords are required for ads inside AI Overviews and AI mode, while exact match is prioritized above or below them — (5GkO2fzQYxk, @jyll-saskin-gales; e-p1kef8YZU, @aaron-young) re-verify in the live product.
- Broad match conceals many triggered queries from the search-terms report, so a fully clean search-terms report is only a realistic goal under exact match — (amlH9oNtS-M, @jyll-saskin-gales) re-verify in the live product.
- Negatives added from the search-terms report default to exact match on the full term — (5vG9ma30Vr0, @ben-heath) re-verify in the live product.
- Keyword prioritization in Search: an exactly matching keyword wins; otherwise phrase, broad and PMax search themes are equal priority decided by Ad Rank — (Ko-uIvLXntM, @jyll-saskin-gales) re-verify in the live product.
- AI Max moves location-of-interest targeting down to the ad group level and is described as replacing the broad-match upgrade nudges — (EvJrxtDxeAI, @optmyzr; 8DgOX5aizyE, @jyll-saskin-gales) re-verify in the live product.
- The interface auto-generates suggested ad groups during setup — (_RTd76T6LnE, @ben-heath) re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

RIG runs local B2B on small budgets with calls and forms as the only truth, so structure stays boring: one campaign per service area, STAG-named ad groups of 5–15 theme-tight keywords mapped one-to-one to landing pages, no SKAGs and no match-type or device segmentation.
Brand terms live in their own campaign with a brand-negative list on every non-brand campaign, so branded calls and form fills are never double-counted against prospecting spend.
Start every new account on exact/phrase; broad match enters only as an expansion move after conversion data exists and a target-based bid strategy is stable — and because broad widens spend, that switch is a Gate-D-covered change, not an optimization side effect.
Overlapping ad groups get merged before launch (competing groups burn budget against each other), and broad-match ad groups are curated deliberately since sibling keywords and the landing page steer what they serve.
Creator result numbers are never repeated as fact — they stay UNVERIFIED until reproduced in RIG's own account.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/single-purpose-campaigns.md` | splitting accreted accounts into single-purpose campaigns |
| `references/naming-and-hierarchy.md` | the naming convention, labels and hierarchy that keep reports honest |

## Hard rules

- Never rebuild SKAGs. The matching system that made them necessary no longer exists (corpus consensus; the 2019 advice in the corpus is flagged dated).
- Brand campaigns are worth running even when they feel redundant; never merge brand into prospecting.
- A split needs a money reason (different bids or budgets), not tidiness.
- Smart bidding works at the campaign's conversion data level: never fragment themes so thin that each campaign starves the learning system.
- Spend-affecting structural changes go through Gate-D.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-structure/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-structure` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
