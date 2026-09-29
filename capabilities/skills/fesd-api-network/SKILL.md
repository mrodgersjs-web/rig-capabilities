---
name: fesd-api-network
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Owns stages S06 and S10 of front-end system design: the client-facing API surface (named calls,
  parameter shapes, REST vs GraphQL, deltas, lazy detail reads), paging and request discipline,
  the HTTP protocol floor (versions, headers, connection behavior, caching layers) and the thin
  frontend security slice (DOM encapsulation, untrusted-content filtering). Produces the API and
  network contract that sits on top of the S05 store. Use when designing endpoints for a
  front-end system design answer or a real app, when asked "REST or GraphQL", "how should this
  page", "why is this fetch slow", "what does the wire look like", or before trusting rendered
  server data. 36 laws (34 S06 plus 2 S10) from 10 Front-End Engineer videos. JEV-FIRST MANDATE,
  findable at task start: typed judgments in this stage go to rig-s1gate (Jev) BEFORE any
  frontier LLM call; DEFERRED is the only answer when the classifier is down. Child of
  fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, api, rest, graphql, pagination, http, security]
outcome: "code-engineering: a cited API and network contract (calls, paging, protocol, trust boundaries)"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-api-network/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S06, S10"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# FE system design S06/S10: API, network and security

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-api-designer loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate

Typed judgments this stage forces, and which go to Jev first:

1. Is this API surface complete enough to build the UI against (every screen has its call) (kind: api.backend).
2. Does the chosen style (REST or GraphQL) fit the actual field-selection and caching needs (kind: api.backend).
3. Is the paging scheme deterministic under concurrent writes (kind: api.backend).
4. Is any rendered server data treated as untrusted until filtered or encapsulated (kind: api.backend).

