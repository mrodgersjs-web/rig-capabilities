---
name: fesd-interview-framework
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Owns stage S01 of front-end system design interviewing: the written design plan, the delivery
  discipline inside a 45-60 minute round, scope steering, and what interviewers actually score.
  Produces the ordered plan artifact and the practice-round protocol that turns 33 laws from 11
  Front-End Engineer videos into a repeatable interview routine. Use when preparing or running a
  front-end system design mock, when asked "how do I structure a design interview answer", when a
  candidate starts drawing before requirements are written, or when a practice answer needs
  scoring. JEV-FIRST MANDATE, findable at task start: typed judgments in this stage go to
  rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED is the only answer when the classifier
  is down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, interview, plan, mock-round]
outcome: "code-engineering: a written, ordered design-plan discipline and mock-round scoring loop for FE system design interviews"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-interview-framework/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S01"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Front-end system design interview framework

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-interview-coach loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate

Typed judgments this stage forces, and which go to Jev first:

1. Is this design plan complete and correctly ordered before any component work starts (kind: plan.readiness).
2. Does a practice answer show interview-grade structure and reasoning, not just a finished sketch (kind: hm.technical).
3. Did the candidate accept the interviewer's scope narrowing instead of fighting it (kind: hm.technical).
4. Does one mock round pass the bar or does the drill repeat (kind: hm.technical).

Command shape: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
Nearest existing rubrics: hm.technical (scoring a mock answer) and plan.readiness (the written
design plan), advisory until calibrated. A pass needs every required signal above 0.9. Classifier
down, erroring, or rubric missing = DEFERRED, never a guessed verdict. An advisory PASS is not
permission to ship or publish; here it only means the drill may be treated as a pass.

## When to use

- Before any mock or real front-end system design round, to fix the plan and the clock.
- When a candidate's answer opens with architecture instead of requirements.
- When asked how interviewers grade a design answer, or what to prepare for a 45-60 minute round.
- When building a practice program around the 13 worked cases in this corpus.

## Inputs and output contract

Input: the problem statement (a named product or component) and the round format (product design,
feature system design, or component design).

Output artifact: a one-page design plan, written before design talk, with these headings in order:

1. Plan list (the ordered stage list, reconciled per references/step-plan.md).
2. Interview genre (product / feature / component) and the scope decision.
3. The two hardest problems named up front.
4. Time box per stage (references/time-budget-and-driving.md).
5. Prepared assets brought to the round (schemas, mockup, requirements slide).

Then, per practice round: a scored record (rubric hm.technical) listing each plan step, the
verdict, and the one fix to carry into the next drill (references/mock-drill.md).

## Procedure

1. Classify the genre before anything else: product design wants a holistic shallow pass over a
   whole app, feature design completes one key feature, component design is about the public API
   and reuse story. Load references/interviewer-signals.md. CLAIM(Tu-hZ6lqNtY@01:21) CLAIM(9aOXGE7wAZo@00:33)
2. Walk the real product first and name the two hardest problems before any architecture.
   CLAIM(Tu-hZ6lqNtY@02:05) CLAIM(HR2jXy_wPg4@00:33) CLAIM(tsGarhpWOws@01:07)
3. Write the ordered plan on the board and announce you will work it in order. Load
   references/step-plan.md. CLAIM(9mjsRrJYOWE@01:14) CLAIM(fmIiDLbLc_s@05:57)
4. Ask the interviewer which platforms and browsers matter, and expect steering toward
   optimization or accessibility. Load references/time-budget-and-driving.md.
   CLAIM(3MADCVqL534@01:38) CLAIM(3MADCVqL534@03:55)
5. Run requirements collection as its own stage (this is stage S02; use fesd-requirements).
6. Work the middle stages (mockup, layout, data model, API, state, hard feature) inside the time
   box; sketch hierarchies only. CLAIM(fmIiDLbLc_s@12:14) CLAIM(5vyKhm2NTfw@01:09)
7. Give performance, security and accessibility their own plan steps, then re-check the
   requirements list before closing. CLAIM(9mjsRrJYOWE@03:39) CLAIM(lO6GyCvbDm8@31:56)
8. Run the practice round per references/mock-drill.md and score it with hm.technical through
   Jev before deciding pass or repeat. CLAIM(v4Dt4FalMOA@21:21)

