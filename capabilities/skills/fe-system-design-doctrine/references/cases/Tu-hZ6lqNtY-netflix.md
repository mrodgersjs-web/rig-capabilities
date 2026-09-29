# Case: [Front-End Product Design] - Netflix

Source: https://www.youtube.com/watch?v=Tu-hZ6lqNtY (video id Tu-hZ6lqNtY). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video Tu-hZ6lqNtY against the local transcript.

- published 2020-12-10 / duration 2784s (~46 min) / problem type: product-design
- Speaker: Evgenii Ray (Front-End Engineer channel), episode 3. This one is explicitly "product design", which he contrasts with the system-design format of episodes 1-2.

## Author's framework as used
1. First, separate the two interview genres: system design completes one key feature; product design takes a holistic, shallow view of a whole application and defends which features matter most. CLAIM(Tu-hZ6lqNtY@00:55) CLAIM(Tu-hZ6lqNtY@01:31)
2. Explore the live product before designing anything (he searches by actor and title, hovers cards, opens details) to enumerate real features. CLAIM(Tu-hZ6lqNtY@02:05) CLAIM(Tu-hZ6lqNtY@03:22)
3. Lay out the plan: general requirements, functional requirements, application architecture and components, data entities, data API, data store, optimization, accessibility. CLAIM(Tu-hZ6lqNtY@03:59) CLAIM(Tu-hZ6lqNtY@04:37)
4. General requirements as features: search (actor, genre, name), preview, watch. CLAIM(Tu-hZ6lqNtY@04:41) CLAIM(Tu-hZ6lqNtY@05:27)
5. Functional requirements as device breadth and network adaptation (video quality and promo media tuned to bandwidth and viewport). CLAIM(Tu-hZ6lqNtY@05:33) CLAIM(Tu-hZ6lqNtY@07:14)
6. For a large multi-team app, assume a shared design system first (typography, UI primitives, grid, common components) before page design. CLAIM(Tu-hZ6lqNtY@07:44) CLAIM(Tu-hZ6lqNtY@08:34)
7. Enumerate the pages (sign up, main, profile), then pick the most important two to actually design. CLAIM(Tu-hZ6lqNtY@08:40) CLAIM(Tu-hZ6lqNtY@09:46)
8. Build the page mockup, then the dependency-graph schema; pre-prepare schemas because drawing them live eats the interview. CLAIM(Tu-hZ6lqNtY@12:25) CLAIM(Tu-hZ6lqNtY@13:51)
9. Show page reuse (search = main page minus the promo block) instead of a second design. CLAIM(Tu-hZ6lqNtY@14:42) CLAIM(Tu-hZ6lqNtY@16:13)
10. Define entities (movie, episode, actor, dashboard shape) in plain type notation. CLAIM(Tu-hZ6lqNtY@16:55) CLAIM(Tu-hZ6lqNtY@21:11)
11. Define the API (get dashboard, search) with query/tag/pagination controls. CLAIM(Tu-hZ6lqNtY@21:20) CLAIM(Tu-hZ6lqNtY@22:53)
12. Define the store: fetching points, normalized id-keyed stores, lazy detail fetch at the full card. CLAIM(Tu-hZ6lqNtY@24:42) CLAIM(Tu-hZ6lqNtY@28:51)
13. Optimization in three pillars: network, JavaScript, rendering. CLAIM(Tu-hZ6lqNtY@30:15) CLAIM(Tu-hZ6lqNtY@30:37)
14. Close with accessibility (subtitles, color schemes, hotkeys, rem sizing, aria-live). CLAIM(Tu-hZ6lqNtY@43:02) CLAIM(Tu-hZ6lqNtY@45:12)
15. Add device-specific delivery last (modern Smart TV builds can ship raw ES6 modules without polyfills). CLAIM(Tu-hZ6lqNtY@45:23) CLAIM(Tu-hZ6lqNtY@45:47)

## Worked design
Requirements
- Search movies by actor, genre, and name. CLAIM(Tu-hZ6lqNtY@05:01)
- Watch movies and see a short preview first. CLAIM(Tu-hZ6lqNtY@05:15)
- Run on Smart TVs, tablets, smartphones, desktops. CLAIM(Tu-hZ6lqNtY@05:35)
- Adapt stream quality to network bandwidth so the movie stays watchable. CLAIM(Tu-hZ6lqNtY@06:14)
- Hover previews and promos tuned to viewport and connection. CLAIM(Tu-hZ6lqNtY@07:14)

