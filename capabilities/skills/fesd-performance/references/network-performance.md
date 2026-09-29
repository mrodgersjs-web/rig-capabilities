# Network performance

Purpose: move fewer bytes over fewer connections, cache in layers, and stop a widget from firing requests per keystroke.

## When to load

Compression and protocol choices, CDN placement, HTTP cache semantics, connection and request economics, typeahead or search request patterns (debounce, cancellation, batching), and any "why is the payload so slow to arrive" question.

## Step checklist

1. Take the simplest wins first: compress (gzip, then Brotli), modern formats, minify, nearest CDN edge. Measure before touching architecture.
2. Choose the protocol: HTTP/2 so one connection multiplexes the loads; count any extra connection you are about to open.
3. Count requests as a first-class metric: reuse through caching, bundle, sprite, inline critical.
4. Design the cache layers explicitly: own client cache, browser cache via response headers, server cache for expensive work.
5. For interactive search: debounce input, cancel superseded requests, cache by query with a bound and a TTL.
6. Skip the whole network budget when the product is offline-first and loads its sources once.

## Laws

**Order of attack**

- Start network performance with the simplest wins (compression and modern formats) before any architectural change. **single-source** CLAIM(LEaiGjffLEs@28:56)
- Even for a small widget: minify, compress (Brotli where supported), and serve from the nearest CDN location. **consensus** CLAIM(lO6GyCvbDm8@20:41, u6jhTo13_No@29:28, 9mjsRrJYOWE@45:15)

**Compression**

- Zip assets first (roughly 40-50 percent savings), then add Brotli for browsers that support it (another 10-20 percent). **consensus** CLAIM(3MADCVqL534@35:08, 5vyKhm2NTfw@33:41, Tu-hZ6lqNtY@31:02)
- Compress with Brotli (or Zstd) at the CDN and keep assets compressed per CDN configuration. **consensus** CLAIM(tsGarhpWOws@47:55, 9mjsRrJYOWE@45:15)
- For a component, the network budget is limited to your own assets: compress your JS and CSS with gzip and Brotli. **single-source** CLAIM(u6jhTo13_No@26:01)

**Protocol and connections**

- Serve over HTTP/2 so one connection multiplexes hundreds of parallel resource loads. **consensus** CLAIM(3MADCVqL534@36:13, 5vyKhm2NTfw@36:08, Tu-hZ6lqNtY@31:02, leo1FZ6vu1I@52:00, tsGarhpWOws@45:00)
- For a streaming catalog that fetches many thumbnails at once, HTTP/2 multiplexing is a core requirement, not a nice-to-have. **single-source** CLAIM(Tu-hZ6lqNtY@31:37)
- Price every extra TCP connection before adding one: a handshake costs three network trips (about one and a half round trips), connections consume client and server memory, and there is no prioritization between them. **single-source** CLAIM(gxF9fLo5XQw@18:27, gxF9fLo5XQw@19:08)
- Treat domain sharding as a legacy hack: it buys parallelism by pretending one server is several, with all the connection overhead that implies. **single-source** CLAIM(gxF9fLo5XQw@16:36, gxF9fLo5XQw@17:16)

**Request count**

- Cut the number of requests rather than multiplying connections: reuse through caching, pack images into sprites, bundle CSS and JS, inline critical styles. **single-source** CLAIM(gxF9fLo5XQw@20:00)
- Weigh bundling against cache granularity: any small change produces a new bundle that must be downloaded whole. **single-source** CLAIM(gxF9fLo5XQw@21:51)
- Render latency scales with resource count, because the page appears only after every critical resource has loaded. **single-source** CLAIM(gxF9fLo5XQw@14:03)

**Caching in layers**

- Plan caching in layers: your own client cache for the hybrid approach, the browser cache driven by server response headers, and a server cache for expensive searches. **single-source** CLAIM(9mjsRrJYOWE@41:17)
- Combine service-worker caching with HTTP caching semantics such as ETag. **single-source** CLAIM(Tu-hZ6lqNtY@42:13)

**CDN and edge**

