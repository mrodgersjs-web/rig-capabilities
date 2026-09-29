---
name: fe-system-design-os
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: every typed judgment in this
  family (mode and prompt-type routing, requirement completeness, transport choice, design readiness,
  answer score) goes to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED is the only answer when
  the classifier is down, never a guessed verdict. FE System Design OS: the single front door for front-end engineering and design-architecture work -
  designing a web app's front end (feeds, chat, editors, spreadsheets, calendars, dashboards, media
  catalogs), designing a reusable widget (typeahead, data table, poll), reviewing a front-end
  architecture, or preparing for and running a front-end system design interview. Picks the mode
  (INTERVIEW, BUILD-DESIGN, REVIEW, DRILL), fixes the prompt type, and routes to exactly one of 10 stage
  skills (interview-framework, requirements, architecture, component-api, state-data, api-network,
  realtime-sync, performance, a11y-i18n, career-prep), each with sub-skills, conducted by the
  fesd-conductor meta agent over 6 agents and 4 sub-agents. Backed by fe-system-design-doctrine: 483
  paraphrased laws from every video on Evgenii Ray's Front-End Engineer channel (16 videos, 96K words),
  each cited CLAIM(<videoId>@mm:ss). Use for /fe-system-design-os, /fesd, "front end system design", "design the
  frontend for X", "mock FE interview", "review this frontend architecture".
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, meta-skill, router, doctrine, interview, architecture]
outcome: "code-engineering: every front-end design or FE interview job enters one router that fixes the mode, loads exactly one stage skill at a time, applies cited corpus doctrine, and ends in a design doc or scored answer judged by someone other than its author"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py --plant
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py --self-test
quality_floor: 0.6
metadata:
  purpose: meta-skill
  parent: when-shipping-code
  stages: "10"
  agents: "1 meta, 6 agents, 4 sub-agents"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl: 16 videos, 483 laws"
---

# FE System Design OS (meta-skill)

JEV FIRST, and it binds every front-end design, review and FE interview job under this skill: an
agent whose only context is this excerpt sends semantic triage, routing, and classification to the
rig-s1gate Jev path BEFORE any frontier LLM call. Mode routing, requirement completeness, transport
choice, design readiness and answer scores are typed judgments, not vibes. When the fast classifier
is unavailable: DEFER, never guess a verdict locally. A required signal passes only above 0.9; below
that the stage does not advance, and an uncalibrated ESCALATE is a held transition.

## Load surface

This meta-skill is an always-loaded task-start surface for front-end system design: the `/fesd` and
`/fe-system-design-os` commands in `~/.rig/universal-commands/` load it first, `fesd-conductor` loads
it before its first action, and `when-shipping-code` routes every front-end architecture or FE
interview request here. It is the front door for the family, not a deep reference an agent must
already know about. Every path and command in this family is relative to the canonical repo
`~/Developer/rig-capabilities`; installed copies in other harness roots run from there.

## JEV-first mandate

Inventory the decisions the task forces and route each one, first match wins: CODE (deterministic rule, e.g. claims_check) -> JEV -> SYSTEM 2 (frontier model for generating the design) -> HUMAN (Gate-D: publishing, pushing, sending anything outward).

| typed judgment | Jev rubric (nearest existing; advisory until calibrated) |
|---|---|
| which mode / which prompt type / which case is closest | jev.skill-router, jev.triage |
| is the requirement list complete enough to design against | plan.readiness |
| is the architecture / stack choice sound | app.stack |
| is the API surface sound | api.backend |
| does the rendered UI pass | ui.design |
| does this interview answer pass | hm.technical |
| does a skill file in this family still carry its mandate | doctrine.surface |

Command: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. A pass needs every required signal above 0.9 (exactly 0.90 fails). Classifier down, erroring or rubric missing = **DEFERRED**, never a guessed verdict and never a frontier model's opinion in its place. An advisory PASS is not permission to publish, push or ship. A claim that "Jev judged X" cites the decision id in `~/.rig/s1gate/decisions.db`.

Hierarchy: `when-shipping-code` -> **fe-system-design-os** -> one stage skill -> at most one of its sub-skills. Doctrine: `fe-system-design-doctrine`. Meta agent: `fesd-conductor`.

## Step 0: Mode guard (always first)

| mode | trigger | end artifact | who judges |
|---|---|---|---|
| **INTERVIEW** | "mock interview", "practice FE system design", a named prompt with a clock | timed answer transcript + scored rubric per stage | fesd-interview-coach, scored with hm.technical |
| **BUILD-DESIGN** | "design the frontend for <real product>", App Studio stage 2-3 hand-off | design doc (template below) | fesd-design-reviewer (never the author) |
| **REVIEW** | "review this architecture / PR / design doc" | findings table: stage, finding, law cited, severity | fesd-design-reviewer |
| **DRILL** | "quiz me on <topic>", "what does he say about X" | Q&A drawn from one stage skill + case | fesd-interview-coach |

Then classify the prompt type (route with jev.skill-router; DEFERRED means ask Mike, never guess):

| prompt type | closest worked cases (fe-system-design-doctrine/references/cases/) |
|---|---|
| infinite feed / media grid | 5vyKhm2NTfw News Feed, 3MADCVqL534 Pinterest, Tu-hZ6lqNtY Netflix |
| realtime messaging | LEaiGjffLEs Chat |
| collaborative editor / grid | tsGarhpWOws Notion, fmIiDLbLc_s Google Sheets |
| scheduling / calendar | leo1FZ6vu1I Google Calendar |
| data-heavy dashboard / charts | HR2jXy_wPg4 Financial Dashboard |
| reusable widget | 9mjsRrJYOWE + 9aOXGE7wAZo Typeahead, u6jhTo13_No Data Table, lO6GyCvbDm8 Poll |
| protocol / networking concept | gxF9fLo5XQw HTTP deep dive |
| career / loop prep | 2Xqu_GNvnxg, 1kO54TT2cbs, v4Dt4FalMOA |

