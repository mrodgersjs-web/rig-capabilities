---
name: fesd-performance
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Stage S08 of the FE System Design OS: the performance stage, the deepest-probed topic in the
  corpus. Owns the performance plan of any front-end design or FE interview answer: rendering and
  virtualization (windowing, DOM churn, reflow vs paint, canvas vs DOM, web workers), asset loading
  (images, formats, fonts, lazy loading, hints, code splitting, bundle shape), network performance
  (CDN, compression, HTTP caching, request cost, debounce for typeahead), memory and long-lived
  sessions (node recycling, cache caps, listener cleanup), and a stated performance budget with the
  metrics the author actually names. Produces a performance section for a design doc or an interview
  answer: one line per lever with its mechanism, its number where the corpus has one, and its
  citation. Use when asked "how do you make X fast", "how would you render a million rows", "optimize
  this list / feed / grid / table", "what is the performance budget", "why is scrolling janky",
  "virtualize or paginate", or any FE system design round reaching its optimization half. Distilled
  from 127 laws across 13 Front-End Engineer videos. Hand-off to fixing-motion-performance and
  code-perf-bottleneck-finder once there is real code to fix. JEV-FIRST MANDATE, findable at task
  start: typed judgments in this stage go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED
  is the only answer when the classifier is down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, performance, rendering, virtualization, asset-loading, network, memory]
outcome: "code-engineering: every design and interview answer ships a cited performance plan (rendering, assets, network, memory, budget) instead of a pile of unranked tips"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-performance/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S08"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Performance (stage S08)

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-performance-engineer loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate

Typed judgments this stage forces, routed to Jev first:

1. Is this list of performance levers complete and correctly prioritized for this prompt (not just the ones the author happened to mention)?
2. Which rendering strategy fits this collection: virtualize, paginate, prerender and cap, or leave it plain DOM?
3. Does the changed code actually reduce the named bottleneck (rubric `code.review` for code)?
4. Does the rendered screen meet the stated budget on the named device class (rubric `ui.design` for rendered screens)?

Command: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Nearest existing rubrics: `code.review` for code, `ui.design` for rendered screens, both advisory until calibrated. A pass needs every required signal above 0.9. Classifier down, erroring, or rubric missing = DEFERRED, never a guessed verdict and never a frontier model's opinion in its place. An advisory PASS is not permission to ship.

## When to use

- The design has an unbounded or large collection: feed, masonry grid, spreadsheet, table, chat log, calendar, chart dashboard, media catalog.
- An FE interview round has moved to "how would you optimize this" or "what are the bottlenecks".
- Someone reports jank, slow first paint, heavy bundles, slow scroll, or a tab that grows in memory over hours.
- The prompt asks for a performance budget, target numbers, or "how fast should this be".

Not the stage for: picking the transport (fesd-realtime-sync), the API shape (fesd-api-network), the client store (fesd-state-data), or polishing actual code (hand-off skills below).

## Inputs and output contract

Consumes from earlier stages: the requirement list (collection sizes, device classes, online/offline), the architecture and rendering strategy (fesd-architecture), the data model and cache policy (fesd-state-data), and the API/pagination shape (fesd-api-network).

Emits a "Performance plan" section with exactly these sub-headings, each item carrying a mechanism and its CLAIM citation:

1. Rendering and virtualization (which strategy, which axis, which window, what stays mounted)
2. Asset loading (images, bundle shape, critical path, hints)
3. Network (compression, protocol, caching layers, request count)
4. Memory and long sessions (what is capped, what is evicted, what is cleaned up)
5. Budget (metric, device class, number, mechanism, and the trade accepted)

## Procedure

