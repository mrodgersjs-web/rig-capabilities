# Case: [Front-End System Design] - Data Table Component

Source: https://www.youtube.com/watch?v=u6jhTo13_No (video id u6jhTo13_No). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video u6jhTo13_No against the local transcript.

- published 2021-01-12 / duration 2703s (~45 min) / problem type: component-design (generic data table component, framework-agnostic)

## Author's framework as used
1. Standard plan first: general requirements (what the tool does and what API is expected), then functional requirements (how it works, platforms, technical details). CLAIM(u6jhTo13_No@01:06)
2. Component architecture: high-level mockup plus a dependency graph, so later data handling is understandable. CLAIM(u6jhTo13_No@01:29)
3. Replace data-entity design with prop design: what the component takes as input and how it processes it. CLAIM(u6jhTo13_No@01:44)
4. Event API design as its own stage: how consumers subscribe to cell clicks, row selection, page changes. CLAIM(u6jhTo13_No@02:00)
5. Store design: how input data is held inside the tool. CLAIM(u6jhTo13_No@02:23)
6. Optimization and accessibility, plus one extra closing stage he names explicitly: extensibility, how the tool can be extended or formatted to user requirements. CLAIM(u6jhTo13_No@02:37)
7. Mid-a11y he remembers missing props and adds them on the spot (filter and search functions), showing the plan is re-checked as he goes. CLAIM(u6jhTo13_No@43:25)

## Worked design
- Requirements: multiple data formats (date/number/text) with custom cell formatting; per-column custom render; sorting per column + query search; optional CSV export (ask); thousands of rows; strong performance across old and new devices; screen-reader access; CSS API; configurable columns (hide, sortable flag, name, comparator), CLAIM(u6jhTo13_No@03:05).
- Components: JTTable root with Header and RowList; header holds ColumnHeader per column; rows hold Row then Column per cell; the render element is the consumer-defined slot (highlighted in his diagram), CLAIM(u6jhTo13_No@08:54).
- Props: generic data array of objects; column descriptors (name, comparator, hidden, sortable, render); pagination, pageSize, className; later added filter and search functions, CLAIM(u6jhTo13_No@10:18).
- Event API: on(event, callback) with DataTableEvent = cell select, row select, page change; lifecycle destroy() and initialize(), CLAIM(u6jhTo13_No@16:24).
- Data model: state holds data[], filtered data[], sort columns + direction, columns, listeners, searchable flag, class names, current page + page size, cached row elements, CLAIM(u6jhTo13_No@19:13).
- Data flow: state feeds header with all columns and row list with data; a row gets one data item; a cell resolves the column key against the item; the resolved piece goes to the render element, CLAIM(u6jhTo13_No@22:50).
- Realtime: none; updates arrive through async filter functions (client worker or server promise) and repaint the table, CLAIM(u6jhTo13_No@37:04).
- Perf: asset compression + minify, ES5/ES6 bundles, modular core/utils/themes split, CDN, pagination over virtualization, constant node count, DOM reuse with updaters, flat CSS, CSS animations, placeholders, Web Workers/server filtering, event delegation, CLAIM(u6jhTo13_No@26:01).
- A11y: semantic table markup (SEO + screen readers), rem sizing, keyboard navigation, search/filter shortcuts, ARIA labels/descriptions, CLAIM(u6jhTo13_No@40:51).
- Extensibility: CSS API, custom column render functions, ES6 inheritance, CLAIM(u6jhTo13_No@39:44).

## Trade-offs he names
- Virtualization vs pagination for tables: virtualization gives infinite scroll with a fixed node set, but table data is complex and users want an exact page -> pagination fits data tables better. CLAIM(u6jhTo13_No@30:46)
- Index as column key vs key-in-descriptor: an index key assumes objects with consistent key order; a descriptor key is more correct but more complex -> he takes the index for simplicity and says why. CLAIM(u6jhTo13_No@23:51)
- Re-render column vs update function: custom render formats would force full column re-renders -> optional update function lets even custom formats patch cheaply. CLAIM(u6jhTo13_No@21:06)
- Web Worker vs server-side filtering: both keep the UI thread free -> decide from the consumer's function shape (async local data vs promise-returning server filter). CLAIM(u6jhTo13_No@37:04)
- div-based layout flexibility vs table semantics: divs are more layout-flexible but table tags win on SEO and screen readers -> he takes the user-first semantic route. CLAIM(u6jhTo13_No@41:43)
- Per-element listeners vs delegated root listener: many listeners leak memory and die with destroyed elements -> delegate from the root with data attributes. CLAIM(u6jhTo13_No@37:45)
- Always-on features vs interview-driven features: CSV export depends on the interviewer -> ask rather than assume. CLAIM(u6jhTo13_No@05:01)

## Anti-patterns he warns about
- Creating and merging new DOM nodes for every table update instead of patching cached nodes. CLAIM(u6jhTo13_No@31:50)
- Nested CSS selectors and JS animations in a table UI. CLAIM(u6jhTo13_No@33:06)
- Running large filter operations synchronously on the UI thread. CLAIM(u6jhTo13_No@35:38)
- Attaching listeners to every cell/row element instead of delegating from the root. CLAIM(u6jhTo13_No@37:45)
- Building tables from divs and patching the accessibility gap with heavy ARIA afterwards. CLAIM(u6jhTo13_No@40:51)
- Shipping one universal bundle with polyfills every consumer pays for. CLAIM(u6jhTo13_No@26:39)

## Dated / contestable
- "RAMs" in the transcript is rem units, not memory; same garbling family as in the other videos of this series. CLAIM(u6jhTo13_No@42:14)
- The pagination-over-virtualization call is opinionated: modern data grids routinely virtualize with frozen headers and keyboard nav, and infinite scroll plus virtualization is often the 2024+ default even for tables. Claim holds for the "exact page of complex data" use case he names. CLAIM(u6jhTo13_No@30:46)
- ES5 targeting and polyfill economy matter much less post-IE11. CLAIM(u6jhTo13_No@26:39)
- Index-based column keys are fragile advice he himself flags; today's default would be explicit field keys or typed column definitions end to end. CLAIM(u6jhTo13_No@23:51)
- "CSS animations perform better than JS animations" is broadly true for simple transitions but contested for orchestrated/interactive animation (JS-driven WAAPI and transforms are fine). CLAIM(u6jhTo13_No@33:54)
