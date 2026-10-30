---
name: ss-bestseller
description: >-
  The Bestseller track for a Substack publication: the math to 100 paid subscribers (the Substack Bestseller badge), the paid tier designed as a membership, upgrade entry points (premium content library, start-here post, free preview with a paywall), trust cadence, quarterly sprint launches and the 30/60/90/180-day roadmap. USE WHEN Mike asks to make the Substack a bestseller, to get paid subscribers, to redesign the paid tier, to plan a paid launch, or to check progress toward the badge. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, bestseller]
outcome: "business-ops: the publication runs a dated roadmap to 100 paid subscribers, with a membership-grade paid tier, at least three upgrade entry points, a weekly trust cadence and one sprint launch per quarter, each milestone read from Substack's own stats"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-bestseller/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-bestseller
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "15"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-bestseller: the Bestseller track: 100 paid subscribers in 12 months

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: is the paid tier worth more than its price, is a perk distinct from the free tier, is a launch plan ready, is a milestone movement real. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check opportunity.money --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `opportunity.money` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when the goal is paid subscribers or the badge, when designing or repricing the paid tier, before any paid launch, and on the monthly bestseller review. Not for the general money model or lead magnets (ss-convert), the send itself (ss-publish) or Notes craft (ss-notes).

## Procedure

1. **Baseline from the source**: signed in as the owner account (rodgemd1@gmail.com for rigoperator), read Settings > Payments and Stats: free subscribers, paid subscribers, paid conversion. Never a remembered number. If the browser is signed in as a different account, stop with `BLOCKED: wrong Substack account`.
2. **Run the math** (sub-skill `bestseller-roadmap.md`): 100 paid divided by a planning conversion of 1 to 3 percent gives the free list the badge needs (roughly 3,300 to 10,000). Turn that into a weekly free-subscriber target and a dated milestone ladder.
3. **Design the paid tier as a membership** (sub-skill `paid-tier-as-membership.md`): perks that are different in kind from the free issues (live sessions, templates, a resource vault, guides), not more of the same emails. Jev `opportunity.money` on the tier before it goes to Mike. Price and tier changes are Gate-D.
4. **Build the upgrade entry points** (sub-skill `upgrade-entry-points.md`): a premium content library page, a pinned start-here post with the upgrade link, and a free preview with the paywall placed after real value on every premium issue.
5. **Hold the trust cadence** (sub-skill `trust-cadence.md`): Notes on weekdays (ss-notes), one long-form issue a week (ss-plan), credentials on the About page and bio (ss-strategy), one live session a month (ss-network).
6. **Sprint launch once a quarter** (sub-skill `sprint-launch.md`): a three-day campaign with a clear reason to join now; between sprints, no constant pitching.
7. **Monthly review**: compare the ladder with Substack's own stats (ss-measure), name the one lever that moves next month, and file it on the Kanban `funnel` stream.

## Hands the next stage

