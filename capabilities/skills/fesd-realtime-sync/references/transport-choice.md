# transport-choice (fesd-realtime-sync)

Purpose: turn a freshness requirement and a traffic shape into one named live-update transport, using the author's own written pros/cons method.

When to load: at the start of every S07 job, whenever someone asks "SSE or WebSocket", and before any subscription interface is designed.

## Step checklist
1. Write the latency budget, direction (client reads versus writes), payload type (text versus binary, framed versus unframed), and device class on the page first.
2. Draw the pros/cons table with one row per option and one column per requirement. Never pick from taste.
3. Eliminate by direction: receive-only traffic does not pay for duplex.
4. Eliminate by cost: per-tick request overhead, persistent socket cost, HTTP/2 reimplementation cost.
5. Eliminate by environment: proxies and TCP-filtering firewalls, load balancer failover, HTTP/2 semantics.
6. Name the winner plus the fallback (for example SSE primary with long polling behind the subscription interface).
7. Check the dated claims at the bottom before shipping the decision.

## Laws

Decision procedure
- Evaluate transport options as a written pros/cons table before committing to one. consensus. CLAIM(LEaiGjffLEs@07:25)
- For live feed updates, compare long polling, WebSockets, and server-sent events before committing. consensus. CLAIM(5vyKhm2NTfw@22:04)
- Choose transport by named trade-offs: WebSockets for realtime duplex binary at the cost of statefulness and scaling pain; SSE for stateless HTTP/2 multiplexing and free reconnection at the cost of text-only one-way delivery. consensus. CLAIM(HR2jXy_wPg4@48:00)

Polling family
- Treat long polling as simple but expensive: a full request (headers, tokens) per tick and higher latency. consensus. CLAIM(5vyKhm2NTfw@22:44)
- Reject plain polling for chat: every request resends headers and tokens, wasting data on cellular links. consensus. CLAIM(LEaiGjffLEs@10:22)

Connection and environment costs
- Count persistent connections as a cost: one socket per tab scales badly and drains battery. single-source. CLAIM(LEaiGjffLEs@11:35)
- Weigh a transport against HTTP/2: if it forces you to reimplement multiplexing and asset splitting yourself, it is expensive. single-source. CLAIM(LEaiGjffLEs@12:21)
- Consider firewalls and proxies that filter TCP when choosing a protocol, since upgrade-based connections can be blocked. single-source. CLAIM(LEaiGjffLEs@14:01)

SSE
- Prefer SSE when you want HTTP/2 semantics, minimal payloads (text only), cheap resource use, and trivial load-balancer failover. consensus. CLAIM(LEaiGjffLEs@15:02)
- Pick server-sent events for feed updates when roughly 60ms latency is acceptable: low overhead, HTTP/2-friendly, easier to load balance. consensus. CLAIM(5vyKhm2NTfw@24:26)
- Choose server-sent events for receive-mostly updates: HTTP/2 friendly, text-only is enough, and it activates only the receive antenna on mobile radios. consensus. CLAIM(leo1FZ6vu1I@35:35)

WebSocket
- Skip WebSockets when true real-time is not required and HTTP/2 support matters more than bidirectional speed. consensus. CLAIM(5vyKhm2NTfw@23:43)
- Reject WebSockets when duplex is not needed: expensive to hold open, outside HTTP/2, hard to load balance. consensus. CLAIM(leo1FZ6vu1I@34:26)

Asymmetric and read-only cases
- When the inbound stream is one-way, use a hybrid: SSE for receiving, a plain HTTP request for sending, because receive volume dominates. single-source. CLAIM(LEaiGjffLEs@20:38)
- Note that a one-directional channel is acceptable when the client only reads data. single-source. CLAIM(HR2jXy_wPg4@51:00)

Framing, binary, and WebTransport
- Reject plain HTTP streaming for time-series data when it cannot mark frames, because financial payloads need frame boundaries. single-source. CLAIM(HR2jXy_wPg4@52:17)
- Prefer WebTransport where browsers and servers allow it: QUIC-based zero-RTT delivery is faster than WebSockets and it supports framing and binary data. single-source. CLAIM(HR2jXy_wPg4@53:01)

Interface
- Expose the live channel as a GraphQL subscription implemented over SSE, so the transport stays swappable (SSE, WebSocket or polling). single-source. CLAIM(leo1FZ6vu1I@38:41)

## Decision table

