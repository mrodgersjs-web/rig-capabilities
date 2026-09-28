# Idea engines: matrix, collision, trend, Eden cards

Sub-skill of lv-plan. Four engines feed one idea pool. Every idea that reaches the slate carries a
moat (story, proprietary data or physical proof), a receipt, and the job it does in the week.

## 1. Pillar-format matrix (breadth engine)

Grid the lane's 3-5 pillars (rows) against eight proven post shapes (columns) and fill every cell
with one concrete headline idea, specific enough to start drafting and impossible to reuse in
another cell. Aim for 30 or more ideas per run.

| shape | what the idea must do |
|---|---|
| Actionable | teach one specific move the reader can execute today |
| Motivational | tell one real person's extraordinary result as a story, not a pep talk |
| Analytical | break down why a mechanism works, with the numbers visible |
| Contrarian | refuse a common practice and back the refusal with evidence |
| Observation | name a quiet trend the buyer has not seen articulated yet |
| X versus Y | compare two tools, frameworks or companies on one axis that matters to the buyer |
| Present versus Future | today's state against one dated prediction, with the reasoning shown |
| Listicle | a list of mistakes, lessons, tools or steps that a buyer would forward internally |

Rules: 3-5 pillars, no more; every cell is a headline, not a theme; the language follows the lane's
voice profile; below 3 pillars the grid has nothing to pair against.

## 2. Collision engine (Lane A worldview articles)

The deterministic generator: a well-known cultural artifact crossed with a decades-deep veteran
lens, unified onto one worldview skeleton, closed on unresolved tension. It produces articles and
on-brand cards without ever naming AI in the prose.

- Three banks: cultural artifacts, veteran lenses, worldview skeletons, plus 22 collision types.
- Scoring: BlendValue (novelty, systematicity, weighted provocation) with two hard floors that kill
  a piece even at a high score: commodity (a competitor could publish it) and preach (Mike speaks
  the moral himself).
- Funnel metric: qualified DMs weighted highest, then comments, saves and dwell; likes excluded.
- Commands run through the collision engine script (banks, score, score-all, generate) and the card
  builder. The Hermes command `/rig-collider` is the deterministic entrypoint wrapper: pure Python,
  zero AI cost, JSON receipt per run, and the receipt is the proof that the run happened.
- Sealed gold articles live in the engine's own state files; the gallery build is deterministic.
- Note: the module path recorded inside the `/rig-collider` command file did not resolve at build
  time (2026-09-28); call the engine through the command file or locate the module before assuming
  the wrapper works.

## 3. Trend pipeline (live signals)

The daily competitor and industry scan returns a JSON trend report (multi-provider fetch with
fallbacks). Planning use:

- A trend earns a slot only when it clears three tests: it touches a pillar, it carries a receipt,
  and the lane holds credibility to comment on it.
- Borrowed-name openings stay a minority of the slate and repay the borrowed attention with real
  insight.
- Trend reports are inputs to the matrix and the weekly slate, never a substitute for them.

## 4. Eden idea engine (cards for today)

The Eden-resident idea engine hands 5-8 concrete cards a person could post today, fused from three
legs: the user's own saved captures, breakout posts in the niche this week, and creators just
outside the niche whose formats transfer. Planning rules worth keeping:

- An idea card must stand on at least two of the three legs; one-leg ideas get cut.
- Never re-pitch anything from the last three runs, anything queued, or anything already published.
- Hooks on the cards follow the lane's voice profile; no generic growth-account phrasing.
- If only three ideas clear the bar, deliver three. Padded cards kill the idea habit.
- Drafting one into the Eden scheduler is a separate, user-initiated step and stays a draft.

The Eden content command center (Analyst, Scout, Strategist, Planner, Repurposer stations) is the
dashboard version of this pipeline; its Planner station consumes this stage's slate and its Scout
station feeds the market lane. Own posts are never market evidence in any station.

## Choosing the engine

| situation | engine |
|---|---|
| "fill next week" or "I need volume of ideas" | pillar-format matrix |
| "one big article that is unmistakably mine" | collision engine (Lane A only) |
| "what is moving right now" | trend pipeline, then the matrix |
| "what can I post today" | Eden idea engine cards |

Absorbed from: content-matrix, rig-collision-engine, /rig-collider, idea-engine, content-command-center.
