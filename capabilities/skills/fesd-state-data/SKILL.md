---
name: fesd-state-data
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Owns stage S05 of front-end system design: the entity shapes, the normalized client store,
  fetching points and id flow, derived indexes, and the client storage and caching decisions
  (runtime state vs IndexedDB, localStorage roles, eviction rules, byte-level storage math).
  Produces the state-and-data artifact that a component layer and an API layer can be built
  against. Use when designing a data model or client store for a front-end system design answer
  or a real client app, when asked "how should I model this data", "normalize the store", "where
  does state live", "how much storage does this need", or when a candidate starts building
  components before entities exist. 61 laws from 12 Front-End Engineer videos. JEV-FIRST
  MANDATE, findable at task start: typed judgments in this stage go to rig-s1gate (Jev) BEFORE
  any frontier LLM call; DEFERRED is the only answer when the classifier is down. Child of
  fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, state, data-model, normalization, caching, storage]
outcome: "code-engineering: a typed entity model plus a normalized, bounded client store with cited laws"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-state-data/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S05"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# FE system design S05: state and data model

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-architect loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate

Typed judgments this stage forces, and which go to Jev first:

1. Is this entity list complete enough to design the store against, with no unmodeled noun the UI renders (kind: plan.readiness).
2. Is the proposed store shape normalized so every record read is a single keyed lookup (kind: plan.readiness).
3. Does the storage math hold at the stated data rate before the scheme is committed (kind: plan.readiness).
4. Is every cache bounded by a named eviction rule instead of growing without limit (kind: plan.readiness).

Command shape: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
Nearest existing rubric: plan.readiness, advisory until calibrated. A pass needs every required
signal above 0.9. Classifier down, erroring, or rubric missing = DEFERRED, never a guessed
verdict. An advisory PASS is not permission to ship or publish; here it only means the state
design may be treated as ready to design an API against.

## When to use

- After requirements and before component or API design: the entities decide both.
- When a design answer stores nested response objects straight into components.
- When asked how much client storage a data set needs, or whether history belongs in memory or on disk.
- When a widget or table needs a cache, a sort config, or a filtered view of its data.

## Inputs and output contract

Input: the S02 requirement list (features, platforms, data volume and freshness expectations) and
any S03/S04 component sketch that names what renders.

Output artifact: a state-and-data document with these headings in order:

1. Entities: one typed field list per entity, optional fields marked, ids named (see references/entity-modeling.md).
2. Store shape: each map, what it is keyed by, and what lives outside it (see references/client-store-normalization.md).
3. Fetching points: which component fetches and which ids flow down to children.
4. Derived structures: search, conflict, or dependency indexes, and how they update on mutation.
5. Storage decision: runtime state vs disk, key design, and the byte math (see references/client-caching-and-storage.md).
6. Cache policy: what is cached, the key, the size cap, and the eviction rule.

## Procedure

1. Inventory entities from the requirement sentences: one entity per noun the UI renders, each with
   an explicit typed field list. Load references/entity-modeling.md. Entities are defined before
   components or endpoints, not after them
   (CLAIM(3MADCVqL534@26:44, 5vyKhm2NTfw@09:10)).
2. Cut parent and child: decide which child collections load on their own request instead of riding
   in the parent payload (CLAIM(3MADCVqL534@27:34)), and keep the server representation close to
   the client model so no transformation layer appears (CLAIM(leo1FZ6vu1I@11:32)).
3. Normalize the store into flat id-keyed maps and name one map per entity plus per view
   (CLAIM(3MADCVqL534@32:14, 5vyKhm2NTfw@19:33)). Load references/client-store-normalization.md.
4. Place one fetching point at the page or content level and pass ids down; children read their own
   record by id (CLAIM(3MADCVqL534@33:16, 5vyKhm2NTfw@20:55, Tu-hZ6lqNtY@24:46)).
5. Decide mutations as slice updates: create, update and delete touch only the changed slice and
   never rebuild derived structures wholesale (CLAIM(leo1FZ6vu1I@10:29)).