| option | direction | payload | HTTP/2 story | connection cost | ops cost | pick when | avoid when | cite |
|---|---|---|---|---|---|---|---|---|
| short polling | request/response | any | inherits HTTP | one full request per tick, headers and tokens resent | lowest build cost | updates are rare, simplicity wins | freshness matters or data budget is tight | CLAIM(5vyKhm2NTfw@22:44, LEaiGjffLEs@10:22) |
| long polling | request/response held open | any | inherits HTTP | full request per tick, higher latency | low build, timeout tuning | you want near-push with no new infrastructure | per-tick overhead is visible to users | CLAIM(5vyKhm2NTfw@22:44) |
| SSE | server to client | text | stateless streams, multiplexed, free reconnection | one cheap stream, battery friendly | trivial failover | client mostly reads, text is enough | heavy outbound or binary framing | CLAIM(LEaiGjffLEs@15:02, 5vyKhm2NTfw@24:26, leo1FZ6vu1I@35:35) |
| SSE plus plain HTTP send | push in, request out | text in, any out | same as SSE | same as SSE | low | inbound volume dominates outbound | sends dominate or need guaranteed ordering across both paths | CLAIM(LEaiGjffLEs@20:38) |
| WebSocket | full duplex | text and binary | outside the HTTP/2 story he assumes; reconnection and multiplexing are yours | persistent socket per tab, battery cost | stateful, scaling and load-balancing pain | true duplex realtime is the product | stream is receive-only | CLAIM(5vyKhm2NTfw@23:43, LEaiGjffLEs@11:35, leo1FZ6vu1I@34:26, HR2jXy_wPg4@48:00) |
| plain HTTP streaming | server to client | binary possible | HTTP/2 benefits | one stream | handshake latency | nothing better is available | payload needs message framing | CLAIM(HR2jXy_wPg4@52:17) |
| WebTransport | duplex or one-way | binary with framing | QUIC/UDP based, zero RTT | low latency | support matrix risk | browsers and servers allow it | coverage is unproven on your audience | CLAIM(HR2jXy_wPg4@53:01) |

Multi-criteria filter as he applies it (each row is one requirement he writes down before comparing):

| requirement | what it eliminates | cite |
|---|---|---|
| client only reads | all duplex options | CLAIM(HR2jXy_wPg4@51:00, leo1FZ6vu1I@34:26) |
| latency budget around 60ms is fine | nothing; it licenses SSE over WebSocket | CLAIM(5vyKhm2NTfw@24:26) |
| cellular data and battery matter | polling, heavy sockets | CLAIM(LEaiGjffLEs@10:22, LEaiGjffLEs@11:35, leo1FZ6vu1I@35:35) |
| HTTP/2 semantics must come for free | hand-rolled multiplexing over WebSocket | CLAIM(LEaiGjffLEs@12:21) |
| corporate proxies in the path | upgrade-based connections | CLAIM(LEaiGjffLEs@14:01) |
| framed binary time-series | plain HTTP streaming | CLAIM(HR2jXy_wPg4@52:17) |
| fastest delivery where supported | anything but WebTransport | CLAIM(HR2jXy_wPg4@53:01) |

## Worked cases
- 5vyKhm2NTfw: [Front End System Design] - Facebook News Feed. The canonical three-way comparison (long polling, WebSocket, SSE) for feed updates.
- LEaiGjffLEs: [Front-End System Design] - Chat application. The full pros/cons table and the hybrid SSE plus POST verdict for chat.
- leo1FZ6vu1I: [Front-End System Design] - Google Calendar. Protocol comparison against a freshness requirement a calendar can afford.
- tsGarhpWOws: Frontend System Design - Notion-like editor. WebSockets rejected for an offline-first editor in favor of SSE.
- HR2jXy_wPg4: Frontend System Design - Financial Dashboard / TradingView. Four-transport comparison on binary, framing, statefulness and latency.

## Dated / contestable
- "WebSockets cannot use HTTP/2" (2020). Distiller note (not the author): RFC 8441 extended CONNECT tunnels WebSockets over HTTP/2 and HTTP/3; support is uneven but the claim is no longer a blanket rule. His load-balancer and proxy objections still hold. CLAIM(5vyKhm2NTfw@23:43)
- SSE payloads described as binary. Distiller note (not the author): EventSource delivers text (with JSON in it); WebSocket and WebTransport are the binary routes. CLAIM(5vyKhm2NTfw@24:35)
- WebTransport coverage at roughly 60 percent of browsers, mid-2025 snapshot. Distiller note (not the author): treat as a dated number and re-measure. CLAIM(HR2jXy_wPg4@52:55)
- "WebSockets will soon be replaced" is his opinion; WebSocket usage in trading and chat stacks remains widespread. CLAIM(HR2jXy_wPg4@49:22)
- GraphQL subscriptions over SSE used to mean writing your own transport glue; now dedicated libraries exist, so the swappable-interface law is cheaper to obey. CLAIM(leo1FZ6vu1I@38:41, leo1FZ6vu1I@41:23)