1. Size the problem before optimizing. Ask for row/element counts, data source (local vs server), and device classes; without numbers every lever is a guess. Frame the answer on the three tracks, network, rendering, and JavaScript, and treat each separately. CLAIM(5vyKhm2NTfw@33:03, Tu-hZ6lqNtY@30:15) Load `references/perf-budget-and-metrics.md`.
2. Choose the collection strategy (virtualize / paginate / prerender-and-cap / plain DOM) and only then the mechanics. Load `references/rendering-and-virtualization.md`. CLAIM(u6jhTo13_No@30:46, lO6GyCvbDm8@22:44, tsGarhpWOws@51:11)
3. Plan the critical path: what must arrive before first content, what can be deferred, what is hinted. Load `references/asset-loading.md`. CLAIM(3MADCVqL534@42:03, 3MADCVqL534@42:44)
4. Price the wire: compression, protocol, connection count, cache layers, request count. Load `references/network-performance.md`. CLAIM(3MADCVqL534@35:08, gxF9fLo5XQw@18:27)
5. Bound memory for the session length the product implies (feed, chat, dashboard tabs live for hours). Load `references/memory-and-long-sessions.md`. CLAIM(leo1FZ6vu1I@48:46, u6jhTo13_No@37:45)
6. Write the budget line per lever: metric, device class, number, mechanism, trade. Numbers exist in the corpus for compression, virtualization thresholds, and prerender caps; do not invent the rest. CLAIM(9mjsRrJYOWE@47:44, 3MADCVqL534@35:08)
7. Hand code-level findings to `fixing-motion-performance` (animation, layout thrash) and `code-perf-bottleneck-finder` (profiling, real bottlenecks). This stage designs; those skills measure and patch.

## Core laws

**Framing**

- Split performance work into network, rendering, and JavaScript tracks and solve each on its own; the answer is not one optimization, it is three lists. **consensus** CLAIM(5vyKhm2NTfw@33:03, Tu-hZ6lqNtY@30:15)
- Render latency scales with the number of resources: the page exists only after every critical resource has loaded, so request count is a rendering decision too. **single-source** CLAIM(gxF9fLo5XQw@14:03)

**Rendering**

- Hold the mounted node count constant. Slide a window over the loaded data, recycle the nodes on the far side, and write new data into them instead of creating and destroying elements. **consensus** CLAIM(3MADCVqL534@19:09, 5vyKhm2NTfw@29:21, u6jhTo13_No@31:10)
- Patch, never rebuild: swap text or data on existing nodes (soft write), with predefined updaters for simple formats such as numbers and dates. Creating and merging nodes is the expensive part. **consensus** CLAIM(3MADCVqL534@20:40, 9aOXGE7wAZo@13:32, fmIiDLbLc_s@21:21, u6jhTo13_No@31:50, leo1FZ6vu1I@53:51)
- Detect edges with IntersectionObserver over dedicated sentinel nodes, not scroll-event math, and keep the scrollbar honest with padding or a spacer that reflects the unloaded data. **consensus** CLAIM(3MADCVqL534@17:58, 5vyKhm2NTfw@28:09, 5vyKhm2NTfw@31:39, fmIiDLbLc_s@16:36, fmIiDLbLc_s@23:31)
- Position items absolutely on one canvas and move them with CSS transforms: translation is a paint operation, so scrolling and view switches never trigger reflow. **consensus** CLAIM(3MADCVqL534@20:55, 3MADCVqL534@22:40, fmIiDLbLc_s@18:32, leo1FZ6vu1I@53:31)
- Offload heavy computation to a web worker only when there is a genuinely costly operation (large filtering, dependency computation), and apply the result lazily on the main thread, because DOM nodes cannot cross that boundary. Expensive search belongs on the server. **consensus** CLAIM(9aOXGE7wAZo@28:34, 9mjsRrJYOWE@50:46, 9mjsRrJYOWE@51:34, fmIiDLbLc_s@40:07, lO6GyCvbDm8@25:59, u6jhTo13_No@35:38, u6jhTo13_No@37:04)

**Assets and network**

