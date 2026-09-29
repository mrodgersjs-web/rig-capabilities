---
name: fesd-requirements
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Owns stage S02 of front-end system design: requirements collection and write-up before any
  architecture talk. Produces the two-level requirements artifact (user-visible capabilities plus
  system guarantees), the functional and non-functional split, and the explicit scope and
  assumption statements, from 43 laws across 12 Front-End Engineer videos. Use when a design
  interview or design doc needs requirements, when someone jumps straight to components, when
  "real-time feel" or "fast" appears as an adjective instead of a number, or when scope and
  assumptions must be written down. JEV-FIRST MANDATE, findable at task start: typed judgments in
  this stage go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED is the only answer
  when the classifier is down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, requirements, scoping, non-functional]
outcome: "code-engineering: a complete, number-bearing requirements artifact a design can be built against"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-requirements/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S02"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Requirements for front-end system design

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-requirements-analyst loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate

Typed judgments this stage forces, and which go to Jev first:

1. Is this requirement list complete enough to design against, or are whole categories (devices,
   accessibility, offline, scale) missing (kind: plan.readiness).
2. Does every performance adjective carry a number or a named exclusion (kind: plan.readiness).
3. Is the scope statement honest about what is out and what is bonus (kind: plan.readiness).
4. Is this requirement functional or non-functional, and is it filed in the right section
   (kind: plan.readiness).

Command shape: `~/.rig/bin/rig-s1gate check plan.readiness --file <requirements.md> --subject "requirements <id> sha256:<hash>" --json`.
Nearest existing rubric: plan.readiness, advisory until calibrated. A pass needs every required
signal above 0.9. Classifier down, erroring, or rubric missing = DEFERRED, never a guessed
verdict. An advisory PASS is not permission to ship or publish.

## When to use

- As step one of any front-end system design answer (stage S01 hands off here).
- When a design document exists but no requirements section does.
- When requirements are being asserted as adjectives ("fast", "real-time", "most browsers").
- When deciding what the design deliberately will not cover.

## Inputs and output contract

Input: the problem statement, the genre call (product / feature / component), and any platform or
browser constraints the interviewer supplied.

Output artifact: `requirements.md` with exactly these headings:

1. General requirements (user-visible capabilities; feature statement plus basic user actions).
2. Advanced / configurable requirements (what a consumer can tune).
3. Functional requirements (behaviors the system must support: data shapes, formats, modes).
4. Non-functional requirements (latency, bandwidth, device range, accessibility, scale), every
   adjective carrying a number, a percentage, or a named exclusion.
5. Scoping and assumptions (explicit outs, bonus features, environment assumptions).

## Procedure

1. Write general requirements as user-visible capabilities before any architecture talk. Load
   references/functional-requirements.md. CLAIM(Tu-hZ6lqNtY@04:41) CLAIM(5vyKhm2NTfw@04:02)
2. Split the second block: what the consumer can configure (cache TTL, cache size, max results,
   item template). CLAIM(9mjsRrJYOWE@17:28)
3. Define core behavior first, then the data-shape and source rules (static and async, any data
   type). CLAIM(9aOXGE7wAZo@03:27) CLAIM(9aOXGE7wAZo@04:40)
4. Move to non-functional: state requirements at two levels and pin each one. Load
   references/non-functional-requirements.md. CLAIM(LEaiGjffLEs@01:14) CLAIM(LEaiGjffLEs@02:23)
5. Declare device breadth and accessibility explicitly as requirements, then move on.
   CLAIM(5vyKhm2NTfw@05:20) CLAIM(u6jhTo13_No@06:41)
6. State scale plainly (row counts, dataset size) and the device floor.
   CLAIM(u6jhTo13_No@05:36) CLAIM(u6jhTo13_No@06:07)
7. Write scope and assumptions: named browser exclusions, what is out, what is bonus. Load
   references/scoping-and-assumptions.md. CLAIM(3MADCVqL534@06:54) CLAIM(HR2jXy_wPg4@04:31)
