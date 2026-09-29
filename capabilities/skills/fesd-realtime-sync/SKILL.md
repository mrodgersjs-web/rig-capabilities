---
name: fesd-realtime-sync
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Stage S07 (realtime and sync) of the Front-End System Design family: how to pick a live-update
  transport (short polling, long polling, SSE, WebSocket, plain HTTP streaming, WebTransport), how to
  wrap it in a swappable subscription interface, how client and server state stay in sync, and where
  collaboration conflict handling sits relative to a front-end design. Produces a written transport
  decision record plus a sync model (initial chunk, deltas, resync checkpoint, offline behavior).
  Use when designing live feeds, chat, notifications, collaborative or offline-first editors,
  streaming dashboards, or when asked "SSE or WebSocket", "how do I sync client state", or "design
  the realtime layer". Cites corpus "20 laws from 5 Front-End Engineer videos". JEV-FIRST MANDATE,
  findable at task start: typed judgments in this stage go to rig-s1gate (Jev) BEFORE any frontier
  LLM call; DEFERRED is the only answer when the classifier is down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, realtime, sync, sse, websocket, offline, collaboration]
outcome: "code-engineering: a live-update design whose transport, sync loop, and conflict stance are chosen from a written comparison and cited to source"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-realtime-sync/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S07"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Realtime and sync design (stage S07)

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-api-designer and fesd-transport-picker loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate
Typed judgments this stage forces: (1) which transport fits these latency, direction, and payload requirements; (2) is this transport comparison table complete enough to decide from; (3) is this sync design complete (initial load, deltas, resync, offline, conflict stance all named); (4) is this offline write queue safe to ship (ordering, idempotency, retry named). Send each to Jev first: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Nearest existing rubric: app.stack, advisory until calibrated. A pass needs every required signal above 0.9. Classifier down, erroring or rubric missing = DEFERRED, never a guessed verdict. An advisory PASS is not permission to ship or publish.

## When to use
- A design needs live updates: feeds, chat, calendars, notifications, quotes, dashboards.
- Someone asks "SSE or WebSocket", "do I need WebSockets", "how do I push updates", "how do I do offline sync", "how do two users edit the same document".
- The previous stage (API and network) named a freshness requirement and now a channel must be chosen.
- An existing design re-fetches on a timer and you need to name the better pattern and why.

Not the stage for: rendering performance (fesd-performance), store shape (fesd-state-data), endpoint design (fesd-api-network). Those come in through the input contract below.

## Inputs and output contract
Consumes from the previous stages: the freshness requirement as a number (how stale is acceptable), the traffic shape (how much the client reads versus writes), the payload shape (text versus binary, framed versus unframed), the entity model, and the API surface.

Emits one artifact, the realtime and sync record, with these headings:
1. Requirements restated (latency budget, direction, payload, offline expectation, device and network assumptions).
2. Transport decision table (every option with named trade-offs) plus the chosen transport and the reason.
3. Channel interface (subscribe / initial chunk / incremental update / send path), transport-swappable.
4. Sync model (resync checkpoint, delta policy, how updates land in client state).
5. Offline behavior (what is cached, what queues, what reconciles on reconnect).
6. Conflict stance (last-write-wins, locking, OT/CRDT, or explicitly out of scope with the reason).
7. Dated claims check (any 2020-era assumption corrected or confirmed).

