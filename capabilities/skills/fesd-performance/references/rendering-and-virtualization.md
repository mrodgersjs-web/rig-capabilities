# Rendering and virtualization

Purpose: choose and specify how a large or unbounded collection renders, so the mounted DOM stays small, scrolling is paint-bound, and heavy work never blocks the UI thread.

## When to load

Any feed, masonry grid, spreadsheet, data table, chat log, calendar, chart dashboard, or typeahead result list; any complaint about scroll jank, slow re-render, DOM churn, or layout thrash; any question about web workers or canvas vs DOM rendering.

## Step checklist

1. Count what can grow. Name the axis that can explode and the axis you will cap instead of virtualizing.
2. Pick the collection strategy: plain DOM, virtualization, pagination, or prerender-and-slide. Say why in one line.
3. If virtualizing: define zones (visible, rendered buffer, recycle), page size per device class, and a buffer page so chunk swaps are invisible.
4. Keep the scrollbar honest: the container's height reflects loaded-but-unrendered data via padding or a spacer, never via fake nodes.
5. Detect edges with IntersectionObserver on sentinel nodes, not scroll-event math.
6. Recycle nodes with soft writes; absolute-position items and move them with CSS transforms.
7. Decide where computation goes: server for expensive search, web worker for large local filtering or dependency graphs, main thread for everything small.
8. Cap everything that grows (prerendered views, caches, listeners) before writing the budget line.

## Laws

**Zones and the honest scrollbar**

- Model the scroll area as three zones: what the viewport shows, what is rendered but invisible (the buffer), and what is fetched but unrendered (the recycle zone). Fetched-but-unseen data only grows the canvas size; it is never rendered. **single-source** CLAIM(3MADCVqL534@16:06, 3MADCVqL534@16:47)
- Fake the full scrollable height with adjustable top and bottom padding (or a spacer) so the scrollbar stays accurate while nodes are unmounted; preserve content height across chunk swaps. **consensus** CLAIM(5vyKhm2NTfw@31:39, fmIiDLbLc_s@16:36, fmIiDLbLc_s@23:31)
- Keep one page of offscreen rows as a buffer so the user never sees a chunk swap. **single-source** CLAIM(fmIiDLbLc_s@16:06)

**Edges and the window**

- Detect the top and bottom edges with IntersectionObserver against dedicated sentinel nodes instead of computing scroll offsets. **consensus** CLAIM(3MADCVqL534@17:58, 5vyKhm2NTfw@28:09, fmIiDLbLc_s@16:36)
- Treat the rendered set as a sliding window over a two-sided stack: at each sentinel hit, pop the far side and push new data on the near side, keeping a constant number of mounted nodes. **consensus** CLAIM(3MADCVqL534@19:09, 5vyKhm2NTfw@29:21, u6jhTo13_No@31:10)
- Evict only nodes far from the viewport; keep near-viewport nodes so fast down-then-up scrolling does not thrash renders. **single-source** CLAIM(3MADCVqL534@19:57)

**Recycling and DOM writes**

- Avoid raw DOM insertion and deletion in the grid; reuse nodes by swapping their data and position instead. Creating and merging nodes is expensive, patching data is cheap. **consensus** CLAIM(3MADCVqL534@20:40, 9aOXGE7wAZo@13:32, LEaiGjffLEs@37:34)
- Recycle with soft writes: replace only text content (or the fields that changed), never whole subtrees. Predefine updaters for simple formats such as numbers and dates. **consensus** CLAIM(fmIiDLbLc_s@21:21, u6jhTo13_No@31:50, leo1FZ6vu1I@53:51)
- Confine DOM mutations to the edited region and reuse cached tokens and HTML instead of re-parsing the whole document (editor case). **single-source** CLAIM(tsGarhpWOws@50:50)

**Positioning and motion**