- Compress everything first (gzip, then Brotli for supporting clients), serve over HTTP/2 so one connection multiplexes the resource loads, and only then consider architecture. **consensus** CLAIM(3MADCVqL534@35:08, 3MADCVqL534@36:13, 5vyKhm2NTfw@33:41, Tu-hZ6lqNtY@31:02, LEaiGjffLEs@28:56, lO6GyCvbDm8@20:41)
- Split bundles along stability and usage: rarely changing vendor code caches separately, rarely needed features load on demand, and the package a consumer installs is modular (core, theming, utilities). **consensus** CLAIM(3MADCVqL534@37:22, LEaiGjffLEs@29:50, Tu-hZ6lqNtY@33:48, tsGarhpWOws@47:07, lO6GyCvbDm8@22:02, u6jhTo13_No@28:08)
- Inline what blocks first paint and defer the rest; hint the high-priority follow-ups with preconnect or preload and push late small work (analytics) to the end. **consensus** CLAIM(3MADCVqL534@42:03, 3MADCVqL534@42:44, Tu-hZ6lqNtY@38:48, Tu-hZ6lqNtY@39:59, leo1FZ6vu1I@54:27)
- The image pipeline is format, size, and distance: a modern format with a fallback, resized per device through a service behind the CDN, fetched lazily on viewport intersection. **consensus** CLAIM(3MADCVqL534@38:50, 3MADCVqL534@40:20, 3MADCVqL534@41:14, LEaiGjffLEs@33:14, 5vyKhm2NTfw@34:42)
- Price every additional TCP connection before adding one: the handshake costs network trips, connections eat client and server memory, and nothing prioritizes between them. **single-source** CLAIM(gxF9fLo5XQw@18:27, gxF9fLo5XQw@19:08)

**Perceived speed and memory**

- Show skeletons or placeholders instead of empty screens; visible progress shortens perceived wait, which is a budget item like any other. **consensus** CLAIM(3MADCVqL534@45:17, 9mjsRrJYOWE@46:14, LEaiGjffLEs@37:01, Tu-hZ6lqNtY@40:53, lO6GyCvbDm8@24:45)
- Keep CSS selectors flat through a naming convention and animate with CSS (GPU composed) rather than JavaScript that reflows. **consensus** CLAIM(3MADCVqL534@44:35, 9aOXGE7wAZo@26:01, 9mjsRrJYOWE@49:41, Tu-hZ6lqNtY@41:34, tsGarhpWOws@49:52, u6jhTo13_No@33:06)
- Delegate events from the root and resolve the target with data attributes; per-element listeners leak memory and die with the elements they were attached to. **consensus** CLAIM(lO6GyCvbDm8@25:26, u6jhTo13_No@37:45)
- Bound everything that grows: evict only nodes far from the viewport, cap prerendered screens, cap caches. Long sessions are a memory design, not an afterthought. **consensus** CLAIM(3MADCVqL534@19:57, leo1FZ6vu1I@48:46)

## Sub-skills

| sub-skill | file | load when |
|---|---|---|
| rendering and virtualization | references/rendering-and-virtualization.md | any large or unbounded collection, scroll jank, node churn, reflow questions, web worker questions |
| asset loading | references/asset-loading.md | bundle shape, images, fonts, lazy loading, preload/preload hints, critical path, offline caching |
| network performance | references/network-performance.md | compression, HTTP version, CDN, cache layers, connection cost, debounce for typeahead |
| memory and long sessions | references/memory-and-long-sessions.md | feed / chat / dashboard tabs that live for hours, growing memory, listener or observer leaks |
| perf budget and metrics | references/perf-budget-and-metrics.md | "what is the budget", "how fast should it be", naming metrics and numbers in an interview |

## Decision tables

**Collection strategy** (details and citations in references/rendering-and-virtualization.md)

| option | pick when | against |
|---|---|---|
| plain DOM, no virtualization | element count is inherently bounded (poll options, a month grid) CLAIM(lO6GyCvbDm8@22:44, leo1FZ6vu1I@45:39) | counts can grow |
| virtualization / windowing | unbounded scrolling collections, one axis that can explode CLAIM(fmIiDLbLc_s@13:31, 9mjsRrJYOWE@47:44) | users need an exact page of complex data |
| pagination | data users analyze in pages (tables) CLAIM(5vyKhm2NTfw@26:37, u6jhTo13_No@30:46) | entertainment feeds where scroll is the interaction |
| prerender adjacent views, slide with transforms | a few discrete views users flip between fast (calendar periods) CLAIM(leo1FZ6vu1I@46:53) | many views; cap the prerendered count CLAIM(leo1FZ6vu1I@48:46) |

