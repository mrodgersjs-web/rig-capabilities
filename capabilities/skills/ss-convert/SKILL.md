---
name: ss-convert
description: >-
  Monetization for a Substack publication: paid tier settings, founding members, lead magnets, next steps in every post, and the route from reader to client. USE WHEN setting prices, designing a lead magnet, adding a call to action, or deciding whether the Substack should earn subscriptions or clients. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, convert]
outcome: "business-ops: every post carries one next step, and the publication routes serious readers to the One-Workflow Review rather than relying on subscription revenue"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-convert/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-convert
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "15"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-convert: free to paid, offers and readers to clients

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this offer or price sound, does a post's next step fit, is a lead magnet specific enough. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check opportunity.money --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `opportunity.money` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use when designing the paid tier, a lead magnet or a post's call to action. Not for publication settings mechanics (ss-publish).

## Procedure

1. **Decide the money model**: for RIG the Substack is the audience engine and the money is the back end (the $3,500 One-Workflow Review and fixed-scope builds). Paid subscriptions stay on as a filter, not the goal.
2. **One next step per post**: reply, subscribe, download the magnet, or book the review. Pick one.
3. **Lead magnets**: one specific asset per pillar (a workflow failure-test checklist beats "AI tips"). The RIG site's Client Intake Failure-Test Kit is the first candidate.
4. **Paid tier**: keep $8/month for now; if paid revenue becomes a goal, move toward the $10+ band with an announced change, never a silent one.
5. **Founding tier**: only when there is something distinct to give founding members (e.g. a quarterly workflow teardown call).
6. **Jev** `opportunity.money` on any new offer or price before it goes to Mike.

## Hands the next stage

