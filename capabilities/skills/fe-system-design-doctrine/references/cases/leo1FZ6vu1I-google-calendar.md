# Case: [Front-End System Design] - Google Calendar

Source: https://www.youtube.com/watch?v=leo1FZ6vu1I (video id leo1FZ6vu1I). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video leo1FZ6vu1I against the local transcript.

- published 2022-08-01 / duration 3563s (~59 min) / problem type: product-design
- channel: Front-End Engineer (Evgenii Ray)

## Author's framework as used
1. Problem overview against the live product: create/schedule events, invite people, year/month/day drill-down, CLAIM(leo1FZ6vu1I@00:32)
2. General requirements: multiple views, multi-user with live updates, event details, conflict spotting, import/export, PWA/offline, device reminders, CLAIM(leo1FZ6vu1I@01:50)
3. Functional requirements: mobile-first, offline, battery budget, bridging to native capabilities, fast view switching, accessibility, CLAIM(leo1FZ6vu1I@03:38)
4. Action plan in order: layout, component architecture, data model and API, data transferring, rendering optimization, accessibility, notifications, app optimizations, CLAIM(leo1FZ6vu1I@05:08)
5. Layout overview of the three views (year, month, day), CLAIM(leo1FZ6vu1I@06:43)
6. Component architecture (controls vs view, per-view cells, shared event view), CLAIM(leo1FZ6vu1I@08:12)
7. Data model with conflict detection as the hardest requirement, solved with an interval tree, CLAIM(leo1FZ6vu1I@09:45)
8. Data transferring: compare protocols, then design the API surface on the winner, CLAIM(leo1FZ6vu1I@32:27)
9. Data flow: event-driven client store wiring server events to components, CLAIM(leo1FZ6vu1I@42:37)
10. Rendering optimization focused on smooth period switching (prerendering), CLAIM(leo1FZ6vu1I@45:18)
11. Bridging reminders to mobile (web push vs deep links), CLAIM(leo1FZ6vu1I@49:13)
12. Standard web app optimizations and the accessibility pass to close, CLAIM(leo1FZ6vu1I@51:42)

## Worked design
Requirements
- Year, month and day views (week view skipped for simplicity), CLAIM(leo1FZ6vu1I@06:43)
- Multi-user: others can create events for you, you can invite people, and updates arrive live (online calendar, unlike the Sheets design), CLAIM(leo1FZ6vu1I@02:11)
- Conflicting/overlapping events must be visually detectable, CLAIM(leo1FZ6vu1I@02:31)
- Export/import of events; PWA-style offline use; reminders pushed to any device, CLAIM(leo1FZ6vu1I@02:48)
- Mobile-first, battery-conscious, efficient data fetching, native bridging (push, alarms), fast view transitions, accessible, CLAIM(leo1FZ6vu1I@03:38)

Components
- App root splits into calendar controls (create, search, theme, language) and calendar view, CLAIM(leo1FZ6vu1I@08:12)
- Calendar view has three implementations (year, month, day); year uses month cells, month uses day cells, day uses event cells, CLAIM(leo1FZ6vu1I@08:52)
- All cells delegate display to one generic event view component; a global client storage is the single source of truth, CLAIM(leo1FZ6vu1I@09:21)

Data model
- Calendar store: flattened events map (id -> event) plus client state (selected view, language, time zone), CLAIM(leo1FZ6vu1I@13:10) / CLAIM(leo1FZ6vu1I@13:33)
- Event entity: id, participants (email + names), start/end timestamps, title, rich-text description, optional conflicting-events list of ids, CLAIM(leo1FZ6vu1I@15:05)
- Conflict index: interval tree of events built by start date, each node augmented with the max end date in its subtree, CLAIM(leo1FZ6vu1I@20:10) / CLAIM(leo1FZ6vu1I@22:38)
- Search prunes a branch when the target date exceeds the subtree max, and only then tests the node's own start/end range, CLAIM(leo1FZ6vu1I@24:52) / CLAIM(leo1FZ6vu1I@25:37)
- Complexity: year rendering is 365 x log n instead of 365 x n; insert/delete are log n, CLAIM(leo1FZ6vu1I@30:15) / CLAIM(leo1FZ6vu1I@30:26)
- Conflict lists get populated during render from tree query results, CLAIM(leo1FZ6vu1I@29:41)

API
- subscribeEvent(api key, user id, timestamp, period): returns a full initial chunk then small live updates, CLAIM(leo1FZ6vu1I@36:54)
- getEventInfo: fetches full details on demand, CLAIM(leo1FZ6vu1I@37:34)
- createEvent / updateEvent mutations; GraphQL chosen over REST for field selection and a single endpoint, CLAIM(leo1FZ6vu1I@38:03)

