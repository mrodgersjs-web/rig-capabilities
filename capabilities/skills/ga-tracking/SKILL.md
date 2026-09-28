---
name: ga-tracking
description: >-
  Conversion tracking for Google Ads: conversion actions, the Google tag and GTM, call and form tracking, enhanced conversions, GA4 imports, offline/CRM imports and consent mode. USE WHEN building a new account, before any bidding strategy change, when Google prompts to set up conversion tracking, or when reported conversions disagree with the CRM. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of google-ads-os.
owner: rig-intelligence
domain: Marketing
status: Stable
acl: internal
tags: [google-ads, google-ads-os, google-ads, tracking]
outcome: "revenue-gtm: every conversion action defined, firing, and proven by a test before any money is spent"
done_when:
  - cmd:python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-tracking/SKILL.md
  - cmd:python3 capabilities/skills/google-ads-os/scripts/check_family.py ga-tracking
quality_floor: 0.6
metadata:
  parent: "google-ads-os"
  laws: "14"
  corpus: "data/corpora/google-ads (1052 transcripts, 8 channels)"
---

# ga-tracking: conversion tracking as the foundation

## JEV-first mandate (read first)

**Findability anchor - this is an always-loaded instruction surface, not a deep reference.** This block sits in this stage's description, which every harness (Claude Code, Codex, Hermes, OMP, Prime Agent, Aside) loads into every session at start, and in the front door `google-ads-os` and Mike's always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"). The text reaches the agent before any task in this stage begins; an agent whose only context is this excerpt still routes to Jev first.

