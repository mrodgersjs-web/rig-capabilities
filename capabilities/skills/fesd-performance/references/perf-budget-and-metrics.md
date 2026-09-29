# Performance budget and metrics

Purpose: turn the performance plan into a statement with named metrics, named device classes, and numbers the corpus actually supports, so an interviewer or reviewer can check it.

## When to load

"what is the performance budget", "how fast should this be", closing a design's performance section, scoring an answer for whether it quantifies anything, or deciding which metric a given lever moves.

## Step checklist

1. Frame the answer on the three tracks: network, rendering, JavaScript. Never present one undifferentiated optimization list.
2. Name the metric each lever moves. Use the corpus metric set: time-to-first-content, time-to-interactive, frame rate, perceived load time, and render latency as a function of resource count.
3. Attach a device class to every size and page-size claim (phone, tablet, laptop, desktop).
4. Use the corpus's real numbers where they exist (compression savings, virtualization threshold, prerender cap) and say "measure" where they do not.
5. Budget perceived speed explicitly: skeletons and placeholders are part of the number the user feels.
6. State the trade each lever accepts (bounce-only analytics loss, cache invalidation granularity, memory for prerendered views).

## Laws

**Answer structure**

- Split performance work into network, rendering, and JavaScript tracks and address each separately. **consensus** CLAIM(5vyKhm2NTfw@33:03, Tu-hZ6lqNtY@30:15)
- Render latency scales with resource count, because the page appears only after every critical resource has loaded. **single-source** CLAIM(gxF9fLo5XQw@14:03)

**Metrics he names**

- Time-to-first-content: cut it by pre-rendering or server-rendering the pages where arrival decides the outcome. **consensus** CLAIM(5vyKhm2NTfw@38:24, Tu-hZ6lqNtY@38:15)
- Time-to-first-content and time-to-interactive: minimized when the conversion page is clean HTML without JS bundles. **single-source** CLAIM(Tu-hZ6lqNtY@38:15)
- Time-to-first-content versus analytics coverage: delaying analytics cuts it, and the business must accept losing bounce-only visits. **single-source** CLAIM(3MADCVqL534@43:53)
- Frame rate: CSS animations are preferred because they hold the best frame rate; GPU-composed transforms and flat selectors protect it. **consensus** CLAIM(lO6GyCvbDm8@24:16, 9mjsRrJYOWE@49:41, tsGarhpWOws@49:52)
- Perceived load time: skeletons and placeholders make waiting feel shorter, which is a measurable outcome, not decoration. **consensus** CLAIM(3MADCVqL534@45:17, LEaiGjffLEs@37:01, 9mjsRrJYOWE@46:14)
- Constant node count as the DOM budget: the biggest single rendering win is keeping mounted nodes constant. **single-source** CLAIM(u6jhTo13_No@31:10)

**Numbers the corpus gives you (cite these rather than inventing)**

- Compression: gzip roughly 40-50 percent traffic savings, Brotli adding 10-20 more. CLAIM(3MADCVqL534@35:08, Tu-hZ6lqNtY@31:02)
- Virtualization threshold: virtualize result lists once they pass roughly a hundred rows. CLAIM(9mjsRrJYOWE@47:44)
- Page size: define virtualization page size per device class (phone, tablet, laptop, desktop), plus one page of offscreen buffer. CLAIM(fmIiDLbLc_s@15:00, fmIiDLbLc_s@16:06)
- Prerender cap: about four prerendered screens per side plus the visible one. CLAIM(leo1FZ6vu1I@48:46)
- Polyfill budget: an ES6 bundle without polyfills saves tens of kilobytes over the lowest-common-denominator payload. CLAIM(lO6GyCvbDm8@21:29, LEaiGjffLEs@31:06)
- Handshake cost: every extra TCP connection is about three network trips (one and a half round trips). CLAIM(gxF9fLo5XQw@18:27)
- Downsampled charts: derive buckets locally from finer data (first open, last close) instead of a server round trip per zoom level. CLAIM(HR2jXy_wPg4@42:30)

**How to state a budget in an interview**

Distiller note (not the author), assembled from his practice of naming tracks, device classes, and thresholds: state each line as metric, device class, number, mechanism, trade. Example shape: "first content under X ms on a mid phone, because critical CSS/JS is inlined and non-critical work is deferred (CLAIM(3MADCVqL534@42:03, Tu-hZ6lqNtY@38:15)); scrolling holds frame rate because items are absolutely positioned and moved with transforms (CLAIM(3MADCVqL534@22:40)); mounted nodes stay constant at page size plus one buffer page per device class (CLAIM(fmIiDLbLc_s@15:00, fmIiDLbLc_s@16:06))". Where the corpus gives no number, say the measurement you would take instead of inventing one; that is what the author does with thresholds he does not have.

## Decision table

| lever | metric it moves | citation |
|---|---|---|
| inline critical, defer rest, SSR conversion pages | time-to-first-content, time-to-interactive | CLAIM(Tu-hZ6lqNtY@38:15, 3MADCVqL534@42:03) |
| compression, HTTP/2, fewer requests | payload and render latency | CLAIM(3MADCVqL534@35:08, 3MADCVqL534@36:13, gxF9fLo5XQw@20:00) |
| virtualization + node recycling | mounted node count, frame rate while scrolling | CLAIM(u6jhTo13_No@31:10, 9mjsRrJYOWE@47:44) |
| CSS transforms over reflow-triggering JS | frame rate | CLAIM(lO6GyCvbDm8@24:16, tsGarhpWOws@49:52) |
| skeletons and placeholders | perceived load time | CLAIM(3MADCVqL534@45:17, 9mjsRrJYOWE@46:14) |
| worker or server for heavy filtering | interaction latency (main thread free) | CLAIM(u6jhTo13_No@35:38, u6jhTo13_No@37:04) |
| prerender cap and cache caps | memory over long sessions | CLAIM(leo1FZ6vu1I@48:46, 9aOXGE7wAZo@17:14) |

## Worked cases

- 5vyKhm2NTfw [Front End System Design] - Facebook News Feed and Tu-hZ6lqNtY [Front-End Product Design] - Netflix: the three-track split as the skeleton of the whole performance answer.
- 3MADCVqL534 [Front-End System Design] - Pinterest: the compression numbers and the analytics-versus-first-content trade.
- fmIiDLbLc_s [Front-End System Design] - Google Sheets: per-device page sizing as a budget decision.
- 9mjsRrJYOWE Typeahead component - front-end system design: an explicit numeric threshold (a hundred rows) for when virtualization starts.
- HR2jXy_wPg4 Frontend System Design - Financial Dashboard / TradingView: choosing computation over round trips as a budget move.

## Dated / contestable

- The compression percentages (CLAIM(3MADCVqL534@35:08, Tu-hZ6lqNtY@31:02)) are 2020-2021 approximations. Distiller note (not the author): they are order-of-magnitude talking points; measure real payloads before promising a number.
- "Tens of kilobytes saved" from dropping polyfills (CLAIM(lO6GyCvbDm8@21:29)) is bundle-dependent. Distiller note (not the author): the mechanism is right, the size claim depends on the dependency tree.
- The corpus names no Core Web Vitals (LCP, CLS, INP) and no numeric performance budget. Distiller note (not the author): if a client or interview asks for web vitals specifically, say which of his levers maps to them (critical path to LCP, transforms and stable layout to CLS, off-main-thread work to INP) and treat that mapping as your own reasoning, not the author's.
