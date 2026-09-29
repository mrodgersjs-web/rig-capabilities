---
name: fesd-component-api
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Owns stage S04 (component design) plus S11 (ux-product) of the Front-End System Design family:
  component trees and dependency graphs, the public API of a reusable widget (props, generic fetch
  contract, render overrides, controlled-style callbacks, lifecycle methods, event API, column and
  cell customization), extensibility surfaces, and the UX states (loading, empty, error,
  optimistic) with product-level feature trade-offs. Use for typeahead, data table, poll widget,
  or any "design a reusable component" round and for component trees inside product designs;
  trigger phrases include "design a component", "what props does it take", "controlled or
  uncontrolled", "render prop / slot", "customization API", "loading and empty states", "how do I
  embed this widget". Distilled from 46 S04 and 6 S11 laws across 11 Front-End Engineer videos
  (Evgenii Ray). JEV-FIRST MANDATE, findable at task start: typed judgments in this stage go to
  rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED is the only answer when the classifier is
  down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, component-design, widget-api, ux-states]
outcome: "code-engineering: a cited component section (tree, prop/event/lifecycle API, customization surfaces, UX states, embedding) reviewable as an API contract"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-component-api/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S04, S11"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Component design and reusable widget API (S04) plus UX/product states (S11)

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

Typed judgments this stage forces, routed to Jev before any frontier LLM call:
1. Is this component API complete enough that every stated requirement has a hook (props, callback, or override)?
2. Is the component tree the right decomposition (small enough leaves, one clear owner of each state)?
3. For rendered UI: does the widget's rendered state meet the design bar (ui.design rubric)?
4. For an API contract: is the prop/event/lifecycle surface coherent and minimal (code.review rubric)?

Command shape: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Nearest existing rubrics: ui.design for rendered UI, code.review for a component API; both advisory until calibrated. A pass needs every required signal above 0.9. Classifier down, erroring, or rubric missing = DEFERRED, never a guessed verdict. An advisory PASS is not permission to ship or publish.

## When to use

- Any "design a reusable component" round: typeahead, data table, poll widget, autocomplete, combobox.
- The component-tree slice of a product design (feeds, pins, cards, editors).
- When the question is how consumers customize or extend a widget (templates, CSS API, inheritance, render hooks).
- When loading, empty, error, or optimistic behavior must be specified (S11).
- Not for high-level architecture (fesd-architecture) or store/normalization depth (S05).

## Inputs and output contract

Consumes: the S02 requirement set for the component (core behavior first, then the configuration layer), and the S03 architecture variant (stateless / stateful-static / hybrid) when one was chosen.

Emits a component section with these headings:
1. Component tree (root, list, item, control) with the dependency graph.
2. Prop contract: data input shape, configuration props, fetch/query callback typing.
3. Rendering contract: default rendering, consumer template/slot, lazy per-item update.
4. Event and lifecycle API: typed events, callbacks, initialize/destroy.
5. Behavior: mode separation (view vs edit), event delegation, resize/layout behavior.
6. Extensibility surfaces: CSS API, render hooks, class inheritance.
7. UX states (S11): loading placeholders, empty, error, and what is optimistic vs refetched.
8. Embedding and distribution (when relevant): route, iframe/script or provider path.

## Procedure

