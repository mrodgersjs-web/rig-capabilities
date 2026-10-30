---
name: sk-engagement
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Making members talk and stay: the first-48-hours onboarding, conversation prompts, the weekly rhythm, gamification that earns its place, and the churn signals. USE WHEN members join and go quiet, when the room feels dead, or when retention drops. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, engagement]
outcome: "content-publishing: a new member gets a first win and a first conversation inside 48 hours, and the room has a weekly rhythm members can rely on"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-engagement/SKILL.md
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-engagement
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "7"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-engagement: onboarding, conversation and retention

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this member at risk, is this prompt worth posting, is this gamification mechanic earning its place. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check signal.performance --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `signal.performance` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use once members are joining (sk-launch feeds it), continuously after. Not for getting members in the door (sk-growth) or content design (sk-content).

## Procedure

1. **The 48-hour rule**: every new member gets a personal welcome referencing the bottleneck they named at enrollment, plus one concrete next step, within 48 hours. The corpus calls out talking to new members as the highest-leverage retention act.
2. **Prompt the room weekly**: one discussion prompt tied to a real workflow, not to "how is everyone doing". Prompts members can answer with their own work get replies; abstract prompts do not.
3. **Wins are the engine**: run a Wins thread; celebrate member outcomes with specifics. Leaderboards reward contribution (helpful replies, completed workflows), never raw activity.
4. **Office-hours rhythm**: one recurring live touch (call, hot seat, or async review) at a fixed time; consistency is what members cite when they stay.
5. **Churn signals to watch**: no post within 14 days of joining, no reply to the welcome, missed two sessions. Each triggers one personal check-in, not an automation.
6. **Gamification audit**: points/levels/badges only where the corpus evidence is that they drive the behavior wanted (replies, completions). Cut mechanics that only inflate vanity counts.

## Hands the next stage

`engagement-playbook.md`: the 48-hour onboarding script, the weekly prompt bank, the Wins ritual, the churn-signal list with check-in scripts. sk-measure tracks whether these work.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-engagement.md` (local corpus, not republished).

- L22. Owner activity is the engine of member activity: show up active and keep trying ways to engage members and engagement skyrocks first, then discovery numbers and platform traffic follow — Skool rewards the active community with exposure CLAIM(fXiFlwKvB3U@12:10)
- L23. Welcome every new member personally with a gratitude-plus-curiosity script: [quote in corpus notes] — then actually do the thing they name CLAIM(fXiFlwKvB3U@35:31)
- L24. Drop the shame of building in public: declare "I'm trying this" proudly and loudly; most people admire the courage and want to support builders, and the few who judge would never have bought anyway CLAIM(fXiFlwKvB3U@36:02)
- L25. Play party host, not broadcaster: introduce new members to existing ones with a specific credit ([quote in corpus notes]), then prompt both sides ([quote in corpus notes]) until members talk to each other, not just to you CLAIM(fXiFlwKvB3U@38:20)
- L26. The exit test of a community is that it runs without you for stretches — the party where you could step outside and nobody would miss you; your job is to make the sum bigger than its parts through intros and shared energy until that point CLAIM(fXiFlwKvB3U@38:44)
- L27. Be the first dancer (the man dancing alone in the park until the crowd joins): go first, keep the energy high while nobody is with you, accept visible rejection — one person joining starts the spiral; people quit because they tried to be the university professor instead of the host who goes first CLAIM(fXiFlwKvB3U@39:21)
- L28. Expect free-trial churn followed by returns: people sign up, feel overwhelmed or test something quickly, fall off, and come back when it clicks — so count comebacks in your retention read instead of only day-30 actives CLAIM(fXiFlwKvB3U@9:32)

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
| `references/onboarding-48h.md` | the first 48 hours for a new member |

## Hard rules

- Never fabricate engagement: no fake members, no reply rings, no engagement pods.
- Personal check-ins are personal: no mass DMs dressed as check-ins.
- A member's situation stays in the room: no republishing member problems as content without a yes.
- Public posts on behalf of the community go through sk-gate and Gate-D.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-engagement/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-engagement` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
