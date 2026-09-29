# HTTP protocol

Purpose: the protocol floor under every frontend API call - what a page load actually does, which version the stack serves, and which performance advice belongs to which protocol era.

When to load: before reasoning about request cost, headers, connection behavior, caching layers or wire size; before quoting 1.1-era performance workarounds.

## The fetch path he teaches first

Walk the whole path before analyzing anything: domain name resolved to an IP address, TCP connection
opened on the web port (80 plain, 443 encrypted), request sent, page parsed, critical resources
loaded, then background requests fired after first render (CLAIM(gxF9fLo5XQw@01:08)). HTTP rides on
TCP/IP above the physical link and sits at the application layer of the layered model, with the
presentation layer handling formats and the session layer handling encryption
(CLAIM(gxF9fLo5XQw@03:33)). If the reviewer cannot draw this path, protocol advice is guesswork.

## Laws

- Explain the whole fetch path before analyzing protocol behavior: name lookup to IP, TCP connection
  on port 80 or 443, request, page parse, critical resources, then background requests.
  Single-source. (CLAIM(gxF9fLo5XQw@01:08))
- Remember that HTTP rides on TCP/IP above the physical link and sits at the application layer of
  the layered model, with presentation handling formats and session handling encryption.
  Single-source. (CLAIM(gxF9fLo5XQw@03:33))
- Teach the protocol through its versions: 0.9 allowed only a GET with no headers or error states,
  1.0 added methods, headers, status codes and a version field, 1.1 refined the header model.
  Single-source. (CLAIM(gxF9fLo5XQw@05:37, gxF9fLo5XQw@06:30, gxF9fLo5XQw@08:36))
- Send a Host header on every 1.1 request; virtual hosting makes the host part of the URL mandatory
  rather than implicit. Single-source. (CLAIM(gxF9fLo5XQw@10:01))
- Treat persistent connections as the 1.1 default, so closing a connection requires an explicit
  close signal from the server. Single-source. (CLAIM(gxF9fLo5XQw@11:22))
- Diagnose 1.1 by its two structural limits: resources load sequentially with no parallelism, and
  text headers repeat uncompressed across many requests. Single-source.
  (CLAIM(gxF9fLo5XQw@13:23, gxF9fLo5XQw@14:47))
- Check which protocol version a stack actually serves before applying 1.1-era performance advice,
  because some of it contradicts the newer paradigm. Single-source. (CLAIM(gxF9fLo5XQw@16:08))
- Treat caching as multi-level: server cache and browser cache you do not control, plus your own
  widget cache with a TTL. Single-source. (CLAIM(9aOXGE7wAZo@22:26))
- Compare transports (long polling, WebSocket, SSE) against the product's freshness requirement
  before committing. Single-source. (CLAIM(leo1FZ6vu1I@32:42))
- Put a CDN in front of the data servers to keep latency low across regions. Single-source.
  (CLAIM(HR2jXy_wPg4@55:17))

## Version map

| Version | What it adds | What it costs | Cites |
|---|---|---|---|
| 0.9 | a single GET, raw character stream back | no headers, no methods, no error states | CLAIM(gxF9fLo5XQw@05:37) |
| 1.0 | methods (HEAD, POST with body), headers as key-value map, status codes, version field | connection per request unless kept alive | CLAIM(gxF9fLo5XQw@06:30, gxF9fLo5XQw@06:35) |
| 1.1 | mandatory Host header, persistent connections by default, more methods (OPTIONS, PUT, CONNECT, TRACE, DELETE), better caching, proxy and auth support | sequential loading per connection, repeated uncompressed text headers | CLAIM(gxF9fLo5XQw@08:36, gxF9fLo5XQw@10:01, gxF9fLo5XQw@11:22, gxF9fLo5XQw@13:23) |
| 2 and later | multiplexing and prioritization (teased for part 2 of his series) | not covered in this video | CLAIM(gxF9fLo5XQw@22:45) |

