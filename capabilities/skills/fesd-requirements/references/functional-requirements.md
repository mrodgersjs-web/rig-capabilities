# Functional requirements: capabilities, behaviors, and configuration

Purpose: write the requirement block that says what the user can do and what behaviors the system
must support, before any architecture talk.

When to load: at the start of requirements collection for a product, feature, or component
problem, and when a design doc lacks a capabilities section.

## Step checklist

1. Open with the feature statement plus the basic user actions it must support.
   CLAIM(5vyKhm2NTfw@04:02)
2. Write general requirements as user-visible capabilities (search, preview, watch) before any
   architecture talk. CLAIM(Tu-hZ6lqNtY@04:41)
3. Define the core behavior of the artifact first (a typeahead returns result items for the
   typed query). CLAIM(9aOXGE7wAZo@03:27)
4. State media or format scope with explicit outs (pin types gif and picture, video out).
   CLAIM(3MADCVqL534@05:08)
5. Add the data-shape rules: static and async sources, any data type.
   CLAIM(9aOXGE7wAZo@04:40) CLAIM(9mjsRrJYOWE@04:33)
6. Add the configuration layer second: cache TTL, cache size, max results, custom item template.
   CLAIM(9mjsRrJYOWE@17:28)
7. Define interaction semantics explicitly (vote and revoke, single and multiple answer).
   CLAIM(lO6GyCvbDm8@03:08)
8. Add modes (read-only for unauthenticated users, sync mode without a server, async server-backed
   mode). CLAIM(lO6GyCvbDm8@03:47) CLAIM(lO6GyCvbDm8@08:05)
9. State the product's core interaction as a requirement where it is the product (markdown syntax
   transforming into components as the user types). CLAIM(tsGarhpWOws@05:02)
10. Keep every list generic: one event entity, serializable entities, extensible formats and
    components. CLAIM(leo1FZ6vu1I@09:57) CLAIM(leo1FZ6vu1I@10:15) CLAIM(fmIiDLbLc_s@03:32)
    CLAIM(tsGarhpWOws@05:22)
11. Bake in data utilities the problem implies (date/number/text formats, sort by any column,
    search by query). CLAIM(u6jhTo13_No@03:05) CLAIM(u6jhTo13_No@04:33)

## Decision table

| If the artifact is | Lead requirement | Then add | Cite |
|---|---|---|---|
| Reusable widget | core behavior + public data shape | static/async sources, config layer | CLAIM(9aOXGE7wAZo@03:27) CLAIM(9mjsRrJYOWE@17:28) |
| Multi-view app | one entity shape across views | serializable entities, import/export | CLAIM(leo1FZ6vu1I@09:57) CLAIM(leo1FZ6vu1I@10:15) |
| Embeddable component | voting or interaction semantics | read-only mode, sync and async modes, npm package | CLAIM(lO6GyCvbDm8@03:08) CLAIM(lO6GyCvbDm8@08:05) |
| Editor with custom syntax | core interaction as a requirement | extendable component library | CLAIM(tsGarhpWOws@05:02) CLAIM(tsGarhpWOws@05:22) |
| Data component | common formats | sorting, filtering, search | CLAIM(u6jhTo13_No@03:05) CLAIM(u6jhTo13_No@04:33) |

## Laws for this sub-topic

- State media scope in requirements: pin types (gif, picture) and explicitly what is out (video).
  CLAIM(3MADCVqL534@05:08) single-source.
- Express general requirements as the feature statement plus the basic user actions it must
  support. CLAIM(5vyKhm2NTfw@04:02) consensus.
- Define the core behavior first: the widget returns result items for the query the user types.
  CLAIM(9aOXGE7wAZo@03:27) single-source.
- Support both static and asynchronous data, and accept any data shape rather than one entity
  type. CLAIM(9aOXGE7wAZo@04:40) consensus.
- State the general behaviors first: autocomplete from user input, a data-type-agnostic model,
  efficient requests with cached results, and support for both async and static data sources.
  CLAIM(9mjsRrJYOWE@04:33) consensus.
- Add a configuration layer second: cache TTL, cache size, max results, and a custom item
  representation template. CLAIM(9mjsRrJYOWE@17:28) single-source.
- Demand one unified data interface across heterogeneous and legacy data sources so a single
  fetcher can serve every chart. CLAIM(HR2jXy_wPg4@03:35) single-source.
- Keep the server-side data model generic and let each chart type own its display model plus its
  transform. CLAIM(HR2jXy_wPg4@03:57) single-source.
- Write general requirements as user-visible capabilities (search, preview, watch) before any
  architecture talk. CLAIM(Tu-hZ6lqNtY@04:41) consensus.
- Split requirements into general product requirements first and device/behavior requirements
  second. CLAIM(fmIiDLbLc_s@03:13) consensus.
- Design formatting support generically so that a new format type can be added without redesign.
  CLAIM(fmIiDLbLc_s@03:32) single-source.
- Define a default grid size but design for extension beyond it.
  CLAIM(fmIiDLbLc_s@03:44) single-source.
- Define voting semantics up front: vote and revoke, single-answer and multiple-answer modes.
  CLAIM(lO6GyCvbDm8@03:08) single-source.
- Design a read-only mode for unauthenticated users so results are visible without voting rights.
  CLAIM(lO6GyCvbDm8@03:47) single-source.
- Require both sync (no server, client session only) and async (server-backed) modes so the
  widget works standalone. CLAIM(lO6GyCvbDm8@08:05) single-source.
- Enumerate general product requirements (views, multi-user, live updates, conflict spotting,
  import/export) before constraints. CLAIM(leo1FZ6vu1I@01:50) consensus.
- Keep the event entity identical across every view so no view invents its own duplicate shape.
  CLAIM(leo1FZ6vu1I@09:57) single-source.
- Keep entities JSON-serializable in both directions so export and import come for free.
  CLAIM(leo1FZ6vu1I@10:15) single-source.
- State the product's core interaction as a requirement: typed markdown syntax must transform
  into components live as the user types. CLAIM(tsGarhpWOws@05:02) single-source.
- Require the component library to be extendable so new components can be added to the custom
  syntax later. CLAIM(tsGarhpWOws@05:22) single-source.
- Support the common data formats out of the box: date (custom format), number, text.
  CLAIM(u6jhTo13_No@03:05) single-source.
- Bake in sorting and filtering: sort by any column, configurable per column, plus search by
  query. CLAIM(u6jhTo13_No@04:33) single-source.

## Worked cases

- 9mjsRrJYOWE "Typeahead component": the general-behavior block and the configuration layer.
- lO6GyCvbDm8 "[Front-End System Design] - Design a Poll Widget": semantics and modes written as
  requirements before any component work.
- leo1FZ6vu1I "[Front-End System Design] - Google Calendar": one entity shape across views.
- u6jhTo13_No "[Front-End System Design] - Data Table Component": formats and utilities as
  functional requirements.
- tsGarhpWOws "Frontend System Design - Notion": the core interaction as a requirement.
- HR2jXy_wPg4 "Frontend System Design - Financial Dashboard / TradingView": unified interface
  over heterogeneous sources.
