# Mock drill: running and scoring a practice round

Purpose: a repeatable protocol for one practice round against a corpus worked case, ending in a
hm.technical score through Jev and one named fix.

When to load: when scheduling practice, when someone asks "how do I rehearse this", and before
declaring a candidate ready for a real loop.

## Step checklist

1. Pick one worked case from the 13 below, matching the genre the candidate will face.
   CLAIM(Tu-hZ6lqNtY@01:21)
2. Set the clock at 45-60 minutes (or 15 minutes for a single-feature drill) and do not extend
   it. CLAIM(5vyKhm2NTfw@01:09)
3. Candidate writes the plan on the board and announces the order; score whether the plan exists
   before any design. CLAIM(9mjsRrJYOWE@01:14) CLAIM(fmIiDLbLc_s@05:57)
4. Candidate walks the real product (or the component consumer context) and names the two
   hardest problems. CLAIM(HR2jXy_wPg4@00:33) CLAIM(tsGarhpWOws@01:07)
5. Interviewer plays one steering event mid-round: either optimization or accessibility, plus
   one scope narrowing. CLAIM(3MADCVqL534@03:55) CLAIM(3MADCVqL534@05:44)
6. Candidate narrates continuously; the drill is recorded.
   CLAIM(v4Dt4FalMOA@21:21)
7. Candidate closes with the requirements re-check. CLAIM(lO6GyCvbDm8@31:56)
8. Score the round: run `~/.rig/bin/rig-s1gate check hm.technical --file <recording-notes> --subject "mock <case> sha256:<hash>" --json`.
   Advisory until calibrated; DEFERRED when the classifier is down and never a guessed verdict.
9. Record exactly one fix (plan order, time overrun, unparrated reasoning, missed re-check) and
   carry it into the next drill.

## Scoring dimensions for the drill record

Distiller note (not the author): these are drill record fields derived from the cited laws; the
author describes what interviewers notice, not a formal rubric.

| Field | Pass looks like | Cite |
|---|---|---|
| Plan-first | Ordered plan on the board before design talk | CLAIM(9mjsRrJYOWE@01:14) |
| Genre fit | Depth matches product, feature, or component round | CLAIM(Tu-hZ6lqNtY@01:21) CLAIM(9aOXGE7wAZo@00:33) |
| Product grounding | Real product walked, two hard problems named | CLAIM(HR2jXy_wPg4@00:33) |
| Steering response | Took the narrowing, prepped both pivots | CLAIM(3MADCVqL534@03:55) CLAIM(3MADCVqL534@05:44) |
| Narration | Reasoning audible the whole way | CLAIM(v4Dt4FalMOA@21:21) CLAIM(v4Dt4FalMOA@22:21) |
| Explainability | Every line of the design can be explained on probe | CLAIM(v4Dt4FalMOA@23:35) |
| Quality steps | Performance, security, accessibility named as steps | CLAIM(9mjsRrJYOWE@03:39) |
| Closure | Requirements list re-checked | CLAIM(lO6GyCvbDm8@31:56) |

## The 13 worked cases to drill against

1. 5vyKhm2NTfw "[Front End System Design] - Facebook News Feed": plan discipline and infinite
   scroll in a 15 minute box.
2. 3MADCVqL534 "[Front-End System Design] - Pinterest": masonry layout, scope narrowing.
3. Tu-hZ6lqNtY "[Front-End Product Design] - Netflix": product-genre breadth drill.
4. LEaiGjffLEs "[Front-End System Design] - Chat application": latency budgets and protocol
   comparison.
5. 9aOXGE7wAZo "[Front-End System Design] - Typeahead Widget": component-genre public API drill.
6. lO6GyCvbDm8 "[Front-End System Design] - Design a Poll Widget": distribution, embedding,
   sync and async modes.
7. gxF9fLo5XQw "Deep dive into HTTP [Part 1]": concept deep-dive drill (the answer is a mental
   model, not a UI).
8. fmIiDLbLc_s "[Front-End System Design] - Google Sheets": rendering strategy choice (canvas
   versus DOM) inside a plan.
9. leo1FZ6vu1I "[Front-End System Design] - Google Calendar": multi-view entity consistency.
10. u6jhTo13_No "[Front-End System Design] - Data Table Component": scale, sorting, accessibility
    requirements.
11. 9mjsRrJYOWE "Typeahead component": the full 9-step plan executed slowly.
12. tsGarhpWOws "Frontend System Design - Notion": core versus advanced requirements split.
13. HR2jXy_wPg4 "Frontend System Design - Financial Dashboard / TradingView": the lean plan and
    quantified data model.

## Laws for this sub-topic

- Time-box the design exercise (about 15 minutes for one feature).
  CLAIM(5vyKhm2NTfw@01:09) single-source.
- Record yourself while practicing and learn to narrate your reasoning.
  CLAIM(v4Dt4FalMOA@21:21) single-source.
- Prefer a clearly explained partial solution over a fast silent solve.
  CLAIM(v4Dt4FalMOA@22:21) single-source.
- After the design, re-check the original requirements list so nothing promised is left
  undesigned. CLAIM(lO6GyCvbDm8@31:56) single-source.

## Decision table

| Drill outcome | Next action | Cite |
|---|---|---|
| Plan missing or late | Repeat same case, plan-only pass first | CLAIM(9mjsRrJYOWE@01:14) |
| Time overrun past the box | Repeat with the derived budget in references/time-budget-and-driving.md | CLAIM(5vyKhm2NTfw@01:09) |
| Silent stretches in recording | Repeat with narration-only rule | CLAIM(v4Dt4FalMOA@21:21) |
| Probe finds an unexplainable line | Repeat the same case and cut that line from the design | CLAIM(v4Dt4FalMOA@23:35) |
| All fields pass | Move to the next genre case | CLAIM(Tu-hZ6lqNtY@01:21) |