## Decision table

| Decision | Pick | When to deviate | Cites |
|---|---|---|---|
| Performance advice source | match the served protocol version | 1.1 advice on a multiplexed stack is counterproductive | CLAIM(gxF9fLo5XQw@16:08) |
| Connection strategy | fewer requests, persistent connections | more connections only as a last resort; each costs handshake time and memory | CLAIM(gxF9fLo5XQw@11:22, gxF9fLo5XQw@18:27) |
| Caching | all three levels named (server, browser, own TTL cache) | assume nothing about caches you do not control | CLAIM(9aOXGE7wAZo@22:26) |
| Data-server placement | CDN in front | direct origin only for private, non-cacheable data | CLAIM(HR2jXy_wPg4@55:17) |
| Realtime transport | compare long polling, WebSocket, SSE against freshness need | none; the freshness requirement decides | CLAIM(leo1FZ6vu1I@32:42) |

## Anti-patterns

- Applying domain sharding or extra connections to a stack that already multiplexes
  (CLAIM(gxF9fLo5XQw@16:36, gxF9fLo5XQw@16:08)).
- Accepting hundreds of kilobytes of repeated headers across tens of requests without noticing
  (CLAIM(gxF9fLo5XQw@15:26)).
- Opening more connections as the primary performance fix instead of removing the need for them
  (CLAIM(gxF9fLo5XQw@19:20)).
- Reasoning about headers and caching without knowing which version the server speaks
  (CLAIM(gxF9fLo5XQw@16:08)).

## Worked cases

- gxF9fLo5XQw, Deep dive into HTTP [Part 1]: the entire protocol floor. Steal the layered teaching
  walk (CLAIM(gxF9fLo5XQw@01:08, gxF9fLo5XQw@03:33)).
- 9aOXGE7wAZo, [Front-End System Design] - Typeahead Widget: the multi-level caching frame
  (CLAIM(9aOXGE7wAZo@22:26)).
- leo1FZ6vu1I, [Front-End System Design] - Google Calendar: transport choice driven by freshness
  requirements (CLAIM(leo1FZ6vu1I@32:42)).
- HR2jXy_wPg4, Frontend System Design - Financial Dashboard / TradingView: CDN placement for
  geographic latency (CLAIM(HR2jXy_wPg4@55:17)).

## Dated / contestable

- The video stops at 1.1 and points to HTTP/2 as the fix, deferred to a part 2. Distiller note (not
  the author): HTTP/2 is now common and HTTP/3 over QUIC carries real traffic share; the story
  continues well past this 2022 endpoint. (CLAIM(gxF9fLo5XQw@22:45))
- The six-connections-per-domain figure describes 1.1-era browser behavior. Distiller note (not the
  author): multiplexed protocols change the arithmetic behind domain sharding entirely.
  (CLAIM(gxF9fLo5XQw@16:39))
- The traffic statistics he cites (average page weight rising from about 100 KB to around 5 MB at
  roughly 70 requests per site) are period reporting. Distiller note (not the author): re-measure
  before quoting. (CLAIM(gxF9fLo5XQw@12:46))
- "Engineers still use the 1.1 workarounds although they are outdated" was accurate for 2022.
  Distiller note (not the author): HTTP/2 is the common default now, with 1.1-only pockets left.
  (CLAIM(gxF9fLo5XQw@00:37))
- The claim that WebSockets cannot ride HTTP/2 is contested. Distiller note (not the author):
  extended CONNECT (RFC 8441) carries them in later stacks, though browser and server support is
  uneven and the load-balancing costs remain. (CLAIM(5vyKhm2NTfw@23:50))
- Compression and request-count advice in the corpus (zipping then Brotli, bundle splitting,
  sprites) belongs to the performance stage. Distiller note (not the author): keep those laws in
  the S08 skill and cite them from there.
  (CLAIM(3MADCVqL534@35:08, gxF9fLo5XQw@20:00))
