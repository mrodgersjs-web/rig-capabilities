---
name: traject-debrief
description: "Traject OS sub-skill, stage 9 (debrief): capture the 5-line debrief after every screen or interview. CODE gate on the 5-line shape (question asked / actual answer / ownership gap sentence / number stated or NONE / next question). Saves to the debrief store and the room's debrief tab. DEFER JEV where present; never invent an answer."
tags: [rig, traject-os, sub-skill, debrief, interview]
metadata:
  parent: traject-os
  tier: sub
  stage: debrief
  extends: "pre-interview-meta, aside-job-learning"
outcome: "A 5-line debrief per question (question asked, actual answer in his words, ownership gap sentence, number stated or NONE, next question) saved to the debrief store and the room's debrief tab, feeding traject-learn."
activation: "Load within 2 hours of any screen or interview, or when Mike recalls an interview to debrief."
instruction: "Write the 5-line debrief exactly (question asked / actual answer in his words / ownership gap sentence / number stated or NONE / next question), save it to <project>/.traject/debriefs/ and the room's debrief tab, and route ownership gaps and missed numbers to traject-learn. The 5-line shape is a CODE gate; do not pad or invent."
applies_when:
  env: "the Traject cockpit room debrief tab; <project>/.traject/debriefs/"
  runtime: "markdown debrief store; room data module"
  deps: "a drilled or held interview (traject-drill); pre-interview-meta"
  params: "company, role, interview date, questions asked"
  budget: "≤2h after the interview; one debrief per interview"
  scale: "one debrief file per interview"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Within 2h, list the questions actually asked.
  - Write the 5-line debrief per question (CODE gate on the shape).
  - Save to .traject/debriefs/ and the room debrief tab.
  - Route ownership gaps and missing numbers to traject-learn.
done_when:
  - "cmd:python3 capabilities/skills/traject-os/scripts/validate_hierarchy.py"
  - "file:capabilities/harnesses/s1gate/rubrics/rejection.cause.json"
out_of_scope:
  - scoring the interview (traject-coach-grader / traject-drill)
  - inventing what was said; the answer line is his words or NONE
---

# traject-debrief

The 5-line debrief shape is a CODE gate (deterministic, no classifier needed for the shape);
any quality verdict on the content goes to `rig-s1gate check rejection.cause` when the task is
diagnosing a rejection. Classifier down on those: DEFER, never guess.

Sub-skill of `traject-os`, stage 9. Main skills: `pre-interview-meta`, `aside-job-learning`.
Agent: `traject-debrief-clerk`. Harness: `traject-debrief-capture`.

## The 5-line debrief (per question)

1. **Question asked** — the interviewer's question, near-verbatim.
2. **Actual answer** — what Mike actually said, in his words (not what he meant to say).
3. **Ownership gap sentence** — one sentence naming the gap (what he did not own or did not say).
4. **Number stated or NONE** — the concrete number in the answer, or the literal NONE (TL-01).
5. **Next question** — the follow-up the answer invites, or the question to ask next time.

## Where it is saved

- `<project>/.traject/debriefs/<date>-<company>.md` (one file per interview, 5-line blocks).
- The room's **debrief tab** in `src/lib/<company>Content.ts`.
- Ownership gaps and NONE rows flow to `traject-learn` for the Sunday funnel review.

## Lessons that fire here

- **TL-01** the number line is a number or NONE — an adjacent answer with no number is a gap.
- **TL-05** the debrief implies a real Screen/Interview stage, not an ATS_SUBMITTED row.
