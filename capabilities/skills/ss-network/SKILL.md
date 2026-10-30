---
name: ss-network
description: >-
  The Substack network: recommendations in and out, cross-posts, guest posts, collaborations, Lives and chat. USE WHEN building recommendation swaps, planning a collaboration, or when growth inside Substack has stalled after Notes are running. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, network]
outcome: "content-publishing: a target list of peer publications, outgoing recommendations with blurbs, and one collaboration a month, all tracked by subscribers gained"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-network/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-network
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "12"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-network: recommendations, collaborations and community

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: is a peer publication a fit, is a collaboration worth the time, which recommendation to add. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check idea.solid --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `idea.solid` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after the publication has a promise and a few issues (peers check the archive before recommending back). Not for the daily Notes routine (ss-notes).

## Procedure

1. **Build the peer list**: 10-20 Substacks whose readers are RIG's reader (ops leaders, founders, AI practitioners). Source from the writers met in the ss-notes routine and from Substack search.
2. **Qualify each** with Jev `idea.solid` on a short card (topic overlap, size, posting activity).
3. **Recommend out first**: add 3-5 recommendations with a real blurb each. Recommended writers are notified and prompted to recommend back.
4. **Collaborate**: one per month at most: a guest post, a cross-post or a joint Live with a peer in the pillar.
5. **Track**: the Recommendations tab shows subscribers gained per recommendation; drop recommendations that send nothing after 60 days.

## Hands the next stage

