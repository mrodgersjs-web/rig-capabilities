---
name: sk-launch
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Validating a community idea with a tiny cohort before building anything heavy: the first 10-30 members, the enrollment conversation, and the kill/continue call. USE WHEN the idea is untested, when the first push to fill the room is due, or when growth has stalled at the start. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, launch]
outcome: "content-publishing: the idea survives or dies on evidence from a named tiny cohort, with the first 10-30 members inside and their first win recorded"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-launch/SKILL.md
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-launch
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "9"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-launch: validation, first members and the tiny test

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is the idea validated enough to build, is this member a fit, did the test pass or fail. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check idea.solid --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `idea.solid` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use before building the classroom, and whenever member count stalls under ~30. Not for ongoing growth (sk-growth) or content design (sk-content).

## Procedure

1. **Define the tiny test in writing** before inviting: how many members, over how many days, what counts as validation (for example: 10 members, 14 days, 5 of them complete one real workflow). A test without a written pass bar is a vibe.
2. **Recruit by conversation, not broadcast**: invite people Mike already knows have the bottleneck; the corpus favors direct conversations and problem interviews over open links at this stage.
3. **Interview every first-wave member** within 48 hours of joining: what bottleneck did they bring, what would make this worth paying for. Record answers verbatim; they are the content plan.
4. **Deliver one win manually** before automating anything: run one member's workflow through the lab's method (owner, sources, gates, approval boundary, ProofPacket) yourself.
5. **Make the kill/continue call at the deadline** against the written bar. If it fails: change the promise or the member, not the volume.
6. Hand to sk-content with the interview answers as the curriculum seed.

## Hands the next stage

`launch-record.md`: cohort roster, the written pass bar, interview answers verbatim, the win delivered, and the kill/continue call. sk-content builds the classroom from the interview answers.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-launch.md` (local corpus, not republished).

- L9. Don't attempt organic validation of a community idea: warm traffic lies (people join to support you), you're too early to rank in discovery, and a zero-member community makes cold prospects afraid to join — budget $50 for ads instead ($25 if the community is free) CLAIM(fXiFlwKvB3U@27:12)
- L10. The validation ad recipe: your actual community cover image as the ad image, your about-page copy as the ad copy, CTA [quote in corpus notes]; optimize for complete registration on a free community, for purchases on a paid one; targeting wide open to tier-1 countries (US, Canada, Australia, UK, Germany plus the large EU markets) CLAIM(fXiFlwKvB3U@28:39)
- L11. Hard validation thresholds: complete registration under $2 on a $20-25 spend (free community), or at least 1-2 sales from the sales campaign (paid community) = idea validated; otherwise read the funnel (clicks vs joins), revise the hypothesis, and ask in Schoolers or peer communities what the ad failed to say CLAIM(fXiFlwKvB3U@29:42)
- L12. Price a first paid community at $7-$10 maximum; if you have no audience, launch free, validate, and only then convert it to paid CLAIM(fXiFlwKvB3U@28:21)
- L13. Launch with the minimum viable setup ("a western town"): banner, icon, about copy, a few calls on the calendar, one welcome post — then run one themed call/workshop in the shared direction; the members' actual problems named on that call are what you build the classroom from CLAIM(fXiFlwKvB3U@26:02)
- L14. Small Meta budgets get a built-in leg up (new advertisers are cheaply put in front of the right people), so if a $50 test cannot produce registrations or sales, your audience/positioning is too unclear for Meta's AI — and if it is too complicated for Meta it is too complicated for a human; simplify and re-test rather than scale CLAIM(fXiFlwKvB3U@32:17)
- L15. Keep pre-build disposable: one 60-minute workshop you can cut into pieces, or a single YouTube video for immediate consumption, is acceptable — but only if you can abandon the sunk effort; if putting work in means you will never kill it, build nothing before validation CLAIM(fXiFlwKvB3U@34:39)
- L16. Because validation comes before content, a failed idea is cheap to restart — swapping the cover picture and copy takes half an hour, versus months lost building coursework with no product-market fit CLAIM(fXiFlwKvB3U@33:14)
- L17. First members target: 3-10 genuinely valuable members (Sam Ovens' [quote in corpus notes]), and momentum builds from that base rather than from a launch spike CLAIM(fXiFlwKvB3U@41:20)

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
| `references/tiny-test-design.md` | designing the validation test with a written pass bar |

## Hard rules

- No paid ads in the tiny test (sk-ads waits until the promise converts organically).
- Interview answers are member material: never republish them without the member's yes.
- A failed test is recorded as failed. Do not redefine the pass bar after the deadline.
- Gate-D before any public post, invite blast or price change.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-launch/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-launch` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
