---
name: ss-plan
description: >-
  Cadence and calendar for a Substack publication: publishing day, weekly baseline, batching, series formats, the free/paid rhythm and repurposing from LinkedIn. USE WHEN planning a Substack week or month, choosing a publishing day, or when the cadence has slipped. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, plan]
outcome: "content-publishing: a four-week Substack calendar with a fixed day, one issue per week, the Notes slots, and each issue tied to a pillar and a LinkedIn source"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-plan/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-plan
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "14"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-plan: cadence, calendar and batching

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this calendar realistic, which idea fills a slot, is the plan ready to execute. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check plan.readiness --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `plan.readiness` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use weekly (Friday) to fill the next four weeks, and whenever an issue is missed. Not for writing the issue itself (ss-write) or its title (ss-package).

## Procedure

1. **Fix the day and time**: one issue per week on the same day. Default for RIG: Tuesday morning Mountain time, matching the Tuesday LinkedIn rhythm, adjusted once Substack's reader-location stats exist.
2. **Fill four weeks**: each slot names the pillar, the working title, the LinkedIn post or RIG work it grows from, and its lead magnet if any.
3. **Source from LinkedIn first**: the week's strongest LinkedIn post (by its own analytics, read-only) becomes the next issue's seed. LinkedIn is the attention engine; the issue is the deeper version.
4. **Batch**: draft two issues and a week of Notes in one sitting; stage them in Substack as drafts or scheduled (scheduling a public send is Gate-D).
5. **Plan the Notes**: 3-5 Notes per issue cut from it, plus a daily engagement slot (see ss-notes).
6. **Free vs paid**: all-free until the list proves it opens and replies (RIG override of the corpus's one-free-one-paid baseline; see RIG application).
7. **Jev**: run the four-week plan through `plan.readiness`; fix or record DEFERRED.

## Hands the next stage

`calendar-<week>.md` with four issue slots and their Notes slots. ss-package takes each slot's working title; ss-write takes the source material.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-plan.md` (local corpus, not republished).

- L1. Commit to a publishing cadence you can hold every week for months; the consistency itself is what readers and clients pay for. CLAIM(DmcAI5D6r-s, Qk0zAlUdEcM, 5W0tys60VrI, 7gm0J-aiNbw) | channels: 4 | status: consensus
- L2. Start at one post per week as your baseline and only add volume after the rhythm is stable. CLAIM(bq3CeOWtg6M, qch_WGVO4uM) | channels: 2 | status: consensus
- L3. Pick a fixed day (and time) for publication so readers build the habit and you lose the weekly guesswork. CLAIM(Q_BzyGJTj-I, wEfZgaCq25w, gMOA9rMYSlo) | channels: 3 | status: consensus
- L4. Batch produce content in one weekly session and schedule it out, so publishing survives busy weeks. CLAIM(M7G5kXlIxo4, KkCwksLWBpA, mHRJfOWzdJQ, Jo9ZQPnFgLU) | channels: 4 | status: consensus
- L5. Choose a schedule that is sustainable for you; the daily-start-then-burnout pattern is the main reason people quit. CLAIM(bq3CeOWtg6M, uSFE4UMF5CU, nbVk3wKUs7A) | channels: 2 | status: consensus
- L6. Do not just publish: review what performs and iterate, because posting without feedback is running in place. CLAIM(_kjMG_D4oHg, fJkT_Jzb_tw) | channels: 1 | status: single-source
- L7. Pair every published note with an engagement routine: like about 10 notes, write about 5 real comments, start 1 conversation. CLAIM(_kjMG_D4oHg, M7G5kXlIxo4) | channels: 1 | status: single-source
- L8. Repurpose your best-performing material and your archive into new posts instead of always creating from zero. CLAIM(lGeLfsk9Sw4, SPUY_HOLAMM, rFeo2z46A-o) | channels: 3 | status: consensus
- L9. The baseline commercial model is one free issue plus one paid issue per week on one topic. CLAIM(Qk0zAlUdEcM, EAlOdXmIqcs, k3hbRtfpZ84) | channels: 2 | status: consensus
- L10. Match cadence to the reader's time investment: heavier issues earn a slower schedule, lighter issues can go faster. CLAIM(Qk0zAlUdEcM) | channels: 1 | status: single-source
- L11. Check your stats weekly, comparing week to week, never daily. CLAIM(E4KFHhiebCw) | channels: 1 | status: single-source
- L12. Give readers a recurring series or fixed format they can rely on week after week. CLAIM(ng4Km9cwT3I, U0IWoCaBw_o) | channels: 2 | status: consensus
- L13. Schedule sends for when your audience is waking up, using Substack's reader geography to pick the time. CLAIM(wEfZgaCq25w) | channels: 1 | status: single-source
- L14. When selling a newsletter service, sell the consistency you deliver, not promised metrics. CLAIM(7gm0J-aiNbw) | channels: 1 | status: single-source

## Where the creators disagree

Whether publishing frequency matters. The pro-frequency side says volume plus consistency builds the audience and readers judge reliability:
The depth-over-cadence side says frequency is not what retains readers, and that hard consistency claims are a made-up construct:

Whether Substack lets you schedule notes (a dated disagreement inside the corpus; the later claim supersedes the earlier one):

## Creator result claims (UNVERIFIED, never repeat as fact)

- [quote in corpus notes] (nNUmWbjAXPc, @nicolascole77) CLAIM(nNUmWbjAXPc) UNVERIFIED.
- [quote in corpus notes] (ng4Km9cwT3I, @nicolascole77) CLAIM(ng4Km9cwT3I) UNVERIFIED (creator describes another writer's results).
- [quote in corpus notes] (gfETuDIRyi8, @sutoscience) CLAIM(gfETuDIRyi8) UNVERIFIED.
- [quote in corpus notes] (EvLmKcE4mf4, @sutoscience) CLAIM(EvLmKcE4mf4) UNVERIFIED.
- [quote in corpus notes] (uAxVhzGEXD8, @nicolascole77) CLAIM(uAxVhzGEXD8) UNVERIFIED.

## Platform mechanics (Substack's own channel)

- Post formatting should be consistent issue to issue: [quote in corpus notes] (g2k6H0vkoa0). CLAIM(g2k6H0vkoa0).
- Pick a publishing schedule in advance and stick to fixed send times: [quote in corpus notes] (fFX6e2aX_68). CLAIM(fFX6e2aX_68).
- Paywall placement practice shown on the platform channel: [quote in corpus notes] (fFX6e2aX_68). CLAIM(fFX6e2aX_68).

## RIG application (RIG synthesis, not corpus claims)

(RIG synthesis, not corpus claims.)
- Hold one issue per week on a fixed day (recommend Tuesday), written from RIG work: one governed-AI teardown or build log per issue. One post a week beats an ambitious daily plan that dies in three weeks (L1, L2, L5).
- Batch four weeks of issues and notes ahead in one sitting and schedule them, so the job search and client work cannot break the cadence (L4).
- Deviate from the corpus baseline on paid: the corpus wants one free plus one paid issue per week, but with about 2 subscribers RIG should run all-free until the list proves retention, then add a paid tier around client-facing teardowns (L9, noted as RIG override).
- Repurpose deliberately: each LinkedIn post that draws attention becomes an issue, and each issue yields 3-5 notes, so LinkedIn attention is the traffic engine and the archive compounds (L8, L7).
- Skip daily stats checks and skip promised metrics in any client conversation; promise [quote in corpus notes] instead, because RIG's eventual product is a retainer built on visible consistency (L11, L14).

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/weekly-cadence.md` | setting the publishing day and the four-week calendar |
| `references/repurpose-ladder.md` | turning one LinkedIn post into an issue and its Notes |

## Hard rules

- One issue per week is the floor; do not plan daily issues. Daily volume belongs in Notes.
- Scheduling a send or a Note is a public action: staged here, confirmed by Mike.
- Never plan an issue about Jacob (Lane C); that lane is per-post approval and never auto-scheduled.
- A slot with no real source (story, build, receipt, client question) is left empty, not filled with a topic.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-plan/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-plan` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
