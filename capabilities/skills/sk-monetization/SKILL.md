---
name: sk-monetization
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. The money model: price bands, free-to-paid conversion, offer ladders, high-ticket offers, and what the corpus says actually sells on Skool. USE WHEN setting or changing price, when free members are not converting, or when designing an upsell. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, monetization]
outcome: "content-publishing: a price and offer ladder with a named conversion path from free member to paid outcome, each rung justified by a receipt or labeled untested"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-monetization/SKILL.md
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-monetization
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "5"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-monetization: pricing, offers and the free-to-paid conversion

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this price right, is this offer sound, is this conversion path honest. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check offer.eval --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `offer.eval` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after engagement works (members talk and stay). Not for growth volume (sk-growth) or positioning (sk-strategy).

## Procedure

1. **Price from the outcome band**: the corpus price bands that clear are $7-25 one-time (small assets), $27-49/mo (volume communities), $67-97/mo (outcome-named, persona-sharp), $199+ only as ladder-top with thin visible demand. Pick the band the promise can carry and label any creator number UNVERIFIED.
2. **Name the paid tier after the outcome**, not "premium": members buy the named transformation.
3. **Free-to-paid path**: the free room proves the method; the paid tier carries the named outcome (done-with-you workflows, reviews, live seats). Publish exactly what changes at the boundary.
4. **The conversion moment is a win**: convert members right after they experience a first win, not on a timer.
5. **Offer ladder**: free -> paid community -> high-ticket (done-for-you or intensive). Each rung needs its own promise; do not stack vague "VIP" tiers.
6. **Jev**: run each offer through `offer.eval`.

## Hands the next stage