6. Build derived structures id-only so payload edits never touch the index
   (CLAIM(leo1FZ6vu1I@31:44)), and order any computation dependencies as a graph with cycle
   detection (CLAIM(fmIiDLbLc_s@25:42, fmIiDLbLc_s@28:30)).
7. Choose the storage split and run the byte math before committing: runtime state holds what the
   view needs, bulk history goes to disk (CLAIM(HR2jXy_wPg4@26:25, HR2jXy_wPg4@35:15)). Load
   references/client-caching-and-storage.md.
8. Bound every cache with an explicit rule: oldest entry out past a size cap, or least-recently-used
   eviction on an entry limit (CLAIM(9aOXGE7wAZo@17:14, 9mjsRrJYOWE@28:28)).
9. State the write invariants: one writer for shared storage, readers read-only
   (CLAIM(HR2jXy_wPg4@60:03)), and state updated only through a dispatcher plus handler
   (CLAIM(tsGarhpWOws@13:58)).

## Core laws

Entities and shapes

- Define entities explicitly with full field lists before designing anything downstream: the
  Pinterest sketch is pin (id, origin board, description, title, image url, author), comment
  (author id, content), user (id, nickname). Single-source.
  (CLAIM(3MADCVqL534@26:44))
- Describe entity shapes in TypeScript notation so nothing about the shape is ambiguous.
  Single-source. (CLAIM(5vyKhm2NTfw@09:10))
- Store dates as timestamps and convert to local time at render. Consensus.
  (CLAIM(5vyKhm2NTfw@09:59, leo1FZ6vu1I@14:29))
- Keep the server representation close to the client model so transformation code disappears.
  Single-source. (CLAIM(leo1FZ6vu1I@11:32))

Normalized store

- Store client data as flat id-keyed maps; nested multi-level structures are costly to read from.
  Consensus. (CLAIM(3MADCVqL534@32:14, 5vyKhm2NTfw@19:33, leo1FZ6vu1I@13:10, tsGarhpWOws@34:56))
- Fetch at the page level and pass ids down; each child reads its own record from the store by id.
  Consensus. (CLAIM(3MADCVqL534@33:16, 5vyKhm2NTfw@20:55, Tu-hZ6lqNtY@24:46))
- Keep app state minimal (root ids plus normalized records) and keep view stores such as a
  tag-to-list map or a search store alongside entity stores. Single-source.
  (CLAIM(Tu-hZ6lqNtY@26:44, tsGarhpWOws@34:42))

Mutation and derived structures

- Create, update and delete mutate only the changed slice of the store and never rebuild derived
  structures wholesale. Single-source. (CLAIM(leo1FZ6vu1I@10:29))
- Keep derived indexes id-only and mutate the id-keyed map separately, so payload edits never touch
  the search structure. Single-source. (CLAIM(leo1FZ6vu1I@31:44))
- Model computation dependencies as a directed acyclic graph, evaluate in topological order, and
  surface an error on affected cells when a cycle exists. Single-source.
  (CLAIM(fmIiDLbLc_s@25:42, fmIiDLbLc_s@28:30))

Bounding and storage

- Split storage: keep only what the view needs in runtime state and put bulk history on disk in
  IndexedDB. Single-source. (CLAIM(HR2jXy_wPg4@26:25))
- Compute worst-case storage (points per day, bytes per point, per year) before committing to a
  storage scheme. Single-source. (CLAIM(HR2jXy_wPg4@35:15))
- Bound every cache with a size cap and an eviction rule: evict the oldest entry past the cap, or
  evict least-recently-used past an entry limit. Consensus.
  (CLAIM(9aOXGE7wAZo@17:14, 9mjsRrJYOWE@28:28))

Widget state

- Keep component state minimal (the passed props, a root element reference, a reusable element
  cache) and update cached elements in place instead of re-inserting nodes. Consensus.
  (CLAIM(lO6GyCvbDm8@16:23, lO6GyCvbDm8@18:07, u6jhTo13_No@20:27))