- Position every item absolutely on one canvas, translating by the previous item's offset plus size plus margin, so variable heights never break the flow. **single-source** CLAIM(3MADCVqL534@20:55, 3MADCVqL534@25:03)
- Prefer translation-based movement because it repaints pixels without triggering reflow; moving prerendered content with transforms is a paint-only operation. **consensus** CLAIM(3MADCVqL534@22:40, fmIiDLbLc_s@18:32, leo1FZ6vu1I@53:31)
- Prerender adjacent views (for example the neighboring calendar periods) offscreen and slide them in with CSS transforms instead of re-rendering on every switch. **single-source** CLAIM(leo1FZ6vu1I@46:53)
- Animate with CSS so the GPU composes the pixels, and never animate properties that force layout (width, height churn). **consensus** CLAIM(9aOXGE7wAZo@26:01, 9mjsRrJYOWE@49:41, lO6GyCvbDm8@24:16, LEaiGjffLEs@35:43, Tu-hZ6lqNtY@41:34, tsGarhpWOws@49:52, u6jhTo13_No@33:06)

**CSS style cost**

- Adopt a CSS naming strategy that keeps selectors flat (BEM, CSS modules, Tailwind), because deep selectors cost style-matching time on every element. **consensus** CLAIM(3MADCVqL534@44:35, 5vyKhm2NTfw@42:07, 9aOXGE7wAZo@26:46, lO6GyCvbDm8@23:37, LEaiGjffLEs@35:43, Tu-hZ6lqNtY@40:36, tsGarhpWOws@50:12, u6jhTo13_No@33:06)

**Which collections get virtualized**

- Virtualize only the axis that can actually explode (rows); cap the bounded axis (columns) and simplify the design instead of combining two virtualizations. **single-source** CLAIM(fmIiDLbLc_s@13:31)
- Virtualize result lists once they pass roughly a hundred rows, so the node count stays constant. **consensus** CLAIM(9mjsRrJYOWE@47:44, 9aOXGE7wAZo@24:41)
- Skip virtualization when the item count is inherently small (poll options) or bounded by the design (a calendar month). **consensus** CLAIM(lO6GyCvbDm8@22:44, leo1FZ6vu1I@45:39)
- Apply virtualization to heavy list components such as tables, not to page content rendering. **single-source** CLAIM(tsGarhpWOws@51:11)
- Choose infinite scroll for entertainment content and pagination for data users analyze in pages. **single-source** CLAIM(5vyKhm2NTfw@26:37)
- For large analysis tables prefer pagination over virtualization: complex data is easier to handle when you can request the exact page. **single-source** CLAIM(u6jhTo13_No@30:46)
- Define virtualization page size per device class (phone, tablet, laptop, desktop). **single-source** CLAIM(fmIiDLbLc_s@15:00)

**JavaScript work and workers**

- Make JavaScript do less: no blocking synchronous work on the main thread, expensive work asynchronous, heavy calculations cached. **consensus** CLAIM(3MADCVqL534@46:16, 5vyKhm2NTfw@40:24, Tu-hZ6lqNtY@36:54)
- Offload large static filtering to a web worker so filtering thousands of items does not block the UI thread; move dependency computation to a worker and apply the returned data lazily on the main thread, because DOM nodes cannot cross the worker boundary. **consensus** CLAIM(9aOXGE7wAZo@28:34, fmIiDLbLc_s@40:07, u6jhTo13_No@35:38)
- Keep expensive search on the server and reach for web workers only when large client-side filtering demands it. **consensus** CLAIM(9mjsRrJYOWE@50:46, 9mjsRrJYOWE@51:34)
- Distinguish the two async shapes by the consumer's function: an async filter over huge local data means a worker; a promise-returning filter means server-side filtering, executed and repainted on arrival. **single-source** CLAIM(u6jhTo13_No@37:04)
- Do not introduce web workers without a high-cost operation to offload. **single-source** CLAIM(lO6GyCvbDm8@25:59)

**Events**

- Delegate events from the container root and resolve the target with data attributes (row index, column index). **consensus** CLAIM(lO6GyCvbDm8@25:26, u6jhTo13_No@37:45)

**Dashboard-specific rendering**

- Downsample locally from finer buckets (first open, last close per bucket) instead of paying a server round trip for every zoom level. **single-source** CLAIM(HR2jXy_wPg4@42:30)
- When upsampled detail is required, render placeholder duplicate entries per bucket while the server request is in flight. **single-source** CLAIM(HR2jXy_wPg4@44:19)