**Where heavy computation goes**

| shape of the work | put it | citation |
|---|---|---|
| expensive search over server data | server | CLAIM(9mjsRrJYOWE@50:46, 9mjsRrJYOWE@51:34) |
| huge local dataset, async filter function | web worker | CLAIM(9aOXGE7wAZo@28:34, u6jhTo13_No@37:04) |
| promise-returning filter over remote data | server, repaint on arrival | CLAIM(u6jhTo13_No@37:04) |
| small helper or small list | main thread; no worker overhead | CLAIM(lO6GyCvbDm8@25:59, 9mjsRrJYOWE@51:34) |

**Rendering engine** (cross-stage: owned by fesd-architecture, performance-relevant here)

| engine | pick when | cost |
|---|---|---|
| canvas | mass-market product, engineering resources, FPS is the product | needs a rendering library, specialized skills, plus a DOM layer for accessibility CLAIM(fmIiDLbLc_s@08:16, fmIiDLbLc_s@09:44, fmIiDLbLc_s@11:08) |
| DOM | internal or cost-sensitive build, dev cost dominates | CPU and memory per element, two-axis virtualization is hard CLAIM(fmIiDLbLc_s@08:53, fmIiDLbLc_s@11:27) |

## Anti-patterns

- Inserting and deleting DOM nodes on scroll instead of recycling them. CLAIM(fmIiDLbLc_s@21:27, 3MADCVqL534@20:40)
- Rendering fetched-but-unseen data immediately instead of only extending the canvas. CLAIM(3MADCVqL534@16:47)
- Evicting nodes that sit near the viewport, so every scroll reversal re-renders. CLAIM(3MADCVqL534@19:57)
- Chaining deep CSS selectors or animating width and height in JavaScript. CLAIM(3MADCVqL534@44:35, 9aOXGE7wAZo@26:01)
- One universal bundle whose polyfills every consumer pays for. CLAIM(u6jhTo13_No@26:39, 9mjsRrJYOWE@43:51)
- Pulling a heavy dependency for a single helper function. CLAIM(9mjsRrJYOWE@43:51, 9mjsRrJYOWE@44:34)
- Multiplying TCP connections (domain sharding) instead of cutting request count. CLAIM(gxF9fLo5XQw@16:36, gxF9fLo5XQw@20:00)
- Blocking the UI thread with dependency calculation or large filtering. CLAIM(fmIiDLbLc_s@40:34, u6jhTo13_No@35:38)
- Introducing web workers with no high-cost operation to justify them. CLAIM(lO6GyCvbDm8@25:59)
- Adding network optimization as overhead to an app designed to run offline. CLAIM(fmIiDLbLc_s@40:01, fmIiDLbLc_s@41:04)
- Attaching a listener per cell or row instead of delegating from the root. CLAIM(u6jhTo13_No@37:45)

## Worked cases

| video | title | what to steal for this stage |
|---|---|---|
| 3MADCVqL534 | [Front-End System Design] - Pinterest | the zone model (visible / invisible / recycle), the two-sided stack window, the absolute-canvas translation scheme |
| 5vyKhm2NTfw | [Front End System Design] - Facebook News Feed | infinite scroll vs pagination by content type, padding trick for honest scrollbars, the three-track perf split |
| Tu-hZ6lqNtY | [Front-End Product Design] - Netflix | media catalog loading: thumbnail-heavy HTTP/2, per-usage bundle split, SSR for the conversion page |
| fmIiDLbLc_s | [Front-End System Design] - Google Sheets | per-device page size, one-page buffer, soft writes, canvas vs DOM call, worker for dependency computation |
| u6jhTo13_No | [Front-End System Design] - Data Table Component | pagination over virtualization, predefined cell updaters, worker vs server filtering, event delegation |
| LEaiGjffLEs | [Front-End System Design] - Chat application | fixed message-node recycling, skeleton screens, service-worker history caching, when not to SSR |
| 9mjsRrJYOWE | Typeahead component - front-end system design | layered caching, virtualization threshold around a hundred rows, minimal footprint, worker-vs-server hedge |
| 9aOXGE7wAZo | [Front-End System Design] - Typeahead Widget | node reuse per keystroke, worker for large static filtering, debounce as widget-level network control |
| leo1FZ6vu1I | [Front-End System Design] - Google Calendar | prerender-and-slide with a hard cap, soft text updates, transform-only movement |
| lO6GyCvbDm8 | [Front-End System Design] - Design a Poll Widget | small-widget economics: minify, compress, CDN, skip virtualization, event delegation |
| tsGarhpWOws | [Front-End System Design] - Notion-like editor | confine mutations to the edited region, virtualize only heavy lists, Brotli/Zstd at the edge |
| HR2jXy_wPg4 | Frontend System Design - Financial Dashboard / TradingView | local downsampling from finer buckets, placeholder rows while upsampling, delegated handlers for memory |
| gxF9fLo5XQw | Deep dive into HTTP [Part 1] | connection economics: handshake cost, why domain sharding died, request count over connection count |