Command shape: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`.
Nearest existing rubric: api.backend, advisory until calibrated. A pass needs every required
signal above 0.9. Classifier down, erroring, or rubric missing = DEFERRED, never a guessed
verdict. An advisory PASS is not permission to ship or publish; here it only means the API design
may be treated as ready to implement.

## When to use

- After the S05 store exists and a client needs to read or write through a network boundary.
- When a design answer says "we call the API" without naming calls and parameters.
- When paging, cursor, or infinite scroll behavior needs a concrete contract.
- When a rendering decision depends on what the wire format or protocol actually does.
- When data from a server the client does not control reaches the DOM.

## Inputs and output contract

Input: the S05 entity model and store shape, plus S02 requirements (freshness, data volume, trust
of data sources).

Output artifact: an API and network document with these headings in order:

1. Calls: the named operations with explicit parameter lists and return shapes (see references/api-shape-rest-graphql.md).
2. Style decision: REST vs GraphQL with the reason and the costs priced in (see references/api-shape-rest-graphql.md).
3. Paging contract: cursor or offset scheme, page size, and what makes a page deterministic (see references/pagination.md).
4. Protocol notes: which HTTP version serves the app, header and caching expectations, connection behavior (see references/http-protocol.md).
5. Trust boundaries: what is encapsulated, what is filtered before rendering (see references/frontend-security.md).

## Procedure

1. Write the API as named calls with explicit parameters before writing anything else: the call list
   is the contract the UI is built against (CLAIM(LEaiGjffLEs@21:31, leo1FZ6vu1I@36:54,
   tsGarhpWOws@40:31)). Load references/api-shape-rest-graphql.md.
2. Choose the style against the field-selection need: GraphQL when clients pick arbitrary fields
   from one endpoint, REST when free HTTP caching is worth more (CLAIM(5vyKhm2NTfw@17:01,
   tsGarhpWOws@39:02)), and price the style's costs before adopting it
   (CLAIM(tsGarhpWOws@39:09)).
3. Parameterize every read: identity, a cursor or timestamp, a page size, and an id range so paging
   is deterministic (CLAIM(5vyKhm2NTfw@14:48, 3MADCVqL534@28:35)). Load references/pagination.md.
4. Add payload control flags (skip comments, field exclusion) so the client decides response weight
   (CLAIM(5vyKhm2NTfw@14:39, 3MADCVqL534@27:34)), and push large-dataset filtering to the server
   (CLAIM(9aOXGE7wAZo@29:31)).
5. Fix request discipline on the client: no request per keystroke, debounce input, and cancel
   superseded in-flight requests (CLAIM(9aOXGE7wAZo@05:30, 9mjsRrJYOWE@39:33)).
6. Fetch full detail lazily when the detail view opens; lists carry short shapes only
   (CLAIM(Tu-hZ6lqNtY@28:51, leo1FZ6vu1I@37:34)).
7. Check which protocol version the stack serves before applying any 1.1-era performance advice
   (CLAIM(gxF9fLo5XQw@16:08)). Load references/http-protocol.md.
8. Draw the trust boundary: encapsulate component DOM and filter untrusted server content before it
   renders (CLAIM(9mjsRrJYOWE@52:57, 9mjsRrJYOWE@55:05)). Load references/frontend-security.md.

## Core laws

API shape

- Write the API as named calls with explicit parameters before designing entities, and keep the
  surface small: the corpus cases settle on about three operations. Consensus.
  (CLAIM(LEaiGjffLEs@21:31, leo1FZ6vu1I@36:54, tsGarhpWOws@40:31))
- Prefer GraphQL when the data is deeply multi-level and the client needs field selection; prefer
  REST when you want HTTP caching for free. Consensus.
  (CLAIM(5vyKhm2NTfw@17:01, leo1FZ6vu1I@39:34, tsGarhpWOws@39:02))
- Price in GraphQL's costs before adopting it: POST-only traffic that forfeits HTTP caching, a
  required client library, an extra point of failure. Consensus.
  (CLAIM(5vyKhm2NTfw@17:42, tsGarhpWOws@39:09))
- Hide heterogeneous legacy endpoints behind one unified subscription-style interface.
  Single-source. (CLAIM(HR2jXy_wPg4@46:06))
- Prefer binary payloads with a serialization protocol such as protobuf when streaming large
  volumes; the compression win outweighs (de)serialization cost. Single-source.
  (CLAIM(HR2jXy_wPg4@54:23))

Reads and paging

- Parameterize reads with a cursor or timestamp, a page size, and a min-id range so paging is
  deterministic. Consensus. (CLAIM(5vyKhm2NTfw@14:48, 3MADCVqL534@28:35))
- Offer field-exclusion flags on reads so the client controls payload weight. Single-source.
  (CLAIM(5vyKhm2NTfw@14:39))
- Push large-dataset filtering to the server rather than shipping and filtering it client-side.
  Single-source. (CLAIM(9aOXGE7wAZo@29:31))
- Fetch full detail lazily when the detail view opens and keep short versions in list rendering.
  Consensus. (CLAIM(Tu-hZ6lqNtY@28:51, leo1FZ6vu1I@37:34))

Request discipline

- Never fire a request per keystroke: debounce input and cancel superseded in-flight requests so
  only the newest query's response reaches the UI. Consensus.
  (CLAIM(9aOXGE7wAZo@05:30, 9aOXGE7wAZo@22:01, 9mjsRrJYOWE@43:24, 9mjsRrJYOWE@39:33))

Protocol floor

- Diagnose HTTP/1.1 by its two structural limits (sequential resource loading, uncompressed
  repeating text headers) and check which protocol version a stack serves before applying its
  performance advice. Single-source.
  (CLAIM(gxF9fLo5XQw@13:23, gxF9fLo5XQw@14:47, gxF9fLo5XQw@16:08))

Security (thin coverage: 2 laws, 1 video)

- Encapsulate the component DOM (web component / shadow DOM) so external scripts cannot rewrite it
  or steal data through it. Single-source. (CLAIM(9mjsRrJYOWE@52:57))
- Offer a content-filter function when results come from a server you do not trust, so unwanted
  markup or scripts are stripped without building a proxy. Single-source.
  (CLAIM(9mjsRrJYOWE@55:05))

## Sub-skills

| Sub-skill | File | Load when |
|---|---|---|
| API shape: REST vs GraphQL | references/api-shape-rest-graphql.md | naming calls and parameters, choosing the style, pricing its costs, deciding lazy vs eager reads and payload flags |
| Pagination | references/pagination.md | designing paging for feeds, lists or tables, or deciding cursor vs offset style |
| HTTP protocol | references/http-protocol.md | reasoning about versions, headers, connections, caching layers or wire size; before quoting protocol-era performance advice |
| Frontend security | references/frontend-security.md | when untrusted server data reaches the DOM, or when the component must resist surrounding scripts |

## Decision tables

| Decision | Option A | Option B | Pick when | Cites |
|---|---|---|---|---|
| API style | REST | GraphQL | REST when HTTP caching matters and shapes are stable; GraphQL when clients need arbitrary field combinations | CLAIM(5vyKhm2NTfw@17:01, tsGarhpWOws@39:02) |
| GraphQL caching | assume HTTP cache works | client-library caching | client library; GraphQL over POST forfeits the HTTP cache | CLAIM(5vyKhm2NTfw@17:42, leo1FZ6vu1I@39:34) |
| Paging scheme | offset or page number | cursor / timestamp + min-id | cursor for feeds under concurrent writes; page number when the user needs an exact page of analyzed data | CLAIM(5vyKhm2NTfw@14:48, u6jhTo13_No@30:46) |
| Detail payload | full record on list read | short shape + lazy detail | lazy detail; lists carry short shapes | CLAIM(Tu-hZ6lqNtY@28:51, leo1FZ6vu1I@37:34) |
| Large datasets | ship and filter client-side | server-side filtering | server side once the data set is large | CLAIM(9aOXGE7wAZo@29:31) |
| Payload weight | fixed response shape | exclusion flags | flags let the client drop heavy sections | CLAIM(5vyKhm2NTfw@14:39) |
| Legacy endpoints | per-source calls | one unified interface | unified interface over heterogeneous or legacy sources | CLAIM(HR2jXy_wPg4@46:06) |
| Wire format | text (JSON) | binary + serialization | binary when streaming large volumes | CLAIM(HR2jXy_wPg4@54:23) |
| Input-to-request | fire per keystroke | debounce + cancel | debounce and cancel; only the newest response may render | CLAIM(9aOXGE7wAZo@22:01, 9mjsRrJYOWE@39:33) |

## Anti-patterns

- Naming "the API" without named calls and parameter lists (CLAIM(LEaiGjffLEs@21:31)).
- Adopting GraphQL for status and paying its costs without needing field selection
  (CLAIM(tsGarhpWOws@39:09)).
- Offsetting a feed while rows are inserted or deleted concurrently (the cursor is what makes the
  page deterministic) (CLAIM(5vyKhm2NTfw@14:48)).
- Sending whole records where a delta would do (CLAIM(tsGarhpWOws@41:31)).
- Applying 1.1-era workarounds (domain sharding, extra connections) to a stack that already serves a
  multiplexed protocol (CLAIM(gxF9fLo5XQw@16:08, gxF9fLo5XQw@16:36)).
- Rendering untrusted server markup directly into the component DOM
  (CLAIM(9mjsRrJYOWE@55:05)).

## Worked cases

- gxF9fLo5XQw, Deep dive into HTTP [Part 1]: the protocol floor under every frontend API. Steal: the
  fetch-path walkthrough that makes the limits self-evident (CLAIM(gxF9fLo5XQw@01:08)).
- 5vyKhm2NTfw, [Front End System Design] - Facebook News Feed: read parameterization and the
  REST-vs-GraphQL criterion (CLAIM(5vyKhm2NTfw@14:48, 5vyKhm2NTfw@17:01)).
- tsGarhpWOws, Frontend System Design - Notion-like editor: three operations, delta updates,
  GraphQL cost accounting (CLAIM(tsGarhpWOws@40:31, tsGarhpWOws@41:31)).
- leo1FZ6vu1I, [Front-End System Design] - Google Calendar: three calls (subscribe, lazy details,
  mutations) and protocol comparison against freshness needs (CLAIM(leo1FZ6vu1I@36:54, leo1FZ6vu1I@32:42)).
- 3MADCVqL534, [Front-End System Design] - Pinterest: cursor plus min-id paging and a minimal comment
  endpoint (CLAIM(3MADCVqL534@28:35, 3MADCVqL534@30:21)).
- Tu-hZ6lqNtY, [Front-End Product Design] - Netflix: get-dashboard and search shapes with lazy full
  detail (CLAIM(Tu-hZ6lqNtY@21:27, Tu-hZ6lqNtY@28:51)).
- HR2jXy_wPg4, Frontend System Design - Financial Dashboard / TradingView: one interface over legacy
  feeds, binary payloads, CDN placement (CLAIM(HR2jXy_wPg4@46:06, HR2jXy_wPg4@54:23)).
- 9mjsRrJYOWE, Typeahead component: request cancellation and the two security moves
  (CLAIM(9mjsRrJYOWE@39:33, 9mjsRrJYOWE@52:57)).
- 9aOXGE7wAZo, [Front-End System Design] - Typeahead Widget: debounce discipline and multi-level
  caching (CLAIM(9aOXGE7wAZo@22:01, 9aOXGE7wAZo@22:26)).
- LEaiGjffLEs, [Front-End System Design] - Chat application: named calls first (CLAIM(LEaiGjffLEs@21:31)).

## Dated / contestable

- The HTTP deep dive stops at 1.1 and points to HTTP/2 as the fix. Distiller note (not the author):
  HTTP/2 is now the common default and HTTP/3 (QUIC) carries a significant share of traffic, so the
  story continues past this video. (CLAIM(gxF9fLo5XQw@22:45))
- The per-domain connection limit and the domain-sharding workaround describe 1.1-era browsers.
  Distiller note (not the author): multiplexed protocols change that arithmetic entirely, and
  sharding is a legacy hack now. (CLAIM(gxF9fLo5XQw@16:39, gxF9fLo5XQw@16:36))
- The traffic statistics (about 100 KB to 5 MB per page, roughly 70 requests) are period data.
  Distiller note (not the author): re-measure before quoting them. (CLAIM(gxF9fLo5XQw@12:46))
- "WebSockets cannot use HTTP/2" is 2020-era framing. Distiller note (not the author): extended
  CONNECT carries WebSockets over HTTP/2 in later stacks, though browser and server support is
  uneven and the load-balancing costs he names remain real. (CLAIM(5vyKhm2NTfw@23:50))
- Passing an api key as a query parameter is interview shorthand. Distiller note (not the author):
  production auth does not travel as an endpoint parameter. (CLAIM(5vyKhm2NTfw@14:21))
- The GraphQL-vs-REST framing predates typed REST stacks (tRPC, OpenAPI codegen) that address the
  "response shapes are hard to change" complaint without GraphQL. Distiller note (not the author):
  include those in the style comparison today. (CLAIM(tsGarhpWOws@38:51))

## Hand-off

Next stage skill: fesd-realtime-sync (S07) to pick the delivery transport over this API, then the
performance stage (S08) for wire and rendering budgets, and the accessibility stage (S09) for what
these payloads must expose to assistive tech.

Adjacent estate skills: app-web-frontend for build slices, app-data-layer for the backend half of
these contracts, the api design harness hA-09 for contract review, emil-design-eng for UI polish,
fixing-accessibility, fixing-motion-performance, and the estate security skills
(when-securing-the-estate routing, sec-* triage skills) where frontend security needs depth beyond
this stage's two laws.
