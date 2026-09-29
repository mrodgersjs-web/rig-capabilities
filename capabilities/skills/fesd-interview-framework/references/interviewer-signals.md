# Interviewer signals: what the round actually scores

Purpose: map the observable signals a front-end system design interviewer rewards or penalizes,
and set expectations by genre and seniority.

When to load: when preparing the mental model of the round, when debriefing a practice or real
interview, and when deciding what "good" looks like before scoring with hm.technical.

## Step checklist

1. Identify the genre before judging anything; each genre has a different depth target.
   CLAIM(Tu-hZ6lqNtY@01:21) CLAIM(9aOXGE7wAZo@00:33)
2. Assume standardized pools and scoring criteria at large companies; prepare to the rubric, not
   to the person. CLAIM(v4Dt4FalMOA@08:49)
3. Watch the two scored channels: the reasoning narration and the finished structure.
   CLAIM(v4Dt4FalMOA@21:21)
4. At staff and above, expect probing of real scaling experience, not course material.
   CLAIM(v4Dt4FalMOA@13:28)
5. Treat silent solving and memorized code as scoring failures even when the artifact is right.
   CLAIM(v4Dt4FalMOA@22:21) CLAIM(v4Dt4FalMOA@23:35)
6. Note which features the candidate chose to defend; product design has no single correct
   feature set. CLAIM(Tu-hZ6lqNtY@01:45)
7. For behavioral-adjacent questions in the loop, expect written stories against the common
   question list. CLAIM(v4Dt4FalMOA@16:08)

## Decision table

| Signal observed | Read it as | Response | Cite |
|---|---|---|---|
| Candidate designs before a plan is written | Process failure | Stop, write the plan | CLAIM(9mjsRrJYOWE@01:14) |
| Deep component spec in a product round | Wrong genre | Pull back to shallow breadth | CLAIM(Tu-hZ6lqNtY@01:21) CLAIM(Tu-hZ6lqNtY@16:20) |
| Server-contract focus in a component round | Wrong genre | Move to public API and reuse | CLAIM(9aOXGE7wAZo@00:33) |
| Fast silent solve with no narration | Lost reasoning points | Narrate; partial explained beats fast silent | CLAIM(v4Dt4FalMOA@21:21) CLAIM(v4Dt4FalMOA@22:21) |
| Fluent code the candidate cannot explain | Memorization flag | Probe; never keep it in | CLAIM(v4Dt4FalMOA@23:35) |
| Interviewer steers to optimization or a11y | Scored pivot | Take it; both were prepped | CLAIM(3MADCVqL534@03:55) |
| Scope is narrowed mid-round | Scored focus test | Drop the rest | CLAIM(3MADCVqL534@05:44) |
| Candidate demos and explains the real product | Strong opener | Do it first, then name the hard problems | CLAIM(tsGarhpWOws@01:07) CLAIM(HR2jXy_wPg4@00:33) |

## Laws for this sub-topic

- Identify the interview genre first: product design wants a holistic view of the whole app, not
  a single feature's complete design. CLAIM(Tu-hZ6lqNtY@01:21) consensus.
- Accept that product design has no single correct feature set; choose the important features
  and be ready to defend the choice. CLAIM(Tu-hZ6lqNtY@01:45) single-source.
- Walk the live product first and enumerate what it actually does before writing any design.
  CLAIM(Tu-hZ6lqNtY@02:05) consensus.
- Keep the product-design answer shallow by design: high-level structure per feature instead of
  deep component specs. CLAIM(Tu-hZ6lqNtY@16:20) single-source.
- For component interviews, shift attention from server contracts to the component's public API
  and reuse story. CLAIM(9aOXGE7wAZo@00:33) consensus.
- Explain and, if possible, demo the real product before proposing any architecture.
  CLAIM(tsGarhpWOws@01:07) consensus.
- Declare conflict resolution out of scope for a frontend system design, mention it, and move on
  rather than designing CRDTs. CLAIM(tsGarhpWOws@04:20) single-source.
- Prepare against big tech's standardized question pools and scoring criteria rather than to
  whatever an interviewer improvises. CLAIM(v4Dt4FalMOA@08:49) single-source.
- Write out your work stories against the roughly 50 common behavioral questions and memorize
  them when your English is weak. CLAIM(v4Dt4FalMOA@16:08) single-source (see dated note).
- For staff-and-above system design, do not rely on courses: senior interviewers probe for real
  experience scaling infrastructure through practical cases. CLAIM(v4Dt4FalMOA@13:28) single-source.
- Record yourself while practicing and learn to narrate your reasoning, because the interviewer
  scores the thinking signal, not only the finished code. CLAIM(v4Dt4FalMOA@21:21) single-source.
- Prefer a clearly explained partial solution over a fast silent solve, since visible
  understanding passes even when time runs out. CLAIM(v4Dt4FalMOA@22:21) single-source.
- Never memorize a solution you cannot explain: interviewers probe understanding and memorized
  code in an unknown language is detectable. CLAIM(v4Dt4FalMOA@23:35) single-source.

## Worked cases

- Tu-hZ6lqNtY "[Front-End Product Design] - Netflix": the genre argument and the shallow-breadth
  answer, live.
- 9aOXGE7wAZo "[Front-End System Design] - Typeahead Widget": the component-genre alternative
  (public API and reuse instead of server contracts).
- tsGarhpWOws "Frontend System Design - Notion": demo-first opener and explicit out-of-scope call.
- v4Dt4FalMOA "FAANG engineer on salaries, interviews and hedge funds": what big-tech loops
  score and how they probe (podcast, Russian captions; wording approximate).
