# Case: Frontend System Design - Financial Dashboard / TradingView

Source: https://www.youtube.com/watch?v=HR2jXy_wPg4 (video id HR2jXy_wPg4). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video HR2jXy_wPg4 against the local transcript.

- published 2025-07-29, duration ~61 min (3675s), problem type: product-design (multi-chart trading dashboard; heavy component-design and data-engineering inside it)

## Author's framework as used
1. Demo the real product first (TradingView multi-layout, resizable windows, chart synchronization by interval and by symbol) so the design targets observed behavior, then state the two core challenges: resizable layout and large shared datasets. CLAIM(HR2jXy_wPg4@00:33)
2. Run a prepared interview plan: requirements + mockup, layout design, data model, backend API and protocol, data flow and chart synchronization, multi-monitor support. CLAIM(HR2jXy_wPg4@02:16)
3. Write product requirements (resizable multi-chart grid layouts, heterogeneous data sources behind one unified data interface, per-chart models with a generic server model, sync parameters like asset and time frame). CLAIM(HR2jXy_wPg4@03:16)
4. Write non-product requirements (network performance and cache use, rendering stability with downscaled partial charts, one interface over legacy APIs). CLAIM(HR2jXy_wPg4@04:38)
5. Layout design: pick CSS grid (modern-browser assumption), then solve drag and drop with his three-layer "sandwich" construction and delegated events. CLAIM(HR2jXy_wPg4@06:40)
6. Data and property model: a chart-element interface whose transformer maps generic source data to each chart's own model, a finance data type (asset, start, end, interval, open/close points), and a dashboard component type (range, asset, chart union, render, interval). CLAIM(HR2jXy_wPg4@17:27)
7. State design: decide global state versus IndexedDB, then introduce time-bucketed storage with a compound key (asset ID, bucket ID, time frame). CLAIM(HR2jXy_wPg4@26:23)
8. Quantify the design: calculate storage requirement per asset per day and per year before accepting the scheme. CLAIM(HR2jXy_wPg4@35:15)
9. Define the sampling rules: downsampling from fine buckets is local and lossless; upsampling needs server data and gets placeholder buckets meanwhile. CLAIM(HR2jXy_wPg4@41:44)
10. API layer: unify legacy endpoints behind one getData/subscription interface, then compare WebSockets, SSE, HTTP streaming, and WebTransport on binary support, framing, statefulness, and latency. CLAIM(HR2jXy_wPg4@46:06)
11. Add multi-window support: host window owning writes, extension windows replicating state, localStorage for role discovery, BroadcastChannel for events. CLAIM(HR2jXy_wPg4@55:42)

## Worked design
Requirements
- Multi-chart dashboards where the user chooses a grid layout and each chart is independently resizable. CLAIM(HR2jXy_wPg4@03:16)
- Data may come from several legacy APIs but must arrive in one unified shape. CLAIM(HR2jXy_wPg4@03:35)
- Each chart type (table, pie, bar) may have its own display model, with per-chart transformation from the generic server model. CLAIM(HR2jXy_wPg4@03:57)
- Sync parameters (asset ID, time frame) propagate across charts when sync mode is on. CLAIM(HR2jXy_wPg4@04:31)
- Non-functional: network efficiency, rendering stability on parameter change, legacy-API unification. CLAIM(HR2jXy_wPg4@04:38)

Components
- Draggable container: owns all drag-and-drop behavior and accepts any dashboard component. CLAIM(HR2jXy_wPg4@17:52)
- Dashboard component: owns requests, holds range/asset/interval state, exposes render(source) for custom rendering. CLAIM(HR2jXy_wPg4@24:01)
- Chart element: typed generic over its data model with a transformer from source data. CLAIM(HR2jXy_wPg4@19:34)
- Grid cell layer: droppable cells with data-column/data-row attributes; container-level handler via event bubbling. CLAIM(HR2jXy_wPg4@14:18)

Data model
- Finance data type: asset (string), start, end, interval, and points with open/close numbers. CLAIM(HR2jXy_wPg4@21:22)
- Application state keyed by asset ID, each holding bucketed point arrays. CLAIM(HR2jXy_wPg4@27:59)
- Compound key: asset ID + bucket ID + time frame, mapping to a points array. CLAIM(HR2jXy_wPg4@31:47)
- Bucket sizes of 5 minutes, 1 hour, and 1 day coexist in the same store; larger buckets are better for wide ranges. CLAIM(HR2jXy_wPg4@33:05)
- Storage estimate for the worst case: one point per second, 86,400 points/day at 8 bytes = ~0.7 MB/asset/day, ~255 MB/asset/year. CLAIM(HR2jXy_wPg4@36:57)