## Sub-skills

| Sub-skill | File | Load when |
|---|---|---|
| Entity modeling | references/entity-modeling.md | before writing any entity, interface, or typed field list; when a case needs its exact sketch |
| Client store normalization | references/client-store-normalization.md | when shaping the store, placing fetching points, or wiring mutations and derived indexes |
| Client caching and storage | references/client-caching-and-storage.md | when choosing memory vs disk, designing keys or buckets, sizing storage, bounding caches, or deciding multi-window write ownership |

## Decision tables

| Decision | Option A | Option B | Pick when | Cites |
|---|---|---|---|---|
| Store shape | nested response trees | flat id-keyed maps | flat maps whenever one record is read from more than one place; nested trees cost access | CLAIM(3MADCVqL534@32:14, 5vyKhm2NTfw@19:33) |
| Fetching point | per-component fetch | one page-level fetch, ids down | page-level fetch; children read the store by id | CLAIM(3MADCVqL534@33:16, Tu-hZ6lqNtY@24:46) |
| Child collections | embedded in parent payload | separate request | separate when the child set is large or independently paged | CLAIM(3MADCVqL534@27:34) |
| History storage | all in runtime state | runtime state + IndexedDB | split when bulk history outgrows what the view needs | CLAIM(HR2jXy_wPg4@26:25) |
| Time-series rows | one row per point | fixed time buckets | buckets when range queries dominate; raw points force linear scans | CLAIM(HR2jXy_wPg4@29:56, HR2jXy_wPg4@31:47) |
| Cache eviction | oldest out past a cap | LRU past an entry cap | either bounded variant; an unbounded cache is not an option | CLAIM(9aOXGE7wAZo@17:14, 9mjsRrJYOWE@28:28) |
| Formatting state | CSS class names | stable enum values | enums, so a styling refactor never forces a state migration | CLAIM(fmIiDLbLc_s@36:21) |
| User scoping | per-user entity maps | single store | single store when the app has one active user | CLAIM(Tu-hZ6lqNtY@25:33) |
| Shared storage writes | every window writes | one host window writes | single writer; extensions are read-only replicas | CLAIM(HR2jXy_wPg4@60:03) |

## Anti-patterns

- Nesting entities several levels deep and reading through the tree at render time
  (CLAIM(3MADCVqL534@32:14)).
- Storing one point per timestamp and scanning it for every range query
  (CLAIM(HR2jXy_wPg4@29:20)).
- Letting a query cache grow past its cap with no eviction rule (CLAIM(9aOXGE7wAZo@17:14)).
- Rebuilding derived structures wholesale on every mutation (CLAIM(leo1FZ6vu1I@10:29)).
- Carrying payload inside a derived index so every edit touches both structures
  (CLAIM(leo1FZ6vu1I@31:44)).
- Persisting CSS class names as state (CLAIM(fmIiDLbLc_s@36:21)).
- Letting several windows write shared storage (CLAIM(HR2jXy_wPg4@60:03)).
- Assuming upsampled detail can be produced from local data (the finer bucket is on the server)
  (CLAIM(HR2jXy_wPg4@44:11)).

## Worked cases

- HR2jXy_wPg4, Frontend System Design - Financial Dashboard / TradingView: bucketed IndexedDB with a
  compound key and the byte-level storage math. Steal: the arithmetic that turns an opinion into a
  checkable claim (CLAIM(HR2jXy_wPg4@35:15)).
- fmIiDLbLc_s, [Front-End System Design] - Google Sheets: flat cell map plus a dependency DAG with
  topological evaluation and cycle detection. Steal: derived computation modeled as a graph
  (CLAIM(fmIiDLbLc_s@25:42)).
- leo1FZ6vu1I, [Front-End System Design] - Google Calendar: flat event map with an id-only interval
  tree for conflict detection. Steal: index and payload kept apart (CLAIM(leo1FZ6vu1I@31:44)).
