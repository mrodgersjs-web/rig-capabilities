---
name: lv-plan
description: >-
  Sourcing ideas and facts, idea engines, the weekly and monthly calendar, cadence and funnel mix,
  and the lane runners for Mike Rodgers' LinkedIn estate: claim-ledger discipline, the content
  matrix, the collision engine, the trend pipeline, the Clark 2026 cadence rules, and how each lane
  runner (Lane A weekly rhythm, Lane B daily post, Ideawake client weekly, Alfred planner crons, the
  P1 content cycle) calls this stage. Use when asked "plan my week", "what should I post this week",
  "give me post ideas", "fill the calendar", or "what is the cadence". JEV-FIRST MANDATE, findable
  at task start: every typed judgment in this stage (idea selection, slot assignment, cadence
  adequacy, trend-claim triage, runner brief completeness) goes to rig-s1gate (Jev) BEFORE any
  frontier LLM call, and DEFERRED is the only answer when the classifier is down. Child of
  linkedin-viral.
owner: rig-intelligence
domain: Communications
status: Stable
acl: internal
tags: [linkedin, linkedin-viral, planning, calendar, ideas]
outcome: "content-publishing: every week is a dated slate of 3-5 slots whose ideas carry receipts, jobs and formats, written to the board Mike already uses and handed to the lane runners as briefs"
done_when:
  - cmd:python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-plan
quality_floor: 0.6
metadata:
  parent: linkedin-viral
  absorbed: "14"
---

# lv-plan: sourcing, ideas, calendar, cadence, runners

## JEV-first mandate (read first)

Every typed judgment this stage forces goes to Jev through rig-s1gate BEFORE any frontier LLM call:
which idea wins a slot, which slot a post takes, whether a week's slate is strong enough to ship,
whether a trend claim is real enough to plan on, and whether a runner brief is complete.
Command: `rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
Stored rubrics: `post.linkedin` (Lane B), `post.viral`, `post.eden`, `comment.linkedin`, `doctrine.surface`.
A ranking of idea candidates may use `post.viral`; everything else here usually has no stored
rubric, and the verdict is then DEFERRED to Mike. Fail closed: classifier down, erroring, or rubric
missing means DEFERRED, never a pass and never a local guess. An advisory PASS is not permission to
publish, schedule live or spend; Gate-D still applies. A "Jev judged X" claim cites the decision id.

## When to use / when not to

Use when sourcing ideas or facts for a plan, generating idea sets, building a weekly or monthly
calendar, setting cadence and funnel mix, or briefing a lane runner.

Do not use to settle positioning, pillars or voice (lv-strategy), to write hooks (lv-hooks) or
prose (lv-draft), to gate a draft (lv-gate), or to publish (lv-launch). This stage produces a slate
and its evidence labels; it never produces finished copy and never fires anything outward.

## Procedure

1. Load lv-strategy first: the golden question, the pillar slot map, the lane register and
   `references/doctrine-2026.md`. A plan without them is guessing.
2. Source the facts (references/sourcing-and-evidence.md): pick the corpus cluster before opening
   transcripts, tag every claim by evidence class, answer NOT COVERED when the corpus is silent, and
   keep unverified numbers in the claim ledger instead of the plan.
3. Generate ideas (references/idea-engines.md): the pillar-format matrix for breadth, the collision
   engine for Lane A worldview articles, the trend pipeline for live signals, and the Eden idea
   engine for cards the user can post today. Every idea needs a moat (story, data or proof) and a
   receipt.
4. Build the week (references/calendar-and-cadence.md): read last week's actuals first, state the
   target as a range with its basis (or say it is unreachable and what is reachable), then slot 3-5
   posts, never two in one day, each with one job, different format and energy across the week.
5. Set the cadence and funnel mix from the same file: three better posts a week is the 2026 bar,
   lanes keep their existing rhythm only while it beats baseline, and the weekly review decides.
6. Write the week to the board Mike already uses. No parallel plan file, no month-deep queue; plan
   about a week ahead and revisit weekly.
7. Hand each lane runner its brief per references/lane-runners.md: pillar, job, format, evidence
   label and funnel stage per slot. Runners execute briefs; they never invent slots or numbers.

## Quality bar

- Every slot cites evidence: a receipt post, the lane's own baseline data, or a deliberate experiment
  marked as one. At most one experiment per week.
- The target is a range with arithmetic behind it; an unreachable request is answered with numbers.
- No two posts share a day; three formats differ in format, material and energy.
- Give-to-take on calls to action is at least 4:1; at most one ask-bearing post in five.
- Every creator-sourced number is marked or dropped; no magnitude travels into copy.
- The slate is on the board Mike already uses, and every outward step is marked as needing Mike's yes.

## Lanes

- **Lane A (personal brand):** themed days run by the weekly rhythm runner; Birch Tuesday-only, The
  Coach from behind or in silhouette, pop-culture openings. The lane keeps its rhythm while it beats
  baseline.
- **Lane B (RIG B2B):** the daily post runner, 4-5 posts a week on fixed days, evidence-led with
  named receipts and AntiGenericForce at or above 85. Its slate maps onto the three-post barbell
  when a week needs cutting.
- **Ideawake client lane:** Coby's account, Mon/Wed/Fri publish plus amplify, Tue/Thu engagement
  only. Nothing fires without Mike's explicit client approval; the brief is written for Coby's
  voice.
- **Job-search lane:** recruiter-visibility content is planned separately and never mixed into the
  RIG pipeline.

## Tools and runners

| name | kind | path | when to call |
|---|---|---|---|
| step-1-source | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-1-source.md` | to run the corpus-first sourcing step of the growth-os pipeline |
| step-2-plan | tool | `~/.aside/u/0/skills/user/linkedin-growth-os/agents/step-2-plan.md` | to run the week-planning step of the growth-os pipeline |
| eden-discover | tool | `eden://settings/skills/eden-discover` | to pull Eden-indexed market evidence (named by Eden, not a disk path) |
| linkedin-weekly-rhythm | runner | `~/.aside/u/0/skills/user/linkedin-weekly-rhythm/SKILL.md` | Lane A themed-day runner; calls this stage for the weekly slate and evidence labels |
| rig-daily-linkedin-post | runner | `~/.aside/u/0/skills/user/rig-daily-linkedin-post/SKILL.md` | Lane B daily runner; calls this stage for slots, jobs and funnel stages |
| ideawake-linkedin-weekly | runner | `~/.aside/u/0/skills/user/ideawake-linkedin-weekly/SKILL.md` | client lane weekly engine; calls this stage for the Mon/Wed/Fri slate under client approval |
| alfred-content-planning-cron | runner | `~/.aside/u/0/skills/user/alfred-content-planning-cron/SKILL.md` | builds tomorrow.json for the Alfred pipeline; calls this stage for the slot brief before filling it |
| alfred-trend-pipeline | runner | `~/.hermes/skills/alfred-trend-pipeline/SKILL.md` | daily competitor and industry trend scan; feeds this stage's trend leg with JSON reports |
| linkedin-content-planning | runner | `~/.hermes/skills/content-automation/linkedin-content-planning/SKILL.md` | Alfred content-planner cron skill; calls this stage for the week's slate |
| alfred-linkedin-cron | runner | `~/.prime/agent/skills/alfred-linkedin-cron/SKILL.md` | Prime Agent Alfred cron; calls this stage for drafts-in-brief, never publishes |
| li-content-cycle | runner | `~/.hermes/skills/rig-linkedin-virality/skills/li-content-cycle/SKILL.md` | rig-linkedin-virality P1 daily cycle; calls this stage for the idea and slot brief before drafting |
| li-content-cycler | runner | `~/.hermes/agents/li-content-cycler.json` | agent config for the P1 cycle; load with li-content-cycle |
| prime-alfred | runner | `~/.omp/agent/agents/prime-alfred.json` | OMP agent config for the Alfred content pipeline |