8. Keep requirements generic where extension is expected (formats, grid size, component library,
   entities) so a new type does not force a redesign. CLAIM(fmIiDLbLc_s@03:32)
   CLAIM(fmIiDLbLc_s@03:44) CLAIM(tsGarhpWOws@05:22) CLAIM(leo1FZ6vu1I@09:57)
9. Hand the artifact to stage S03 (architecture) and keep it open for the closing re-check.

## Core laws

Structure (consensus):

- State requirements at two levels: what the user can do, and what the system must guarantee
  (latency, bandwidth, device range). CLAIM(LEaiGjffLEs@01:14) consensus with
  CLAIM(fmIiDLbLc_s@03:13) CLAIM(9mjsRrJYOWE@04:33).
- Write general requirements as the feature statement plus the basic user actions it must
  support. CLAIM(5vyKhm2NTfw@04:02) consensus with CLAIM(Tu-hZ6lqNtY@04:41).
- Enumerate general product requirements before constraints.
  CLAIM(leo1FZ6vu1I@01:50) consensus.

Numbers instead of adjectives (single-source, load-bearing):

- Pin "real-time feel" to a concrete latency budget (he uses roughly 40-60 ms) instead of leaving
  it as an adjective. CLAIM(LEaiGjffLEs@02:23) single-source.
- Declare browser coverage as a percentage with named exclusions (for example 95% minus IE11)
  instead of vague "most browsers". CLAIM(3MADCVqL534@06:54) single-source.
- State the scale requirement plainly: tables deal in thousands of rows and must handle large
  datasets well. CLAIM(u6jhTo13_No@05:36) single-source.

Coverage requirements (consensus):

- Declare device breadth explicitly as an adaptive-design requirement spanning tablets and
  phones. CLAIM(3MADCVqL534@07:05) consensus with CLAIM(Tu-hZ6lqNtY@05:35)
  CLAIM(5vyKhm2NTfw@05:20).
- Require screen-reader accessibility and a CSS API for table styling as functional
  requirements. CLAIM(u6jhTo13_No@06:41) consensus with CLAIM(5vyKhm2NTfw@05:20).
- Add offline or reduced-network behavior as a functional requirement.
  CLAIM(3MADCVqL534@07:39) consensus with CLAIM(leo1FZ6vu1I@03:38) CLAIM(tsGarhpWOws@06:56).
- Design for low-bandwidth mobile networks and battery limits where the users are on phones.
  CLAIM(LEaiGjffLEs@02:29) consensus with CLAIM(leo1FZ6vu1I@03:38).

Behavior and shape rules (consensus):

- Define the core behavior first (the widget returns result items for the query the user types).
  CLAIM(9aOXGE7wAZo@03:27) single-source.
- Support both static and asynchronous data, and accept any data shape rather than one entity
  type. CLAIM(9aOXGE7wAZo@04:40) consensus with CLAIM(9mjsRrJYOWE@04:33).
- Keep the event entity identical across every view so no view invents its own duplicate shape.
  CLAIM(leo1FZ6vu1I@09:57) single-source.
- Keep entities JSON-serializable in both directions so export and import come for free.
  CLAIM(leo1FZ6vu1I@10:15) single-source.
- Define rendering stability explicitly: when the user switches time frames, show a downscaled
  chart before the new data arrives. CLAIM(HR2jXy_wPg4@04:56) single-source.

## Sub-skills

| Sub-skill | File | Load when |
|---|---|---|
| Functional requirements | references/functional-requirements.md | Writing capabilities, behaviors, modes, formats, configuration surface |
| Non-functional requirements | references/non-functional-requirements.md | Pinning latency, bandwidth, device, accessibility, scale, offline |
| Scoping and assumptions | references/scoping-and-assumptions.md | Declaring outs, bonus features, environment assumptions, extensibility |