## Stage routes (load exactly one at a time, in this order for a full design)

| # | stage skill | owns | agent | load when |
|---|---|---|---|---|
| 1 | fesd-interview-framework | the step plan, time budget, driving the round, what gets scored | fesd-interview-coach | INTERVIEW/DRILL start, or to pick the plan order for a design doc |
| 2 | fesd-requirements | functional, non-functional, scope, assumptions | fesd-requirements-analyst | every mode, first real step |
| 3 | fesd-architecture | high-level components, layering, rendering strategy | fesd-architect | after requirements pass plan.readiness |
| 4 | fesd-component-api | component tree, reusable widget API, UX states | fesd-architect | UI decomposition or any widget prompt |
| 5 | fesd-state-data | entities, client store, normalization, client caching/storage | fesd-architect | before API design |
| 6 | fesd-api-network | REST/GraphQL shape, pagination, HTTP, front-end security | fesd-api-designer | after data model |
| 7 | fesd-realtime-sync | polling/SSE/WebSocket choice, collaboration, offline | fesd-api-designer (+ fesd-transport-picker) | any live, collaborative or offline requirement |
| 8 | fesd-performance | rendering, virtualization, assets, network perf, memory, budgets | fesd-performance-engineer | every design; deepest-probed stage in the corpus |
| 9 | fesd-a11y-i18n | keyboard, ARIA, contrast, RTL, locale | fesd-a11y-auditor (sub-agent) | every user-facing design |
| 10 | fesd-career-prep | big-tech loop prep, leveling, compensation context, AI-era engineering | fesd-interview-coach | career questions only; Mike's own search routes to traject-os |

Quick mode (time-boxed interview): 1 -> 2 -> 3 -> 5 -> 6 -> 8, then 7 and 9 only if requirements demand them. His 2025 order is requirements and mockup, layout, data model, API, data flow, synchronization, multi-window. CLAIM(HR2jXy_wPg4@02:16)

## Agent org chart

```
fesd-conductor (META agent: routes, never designs itself)
├── fesd-interview-coach        S01, S13  -> mock rounds, drills, scoring
├── fesd-requirements-analyst   S02
├── fesd-architect              S03, S04, S05
│   └── fesd-case-retriever     (sub-agent) closest worked case(s) for the prompt
├── fesd-api-designer           S06, S07
│   └── fesd-transport-picker   (sub-agent) realtime transport decision table
├── fesd-performance-engineer   S08
├── fesd-a11y-auditor           (sub-agent) S09 checklist pass
├── fesd-design-reviewer        independent critic across all stages; never the author
    └── fesd-citation-verifier  (sub-agent) runs claims_check + check_family
```
Agent files: `capabilities/agents/fesd-*.md`.

## Design doc template (BUILD-DESIGN output)

1. Problem and scope (in / out) - fesd-requirements
2. Functional requirements, non-functional requirements (numbers where possible)
3. High-level architecture diagram + rendering strategy - fesd-architecture
4. Component tree and any reusable component API - fesd-component-api
5. Data model: entities, client store shape, cache/storage policy - fesd-state-data
6. API: endpoints or queries, pagination, error/retry, security notes - fesd-api-network
7. Realtime / sync / offline (if required) - fesd-realtime-sync
8. Performance plan: rendering, assets, network, memory, budget - fesd-performance
9. Accessibility and i18n - fesd-a11y-i18n
10. Trade-offs taken and rejected, each citing the law it leans on
11. Open questions for Mike

## Hard rules
- Cite or label. Every doctrine-backed statement carries CLAIM(<videoId>@mm:ss); anything else is labeled "Distiller note" or "own reasoning". Never cite from memory: look it up in the stage skill or law index (a memory-written timestamp was wrong once while this family was being built).
- Single-author doctrine. Where the estate or current platform reality disagrees (dated items), the stage skill's Dated / contestable section wins, labeled.
- The author of a design never judges it. BUILD-DESIGN and REVIEW verdicts come from fesd-design-reviewer plus Jev.
- Nothing outward: publishing a design, pushing code, or sending anything goes to Gate-D.
- Adjacent estate skills, not duplicated here: app-web-frontend (building slices), app-ui-design / emil-design-eng / impeccable (visual design and polish), fixing-accessibility, fixing-motion-performance, code-perf-bottleneck-finder, app-data-layer, security-threat-model, traject-os (Mike's job search).

## Invocation
`/fe-system-design-os <mode> <prompt>` or `/fesd`. Examples: `/fesd interview "design Instagram stories" 45min`, `/fesd build "front end for the RIG client portal"`, `/fesd review ~/Developer/<repo>/docs/frontend-arch.md`, `/fesd drill realtime`.

## Maintenance
- Refresh: re-list @FrontEndEngineer uploads; new ids get transcripts in `.context/frontend-engineer-yt/transcripts/`, a manifest row, a notes file (DISTILL_BRIEF.md in `~/Developer/rig-doctrine-corpora/frontend-engineer-yt/`), then laws merged into the owning stage.
- Gates: `scripts/claims_check.py` (every citation resolves to a transcript line within 15s; `--plant` proves it goes RED) and `scripts/check_family.py` (structure, mandate present, references exist, no 12-word verbatim run; `--self-test` proves it goes RED).