Components
- Design system assumed up front: typography, buttons/selects, grid system, shared components. CLAIM(Tu-hZ6lqNtY@08:05)
- Pages: sign up (conversion-critical), main page (designed), profile management (named, not designed). CLAIM(Tu-hZ6lqNtY@08:40) CLAIM(Tu-hZ6lqNtY@09:38)
- Main page: header with genre switcher (my list, TV shows, ...) and profile actions (search, profile menu with account/help links). CLAIM(Tu-hZ6lqNtY@09:58) CLAIM(Tu-hZ6lqNtY@10:35)
- Promo movie block with play and more-info. CLAIM(Tu-hZ6lqNtY@11:13)
- Dashboard rows of movie cards keyed by tag (recommended first). CLAIM(Tu-hZ6lqNtY@11:35)
- Card levels: hover preview; full card with preview, actions (rate, share, more info), description, genres, cast, episode list with switching, and a more-like-this row. CLAIM(Tu-hZ6lqNtY@12:35) CLAIM(Tu-hZ6lqNtY@12:55)
- Hierarchy: main page -> header (genres, actions) + page content (promo, movie list -> preview/card -> card full) + footer. CLAIM(Tu-hZ6lqNtY@14:02)
- Search page: same skeleton minus promo, movie-card grid, suggested tags. CLAIM(Tu-hZ6lqNtY@15:21) CLAIM(Tu-hZ6lqNtY@15:59)

Data model
- Movie: id, preview url, title, description (optional), tags, episodes, rating number, cast as actors. CLAIM(Tu-hZ6lqNtY@17:39) CLAIM(Tu-hZ6lqNtY@18:40)
- Episode: id, movie id, preview, title, description text, watch url(s), tags. CLAIM(Tu-hZ6lqNtY@19:19) CLAIM(Tu-hZ6lqNtY@20:18)
- Actor: name, full name, profile url. CLAIM(Tu-hZ6lqNtY@20:27)
- Dashboard response: map of tag -> movie array. CLAIM(Tu-hZ6lqNtY@20:52)
- Stores: movie by id, episodes by movie id, dashboard by tag, search results; fetched at page content and normalized. CLAIM(Tu-hZ6lqNtY@25:17) CLAIM(Tu-hZ6lqNtY@26:44)

API
- get dashboard: api key, user id -> dashboard map. CLAIM(Tu-hZ6lqNtY@21:27)
- search: api key, user id, query string, tag array, page size -> movie array in card form. CLAIM(Tu-hZ6lqNtY@22:11) CLAIM(Tu-hZ6lqNtY@22:53)
- Lazy detail fetch wired to opening the full movie card. CLAIM(Tu-hZ6lqNtY@28:47)

Realtime
- Not covered. This is a browse-and-consume product design; no push/sync/conflict discussion appears. Noted as absent (no citation).

Perf
- Network: zipping, Brotli, HTTP/2, WebP/PNG, gif promos, lazy detail fetches, bundle splitting (vendor / player on demand / profile / dashboard), image+video optimizer behind CDN, preload for likely-next pages. CLAIM(Tu-hZ6lqNtY@31:02) CLAIM(Tu-hZ6lqNtY@33:48) CLAIM(Tu-hZ6lqNtY@35:01)
- JS: do less, async heavy work, web workers for slow tasks, minimized code via bundler tooling. CLAIM(Tu-hZ6lqNtY@36:54) CLAIM(Tu-hZ6lqNtY@37:21) CLAIM(Tu-hZ6lqNtY@37:52)
- Rendering: SSR clean-HTML sign-up page, inline critical, defer non-critical, short CSS selectors, skeleton placeholders, transform-based animation, service-worker plus ETag caching. CLAIM(Tu-hZ6lqNtY@38:15) CLAIM(Tu-hZ6lqNtY@40:36) CLAIM(Tu-hZ6lqNtY@42:13)
- Device-specific: no-polyfill ES6 bundles for modern Smart TVs. CLAIM(Tu-hZ6lqNtY@45:23)

A11y
- Subtitles readable by screen readers. CLAIM(Tu-hZ6lqNtY@43:22)
- Color-blind color schemes; hotkeys for navigation, genres, search, open movie, open description, menu, help. CLAIM(Tu-hZ6lqNtY@43:46) CLAIM(Tu-hZ6lqNtY@44:28)
- rem sizing for zoom consistency; aria-live on input fields. CLAIM(Tu-hZ6lqNtY@44:39) CLAIM(Tu-hZ6lqNtY@45:06)