The next-step line and magnet link for each issue (to ss-write and ss-package); price or tier proposals to Mike as Gate-D items.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-convert.md` (local corpus, not republished).

- L1. Turn on paid subscriptions and connect Stripe from day one, even with nothing behind the paywall yet. CLAIM(wEcOTy2gKcA, SzJlV4PVvn8, Do4_17UQu6k) | channels: 3 | status: consensus
- L2. Plan for 1 to 5 percent free-to-paid conversion, not more, and know that conversion differs by category. CLAIM(kpAZE6h9Ano, 4yQXgOoQYiI, xZtrPtlccBE) | channels: 3 | status: consensus
- L3. Do not treat paid subscriptions as the business: Substack is the audience engine and the money comes from what you sell on the back end. CLAIM(4yQXgOoQYiI, 2Tj4sZC2yes, C_R4O_y87qM, SdIT1XhD0eE) | channels: 3 | status: consensus
- L4. Sell one high-value offer instead of chasing hundreds of cheap subscribers: convincing one buyer at $1,500 takes the same marketing effort as convincing fifteen at $50. CLAIM(kpAZE6h9Ano, K74keCwfd0w, OB1MpswX8_o) | channels: 2 | status: consensus
- L5. Price the paid tier above $5, roughly $8 to $10 a month: the conversion difference is small and a $5 price cuts revenue in half. CLAIM(tKqhb7M4nyU, bgrm4pQU0oo) | channels: 2 | status: consensus
- L6. Run a founding-member tier at about 1.5 to 2 times the annual price with extra access, and give every tier its own distinct reason to exist. CLAIM(j67SabtPjGA, CzRjVEa0okA, KyQ4dmdkzV8, TMKw85o5bIw) | channels: 4 | status: consensus
- L7. Give every piece of content a next step: an article with a call to action beats one without, and each post should point at an offer. CLAIM(69ZI7ofPxUA, 4yQXgOoQYiI, HacRdXOMZSM) | channels: 2 | status: consensus
- L8. Use a specific lead magnet per article: low conversion usually means the offer is too generic for the audience. CLAIM(dBlSgcbHcug, EUughLjsbL8) | channels: 2 | status: consensus
- L9. Build a product ladder: start with low-cost entry products, bundle them upward, and sell the next step to people who already paid once. CLAIM(4yQXgOoQYiI, lOCoBwaG1b8, bzGYnY-Lzes) | channels: 2 | status: consensus
- L10. Treat the paid tier as a door to higher-ticket services, not the ceiling: one $5,000 client a month is already a $60,000 a year business. CLAIM(cbXWQTDQm3I, 3Cg75EWgV3k, mHRJfOWzdJQ) | channels: 2 | status: consensus
- L11. Package offers as course plus coaching so the price reflects applied help, not just information. CLAIM(kpAZE6h9Ano, K74keCwfd0w, As2CPh3N1dM) | channels: 2 | status: consensus
- L12. Use the publication to attract consulting and coaching clients: authority built in public makes every offer convert more easily. CLAIM(KyQ4dmdkzV8, W4rXKY5h6Fk) | channels: 2 | status: consensus
- L13. Add sponsorship revenue once the list can carry it: newsletter placements run from small flat fees to four figures per run. CLAIM(-s9dWPYSpAg, 7BVfCbIYihk, _m3lbUZnwT0) | channels: 3 | status: consensus
- L14. Announce price rises before they happen and stop fiddling with price: usually the problem is not the price. CLAIM(i4rzDd3NSEE, lfQfA32U0DE) | channels: 1 | status: single-source
- L15. Run the conversion levers on every send: get the welcome email reply, put the paid button near the top, use page breaks at 50 to 75 percent, and keep a sales page that explains the paid offer. CLAIM(xZtrPtlccBE, BFeOr46XCR4) | channels: 2 | status: consensus

## Where the creators disagree

Whether to sell subscriptions at all. For turning on paid immediately and converting free readers: CLAIM(wEcOTy2gKcA, Do4_17UQu6k, SzJlV4PVvn8) as in L1.
Against treating subscriptions as the model: the math needs thousands of free readers, so sell a product or service instead. CLAIM(C_R4O_y87qM, SdIT1XhD0eE, 4yQXgOoQYiI)
Middle path from one creator who did both: keep paid on as a filter, but expect the back end to carry the income. CLAIM(2Tj4sZC2yes)

Launch pricing. Low and low again: start cheap when the publication is new. CLAIM(VjKIdgUHpgs)
Against underpricing: hold $8 to $10 or higher because cheap prices halve revenue and attract buyers who do not value the work. CLAIM(tKqhb7M4nyU, bgrm4pQU0oo)

Where paid members actually come from. The standard doctrine assumes a free-to-paid funnel. One creator reports the opposite: her members skip the free tier entirely. CLAIM(pkvTxFyxnew)

## Creator result claims (UNVERIFIED, never repeat as fact)

(none recorded)

## Platform mechanics (Substack's own channel)

Feature facts, not doctrine. CLAIM(l9EaEdBxKm8, xsQtpZP9Ujs, -zcwkoORgCY, bTdUaD3dZ9E, GmCffJgypv0)

## RIG application (RIG synthesis, not corpus claims)

RIG synthesis, not corpus claims.
- Keep the $8 paid tier switched on (L1) but expect almost nothing from it: at the corpus's 1 to 5 percent math, 5,400 LinkedIn followers cannot produce meaningful subscription income, and the tier's real job is filtering the most serious readers (L3).
- The revenue target is the $3,500 One-Workflow Review, which fits the corpus's own instruction: one back-end sale beats hundreds of $8 subscribers (L4). Every post should carry a next step pointing at that offer or at a booking conversation (L7).
- Price the review using the course-plus-coaching logic (L11): the workflow blueprint is the course part, the live review session is the coaching part. That is what justifies a price above information products.
- B2B pricing context from the platform data: business and finance newsletters commonly run $10 to 50 a month or $100 to 500 a year. If paid revenue ever becomes a goal, $8 sits below that band; raising it later means pre-announcing (L14).
- Skip sponsorships for now (L13): the list is too small to sell placements, and sponsor money would distract from the client funnel. Revisit only after the list is in the thousands.
- Use one specific lead magnet per pillar post (L8): a workflow checklist for ops leaders beats a generic [quote in corpus notes], and each magnet should end with the paid-tier mention or the review offer (L15).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/reader-to-client.md` | routing serious readers to the One-Workflow Review |
| `references/lead-magnets.md` | specific lead magnets per pillar |

## Hard rules

- Price and tier changes are Gate-D; announce before changing.
- Never promise results in an offer; sell the scope and the acceptance test.
- Client case material needs the client's written permission before it appears in a post or offer.
- Creator income figures are UNVERIFIED and never quoted to Mike's buyers.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-convert/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-convert` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
