---
name: ga-campaigns
description: >-
  Campaign-type selection and mechanics: Search, Performance Max, Shopping, Demand Gen, Display, Video, local campaigns and Local Services Ads boundaries, with asset groups, signals and exclusions. USE WHEN choosing which types to run, when PMax is proposed for a lead-gen account, or when a new type is added to the mix. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, campaigns]
outcome: "revenue-gtm: each campaign type in the account has a stated job, its required assets are complete, and the budget map shows where the money lives and why"
done_when:
  - grep:capabilities/skills/ga-campaigns/SKILL.md:Inbound before outbound
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-campaigns
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-campaigns: campaign types, Performance Max and local, chosen by job

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: is this campaign plan ready, does this type earn its budget, is this PMax setup sound. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check plan.readiness --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `plan.readiness` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after ga-structure fixes the jobs and before builds. Not for keywords (ga-keywords), bidding (ga-bidding), or creative (ga-ads).

## Procedure

1. **Choose the type by the job**, not by novelty: Search serves existing demand (people already looking); Shopping/PMax serve feed-driven retail; Demand Gen/Video create demand; local formats serve store/area visits; Local Services Ads (where available) serve pay-per-lead local services.
2. **Inbound before outbound**: search/inbound gets the first claim on budget; display/outbound is the most expensive and most frustrating, and runs last (corpus consensus, prior skill R7).
3. **PMax discipline**: PMax is a feed-and-asset machine. Run it with complete asset groups, audience signals, brand exclusions where brand runs separately, and a written statement of what it is for. Do not put a local lead-gen account's whole budget into PMax first (corpus consensus, prior skill R4).
4. **Local mechanics**: explicit location targeting to the real service area, call tracking in place, and a serving check at 48 hours (ga-local-b2b). Geo-narrowing that starves the auction is a launch bug, not a strategy.
5. **One type, one measurement**: each type's success metric is named before launch (Search: cost per qualified lead; PMax: value/conv with feed health; Video: qualified reach or view-through to action).
6. **Jev**: the campaign plan through `plan.readiness`; DEFERRED blocks the build.

## Checklist (before this stage is called done)

- [ ] Type chosen by job; inbound/outbound order respected
- [ ] PMax, if used, has complete asset groups, signals and a written purpose
- [ ] Budget map shows money per type with the reason
- [ ] Success metric named per type
- [ ] Kill criteria written for each new type
- [ ] Location targeting set to the real service area
- [ ] 48-hour serving check scheduled at launch
- [ ] Jev `plan.readiness` run on the campaign plan

## Hands the next stage

