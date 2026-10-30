---
name: ss-distribute
description: >-
  Off-platform distribution for Substack issues: LinkedIn route-back, X, email signature, the RIG site and other channels, each with its own link rules. USE WHEN an issue is published and must be amplified, or when the Growth page shows almost no outside traffic. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, distribute]
outcome: "content-publishing: every issue gets a per-channel amplification set (LinkedIn first comment, X post, Note), each adapted and route-back compliant, with a distinct utm per channel"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-distribute/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-distribute
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "14"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-distribute: driving readers in from LinkedIn, X and beyond

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: which channel fits this issue, is each adapted version good enough, is the route-back compliant. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check post.viral --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `post.viral` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after ss-publish on every issue, and to re-amplify the archive. Coordinates with `lv-distribute` (LinkedIn side). Not for Substack-internal discovery (ss-notes, ss-network).

## Procedure

1. **LinkedIn first** (Mike's 5,400-follower channel): a native post carrying the issue's hook and one idea; the Substack link goes in the first comment, never the post body. Eden drafts LinkedIn copy.
2. **X**: one post with the hook and the link (X allows links in the post; 280 characters unless Premium is confirmed on @RodgersRIG).
3. **Substack Note** restack (ss-notes).
4. **Owned surfaces**: the Substack link in Mike's email signature, the LinkedIn Featured section, and a subscribe embed on rodgersintelligence.com (site change is Gate-D and goes through the website release process).
5. **Tag every link** with a distinct `utm_source` (linkedin, x, site, email) so the Growth page attributes it.
6. **Gate** the set in ss-gate; Gate-D itemized; pace one issue's set per day, never a burst across the archive.

## Hands the next stage

`amplify-<slug>.md`: the per-channel texts, links and utm values, gate verdicts. ss-measure reads the Growth page for them 7 days later.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-distribute.md` (local corpus, not republished).

- L1. Send every off-platform channel to one home base where you capture the email address, never to a destination that pays someone else. CLAIM(lXC52aR6NFM, GtRUXjbI2WQ, tggaKz5jrGo, Qk0zAlUdEcM) | channels: 4 | status: consensus
- L2. Assume the platform throttles external links: give the native post full value on its own and put the link in a reply, bio, or profile slot. CLAIM(n36h4t-8EYU, jXHsvsPz1dQ, VRlix-8tXtM, D8JIHJvpmSw) | channels: 3 | status: consensus
- L3. Treat the email list as the only owned asset; followers on any platform are rented reach you can lose overnight. CLAIM(AdLLOjrToC4, O26k2E71oIE, vaDQnuO_eik, SKrjde_Hs-E, byrTbfpVURk) | channels: 3 | status: consensus
- L4. Spend original energy only on platforms that deepen a relationship or lead to revenue, and pick the platform where your specific audience already lives. CLAIM(A8HHa29PDGo, ia7UNPjWpZY, CkhTN-4aWRU, c8dslu2PbaE) | channels: 4 | status: consensus
- L5. Make one core piece of content and cut it into many platform assets instead of authoring each post from scratch. CLAIM(1sjsp4xVTAA, -WyMIQEteRk, 4kcYqHbmJa8, vWmOfFNh0pg) | channels: 3 | status: consensus
- L6. Repackage natively per platform: split long form into several short pieces and match content type to the platform's consumption style. CLAIM(vWmOfFNh0pg, gc3DrMOrcrk, OPc1JY1fQzI, 4kcYqHbmJa8) | channels: 3 | status: consensus
- L7. Put the subscribe link in every piece of real estate you control: bio, channel description, email signature, pinned post, link-in-bio page. CLAIM(VjrgK8Ah8A0, TAqEplyhREw, nBK5uL4GGZ4, Be3px_oTo1s) | channels: 3 | status: consensus
- L8. Use search-driven channels (YouTube, Pinterest) for compounding discovery and social channels for community and conversation; write for each accordingly. CLAIM(SPUY_HOLAMM, A8HHa29PDGo, c8dslu2PbaE, urq6xcFtxhg, 7eHV_uw-c28) | channels: 3 | status: consensus
- L9. Let free platforms supply traffic and monetize the list on the back end; platform payouts and ads are the weakest income path. CLAIM(cQl88Ga2WTk, tggaKz5jrGo, nBK5uL4GGZ4, Qk0zAlUdEcM) | channels: 3 | status: consensus
- L10. Bridge social attention to the list with a freebie or email course advertised in the bio, not with a bare subscribe link. CLAIM(nBK5uL4GGZ4, GtRUXjbI2WQ, Qk0zAlUdEcM) | channels: 3 | status: consensus
- L11. Show up consistently on the chosen channels and expect months without traffic before distribution compounds; publishing cadence beats occasional brilliance. CLAIM(EClMOpqWTgg, n36h4t-8EYU, G3kol7GZ70w, gfETuDIRyi8) | channels: 4 | status: consensus
- L12. Diversify lead funnels across several sites and back up the list, because no single platform's algorithm is a safe foundation. CLAIM(vaDQnuO_eik, AdLLOjrToC4, Nyl4JGRNjoQ, C4IO3Yd4t4c) | channels: 3 | status: consensus
- L13. For B2B or professional audiences, LinkedIn is the highest-converting source channel for paid subscribers despite its reputation. CLAIM(pt8X9etCd48, SmewncRQDeo, CkhTN-4aWRU, 04CO6ImZLaY) | channels: 3 | status: consensus
- L14. Cross-post video to YouTube under the same name as the publication for free reach, accepting slightly fewer views than native uploads. CLAIM(wEcOTy2gKcA, 3uMOaySeafs, urq6xcFtxhg, As2CPh3N1dM) | channels: 4 | status: consensus

## Where the creators disagree

X/Twitter as a traffic source worth investing in. For: @nicolascole77 prioritizes it deliberately. CLAIM(Qk0zAlUdEcM)
For: @substackgrowth ranks it first among social channels. CLAIM(Jki9RboayGk)
Against: @sutoscience quit over Substack-link deprioritization. CLAIM(D8JIHJvpmSw)
Against: @substackgrowth also walked away after an unexplained ban (same channel as the pro side). CLAIM(VRlix-8tXtM)

Whether to promote a Substack on external social at all. Against: @sinemgunel argues the same effort grows faster inside Substack. CLAIM(Y3G8NrvlcE8)
For: @soloshannonhq's second biggest traffic source is YouTube referrals. CLAIM(As2CPh3N1dM)
For: @creativelyconsciousUK saw Pinterest move the needle when other platforms did not. CLAIM(eXB_qIgazqw)

Whether Instagram/Facebook are worth keeping. Valuable: @creativelyconsciousUK's guest credits both for growth and for reaching people who will never join Substack. CLAIM(AslL2PK7MFk)
Quitting: @sutoscience reports many creators leaving Instagram entirely, though she personally keeps it as a nurture channel. CLAIM(OgUDJFzvhic)

Posting volume on social. High volume: @nicolascole77 publishes many times daily per platform. CLAIM(EClMOpqWTgg)
Paced: @TheCoachsAlchemist warns against flooding the feed and schedules cross-posted clips to spread out. CLAIM(urq6xcFtxhg)

## Creator result claims (UNVERIFIED, never repeat as fact)

[quote in corpus notes] (-s9dWPYSpAg, @Loriballen) UNVERIFIED
Traffic mix roughly Substack app 66%, Facebook/Instagram promotion 12%, YouTube 5.34% after starting to promote there. CLAIM(mHRJfOWzdJQ, @Loriballen) UNVERIFIED
[quote in corpus notes] (G3kol7GZ70w, @MarkJThompson) UNVERIFIED
Article traffic "7,000 views" with [quote in corpus notes]. CLAIM(Nyl4JGRNjoQ, @MarkJThompson) UNVERIFIED
[quote in corpus notes] while under 10% of direct income does. CLAIM(cQl88Ga2WTk, @MarkJThompson) UNVERIFIED
[quote in corpus notes] while most posts get 2,000 to 10,000 views. CLAIM(EClMOpqWTgg, @nicolascole77) UNVERIFIED
Warm-traffic landing page opt-in "as high as 65 70%" versus 30% for cold traffic. CLAIM(7gm0J-aiNbw, @nicolascole77) UNVERIFIED
Title claims a [quote in corpus notes] (Qk0zAlUdEcM, @nicolascole77) UNVERIFIED
[quote in corpus notes] (VRlix-8tXtM, @substackgrowth) UNVERIFIED
Title claims [quote in corpus notes] (VRlix-8tXtM, @substackgrowth) and [quote in corpus notes] (vaDQnuO_eik, @substackgrowth) UNVERIFIED
[quote in corpus notes] (VRlix-8tXtM, @substackgrowth) UNVERIFIED (note: "substance" is a caption error for Substack)
LinkedIn optimization [quote in corpus notes]. CLAIM(CkhTN-4aWRU, @sutoscience) UNVERIFIED
Titles claim [quote in corpus notes] (D8JIHJvpmSw, OgUDJFzvhic, @sutoscience) UNVERIFIED
[quote in corpus notes] (As2CPh3N1dM, @soloshannonhq) UNVERIFIED
Titles claim [quote in corpus notes] (5nDpH83b3XY, @soloshannonhq) and [quote in corpus notes] (NVkYVBemiac, @soloshannonhq) UNVERIFIED

## Platform mechanics (Substack's own channel)

Recordings can auto-upload to a connected YouTube account, and clips can auto-publish to YouTube Shorts and LinkedIn. CLAIM(6nT6G_do-6c)
Clips shared to other platforms by the host and co-hosts are a named growth lever. CLAIM(6nT6G_do-6c)
Each post shows a social preview before sending, and after publishing offers share buttons for Facebook and Twitter plus copy-link. CLAIM(kjc7GFFnkU4)
Paid posts can be teased on social with summary threads or screenshots to reach non-subscribers. CLAIM(qoif4TP0mLM)
Put your Substack link in your bio on every platform, and link back to other profiles from the Substack navbar. CLAIM(bTdUaD3dZ9E)
Put the Substack URL in your Twitter profile and pin a post at the top of the profile. CLAIM(FWJlc1alurM)
A paid launch should be promoted everywhere, because social algorithms do not reliably show your announcement to your own followers. CLAIM(9qBLzYI4oX8)
Local publishers can post articles into relevant community Facebook groups for immediate feedback and reach. CLAIM(Eucsl6CvfH4)
Open-ended questions drive the most engagement on discussion threads. CLAIM(fFX6e2aX_68)

## RIG application (RIG synthesis, not corpus claims)

- LinkedIn is Mike's only real distribution asset (about 5,400 followers) and the corpus says LinkedIn converts B2B traffic well (L13) while suppressing external links (L2). So write the full value natively in the LinkedIn post, keep the Substack URL out of the body (first comment or profile slot), and end every post at the same subscribe destination.
- rigoperator.substack.com is the home base that captures email (L1, L3). Before more posts, wire the capture everywhere: LinkedIn profile/featured link, X bio, YouTube channel description first link, email signature, and one freebie (a governed-AI checklist or self-assessment) as the bio bridge (L7, L10).
- One essay a week becomes one native LinkedIn post, a reshaped X thread, two or three Notes, and only if video exists a Substack video cross-posted to YouTube under the same name (L5, L6, L14). Do not build a Pinterest or Instagram engine first: L4 says pick where the audience lives, and B2B AI-ops buyers are not the Pinterest/BookTok lanes the corpus wins with.
- With one X follower, expect no X traffic for months (L11) and treat X as link-in-bio real estate plus occasional reposts. The tech-lead channels the corpus names beyond LinkedIn are Reddit and Hacker News (L12): occasional genuinely useful comments, never link-dropped spam.
- Nothing is measured yet. Substack analytics shows a traffic-source panel (CLAIM(mHRJfOWzdJQ)), so record [quote in corpus notes] weekly and apply the corpus rule of giving original energy only to channels that produce subscribers or conversations (L4). If after 8 to 12 weeks a channel shows zero converted subscribers, cut it rather than defending it.
- Keep the owned-asset discipline in RIG terms: the email list is the deliverable, LinkedIn is the rented distribution channel, and Substack posts are the durable asset both point at. This matches Mike's standing preference for durable artifacts over single-use output.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/linkedin-route-back.md` | moving LinkedIn attention to the Substack |
| `references/x-and-owned.md` | X posts, email signature and the RIG site |
| `references/archive-reamplify.md` | re-sharing the back catalogue |

## Hard rules

- Every outward post is Gate-D, itemized by channel.
- No raw Substack link in a LinkedIn post body; first comment only (LinkedIn suppresses external links).
- Adapt, never paste: near-identical text on two channels within 48 hours is a delivery failure.
- X writes go only to @RodgersRIG; assert the signed-in handle first (the browser's X session can be a minor's account).
- Conflict logged: `lv-distribute` says Substack is a weekly digest "never per post". This family treats each issue as a native Substack post and uses the digest rule only for LinkedIn-to-Substack roundups. Mike decides which rule wins.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-distribute/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-distribute` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