`peer-list.md` with status per publication. ss-measure tracks the recommendation numbers.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-network.md` (local corpus, not republished).

- L1. Turn on the recommendations tool and recommend writers you genuinely read; it is the cheapest subscriber channel on the platform. CLAIM(FXmm21-Bdtc, sGV4NbLJezU, J1CMFNeRSnw, -s9dWPYSpAg) | channels: 6 | status: consensus
- L2. Do not accept Substack's suggested recommendations at signup; pick every recommendation partner yourself. CLAIM(TAqEplyhREw, K9eCC33QrQY) | channels: 2 | status: consensus
- L3. Start with three to seven recommendation partners at your own stage with audience overlap, not big names who will ignore you. CLAIM(K9eCC33QrQY, 4IEBRt8X2f0, k3hbRtfpZ84) | channels: 2 | status: consensus
- L4. Treat a recommendation as the opening move, then escalate the relationship to guest posts, shared lives, and joint workshops. CLAIM(K9eCC33QrQY, FXmm21-Bdtc, gMOA9rMYSlo) | channels: 3 | status: consensus
- L5. Co-host live streams with partner writers so both audiences get notified and each side is introduced by someone the audience already trusts. CLAIM(064AguKrp0M, 4kcYqHbmJa8, B3xgbjXUoJ4) | channels: 3 | status: consensus
- L6. Publish every live session as a post on both publications so the recording keeps working after the stream ends. CLAIM(uCVaTblDMxw, ILNjZPn78lg, 6nT6G_do-6c) | channels: 3 | status: consensus
- L7. Build the relationship before you pitch: read and comment on a writer's work first, then ask for the guest post or swap. CLAIM(uAz63ohoK_A, gMOA9rMYSlo, zm7pUqjQS6s) | channels: 3 | status: consensus
- L8. Pitch guest posts to publications with similar topics and similar audiences, and lead with value to their readers, not to you. CLAIM(Fm8FHHJzKTE, uAz63ohoK_A, gMOA9rMYSlo) | channels: 3 | status: consensus
- L9. Never drop links into other communities to recruit; participate first or you get a reputation as a spammer and doors close. CLAIM(1ixpYP8FjDo, B0oWRrWucBI) | channels: 1 | status: single-source
- L10. If you run chat, show up in it consistently; a chat nobody hosts is worse than no chat. CLAIM(FXmm21-Bdtc, gMOA9rMYSlo, 3uMOaySeafs, k3hbRtfpZ84) | channels: 4 | status: consensus
- L11. Do not open chat or a community space before you have members who will use it; an empty room costs moderation effort and discourages you. CLAIM(wEcOTy2gKcA) | channels: 1 | status: single-source
- L12. Go live on a steady cadence, at least monthly; live Q&A builds trust faster than text alone and lifts engagement and paid conversion. CLAIM(B3xgbjXUoJ4, C8T6sveRu9Q, _X_nTR0rNi8, dTk-SXIK3tE) | channels: 3 | status: consensus

## Where the creators disagree

- When to switch on chat. sutoscience says wait until a community exists (CLAIM(wEcOTy2gKcA)); the growth expert she hosts says chat is fine even under 1,000 subscribers: [quote in corpus notes] (gMOA9rMYSlo, @sutoscience)
- Where the community should live. The Coach's Alchemist treats an off-platform Skool community as the goal and routes followers there: [quote in corpus notes] (lXC52aR6NFM, @TheCoachsAlchemist) versus soloshannonhq keeping it all on Substack: [quote in corpus notes] (3uMOaySeafs, @soloshannonhq). sutoscience lands between them, wanting a community hub sooner but noting it is hard to move readers off Substack (CLAIM(WEZFIQ24I2c)).
- How selective to be about who you recommend. Mark J. Thompson takes a stand against recommending AI writers (CLAIM(sGV4NbLJezU)); creativelyconsciousUK recommends nearly everyone she reads as a generosity practice (CLAIM(0aOodX6hP1U)); substackgrowth wants agnostic reciprocal recommending among peers (CLAIM(iGFItajDlN0)).

## Creator result claims (UNVERIFIED, never repeat as fact)

- Over 10,000 subscribers to Sparkle from the recommendation tool, and thousands more from one named recommender. CLAIM(lfQfA32U0DE, 0aOodX6hP1U) | UNVERIFIED
- [quote in corpus notes] plus about 2,000 on a second publication. CLAIM(LOMfFtIbhOo) | UNVERIFIED
- [quote in corpus notes] from 85 recommending writers; a later video claims 1,600 from recommendations. CLAIM(uAz63ohoK_A, zm7pUqjQS6s) | UNVERIFIED
- 52 newsletters recommending mine at one point, later 59, plus $4,000 in month 13 and $18,000 in first paid subscriptions. CLAIM(EF_6YRFa_-M, lOXQUrt72tU) | UNVERIFIED
- [quote in corpus notes] CLAIM(0f89F3a4iqE) | UNVERIFIED
- 50,000 subscribers reached; [quote in corpus notes]; 20,000 subscribers within a first year on Substack. CLAIM(064AguKrp0M, Ss6UXtnSCes) | UNVERIFIED
- Substack income headline of $0 to $96,000 ARR by month 3. CLAIM(n36h4t-8EYU) | UNVERIFIED

## Platform mechanics (Substack's own channel)

- Chat rooms are subscriber-only and writer-controlled: [quote in corpus notes] (hmhHdkFcceE, @substackinc). Chat launched mobile-first on iOS.
- Chat is a private channel to your subscribers only, meant for discussion and conversation (CLAIM(bTdUaD3dZ9E)).
- Onboarding ends by inviting you to recommend writers you already subscribe to, who might recommend you back (CLAIM(Zp1KRvM1wW8)).
- [quote in corpus notes] (bTdUaD3dZ9E, @substackinc).
- In the recording studio, both host and co-hosts get a copy of the recording saved to their publication drafts, and both should publish it; branding is host-only and 85% of creators use it (CLAIM(6nT6G_do-6c)).

## RIG application (RIG synthesis, not corpus claims)

- At 2 subscribers and zero Notes, chat and solo lives are premature (L10, L11). The one move that works at this size is 3 to 7 recommendation partners at the same stage: small B2B AI-ops or operator newsletters, recommended first from RIG's side (L2, L3).
- Relationship before ask: comment substantively on a target writer's posts for a few weeks before any guest-post pitch (L7, L8). A cold pitch to an established pub has no barter value at 2 subscribers.
- One collaboration live with a peer pub is the highest-leverage single play: both audiences get notified, and the replay becomes a durable post on both publications (L5, L6). It also creates content RIG can clip back to LinkedIn.
- Keep routing LinkedIn attention (5,400 followers) into the Substack link via comments and profile, since LinkedIn suppresses external links in post bodies; the recommendation network is what compounds that attention into owned email after it lands.
- Skip Skool or Discord for now (contested, both sides above); RIG's community surface is the post comments plus one periodic live, and chat only once there is an active group to populate it.
- Report one network metric weekly: the recommendations dashboard (who recommends RIG and how many subscribers each sends), which is the honest leading indicator of network growth at this stage.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/recommendation-swaps.md` | choosing and writing recommendations |
| `references/collaborations.md` | guest posts, cross-posts and Lives |

## Hard rules

- Recommendations, guest posts, cross-posts, Lives and DMs are public or outward: Gate-D per item.
- Recommend only publications Mike would genuinely vouch for; the blurb is in his voice.
- No recommendation-for-recommendation spam asks in DMs.
- Never recommend or collaborate with a publication that would put a client's name or a minor in public.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-network/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-network` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