1. Load references/component-tree.md. Build the tree from the mockup, smallest unit first, then draw the dependency graph, because the graph is what you plan data flow against. CLAIM(3MADCVqL534@11:50) CLAIM(5vyKhm2NTfw@07:14) CLAIM(LEaiGjffLEs@03:27)
2. Simplify component sizes for the interview (three pin sizes, not the production set) and keep secondary actions behind one trigger so leaf components stay small. CLAIM(3MADCVqL534@09:25) CLAIM(LEaiGjffLEs@05:08)
3. Load references/reusable-widget-api.md. Replace data-entity design with prop design: for a component the data model is the prop contract. CLAIM(9aOXGE7wAZo@06:06) CLAIM(lO6GyCvbDm8@14:18) CLAIM(u6jhTo13_No@10:18)
4. Type the data-in and function-in contracts generically: getResults(query) returns a promise of T array; the query callback is mandatory in the stateless variant because the host owns the search logic. CLAIM(9aOXGE7wAZo@10:55) CLAIM(9mjsRrJYOWE@24:19)
5. Define configuration props per the requirement list: minQuery, maxResults, cache size, pagination, column descriptors (hideable, sortable flag, custom name, comparator, custom render). CLAIM(9aOXGE7wAZo@06:56) CLAIM(9aOXGE7wAZo@11:56) CLAIM(u6jhTo13_No@07:00) CLAIM(u6jhTo13_No@12:24) CLAIM(u6jhTo13_No@13:48)
6. Split rendering into create and mutate: renderItem (datum to element) plus an optional updateItem (mutate an existing element), so consumers control the item template and the widget keeps a constant node count. CLAIM(9aOXGE7wAZo@12:35) CLAIM(9mjsRrJYOWE@23:25) CLAIM(9mjsRrJYOWE@17:49)
7. Keep the component a pure view over its data: option data minimal, parent owns the rest; callbacks (onVote, onItemSelected) let the caller decide local mutation vs a server call. CLAIM(lO6GyCvbDm8@13:49) CLAIM(lO6GyCvbDm8@14:18) CLAIM(lO6GyCvbDm8@11:46)
8. Expose the imperative shell: typed event API (on) and lifecycle methods initialize(props) / destroy(). CLAIM(u6jhTo13_No@16:24) CLAIM(u6jhTo13_No@17:56) CLAIM(lO6GyCvbDm8@15:21)
9. Behavior details: one delegated handler on the root with data attributes, standard drag events resolved at drop time, chart resize by grid span reassignment, central fetch component passing unified data down with a per-chart transformer. CLAIM(HR2jXy_wPg4@13:38) CLAIM(HR2jXy_wPg4@14:18) CLAIM(HR2jXy_wPg4@14:37) CLAIM(HR2jXy_wPg4@16:38) CLAIM(HR2jXy_wPg4@18:23) CLAIM(HR2jXy_wPg4@19:34)
10. Load references/ux-states.md. Specify loading placeholders and skeletons, and treat extensibility as its own design stage (CSS API, render hooks, class inheritance). CLAIM(9aOXGE7wAZo@27:24) CLAIM(u6jhTo13_No@34:26) CLAIM(lO6GyCvbDm8@29:55) CLAIM(u6jhTo13_No@39:44)
11. If the widget must run on third-party pages, load references/widget-embedding.md and design the embed route and both embedding paths. CLAIM(lO6GyCvbDm8@32:18) CLAIM(lO6GyCvbDm8@33:31)
12. Close with the requirements re-check: walk the original list and confirm nothing promised is left undesigned (he catches his own missing embeddability requirement this way). CLAIM(lO6GyCvbDm8@31:56)

## Core laws

Tree and decomposition
- Draw the component dependency graph after the mockup (app root and router down to leaf components); the graph is what reveals data flow. CLAIM(3MADCVqL534@11:50) CLAIM(5vyKhm2NTfw@07:14) consensus.
- Build from the smallest unit up (contact card first, then lists and views), and keep secondary message actions behind one trigger so the message component stays small. CLAIM(LEaiGjffLEs@03:27) CLAIM(LEaiGjffLEs@05:08) single-source.

Prop and rendering contract
- Make item rendering consumer-defined and ship no opinionated default result template; consumers supply the item template or render override. CLAIM(9aOXGE7wAZo@03:59) CLAIM(9mjsRrJYOWE@17:49) consensus (both typeahead videos).
- Expose configuration as props (cache size, the filter/getResults function, the item representation, minQuery, maxResults), typed generically so the widget is data-type agnostic. CLAIM(9aOXGE7wAZo@06:06) CLAIM(9aOXGE7wAZo@06:56) CLAIM(9aOXGE7wAZo@11:56) CLAIM(9aOXGE7wAZo@10:55) single-source.
- Split rendering into renderItem plus an optional lazy updateItem that mutates one element instead of re-rendering the list. CLAIM(9aOXGE7wAZo@12:35) CLAIM(9mjsRrJYOWE@23:25) consensus (typeahead pair).
- Make the query callback mandatory in the stateless variant, because the host application owns the search logic. CLAIM(9mjsRrJYOWE@24:19) single-source.

Purity and control
- Keep the component pure: it renders given data and carries no business logic; keep option data minimal and let the parent own everything else. CLAIM(lO6GyCvbDm8@13:49) CLAIM(lO6GyCvbDm8@14:18) single-source.
- Give the caller callbacks (onVote with the chosen options) and let the caller decide local mutation vs a server call. CLAIM(lO6GyCvbDm8@11:46) single-source.

