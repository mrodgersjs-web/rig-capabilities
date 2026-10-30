---
name: sk-ops
description: >-
  JEV-FIRST MANDATE, findable at task start: every typed judgment in this stage goes to rig-s1gate (Jev) BEFORE any frontier LLM call, and DEFERRED is the only answer when the classifier is down. The operating layer: what runs the community day to day, what to automate (and what never to), the routine inventory, the local-first tooling stance, and the time budget of the owner. USE WHEN standing up automation for the community, when the weekly workload is unsustainable, or when auditing what is actually running. Child of skool-growth-os.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [skool, skool-growth-os, ops]
outcome: "content-publishing: a named operating rhythm where every automation has a fail-loud guard, an owner, and a proven run, and the owner's weekly time in the room is stated and bounded"
done_when:
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-ops/SKILL.md
  - cmd:python3 capabilities/skills/skool-growth-os/scripts/check_family.py sk-ops
quality_floor: 0.6
metadata:
  parent: "skool-growth-os"
  laws: "3"
  corpus: "data/corpora/skool (1,405 videos enumerated across 10 channels; transcripts captured incrementally)"
---

# sk-ops: running the room: systems, automations and time

## JEV-first mandate (read first)

Where this rule lives: it is in this stage's description (loaded at session start by every harness), in the always-loaded `~/.aside/u/0/AGENTS.md` ("JEV before done"), and in the front door `skool-growth-os`, which `when-growing-social-accounts` routes every Skool job through. An agent meets it before any stage work.

Typed judgments this stage forces: is this automation safe to run unattended, is this routine actually running, is this process worth its time. Each goes to Jev (TypeSafe System One) through `rig-s1gate` BEFORE any frontier LLM call.

- Command: `~/.rig/bin/rig-s1gate check plan.readiness --file <artifact> --subject "<kind> <artifact-id> sha256:<hash>" --json`. `plan.readiness` is advisory until calibrated; no Skool-specific rubric exists yet.
- A pass needs every required noul and confidence above 0.9. Exactly 0.90 does not pass.
- Fail closed: classifier down, erroring or rubric missing means DEFERRED. DEFERRED is never a pass and never a guess.
- An advisory PASS is not permission to publish, post, invite, advertise or spend. Gate-D still applies.
- Any claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

## When to use / when not to

Use after the room has real members and real rhythms to automate. Not for content or growth design.

## Procedure

1. **Automate the repeatable interior, never the outward act**: welcome sequences, weekly prompt scheduling, metrics collection, and scout runs are automatable; posting publicly, pricing changes, and member conversations with weight stay human (Gate-D).
2. **Fail-loud guard on every routine**: a scheduled job that cannot do its work emits one explicit `BLOCKED:` line and stops; a clean run with zero output is indistinguishable from success otherwise. Verify produced counts from the source of truth.
3. **Proven run, not a live definition**: a routine counts as running only when a run reached `completed` with an artifact. (RIG's measured lesson: scheduled, full-access routines sat suspended on approval gates for weeks while their definitions claimed schedules.)
4. **Local-first with a named fallback** (Mike's standing model policy): community automations route to a dependable local model first; any paid route carries a fallback procedure, since a settings lane holds exactly one model.
5. **Time budget**: state the owner's weekly hours in the room (onboarding, prompts, live touch) and hold it; a community that needs 20 unlisted hours a week is a job, not an asset.
6. **Inventory audit**: before adding any tool, check what already covers the ground; no second system for the same job.

## Hands the next stage

`ops-map.md`: the routine inventory (name, schedule, model lane, guard, last proven run), the automation boundary table (automate / human / Gate-D), and the weekly time budget.

## Laws (corpus doctrine, cite by id)

Each law is a paraphrase with the videos that carry it. `consensus` = two or more channels; `single-source` = one channel, treat as a hypothesis to test, not a rule. Verbatim quotes for every law are in `data/corpora/skool/notes/sk-ops.md` (local corpus, not republished).

- L40. All-in-one beats the stitched stack: the pre-Skool operating cost was VAs, failed Zaps, and Facebook groups where you could no longer tell who had paid — consolidation of community + classroom + payments + reach is the structural reason creators move CLAIM(fXiFlwKvB3U@8:33)
- L41. Community quality cannot be manufactured alone at a desk: budget the weekly live touch (themed calls, welcomes, intros, documented work) as the core operating job, and accept that hosting discomfort is the work itself CLAIM(fXiFlwKvB3U@39:08)
- L42. Migrating an audience is a real bet worth making when the platform is clearly better: she abandoned a 25,000-member Discord, publicly told her existing audience to follow her to Skool, took the backlash, and most eventually followed — protecting years of work meant bringing it into the future CLAIM(fXiFlwKvB3U@9:07)

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
| `references/routine-inventory.md` | auditing what is actually running |

## Hard rules

- Nothing outward runs unattended without a Gate-D-approved boundary; the approval names the action and the target.
- A routine without a proven `completed` run is reported as not running, however live its definition looks.
- Never print or store raw secrets; reference keychain item names (`com.rig.env.*`).
- Deleting or pausing a working routine is reversible but named to Mike first.

## Done-test

`python3 capabilities/skills/skool-growth-os/scripts/claims_check.py capabilities/skills/sk-ops/SKILL.md` is GREEN only when every CLAIM id resolves to a captured transcript. `check_family.py sk-ops` is GREEN only when the JEV section opens the body, every sub-skill file exists and is over 400 bytes, and no 12-word run of any transcript appears in the stage.
