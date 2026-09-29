# Case: [Front-End System Design] - Google Sheets

Source: https://www.youtube.com/watch?v=fmIiDLbLc_s (video id fmIiDLbLc_s). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video fmIiDLbLc_s against the local transcript.

- published 2022-07-16 / duration 2711s (~45 min) / problem type: product-design
- channel: Front-End Engineer (Evgenii Ray)

## Author's framework as used
1. Quick domain recap before analysis: what the product is and what people use it for (financial reports, budgeting, data analysis), CLAIM(fmIiDLbLc_s@01:36)
2. General requirements: formatting generality, sheet size and extensibility, formula parsing with cell references, row/column resizing, CLAIM(fmIiDLbLc_s@03:13)
3. Specific (behavioral) requirements: device range, offline-feel performance, state management, accessibility, CLAIM(fmIiDLbLc_s@04:36)
4. Publish an explicit action plan of the design sections in execution order, CLAIM(fmIiDLbLc_s@05:57)
5. Choose the fundamental rendering approach (canvas vs DOM) before anything else, since the rest of the design depends on it, CLAIM(fmIiDLbLc_s@07:35)
6. Sketch only a high-level component hierarchy, nothing detailed, CLAIM(fmIiDLbLc_s@12:45)
7. Virtualization design: decide per-axis necessity first, then page sizes, buffer, observers, positioning, CLAIM(fmIiDLbLc_s@13:07)
8. Dependency resolution: model cell references as a directed graph and compute in topological order, CLAIM(fmIiDLbLc_s@25:21)
9. Formula parsing: tokenizing plus lazily loaded function implementations, CLAIM(fmIiDLbLc_s@33:07)
10. State management: one flat map of cells, updates driven by bubbled table-level events, CLAIM(fmIiDLbLc_s@35:08)
11. Optimization pass (no network section, offline assumption), CLAIM(fmIiDLbLc_s@38:58)
12. Accessibility pass: element choice, roles, scaling, keyboard, CLAIM(fmIiDLbLc_s@41:14)

## Worked design
Requirements
- Safe basic spreadsheet with generic formatting support (bold, italic, strikethrough, extensible to new types), CLAIM(fmIiDLbLc_s@03:20)
- Default grid of 1000 rows x 26 columns, extendable, CLAIM(fmIiDLbLc_s@03:44)
- Formula parsing with cell references and inter-cell dependencies, CLAIM(fmIiDLbLc_s@03:55)
- Row/column size editing, CLAIM(fmIiDLbLc_s@04:21)
- Works across phones, tablets, laptops; should feel offline (few loading placeholders), PWA mode, strong DOM performance, CLAIM(fmIiDLbLc_s@05:04)
- Effective state management for calculation, create/save/edit, CLAIM(fmIiDLbLc_s@05:22)
- Accessibility, which he flags as especially complex for a spreadsheet, CLAIM(fmIiDLbLc_s@05:33)

Components
- Sheet app root containing a table editor, which contains the control panel and a cell cluster (set of rows and cells), CLAIM(fmIiDLbLc_s@12:45)
- Deliberately kept at sketch level for interview use, CLAIM(fmIiDLbLc_s@12:32)

Data model
- Flat map state: key is row+column concatenation; value is a table cell with raw formula string, computed value (nullable until first calculation), type, formatting enum, CLAIM(fmIiDLbLc_s@35:19)
- Formatting held as enums, never class names, so implementation changes stay at code level, CLAIM(fmIiDLbLc_s@37:13)
- Dependency structure is a directed acyclic graph over cells, CLAIM(fmIiDLbLc_s@26:06)

API
- No network layer designed at all; the app is treated as offline-first and loads sources once, CLAIM(fmIiDLbLc_s@05:01) / CLAIM(fmIiDLbLc_s@41:04)

Realtime
- Not covered; no collaboration or sync section (see Distiller notes).