**JEV FIRST - before any frontier LLM call, on every task.** Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule) -> JEV (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`, decision id recorded) -> SYSTEM 2 (frontier LLM for generation) -> HUMAN (Gate-D: outward, paid, destructive). Semantic triage, routing and classification go to the rig-s1gate Jev path BEFORE any frontier LLM call. Re-run the inventory when scope shifts.

Typed judgments this stage forces: is this conversion a real, single, attributable action, is this tracking setup sound. Each goes to Jev (TypeSafe System One) before any frontier model opinion.

- Command: `~/.rig/bin/rig-s1gate check atomic.claim --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. No Google-Ads-specific rubric exists for this judgment; `atomic.claim` is the nearest existing one and is advisory until calibrated.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to spend, enable a campaign, raise a budget or publish. Ad spend is Gate-D: only Mike approves, and only the parent operator acts.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use before the first campaign goes live and before any smart bidding. Not for account structure (ga-structure) or reporting (ga-reporting).

## Procedure

1. **Define conversion actions** from the goal card (ga-strategy): one primary action per goal (call lead, form submit, purchase, booked meeting). Duplicates and vanity micro-conversions are demoted to secondary or removed.
2. **Install the Google tag** (direct or GTM) on every page; confirm it fires in Tag Assistant / the real-time report, not just in the source code.
3. **Call and form reality** (corpus consensus for lead gen): track phone calls at the account level with call detail, and form submits via a thank-you-page or event trigger. Phone is the primary conversion for most local service businesses.
4. **Enhanced conversions** on: hashed first-party data improves measurement in a consent-restricted world; verify the setting is actually recording.
5. **Import the right second source**: GA4 key events or offline CRM imports (with Google Click ID capture) for sales-qualified outcomes. One conversion action fires once per goal; count the click's downstream outcome, not the same lead twice.
6. **Consent mode and privacy**: regions with consent requirements get a consent-mode setup; never model or fabricate conversions to compensate for lost tracking.
7. **Prove it live**: fire a test conversion of each type and see it land in the account before spend. Google showing "Set up conversion tracking" is a red flag, not a suggestion.
8. **Jev**: each conversion action definition through `atomic.claim`; DEFERRED blocks launch.

## Checklist (before this stage is called done)

- [ ] Every conversion action defined with primary/secondary status
- [ ] Google tag verified firing on all key pages
- [ ] Call tracking and form/thank-you-page tracking both proven (lead gen)
- [ ] Enhanced conversions on and recording
- [ ] GA4/offline imports wired where the goal lives downstream
- [ ] Consent mode handled for the target regions
- [ ] Test conversions fired and observed landing in the account
- [ ] Jev `atomic.claim` run on each conversion definition

## Hands the next stage

`tracking-plan.md`: conversion actions with primary/secondary status, firing mechanism, test evidence (screenshot or real-time check), import sources. ga-bidding is only allowed after this is proven.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/google-ads/notes/ga-tracking.md` (local corpus, not republished).

- L1. Until conversion actions exist and fire, campaign spend can neither be steered nor judged — buying traffic before measurement is burning budget instead of learning. CLAIM(UOQK73bobyM, Yaniuwsxd60, vICMCqsa7DQ, 2TdOEFcS2bg, Nf1apn0Ju2Q, XcxGaBvYsW8, IrB1oSftw8c) | channels: 7 | status: consensus
- L2. Prove the tag is actually recording a test conversion before a campaign goes live; weak or broken measurement poisons every decision made after launch. CLAIM(KbZofs6q7R8, XcxGaBvYsW8, C_g9hTd-UgE) | channels: 3 | status: consensus
- L3. For lead forms and phone leads, count each unique lead once (count = one, not every), so page reloads, repeat submissions, and spam cannot inflate totals that bidding then optimizes toward. CLAIM(azlz9DqcALU, vICMCqsa7DQ, gu2qDwlmpiU, 3ok2qX3Iock) | channels: 2 | status: consensus
- L4. Fire the form conversion on a thank-you/success page rather than on the form click or button press, so only completed submissions register as leads. CLAIM(azlz9DqcALU, O3QZLz21V3k, vICMCqsa7DQ) | channels: 3 | status: consensus
- L5. Set the call-conversion duration threshold to whatever a genuinely qualified call lasts in your own call data, not the platform's short default, or bidding will chase disconnected or spam calls. CLAIM(C_g9hTd-UgE, 3ok2qX3Iock, waC1p1CLnA0, 2Y_prev5fb8) | channels: 3 | status: consensus
- L6. Use the native Google Ads conversion tag (with enhanced conversions) as the primary source instead of a GA4 import — the GA4 import path cannot carry enhanced conversions and consistently attributes less back to Google Ads. CLAIM(i_YMgSCUSBo, 17wfLxcRLdE, zMDsA7h8uGo, 6BhGaQ-RTyw, C_g9hTd-UgE) | channels: 2 | status: consensus
- L7. Give the account exactly one primary conversion goal to optimize against and hold everything else as secondary; secondary actions still collect data without steering bids. CLAIM(EwsDW3OQj5k, 4Cgc9PsCWrY, O3QZLz21V3k, 3W0XeR3va20) | channels: 4 | status: consensus
- L8. For lead-gen businesses, the strongest feedback loop is the offline conversion import: send back which form fills and calls became paying customers so bidding learns toward revenue rather than toward raw leads. CLAIM(vICMCqsa7DQ, KbZofs6q7R8, Nf1apn0Ju2Q, 6rfn9UdT4lg, 8DgOX5aizyE) | channels: 4 | status: consensus
- L9. Click-ID (GCLID) based offline imports still match leads at higher rates than enhanced conversions for leads; EC4L is the lighter-lift option that improves identity matching but does not teach the algorithm about revenue. CLAIM(ARR-wcgFC1s, oWSHR2_8uE0) | channels: 2 | status: consensus
- L10. Enhanced conversions for leads depend on capturing user-provided data (name, email) from the form on the thank-you page and passing it through a user-provided-data event in the tag or GTM before Google can match it to later offline outcomes. CLAIM(YtxsHL2w-bA, 4FPgR9a_3c4, r3rv1qugGYw) | channels: 3 | status: consensus
- L11. Consent mode and enhanced conversions are baseline measurement requirements, not optional upgrades — omitting them silently shrinks the conversion data the account optimizes from. CLAIM(6rfn9UdT4lg, 2TdOEFcS2bg, ShUDhQpmyds, XcxGaBvYsW8) | channels: 2 | status: consensus
- L12. Instrument every contact path the business genuinely relies on — calls, forms, chat, bookings — so no real lead route is invisible to optimization, but track nothing that is not a true lead path. CLAIM(fNRvEj9jf3w, O3QZLz21V3k, UOQK73bobyM) | channels: 3 | status: consensus
- L13. Optimization learning accrues per conversion action, so reporting must be segmented by conversion action (plus an all-conversions column) to see which lead type a campaign is really producing behind its headline total. CLAIM(X9xCF5lCzuU, ZoQ30fw4Q5s, 7twmzrtQdpo) | channels: 2 | status: consensus
- L14. Re-labeling a conversion action between primary and secondary only applies from the moment of the change — previously recorded conversions are never reclassified. CLAIM(bcQKmH1cvzE) | channels: 1 | status: single-source

## Where the creators disagree

GA4 as the conversion source: one camp treats Google Analytics as the default tracking route, another actively warns against it as the primary conversion action.
The corpus leans native-tag-primary (L6), but the GA4 route is not universally condemned — treat GA4-linked tracking as acceptable for measurement, inferior only as the bidding primary.

Calls-from-ads as an optimization goal: one window treats calls from ads as a legitimate primary conversion to bid toward, another points out that Google's "calls from ads" counter can report phone calls for clicks where the phone never rang.

The dossier is thin on direct GCLID-vs-EC4L head-to-head trials; the two windows that discuss both (ARR-wcgFC1s, oWSHR2_8uE0) are complementary rather than contradictory, so the point is settled as L9 rather than contested.

## Dated advice (platform mechanics change; re-verify before relying)

RBvD5Z0ucTk (@growmyads) is framed in a 2023 auto-apply-recommendations context, advising that the [quote in corpus notes] recommendation is a yes because it switches the account to data-driven attribution:
Changed since: data-driven attribution is now the standard default and the auto-apply recommendations list has been revised; re-check what that toggle actually applies in the current interface.

Gu-seS8didI (@paid-search-podcast) explicitly notes older attribution menus (first-click, linear, time-decay, position-based) are gone for most accounts, leaving only two choices:
Changed since: any advice referencing the four legacy non-data-driven models pre-dates the current account defaults; verify which models your account still exposes.

17wfLxcRLdE (@paid-search-podcast) describes GA4 as brand-new and clunky in the same window — a snapshot of the early GA4 era. The GA4-vs-native-tag attribution gap it cites may have shifted; re-measure rather than assuming the old magnitude.

## Creator result claims (UNVERIFIED, never repeat as fact)

- Native Google Ads purchase tag yields up to roughly 10-15% more attributed conversions than a GA4 primary import (@growmyads, zMDsA7h8uGo) UNVERIFIED
- Around 80% of accounts the creator audits have incorrect tracking, stated as a personal feeling, not a measured sample (@growmyads, WhaVp5efaFs) UNVERIFIED
- A client account appeared to hold a 93% conversion rate, later found to be page views counted as conversions (@jyll-saskin-gales, 6JI0fjrV1Io) UNVERIFIED
- Better and more accurate attribution observed inside Google Ads when running the Google Ads purchase tag versus a GA4 import (@growmyads, i_YMgSCUSBo) UNVERIFIED

## Platform mechanics notes

- Enhanced conversions for leads is enabled in conversion settings, then chooses between Google tag and Google tag manager as the installation method (4FPgR9a_3c4, @solutions8) — re-verify in the live product.
- Offline import rows require the gclid, the conversion name, and an event time that falls after the click; value and currency are optional and default to 1 USD (4FPgR9a_3c4, @solutions8) — re-verify in the live product.
- Count setting (one vs every), 30-day click-through window, and data-driven attribution are the defaults walked through during conversion-action setup (azlz9DqcALU, @growmyads; 1gcjYJLUyf8, @ben-heath) — re-verify in the live product.
- Per-action reporting is exposed via the all-conversions column plus Segments → Conversions → Conversion action (7twmzrtQdpo, @jyll-saskin-gales; ZoQ30fw4Q5s, @solutions8) — re-verify in the live product.
- Consent mode status appears under the measurement diagnostics tab with a good/excellent rating (ShUDhQpmyds, @jyll-saskin-gales) — re-verify in the live product.
- The free Google Tag Assistant Chrome extension lists the Google Ads tag, Google tag, and GTM container installed on a site (r3rv1qugGYw, @surfsideppc) — re-verify in the live product.

## RIG application (RIG synthesis, not corpus claims)

- Gate-D on spend doubles as a tracking receipt: no campaign launches until Tag Assistant shows the tags live and a test form submission lands in the conversions summary — proof before budget, same pattern as every RIG outward-action gate.
- RIG's local B2B setup is the L3/L4/L5 combo by default: thank-you-page form conversion with count = one, plus a phone conversion whose duration equals a real qualified call (a few minutes, not 10-60 seconds), since calls + forms are the only truth in a small account.
- Keep one primary goal per campaign (L7) — booked appointments primary, everything else secondary — so a small daily budget has a single learning signal instead of splitting across five actions.
- Segment by conversion action weekly (L13) so call leads and form leads are read separately; a campaign totals 12 conversions while producing 10 junk chat clicks is invisible without the segment.
- GA4 stays linked but secondary; the native Google Ads tag with enhanced conversions is the bidding primary (L6, Contested).
- When a CRM or call log exists, start importing offline conversions on gclid for closed-won only (L8/L9) — EC4L is the cheap first step, GCLID the upgrade once lead quality data is trustworthy; consent mode on for any non-US traffic (L11).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/conversion-actions.md` | defining, deduplicating and prioritising conversion actions |
| `references/enhanced-and-offline.md` | enhanced conversions, offline imports and the CRM feedback loop |

## Hard rules

- Never turn on spend, and never switch to smart bidding, with unproven conversions (corpus consensus; the failure mode is bidding against noise).
- One real-world outcome = one conversion action. No duplicate goals counting the same lead.
- Never edit tracking to make a report look better; tracking reflects reality.
- Do not model, backfill or fabricate conversions when consent blocks measurement; report the gap instead.
- Account-level changes to conversion settings are audited through change history (ga-reporting).

## Done-test

`python3 capabilities/skills/google-ads-os/scripts/claims_check.py capabilities/skills/ga-tracking/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ga-tracking` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