Imperative shell and data shape
- Expose a tiny imperative API: initialize(props) and destroy(), plus a typed event API (on) with events like cell selection, row selection, page change. CLAIM(lO6GyCvbDm8@15:21) CLAIM(u6jhTo13_No@17:56) CLAIM(u6jhTo13_No@16:24) consensus (poll widget and data table).
- Type data input as an array of objects (never primitives) and keep columns as separate descriptors that know their type but hold no data; resolve a cell by applying the column key to the data item. CLAIM(u6jhTo13_No@10:18) CLAIM(u6jhTo13_No@23:29) single-source.
- Give each column an optional comparator and an optional custom render function for its cell display. CLAIM(u6jhTo13_No@12:24) CLAIM(u6jhTo13_No@13:48) single-source.

Behavior
- Register one delegated handler on the container and resolve the target via data attributes; use standard drag events and resolve placement at drop time. CLAIM(HR2jXy_wPg4@13:38) CLAIM(HR2jXy_wPg4@14:18) CLAIM(HR2jXy_wPg4@14:37) single-source.
- Encapsulate cross-cutting behavior in one generic container (draggable wrapper accepting any child type), centralize fetching in one component that passes unified data down, and give each chart a transformer from generic source data to its rendering model. CLAIM(HR2jXy_wPg4@17:52) CLAIM(HR2jXy_wPg4@18:23) CLAIM(HR2jXy_wPg4@19:34) single-source.

Extensibility and UX states (S11)
- Treat extensibility as a design stage of its own with three named surfaces: a CSS API, custom render functions, and class-based inheritance. CLAIM(lO6GyCvbDm8@29:55) CLAIM(u6jhTo13_No@39:44) consensus.
- Show skeletons, loaders, and placeholders on slow loads: perceived load time drops even when actual time does not. CLAIM(9aOXGE7wAZo@27:24) CLAIM(u6jhTo13_No@34:26) consensus.

## Sub-skills

| Sub-skill | File | Load when |
|---|---|---|
| Component tree | references/component-tree.md | Drawing or judging the tree/dependency graph, page-level component structure, block taxonomy |
| Reusable widget API | references/reusable-widget-api.md | Designing props, render overrides, callbacks, lifecycle, event API, column/cell customization |
| UX states | references/ux-states.md | Loading/empty/error/optimistic behavior and the S11 product trade-offs |
| Widget embedding | references/widget-embedding.md | Third-party embedding: route, iframe/script, provider registry |

## Decision tables

Control surface (CLAIM(lO6GyCvbDm8@11:46), CLAIM(9mjsRrJYOWE@24:19), CLAIM(9aOXGE7wAZo@19:58))
| Option | Pick when |
|---|---|
| Stateless with mandatory query callback | Default: the host owns data and search logic (about nine cases in ten) |
| Static local data in a closure | Small vocabulary searched without a server |
| Widget-internal cache (TTL, size) | Only when an unchangeable slow API forces it |

Rendering override (CLAIM(9aOXGE7wAZo@03:59), CLAIM(lO6GyCvbDm8@12:28), CLAIM(u6jhTo13_No@13:48))
| Mechanism | Use for |
|---|---|
| Consumer item template / render prop | Whole result item appearance (people vs groups) |
| Per-column render function | Cell-level formatting inside a fixed table shape |
| updateItem / onItemUpdate lazy hook | Cheap in-place refresh when one datum changes |
| CSS API classes | Restyling without changing markup |

Long-data handling (CLAIM(u6jhTo13_No@30:46), CLAIM(9mjsRrJYOWE@47:44), CLAIM(9mjsRrJYOWE@48:33))
| Case | Pick |
|---|---|
| Complex table data, exact page needed | Pagination |
| Long list past roughly a hundred rows | Virtualization (and treat the size as a design smell for typeaheads) |
| Few items (poll options) | No virtualization at all |

Filtering placement (CLAIM(u6jhTo13_No@37:04), CLAIM(9aOXGE7wAZo@29:31), CLAIM(9aOXGE7wAZo@28:34))
| Consumer function shape | Strategy |
|---|---|
| Promise-returning function | Server filtering, repaint on arrival |
| Async local filter over huge data | Web Worker |
| Small local data | Filter inline |