`bestseller-plan.md` (math, ladder, tier design, entry-point checklist, next sprint date). ss-convert keeps the back-end offer; ss-plan schedules the premium issues; ss-publish installs pages and paywall placement after Mike approves; ss-measure reads the ladder weekly.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-bestseller.md` (local corpus, not republished).

- L1. Design the paid tier as a membership with perks, not as more of the same emails behind a wall. CLAIM(Z0Gsoq_XaFg, Q9LyrI1-Ikg, evhFCjvrZPY) | channels: 3 | status: consensus
- L2. Put the what and why in free posts and the how, processes and implementation details behind the paywall. CLAIM(evhFCjvrZPY, KOVyFPVIiMk) | channels: 2 | status: consensus
- L3. Use the free preview then paywall mechanic on paid posts: give free readers the opening half, keep the rest for paid. CLAIM(H7kMwgF4s8s, tdG-eFG8m9U) | channels: 2 | status: consensus
- L4. Build a premium content library and a become-a-member page, and use them as the upgrade entry points free readers can see. CLAIM(1HesDOF88zI, 9i2YgGGOQlk) | channels: 2 | status: consensus
- L5. Switch paid on early, even if most content is still free, and launch the paid tier instead of waiting for it to sell itself. CLAIM(tdG-eFG8m9U, 62w-shatAGs) | channels: 2 | status: consensus
- L6. Do not compete on being cheap; make the paid tier so valuable that the price stops being the question. CLAIM(1HesDOF88zI, evhFCjvrZPY) | channels: 2 | status: consensus
- L7. Price in the low single digits per month for most writers, and make the annual plan the clearly better deal you promote. CLAIM(evhFCjvrZPY, 62w-shatAGs, Ai2jOkW8L7o) | channels: 3 | status: consensus
- L8. Anchor the founding tier as the premium, more-access plan so the annual plan reads as a bargain. CLAIM(kuEKgddrTPo, XMrtkjcnPfY, -oefERiv7M0) | channels: 2 | status: consensus
- L9. Sell in sprints: run a launch with a reason to buy now every couple of months instead of promoting constantly. CLAIM(Hl5aJ_qt0Q4, eRnuvgty84A, dqIszSNFLX4) | channels: 3 | status: consensus
- L10. Build trust before the ask; trust comes from consistency, expertise and personality, and no trust means no upgrade. CLAIM(Z0Gsoq_XaFg, evhFCjvrZPY, SDhiDwkHu-w) | channels: 3 | status: consensus
- L11. Show up frequently; posting weekly is not enough visibility to convert, and paywalled posts are part of the cadence. CLAIM(evhFCjvrZPY, Z0Gsoq_XaFg) | channels: 2 | status: consensus
- L12. Budget realistic free-to-paid conversion: expect a single-digit percent of the free list to pay, and plan years not weeks for large paid counts. CLAIM(P18ORkNQj1Q, 2VBILAKOT2o) | channels: 2 | status: consensus
- L13. Treat the bestseller badge as social proof and take readers on the journey to 100 paid subscribers out loud. CLAIM(Z0Gsoq_XaFg, Hl5aJ_qt0Q4, Q9LyrI1-Ikg) | channels: 3 | status: consensus
- L14. Treat the paid tier as the starting point of monetization and stack products and services on top, selling again to existing buyers. CLAIM(V2rJMfhLOYw, 1HesDOF88zI, SriVT0SUGE4) | channels: 2 | status: consensus
- L15. Sell the paid tier at every touchpoint: welcome emails, footers, notes, thank-you pages, and every post. CLAIM(evhFCjvrZPY, tQW1gYsCZak, 4s7nmI2fN6U) | channels: 3 | status: consensus

## Where the creators disagree

Discounting. One side says give extra value instead of cutting price; the other side runs percentage discounts as standard launch mechanics.

Price level. One side prices low for impulse conversion; the other anchors the list price high and discounts down, because raising prices later is harder.

Role of paid subscriptions. One side treats the paid tier as the core path and promotes it hard; the other calls paid subscriptions the lowest, most effort-heavy tier and prefers higher-ticket offers.

Conversion rate. One side plans on 5 to 10 percent of the free list paying; the other reports that most publications land nearer 1 to 3 percent, below the platform's published average. Plan on the low band. (Added by the parent agent after review; quote verified verbatim in the transcript.)

## Creator result claims (UNVERIFIED, never repeat as fact)

All numbers below are creators stating their own results. UNVERIFIED.

## Platform mechanics (Substack's own channel)

(none in this dossier)

## RIG application (RIG synthesis, not corpus claims)

- Honest goal math: the corpus disagrees on conversion, 5 to 10 percent (CLAIM(P18ORkNQj1Q)) versus 1 to 3 percent (CLAIM(Z0Gsoq_XaFg)), so 100 paid subscribers needs somewhere between about 1,000 and 10,000 free subscribers; plan on the low band (about 3,300 to 10,000) and treat anything better as upside. rigoperator.substack.com has about 2 subscribers and 9 posts (2026-09-28). The binding constraint is list growth from Mike's ~5,400 LinkedIn followers, not price or perks.
- Honest revenue math: 100 paid at $8/month is about $800/month, roughly $8,600/year after Substack's 10 percent cut, against one $3,500 One-Workflow Review. Per the corpus, the paid tier is the beginning of monetization, not the end: its real jobs are trust, qualification and the bestseller badge as social proof for the back-end offer.
- Redesign the $8 tier as a small membership (perks like a monthly office hour, workflow teardowns, a template vault), add a founding tier above it as the anchor, and make annual the plan every promotion points to.
- Hold the free/paid line consistently: free posts carry the what and why of governed AI operations; paid posts carry the how (implementation checklists, prompts, gates, before/after workflows). Use the free preview then paywall format on every paid post.
- Build the premium library and become-a-member page now and link them from post footers and the welcome email. Since LinkedIn suppresses external links in post bodies, put the Substack link in comments and the profile instead.
- Run sprint launches (a founding window or a bonus template pack every 2 to 3 months) rather than constant promotion, take readers on the journey to 100 paid out loud, and stack the One-Workflow Review on top as the high-ticket offer the corpus says is easier to sell than 100 subscriptions.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/bestseller-roadmap.md` | the math to 100 paid and the dated 30/60/90/180-day ladder |
| `references/paid-tier-as-membership.md` | designing the paid tier as a membership whose value clearly beats its price |
| `references/upgrade-entry-points.md` | premium content library, start-here post and free-preview paywall placement |
| `references/sprint-launch.md` | a three-day paid-tier sprint launch instead of constant promotion |
| `references/trust-cadence.md` | consistency, expertise and personality as the weekly trust routine |

## Hard rules

- The badge is a paid-subscriber count Substack shows; it is never claimed, rounded up or implied before Substack's own dashboard shows it.
- Price, tier, founding-plan, discount and launch changes are Gate-D: drafted here, applied only after Mike's explicit yes for that item.
- Perks must be deliverable every month by RIG as it is staffed today; never promise a live session or a vault that nobody will run.
- No fake scarcity: a sprint deadline or discount must be real and must actually end.
- Creator income and subscriber claims from the corpus are UNVERIFIED and never shown to readers as proof.
- The minor's lane (Jacob) is never material for a paid perk, a launch or a case study.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-bestseller/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-bestseller` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
