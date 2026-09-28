---
name: ga-local-b2b
description: >-
  Local B2B and service-business application: the $1-50/day reality, calls and forms as the conversion truth, vertical-specific pages, brand defence, what NOT to run at small scale, the 48-hour serving check and lead-quality loops. USE WHEN planning or auditing a local service or B2B account on a small budget, and before any local spend decision. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, local-b2b]
outcome: "revenue-gtm: a small-budget account that spends only on proven inbound intent, tracks calls and forms as truth, and catches non-serving campaigns within 48 hours"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-local-b2b/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-local-b2b
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "12"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-local-b2b: local B2B service accounts on small budgets

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: is this account ready to spend, does this local build pass, is this spend justified. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check ad.search --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `ad.search` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use for local service and B2B accounts at small budgets ($1-50/day), from plan through post-launch checks. Not for large multi-market builds (ga-structure owns general architecture).

## Procedure

1. **Tracking before campaigns** (absorbed doctrine R2/R3): call leads AND form submits tracked and testable first; account-level call tracking, thank-you-page form tracking. A budget is wasted without this.
2. **Campaign roles named**: brand defence (worth running even when it feels redundant), inbound search (people already looking - the first claim on budget), outbound/display (most expensive, most frustrating, last resort) (absorbed doctrine R7).
3. **PMax is not the first home of a small local budget** (absorbed doctrine R4). Local lead gen starts on inbound search with themes and negatives (R5).
4. **Keyword-signal reality** (R1/R5): structure for intent and message match; broad match only with negatives and multiple themed keywords per group. No SKAG rebuilds (R6 - the 2019 advice is dated).
5. **Geo and call-detail settings are part of the build** (R8): explicit location targeting to the real service area; phone tracking set at account level.
6. **48-hour serving check** (post-launch lesson): read the account live at 48 hours and day 5; fix the first failing check the same day (status/limits, low-search-volume keywords, geo starvation, budget vs planner range, billing, conversions recording). If nothing can be fixed today, pause and say so.
7. **Small-scale honesty**: a test budget buys a few clicks a day; the measurement plan is calls and form fills per dollar, never impressions. Expectations are written before launch.
8. **Jev**: build/audit doc through `ad.search`; DEFERRED blocks "ready to spend".

## Checklist (before this stage is called done)

- [ ] Call + form conversions proven firing before any spend
- [ ] Campaign roles named: brand / inbound / outbound
- [ ] Inbound search gets first claim on budget; PMax not carrying it all
- [ ] Negative lists in place before any broad match
- [ ] Location targeting and call detail verified per the real service area
- [ ] Budget math and expectations written (calls/forms per dollar)
- [ ] 48-hour + day-5 serving checks scheduled
- [ ] Jev `ad.search` run on the build doc; Gate-D filed for spend

## Hands the next stage