## Anti-patterns

- Stuffing business logic into a display component instead of keeping a pure view. CLAIM(lO6GyCvbDm8@13:49)
- Re-rendering the whole list when one item's data changes. CLAIM(9mjsRrJYOWE@23:37)
- Shipping an opinionated default item template the consumer must fight. CLAIM(9aOXGE7wAZo@03:59)
- Building tables from divs and patching accessibility with heavy ARIA afterwards. CLAIM(u6jhTo13_No@40:51)
- Per-cell or per-item listeners instead of one delegated root handler (leaks, dies with destroyed elements). CLAIM(u6jhTo13_No@37:45)
- Reaching for ARIA before using HTML5 semantics that already carry meaning. CLAIM(lO6GyCvbDm8@27:47)
- Introducing machinery (Web Workers) with no high-cost operation to justify it. CLAIM(lO6GyCvbDm8@25:59)
- Rendering a thousand rows in a typeahead: either the design or the use case is wrong. CLAIM(9mjsRrJYOWE@48:33)
- Finishing without re-checking the design against the stated requirements list. CLAIM(lO6GyCvbDm8@31:56)

## Worked cases

| Video | Title | Steal this |
|---|---|---|
| 9aOXGE7wAZo | Typeahead Widget | Prop contract (getResults typing, minQuery, maxResults, renderItem/updateItem), fixed-size query cache |
| 9mjsRrJYOWE | Typeahead component | Variant-aware API split, mandatory query callback, lazy per-item update, race handling |
| u6jhTo13_No | Data Table Component | Column descriptor model, comparator + custom render, event API + lifecycle, pagination over virtualization |
| lO6GyCvbDm8 | Poll Widget | Pure-view widget, view/edit mode split, initialize/destroy shell, extensibility as a stage |
| HR2jXy_wPg4 | Financial Dashboard | Generic draggable container, delegated drag handling, chart transformer interface, chart sync as a product feature |
| 3MADCVqL534 | Pinterest | Pin shell as interactive component, dependency hierarchy, comment components kept simple |
| 5vyKhm2NTfw | Facebook News Feed | Story card + comment list + input decomposition |
| LEaiGjffLEs | Chat application | Smallest-unit-first tree, secondary actions behind one trigger |
| Tu-hZ6lqNtY | Netflix (product design) | Header/content/footer structure, three card levels |
| tsGarhpWOws | Notion-like editor | Visual/structural/database-connectable component families, token + rule + render-set plumbing |
| leo1FZ6vu1I | Google Calendar | Native capability bridging with consent caveats (S11) |

## Dated / contestable

- The framework-agnostic initialize/destroy widget shell and DOM-element render functions are 2020-2021 vanilla-JS shapes; today's equivalent is typed framework components with the same prop/callback geometry. Distiller note (not the author). CLAIM(lO6GyCvbDm8@15:21) CLAIM(9aOXGE7wAZo@09:59)
- Index-based column keys (an index accepted for simplicity) are fragile; today's default is an explicit field key or typed column definitions end to end. Distiller note (not the author). CLAIM(u6jhTo13_No@23:29)
- The minQuery default of 3 is convention, not law; search-as-you-type products often run 1 with aggressive debouncing. Distiller note (not the author). CLAIM(9aOXGE7wAZo@11:45)
- Pagination-over-virtualization for tables is opinionated; modern grids routinely virtualize with frozen headers. The claim holds for the exact-page complex-data case he names. Distiller note (not the author). CLAIM(u6jhTo13_No@30:46)
- Embedly-style provider registries are less central than in 2021. Distiller note (not the author). CLAIM(lO6GyCvbDm8@33:31)
- ES5/ES6 dual bundles and polyfill economy largely expired with IE11. Distiller note (not the author). CLAIM(u6jhTo13_No@26:39)

## Hand-off

- Next stage: the S05 state/data-model stage skill for store shape and normalization; the S06 api/network stage skill for request design.
- Adjacent estate skills: app-web-frontend for build slices, emil-design-eng for UI polish, fixing-accessibility (the ARIA/semantics laws here are the interview version of that audit), fixing-motion-performance, app-data-layer, and the api design harness hA-09 where the widget's callback contract becomes a real API.
