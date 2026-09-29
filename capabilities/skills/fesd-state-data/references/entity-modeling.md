# Entity modeling

Purpose: the entity shapes and interface sketches this author draws per case, so a design answer can name its data before it names its components.

When to load: at the start of any S05 pass, whenever "what does the data look like" is still unanswered, or when a case needs its exact field lists reproduced.

## Step checklist

1. List the entities from the requirement sentences: one entity per noun the UI renders or mutates.
2. Give each entity an explicit typed field list in TypeScript notation, name the id field, and mark optional fields optional.
3. Decide the parent/child cut: which child collections get their own request instead of riding inside the parent payload.
4. Fix the date representation: timestamps in state, local time only at render.
5. Add explicit ordering fields where display order is not the natural key order.
6. Bound the model: name what is deliberately out of scope so the design stays finite.
7. Check the model against the store plan in references/client-store-normalization.md before writing endpoints.

## Laws

- Define entities explicitly with full field lists before designing components or endpoints.
  Single-source. (CLAIM(3MADCVqL534@26:44))
- Describe entity shapes in TypeScript notation so the shape is unambiguous. Single-source.
  (CLAIM(5vyKhm2NTfw@09:10))
- Load child collections separately from their parent instead of embedding them in the parent
  payload. Single-source. (CLAIM(3MADCVqL534@27:34))
- Model a post source as a generic origin carrying a type and a name (user, page, group) rather than
  a hard-coded user reference. Single-source. (CLAIM(5vyKhm2NTfw@10:48))
- Store creation dates as timestamps and keep media as a small typed shape of type plus url.
  Single-source. (CLAIM(5vyKhm2NTfw@09:59))
- Treat timestamps as the canonical date representation and convert to local time at render.
  Single-source. (CLAIM(leo1FZ6vu1I@14:29))
- Give a content item id, preview url, title, optional description, tags, child items, rating and an
  author array (the Netflix movie sketch). Single-source. (CLAIM(Tu-hZ6lqNtY@17:39))
- Make child items first-class entities: the episode sketch is id, movie id, preview, title, text,
  watch url, with one entry for a film and many for a series. Single-source.
  (CLAIM(Tu-hZ6lqNtY@18:22))
- Attach cast at the series or movie level, never to individual episodes. Single-source.
  (CLAIM(Tu-hZ6lqNtY@19:58))
- Let an episode carry several stream URLs so playback can pick a rendition by connection quality.
  Single-source. (CLAIM(Tu-hZ6lqNtY@19:43))
- Shape a dashboard response as a map from tag to item array so rows are data-driven. Single-source.
  (CLAIM(Tu-hZ6lqNtY@20:52))
- Store a table as a flat map keyed by row-and-column concatenation, each cell holding formula,
  computed value, type and formatting. Single-source. (CLAIM(fmIiDLbLc_s@35:19))
- Persist formatting as stable enum values rather than CSS class names, so a styling refactor never
  forces a state migration. Single-source. (CLAIM(fmIiDLbLc_s@36:21))
- Model cell dependencies as a directed acyclic graph and evaluate cells in topological order.
  Single-source. (CLAIM(fmIiDLbLc_s@25:42))
- Use topological sorting both to order computation and to detect dependency cycles, and surface an
  error on the affected cells when one exists. Single-source. (CLAIM(fmIiDLbLc_s@28:30))
- Budget the dependency-ordering pass as O(V+E) work. Single-source. (CLAIM(fmIiDLbLc_s@30:26))
- Tokenize formulas with a standard arithmetic parsing algorithm, and import each function
  implementation dynamically only when a formula references it. Single-source.
  (CLAIM(fmIiDLbLc_s@34:47))
- Catch cell edits with one listener at the table level and identify the source cell through
  row/column data attributes. Single-source. (CLAIM(fmIiDLbLc_s@37:48))
- Normalize chat data as contacts keyed by id, message arrays per contact id, and attachments as an
  optional collection. Single-source. (CLAIM(LEaiGjffLEs@25:56))
- Store chart points as minimal open/close pairs so each entry costs a fixed small number of bytes.
  Single-source. (CLAIM(HR2jXy_wPg4@21:22))