`campaign-plan.md`: type-by-type job table, budget map, asset requirements per type, measurement per type. ga-bidding sets strategies per campaign; ga-ads supplies the creative.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-campaigns.md` (local corpus, not republished).

- L1. Pick the starting campaign type by job: lead-generation and new accounts start on Search (e-commerce starts on Search or shopping), and Performance Max is a secondary campaign added only after Search is already producing results.
- L2. Avoid Performance Max for lead generation - especially B2B, service and local businesses - until Search campaigns are dialed in, because PMax tends to deliver low-quality or junk leads for service businesses.
- L3. Local and service businesses have no product feed, so they start on Search, add remarketing later, and treat Performance Max as a cautious budget-limited addition - very low budgets get wasted in PMax.
- L4. Performance Max runs on signals, not targeting: an audience you supply does not constrain delivery, so PMax cannot be restricted to remarketing - use Demand Gen when you need true audience targeting.
- L5. Split a Performance Max campaign into separate asset groups only when you have genuinely different assets or product sets - never one asset group per audience signal - because too many asset groups split the learning and slow results.
- L6. Tweaking audience signals or search themes after launch is not an optimization lever for a running PMax campaign - fix the creative, bid strategy, feed or conversion foundations instead.
- L7. Search and Performance Max overlap wastes money: Google keeps the search campaign prioritised when the query matches your keyword, so running both duplicates spend and lets PMax take credit for search - pick one container or fund them deliberately.
- L8. When the same product sits in both a standard shopping campaign and PMax, PMax wins priority - paired shopping-plus-PMax setups must therefore divide roles deliberately instead of hoping each campaign reports its own demand.
- L9. Shopping is available only to advertisers with a Merchant Center product feed: e-commerce anchors on shopping (with search), while service and local businesses never have shopping as an option.
- L10. Performance Max locks you into smart bidding at the campaign level - only maximize conversions or maximize conversion value, with no asset-group-level bid optimizations - unlike search and shopping, which keep extra bid levers.
- L11. Do not run Performance Max on a small budget: the spend fragments across every Google surface at once and neither the advertiser nor the system can optimize it properly.
- L12. Performance Max buys display, video and YouTube whether you want it or not - if you cannot accept that, run a standard shopping campaign instead of a feed-only PMax, because feed-only PMax is shopping with far less control.
- L13. Feed quality is the foundation of shopping and PMax: without an optimized product feed, the campaigns underperform and PMax drifts off the shopping network into display and Gmail.
- L14. Demand Gen is the campaign type for advertisers arriving with social-platform creative and for top-of-funnel demand creation, and it is the recommended first step beyond search, especially for B2B.

## Where the creators disagree

Feed-only PMax: one channel praises it as a conservative, smart-shopping-like way to start, while another has moved against it, and a third dislikes it too - the same podcast that once recommended feed-only builds now advises against them.
Related: the shopping episode of the same podcast still says feed-only is what it likes (17wfLxcRLdE, @paid-search-podcast), and another channel flatly prefers a plain shopping campaign over feed-only PMax (12WcVma-rSA, @jyll-saskin-gales).

Running Search and PMax together: one camp says consolidate - either all-in PMax or separate campaigns - while another runs PMax deliberately as a secondary layer on top of working Search.

E-commerce starting campaign: shopping-first, search-plus-shopping-first, or PMax-and-shopping-first - the corpus disagrees on the ecom launch recipe.

Brand terms inside PMax: keep brand in PMax so the campaign gets easy conversion data, versus keep PMax off brand so it works as a prospector (with brand exclusions and a catch-all shopping campaign as the alternative pattern).

The dossier is thin on the legacy Local campaign type itself: the only local-campaign mechanics evidence is the 2026 transition of Local Services ads into PMax pay-per-lead campaigns (4Fz0hfRELE0, @surfsideppc), so treat everything else here as local-lead-gen advice rather than Local-campaign documentation.

## Dated advice (platform mechanics change; re-verify before relying)

- Feed-only PMax described as replicating Smart Shopping (kKV_l8-Idxo, @solutions8 - video titled [quote in corpus notes]; also i_YMgSCUSBo, @growmyads and al_9S9ulAHM, @solutions8): Smart Shopping no longer exists as a campaign type - it was retired into Performance Max - so this is a 2023-era migration analogy, not current mechanics.
- Discovery campaigns listed among the available campaign types (QMIu5P8Io_w, @paid-search-podcast - video date not stated in the dossier, vocabulary predates the rename): Discovery was renamed to Demand Gen, and every later window in this dossier (2025-2026 era) uses Demand Gen.
- Treating PMax as an unreportable black box (older windows; era contrast from hjR-ZoaDthU, @jyll-saskin-gales - "How to Win in 2026" - and e_CbHH4yeY4, @jyll-saskin-gales): as of the 2026 windows, PMax reports asset and channel level data, so black-box workarounds and pure guesswork optimization advice are outdated.
- AI Max described as currently rolling out in beta on search campaigns (EvJrxtDxeAI, @optmyzr; toggle also noted in P4uEJvRWuII, @optmyzr - GML 2025), and smart bidding exploration described as rolling out by audience (OncFM7TkjxY and Z6__SrYuXjo, @surfsideppc - [quote in corpus notes]): beta availability, defaults and eligibility change quickly - re-verify before relying on either.
- Campaign-type landscape in the 2025-titled videos (FV398dDqNG0 and QhaiqGPlY2Y, @aaron-young) predates AI Max, which later windows describe as a new campaign type (hJgR4Uu2VMo, @ben-heath): any six-type taxonomy from those videos is now incomplete.

## Creator result claims (UNVERIFIED, never repeat as fact)

- Up to a 52% increase in sales attributed to search from a feed-driven DSA automation (QplC-zjbu_E, @optmyzr) UNVERIFIED
- A 31% ROAS increase in 2.5 months, as stated in the video title (H4ewmCKxFQM, @solutions8) UNVERIFIED
- Standard shopping ROAS moved from about 90% down to 75-77% while PMax launched at 200% ROAS on the same account (u2jJH6wrbAY, @solutions8) UNVERIFIED
- Sales doubled using the standard-shopping feeder strategy, as stated in the video title (VfBMl8WOVH4, @growmyads) UNVERIFIED
- Audits of 20-30 accounts over the prior couple of months showed PMax consistently producing low-quality or junk leads for B2B/B2C service businesses (w7C_GRLklf0, @growmyads) UNVERIFIED
- With a standard shopping feeder feeding PMax, PMax eventually out-spent and out-performed standard shopping, flipping a client's spend ratio (vhOCc2S5xxM, @solutions8) UNVERIFIED

## Platform mechanics notes

- New Google Ads accounts are pushed to create a Performance Max campaign before account setup is even complete (lg9ixk2KOWQ, @jyll-saskin-gales) - re-verify in the live product.
- PMax serves search, shopping, display, video, Gmail, Discover and Maps (Maps where applicable) from a single campaign (lg9ixk2KOWQ, @jyll-saskin-gales; EXulCRg926Q, @ben-heath) - re-verify in the live product.
- Optimize targeting is on by default in Demand Gen and Display ad groups; left on, audience targeting is treated like signals, so it is recommended off before launch (XVoqjS90FZY, @jyll-saskin-gales) - re-verify in the live product.
- An account-level negative keyword list holds up to 1,000 negatives that apply to Shopping, Performance Max and Search campaigns (WfN0hZ6Qupc, @surfsideppc) - re-verify in the live product.
- Local Services ads are being integrated into the Google Ads interface as Performance Max pay-per-lead campaigns in 2026, still paying per lead, call or message rather than per click (4Fz0hfRELE0, @surfsideppc) - re-verify in the live product.
- There is no dedicated feed-only PMax campaign type: you build a normal PMax and strip it (including removing the final URL from the asset group so it saves) to run feed-only (17wfLxcRLdE, @paid-search-podcast) - re-verify in the live product.
- Brand exclusion lists can be applied to PMax, and excluding brand from PMax requires a catch-all standard shopping campaign or brand shopping ads stop serving entirely (Legy3ZUPYiQ, @growmyads) - re-verify in the live product.
- PMax now exposes asset-level and channel-level reporting, AI Max is a toggle on search campaigns, and smart bidding exploration is rolling out in stages (hjR-ZoaDthU and P4uEJvRWuII, @jyll-saskin-gales/@optmyzr; EvJrxtDxeAI, @optmyzr; Z6__SrYuXjo, @surfsideppc) - re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

RIG runs local B2B on small budgets with calls and forms as the only truth, so the default is Search alone; PMax stays off until Search has produced a real 30-day run of tracked call and form conversions.
Any PMax test sits behind Gate-D: budget raise, channel spread and kill decision all require typed approval, and lead quality is reconciled against the CRM - a PMax conversion that is not a real call or form fill does not count.
Budgets are small enough that L11 and L3 settle it outright - no PMax, no display/video expansion, one or two tightly funded search campaigns beat spend fragmented across surfaces.
If PMax is ever tested for a local offer, split asset groups by offer or landing page, never by audience; set signals once at launch and never treat signal edits as an optimization (L5, L6).
Shopping, feeder and feed-quality laws (L8, L9, L13) stay dormant for RIG - there is no Merchant Center feed - and Demand Gen is only a small, optimize-targeting-off top-of-funnel test after search is proven (L14).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/pmax-playbook.md` | running Performance Max without losing the plot |
| `references/local-campaigns.md` | local and service-area campaign mechanics |

## Hard rules

- A new campaign type is a hypothesis with a kill criterion written at launch (budget, time, and the metric that ends it).
- PMax never carries a small local lead-gen budget alone (corpus consensus).
- Any campaign that starts serving gets the 48-hour serving check (status, keywords, geo, budget vs planner range, billing, conversions recording).
- Local Services Ads eligibility and verification (Google's own background checks) are human steps for Mike; the skill stages, never signs.
- Enabling any campaign is spend: Gate-D.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-campaigns/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-campaigns` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
