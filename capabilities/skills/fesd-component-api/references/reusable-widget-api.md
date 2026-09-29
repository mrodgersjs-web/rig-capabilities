# Reusable widget API (S04 sub-skill)

Purpose: design the public contract of a reusable widget: data-in shape, configuration props, function-in typing, render overrides, callbacks, event API, and lifecycle methods.

When to load: any "design a component API" step, from typeahead to data table to an embeddable poll widget.

## Step checklist

1. Delete data-entity design and design props instead: for a reusable component the prop contract is the data model. CLAIM(9aOXGE7wAZo@06:06) CLAIM(lO6GyCvbDm8@14:18) CLAIM(u6jhTo13_No@10:18)
2. Type data input as an array of objects (never primitives); keep descriptors (columns) separate from data. CLAIM(u6jhTo13_No@10:18)
3. Type the fetch/query function generically: getResults(query) returns a promise of T array, so the widget stays data-type agnostic. CLAIM(9aOXGE7wAZo@10:55)
4. Make the query callback mandatory in the stateless variant; the host owns search logic. CLAIM(9mjsRrJYOWE@24:19)
5. Configuration props from the requirement list: minQuery, maxResults (default 10), cache size, TTL, pagination toggle, page size, className. CLAIM(9aOXGE7wAZo@06:56) CLAIM(9aOXGE7wAZo@11:56) CLAIM(9aOXGE7wAZo@06:06) CLAIM(u6jhTo13_No@14:55)
6. Rendering contract: consumer supplies the item template (no opinionated default), plus optional per-item update hook. CLAIM(9aOXGE7wAZo@03:59) CLAIM(9mjsRrJYOWE@17:49) CLAIM(9aOXGE7wAZo@12:35) CLAIM(9mjsRrJYOWE@23:25)
7. Column-level customization for tables: hideable, sortable flag, custom name, optional comparator, optional custom render function per cell. CLAIM(u6jhTo13_No@07:00) CLAIM(u6jhTo13_No@12:24) CLAIM(u6jhTo13_No@13:48) CLAIM(u6jhTo13_No@03:44)
8. Callbacks carry the outcome, not the policy: onVote(option[]) / onItemSelected and the caller decides local mutation vs a server call. CLAIM(lO6GyCvbDm8@11:46)
9. Event API: a typed subscription surface (on(event, callback)) with events like cell selection, row selection, page change. CLAIM(u6jhTo13_No@16:24)
10. Lifecycle: initialize(props) to re-init with fresh props, destroy() to tear down. CLAIM(u6jhTo13_No@17:56) CLAIM(lO6GyCvbDm8@15:21)
11. Modes as separate renderings of the same data (view mode vs edit mode). CLAIM(lO6GyCvbDm8@09:12)
12. Behavior hooks: one delegated root handler with data attributes for identification, standard drag events resolved at the drop target, resize by grid span reassignment. CLAIM(HR2jXy_wPg4@13:38) CLAIM(HR2jXy_wPg4@14:18) CLAIM(HR2jXy_wPg4@14:37) CLAIM(HR2jXy_wPg4@16:38)
13. Data-flow shape for composed widgets: one component fetches and passes unified data down; each chart/child gets a transformer from generic source data to its own rendering model. CLAIM(HR2jXy_wPg4@18:23) CLAIM(HR2jXy_wPg4@19:34)
14. Keep the widget a pure view: minimal internal data (props mirror, root element reference, cached elements), no business logic. CLAIM(lO6GyCvbDm8@13:49) CLAIM(lO6GyCvbDm8@14:18)
15. Cell resolution: apply the column key to the data item; an index key is acceptable only for objects with consistent key order. CLAIM(u6jhTo13_No@23:29)
16. Customization surface for generic widgets: a CSS customization API when many teams will restyle it. CLAIM(9mjsRrJYOWE@18:24)
17. Cross-cutting behavior in one generic container that accepts any child component type. CLAIM(HR2jXy_wPg4@17:52)

## Laws for this sub-topic (by contract area)

Props and data shape
- Consumer-defined item rendering, no opinionated default template. CLAIM(9aOXGE7wAZo@03:59) CLAIM(9mjsRrJYOWE@17:49) consensus (typeahead pair).
- Configuration props: cache size, filter/getResults function, item representation. CLAIM(9aOXGE7wAZo@06:06) single-source.
- minQuery prop gates filtering. CLAIM(9aOXGE7wAZo@06:56) single-source.
- Generic fetch typing (query to promise of T array). CLAIM(9aOXGE7wAZo@10:55) single-source.
- maxResults prop caps the visible/DOM item count (default 10). CLAIM(9aOXGE7wAZo@11:56) single-source.
- Mandatory query callback in the stateless variant. CLAIM(9mjsRrJYOWE@24:19) single-source.
- Data as array of objects; column descriptors hold types, not data. CLAIM(u6jhTo13_No@10:18) single-source.
- Minimal option data (votes, order, name); parent owns the rest. CLAIM(lO6GyCvbDm8@14:18) single-source.
- Column configurability: hideable, sortable flag, custom name. CLAIM(u6jhTo13_No@07:00) single-source.
- Cell customization function for custom datum formats. CLAIM(u6jhTo13_No@03:44) single-source.
- Optional per-column comparator (two entities to a number). CLAIM(u6jhTo13_No@12:24) single-source.
- Optional per-column render function (datum to element). CLAIM(u6jhTo13_No@13:48) single-source.
- Pagination props: toggle, page size, custom className. CLAIM(u6jhTo13_No@14:55) single-source.
- Cell resolution via column key (index key only for consistent object key order). CLAIM(u6jhTo13_No@23:29) single-source.

