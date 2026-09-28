---
name: ga-landing
description: >-
  Landing pages for Google Ads: message match, first-screen facts, offer clarity, forms, speed, mobile integrity and trust evidence. USE WHEN launching to a new page, when clicks convert poorly, or when quality score or ad relevance flags the page. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, landing]
outcome: "revenue-gtm: every ad group lands on a page whose first screen states the same promise as the ad, with one clear action and honest proof"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-landing/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-landing
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-landing: landing pages that pay the ad's promise

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: does this page pay the ad's promise, which page variant wins. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check website.buyer --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `website.buyer` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use before launch and whenever a well-clicked theme converts poorly. Not for ad copy itself (ga-ads) or tracking (ga-tracking).

## Procedure

1. **First-screen facts**: H1 restating the query's promise, the offer with its entry point, one primary CTA, and who it is for - visible without scrolling on mobile.
2. **Message match audit**: for each ad group, compare query -> ad headline -> page H1. Discontinuity is the first thing to fix; it wastes every click.
3. **One page, one action**: the primary CTA is singular (call, form, booking); secondary links exist but never compete visually.
4. **Form reality**: ask only what qualification truly needs; every extra field costs conversions. Phone-first pages for local services offer click-to-call above the fold.
5. **Speed and mobile**: the page loads fast on 4G and does not shift under the thumb; run the budget page test (payload caps, LCP) before pointing spend at it.
6. **Trust and honesty**: real proof (named, permissioned), real prices where possible, no invented reviews; anti-slop: no generic stock-hero fluff (the `website.buyer` rubric scores trust, offer clarity, conversion architecture and anti-genericity for exactly this).
7. **Jev**: page through `website.buyer`; the weakest axes become the fix list. DEFERRED blocks launch claims.

## Checklist (before this stage is called done)

- [ ] First screen: promise, offer/entry, CTA, audience visible on mobile
- [ ] Query-to-ad-to-H1 match verified per ad group
- [ ] One primary CTA; secondary links do not compete
- [ ] Form fields minimised; click-to-call for phone-first
- [ ] Speed/mobile sanity checked on real mobile
- [ ] Proof elements real and permissioned; anti-slop pass
- [ ] Jev `website.buyer` run; fix list produced

## Hands the next stage

`page-audit.md` or the live page URL: message-match table, first-screen facts, CTA, fix list by priority. ga-ads mirrors the page's winning lines back into headlines.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-landing.md` (local corpus, not republished).