- Carry an explicit order field on sortable options instead of inferring order from array position.
  Single-source. (CLAIM(lO6GyCvbDm8@19:36))
- Hold the widget data array, a separate filtered array, and the sort configuration (columns plus
  direction) in the component state shape. Single-source. (CLAIM(u6jhTo13_No@19:13))
- Do not model per-user entity maps when the app effectively has one active user; keep the store
  focused. Single-source. (CLAIM(Tu-hZ6lqNtY@25:33))

## Per-case sketches he draws

| Case | Entities he sketches | Cites |
|---|---|---|
| Pinterest (3MADCVqL534) | pin (id, origin board, description, title, image url, author), comment (author id, content), user (id, nickname) | CLAIM(3MADCVqL534@26:44) |
| Facebook News Feed (5vyKhm2NTfw) | story (id, comments, media, creation timestamp, content, origin, share id), origin (type + name), comment (id, type, author id, media, date, content), media (type + url) | CLAIM(5vyKhm2NTfw@09:10, 5vyKhm2NTfw@10:48, 5vyKhm2NTfw@09:59) |
| Netflix (Tu-hZ6lqNtY) | movie, episode, actor, dashboard map by tag | CLAIM(Tu-hZ6lqNtY@17:39, Tu-hZ6lqNtY@18:22) |
| Google Sheets (fmIiDLbLc_s) | cell (formula, computed value, type, formatting enum) in a row+column keyed map, dependency DAG | CLAIM(fmIiDLbLc_s@35:19, fmIiDLbLc_s@25:42) |
| Google Calendar (leo1FZ6vu1I) | event (id, participants, start/end timestamps, title, rich description), interval tree index of ids | CLAIM(leo1FZ6vu1I@14:29, leo1FZ6vu1I@18:07) |
| Chat application (LEaiGjffLEs) | contact, per-contact message array, optional attachment collection | CLAIM(LEaiGjffLEs@25:56) |
| Financial Dashboard (HR2jXy_wPg4) | finance data (asset, start, end, interval, open/close points) | CLAIM(HR2jXy_wPg4@21:22) |
| Notion-like editor (tsGarhpWOws) | page map by id, per-view plugin data (timeline start/end, calendar timestamp, table columns) | CLAIM(tsGarhpWOws@34:56) |
| Data Table (u6jhTo13_No) | data array, filtered array, sort config, cached row elements | CLAIM(u6jhTo13_No@19:13) |
| Poll Widget (lO6GyCvbDm8) | props, root element reference, reusable element cache, explicit order field | CLAIM(lO6GyCvbDm8@16:23, lO6GyCvbDm8@19:36) |

## Decision table

| Question | Answer | When to deviate | Cites |
|---|---|---|---|
| Typed notation or prose field lists | typed notation | never in a design answer; ambiguity here poisons the store and API stages | CLAIM(5vyKhm2NTfw@09:10) |
| Embed child collections or request them separately | separate request | embed only when the child set is small and always shown with the parent | CLAIM(3MADCVqL534@27:34) |
| Dates as strings or timestamps | timestamps | convert to local strings only at render | CLAIM(leo1FZ6vu1I@14:29) |
| Formatting in state as class names or enums | enums | never class names; they couple state to styling | CLAIM(fmIiDLbLc_s@36:21) |
| One entity per user or one shared store | shared store | add user scoping only when multiple active users are real | CLAIM(Tu-hZ6lqNtY@25:33) |
| Compute order by iteration or dependency graph | DAG + topological order | a flat list is fine only when no cell or field references another | CLAIM(fmIiDLbLc_s@25:42, fmIiDLbLc_s@28:30) |

## Worked cases

- 3MADCVqL534, [Front-End System Design] - Pinterest: the cleanest explicit entity sketch in the corpus.
- 5vyKhm2NTfw, [Front End System Design] - Facebook News Feed: generic origin modeling, worth stealing for any feed with mixed sources.
- Tu-hZ6lqNtY, [Front-End Product Design] - Netflix: parent/child/author hierarchy and where each attaches.
- fmIiDLbLc_s, [Front-End System Design] - Google Sheets: entity plus derived graph in one model.
- LEaiGjffLEs, [Front-End System Design] - Chat application: per-contact arrays as a normalization hint.