Rendering contract (slots / render props)
- renderItem (datum to new element) plus optional updateItem (mutate an existing element). CLAIM(9aOXGE7wAZo@12:35) CLAIM(9mjsRrJYOWE@23:25) consensus (typeahead pair).
- Render-override hooks (renderEditItem, renderItem returning an element) so consumers replace default option rendering. CLAIM(lO6GyCvbDm8@12:28) single-source.
- CSS customization API for generic widgets. CLAIM(9mjsRrJYOWE@18:24) consensus with the extensibility laws (lO6GyCvbDm8@29:55, u6jhTo13_No@39:44).
- View mode vs edit mode as distinct renderings of the same data. CLAIM(lO6GyCvbDm8@09:12) single-source.

Controlled vs uncontrolled (mapping his contract)
- The widget stays a pure view and the caller decides mutation policy through callbacks, which is the controlled shape: state lives with the consumer. CLAIM(lO6GyCvbDm8@13:49) CLAIM(lO6GyCvbDm8@11:46) single-source.
- The uncontrolled shape appears as self-contained modes: static data held in a closure inside getResults for local filtering. CLAIM(9aOXGE7wAZo@19:58) single-source.
- Re-initialization with fresh props (after a server update) is how a controlled consumer refreshes the widget. CLAIM(lO6GyCvbDm8@15:21) CLAIM(u6jhTo13_No@17:56) consensus (poll widget and data table).

Events and lifecycle
- Typed event API (on) with callbacks per event. CLAIM(u6jhTo13_No@16:24) single-source.
- Lifecycle: initialize(props) and destroy(). CLAIM(u6jhTo13_No@17:56) CLAIM(lO6GyCvbDm8@15:21) consensus.
- Callbacks carrying selection outcomes (onVote with chosen options, onItemSelected). CLAIM(lO6GyCvbDm8@11:46) consensus with 9mjsRrJYOWE@24:38.

Behavior
- One delegated handler on the container; identify the target via data attributes. CLAIM(HR2jXy_wPg4@13:38) CLAIM(HR2jXy_wPg4@14:18) single-source.
- Standard drag-and-drop events with placement resolved at the drop-end target cell. CLAIM(HR2jXy_wPg4@14:37) single-source.
- One generic draggable container accepting any child component type. CLAIM(HR2jXy_wPg4@17:52) single-source.
- Centralized fetch component passing unified data down; per-child transformer from generic source data. CLAIM(HR2jXy_wPg4@18:23) CLAIM(HR2jXy_wPg4@19:34) single-source.
- Resize by reassigning grid-column/grid-row spans, not manual repositioning. CLAIM(HR2jXy_wPg4@16:38) single-source.

## Decision tables

| Contract question | Pick | When |
|---|---|---|
| Default item template vs consumer template | Consumer template | Item looks vary by consumer (people, groups, options). CLAIM(9aOXGE7wAZo@03:59) |
| Config flag vs function shape as the strategy switch | Function shape | Let the contract (promise-returning vs async local) decide worker vs server. CLAIM(u6jhTo13_No@37:04) |
| updateItem hook vs full re-render | updateItem hook | One datum changes in a long list. CLAIM(9mjsRrJYOWE@23:25) |
| Comparator vs fixed sort | Comparator per column | Custom data types must sort correctly. CLAIM(u6jhTo13_No@12:24) |
| Callback-only vs callback + imperative shell | Callback + initialize/destroy | Consumers refresh from server data mid-life. CLAIM(u6jhTo13_No@17:56) |
| CSS API vs inheritance vs render hooks | Offer all three | Extensibility is its own design stage. CLAIM(lO6GyCvbDm8@29:55) |
| Index key vs descriptor key for cells | Descriptor key in production | Index keys assume consistent key order. CLAIM(u6jhTo13_No@23:29) |

## Anti-patterns

- One opinionated result template the consumer must override with hacks. CLAIM(9aOXGE7wAZo@03:59)
- Business logic inside the display component. CLAIM(lO6GyCvbDm8@13:49)
- Re-rendering the entire list when a single item updates. CLAIM(9mjsRrJYOWE@23:37)
- Per-cell/per-row listeners instead of delegation from the root. CLAIM(u6jhTo13_No@37:45)
- One universal config flag where the consumer's function shape already tells you the strategy. CLAIM(u6jhTo13_No@37:04)
- Shipping a widget with no lifecycle (no way to re-init or destroy). CLAIM(u6jhTo13_No@17:56)

## Worked cases

- 9aOXGE7wAZo "Typeahead Widget": the full prop contract and the renderItem/updateItem split.
- 9mjsRrJYOWE "Typeahead component": variant-split API, mandatory query callback, onItemUpdate.
- u6jhTo13_No "Data Table Component": column descriptors, comparator, cell render, event API, lifecycle.
- lO6GyCvbDm8 "Poll Widget": pure view, view/edit modes, onVote callback, render overrides, initialize/destroy.
- HR2jXy_wPg4 "Financial Dashboard": delegated drag handling, generic draggable container, per-chart transformer.
