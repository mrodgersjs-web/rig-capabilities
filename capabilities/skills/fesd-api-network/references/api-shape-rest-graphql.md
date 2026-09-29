# API shape: REST vs GraphQL

Purpose: name the calls, fix their parameter and return shapes, choose REST or GraphQL against the real field-selection need, and keep the client's request discipline honest.

When to load: when naming endpoints or operations, choosing an API style, deciding what a list payload carries, or writing the fetch layer of a widget.

## Step checklist

1. Write the call list first: named operations with explicit parameters and return shapes, before any entity or component work.
2. Keep the surface small: get/list, update, subscribe is the shape most corpus cases settle on.
3. Decide the style against field selection and caching, not fashion; price the costs of the chosen style out loud.
4. Mirror the client state model in the server types where the style allows it, so types are reusable.
5. Send deltas on update, not whole records.
6. Add payload control flags (exclusion flags, optional includes) so the client decides response weight.
7. Fetch short shapes for lists and full detail lazily on open.
8. Set client request discipline: debounce, cancel superseded in-flight requests, never one request per keystroke.
9. Unify heterogeneous or legacy sources behind one interface before the UI sees them.

## Laws

- Design the API as named calls with explicit parameters before writing entities. Single-source.
  (CLAIM(LEaiGjffLEs@21:31))
- Keep the API surface to about three operations: one read (or subscribe-to-events with an initial
  chunk plus incremental updates), one lazy detail read, and create/update mutations. Consensus.
  (CLAIM(leo1FZ6vu1I@36:54, tsGarhpWOws@40:31))
- Prefer GraphQL over REST when clients need arbitrary field combinations, because REST forces
  query-param workarounds and is hard to change after release. Consensus.
  (CLAIM(5vyKhm2NTfw@17:01, leo1FZ6vu1I@39:34, tsGarhpWOws@39:02))
- Note that GraphQL over POST carries its own cache management instead of inheriting HTTP cache
  semantics, and that a client library is required. Consensus.
  (CLAIM(5vyKhm2NTfw@17:42, tsGarhpWOws@39:09))
- Design GraphQL entities to mirror the client state model so server and client types can be reused.
  Single-source. (CLAIM(tsGarhpWOws@39:45))
- Send content diffs to the server instead of whole pages, using a delta library to compute them.
  Single-source. (CLAIM(tsGarhpWOws@41:31))
- Offer field-exclusion flags on reads (for example skip comments) so the client controls payload
  weight. Single-source. (CLAIM(5vyKhm2NTfw@14:39))
- Keep a child endpoint minimal: identity, parent id, page size. Single-source.
  (CLAIM(3MADCVqL534@30:21))
- Shape reads around what the screen shows: a dashboard read returning a tag-keyed map and a search
  read taking query, tags and page size returning card shapes. Single-source.
  (CLAIM(Tu-hZ6lqNtY@21:27))
- Fetch full record details (cast, tags, related items) lazily when the user opens the full card,
  not with the list read. Consensus. (CLAIM(Tu-hZ6lqNtY@28:51, leo1FZ6vu1I@37:34))
- Hide heterogeneous legacy endpoints behind one getData(entity, start, end, timeFrame)
  subscription-style interface. Single-source. (CLAIM(HR2jXy_wPg4@46:06))
- Prefer binary payloads with a serialization protocol such as protobuf when streaming large
  volumes; the compression win outweighs (de)serialization cost. Single-source.
  (CLAIM(HR2jXy_wPg4@54:23))
- Make the widget network-efficient: never fire a request per keystroke. Single-source.
  (CLAIM(9aOXGE7wAZo@05:30))
- Debounce input so a typing burst produces one request, not one per letter. Consensus.
  (CLAIM(9aOXGE7wAZo@22:01, 9mjsRrJYOWE@43:24))
- Cancel superseded in-flight requests (AbortController) so only the newest query's response ever
  reaches the UI. Single-source. (CLAIM(9mjsRrJYOWE@39:33))
- Push large-dataset filtering to the server rather than shipping and filtering it client-side.
  Single-source. (CLAIM(9aOXGE7wAZo@29:31))

## Decision table

| Decision | Pick | When to deviate | Cites |
|---|---|---|---|
| Style | REST | GraphQL when clients need arbitrary field combinations from one endpoint | CLAIM(5vyKhm2NTfw@17:01, tsGarhpWOws@39:02) |
| Caching under GraphQL | client library cache | assume HTTP cache works only for plain REST GETs | CLAIM(5vyKhm2NTfw@17:42) |
| Update payload | delta or diff | whole record only when it is small and mostly changed | CLAIM(tsGarhpWOws@41:31) |
| List payload | short shape + lazy detail | full record when the list renders everything anyway | CLAIM(Tu-hZ6lqNtY@28:51, leo1FZ6vu1I@37:34) |
| Heavy sections | exclusion flags | fixed shape when every client needs everything | CLAIM(5vyKhm2NTfw@14:39) |
| Legacy sources | one unified interface | per-source calls when there is genuinely one source | CLAIM(HR2jXy_wPg4@46:06) |
| Wire format for volume | binary + serialization | JSON for small, human-debugged traffic | CLAIM(HR2jXy_wPg4@54:23) |
| Typing to request | debounce + cancel | none; a request per keystroke is not an option | CLAIM(9aOXGE7wAZo@05:30, 9mjsRrJYOWE@39:33) |
| Filtering location | server | client only when the data set is already local and small | CLAIM(9aOXGE7wAZo@29:31) |

## Worked cases

- LEaiGjffLEs, [Front-End System Design] - Chat application: the call list before the entity list (CLAIM(LEaiGjffLEs@21:31)).
- tsGarhpWOws, Frontend System Design - Notion-like editor: three operations, delta updates, GraphQL cost accounting (CLAIM(tsGarhpWOws@40:31, tsGarhpWOws@39:09)).
- 5vyKhm2NTfw, [Front End System Design] - Facebook News Feed: read flags and the style criterion (CLAIM(5vyKhm2NTfw@14:39, 5vyKhm2NTfw@17:01)).
- Tu-hZ6lqNtY, [Front-End Product Design] - Netflix: screen-shaped reads and lazy detail (CLAIM(Tu-hZ6lqNtY@21:27, Tu-hZ6lqNtY@28:51)).
- HR2jXy_wPg4, Frontend System Design - Financial Dashboard / TradingView: one interface over legacy feeds, binary payloads (CLAIM(HR2jXy_wPg4@46:06, HR2jXy_wPg4@54:23)).
- 9aOXGE7wAZo, [Front-End System Design] - Typeahead Widget: debounce and server-side filtering (CLAIM(9aOXGE7wAZo@22:01, 9aOXGE7wAZo@29:31)).

## Dated / contestable

- Passing an api key as an endpoint parameter is interview shorthand, not production auth design.
  Distiller note (not the author): use real auth (headers, tokens, session) in anything that ships.
  (CLAIM(5vyKhm2NTfw@14:21))
- The GraphQL-vs-REST framing predates typed REST stacks (tRPC, OpenAPI codegen) that answer the
  "shapes are hard to change" complaint without GraphQL. Distiller note (not the author): put those
  on the comparison table today. (CLAIM(tsGarhpWOws@38:51))
- The 6-8x compression figure for binary serialization is an unsourced estimate. Distiller note (not
  the author): actual ratios depend on payload shape and encoding; measure your own payloads.
  (CLAIM(HR2jXy_wPg4@54:23))