## Trade-offs he names
- Holistic product view vs deep single-feature design -> Netflix has no single killer interaction like infinite scroll or masonry, so product design takes the whole-app view. CLAIM(Tu-hZ6lqNtY@01:17) CLAIM(Tu-hZ6lqNtY@01:31)
- Design every page vs a chosen subset -> impossible to cover all pages; pick main + sign up and mention profile without designing it. CLAIM(Tu-hZ6lqNtY@09:02) CLAIM(Tu-hZ6lqNtY@09:38)
- Where to place sign-up depth -> in the optimization section, because fast first paint is what converts users there. CLAIM(Tu-hZ6lqNtY@09:13)
- Full card data upfront vs on open -> fetch lazily when more-info opens. CLAIM(Tu-hZ6lqNtY@30:59) CLAIM(Tu-hZ6lqNtY@31:15)
- Player code in the main bundle vs on demand -> on demand, since the player is not always open. CLAIM(Tu-hZ6lqNtY@34:05)
- Video vs gif hover promos -> gif, to avoid video's traffic cost (dated - see below). CLAIM(Tu-hZ6lqNtY@32:33)
- Analytics and extra code before vs after first render -> after. CLAIM(Tu-hZ6lqNtY@39:05)
- Web workers everywhere vs only where they fit -> he hedges: mention them, unsure they apply to this app. CLAIM(Tu-hZ6lqNtY@37:21)
- Polyfilled universal bundle vs runtime-targeted bundles -> targeted ES6 modules for modern Smart TVs, polyfills only where needed. CLAIM(Tu-hZ6lqNtY@45:23)

## Anti-patterns he warns about
- Trying to design every page of a large application in one sitting. CLAIM(Tu-hZ6lqNtY@09:02)
- Deep-diving individual component internals in a product-design round where the whole-app view is what's scored. CLAIM(Tu-hZ6lqNtY@13:30)
- Using full video for hover promos; the traffic cost is disproportionate. CLAIM(Tu-hZ6lqNtY@32:33)
- Blocking synchronous JavaScript on the interaction path. CLAIM(Tu-hZ6lqNtY@37:01)
- Animations that trigger reflow instead of paint/composition-level transforms. CLAIM(Tu-hZ6lqNtY@41:41)
- Long CSS selectors that slow the browser's matching work. CLAIM(Tu-hZ6lqNtY@40:43)
- Shipping polyfills to modern Smart TV runtimes and bloating the modules. CLAIM(Tu-hZ6lqNtY@45:33)
- Modeling cast as a plain string; it should be an actor array. CLAIM(Tu-hZ6lqNtY@18:54)

## Dated / contestable
- "Use gifs for promos" (CLAIM(Tu-hZ6lqNtY@32:33)) is the weakest call in the video and contradicts his own traffic logic: gifs are heavy. Modern apps use short muted MP4/WebM loops or animated WebP/AVIF; Netflix-style hover previews are video.
- AppCache again (CLAIM(Tu-hZ6lqNtY@42:13)) is the deprecated 2020 pattern; service-worker caching alone is the current tool.
- WebP-with-PNG fallback (CLAIM(Tu-hZ6lqNtY@32:17)) predates AVIF as a practical step in that negotiation.
- Serving sign-up as SSR with zero JS bundles (CLAIM(Tu-hZ6lqNtY@38:15)) remains good advice for first paint, but a fully JS-less form today needs care around validation and progressive enhancement; the spirit (minimal JS on the conversion page) stands.
- The no-polyfill ES6 Smart TV claim (CLAIM(Tu-hZ6lqNtY@45:23)) assumes a modern Chromium-based TV; plenty of 2020-era TVs still needed transpilation, and differential loading is now a bundler feature rather than a hand-made second bundle.
- ETag-only caching mention (CLAIM(Tu-hZ6lqNtY@42:42)) is dated shorthand; immutable content-hashed assets with Cache-Control is the standard complement today.
- His hedge that web workers "may not apply" to Netflix (CLAIM(Tu-hZ6lqNtY@37:21)) is arguable: client-side search ranking or thumbnail processing would justify them; it is honest uncertainty, not a law.
- The episode-URL choice "depending on network connection" (CLAIM(Tu-hZ6lqNtY@19:43)) is really adaptive bitrate streaming (HLS/DASH) done by the player, which he does not name; treat the entity shape as a simplification.
