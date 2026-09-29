# Case: Frontend System Design - Notion-like editor

Source: https://www.youtube.com/watch?v=tsGarhpWOws (video id tsGarhpWOws). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video tsGarhpWOws against the local transcript.

- published 2023-12-18, duration ~56 min (3372s), problem type: product-design (full-app design: extendable markdown editor + Notion-style databases)

## Author's framework as used
1. Ground the problem first: explain what the real product is (workspace of pages with a custom markdown syntax, databases as page groups with view implementations) and tell viewers to actually try the product before designing it. CLAIM(tsGarhpWOws@01:07)
2. Open a written plan before drawing anything. His plan for this episode: general requirements, additional requirements, mockup, high-level component hierarchy + data flow, markdown parser design, database design, state design, API design, optimization, accessibility. CLAIM(tsGarhpWOws@02:41)
3. Collect general requirements (live element transformation while typing, extendable component library, nested page hierarchy, accessibility, performance). CLAIM(tsGarhpWOws@05:02)
4. Collect advanced requirements (databases/views, offline-first with efficient network sync, cross-platform, multi-viewport). CLAIM(tsGarhpWOws@06:27)
5. Show a mockup (he pastes a prepared one and says a real interview usually does not need a drawn mockup), then move to the high-level component schema. CLAIM(tsGarhpWOws@07:54)
6. Build the architecture top-down from the application route: app route (root page id) -> app menu + application router -> page route -> page content -> lexer/parser/render pipeline. CLAIM(tsGarhpWOws@08:47)
7. Draw the data flow loop: raw content -> lexer -> parser -> render -> DOM; edits tracked by MutationObserver -> dispatcher -> action handler -> new global state -> re-render. CLAIM(tsGarhpWOws@10:48)
8. Classify components into three families (visual, structural, database-connectable) so the library shares one interface. CLAIM(tsGarhpWOws@16:57)
9. Prototype the parser contracts in TypeScript: lexer interface (rules + content -> component tokens), rule interface (isValid + getToken), token interfaces (generic props, container children, database data). CLAIM(tsGarhpWOws@19:16)
10. Design the Notion-style database as a page holding pages, with per-view plugin metadata (timeline start/end, calendar timestamp, table columns). CLAIM(tsGarhpWOws@29:15)
11. Design state and entities: minimal app state (root page id + normalized page map) plus a page hash for render caching. CLAIM(tsGarhpWOws@34:42)
12. Design the API by comparing protocol options (REST vs GraphQL, WebSockets vs SSE), then settle on get page / update page (delta) / subscribe for changes. CLAIM(tsGarhpWOws@35:49)
13. Cover optimization in one pass (network + JS + rendering), then accessibility in one pass (rem units, hotkeys, color schemes, semantic tags, alt text). CLAIM(tsGarhpWOws@43:52)

## Worked design
Requirements
- Core: live transformation of typed markdown into components as the user types. CLAIM(tsGarhpWOws@05:02)
- Core: extendable component library with matching extendable custom syntax. CLAIM(tsGarhpWOws@05:22)
- Core: nested page hierarchy (a page inside a page) as the workspace shape. CLAIM(tsGarhpWOws@05:42)
- Advanced: databases grouping pages into views (table, calendar, timeline) with per-view metadata. CLAIM(tsGarhpWOws@06:27)
- Advanced: offline-first operation plus efficient network communication, sending diffs instead of whole pages. CLAIM(tsGarhpWOws@06:56)
- Default: cross-platform via web, and multi-viewport support at the component level. CLAIM(tsGarhpWOws@07:28)

Components
- Three families: visual (pure render), structural (accept children), database-connectable (accept pages and render a view). CLAIM(tsGarhpWOws@16:57)
- Component token typed with a generic props parameter; container variant adds a children array of tokens. CLAIM(tsGarhpWOws@22:04)
- Lexer interface: process(rules, content) returning component tokens; rule interface: isValid(line) + getToken(line). CLAIM(tsGarhpWOws@20:48)
- Parser interface: process(token) -> HTML element, called recursively for children, with a render-set map from token type to render function. CLAIM(tsGarhpWOws@27:18)
- Page entity: id, title, optional content, optional icon, children pages, hash, plugins. CLAIM(tsGarhpWOws@32:30)

Data model
- Plugin data per view: timeline (start, end timestamps), calendar (one timestamp), table (column list). CLAIM(tsGarhpWOws@33:35)
- App state: root page id + normalized map of pages keyed by id for O(1) access and easy live inserts. CLAIM(tsGarhpWOws@34:56)
- Page hash drives whether the cached static area is reused. CLAIM(tsGarhpWOws@32:30)
- Database modeled as a page containing pages (one-to-many), with view components inheriting the database-component interface. CLAIM(tsGarhpWOws@30:05)

