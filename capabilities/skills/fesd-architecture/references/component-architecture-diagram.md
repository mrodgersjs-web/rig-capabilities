# Component architecture diagram (S03 sub-skill)

Purpose: turn a requirement set into the boxes he actually draws (app route, router, page, controller/store, API client, cache, view components), with the layers and roles named before any widget detail.

When to load: when you must draw, critique, or narrate the high-level diagram for a front-end system design answer, or decide the layer split for a canvas-style layout.

## Step checklist

1. Write the design order on the board first (requirements, components, entities, API, store, flagship feature, optimization, accessibility), so the diagram has an assigned slot and cannot swallow the round. CLAIM(5vyKhm2NTfw@01:28)
2. For large multi-team apps, assume the shared design system before drawing pages: typography, UI primitives, grid, common components. CLAIM(Tu-hZ6lqNtY@07:44)
3. Enumerate the page inventory, then draw only the pages that carry key flows; say which pages are named but not designed. CLAIM(Tu-hZ6lqNtY@08:40)
4. Give the acquisition (sign up) page real attention; it is the conversion surface. CLAIM(Tu-hZ6lqNtY@08:55)
5. Show structural reuse between pages (search page = main page minus promo block) instead of drawing a second page. CLAIM(Tu-hZ6lqNtY@14:42)
6. Start the schema at the application route and descend: router, page route, page content, then widget detail. CLAIM(tsGarhpWOws@08:47)
7. Prefer the SPA shape when an item selected on the left must instantly render content in the center. CLAIM(tsGarhpWOws@09:48)
8. For reconfigurable 2D layouts, pick CSS grid over flexbox. CLAIM(HR2jXy_wPg4@07:48)
9. Split the canvas into named layers: grid container, draggable-cell layer, chart/content layer spanned onto the grid by column and row ranges. CLAIM(HR2jXy_wPg4@16:55)
10. Multi-window: one host window owns state writes and fetching, extensions are read-only, roles discovered through shared localStorage, events over BroadcastChannel. CLAIM(HR2jXy_wPg4@57:01) CLAIM(HR2jXy_wPg4@57:42) CLAIM(HR2jXy_wPg4@58:58)
11. For reusable components, classify the architecture variant (stateless / stateful-static / hybrid) before the diagram goes deep. CLAIM(9mjsRrJYOWE@06:20)
12. Mark the distribution boundary on the diagram: npm package for reuse, embed route for third-party hosts. CLAIM(9aOXGE7wAZo@35:04) CLAIM(lO6GyCvbDm8@32:18)

## Laws for this sub-topic

- Diagram order: plan first, then mockup, then the dependency/box graph; the graph is what you reason about data flow against. CLAIM(5vyKhm2NTfw@01:28) consensus (the same mockup-then-graph habit runs in 3MADCVqL534@11:50 and 5vyKhm2NTfw@07:14).
- Design-system precondition for large apps. CLAIM(Tu-hZ6lqNtY@07:44) single-source.
- Page inventory with a designed subset. CLAIM(Tu-hZ6lqNtY@08:40) single-source.
- Acquisition page first-class. CLAIM(Tu-hZ6lqNtY@08:55) single-source.
- Structural reuse between pages over duplicate page designs. CLAIM(Tu-hZ6lqNtY@14:42) single-source.
- Top-down schema descent from application route. CLAIM(tsGarhpWOws@08:47) single-source.
- SPA shape for instant cross-pane rendering. CLAIM(tsGarhpWOws@09:48) single-source (implied).
- CSS grid over flexbox for a resizable 2D layout the user reconfigures. CLAIM(HR2jXy_wPg4@07:48) single-source.
- Three-layer canvas: grid container, draggable-cell layer, spanned content layer. CLAIM(HR2jXy_wPg4@16:55) single-source.
- Single host writer, localStorage role discovery, BroadcastChannel events. CLAIM(HR2jXy_wPg4@57:01) CLAIM(HR2jXy_wPg4@57:42) CLAIM(HR2jXy_wPg4@58:58) single-source.
- Variant classification before detail. CLAIM(9mjsRrJYOWE@06:20) single-source.
- Package boundary (npm) on the diagram. CLAIM(9aOXGE7wAZo@35:04) consensus (lO6GyCvbDm8@05:08).
- Embed route boundary on the diagram. CLAIM(lO6GyCvbDm8@32:18) single-source.

## Decision table

| Diagram question | Pick | When |
|---|---|---|
| One page per view vs shared skeleton | Shared skeleton with a subtracted block | Two views differ by one region (main vs search). CLAIM(Tu-hZ6lqNtY@14:42) |
| Flexbox vs CSS grid for the canvas | CSS grid | Users resize and rearrange a 2D layout. CLAIM(HR2jXy_wPg4@07:48) |
| Per-cell handlers vs container-level | Container-level with data attributes | Many cells; one delegated handler keeps memory flat. CLAIM(HR2jXy_wPg4@13:53) |
| Multi-writer vs single-writer windows | Single writer (host) | Any multi-window feature. CLAIM(HR2jXy_wPg4@60:03) |
| Full detail in the tree vs lazy branch | Lazy branch fetched on open | Detail payloads are heavy and rarely opened. CLAIM(Tu-hZ6lqNtY@28:47) |

## Worked cases

- HR2jXy_wPg4 "Financial Dashboard / TradingView": the sandwich layout and the host/extension window protocol.
- Tu-hZ6lqNtY "Netflix (product design)": page inventory, design-system precondition, structural reuse.
- tsGarhpWOws "Notion-like editor": app-route-first schema descent and the SPA call.
- 3MADCVqL534 "Pinterest": app root to router to pages to pins hierarchy as drawn on the board.
- fmIiDLbLc_s "Google Sheets": component tree kept deliberately at sketch level so decisions get the time.
