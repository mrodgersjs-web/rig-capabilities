# Time budget and driving the round

Purpose: allocate a 45-60 minute design round across the plan stages, and handle interviewer
steering, scope cuts, and drawing economy without losing the clock.

When to load: when scheduling practice, when the round starts, and whenever an answer is running
long or the interviewer redirects.

## Step checklist

1. Write the plan with rough minute marks before the first design word.
   CLAIM(5vyKhm2NTfw@01:09)
2. Ask which platforms and browsers matter in the first minutes; the answer changes the design.
   CLAIM(3MADCVqL534@01:38)
3. Expect the interviewer to steer toward optimization or accessibility; prepare both.
   CLAIM(3MADCVqL534@03:55)
4. If scope is narrowed, drop everything else and stay where pointed.
   CLAIM(3MADCVqL534@05:44)
5. Raise optional features as questions, not assumptions. CLAIM(u6jhTo13_No@05:01)
6. Sketch hierarchies only; never draw full component diagrams live.
   CLAIM(fmIiDLbLc_s@12:14)
7. Skip a polished mockup; use a rough one only to anchor the component hierarchy.
   CLAIM(tsGarhpWOws@07:59)
8. Bound the data model so the live reasoning stays tractable. CLAIM(HR2jXy_wPg4@21:06)
9. Keep minutes for the closing requirements re-check. CLAIM(lO6GyCvbDm8@31:56)

## A 45-60 minute budget

Distiller note (not the author): the author never gives a full-round minute table; he gives a 15
minute box per feature for self practice CLAIM(5vyKhm2NTfw@01:09) and a set of drawing and
steering rules. The allocation below is derived from those rules and from how his episodes
actually spend their runtime; treat it as a practice scaffold, not as his table.

| Minutes | Stage | Anchor |
|---|---|---|
| 0-5 | Product walk, genre call, two hardest problems, plan on the board | CLAIM(HR2jXy_wPg4@00:33) CLAIM(Tu-hZ6lqNtY@01:21) CLAIM(9mjsRrJYOWE@01:14) |
| 5-13 | Requirements (core then advanced), platforms asked out loud | CLAIM(tsGarhpWOws@02:41) CLAIM(3MADCVqL534@01:38) |
| 13-18 | Mockup and component hierarchy, rough only | CLAIM(tsGarhpWOws@07:59) CLAIM(fmIiDLbLc_s@12:14) |
| 18-30 | Layout, data model, API | CLAIM(HR2jXy_wPg4@02:16) CLAIM(HR2jXy_wPg4@21:06) |
| 30-42 | The hard feature (the two named problems) | CLAIM(HR2jXy_wPg4@00:33) |
| 42-50 | Performance, security, accessibility as named steps | CLAIM(9mjsRrJYOWE@03:39) |
| 50-55 | Interviewer steering buffer (optimization or accessibility) | CLAIM(3MADCVqL534@03:55) |
| 55-60 | Requirements re-check and candidate questions | CLAIM(lO6GyCvbDm8@31:56) |

Time compression rules: when the interviewer narrows scope, delete whole rows from the middle,
never the requirements step or the closing check. CLAIM(3MADCVqL534@05:44) When a schema is
well known (feed, chat, table), spend near-zero minutes drawing it because it was pre-built.
CLAIM(5vyKhm2NTfw@07:38) CLAIM(HR2jXy_wPg4@05:50)

## Laws for this sub-topic

- Time-box the design exercise (about 15 minutes for one feature).
  CLAIM(5vyKhm2NTfw@01:09) single-source.
- Pre-build the schemas for well-known interview problems so you do not burn interview minutes
  drawing from scratch. CLAIM(5vyKhm2NTfw@07:38) consensus.
- Ask the interviewer which platforms and target browsers matter before designing, because the
  answer changes the design. CLAIM(3MADCVqL534@01:38) single-source.
- Be ready for the interviewer to steer focus toward either optimization or accessibility and
  prepare both. CLAIM(3MADCVqL534@03:55) single-source.
- If the interviewer narrows the scope (for example just the masonry layout), stay there; the
  time budget cannot cover everything. CLAIM(3MADCVqL534@05:44) single-source.
- Bring a prepared mockup and requirements slide to save interview time, then reason live about
  the hard parts instead. CLAIM(HR2jXy_wPg4@05:50) consensus.
- Bound the data model deliberately (asset, start, end, interval, points) because every extra
  parameter makes the design harder to reason about in the interview.
  CLAIM(HR2jXy_wPg4@21:06) single-source.
- Do not draw full component diagrams in a design interview; sketch a high-level hierarchy only,
  because detailed drawing burns the time budget. CLAIM(fmIiDLbLc_s@12:14) consensus.
- Skip drawing a polished mockup in a real interview; use one only to anchor the component
  hierarchy discussion. CLAIM(tsGarhpWOws@07:59) consensus.
- Prepare diagrams in advance; producing every schema live is impractical without a whiteboard.
  CLAIM(Tu-hZ6lqNtY@13:51) consensus.
- Raise optional features (for example CSV export) as a question to the interviewer instead of
  assuming them. CLAIM(u6jhTo13_No@05:01) single-source.
- After the design, re-check the original requirements list so nothing promised is left
  undesigned. CLAIM(lO6GyCvbDm8@31:56) single-source.

## Worked cases

- 3MADCVqL534 "[Front-End System Design] - Pinterest": the interviewer narrows the problem and
  the design stays on masonry.
- 5vyKhm2NTfw "[Front End System Design] - Facebook News Feed": a full plan inside a 15 minute
  self-imposed box.
- HR2jXy_wPg4 "Frontend System Design - Financial Dashboard / TradingView": prepared slides and
  bounded data model as time savers.
- lO6GyCvbDm8 "[Front-End System Design] - Design a Poll Widget": closing requirements re-check.
