# Memory and long sessions

Purpose: keep a tab that lives for hours (feed, chat, dashboard) from growing without bound, by capping, evicting, recycling, and cleaning up deliberately.

## When to load

Feed, chat, dashboard, or editor tabs expected to stay open all day; reports of growing memory, sluggishness after hours of use, listener leaks, observer leaks, or unbounded caches; any design that mounts, prerenders, or caches "just a few more" things.

## Step checklist

1. List everything that grows with time or user action: mounted nodes, prerendered views, caches, listeners, observers, workers, connections, blob URLs.
2. Give each one a bound and an eviction rule before writing the design. Unbounded growth is a design decision too; make it a named one.
3. Recycle DOM nodes instead of creating and destroying them; a constant mounted node count is both a rendering and a memory win.
4. Evict far-from-viewport nodes only; keep near-viewport nodes so scroll jitter does not cause render churn.
5. Delegate events from the root instead of per-element listeners.
6. For long-lived tabs, decide what survives offline via the service worker cache and what is evicted from it.
7. Write the cleanup story: what is torn down on unmount or view change (listeners, observers, workers, in-flight requests).

## Laws

**Bound what grows**

- Only evict nodes far from the viewport; keep near-viewport nodes so fast down-up scrolling does not thrash renders. **single-source** CLAIM(3MADCVqL534@19:57)
- Cap the number of prerendered screens (for example four per side plus the visible one) to bound memory. **single-source** CLAIM(leo1FZ6vu1I@48:46)
- Hold the constant-node-count principle regardless of paging or virtualization; it is the biggest DOM win. **single-source** CLAIM(u6jhTo13_No@31:10)
- Keep a constant number of mounted DOM nodes by sliding a window over the loaded data and rewriting its contents. **consensus** CLAIM(5vyKhm2NTfw@29:21, 3MADCVqL534@19:09)
- Recycle nodes with soft writes (replace only text content) instead of replacing whole subtrees; node creation and merging is the expensive and memory-churning path. **consensus** CLAIM(fmIiDLbLc_s@21:21, u6jhTo13_No@31:50, 3MADCVqL534@20:40)

**Listeners and handlers**

- Delegate events from the container root, resolving the target cell via data attributes (row index, column index); per-element listeners leak memory and lose events when their elements are destroyed. **consensus** CLAIM(u6jhTo13_No@37:45, lO6GyCvbDm8@25:26)
- Prefer one delegated handler over per-cell handlers for memory and performance in a large grid. **single-source** CLAIM(HR2jXy_wPg4@13:53)

**Caches with eviction (cross-stage; also fesd-state-data)**

- Store results in a fixed-size map keyed by query, evicting the oldest entry when the cache size (default 5) is exceeded; an unbounded cache is the anti-pattern. **single-source** CLAIM(9aOXGE7wAZo@17:14)
- Bound the hybrid variant's cache with an LRU structure that evicts least-recently-used entries once the entry limit is exceeded. **single-source** CLAIM(9mjsRrJYOWE@28:28)

**Connections, workers, and boundaries**

- Price every extra TCP connection before adding one: connections consume client and server memory in addition to handshake time. **single-source** CLAIM(gxF9fLo5XQw@18:27, gxF9fLo5XQw@19:08)
- Do not introduce web workers without a high-cost operation to offload; each worker is a thread with its own memory cost. **single-source** CLAIM(lO6GyCvbDm8@25:59)
- Move heavy computation to a web worker and apply the returned data lazily on the main thread, since DOM nodes cannot cross that boundary; this also keeps main-thread memory churn down. **single-source** CLAIM(fmIiDLbLc_s@40:07)

**Long-lived tabs: feed, chat, dashboard**

- Support offline mode by caching the application's code, styles, data, and images in a service worker, so a long session survives a reload. **consensus** CLAIM(3MADCVqL534@47:44, 5vyKhm2NTfw@43:40, LEaiGjffLEs@40:13)
- Cache scripts, styles, data, and images in a service worker combined with HTTP caching semantics such as ETag, so stale entries age out instead of accumulating. **single-source** CLAIM(Tu-hZ6lqNtY@42:13)
- Enable HTTP/2 and a service worker that caches fetched assets so the app boots fast and works offline across sessions. **single-source** CLAIM(tsGarhpWOws@45:00)

**Storage quotas (cross-stage; also fesd-state-data)**

- Treat client-side storage as quota-limited and approximate: the corpus frames IndexedDB at roughly 30 percent of disk and about 2 GB per domain, and flags that real quotas are origin- and browser-specific with their own eviction policies. **single-source** CLAIM(HR2jXy_wPg4@27:08)

## Decision table

| what grows | bound it with | citation |
|---|---|---|
| mounted DOM nodes | constant window + node recycling | CLAIM(u6jhTo13_No@31:10, 5vyKhm2NTfw@29:21) |
| rendered buffer | keep near-viewport nodes, evict far ones only | CLAIM(3MADCVqL534@19:57) |
| prerendered views | hard cap (four per side plus visible) | CLAIM(leo1FZ6vu1I@48:46) |
| query result cache | fixed size, evict oldest / LRU | CLAIM(9aOXGE7wAZo@17:14, 9mjsRrJYOWE@28:28) |
| event handlers | one delegated root listener with data attributes | CLAIM(u6jhTo13_No@37:45) |
| threads | workers only for named heavy work | CLAIM(lO6GyCvbDm8@25:59) |
| connections | price handshake + memory before adding one | CLAIM(gxF9fLo5XQw@18:27) |
| offline data | service-worker cache with HTTP cache semantics | CLAIM(Tu-hZ6lqNtY@42:13) |

Cleanup checklist (Distiller note, not the author): the corpus names listener leaks and memory bounds but not a teardown procedure. On unmount or view change, remove observers and delegated listeners, terminate workers, abort in-flight requests, revoke object URLs, and drop references to recycled node data. In a long-lived SPA this is the difference between a flat and a climbing heap.

## Worked cases

- 3MADCVqL534 [Front-End System Design] - Pinterest: eviction hysteresis (keep near-viewport pins) as the memory-aware edge of a virtualized grid.
- leo1FZ6vu1I [Front-End System Design] - Google Calendar: the explicit prerender cap that bounds memory.
- u6jhTo13_No [Front-End System Design] - Data Table Component: listener delegation and the constant-node principle.
- LEaiGjffLEs [Front-End System Design] - Chat application: a message list that stays a fixed size for an all-day tab.
- HR2jXy_wPg4 Frontend System Design - Financial Dashboard / TradingView: delegated handlers for a dense grid and the client storage quota framing.
- Tu-hZ6lqNtY [Front-End Product Design] - Netflix and tsGarhpWOws [Front-End System Design] - Notion-like editor: service-worker caching patterns for apps that reload and resume.

## Dated / contestable

- The application-cache mechanism named alongside service workers (CLAIM(3MADCVqL534@47:48, 5vyKhm2NTfw@40:02, Tu-hZ6lqNtY@42:13, leo1FZ6vu1I@55:40)) is removed from browsers. Distiller note (not the author): the service worker alone owns offline caching; the web worker has no offline role.
- The IndexedDB quota framing (CLAIM(HR2jXy_wPg4@27:08)) is approximate and browser-dependent. Distiller note (not the author): query navigator.storage.estimate() and treat eviction policy as browser-defined.