- 5vyKhm2NTfw, [Front End System Design] - Facebook News Feed: typed entity sketch with a generic
  origin and id-keyed store maps. Steal: the entity-writing discipline (CLAIM(5vyKhm2NTfw@09:10)).
- 3MADCVqL534, [Front-End System Design] - Pinterest: explicit entities, separate comment loading,
  normalized store, ids passed down. Steal: the full S05 sequence (CLAIM(3MADCVqL534@32:14)).
- Tu-hZ6lqNtY, [Front-End Product Design] - Netflix: movie/episode/actor hierarchy, dashboard map by
  tag, separate search store. Steal: view stores next to entity stores (CLAIM(Tu-hZ6lqNtY@26:44)).
- LEaiGjffLEs, [Front-End System Design] - Chat application: contacts by id with per-contact message
  arrays and timestamp-checkpoint sync. Steal: sync markers as state (CLAIM(LEaiGjffLEs@26:30)).
- tsGarhpWOws, Frontend System Design - Notion-like editor: normalized page map, reducer-style
  updates, static area reuse keyed by a page hash. Steal: minimal app state (CLAIM(tsGarhpWOws@34:42)).
- 9mjsRrJYOWE, Typeahead component: trie vocabulary store and the LRU-capped variant. Steal: a data
  structure chosen for the access pattern (CLAIM(9mjsRrJYOWE@28:05)).
- 9aOXGE7wAZo, [Front-End System Design] - Typeahead Widget: query-keyed fixed-size cache and
  fetch-more-than-visible paging state. Steal: the eviction rule (CLAIM(9aOXGE7wAZo@17:14)).
- u6jhTo13_No, [Front-End System Design] - Data Table Component: data array, filtered array, sort
  config and cached row elements in one widget state. Steal: the state inventory
  (CLAIM(u6jhTo13_No@19:13)).
- lO6GyCvbDm8, [Front-End System Design] - Design a Poll Widget: minimal widget state with an element
  cache and an explicit order field. Steal: element caching over re-insertion
  (CLAIM(lO6GyCvbDm8@18:07)).

## Dated / contestable

- The IndexedDB quota framing of roughly 2 GB per domain is approximate and browser-dependent.
  Distiller note (not the author): quotas are origin- and browser-specific and eviction policies
  differ, so measure in the target browser rather than assuming a number.
  (CLAIM(HR2jXy_wPg4@27:08))
- "LRU trie" is his own naming for the capped, LRU-evicting variant, and he says so. Distiller note
  (not the author): use an existing capped/LRU library rather than implementing his label.
  (CLAIM(9mjsRrJYOWE@06:12, 9mjsRrJYOWE@34:23))
- The line that caching is unneeded in most scenarios is a heuristic he offers, not a measurement.
  Distiller note (not the author): treat it as a default to argue against, not a law.
  (CLAIM(9mjsRrJYOWE@05:14))
- Offline state is described through the browser application-cache mechanism in the older episodes.
  Distiller note (not the author): that API is deprecated and removed; service workers own offline
  caching now. (CLAIM(5vyKhm2NTfw@40:02, leo1FZ6vu1I@55:40))
- ES5-era bundling and polyfill framing appears in the state and widget discussions of the 2020-2022
  videos. Distiller note (not the author): differential module builds and browserslist-driven
  transpilation are the current answer, and the goal (small modern payload) is unchanged.
  (CLAIM(leo1FZ6vu1I@52:56, u6jhTo13_No@26:39))
- Index-based column keys in the data table are fragile advice he himself flags. Distiller note (not
  the author): explicit field keys or typed column definitions end to end are the modern default.
  (CLAIM(u6jhTo13_No@23:51))

## Hand-off

Next stage skill: fesd-api-network (S06) to put an API surface over this store, then the realtime
stage (S07) for update delivery, and the performance stage (S08) for rendering budgets.

Adjacent estate skills: app-web-frontend for build slices, emil-design-eng for UI polish,
fixing-accessibility, fixing-motion-performance, app-data-layer for backend and persistence slices,
and the api design harness hA-09 where an API contract review is needed.
