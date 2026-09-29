# offline-first (fesd-realtime-sync)

Purpose: design the offline and reconnect path of a live app (what caches, what queues, how the client resyncs) using this author's offline-first and service-worker practice.

When to load: when the product must work offline or on flaky networks, when a write queue is being designed, and whenever a design says "PWA" or "offline mode".

## Step checklist
1. Write the offline requirement as a requirement, not an optimization: what must work with no network, what may degrade.
2. Decide what is cached: app shell (code, styles) plus the data the user reads offline.
3. Choose the live channel with offline in mind: he rejects WebSockets as unnecessary complexity for an offline-first app and prefers SSE for one-directional updates.
4. Design the sync loop: last-sync checkpoint on the wire, deltas instead of whole documents, updates flowing into client state automatically.
5. Design the offline write path (queue, order, retry, idempotency). Name it even when the author does not: an unstated write path is a defect.
6. Mark any AppCache-era mechanism as dated and replace with service-worker caching.

## Laws (this stage)
- Rejected WebSockets for an offline-first app as unnecessary complexity; prefer HTTP/2 server-sent events for one-directional live updates. single-source. CLAIM(tsGarhpWOws@36:37)
- Let a correctly configured GraphQL layer keep client and server state in sync so subscription updates flow into client state automatically. single-source. CLAIM(tsGarhpWOws@43:03)

## Laws (adjacent stages, cited because this sub-topic needs them)
Requirements
- Add offline and reduced-network behavior as a functional requirement (PWA mode for already-loaded data, usable on slow connections). (stage S02) CLAIM(3MADCVqL534@07:39)
- List offline support and delta-based network updates as advanced requirements for an offline-first editor. (stage S02) CLAIM(tsGarhpWOws@06:56)
- Treat mobile-first, offline usage and battery cost as requirements, not optimizations. (stage S02) CLAIM(leo1FZ6vu1I@03:38)

Caching
- Support offline reading (PWA) by caching resources through service workers. (stage S08) CLAIM(5vyKhm2NTfw@43:40)
- Use a service worker to cache chat code, styles, message data and images so history reads offline. (stage S08) CLAIM(LEaiGjffLEs@40:13)
- Support offline mode by caching JS, CSS, data, and images through registered service workers. (stage S08) CLAIM(3MADCVqL534@47:44)
- Enable HTTP/2 and a service worker that caches fetched assets so the app boots fast and works offline. (stage S08) CLAIM(tsGarhpWOws@45:00)
- Cache scripts, styles, data, and images in a service worker and combine with HTTP caching semantics like ETag. (stage S08) CLAIM(Tu-hZ6lqNtY@42:13)
- Skip network optimization entirely for an offline-first app that loads its sources once. (stage S08) CLAIM(fmIiDLbLc_s@40:01)

Sync and deltas
- Sync from a timestamp checkpoint: send the last-sync marker so the client only pulls messages from that point onward. (stage S05) CLAIM(LEaiGjffLEs@26:30)
- Send content diffs to the server instead of whole pages, using a delta library to compute them. (stage S06) CLAIM(tsGarhpWOws@41:31)

## Queues (where the corpus is silent)
Distiller note (not the author): no episode designs an offline write queue. For product work the minimum bar is: queue writes locally (IndexedDB), assign each a client-generated id so replay is idempotent, replay in order on reconnect, surface failures instead of dropping them, and resolve replay conflicts against the server version rather than blind last-write-wins. The author's delta-plus-checkpoint sync (CLAIM(LEaiGjffLEs@26:30), CLAIM(tsGarhpWOws@41:31)) covers the read side of reconnect; the write side is yours to design.

## Decision table
| offline question | answer in this corpus | cite |
|---|---|---|
| what must work offline | already-loaded content reads; core flows usable on slow connections | CLAIM(3MADCVqL534@07:39) |
| what caches | app shell plus data, via service workers | CLAIM(5vyKhm2NTfw@43:40, LEaiGjffLEs@40:13, 3MADCVqL534@47:44) |
| which live transport for an offline-first app | SSE over WebSockets for one-directional updates | CLAIM(tsGarhpWOws@36:37) |
| how does the client catch up | timestamp checkpoint plus deltas | CLAIM(LEaiGjffLEs@26:30, tsGarhpWOws@41:31) |
| where do updates land | client state, via the subscription layer | CLAIM(tsGarhpWOws@43:03) |
| is a network optimization pass needed | no, if the app loads its sources once | CLAIM(fmIiDLbLc_s@40:01) |
| how are offline writes queued | not covered; design it explicitly | distiller note above |

## Worked cases
- tsGarhpWOws: Frontend System Design - Notion-like editor. The offline-first requirement, the SSE-over-WebSocket call, delta updates, service-worker asset caching.
- LEaiGjffLEs: [Front-End System Design] - Chat application. Service-worker caching of message history for offline reads, timestamp checkpoint sync.
- 5vyKhm2NTfw: [Front End System Design] - Facebook News Feed. PWA offline reading via service workers.
- fmIiDLbLc_s: [Front-End System Design] - Google Sheets. The pure offline stance: no network layer designed at all.
- leo1FZ6vu1I: [Front-End System Design] - Google Calendar. PWA/offline as requirement; the offline section itself is where the dated AppCache wording lives.

## Dated / contestable
- AppCache. Distiller note (not the author): the browser application-cache mechanism is deprecated and removed; service workers own offline resource caching today. Two episodes name AppCache-era wording for offline support. CLAIM(5vyKhm2NTfw@40:02, leo1FZ6vu1I@55:40)
- Web workers named alongside app cache for offline operation. Distiller note (not the author): web workers do not cache resources; they move computation off the main thread. The offline intent is current, the mechanism pairing is not. CLAIM(leo1FZ6vu1I@55:40)
- Offline-first scoped as "load sources once" is an interview scoping choice, not how a real Sheets-class product behaves. CLAIM(fmIiDLbLc_s@05:01)