API
- Single getData interface over legacy endpoints returning the unified data type. CLAIM(HR2jXy_wPg4@46:29)
- Subscription-style access implemented by different transports (polling, streaming, SSE, WebSockets, WebTransport). CLAIM(HR2jXy_wPg4@47:02)
- WebSockets: realtime, binary, duplex; cost is state handling, reconnection, serialization, and scaling. CLAIM(HR2jXy_wPg4@48:41)
- SSE: stateless HTTP/2, multiplexed (hundreds of streams per TCP connection), free reconnection; slower, text-only, one-way. CLAIM(HR2jXy_wPg4@49:38)
- HTTP streaming: binary and HTTP/2 benefits, but handshake latency and no frame marking. CLAIM(HR2jXy_wPg4@51:17)
- WebTransport: QUIC/UDP-based, zero-RTT, framing plus binary, faster than WebSockets; limited browser/server support (~60%). CLAIM(HR2jXy_wPg4@52:42)

Realtime
- Live updates flow through the chosen subscription transport into the dashboard state. CLAIM(HR2jXy_wPg4@47:02)
- Cross-window live sync via BroadcastChannel events between host and extension windows. CLAIM(HR2jXy_wPg4@58:58)
- Multi-monitor use case: second window is an extension of the app, not a standalone instance. CLAIM(HR2jXy_wPg4@55:53)

Perf
- Bucketed compound-key lookups turn 3,600-point scans into ~12 bucket reads for a 60-minute range. CLAIM(HR2jXy_wPg4@30:08)
- Local downsampling avoids refetch when switching to a coarser time frame. CLAIM(HR2jXy_wPg4@42:30)
- Binary serialization (protobuf-class) compresses payloads roughly 6-8x, reducing bytes and latency. CLAIM(HR2jXy_wPg4@54:23)
- Single delegated drag handler instead of per-cell handlers (64 handlers on an 8x8 grid is called out as wasteful). CLAIM(HR2jXy_wPg4@13:53)
- CDN for geographic latency. CLAIM(HR2jXy_wPg4@55:17)

A11y
- Not covered in this episode. (No accessibility discussion appears in the transcript.)

## Trade-offs he names
- Global state vs IndexedDB -> use both: runtime state for the active view, IndexedDB (the browser's only large disk store, roughly 2 GB/domain) for history. CLAIM(HR2jXy_wPg4@26:48)
- Per-point storage vs bucketed storage -> buckets, because raw per-second points force linear scans. CLAIM(HR2jXy_wPg4@29:20)
- One bucket size vs many -> store several sizes; storage overhead is acceptable on disk and pick the size to the visible range. CLAIM(HR2jXy_wPg4@33:05)
- WebSockets vs SSE vs HTTP streaming vs WebTransport -> WebTransport where supported, otherwise weigh realtime need against operational complexity; SSE suits read-only dashboards. CLAIM(HR2jXy_wPg4@54:01)
- Text vs binary payloads -> binary plus serialization when volumes are large, even with (de)serialization cost. CLAIM(HR2jXy_wPg4@54:23)
- Downsample vs refetch -> downsample locally when data exists; upsample only with server data and placeholders meanwhile. CLAIM(HR2jXy_wPg4@45:12)
- Per-cell handlers vs delegated handler -> delegated, for memory and performance. CLAIM(HR2jXy_wPg4@13:53)
- Multi-writer vs single-writer windows -> single writer (host), so no cross-window races are possible. CLAIM(HR2jXy_wPg4@60:03)

## Anti-patterns he warns about
- Do not store one point per second and scan it linearly; it makes every range query O(points). CLAIM(HR2jXy_wPg4@29:20)
- Do not assume upsampling can be done from local data; finer detail requires a server request. CLAIM(HR2jXy_wPg4@44:11)
- Do not display an empty chart while upsampled data loads; placeholder buckets keep something on screen. CLAIM(HR2jXy_wPg4@44:19)
- Do not attach event handlers to every grid cell; register one on the container. CLAIM(HR2jXy_wPg4@13:53)
- Do not let multiple windows write state; make extensions read-only replicas. CLAIM(HR2jXy_wPg4@60:03)
- Do not pick HTTP streaming for framed time-series data; it lacks frame marking. CLAIM(HR2jXy_wPg4@52:17)
- He notes his own slip: the bucket-ID formula was written inverted at first (bucket size over time) and he corrected it to time over bucket size. CLAIM(HR2jXy_wPg4@33:39)

## Dated / contestable
- WebTransport support cited as roughly 60% of browsers and not all servers (mid-2025 claim); treat the coverage number as a dated snapshot and re-check before designing on it. CLAIM(HR2jXy_wPg4@52:55)
- The prediction that WebSockets will soon be replaced is his opinion, not a settled industry consensus; WebSocket usage remains widespread in trading UIs. CLAIM(HR2jXy_wPg4@49:22)
- The IndexedDB quota framing (about 30% of disk, roughly 2 GB per domain) is approximate and browser-dependent; actual quotas are origin- and browser-specific and eviction policies differ. CLAIM(HR2jXy_wPg4@27:08)
- The protobuf 6-8x compression figure is an unsourced estimate; actual ratios depend on payload shape and encoding choices. CLAIM(HR2jXy_wPg4@54:23)
- His terminology slips (he cannot recall the term for frame marking) are in the transcript; the concept he means is message framing / envelope delimiting. CLAIM(HR2jXy_wPg4@51:52)