**Rendering engine (cross-stage; owned by fesd-architecture)**

- Decide the rendering engine (canvas vs DOM) before the component and data design, because the choice rewrites everything downstream. **single-source** CLAIM(fmIiDLbLc_s@07:35)
- Canvas buys GPU-accelerated rendering, the best frame rate, and no per-element memory cost, but demands a rendering library, specialized skills, and a DOM layer for accessibility. **single-source** CLAIM(fmIiDLbLc_s@08:16, fmIiDLbLc_s@08:53, fmIiDLbLc_s@09:44)
- Choose canvas for mass-market products with large engineering resources; choose DOM for internal or cost-sensitive builds where development cost dominates. **single-source** CLAIM(fmIiDLbLc_s@11:08, fmIiDLbLc_s@11:27)

## Decision table

| situation | move | citation |
|---|---|---|
| unbounded scroll feed or masonry | zones + sliding window + absolute canvas | CLAIM(3MADCVqL534@16:06, 3MADCVqL534@19:09, 3MADCVqL534@20:55) |
| large table of complex data | pagination, exact page per request | CLAIM(u6jhTo13_No@30:46, 5vyKhm2NTfw@26:37) |
| list past ~100 rows | virtualize, keep node count constant | CLAIM(9mjsRrJYOWE@47:44) |
| small bounded list (poll options, month grid) | plain DOM, spend the budget elsewhere | CLAIM(lO6GyCvbDm8@22:44, leo1FZ6vu1I@45:39) |
| users flip between a few views fast | prerender neighbors, slide with transforms, cap the count | CLAIM(leo1FZ6vu1I@46:53, leo1FZ6vu1I@48:46) |
| huge local dataset needs filtering | web worker, soft-apply results | CLAIM(9aOXGE7wAZo@28:34, fmIiDLbLc_s@40:07) |
| expensive search over server data | keep it on the server | CLAIM(9mjsRrJYOWE@50:46) |
| animation needed | CSS transforms/opacity, GPU composed | CLAIM(Tu-hZ6lqNtY@41:34, tsGarhpWOws@49:52) |

## Worked cases

- 3MADCVqL534 [Front-End System Design] - Pinterest: the complete virtualized masonry answer (zones, two-sided stack, absolute canvas).
- fmIiDLbLc_s [Front-End System Design] - Google Sheets: per-device page size, buffer page, soft writes, worker-based dependency computation.
- u6jhTo13_No [Front-End System Design] - Data Table Component: pagination call, cell updaters, worker-vs-server filtering, event delegation.
- 5vyKhm2NTfw [Front End System Design] - Facebook News Feed: windowed story list with padding-based scrollbar.
- leo1FZ6vu1I [Front-End System Design] - Google Calendar: prerender-and-slide with a hard cap.
- 9mjsRrJYOWE Typeahead component - front-end system design and 9aOXGE7wAZo [Front-End System Design] - Typeahead Widget: result-list virtualization threshold and node reuse per keystroke.
- HR2jXy_wPg4 Frontend System Design - Financial Dashboard / TradingView: local downsampling and placeholder rows while upsampling.
- tsGarhpWOws [Front-End System Design] - Notion-like editor: mutation scoping and virtualizing only heavy lists.

## Dated / contestable

- Capping columns at about three alphabets to dodge two-axis virtualization (CLAIM(fmIiDLbLc_s@14:14)) is a 2022 simplification; modern grid stacks handle both axes. Distiller note (not the author).
- CSS animations outperforming JavaScript animations (CLAIM(lO6GyCvbDm8@24:16, u6jhTo13_No@33:06)) is true for simple transitions and contested for orchestrated motion. Distiller note (not the author): the Web Animations API and transform-driven scripts are acceptable for interactive sequences.
- Pagination over virtualization for tables (CLAIM(u6jhTo13_No@30:46)) is opinionated; virtualized grids with frozen headers are a common modern default. Distiller note (not the author): keep his call for exact pages of complex data.
