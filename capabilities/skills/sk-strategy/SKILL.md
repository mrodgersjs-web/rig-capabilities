---
name: sk-strategy
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Positioning for a Skool community: who it is for, the one-line promise, community-first versus course-first, free versus paid, and the About page as the offer. USE WHEN starting or re-positioning a community, when members join but do not engage, or when Mike asks what the community should be about. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, strategy]
outcome: "content-publishing: the community leaves this stage with a named member, a one-line promise, an offer shape (free/paid/price), and an About page that sells the promise"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-strategy/SKILL.md
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-strategy
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "8"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-strategy: positioning, promise and the offer shape

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: does a topic fit the promise, is the promise specific enough, which positioning option wins, is free or paid the right shape. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check idea.solid --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `idea.solid` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use before the first public invite, before any growth push, and whenever members churn without engaging. Not for classroom content (sk-content) or pricing detail (sk-monetization).

## Procedure

1. **Name the member** in one sentence (role, company size, the bottleneck they carry). For RIG Intelligence Lab: an owner or ops lead at a small or mid-size company with AI tooling that is not running anything reliably.
2. **Write the promise** in the form `I help <member> get <outcome> without <pain>` and test it against three strangers: can they say in 10 seconds what happens inside?
3. **Community-first, not course-first** (corpus consensus): the community is a container where people solve real problems together; the classroom content is the byproduct collected from that work. Design the room before the curriculum.
4. **Choose the offer shape**: free community as top-of-funnel with a paid tier named after an outcome, or paid-only with a clear first-24-hours win. The corpus holds both winning; the deciding question is whether Mike's proof is visible before payment.
5. **Rewrite the About page as the offer**: promise, what members do each week, who it is for, who it is not for, one proof receipt, the next step. Biography goes last.
6. **Jev**: run the promise and offer shape through `idea.solid`; keep only PASS or record DEFERRED.
7. Hand the positioning card to sk-launch.

## Hands the next stage

`positioning-card.md`: member, promise, offer shape with price band, About-page draft. sk-launch tests it on a tiny cohort; sk-content builds the classroom from the promise.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-strategy.md` (local corpus, not republished).

- L1. Build a container where like-minded people solve problems and reach goals together, and treat videos/classroom resources as the byproduct collected from that shared work — [quote in corpus notes] is the exact opposite model and you never reach emergent product quality that way CLAIM(fXiFlwKvB3U@0:40)
- L2. Position as a living case study: pick the niche where you are personally seeking the most growth, declare where you are, document what you try daily, and take members alongside the journey ("Biggest Loser" reality-TV frame) — you don't have to be the expert, you have to declare the path and walk it visibly CLAIM(fXiFlwKvB3U@17:44)
- L3. Never claim a secret sauce: say openly that no offer works the same as the next and run everything as hypothesis -> action -> data -> revised hypothesis (stated by someone with 66,000 students and $15M of Facebook ad spend behind her) CLAIM(fXiFlwKvB3U@18:52)
- L4. If you don't yet have a personal brand, start from a declared shared goal others can instantly understand ([quote in corpus notes]) rather than an open-ended self-improvement path; only personal-brand owners can sell multi-passionate adjacent offers on day one CLAIM(fXiFlwKvB3U@22:54)
- L5. Treat the community as a block of marble carved over time, not a perfect product configured once — it evolves with you and members shape what it becomes, so the initial topic is a hypothesis, not a commitment CLAIM(fXiFlwKvB3U@23:49)
- L6. The about page casts a vision in one breath: [quote in corpus notes] — a bold declaration of direction outperforms a finished-looking product you can't yet deliver CLAIM(fXiFlwKvB3U@33:59)
- L7. Let member demand steer the niche: Coachcraft Club started as documenting self-improvement work with ChatGPT, absorbed AI-safety/ethics education when that problem surfaced, and only became an ICF-certified coaching certification after a member (25-year ICF coach) proposed merging her coaching with Evelyn's AI/marketing — lean into what the market and members say they need CLAIM(fXiFlwKvB3U@25:04)
- L8. Expect roughly 10% of your community's content to be what people actually come and return for; find that 10% after members arrive and their real problems are visible instead of pre-building a full library CLAIM(fXiFlwKvB3U@26:38)

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
| `references/promise-and-shape.md` | writing the one-line promise and choosing free vs paid |
| `references/about-page-audit.md` | auditing the About page against the promise |

## Hard rules

- The About page, community name and price are public: drafted here, changed only after Mike's explicit yes (Gate-D).
- A claim on the About page needs a receipt (a dated number or a named, permissioned client). No invented results. Creator revenue numbers from the corpus are UNVERIFIED self-reports.
- Never position around the minor (Jacob) or reuse Lane A mascots (Birch, Unit 7, The Coach) in this community.
- Single-source laws are hypotheses: say so when one drives a recommendation.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-strategy/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-strategy` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
