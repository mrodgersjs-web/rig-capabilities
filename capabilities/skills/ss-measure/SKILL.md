---
name: ss-measure
description: >-
  Measurement for a Substack publication: the weekly stats read, Growth-page sources, per-post and per-Note numbers, and turning each number into one action. USE WHEN asked how the Substack is doing, after every issue, or before planning the next month. JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of ss-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [substack, ss-growth-os, measure]
outcome: "content-publishing: a weekly scoreboard with subscribers by source, opens, and the one action each number triggers"
done_when:
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-measure/SKILL.md
  - cmd:python3 capabilities/skills/ss-growth-os/scripts/check_family.py ss-measure
quality_floor: 0.6
metadata:
  parent: "ss-growth-os"
  laws: "12"
  corpus: "data/corpora/substack (914 transcripts, 27 channels)"
---

# ss-measure: stats, attribution and the weekly review

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `ss-growth-os`, which `when-growing-social-accounts` routes every Substack job through. An agent meets it before any stage work.

Typed judgments this stage forces: is a metric movement real, what caused a flop, which channel earns more effort. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check signal.performance --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `signal.performance` is advisory until calibrated. Substack-specific rubrics `substack.issue` and `substack.note` exist since 2026-09-28 (planted-fixture separation proven, decisions 125944-125948); stages without a Substack rubric use the nearest existing one.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, send, restack, recommend or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use weekly (Friday, before ss-plan) and 7 days after each issue. Not for LinkedIn analytics (lv-measure), though the two scoreboards are read together.

## Procedure

1. **Read weekly, not daily**: Stats > Posts, Growth (sources), Notes, Recommendations.
2. **Log per issue**: views, open rate, new free and paid subscribers, top traffic sources, link clicks on the next step.
3. **Attribute**: Growth-page sources plus the utm values from ss-distribute. A channel that sends nothing for four weeks loses effort.
4. **Wire each number to an action**: low open rate -> ss-package retest; visitors without subscriptions -> ss-strategy (positioning); Notes followers without subscribers -> ss-notes format change.
5. **Jev** `signal.performance` on whether a movement is real before acting on it.
6. File the scoreboard on the Kanban `funnel` stream.

## Hands the next stage