API
- Options compared by protocol: WebSockets (HTTP/1.1) vs HTTP/2 options; WebSockets rejected as overhead for this product. CLAIM(tsGarhpWOws@36:37)
- REST praised for simplicity and HTTP/2 features (caching, multiplexed connections) but criticized for rigid response shapes. CLAIM(tsGarhpWOws@37:32)
- GraphQL chosen for arbitrary field sets and long-term maintainability, with the POST-only caching trade-off named. CLAIM(tsGarhpWOws@40:02)
- Three methods: getPage(id, token), updatePage(id, delta, token), subscribe for changes via SSE-backed GraphQL subscriptions. CLAIM(tsGarhpWOws@41:01)

Realtime
- Live updates via server-sent events over HTTP/2; long polling noted as an alternative behind the subscription interface. CLAIM(tsGarhpWOws@42:18)
- GraphQL subscriptions used as the interface so the implementation underneath can vary. CLAIM(tsGarhpWOws@42:30)
- Collaborative editing and conflict resolution explicitly parked as out of scope. CLAIM(tsGarhpWOws@04:20)

Perf
- HTTP/2 + service-worker asset caching for offline mode and fast first load. CLAIM(tsGarhpWOws@45:00)
- ES6+ bundle, minified, aggressively split, component code lazy-loaded. CLAIM(tsGarhpWOws@46:36)
- Brotli/Zstd compression, WebP images, image optimization service for oversized uploads. CLAIM(tsGarhpWOws@47:55)
- Rendering: cache parsed static area, scope mutations to the selected area, flat CSS names, GPU animations, tables may virtualize. CLAIM(tsGarhpWOws@50:50)

A11y
- rem units for zoom-respecting sizing. CLAIM(tsGarhpWOws@53:03)
- Hotkey set planned but deferred for a low-code product. CLAIM(tsGarhpWOws@53:05)
- Color schemes for visual disabilities. CLAIM(tsGarhpWOws@53:22)
- Semantic HTML and image alt text. CLAIM(tsGarhpWOws@53:38)

## Trade-offs he names
- WebSockets vs SSE for this app -> pick SSE: WebSockets add implementation and scaling complexity while the product only needs server-pushed updates. CLAIM(tsGarhpWOws@36:37)
- REST vs GraphQL -> pick GraphQL when clients need varying field sets and long-term shape changes; REST is fine when simplicity and default HTTP caching matter more. CLAIM(tsGarhpWOws@38:51)
- Whole-page saves vs delta saves -> pick deltas to minimize traffic on big pages. CLAIM(tsGarhpWOws@41:31)
- Global state vs normalized map -> pick the normalized ID map for access speed and live-update ergonomics. CLAIM(tsGarhpWOws@34:56)
- Re-parse whole page vs cached static area -> pick the split so only the edited region costs re-render. CLAIM(tsGarhpWOws@12:43)
- Virtualization everywhere vs only heavy components -> only tables and similar; content rendering is not virtualized. CLAIM(tsGarhpWOws@51:11)

## Anti-patterns he warns about
- Do not design conflict resolution in a frontend system design interview; it is its own research field. CLAIM(tsGarhpWOws@04:20)
- Do not rely on standard input events for contenteditable nodes; you must observe DOM mutations instead. CLAIM(tsGarhpWOws@12:21)
- Do not build UI from divs when semantic tags exist; that breaks default accessibility. CLAIM(tsGarhpWOws@53:53)
- Do not ship ES5 polyfills to a modern-browser-only user base; it bloats the bundle. CLAIM(tsGarhpWOws@46:36)
- Do not run hundreds of rules per line indefinitely without checking cost; fine now, a concern at very large rule sets. CLAIM(tsGarhpWOws@25:55)
- He corrects himself mid-diagram on the dispatch path (content goes to the dispatcher first, then the action handler) rather than skipping the step. CLAIM(tsGarhpWOws@15:00)

## Dated / contestable
- 2023 advice to skip ES5 polyfills assumed a modern-Chromium-only audience; the modern framing is differential loading / browserslists, and baseline-browser-support tooling has moved on. CLAIM(tsGarhpWOws@46:36)
- His Brotli/Zstd wording treats CDN compression as mostly settled; WebP is now often superseded by AVIF for still images. CLAIM(tsGarhpWOws@47:55)
- GraphQL-vs-REST framing predates the wide adoption of typed REST stacks (tRPC, REST + OpenAPI codegen) that address his "hard to change response shapes" complaint without GraphQL. CLAIM(tsGarhpWOws@38:51)
- The suggestion that AI vision models can generate alt text is newer than the surrounding a11y checklist and is presented as an aside rather than a designed pipeline. CLAIM(tsGarhpWOws@54:03)
- SSE-over-WebSockets for an offline-first editor still holds, but collaborative editing since 2023 is more commonly designed around Yjs/CRDT libraries than left as an unexamined park. CLAIM(tsGarhpWOws@04:20)