## Sub-skills

| file | covers |
|---|---|
| `references/sourcing-and-evidence.md` | lg-source method, claim ledger, corpus map, evidence classes, NOT COVERED rule |
| `references/idea-engines.md` | pillar-format matrix, collision engine, Eden idea engine, trend pipeline |
| `references/calendar-and-cadence.md` | weekly and monthly planning, slots and jobs, funnel mix, cadence rules, conflicts |
| `references/lane-runners.md` | what each runner does and how it calls this stage |

## Hard rules carried forward

- Never two posts in one day; the second is cannibalised [lg-plan].
- Give at least 4 takes for every 1 ask on calls to action; at most one ask-bearing post in five [lg-plan, cadence-ritual].
- Ambition is met with a second distribution wave, never more effort on a dead post; past about two hours a post is not rescuable [lg-plan].
- If a requested target is unreachable, say so with the arithmetic; never widen the band or accept a fake-engagement shortcut [lg-plan].
- Write the week to the board Mike already uses; never create a parallel plan file [lg-plan].
- Never publish, edit or delete a live post from a plan; Eden drafts only and Mike publishes [cadence-ritual].
- No automated DMs or connection-note pitches; no bulk connection sending; never stack a follow batch behind a comment sweep [cadence-ritual].
- No golden-window reply that contradicts, negates or pitch-links [cadence-ritual].
- Never let a creator percentage become a publishable claim; distinguish a second source from a second citation of the same source [lg-source].
- Any claim about the feed written before 2026-03-12 describes the replaced system; check dates before importing it [corpus-map].
- If a number cannot survive "who measured it and what did they look at", it stays in the ledger and out of the post [claim-ledger].
- Three posts in a week must differ in format, material and energy; do not spam one format [format-mix].
- A real photo, never stock, never an AI infographic; video strategy is not invented from the corpus [format-mix].
- Cell ideas in the matrix are specific headlines, never themes, and never reused across pillars [content-matrix].
- Present the week's plan and wait for one ok before drafting anything; at most 7 drafts per run [head-of-content].
- Never call the Eden scheduler without draft status, and never publish immediately unless the user explicitly asks and content, platform and time are confirmed [head-of-content, idea-engine].
- Never re-pitch an idea from the last three runs, anything queued, or anything already published [idea-engine].
- Never invent posts, creators, metrics, links or queued drafts; every "queued" claim follows a successful write [weekly-strategist, head-of-content, idea-engine].
- Grades are honest: a plan that was not posted gets said, and "you did not post it" is a valid grade [head-of-content].
- Runners hold their lanes' approval gates; nothing outward fires unattended and the Ideawake lane needs Mike's explicit client approval [li-growth, linkedin-viral].
- Three better posts a week is the 2026 quality bar; a lane keeps its rhythm only while it beats baseline [clark-content-system].

## Done-test

`python3 capabilities/skills/linkedin-viral/scripts/check_ledger.py capabilities/skills/lv-plan`
is GREEN only when the frontmatter name matches the folder and carries the JEV-FIRST MANDATE, the
body opens with the JEV-first mandate section, references/ holds at least three sub-skills of 400+
bytes plus a ledger.md with an action-bearing row for every stage-map row assigned to this stage,
every backticked disk path resolves, and no sub-skill shares a 12-word run with a third-party merge
source.