## Core laws

Plan discipline (consensus across 2020-2023 episodes):

- Write the ordered design plan before any design talk: requirements, advanced features, mockup,
  API, state, problems, performance, security, accessibility. CLAIM(9mjsRrJYOWE@01:14) (same
  habit: CLAIM(5vyKhm2NTfw@01:13) CLAIM(3MADCVqL534@01:12) CLAIM(fmIiDLbLc_s@05:57)
  CLAIM(tsGarhpWOws@02:41)) consensus.
- Give performance, security and accessibility their own plan steps instead of closing
  afterthoughts. CLAIM(9mjsRrJYOWE@03:39) single-source.
- Split the plan's first two items into core requirements and advanced requirements.
  CLAIM(tsGarhpWOws@02:41) consensus (2020 episodes split general then specific:
  CLAIM(5vyKhm2NTfw@01:13)).

Plan order for data-heavy problems (2025 episode):

- Follow a fixed order: requirements and mockup, layout, data model, API, data flow,
  synchronization, multi-window. CLAIM(HR2jXy_wPg4@02:16) single-source.
- Bound the data model deliberately, because every extra parameter makes the design harder to
  defend live. CLAIM(HR2jXy_wPg4@21:06) single-source.

Product first, then architecture (consensus):

- Open by driving the real product and naming the two hardest problems before writing any
  architecture. CLAIM(HR2jXy_wPg4@00:33) consensus with CLAIM(Tu-hZ6lqNtY@02:05)
  CLAIM(tsGarhpWOws@01:07).
- Identify the interview genre first; product design wants a holistic view, not one feature
  finished in depth. CLAIM(Tu-hZ6lqNtY@01:21) consensus with CLAIM(9aOXGE7wAZo@00:33).

Steering and scope (single-source but load-bearing):

- Ask which platforms and target browsers matter before designing, because the answer changes
  the design. CLAIM(3MADCVqL534@01:38) single-source.
- Prepare both optimization and accessibility; the interviewer will steer toward one.
  CLAIM(3MADCVqL534@03:55) single-source.
- If the interviewer narrows the scope, stay there; the budget cannot cover everything.
  CLAIM(3MADCVqL534@05:44) single-source.
- Declare whole subsystems out of scope when they belong to backend design (for example conflict
  resolution), mention them, and move on. CLAIM(tsGarhpWOws@04:20) single-source.

Time and drawing economy (consensus):

- Time-box the exercise. CLAIM(5vyKhm2NTfw@01:09) single-source.
- Pre-build schemas for well-known problems so minutes are not burned drawing from scratch.
  CLAIM(5vyKhm2NTfw@07:38) consensus with CLAIM(HR2jXy_wPg4@05:50) CLAIM(Tu-hZ6lqNtY@13:51).
- Sketch a high-level component hierarchy only; full component diagrams burn the budget.
  CLAIM(fmIiDLbLc_s@12:14) consensus with CLAIM(tsGarhpWOws@07:59).

What the interviewer scores (single-source, one podcast):

- Prepare against standardized question pools and scoring criteria, not against one
  interviewer's improvisation. CLAIM(v4Dt4FalMOA@08:49) single-source.
- The interviewer scores the thinking signal, so narrate reasoning; a clearly explained partial
  solution beats a fast silent solve. CLAIM(v4Dt4FalMOA@21:21) CLAIM(v4Dt4FalMOA@22:21) single-source.
- Never memorize a solution you cannot explain; probing detects memorized code.
  CLAIM(v4Dt4FalMOA@23:35) single-source.
- At staff and above, courses stop working; interviewers probe real experience scaling
  infrastructure. CLAIM(v4Dt4FalMOA@13:28) single-source.
- Close by re-checking the requirements list so nothing promised is left undesigned.
  CLAIM(lO6GyCvbDm8@31:56) single-source.

## Sub-skills

| Sub-skill | File | Load when |
|---|---|---|
| Step plan | references/step-plan.md | Writing or reconciling the plan list; choosing the 9-step versus lean form |
| Time budget and driving | references/time-budget-and-driving.md | Allocating a 45-60 minute round; handling steering and scope cuts |
| Interviewer signals | references/interviewer-signals.md | Reading what the round scores; genre and seniority expectations |
| Mock drill | references/mock-drill.md | Running and scoring a practice round against one of the 13 worked cases |