## Procedure
1. Write the requirements as numbers before touching protocols: latency budget, read/write ratio, payload weight, device class. (Reference: references/offline-first.md step 1; the budgeting habit is what makes step 3 decidable.)
2. Build the written transport comparison table. Load references/transport-choice.md. Cite: evaluate the options in a written pros/cons table before committing CLAIM(LEaiGjffLEs@07:25); for live feed updates, compare long polling, WebSockets and server-sent events before committing CLAIM(5vyKhm2NTfw@22:04); choose transport by named trade-offs, not taste CLAIM(HR2jXy_wPg4@48:00).
3. Filter by direction first. If the client only reads, a one-directional channel is acceptable CLAIM(HR2jXy_wPg4@51:00), and WebSockets are rejected when duplex is not needed CLAIM(leo1FZ6vu1I@34:26).
4. Price the cheap-looking options: long polling is simple but expensive, a full request with headers and tokens per tick plus higher latency CLAIM(5vyKhm2NTfw@22:44); plain polling for chat resends headers and tokens and wastes cellular data CLAIM(LEaiGjffLEs@10:22); count persistent connections as a cost, one socket per tab scales badly and drains battery CLAIM(LEaiGjffLEs@11:35).
5. Weigh the environment: HTTP/2 semantics, load-balancer failover, and proxies. Cite: weigh a transport against HTTP/2, if it forces you to reimplement multiplexing it is expensive CLAIM(LEaiGjffLEs@12:21); prefer SSE when you want HTTP/2 semantics, minimal text payloads, cheap resource use and trivial failover CLAIM(LEaiGjffLEs@15:02); consider firewalls and proxies that filter TCP, upgrade-based connections can be blocked CLAIM(LEaiGjffLEs@14:01).
6. Make the pick. SSE for receive-mostly feeds at roughly 60ms tolerance CLAIM(5vyKhm2NTfw@24:26) and for mobile receive antennas CLAIM(leo1FZ6vu1I@35:35). If inbound dominates outbound, run a hybrid: SSE to receive, plain HTTP request to send CLAIM(LEaiGjffLEs@20:38). Reach for WebTransport where browsers and servers allow it CLAIM(HR2jXy_wPg4@53:01), and reject plain HTTP streaming for time-series data that needs frame boundaries CLAIM(HR2jXy_wPg4@52:17).
7. Wrap the channel in a subscription interface so the transport stays swappable CLAIM(leo1FZ6vu1I@38:41), and let a correctly configured GraphQL layer keep client and server state in sync so subscription updates flow into client state automatically CLAIM(tsGarhpWOws@43:03).
8. Write the sync and offline model. Load references/offline-first.md. The offline-first case for SSE over WebSockets is on record CLAIM(tsGarhpWOws@36:37).
9. State the conflict stance explicitly. Load references/collaboration-and-conflicts.md. Declare conflict resolution out of scope for a front-end system design, mention it, and move on rather than designing CRDTs CLAIM(tsGarhpWOws@04:20).
10. Run the dated-claims check in the Dated / contestable section below before the record is called final.

## Core laws
Single-author corpus: "consensus" means he repeats the point in 2 or more videos, not that the industry agrees.

Decide from a written comparison
- Evaluate transport options as a written pros/cons table before committing to one, and decide by matching each option against the requirements you wrote down. consensus. CLAIM(LEaiGjffLEs@07:25, 5vyKhm2NTfw@22:04, HR2jXy_wPg4@48:00)

SSE is the default for read-mostly live data
- Prefer server-sent events when updates mostly flow to the client: HTTP/2 friendly, minimal text payloads, cheap to hold, trivial load-balancer failover, and on mobile it only activates the receive radio. consensus. CLAIM(5vyKhm2NTfw@24:26, LEaiGjffLEs@15:02, leo1FZ6vu1I@35:35, tsGarhpWOws@36:37)

WebSockets only when duplex earns its cost
- Skip WebSockets when true real-time duplex is not required: they are expensive to hold open, outside the HTTP/2 story his episodes assume, and hard to load balance. consensus. CLAIM(5vyKhm2NTfw@23:43, leo1FZ6vu1I@34:26, tsGarhpWOws@36:37)
- Note that a one-directional channel is acceptable when the client only reads data. single-source. CLAIM(HR2jXy_wPg4@51:00)