`scoreboard-<week>.md` with actions. ss-plan reads it before filling the next four weeks.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the transcripts that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/substack/notes/ss-measure.md` (local corpus, not republished).

- L1. Review stats on a weekly or monthly cadence and compare like periods; never check hourly or daily. CLAIM(E4KFHhiebCw, 19AvFfwfhfc, 0f89F3a4iqE) | channels: 3 | status: consensus
- L2. Judge content by the action after the click (subscribe, reply, buy, book), not by views or opens. CLAIM(8FE7TlxBQkk, EAlOdXmIqcs, W3jen6QERo8) | channels: 3 | status: consensus
- L3. Treat open rate as a directional health trend only; never cut sends or rewrite strategy just to protect it. CLAIM(HacRdXOMZSM, xZtrPtlccBE, htAB9udet5M) | channels: 3 | status: consensus
- L4. Track money per subscriber per month as the real health number; $1 per subscriber per month is the floor worth acting on. CLAIM(HacRdXOMZSM, fAEjwwrZ8G0) | channels: 2 | status: consensus
- L5. Measure churn and retention as hard as acquisition, and watch the first six weeks, where most readers tune out. CLAIM(9wvKnQimriw, MxtuZ85iuX0, Ac_d2OfdmkA) | channels: 2 | status: consensus
- L6. Move paid members onto annual plans on purpose; monthly billing churn is the default you have to design against. CLAIM(LQuHHhnEkC8, GmCffJgypv0) | channels: 2 | status: consensus
- L7. Attribute every subscriber to the article, note, or channel that produced it, and track who actually buys downstream. CLAIM(dBlSgcbHcug, CxiUvgeAGqs, vaDQnuO_eik) | channels: 3 | status: consensus
- L8. Run constant small tests and iterate on what the data rewards: A/B subject lines, keep winning formats, retire losers. CLAIM(CkhTN-4aWRU, _kjMG_D4oHg, ia7UNPjWpZY, ERparntjM7c) | channels: 4 | status: consensus
- L9. Learn the dashboard surfaces and use them on purpose: growth tab for subscriber sources, per-post engagement stats, note-level stats. CLAIM(gc3DrMOrcrk, EteGEtqvAvk) | channels: 2 | status: consensus
- L10. Export your data on a weekly rhythm and keep a copy off-platform so your list survives any platform move. CLAIM(0f89F3a4iqE, EteGEtqvAvk, qpDkbTeAHIY) | channels: 3 | status: consensus
- L11. Plug Substack into Google Analytics or Search Console; the native traffic-source view is not the accurate one. CLAIM(3HUkQ3YX0NM, P6GKLhxBRy0) | channels: 2 | status: consensus
- L12. Ignore the net subscriber counter and measure inflow plus per-piece gains and losses; net hides the truth. CLAIM(ARL-WAi-0to, ERparntjM7c) | channels: 2 | status: consensus

## Where the creators disagree

Open rate as a decision number. Side A, ignore it: [quote in corpus notes] (HacRdXOMZSM, @mattgiaro) and [quote in corpus notes] (xZtrPtlccBE, @substackgrowth). Side B, benchmark it: [quote in corpus notes] (EAlOdXmIqcs, @nicolascole77), and Substack's own guidance: [quote in corpus notes] (xsQtpZP9Ujs, @substackinc). All sides agree the number is imperfect; they disagree on whether it should set strategy.
Stat-check cadence. Side A, weekly or slower: [quote in corpus notes] (E4KFHhiebCw, @MarkJThompson). Side B, daily tracking by a deliberate operator: [quote in corpus notes] (VyFSck568MI, @mattgiaro). The difference is intent: daily tracking to record vs daily checking to feel better.

## Creator result claims (UNVERIFIED, never repeat as fact)

- 27% open rate against an 18.88% real estate industry average. CLAIM(EUughLjsbL8, @Loriballen) UNVERIFIED.
- 38.97% open rate on a 5,676-recipient send, with about 1% click-through. CLAIM(U61eyvw_lp8, @Loriballen) UNVERIFIED.
- Same audience opens at 21-23% on Gumroad and 40% on Kit. CLAIM(gPVfLaswtSk, @MarkJThompson) UNVERIFIED.
- Sends daily email to over 10,000 subscribers. CLAIM(HacRdXOMZSM, @mattgiaro) UNVERIFIED.
- Open rate raised from 5% to 50%; welcome sequence averages 64.7% open and 16.5% click. CLAIM(htAB9udet5M, @mattgiaro) UNVERIFIED.
- First 100 paid subscribers within weeks, over 600 paid today. CLAIM(9wvKnQimriw, @sinemgunel) UNVERIFIED.
- $5,000 in a month on Substack, retaining 70-75% of readers after a year. CLAIM(U9_tgwqwxsg, @substackgrowth) UNVERIFIED.
- $20,000 ARR in just over a year; Substack, LinkedIn and Google are the top paid-subscription sources. CLAIM(vaDQnuO_eik, @substackgrowth) UNVERIFIED.
- Gains 1,000 new subscribers a month and loses 1,000. CLAIM(ARL-WAi-0to, @sutoscience) UNVERIFIED.
- Collective Substack grown past $200,000 ARR. CLAIM(CkhTN-4aWRU, @sutoscience) UNVERIFIED.
- About 10% of monthly-billed subscribers unsubscribe after one month. CLAIM(GmCffJgypv0, @substackinc) UNVERIFIED.
- $0 to $96,000 ARR by months 10 and 11. CLAIM(SH_cX2PFnI4, @sutoscience) UNVERIFIED.

## Platform mechanics (Substack's own channel)

- The dashboard shows a per-post open rate, and Substack treats it as a proxy for reader engagement; guidance is to be at roughly 30% or above before turning on paid, and above 50% you might see 6 to 10% of readers go paid. CLAIM(xsQtpZP9Ujs)
- Every collaborator gets analytics on the posts they publish; a recording studio session stays private, and stats appear once the recording is published. CLAIM(6nT6G_do-6c)
- The dashboard gives post-level performance insight, with deeper data available on each post. CLAIM(bTdUaD3dZ9E)
- Monthly billing reminders after signup drive churn; an annual discount avoids that monthly churn moment. CLAIM(GmCffJgypv0)

## RIG application (RIG synthesis, not corpus claims)

- At 2 subscribers, open rate and retention math are noise. The only numbers worth acting on now are source attribution (which LinkedIn post or comment drove a signup) and the action after the click (reply, booked call, client conversation). That is Law 2 and Law 7 applied to a tiny list.
- Put a weekly stat review on the calendar from day one: growth tab for new-subscriber sources, per-post engagement stats, one exported zip off-platform. Never a daily dashboard check, since a 2-subscriber list makes every fluctuation meaningless.
- Use Substack Notes as the free testing ground for post ideas before committing long-form effort, and A/B subject lines on every send once there is any list to test on. Each send is the cheapest experiment surface RIG has.
- The money number for RIG is not subscription revenue and not $1 per head. It is clicks through to rodgersintelligence.com and booked discovery calls per post, so wire UTM'd links and count conversions, not opens.
- Design the welcome email and the source-tagged signup path now, even at zero scale, because first-six-week retention is where later churn is won. Annual-plan and paid-tier mechanics stay parked until the list exists.
- Connect Google Search Console and Analytics before publishing cadence grows, and hide the vanity subscriber counter on the dashboard so it cannot drive decisions.

## Sub-skills (load at most one)

| File | Use for |
|---|---|
| `references/weekly-scoreboard.md` | the Friday stats read |
| `references/flop-diagnosis.md` | diagnosing an issue that underperformed |

## Hard rules

- A number without an action is a dashboard; every row names what changes.
- Read stats from Substack's own pages; never quote a remembered figure.
- With single-digit subscribers, percentages are noise: report counts.
- Activity (posts made, notes sent) is input, never a result.

## Done-test

`python3 capabilities/skills/ss-growth-os/scripts/claims_check.py capabilities/skills/ss-measure/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py ss-measure` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