`local-build.md`: roles table, tracking proof, themes + negatives, geo settings, budget math, expectations, 48-hour check scheduled. ga-reporting takes the post-launch reads.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-local-b2b.md` (local corpus, not republished).

- L1. When bidding is automated, feed Google qualified or revenue-bearing leads instead of raw form fills and calls — optimizing on unqualified lead count teaches the system to chase the cheapest, easiest leads. CLAIM(dcPh57jpjXE, Enzbe0A_9iM, 6rfn9UdT4lg, ARR-wcgFC1s, PyGLvGZ2TQo) | channels: 5 | status: consensus
- L2. Lead follow-up speed and persistence move results more than ad changes; slow or unanswered leads waste the entire click regardless of how the campaign is tuned. CLAIM(QbIIAH-S6xU, LmUFgCe3bms, g8gnRoCG38o, wYm34_1HHCI, yO1mcXxAoME) | channels: 4 | status: consensus
- L3. Keep location targeting tight and signal the service area in the creative — leads from outside the area are a negative signal that degrades where Google shows the ads. CLAIM(mrNz6FeNhOU, aoxxHsyFTlY) | channels: 2 | status: consensus
- L4. On a small budget, concentrate spend in a deliberately chosen core geography — one city, half a city, or a zip cluster — and treat distance zones differently instead of blanket coverage. CLAIM(O0ujCXXkYmg, JZaC1PHiU-E) | channels: 2 | status: consensus
- L5. Buy high-intent, service-specific queries (near-me, emergency, city + service) and block generic head terms such as a bare trade word, which attract useless clicks. CLAIM(w_5b2tGUpxg, JBQXOv-f2qQ, rmZ4324SL3c, Nf1apn0Ju2Q, v23Szju-CPM) | channels: 3 | status: consensus
- L6. Theme ad groups by intent (general vs emergency vs affordable) so the query that fires the ad and the ad copy actually match. CLAIM(UOQK73bobyM, h2C5OxFNLr8, SoX8Fz8ECV4) | channels: 1 | status: single-source
- L7. Start lead generation on Search and introduce Performance Max only later, and never before qualified-lead or offline conversion feedback is flowing back. CLAIM(EbAVitPFk-c, e-p1kef8YZU, ARR-wcgFC1s, P4uEJvRWuII, e_CbHH4yeY4) | channels: 3 | status: consensus
- L8. Run Local Services Ads alongside Search for local service businesses; LSA charges per lead rather than per click, with a different qualification and review bar. CLAIM(v-qPifo2WHc, j78nEE4s4kw, mrNz6FeNhOU, sq2N0NoFTRY) | channels: 3 | status: consensus
- L9. Derive the allowable cost per lead from unit economics — close rate times job value — and set the bid target comfortably below break-even. CLAIM(BCjgWC6T6W4, zU_zvbfU8Bk) | channels: 2 | status: consensus
- L10. Small local auctions are shallow: extra budget buys more clicks, not proportionally more leads, and more spend by itself does not buy efficiency. CLAIM(Er7mqpU4574, U9Bp3jMmvnc) | channels: 2 | status: consensus
- L11. Give each service its own landing page so the search that triggered the ad lands on matching content instead of a generic homepage. CLAIM(3xP8BVGwmJw) | channels: 1 | status: single-source
- L12. Know the back-end truth per source — answered calls, qualified leads, closed deals — before steering the front-end spend. CLAIM(IO9KXnoQ7No, cb1Pkwx2LGQ, ROs6o7Lllu4, b2i8juU6QOI) | channels: 4 | status: consensus

## Where the creators disagree

Performance Max for lead gen: one side refuses it outright for technical/B2B niches, arguing its conversions are unqualified and untrainable (lmkGyfbzZ_M, @paid-search-podcast).

The other side blames misuse rather than the campaign type, and treats PMax as inevitable once tracking exists (EbAVitPFk-c, e-p1kef8YZU, @aaron-young; also P4uEJvRWuII, @optmyzr).

A third window agrees automation flattens niche service businesses into a lowest common denominator (QGhc7LCLslM, @optmyzr), so the corpus does not settle whether a small local account should ever use PMax.

Starting point: one window advises collecting volume first and refining quality afterward (Vv7WE2qyuSE, @growmyads), while another calls form-fill-only optimization a dead end from day one (6rfn9UdT4lg, @jyll-saskin-gales).

Small accounts versus the algorithm: the corpus contains no evidence either way, only an explicit open question (GSkT5hUK434, @solutions8).

## Dated advice (platform mechanics change; re-verify before relying)

- LSA availability stated as US-only with an expectation of expansion (sq2N0NoFTRY, @jyll-saskin-gales, [quote in corpus notes], no date in window): country and industry coverage is date-sensitive — re-verify in the live product.
- Concentric-ring location bid adjustments (5/10/15-mile rings bid up and down) assume manual location bid adjustments still apply (JZaC1PHiU-E, @paid-search-podcast, [quote in corpus notes], no date in window) — re-verify under current automated bidding.
- Cheap-keyword threshold guidance (7NiYaLazFas, @growmyads, [quote in corpus notes]) is 2024 CPC-era pricing for local trades — re-verify current CPCs before using it as a filter.
- Conversion-goal editing advice (S0ZwJpMMFfU, @growmyads, [quote in corpus notes]) reflects 2024-era conversion goal and smart bidding behavior — re-verify how goal changes affect bidding now.
- "Power pair" for lead gen announced at GML 2025 (P4uEJvRWuII, @optmyzr) and the lead-gen pilots from the GML 2026 recap (YBSwn_fFLsk, @jyll-saskin-gales) were announcements/pilots, not settled product — re-verify availability in the live product.

## Creator result claims (UNVERIFIED, never repeat as fact)

- 3x return on ad spend across client accounts after recommending proper lead follow-up (LmUFgCe3bms, @ben-heath) UNVERIFIED
- A business tripled revenue with no extra ad spend and no more leads, purely from better follow-up (QbIIAH-S6xU, @ben-heath) UNVERIFIED
- Home services client: cost per lead fell from $121 to $68 after switching to maximize conversions, while CPCs rose from $1.77 to $10 and conversion rate went from 1.7% to 15%, off a ~6 leads/month baseline (Q_fB7F-oBVs, @jyll-saskin-gales) UNVERIFIED
- Landing page versus lead form test produced a large CPL drop (title claims 40%) with spend held back pending lead-quality results (2MLpK8SWlgc, @solutions8) UNVERIFIED
- Local service account in one small US city scaled from $20/day to $110/day spend (SZ1umIt9CqI, @aaron-young) UNVERIFIED
- One electrician lead referred onward to two neighbors was worth over $5,000 (yO1mcXxAoME, @aaron-young) UNVERIFIED
- Mature lead-gen accounts still spend roughly 60-85% of budget on search-based campaigns (EbAVitPFk-c, @aaron-young) UNVERIFIED

## Platform mechanics notes

- Local Services Ads are a pay-per-lead program and search ads are displayed below them (sq2N0NoFTRY, @jyll-saskin-gales; v-qPifo2WHc, @surfsideppc) — re-verify in the live product.
- LSA dynamically pulls USPs from the URL you submit into the platform, which you cannot directly control (QGhc7LCLslM, @optmyzr) — re-verify in the live product.
- Out-of-area lead behavior is taken as a negative signal against the campaign, so tighter location targeting is better (mrNz6FeNhOU, @aaron-young) — re-verify in the live product.
- Adding phone-call leads to a lead-collection campaign's conversion goal is fine, but removing the lead goal entirely in favor of phone-only would disrupt smart bidding (S0ZwJpMMFfU, @growmyads, October 2024 window) — re-verify in the live product.
- Linked local ads automatically track driving-direction lookups, which inflates lead counts and skews cost per lead (ZoQ30fw4Q5s, @solutions8) — re-verify in the live product.
- Offline conversion import accepts a plain 1-10 lead score rather than a monetary value, rated by sales staff (YtxsHL2w-bA, @aaron-young) — re-verify in the live product.
- GML 2026 pilots described: text-message assets with an AI agent responding and qualifying leads, a business agent for leads in AI mode, and probabilistic lead scoring Google claims predicts conversion at 90% certainty (YBSwn_fFLsk, @jyll-saskin-gales) — re-verify in the live product.
- Running two conversion actions for the same event (e.g. two lead-form/phone actions) guards against a silent tracking failure (EwsDW3OQj5k, @solutions8) — re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

- RIG buys only high-intent service queries inside a tight service-area radius, with the geography named in both the ad and the landing page so out-of-area clicks self-disqualify.
- Small budget means one focused campaign with intent-themed ad groups (general/emergency/affordable), spend concentrated on the core city or zip cluster, never a wide net across the region.
- Track calls and forms separately, then the booked-and-closed outcome; no PMax and no budget increases until qualified-lead feedback reaches Google — Gate-D holds the spend gate closed until those receipts exist.
- A five-minute callback SLA and answered-call rate are part of the campaign contract, not an afterthought: measure cost per contacted lead alongside cost per lead.
- Derive the target CPL from RIG's own close rate and job value before launch, and treat any corpus result claim as UNVERIFIED until reproduced on RIG's own account.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/small-budget-limits.md` | what a $1-50/day budget can and cannot do |
| `references/local-b2b-lead-quality.md` | the lead-quality loop for service and B2B accounts |

## Hard rules

- This stage absorbs `pmm-google-ads-local-b2b` as its parent material (its R1-R8 doctrine and the 48-hour serving check are restated here as procedure and laws); that skill file stays at `~/.aside/u/0/skills/user/pmm-google-ads-local-b2b/SKILL.md` and is never forked into a second copy.
- Every spend, bid, geography or enablement change is Gate-D through Mike; sub-agents never touch budgets or live status.
- Phone leads are a primary conversion for local service; never run a call-focused business on form-only tracking.
- Never report "we ran ads" unless the account shows serving and spend; state claims are live-read (lesson LS22: two written records disagreed; only the live read was right).
- Dated doctrine (SKAGs, exact-match surgery) stays flagged and unexecuted.
- Local Services Ads verification and any sign-up/verification step is a NEEDS-MIKE item; stage documents only.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-local-b2b/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-local-b2b` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