Polling costs more than it looks
- Treat long polling as simple but expensive: a full request with headers and tokens per tick, plus higher latency. consensus. CLAIM(5vyKhm2NTfw@22:44, LEaiGjffLEs@10:22)
- Count persistent connections as a cost: one socket per tab scales badly and drains battery. single-source. CLAIM(LEaiGjffLEs@11:35)

Match the transport to the environment
- Weigh a transport against HTTP/2: if it forces you to reimplement multiplexing and asset splitting yourself, it is expensive. single-source. CLAIM(LEaiGjffLEs@12:21)
- Consider firewalls and proxies that filter TCP when choosing a protocol, since upgrade-based connections can be blocked. single-source. CLAIM(LEaiGjffLEs@14:01)

Asymmetric traffic is a design lever
- When the inbound stream is one-way, use a hybrid: SSE for receiving, a plain HTTP request for sending, because receive volume dominates. single-source. CLAIM(LEaiGjffLEs@20:38)

Framing and newer transports
- Reject plain HTTP streaming for time-series data when it cannot mark frames, because financial payloads need frame boundaries. single-source. CLAIM(HR2jXy_wPg4@52:17)
- Prefer WebTransport where browsers and servers allow it: QUIC-based zero-RTT delivery beats WebSockets on latency and it supports framing and binary data. single-source. CLAIM(HR2jXy_wPg4@53:01)

Keep the channel replaceable
- Expose the live channel as a GraphQL subscription implemented over SSE so the transport stays swappable (SSE, WebSocket or polling). single-source. CLAIM(leo1FZ6vu1I@38:41)
- Let a correctly configured GraphQL layer keep client and server state in sync so subscription updates flow into client state automatically. single-source. CLAIM(tsGarhpWOws@43:03)

## Sub-skills
| sub-skill | file | load when |
|---|---|---|
| transport-choice | references/transport-choice.md | every S07 job; the written pros/cons table, per-option trade-offs, and the full decision table live here |
| collaboration-and-conflicts | references/collaboration-and-conflicts.md | two or more writers touch the same data, or the design must state its conflict stance |
| offline-first | references/offline-first.md | the product must work offline or on flaky networks, or a sync queue is being designed |

## Decision tables
Full table with per-cell trade-offs: references/transport-choice.md. Condensed verdict map:

| option | pick when | do not pick when | cite |
|---|---|---|---|
| short polling | updates are rare and simplicity wins | every tick matters or cellular data is scarce | CLAIM(5vyKhm2NTfw@22:44, LEaiGjffLEs@10:22) |
| long polling | you need slightly better freshness with zero new infrastructure | per-tick request overhead or latency is unacceptable | CLAIM(5vyKhm2NTfw@22:44) |
| SSE (plus plain HTTP sends) | client mostly reads, text payloads, HTTP/2 and easy failover matter | you need binary framing or heavy two-way traffic | CLAIM(5vyKhm2NTfw@24:26, LEaiGjffLEs@15:02, LEaiGjffLEs@20:38, leo1FZ6vu1I@35:35) |
| WebSocket | true duplex, lowest latency, binary both ways | the stream is receive-only or ops simplicity matters | CLAIM(leo1FZ6vu1I@34:26, HR2jXy_wPg4@48:00) |
| plain HTTP streaming | rarely, when HTTP/2 binary streaming is enough | the payload needs message framing | CLAIM(HR2jXy_wPg4@52:17) |
| WebTransport | browser and server support allow it, and framing plus speed matter | your support matrix forbids QUIC/UDP | CLAIM(HR2jXy_wPg4@53:01) |

Sync-model decision points:

| question | answer he gives | cite |
|---|---|---|
| how does the client catch up after a gap | send a last-sync timestamp marker and pull only newer data | CLAIM(LEaiGjffLEs@26:30) |
| whole document or diffs | send computed deltas, not whole pages | CLAIM(tsGarhpWOws@41:31) |
| who resolves concurrent edits | explicitly out of scope in a front-end design; name it and move on | CLAIM(tsGarhpWOws@04:20) |
| can two windows write the same store | no; one host window owns writes, extensions read and replicate | CLAIM(HR2jXy_wPg4@57:01, HR2jXy_wPg4@60:03) |