Performance
- Vertical virtualization required (rows exceed 10,000); horizontal skipped with a column cap around 72-78, CLAIM(fmIiDLbLc_s@13:31) / CLAIM(fmIiDLbLc_s@14:14)
- Page sizes 50 (phone) / 100 (tablet) / 140 (laptop) / 150-200 (desktop), CLAIM(fmIiDLbLc_s@15:00)
- Buffer recycling with soft writes and transform-based repositioning, CLAIM(fmIiDLbLc_s@21:21)
- Dependency calculations delegated to a web worker to keep the UI thread free, CLAIM(fmIiDLbLc_s@40:34)
- CSS hygiene (short selectors, naming conventions), build minification, CLAIM(fmIiDLbLc_s@39:50)

Accessibility
- Native table elements where possible, otherwise role=grid plus row/cell roles, CLAIM(fmIiDLbLc_s@41:55)
- No unnecessary ARIA; no pixel sizing; keyboard shortcuts and search, CLAIM(fmIiDLbLc_s@41:23)

## Trade-offs he names
- Canvas vs DOM: canvas gives GPU-accelerated rendering, best FPS, no stored element memory cost, but demands a primitive library, specialized skills and a mixed DOM layer for accessibility; DOM is cheap and accessible but loads CPU/memory and complicates two-axis virtualization. Pick canvas for an industry-scale product with resources, DOM for an internal tool where development cost dominates. Claims: CLAIM(fmIiDLbLc_s@08:16), CLAIM(fmIiDLbLc_s@08:53), CLAIM(fmIiDLbLc_s@09:44), CLAIM(fmIiDLbLc_s@11:08), CLAIM(fmIiDLbLc_s@11:27). For this video he picks DOM: CLAIM(fmIiDLbLc_s@11:41).
- Vertical vs horizontal virtualization: virtualize rows only and constrain columns, because combining two virtualizations is a real challenge and most users never exceed a capped column count, CLAIM(fmIiDLbLc_s@13:42), CLAIM(fmIiDLbLc_s@10:31).
- Limit = page size vs limit = page size + buffer: keeping only one page on screen makes chunk swaps visible; adding one page as buffer hides recycling, CLAIM(fmIiDLbLc_s@15:37), CLAIM(fmIiDLbLc_s@16:06).
- Hard write vs soft write on recycle: hard write replaces the whole subtree (row, cell, content); soft write reuses the nodes and updates text only, CLAIM(fmIiDLbLc_s@21:21).
- Enum vs class-name formatting in state: enums survive class renames and file reorganizations without a persisted-state mapping, CLAIM(fmIiDLbLc_s@37:13).

## Anti-patterns he warns about
- Drawing detailed diagrams during an interview instead of spending time on decisions, CLAIM(fmIiDLbLc_s@12:14)
- Persisting CSS class names in user state, which forces legacy mappings when styling changes, CLAIM(fmIiDLbLc_s@37:13)
- Deleting and inserting DOM nodes on scroll instead of reusing them (DOM operations are among the costliest things to do), CLAIM(fmIiDLbLc_s@21:27)
- Combining horizontal and vertical virtualization without a strong reason, CLAIM(fmIiDLbLc_s@10:31)
- Blocking the UI thread with dependency calculation instead of offloading it, CLAIM(fmIiDLbLc_s@40:34)
- Adding ARIA attributes when HTML5 semantics already cover it, CLAIM(fmIiDLbLc_s@41:23)
- Pixel-based sizing that ignores user browser settings, CLAIM(fmIiDLbLc_s@42:31)
- Adding network optimization as overhead to an app meant to run offline, CLAIM(fmIiDLbLc_s@41:04)

## Dated / contestable
- The "no network optimization because the app is offline" stance (CLAIM(fmIiDLbLc_s@05:01)) is a scoping choice of this exercise, not how Google Sheets actually works; any real spreadsheet today is collaboration- and sync-heavy, which the design explicitly omits.
- Capping columns at roughly three alphabets (CLAIM(fmIiDLbLc_s@14:14)) is a 2022 simplification; modern grid stacks routinely handle both axes of virtualization.
- Recomputing via full topological sort on every edit (CLAIM(fmIiDLbLc_s@28:12)) is the simple version; production spreadsheet engines do incremental recomputation over the affected subgraph only. Not addressed in the video.
- The offline/PWA framing (CLAIM(fmIiDLbLc_s@05:04)) still stands; service-worker patterns he hints at remain current.
