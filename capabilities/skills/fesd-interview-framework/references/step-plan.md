# Step plan: the written design plan and its two shapes

Purpose: give the candidate one ordered plan to write on the board before design talk, and the
rules for reconciling the 9-step 2023 form with the lean 2025 form.

When to load: at the start of any mock or real round, and whenever a plan is being drafted or a
practice answer is being structured.

## Step checklist

1. Classify the round genre first (product / feature / component). CLAIM(Tu-hZ6lqNtY@01:21)
2. Walk the real product, or state the component's consumer context, and name the two hardest
   problems. CLAIM(HR2jXy_wPg4@00:33) CLAIM(tsGarhpWOws@01:07)
3. Write the plan list on the board, first two items being core requirements then advanced
   requirements. CLAIM(tsGarhpWOws@02:41)
4. Announce you will work the list in order; do not let the talk wander.
   CLAIM(9mjsRrJYOWE@01:14) CLAIM(fmIiDLbLc_s@05:57)
5. Reserve named plan steps for performance, security, accessibility.
   CLAIM(9mjsRrJYOWE@03:39)
6. Choose the plan form from the decision table below before step 4.
7. If you bring prepared material (schema, mockup, requirements slide), say so and use it to buy
   reasoning time. CLAIM(5vyKhm2NTfw@07:38) CLAIM(HR2jXy_wPg4@05:50) CLAIM(Tu-hZ6lqNtY@13:51)
8. Close by re-checking the requirements list against what got designed.
   CLAIM(lO6GyCvbDm8@31:56)

## The two plan shapes

9-step form (2023 remake of the typeahead episode): requirements, advanced features, mockup, API,
state, problems, performance, security, accessibility. CLAIM(9mjsRrJYOWE@01:14) The 2020 episodes
run the same skeleton: general requirements, specific requirements, component architecture and
dependency graph, data entities, data API, data store, the flagship interaction, optimization,
accessibility. CLAIM(5vyKhm2NTfw@01:13) CLAIM(3MADCVqL534@01:12) CLAIM(Tu-hZ6lqNtY@02:05)

Lean 7-step form (2025 financial dashboard episode): requirements and mockup, layout, data model,
API, data flow, synchronization, multi-window. CLAIM(HR2jXy_wPg4@02:16)

Reconciliation (Distiller note (not the author), built from the two cited plans): the difference
is compression, not contradiction. The lean form folds mockup into requirements, replaces the
generic "problems" step with the domain's own hard step (here synchronization and multi-window),
and drops the explicit performance/security/accessibility steps because that episode is a data and
layout problem. Use the 9-step form by default; use the lean form when the problem is data-model
heavy or multi-window, and always keep at least one closing quality step even if it is named in
one line.

## Decision table

| Situation | Plan form | Cite |
|---|---|---|
| Default interview, unknown format | 9-step | CLAIM(9mjsRrJYOWE@01:14) |
| Data-heavy, state-heavy, multi-window | Lean 7-step | CLAIM(HR2jXy_wPg4@02:16) |
| Product design over a whole app | Requirements, functional requirements, architecture and components, data entities, data API, data store, optimization, accessibility, kept shallow | CLAIM(Tu-hZ6lqNtY@02:05) CLAIM(Tu-hZ6lqNtY@16:20) |
| Component design | Requirements tiers, mockup, dependency graph, prop/API design, widget state, optimization, accessibility | CLAIM(9aOXGE7wAZo@00:33) |
| Self practice, one feature | Ordered stage plan, 15 minute box | CLAIM(5vyKhm2NTfw@01:13) CLAIM(5vyKhm2NTfw@01:09) |

## Laws for this sub-topic

- Start the interview by writing the design plan, beginning with requirements collection.
  CLAIM(3MADCVqL534@01:12) consensus.
- Open the answer by writing the ordered stage plan for the whole design before any component
  work. CLAIM(5vyKhm2NTfw@01:13) consensus.
- Put a written plan on the board before any design talk and work it in order: requirements,
  advanced features, mockup, API, state, problems, performance, security, accessibility.
  CLAIM(9mjsRrJYOWE@01:14) consensus.
- Give performance, security and accessibility their own plan steps.
  CLAIM(9mjsRrJYOWE@03:39) single-source.
- Follow a fixed plan order: requirements and mockup, layout, data model, API, data flow,
  synchronization, multi-window. CLAIM(HR2jXy_wPg4@02:16) single-source.
- State an action plan up front that lists the design sections in the order you will execute
  them. CLAIM(fmIiDLbLc_s@05:57) consensus.
- Write the design plan on the board before drawing, and split requirements into core and
  advanced sections as its first two items. CLAIM(tsGarhpWOws@02:41) consensus.

## Worked cases

- 9mjsRrJYOWE "Typeahead component": the 9-step plan on the board, step numbers spoken aloud.
- HR2jXy_wPg4 "Frontend System Design - Financial Dashboard / TradingView": the lean plan read
  out before the design, then executed in that order.
- tsGarhpWOws "Frontend System Design - Notion": plan-first with the core/advanced split.
- fmIiDLbLc_s "[Front-End System Design] - Google Sheets": explicit action plan of sections.
- 5vyKhm2NTfw "[Front End System Design] - Facebook News Feed": ordered stage plan in the tight
  self time box.