## Anti-patterns
- Repeated get-calls just to catch new stories: pure traffic overhead. CLAIM(5vyKhm2NTfw@21:41)
- Sending a full request with headers and tokens for every tiny update. CLAIM(5vyKhm2NTfw@22:44, LEaiGjffLEs@10:22)
- Holding a persistent socket per tab and calling it cheap. CLAIM(LEaiGjffLEs@11:35)
- Choosing WebSockets and then reimplementing HTTP/2 features (multiplexing, asset splitting) by hand. CLAIM(LEaiGjffLEs@12:21)
- Ignoring proxies and connection timeouts, which force constant reconnects. CLAIM(LEaiGjffLEs@14:01)
- Holding WebSockets open for a receive-only data stream. CLAIM(leo1FZ6vu1I@34:26)
- Picking plain HTTP streaming for data that needs frame boundaries. CLAIM(HR2jXy_wPg4@52:17)
- Letting multiple windows write shared state; make extensions read-only replicas. CLAIM(HR2jXy_wPg4@60:03)
- Designing CRDTs inside a front-end system design interview instead of stating the stance. CLAIM(tsGarhpWOws@04:20)

## Worked cases
- 5vyKhm2NTfw: [Front End System Design] - Facebook News Feed. Steal the transport comparison for a feed, and the ~60ms tolerance argument that picks SSE.
- LEaiGjffLEs: [Front-End System Design] - Chat application. Steal the requirement-first protocol filter and the hybrid SSE-receive plus HTTP-send decision.
- leo1FZ6vu1I: [Front-End System Design] - Google Calendar. Steal the subscription interface that keeps the transport swappable.
- tsGarhpWOws: Frontend System Design - Notion-like editor. Steal the offline-first SSE call and the subscription-as-state-sync pattern.
- HR2jXy_wPg4: Frontend System Design - Financial Dashboard / TradingView. Steal the four-transport comparison (WebSocket, SSE, HTTP streaming, WebTransport) and the framing argument.

## Dated / contestable
- The 2020 claim that WebSockets cannot ride HTTP/2 is contested. Distiller note (not the author): RFC 8441 extended CONNECT carries WebSockets over HTTP/2, though browser and server support is still uneven; his load-balancing and proxy objections remain directionally valid. CLAIM(5vyKhm2NTfw@23:43)
- SSE payloads described as binary. Distiller note (not the author): the EventSource stream is text; the efficiency point stands. CLAIM(5vyKhm2NTfw@24:35)
- WebTransport browser support quoted at roughly 60 percent is a mid-2025 snapshot. Distiller note (not the author): re-check current coverage before designing on it. CLAIM(HR2jXy_wPg4@52:55)
- The prediction that WebSockets will soon be replaced is his opinion, not settled consensus; WebSocket use in trading UIs remains widespread. CLAIM(HR2jXy_wPg4@49:22)
- "Client libraries rarely implement SSE for GraphQL" is directionally true but now a buy-versus-build question: dedicated GraphQL-over-SSE libraries exist. CLAIM(leo1FZ6vu1I@41:23)
- The 40-60ms "instant" latency budget is his chosen number for chat, not a measured standard. CLAIM(LEaiGjffLEs@02:23)
- AppCache-era offline wording elsewhere in this corpus is obsolete; see references/offline-first.md.

## Hand-off
- Next stage in the family: fesd-performance, which takes the chosen channel and prices its rendering and bundle cost.
- Upstream: fesd-api-network for the endpoint surface the channel sits on, fesd-state-data for the store the updates land in.
- Estate skills: app-web-frontend for build slices; app-data-layer when the sync loop touches server persistence; the api design harness hA-09 when the subscription surface needs its own contract; fixing-accessibility if the live channel must announce changes to screen readers (see fesd-a11y-i18n).