Realtime
- SSE as transport, wrapped as GraphQL subscription; alternative transports (WebSocket, long polling) rejected or kept as fallbacks at the subscription layer, CLAIM(leo1FZ6vu1I@38:41)
- Client flow: store subscriptions, events through an event bus to a handler, async action updates the store, root passes data down, CLAIM(leo1FZ6vu1I@43:55)

Performance
- No virtualization needed; prerender prev/next periods and slide with transforms, CLAIM(leo1FZ6vu1I@46:53)
- Prerender window capped (e.g. 4 screens per side + 1 visible), CLAIM(leo1FZ6vu1I@48:46)
- Bundle splitting over HTTP/2, brotli, ES5+polyfills vs ES6 bundles, CLAIM(leo1FZ6vu1I@52:56)
- App cache plus web workers for offline operation, CLAIM(leo1FZ6vu1I@55:40)

Accessibility
- No pixel sizing; hotkeys (period nav, search, help); color schemes for color blindness, CLAIM(leo1FZ6vu1I@56:22)
- role=grid on the calendar surface; HTML5 semantics first, CLAIM(leo1FZ6vu1I@56:55)

## Trade-offs he names
- Long polling vs WebSocket vs SSE -> pick SSE: polling wastes traffic and suffers timeouts (harmless here since a calendar is not real-time critical), WebSockets bring duplex costs nobody needs, SSE rides HTTP/2 and saves mobile battery. Claims: CLAIM(leo1FZ6vu1I@33:53), CLAIM(leo1FZ6vu1I@34:26), CLAIM(leo1FZ6vu1I@35:35).
- GraphQL vs REST -> pick GraphQL for field selection and one endpoint, accept losing native HTTP caching and possibly implementing SSE support yourself. Claims: CLAIM(leo1FZ6vu1I@39:34), CLAIM(leo1FZ6vu1I@40:35), CLAIM(leo1FZ6vu1I@42:00).
- Naive array scan vs date-keyed map vs interval tree -> scan is 365 x n, the map duplicates a year-long event across 365 entries, the interval tree gives log n access with no duplication. Claims: CLAIM(leo1FZ6vu1I@16:25), CLAIM(leo1FZ6vu1I@17:25), CLAIM(leo1FZ6vu1I@18:07).
- Soft text update vs prerendering for view switching -> soft update is easy but re-renders and refetches on rapid switching; prerendering costs more memory but makes transitions trivial and smooth. Claims: CLAIM(leo1FZ6vu1I@45:49), CLAIM(leo1FZ6vu1I@46:30), CLAIM(leo1FZ6vu1I@47:05).
- Web push vs deep links for native reminders -> push needs consent and a push server; deep links depend on the target app implementing link handling. Claims: CLAIM(leo1FZ6vu1I@49:48), CLAIM(leo1FZ6vu1I@50:17).

## Anti-patterns he warns about
- Rendering a day by scanning the whole event array (linear per day, quadratic across a year), CLAIM(leo1FZ6vu1I@16:25)
- Indexing events per date in a map, which explodes into duplication for long-spanning events, CLAIM(leo1FZ6vu1I@17:25)
- Storing full event payloads inside the conflict index instead of ids, coupling edits to the search structure, CLAIM(leo1FZ6vu1I@31:44)
- Rebuilding derived structures on every mutation instead of touching one slice, CLAIM(leo1FZ6vu1I@10:29)
- Holding WebSocket connections for a receive-only data stream, CLAIM(leo1FZ6vu1I@34:26)
- Re-rendering whole views on every year/month switch, CLAIM(leo1FZ6vu1I@46:30)
- Removing and re-inserting DOM nodes where a soft text update would do, CLAIM(leo1FZ6vu1I@53:51)
- Pixel-based UI sizing that breaks under custom browser settings, CLAIM(leo1FZ6vu1I@56:09)

## Dated / contestable
- The offline story names the browser application-cache mechanism plus web workers (CLAIM(leo1FZ6vu1I@55:40)): that cache API is deprecated and removed from browsers, and offline resource caching is the service worker's job, not the web worker's. The intent (PWA offline) is current; the named mechanism is not.
- The dual ES5-with-polyfills / ES6 bundle strategy (CLAIM(leo1FZ6vu1I@52:56)) has largely been replaced by differential module builds and browserslist-driven transpilation; the goal (small modern payload) is unchanged.
- His point that GraphQL client libraries rarely implement SSE (CLAIM(leo1FZ6vu1I@41:23)) is still directionally true, but dedicated GraphQL-over-SSE/WS libraries now exist, so today this is a buy-vs-build decision.
- The dismissal of latency and connection timeouts as non-issues for a calendar (CLAIM(leo1FZ6vu1I@33:07)) is reasonable for personal use and contestable for shared scheduling, where stale availability data directly costs double bookings.
- The stated multi-user requirement is never followed by a conflict-resolution story (last-write-wins, OT/CRDT, invitations state machine); that is a gap rather than dated advice.
