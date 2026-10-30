---
name: traject-drill
description: "Traject OS sub-skill, stages 7-8 (drill, interview-day): run mock/live drills against a Traject room, score answers with the pre-interview run.py shape, and coach through interview day. Gated by JEV interview.answer, training.readiness, hm.technical, screen.pitch. Every answer states a number or NONE; the floor is never spoken. DEFER when the classifier is down."
tags: [rig, traject-os, sub-skill, drill, interview, coaching]
metadata:
  parent: traject-os
  tier: sub
  stage: drill
  covers: [drill, interview-day]
  extends: "pre-interview-meta, lucy-skills"
outcome: "A drilled run with per-answer scores (qid, scores, gap, quote) and a coach verdict, then an interview-day run where every answer carried a number or NONE and no banned claim or floor was spoken."
activation: "Load when drilling a room before a screen, or running live coaching on interview day."
instruction: "Drill room cards with the pre-interview scoring shape, score each answer with interview.answer and training.readiness, and on interview day coach with hm.technical and screen.pitch. Enforce numbers-or-NONE and never speak the floor; a DEFERRED judge is never a pass."
applies_when:
  env: "the Traject cockpit live-coach / pre-interview; ~/.aside Pre-interview .os runtime"
  runtime: "pre-interview-meta run.py score; lucy liveCoachSimulation.ts"
  deps: "a built room (traject-room-build); pre-interview-meta; JEV interview.answer"
  params: "room, drill mode (mock/live), question set"
  budget: "reps per session; three fix attempts per weak answer before a new story"
  scale: "one room per drill session"
permissions:
  - fs.read
  - fs.write
  - bash
  - browser.read
flow:
  - Load the room and pick the drill mode (mock reps or live coach).
  - Score each answer with interview.answer (and training.readiness for readiness).
  - On interview day, coach with hm.technical / screen.pitch; enforce numbers-or-NONE.
  - Hand gaps to traject-debrief and traject-learn.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/interview.answer.json"
  - "file:capabilities/harnesses/s1gate/rubrics/training.readiness.json"
out_of_scope:
  - building the room content (traject-room-build)
  - stating the compensation floor or any banned claim in a drill or live answer
  - inventing a number the résumé does not support
---

# traject-drill

JEV FIRST: answer verdicts go to `rig-s1gate check interview.answer` (and
`training.readiness`, `hm.technical`, `screen.pitch` on interview day) BEFORE any frontier
call. Classifier down: DEFER, never guess. Required signals above 0.9.

Sub-skill of `traject-os`, stages 7-8. Main skills: `pre-interview-meta`, `lucy-skills`.
Agent: `traject-coach-grader`. Harnesses: `traject-drill-rep` (drill),
`traject-interview-prep-session` (interview day).

## Procedure

1. **Load the room** built by `traject-room-build`. Pre-interview score shape:
   `run.py score --payload '{"qid","scores","gap","quote"}'` (see the lucy audit).
2. **Drill reps**: work the room cards (TMAY ≤90s, STAR bank, question bank, close). Score each
   answer with `rig-s1gate check interview.answer`; `training.readiness` gates whether Mike is
   ready for the real screen.
3. **Numbers or NONE (TL-01)**: every answer states a number or the literal NONE. The Sep 17
   Salesforce transcript failure — answering the adjacent question 3x with zero numbers in 30
   minutes — is the gate this rep is measured against.
4. **Never speak the floor (TL-02)**: the compensation floor is a decision input only. A trainer
   recall card that drilled saying the floor aloud was fixed 2026-09-28; keep it fixed.
5. **Interview day**: coach live with `hm.technical` / `screen.pitch`. Consult, don't audition;
   interviewer ≥40% talk; equalizer pause; never "good question".
6. **Hand gaps** to `traject-debrief` (5-line) and `traject-learn`.

## Lessons that fire here

- **TL-01** every answer states a number or NONE (Sep 17 Salesforce transcript).
- **TL-02** never state the floor aloud in a drill or a live answer.