## Dated / contestable

- ES5/ES6 dual bundles with polyfill economies (CLAIM(lO6GyCvbDm8@21:29, u6jhTo13_No@26:39, leo1FZ6vu1I@52:00)) are 2020-2022 advice. Distiller note (not the author): post-IE11 the answer is a single modern target driven by browserslist, with transpilation and polyfills only where the real support matrix demands them; the goal (small modern payload) is unchanged.
- "WebP with PNG fallback" (CLAIM(3MADCVqL534@38:50, LEaiGjffLEs@31:06, Tu-hZ6lqNtY@32:17)) predates AVIF. Distiller note (not the author): keep the fallback pattern, update the pair; AVIF often beats WebP on size, and the responsive-image service pattern is the durable part.
- Animated GIFs for hover promos (CLAIM(Tu-hZ6lqNtY@32:17)) are the heavy 2021 choice. Distiller note (not the author): a short muted MP4/WebM loop or animated WebP/AVIF is dramatically smaller for the same clip.
- Application cache plus service workers as the offline story (CLAIM(3MADCVqL534@47:48, 5vyKhm2NTfw@40:02, Tu-hZ6lqNtY@42:13, leo1FZ6vu1I@55:40)) names a deprecated API. Distiller note (not the author): the service worker alone owns offline resource caching today; the web worker has no offline role.
- Domain sharding (CLAIM(gxF9fLo5XQw@16:36, gxF9fLo5XQw@17:16)) is already called a legacy hack in the corpus. Distiller note (not the author): HTTP/2 and HTTP/3 multiplexing removed the reason it existed.
- The compression savings figures, gzip around 40-50 percent and Brotli adding 10-20 (CLAIM(3MADCVqL534@35:08, Tu-hZ6lqNtY@31:02)), are 2020-2021 approximations. Distiller note (not the author): measure your own payloads; Zstd content-encoding is arriving in browsers (the author already names it, CLAIM(tsGarhpWOws@47:55)).
- Pagination over virtualization for tables (CLAIM(u6jhTo13_No@30:46)) is opinionated. Distiller note (not the author): modern grids virtualize with frozen headers and keyboard navigation; the claim stands for his named case, exact pages of complex data.
- CSS animations beat JavaScript animations (CLAIM(lO6GyCvbDm8@24:16, u6jhTo13_No@33:06)) holds for simple transitions and is contested for orchestrated motion. Distiller note (not the author): for interactive or sequenced animation, the Web Animations API and transform-driven JavaScript are fine.

## Hand-off

- Next stage skill: `fesd-a11y-i18n` (virtualized lists must stay keyboard and screen-reader navigable; canvases need a DOM accessibility layer).
- Real code, real measurement: `fixing-motion-performance` for animation, layout thrash, and compositor work; `code-perf-bottleneck-finder` for profiling and bottleneck ranking. This stage designs and cites; those skills measure and patch.
- Adjacent estate skills: `app-web-frontend` for build slices, `app-ui-design` / `emil-design-eng` / `impeccable` for visual polish, `fixing-accessibility`, `app-data-layer` for the storage and quota questions, and the api design harness `hA-09` where the perf plan constrains the API surface (pagination size, batching).
