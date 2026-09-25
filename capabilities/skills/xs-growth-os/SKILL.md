---
name: xs-growth-os
description: "JEV-FIRST entry point for Mike Rodgers' X (@RodgersRIG) audience-growth lane: every typed judgment (rank topics, screen tactics, gate drafts, verdict claims) routes through rig-s1gate before any frontier model call, and DEFERS when the classifier is down. LOAD THIS FILE AT THE START of any X-lane session; the route table inside is the only path to the child skills. Covers: corpus sourcing, weekly stage-aware planning, profile conversion assets, drafting posts/threads/replies, the reply engine, and measurement with wired actions. USE WHEN posting to X, planning an X week, writing a thread, running a reply batch, auditing the X profile, or asking why an X post flopped. Never publishes from here."
---

# X Growth OS — meta skill

> **JEV-FIRST SURFACE.** Every typed judgment in this lane (rank, screen, gate, verdict) runs
> through `rig-s1gate` BEFORE any frontier call, and DEFERS when the classifier is down. This
> file changes routing; the mandate below is binding, not decorative.

**Load this file first when any X-lane work begins.** It is the entry surface: the route table
below is the only path into the child skills, and the JEV mandate at the top of this body binds every judgment
made in this lane.

## JEV-first mandate (binds every skill and agent in this lane)

Typed judgments in this lane route through Jev BEFORE any frontier model call:

| Judgment in this lane | How it routes |
|---|---|
| rank topics/formats for the week | `rig-s1gate rank` on the candidate set |
| screen a tactic before it enters a plan | `rig-s1gate check` on the tactic artifact |
| quality-gate a draft or batch before staging Mike | `rig-s1gate check <rubric> --file <artifact> --subject <kind> --json` |
| verdict on a corpus claim (real vs vendor noise) | `rig-s1gate check`, then human eye on the video itself |

Command shape: `~/Developer/rig-capabilities/bin/rig-s1gate check <rubric> --file <artifact>
--subject <kind> --json`. A required noul passes only above 0.9. **Fail closed:** if the command
errors, the kind is absent from `work-criteria.json`, or the classifier is unreachable — DEFER and
say so; never guess a verdict locally, and never let an advisory PASS authorize a send (sends
belong to Mike regardless).

**Router only. This file holds no doctrine and no tactics.** Load a child skill; a child loads its
own sub-skill. Do not read all of them.

- Corpus (21 transcripts, 10 channels + control bench): `~/Developer/rig-x-studio/corpus/`
- Per-channel doctrine: `~/Developer/rig-x-studio/corpus/<channel>/FRAMEWORK-EXTRACTION.md`
- Agents: `~/Developer/rig-x-studio/agents/`

## Lane ownership (hard boundary)

`@RodgersRIG` is Mike's goal-1 surface (audience). Decided 2026-09-24; full rationale in
`~/.aside/u/0/memory/projects/rodgers-x-growth.md`. Goals 2 (job) and 3 (clients) stay on LinkedIn.
Birch / Unit 7 / The Coach never appear here. **This skill never touches `@JacobRodge52987`** — that
is the minor's lane (`projects/jacob-x-studio.md`), out of scope unconditionally.

## Route table

Absolute paths so installs resolve from any harness. Canonical tree:
`~/Developer/rig-x-studio/`.

| The ask | Load |
|---|---|
| "what does the corpus say about X", "who taught this", "is this number real" | `~/Developer/rig-x-studio/skills/xs-source/SKILL.md` |
| plan the week, cadence, what stage are we in, what do I post | `~/Developer/rig-x-studio/skills/xs-plan/SKILL.md` |
| profile, bio, banner, pinned, conversion assets | `~/Developer/rig-x-studio/skills/xs-profile/SKILL.md` |
| write a post, a thread, hooks, compress to 280 | `~/Developer/rig-x-studio/skills/xs-draft/SKILL.md` (+ its `sub/` for detail) |
| reply engine, reply lists, engagement mode, boosts | `~/Developer/rig-x-studio/skills/xs-amplify/SKILL.md` (+ `sub/reply-list-ops.md`) |
| how did it do, what changes, promote or kill a topic | `~/Developer/rig-x-studio/skills/xs-measure/SKILL.md` |
| platform limits, identity assertion, what needs approval | `~/Developer/rig-x-studio/skills/xs-comply/SKILL.md` |

## Gate order — never reorder

`comply → source → profile → plan → draft → amplify → measure`

The JEV mandate is part of this order: any typed judgment (topic rank, tactic screen, draft gate,
claim verdict) passes `rig-s1gate` before any frontier model call, and every specialist's staged
output gets the gate check before it reaches Mike. This changes routing, not just style.

Comply first is not bureaucracy: the reply engine is outward public speech and the carrier rules
(Eden → Ayrshare, never the browser) exist because the browser session has carried the wrong
account before. Draft before profile is how traffic lands on a page that cannot convert it.

## Hard stops

1. **No publish from this skill.** Original posts, threads, and reply batches are staged as drafts
   and go out only under Mike's approval posture (daily batch for replies, batch for originals;
   per-item for anything naming a client or candidate, any spend, or a mention of Jacob).
2. **No engagement pods, no bought engagement, no follow-for-follow.** The corpus itself marks
   large engagement groups as suspension bait (`jacob-c-edmunds`, tactic 21), and X's rule text
   names automation as an aggravating factor independent of volume (`sites/x.com.md`). The
   compliant versions of the same intents are in `xs-amplify` (mastermind-of-record, authentic
   boosts) — offer those and say that is what they are.
3. **Write X copy to fit 280 characters** unless Premium on the account is verified. It is
   unverified as of 2026-09-24; do not tick Eden's Premium checkbox on a guess.

## The one cross-corpus contradiction (read before scaling replies)

The corpus disagrees with itself on reply volume, and the disagreement is load-bearing:

- **Reply-heavy doctrine:** Collin Rutherford runs 50 high-value replies/day to buy the first 1,000
  followers; Creator Freedom's "200 rule" regulars interact with 200 niche accounts daily;
  Hypefury's grade-A reply guy is the named escape from "beginner hell".
- **The measured control:** Sharbel's 7-day 100-replies/day experiment found replies correlate with
  new followers at **69%** while impressions correlate at **87%** — replies put you "on the map",
  impressions convert (`bench/SJIZIgb-cCM`). He also observed **discoverability decay**: the value
  of a reply falls as your own impressions grow.

Standing synthesis until Mike's own data overrides it: **replies are the discovery engine below
~1,000 followers; content is the conversion engine; shift hours from replies to content as
impressions compound.** Every stage plan in `xs-plan` encodes this taper; `xs-measure` carries the
correlation check so the taper happens on data, not on mood.