## Decision tables

Genre, by what the prompt asks (cited):

| Prompt shape | Genre | Where to spend | Cite |
|---|---|---|---|
| "Design <whole product>" | Product design | Broad shallow structure per feature; defend feature choice | CLAIM(Tu-hZ6lqNtY@01:21) CLAIM(Tu-hZ6lqNtY@01:45) CLAIM(Tu-hZ6lqNtY@16:20) |
| "Design <one feature> in depth" | Feature system design | The hard mechanism, with full plan | CLAIM(HR2jXy_wPg4@02:16) |
| "Design <reusable component>" | Component design | Public API, props, reuse, widget-internal state | CLAIM(9aOXGE7wAZo@00:33) |

Plan form (cited):

| Situation | Plan form | Cite |
|---|---|---|
| General interview, 2023 style | 9-step: requirements, advanced features, mockup, API, state, problems, performance, security, accessibility | CLAIM(9mjsRrJYOWE@01:14) |
| Data-heavy or multi-window problem | Lean 7-step: requirements+mockup, layout, data model, API, data flow, synchronization, multi-window | CLAIM(HR2jXy_wPg4@02:16) |
| Short time box or one-feature drill | Ordered stage plan only, ~15 minutes per feature | CLAIM(5vyKhm2NTfw@01:13) CLAIM(5vyKhm2NTfw@01:09) |

## Anti-patterns

- Opening with architecture before requirements and plan. Refuted by
  CLAIM(3MADCVqL534@01:12) CLAIM(9mjsRrJYOWE@01:14).
- Drawing a full component diagram live. Refuted by CLAIM(fmIiDLbLc_s@12:14).
- Polishing a mockup instead of reasoning about the hard part. Refuted by
  CLAIM(tsGarhpWOws@07:59) CLAIM(HR2jXy_wPg4@05:50).
- Solving the whole app when the interviewer asked for one narrowed piece. Refuted by
  CLAIM(3MADCVqL534@05:44).
- Memorized solutions the candidate cannot explain. Refuted by CLAIM(v4Dt4FalMOA@23:35).
- Silent fast solves. Refuted by CLAIM(v4Dt4FalMOA@21:21) CLAIM(v4Dt4FalMOA@22:21).

## Worked cases

- 9mjsRrJYOWE "Typeahead component" (steal: the 9-step board plan executed end to end).
- HR2jXy_wPg4 "Frontend System Design - Financial Dashboard / TradingView" (steal: the lean
  plan order and the product demo opener).
- tsGarhpWOws "Notion-like editor" (steal: plan-first with core/advanced requirement split).
- Tu-hZ6lqNtY "[Front-End Product Design] - Netflix" (steal: genre separation and shallow breadth).
- 3MADCVqL534 "[Front-End System Design] - Pinterest" (steal: asking the interviewer for platform
  constraints and surviving scope narrowing).
- 5vyKhm2NTfw "[Front End System Design] - Facebook News Feed" (steal: the 15 minute self time box).

## Dated / contestable

- The 2020 episodes express browser coverage as a percentage minus IE11. IE11 reached end of
  support in 2022. Distiller note (not the author): keep the percentage-plus-named-exclusions
  habit, but name current evergreen exclusions instead. CLAIM(3MADCVqL534@06:54)
- The behavioral memorization advice (write out stories against roughly 50 questions and memorize
  them when English is weak) sits against the same author's rule never to lie or recite what you
  cannot explain. Distiller note (not the author): memorize the story beats and numbers, not
  sentences. CLAIM(v4Dt4FalMOA@16:08) CLAIM(v4Dt4FalMOA@23:35)
- The v4Dt4FalMOA interview is a Russian-language podcast (published 2026-07-10); its wording is
  a paraphrase back from Russian captions, so phrasings are approximate while the advice is not.

## Hand-off

- Next stage: fesd-requirements (stage S02), which turns the plan's first step into a written
  requirements artifact.
- Adjacent estate skills: fe-system-design-doctrine for the corpus-wide doctrine, fesd-career-prep
  for the wider interview loop, hm.technical and plan.readiness rubric packs for scoring,
  app-web-frontend for build slices, emil-design-eng for UI polish, fixing-accessibility and
  fixing-motion-performance for the a11y and motion passes named in the plan.