`monetization-card.md`: tier map with prices and outcome names, the conversion moment design, the ladder. sk-gate screens all public price/offer language; the price change itself is Gate-D.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-monetization.md` (local corpus, not republished).

- L29. Use a price-tier ladder: her membership began at $27/month, then a lower $7 tier was added and exploded to over 1,000 members within two months — the low-ticket tier became the breakthrough engine of the business CLAIM(fXiFlwKvB3U@3:33)
- L30. Low price competes with big audiences in platform contests: an $8 community did $81,000 during the first Skool Games and took second place behind a $129 community with a massive YouTube following CLAIM(fXiFlwKvB3U@4:09)
- L31. Give the core playbook away free as mid-funnel: her community-idea validation method is free on YouTube and she says outright [quote in corpus notes] — generosity converts later and pre-filters serious builders CLAIM(fXiFlwKvB3U@30:54)
- L32. Monetize depth after the base: Coachcraft Club layered an ICF-certified coaching certification (co-created with a member who is a 25-year ICF coach) on top of the low-ticket community — let the community's revealed needs dictate the higher-ticket deliverable CLAIM(fXiFlwKvB3U@25:04)
- L33. A personal-brand community can sell across interests (ads, YouTube content, coaching, education offers) because members buy from the person; a no-name community should sell one shared goal only until that trust exists CLAIM(fXiFlwKvB3U@23:00)

## Where the creators disagree

(none recorded - one channel)

## Creator result claims (UNVERIFIED, never repeat as fact)

All figures below are self-reported in this interview (or stated by the host from her materials) and are not independently verified:

- $9M+ total online sales (host intro, CLAIM(fXiFlwKvB3U@0:00) and 1:30)
- Skool communities doing ~$61,000/month; biggest community over $61,000/month (CLAIM(fXiFlwKvB3U@1:47))
- [quote in corpus notes] (host framing, CLAIM(fXiFlwKvB3U@0:12)); her own account: second place behind Hamza in the first games (CLAIM(fXiFlwKvB3U@3:58))
- 66,000+ customers served, more than 36,000 of them paying subscribers (CLAIM(fXiFlwKvB3U@1:36))
- $81,000 revenue during the first Skool Games with an $8 community (CLAIM(fXiFlwKvB3U@4:16))
- $27 membership; a $7 lower tier that grew past 1,000 members in two months (CLAIM(fXiFlwKvB3U@3:26))
- $15M spent on Facebook ads across her career (CLAIM(fXiFlwKvB3U@19:06))
- Abandoned a 25,000-member Discord in the move to Skool (CLAIM(fXiFlwKvB3U@9:07))
- 15 years in digital marketing; runs the ads for the Skool platform itself (CLAIM(fXiFlwKvB3U@3:06), CLAIM(fXiFlwKvB3U@1:56))
- Platform-level stats repeated from Skool/its ecosystem (not her results): ~20M Skool users (CLAIM(fXiFlwKvB3U@10:04)); communities get ~30% of members from Skool discovery on average (CLAIM(fXiFlwKvB3U@11:27))

## Platform mechanics (Skool's own behavior)

Skool discovery rewards community activity: owner activity drives engagement, which drives platform exposure (fXiFlwKvB3U@12:10). Skool Games is a monthly platform contest with a leaderboard (fXiFlwKvB3U@3:33).

## RIG application (RIG synthesis, not corpus claims)

- The container model maps directly onto [quote in corpus notes]: members bring one real workflow and leave with owner, sources, gates, approval boundary, ProofPacket, and agent routing. Those ProofPackets and gate runs ARE the emergent classroom — record the live teardowns and collect the artifacts instead of pre-building a governance course (L1, L18, L21).
- Positioning can run pure living-case-study: Mike documents RIG's own governed build-outs (real gate runs, real deferrals, real ProofPacket hashes) as the shared journey. This dovetails with RIG's [quote in corpus notes] law — the transcript's [quote in corpus notes] frame is the same anti-fabrication posture dressed for marketing (L2, L3, L19, L20).
- Validate before building, at $50: about-page copy = one vision sentence ([quote in corpus notes]), cover image as ad creative, open tier-1 targeting. Pass = registration under $2 or 1-2 sales at a $7-10 entry price. The Meta-clarity test doubles as a positioning gate: if Meta's AI can't parse the audience, a human operator won't either (L9-L12, L14).
- Monetization ladder: $7-10/month entry community funds discovery and retention; the certification-style upsell (Coachcraft's ICF play) becomes a [quote in corpus notes] credential or a fixed-scope governed-build engagement — and per the 10% rule, let members' repeated bottlenecks reveal which workflow deserves the high-ticket product (L8, L29, L32).
- Engagement ops is one adapted script plus intros: welcome DM = [quote in corpus notes], then actually do it; party-host intros between members with adjacent bottlenecks; Mike runs a real workflow live on calls (up the slide first) rather than lecturing governance theory (L22-L25).
- The party-without-you exit test translates to: members run their own workflow reviews with the gate ritual unprompted. That is also the retention metric — count the ritual's recurrence, plus comebacks after trial churn, not just day-30 actives (L26, L28).
- Growth surface plan for a small lab: choose a discovery category with under a handful of competitors, spend real effort on cover art (AI image tooling is already in the stack), and give genuine value in adjacent Skool communities (AI, ops, agency operators) so profile clicks funnel into the lab — the ~30% free discovery share is the channel that makes the rest affordable (L34-L38).
- Ops reality check: Skool's consolidation replaces the VAs/Zapier-era stack, but the actual weekly operating cost is live hosting time — budget Mike's hours for themed calls and welcomes, and treat [quote in corpus notes] as the completion condition for the build-out (L40, L41).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/tier-map.md` | designing the free/paid/ladder tier map |

## Hard rules

- No invented scarcity and no fake countdowns; price changes are announced honestly with the real reason.
- Never quote a creator's revenue figure as expected outcome; the corpus's $61K/mo, $100K/mo, $18K/mo claims are self-reports (UNVERIFIED).
- Refund and cancellation terms are published before the first charge.
- Setting or changing a price is Gate-D.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-monetization/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-monetization` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