## Decision tables

Where does a requirement go (cited):

| Statement type | Section | Example | Cite |
|---|---|---|---|
| User-visible capability | General | search, preview, watch | CLAIM(Tu-hZ6lqNtY@04:41) |
| Consumer configuration | Advanced | cache TTL, max results, item template | CLAIM(9mjsRrJYOWE@17:28) |
| Supported behavior or mode | Functional | sync and async modes, read-only mode | CLAIM(lO6GyCvbDm8@08:05) CLAIM(lO6GyCvbDm8@03:47) |
| Measurable system guarantee | Non-functional | 40-60 ms latency budget | CLAIM(LEaiGjffLEs@02:23) |
| Environment assumption | Scoping | professional desks, modern browsers only | CLAIM(HR2jXy_wPg4@07:33) |
| Explicitly excluded or bonus | Scoping | chart synchronization as bonus; video out | CLAIM(HR2jXy_wPg4@04:31) CLAIM(3MADCVqL534@05:08) |

## Anti-patterns

- Architecture talk before requirements are written. Refuted by CLAIM(Tu-hZ6lqNtY@04:41)
  CLAIM(5vyKhm2NTfw@04:02).
- "Fast", "real-time", "most browsers" left as adjectives. Refuted by
  CLAIM(LEaiGjffLEs@02:23) CLAIM(3MADCVqL534@06:54).
- Accessibility or device coverage handled as a closing afterthought. Refuted by
  CLAIM(u6jhTo13_No@06:41) CLAIM(5vyKhm2NTfw@05:20).
- One hard-coded entity type or format where the problem is generic. Refuted by
  CLAIM(9aOXGE7wAZo@04:40) CLAIM(fmIiDLbLc_s@03:32).
- A design that silently includes what the requirements ruled out. Refuted by
  CLAIM(3MADCVqL534@05:08) CLAIM(lO6GyCvbDm8@31:56).

## Worked cases

- Tu-hZ6lqNtY "[Front-End Product Design] - Netflix": general requirements as user-visible
  capabilities, device breadth including Smart TV.
- LEaiGjffLEs "[Front-End System Design] - Chat application": two-level requirements with a
  concrete latency budget.
- u6jhTo13_No "[Front-End System Design] - Data Table Component": formats, sorting, scale,
  accessibility as requirements.
- lO6GyCvbDm8 "[Front-End System Design] - Design a Poll Widget": modes, distribution and
  embeddability as requirements.
- leo1FZ6vu1I "[Front-End System Design] - Google Calendar": one entity shape, serializable
  entities, mobile-first and offline as requirements.
- HR2jXy_wPg4 "Frontend System Design - Financial Dashboard / TradingView": unified data
  interface, rendering stability, bonus scoping.

## Dated / contestable

- The 2020 browser-coverage example excludes IE11 by name. IE11 is end-of-support since 2022.
  Distiller note (not the author): keep the percentage-plus-named-exclusions pattern and name
  current exclusions. CLAIM(3MADCVqL534@06:54)
- The 40-60 ms "instant" latency figure is the author's chat-app target from 2020, not a
  standard. Distiller note (not the author): treat it as one worked example of pinning an
  adjective, and derive your own number per product. CLAIM(LEaiGjffLEs@02:23)
- Device lists in the 2020 episodes name Smart TV and tablets of that era. Distiller note (not
  the author): re-derive the device floor from the audience, the habit is what transfers.
  CLAIM(Tu-hZ6lqNtY@05:35)

## Hand-off

- Next stage: the architecture stage of fe-system-design-os (stage S03), which consumes this
  artifact; stage S01 (fesd-interview-framework) owns the plan and clock that surrounds it.
- Adjacent estate skills: plan.readiness rubric for gating the artifact, app-data-layer for
  schema and backend slices, harness ha-09 (api design) and ha-10 (schema design) when the
  data model goes deep, fixing-accessibility for the accessibility requirements named here.
