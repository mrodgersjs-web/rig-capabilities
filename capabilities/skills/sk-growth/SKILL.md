---
name: sk-growth
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Getting members in the door: the traffic sources that work for communities, lead magnets, the zero-audience playbook, YouTube/content funnels, and referral loops. USE WHEN the room is under-filled, when a growth channel is being chosen, or when a lead magnet is being built. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, growth]
outcome: "content-publishing: a named traffic source with a measured member-per-week rate, one lead magnet earning its keep, and a referral loop members actually use"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-growth/SKILL.md
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-growth
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "6"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-growth: traffic, lead magnets and filling the room

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this channel worth the effort, is this lead magnet strong enough, is this growth tactic honest. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check idea.solid --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `idea.solid` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after the promise survives its tiny test (sk-launch). Not for paid acquisition (sk-ads) or distribution of community content (sk-distribute).

## Procedure

1. **One channel at a time**: pick the single channel where the member already spends attention (for RIG: LinkedIn and YouTube for ops/AI buyers), run it 30 days, measure members per week before adding another.
2. **Zero-audience playbook** (corpus): direct conversations and borrowed audiences (comments, collaborations, podcasts, others' newsletters) beat broadcasting into an empty room; show up where the bottleneck is already discussed.
3. **Lead magnet = a solved slice of the promise**: a checklist, template, or mini-workflow that delivers one win without the community, ending with the natural next step inside. The corpus's strongest magnets are outcome-named and small.
4. **Content funnel**: publish the de-identified cases and lessons publicly (sk-distribute places them); the community link is the CTA, one per piece.
5. **Referral loop**: ask members who got a win to name one person with the same bottleneck; make the ask specific and easy, never incentivized into spam.
6. **Jev**: screen each tactic with `idea.solid`; growth that needs deception is cut.

## Hands the next stage

`growth-plan.md`: the chosen channel with a 30-day plan, the lead magnet spec, the referral ask script, and the members-per-week target. sk-ads is the paid escalation; sk-measure reports the rate.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-growth.md` (local corpus, not republished).

- L34. Skool is a marketplace, not just a tool: ~20M users who already understand communities, joining multiple communities, with VC-funded supply growth building demand like Etsy or Amazon — being listed puts you where buyers already are CLAIM(fXiFlwKvB3U@10:04)
- L35. Platform discovery delivers about 30% of members on average (her main community: 30% directly from Skool) — treat discovery as a free acquisition channel you deliberately work, not a lottery CLAIM(fXiFlwKvB3U@11:19)
- L36. Four discovery surfaces to work, each with low competition: community-category search (often fewer than a handful of real competitors per category), cover art (easy standout with AI image tools and templates — [quote in corpus notes]), recommended-communities modules (hobby-plan communities get recommended to interested users), and profile exposure from engaging on the platform CLAIM(fXiFlwKvB3U@13:25)
- L37. Borrow audiences by genuinely engaging in big peer communities (e.g. Schoolers): post a real experience that worked for you or changed you, respond to people as a human (an encouraging comment or a genuine reply beats a value-bomb), never spam, and respect the host owner — profile clicks convert to community joins and follows CLAIM(fXiFlwKvB3U@15:56)
- L38. Give-first karma is the growth posture: never lead with [quote in corpus notes] — service the other community's members (you raise their owner's value too) and the joins follow on their own CLAIM(fXiFlwKvB3U@17:02)
- L39. Full-reach mechanics compound everything: one Skool post reaches every member with notifications, unlike a Facebook group where reaching your own members with a single post is impossible — that owned reach is what turns engagement into growth CLAIM(fXiFlwKvB3U@8:54)

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
| `references/lead-magnet-slice.md` | building a lead magnet that is a solved slice of the promise |

## Hard rules

- No fake engagement, no bought members, no link spam in other people's spaces (comment rules: positive-only, add value, one soft link at most).
- Every growth claim is labeled measured vs projected.
- Cold outreach beyond warm connections follows the gtm-cold-send-safety-gate before anything sends.
- Anything that publishes or sends externally is Gate-D.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-growth/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-growth` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
