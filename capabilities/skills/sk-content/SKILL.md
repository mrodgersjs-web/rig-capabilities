---
name: sk-content
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Designing the classroom and the weekly value loop: what to teach, in what format, how the community's own work becomes content, and the lessons-learned pipeline. USE WHEN the classroom is empty or stale, when content is being planned, or when community work should become reusable lessons. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, content]
outcome: "content-publishing: the classroom has a named path (first win -> core method -> advanced), a weekly value rhythm, and a working pipeline from community work to reusable lessons"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-content/SKILL.md
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-content
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "4"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-content: classroom design and the value delivery engine

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: does this content earn a classroom slot, is the format right, is this lesson publishable. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check post.viral --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `post.viral` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after the tiny test, before promising any curriculum, and whenever classroom usage drops. Not for member engagement mechanics (sk-engagement) or the publish gate (sk-gate).

## Procedure

1. **Build backward from the first win**: the first classroom item must deliver the outcome the promise names, inside the first session. Everything else waits.
2. **Community-first content**: every real workflow the lab runs for a member becomes a de-identified classroom case (owner, sources, gates, approval boundary, ProofPacket shape). The byproduct model beats planned curriculum (corpus consensus).
3. **Format rules from the corpus**: short screenshotted walkthroughs over long lectures; one concept per item; checklists and templates over theory; each item ends with the member's next action.
4. **The lessons-learned pipeline** (sk-lessons owns the harvest; this stage owns placement): every published lesson gets a slot in the classroom's "Lessons Learned" section, dated, with the trap and the rule.
5. **Cadence**: one new classroom item per week maximum; stale-and-correct beats thin-and-often.
6. **Jev**: screen each item with `post.viral` before it enters the classroom.

## Hands the next stage

`classroom-plan.md`: the path (first win -> core -> advanced), the weekly rhythm, the de-identified case pipeline, and the Lessons Learned section layout. sk-gate screens items before they go live.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-content.md` (local corpus, not republished).

- L18. Generate classroom content as the collected byproduct of solving member problems live (recordings, resources produced in real work), never as coursework authored alone at your desk — emergent quality cannot be manufactured solo CLAIM(fXiFlwKvB3U@0:52)
- L19. Document your own journey in a productized form — attempts, failures, numbers, what you tried this week — because watching you go through the experience before they have is among the most engaging content there is (people are nosy) CLAIM(fXiFlwKvB3U@20:45)
- L20. [quote in corpus notes]: don't stand at the bottom shouting that it's safe — do the thing yourself in front of them, experience it with them, and show even the small hurts ([quote in corpus notes]); that removes the experiential burden and gives members permission to act CLAIM(fXiFlwKvB3U@21:02)
- L21. Deliver value through themed calls and workshops tied to the declared shared goal, then let those live sessions convert into classroom material incrementally as you learn what members actually need CLAIM(fXiFlwKvB3U@26:20)

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
| `references/lesson-pipeline.md` | turning community work into reusable lessons |

## Hard rules

- De-identify every member case: no names, no company names, no raw numbers without permission.
- No verbatim transcript text from the corpus in classroom items; paraphrase and cite the video id.
- Every classroom claim of result is labeled: member-observed, RIG-internal, or creator self-report (UNVERIFIED).
- The classroom is public surface: adding items is reversible, but any item naming a client or a price goes through Gate-D.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-content/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-content` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