- L1. The page must continue the click's context: congruity between what the ad offered and what the page says is among the most reliable ways to lift landing-page conversion. CLAIM(w_5b2tGUpxg, pYKHOU1LW_0, g_Iu0-nJR5E, 0KIY8kV2X6E, jnAYabeKSag) | channels: 3 | status: consensus
- L2. Give each distinct service or ad-group theme its own landing page instead of sending every click in the account to one generic page. CLAIM(LfkAXL16vWg, 2YLibZjYsdo, c2RJdGLVAfQ, 7NiYaLazFas, ycJzp9qws74, O3QZLz21V3k) | channels: 4 | status: consensus
- L3. Speed is part of conversion: a cluttered or slow-loading page burns the paid click before the offer is ever evaluated. CLAIM(jqhCN63n5o0, LfkAXL16vWg, IzRWGp6bhFs, g_Iu0-nJR5E, 4ntMYTYW99E, DPOqrGqX0Rs) | channels: 4 | status: consensus
- L4. Structure the page around one immediate next action: the call to action and form visible up front, not buried under a wall of text the visitor must scroll. CLAIM(LfkAXL16vWg, za3IfB_5UME, tL6GRaZnTvs, O3QZLz21V3k) | channels: 4 | status: consensus
- L5. Carry the keyword and the searcher's language into the page's headline and copy, so the context that produced the click survives the jump to the page. CLAIM(vICMCqsa7DQ, LfkAXL16vWg, jnAYabeKSag, 7NiYaLazFas) | channels: 4 | status: consensus
- L6. Conversion rate is the diagnostic that separates an ad problem from a page problem: relevant clicks arriving with no conversions point at the offer or the page, not at the platform. CLAIM(jKyJt4wcfjw, h7xOSw1i7Jw, 2U6svvKSHVA, iMyrQVNiTLQ) | channels: 2 | status: consensus
- L7. The page is the leverage point: a strong landing page can still rescue a mediocre campaign, while no amount of campaign polish saves a poor one. CLAIM(RqXUSIo6ySw, RCRPj2JmqCY, WhaVp5efaFs) | channels: 2 | status: consensus
- L8. When paid visitors leave the page within about thirty seconds, the first suspects are the headline, the description and the top-of-page layout — diagnose there before touching targeting. CLAIM(2U6svvKSHVA) | channels: 1 | status: single-source
- L9. Forms should qualify, not merely capture: qualifier or anti-spam fields drop unfit leads out early instead of buying raw volume that wastes sales time. CLAIM(6rfn9UdT4lg, HQVyxAE-wLM) | channels: 2 | status: consensus
- L10. Check the page on a schedule: a contact form or step that has silently stopped working costs leads every day it goes unfixed. CLAIM(N1bqDcjRkdc) | channels: 1 | status: single-source
- L11. Trust elements — testimonials, before/after proof, a demonstration video showing the product working — are a direct conversion lever, not decoration. CLAIM(tL6GRaZnTvs, IzRWGp6bhFs, LfkAXL16vWg, 3UO1VcidoMk) | channels: 2 | status: consensus
- L12. There is no universal conversion-rate benchmark: any quoted percentage is account-specific, so judge a low rate against the account's own economics rather than agency-touted numbers. CLAIM(SCKxRaRuGXA, v1CyqPqs82k, VZxIrvPAC8Y) | channels: 2 | status: consensus
- L13. Optimise the page by testing it: split traffic between page variants to find the winner, but reserve formal experiments for changes that justify the traffic they cost. CLAIM(C-vE6IR7IfI, VQF7GfwSnvU, w_5b2tGUpxg, Wj4af7IwRFI, aP9_U1gweOc) | channels: 4 | status: consensus
- L14. Landing page experience is a Quality Score component — relevance to the keywords, load speed, mobile-friendliness and navigability — and it shapes both what a click costs and whether ads serve at all. CLAIM(DPOqrGqX0Rs, 4ntMYTYW99E, LiiXqXPblyY) | channels: 3 | status: consensus

## Where the creators disagree

Dedicated landing pages versus the client's own site. One camp says the client paid for their website and it should carry the traffic, and that the biggest fans of landing pages are the people who sell them:

The other camp treats a dedicated, distraction-free paid page as the better default:

The same podcast host elsewhere says plainly that he dislikes siloed self-contained landing pages, while @ben-heath and @growmyads build per-theme pages as a core recommendation — the corpus does not converge on one answer (see also L2).

Conversion-rate benchmarks. The corpus disagrees on what a "good" rate is: @jyll-saskin-gales gives a form-fill target of about 10% for service businesses,

@ben-heath anchors 5%+ for lead gen in another video, @growmyads sets a local-services floor of 5% aiming at 8-10%,

while @paid-search-podcast (L12) rejects benchmarking altogether. Treat all of these as starting hypotheses, not thresholds.

Does headline copy move conversion rate? @paid-search-podcast says headline-level conversion data is not worth optimising because the rate is driven by keyword-to-page relevance,

whereas @aaron-young's 30-second-exit diagnostic (L8) points at the headline as the first thing to fix.

Is the landing page gaining or losing power? @optmyzr argues generative assistants are draining landing-page influence,

while @aaron-young and @growmyads still treat the page as the decisive lever (L7) in 2026-dated videos.

## Dated advice (platform mechanics change; re-verify before relying)

SCAG-era granularity, referenced in @growmyads' AMA dated August 2024 ([quote in corpus notes], 7NiYaLazFas). Single-keyword ad groups predate full smart-bidding adoption; the same video's own working guidance themes pages by service (emergency vs. generic plumbing), and the rest of this dossier recommends per-service or per-ad-group pages, not per-keyword pages. Dated advice; page granularity now follows volume and theme, not keyword count.

Forward-looking speculation in @paid-search-podcast Episode 465 (BcXaBsX3-gM, [quote in corpus notes]) that upcoming AI features would expose search terms, headlines and landing pages like DSA, with open uncertainty about whether an ad group's specific landing page would still be honoured. That was a bet on a rollout timeline; verify what actually shipped before designing page structure around it.