- Serve assets from a CDN and keep the optimizer behind it so each rendition is generated once and served from the nearest edge. **consensus** CLAIM(3MADCVqL534@40:20, 5vyKhm2NTfw@34:42, Tu-hZ6lqNtY@35:01, LEaiGjffLEs@33:14, 9mjsRrJYOWE@45:15)

**Interactive requests (typeahead and search)**

- Debounce the search call so a typing burst produces one request, not one per letter. **consensus (cross-stage, also fesd-api-network)** CLAIM(9aOXGE7wAZo@22:01, 9mjsRrJYOWE@43:24)
- Cancel superseded in-flight requests when a newer query supersedes them; this is part of the network-efficiency requirement, not an afterthought. **single-source (cross-stage)** CLAIM(9mjsRrJYOWE@39:55)
- A widget owns only what it controls: it cannot set app-wide compression or CDN policy, so it optimizes its own request pattern (debounce plus its cache) and leaves the rest to the application. **single-source** CLAIM(9aOXGE7wAZo@21:28)

**Counter-case**

- Skip network optimization entirely for an offline-first app that loads its sources once; adding that overhead is a mistake. **single-source** CLAIM(fmIiDLbLc_s@40:01, fmIiDLbLc_s@41:04)

## Decision table

| question | pick when | citation |
|---|---|---|
| compress first or re-architect first | always compress and modernize formats first | CLAIM(LEaiGjffLEs@28:56) |
| gzip or Brotli | gzip as the floor, Brotli/Zstd where the client supports it | CLAIM(3MADCVqL534@35:08, tsGarhpWOws@47:55) |
| more connections or fewer requests | fewer requests; every connection costs a handshake and memory | CLAIM(gxF9fLo5XQw@18:27, gxF9fLo5XQw@20:00) |
| one bundle or split | split when it improves cache stability; accept invalidation granularity cost | CLAIM(gxF9fLo5XQw@21:51, 3MADCVqL534@37:22) |
| per-keystroke request or debounced | debounced, with cancellation and a bounded query cache | CLAIM(9aOXGE7wAZo@22:01, 9mjsRrJYOWE@43:24) |
| optimize the network at all | skip it for offline-first apps that fetch sources once | CLAIM(fmIiDLbLc_s@40:01) |

## Worked cases

- gxF9fLo5XQw Deep dive into HTTP [Part 1]: the connection economics behind every recommendation here (handshake cost, sharding history, request count).
- 9mjsRrJYOWE Typeahead component - front-end system design: layered caching plus debounced, cancellable search requests.
- 9aOXGE7wAZo [Front-End System Design] - Typeahead Widget: widget-level request control (debounce and its own cache).
- Tu-hZ6lqNtY [Front-End Product Design] - Netflix: HTTP/2 as a hard requirement for a thumbnail-heavy catalog.
- 3MADCVqL534 [Front-End System Design] - Pinterest: the compression ladder with its savings numbers and the CDN-backed image service.

## Dated / contestable

- Domain sharding (CLAIM(gxF9fLo5XQw@16:36, gxF9fLo5XQw@17:16)) is already labeled legacy inside the corpus. Distiller note (not the author): HTTP/2 and HTTP/3 multiplexing removed the reason it existed; do not shard origins for parallelism today.
- The savings figures (gzip 40-50 percent, Brotli +10-20, CLAIM(3MADCVqL534@35:08, Tu-hZ6lqNtY@31:02)) are 2020-2021 approximations. Distiller note (not the author): measure your own payloads; the ordering (gzip floor, better encoding where supported) is the durable part.
- "Brotli rather than gzip" plus legacy/modern bundles (CLAIM(leo1FZ6vu1I@52:00)) mixes a current encoding choice with a dated delivery split. Distiller note (not the author): keep the encoding advice, revisit the bundle split.
- Zstd content-encoding (CLAIM(tsGarhpWOws@47:55)) was ahead of browser support in 2023. Distiller note (not the author): it is arriving in browsers now; keep it behind a content-encoding negotiation, with Brotli as the fallback.