@optmyzr's 2024 Google Marketing Live recap (Ev7-JF43Ro4, framed [quote in corpus notes]) forecasts landing pages losing power to assistant-driven research. Dated to the 2024-2025 AI-search narrative; every 2026-dated window in this dossier still treats the page as decisive, so re-check as assistant traffic grows rather than acting on the forecast.

## Creator result claims (UNVERIFIED, never repeat as fact)

@solutions8 reports click costs falling ~40% overnight after a landing-page speed fix (JxGwtdq--9k, title: [quote in corpus notes]) UNVERIFIED

@solutions8 claims a 40% CPL drop comparing landing page vs. lead form in a lead-gen build (2MLpK8SWlgc, title: [quote in corpus notes]) UNVERIFIED

@growmyads' title claims leads tripled overnight via landing-page conversion hacks (tL6GRaZnTvs, [quote in corpus notes]) UNVERIFIED

@solutions8 reports a campaign conversion rate moving from 0.6% to 2.02% after restructuring which campaign feeds cheap leads into another (nv5OaVbzPLg) UNVERIFIED

@solutions8 claims a seasonal bid adjustment saved a client about 30% of budget around a pre-Christmas slump (5GqrDfFszQM) UNVERIFIED

@paid-search-podcast reports an automated campaign at 15% conversion rate versus a tight manual exact-match campaign at 5%, with different lead economics behind each (O9x9Y6KQbtk) UNVERIFIED

## Platform mechanics notes

Quality Score's landing page experience component is described as judging load speed, mobile-friendliness, original content and navigability (DPOqrGqX0Rs) — re-verify in the live product.

Landing pages that redirect, are low quality, 404, or confuse who the business is can trigger ad-serving limits or get ads turned off, and hurt ad rank/quality score (LiiXqXPblyY) — re-verify in the live product.

Conversions are commonly tracked by redirecting to an unfindable thank-you page and firing a Google Tag Manager page-view trigger when the URL contains "thank you" (r3rv1qugGYw, O3QZLz21V3k, LoyJP3qxJyY) — re-verify in the live product.

The lead form asset collects contact details directly in the ad without a site visit, and can then seed lead-form audiences (h6dYV5SJwmg); @paid-search-podcast reports only spam from this asset (qPKq784aP34) — re-verify in the live product.

Dynamic H1/headline swapping based on the search keyword is done through a URL parameter picked up by landing-page software (7NiYaLazFas) — re-verify in the live product.

Broad match, optimized targeting and AI Max read landing-page content as a targeting signal (IWfM94UfA4o, iODRmLSUTHQ, Rnwc4gN7GNs) — re-verify in the live product.

Google's seasonality-adjustment UI suggests entering the expected conversion-rate change (e.g. +50% for a 3-day sale), which @growmyads explicitly advises against following literally (Yc-8Vo8J5pA) — re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

RIG buys local-B2B clicks on small budgets, so message match is free leverage: one page per service theme carrying the ad's exact language in the headline, and no spend increase (Gate-D) until that page's own conversion truth — calls plus form submits — is proven.

Speed and form function are cheap insurance against a small budget's worst failure mode: a weekly smoke test of every form and a page-speed check catch the silent lead leaks the corpus warns about.

We track calls as first-class conversions because local buyers ring, and benchmark our conversion rate only against our own history — never guru numbers or other accounts' claimed percentages.

Qualifier fields on the form keep lead quality high so a one-person sales load is not burned on unfit enquiries; we trade a few points of raw conversion rate for it deliberately.

Split tests only earn their traffic once a page is stable and volume justifies the split; below that, ship the change and watch the account's own numbers.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/message-match.md` | the query-to-ad-to-page continuity audit |
| `references/form-and-speed-basics.md` | forms, first screens and speed checks that do not need a dev team |

## Hard rules

- The ad may never promise a step the page does not contain (no "instant quote" to a contact form that quotes nothing).
- No fake scarcity, fake reviews, or fabricated credentials; trust axes fail these hard.
- Tracking on the conversion event lives here too (ga-tracking owns the mechanism; this stage owns the placement).
- Every claim on the page is dated-checked before a flight starts; stale prices are bugs.
- Page changes on a live flight are experiments, not silent swaps.

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-landing/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-landing` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
