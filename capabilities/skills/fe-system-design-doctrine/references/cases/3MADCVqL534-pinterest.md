# Case: [Front-End System Design] - Pinterest

Source: https://www.youtube.com/watch?v=3MADCVqL534 (video id 3MADCVqL534). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video 3MADCVqL534 against the local transcript.

- published 2020-12-03 / duration 3107s (~52 min) / problem type: product-design
- Speaker: Evgenii Ray (Front-End Engineer channel), episode 2 of the series. Note: the ASR renders "masonry" as "mastery/menstrual/military" throughout; it always means the masonry grid layout.

## Author's framework as used
1. Open with the plan of the design: general requirements, functional requirements, component architecture, the masonry layout implementation, data entities, API, data store/layers, optimization, accessibility. CLAIM(3MADCVqL534@01:01) CLAIM(3MADCVqL534@03:42)
2. Collect general requirements first (feature behavior: masonry pins, hover/click details, comments, sharing, no video). CLAIM(3MADCVqL534@04:08) CLAIM(3MADCVqL534@05:32)
3. Collect functional requirements as platform/browser/device constraints - and ask the interviewer for them explicitly. CLAIM(3MADCVqL534@01:31) CLAIM(3MADCVqL534@01:38)
4. Componentize: mockup first (pin sizes), then enumerate components, then build the dependency graph. CLAIM(3MADCVqL534@09:01) CLAIM(3MADCVqL534@11:48)
5. Design the signature layout in depth (the masonry grid mechanics: zones, sentinels, sliding window, absolute positioning). CLAIM(3MADCVqL534@14:05) CLAIM(3MADCVqL534@15:26)
6. Describe data entities (pin, comment, user) even if the interview skips it. CLAIM(3MADCVqL534@26:02) CLAIM(3MADCVqL534@28:14)
7. Describe the API endpoints (get pins, get comments) with pagination controls. CLAIM(3MADCVqL534@28:33) CLAIM(3MADCVqL534@30:51)
8. Describe data layers: fetching points, normalized store, id-based access. CLAIM(3MADCVqL534@31:23) CLAIM(3MADCVqL534@32:14)
9. Work performance as three tracks: network, rendering, JavaScript. CLAIM(3MADCVqL534@34:02) CLAIM(3MADCVqL534@34:40)
10. Close with accessibility (keyboard shortcuts, color themes, aria-live, rem sizing). CLAIM(3MADCVqL534@48:24) CLAIM(3MADCVqL534@50:44)
11. Acknowledge time reality: a full run needs far more time than an interview slot, so expect to deep-dive one or two points only. CLAIM(3MADCVqL534@51:08) CLAIM(3MADCVqL534@51:18)

## Worked design
Requirements
- Pins laid out in a masonry grid, loaded as the user scrolls. CLAIM(3MADCVqL534@04:14)
- Hover shows pin affordances; click opens full pin details. CLAIM(3MADCVqL534@04:51)
- Pin media is gif or picture; video explicitly out of scope. CLAIM(3MADCVqL534@05:08)
- Users can comment and share. CLAIM(3MADCVqL534@05:29)
- ~95% browser support excluding IE11; adaptive across tablets and phones; PWA offline view of loaded pins; tolerates slow networks. CLAIM(3MADCVqL534@06:54) CLAIM(3MADCVqL534@07:39) CLAIM(3MADCVqL534@08:12)

Components
- Masonry grid with pin sizes L/M/S. CLAIM(3MADCVqL534@09:25)
- Pin shell: picture, link/share menu, actions dropdown; click opens the detail window. CLAIM(3MADCVqL534@10:30)
- Detail window: pin comments, pin details, pin picture. CLAIM(3MADCVqL534@13:32)
- Comment list (with show-more) and comment input. CLAIM(3MADCVqL534@11:28)
- Hierarchy: app root -> router -> pages (home/profile/header) -> pins feed page -> pins grid -> pins -> pin controls/menu/picture. CLAIM(3MADCVqL534@12:26) CLAIM(3MADCVqL534@13:13)

Data model
- Pin: id, origin (usually the pin board), description, title, image url, author. CLAIM(3MADCVqL534@26:48)
- Comment: author id, content; fetched separately from the pin. CLAIM(3MADCVqL534@27:41)
- User: id, nickname. CLAIM(3MADCVqL534@27:55)
- Store: flattened id-keyed maps (pins by id, users by id, comments by pin id). CLAIM(3MADCVqL534@32:22) CLAIM(3MADCVqL534@32:53)

API
- get pins: api key, user id, include-comments flag, timestamp cursor, min id range. CLAIM(3MADCVqL534@28:35) CLAIM(3MADCVqL534@29:28)
- get comments: api key, pin id, page size. CLAIM(3MADCVqL534@30:21)
- Fetching point lives at the pins feed page route. CLAIM(3MADCVqL534@31:50)

Realtime
- Not covered in this video (no update-push discussion; scrolling fetches are cursor-driven). No citation - noted as absent.

Masonry / infinite scroll (the core design)
- Canvas model: content height container, top and bottom sentinels as content edges, two-column grid with 8 pins initially. CLAIM(3MADCVqL534@15:42)
- Three zones: visible viewport, rendered-but-invisible pins, recycle zone of future data. CLAIM(3MADCVqL534@16:06)
- Loaded-but-unseen data only grows the canvas size; it is not rendered. CLAIM(3MADCVqL534@16:47)
- On bottom-sentinel intersection: evict the two farthest pins and render pins 9-10 in their place via a two-sided stack pop/push. CLAIM(3MADCVqL534@18:43) CLAIM(3MADCVqL534@19:23)
- Keep near-viewport pins (3-4) mounted against fast scroll jitter. CLAIM(3MADCVqL534@20:13)
- Absolute canvas: each pin absolutely positioned by cumulative translation (previous pin translation + size + margin) inside a flex-row grid. CLAIM(3MADCVqL534@20:55) CLAIM(3MADCVqL534@21:34)
- Repositioning is a paint-layer pixel move, not a reflow. CLAIM(3MADCVqL534@22:40)
- Recycled nodes keep their DOM identity; only data and position change, and the bottom sentinel moves down by the size of the swapped-in data. CLAIM(3MADCVqL534@23:02) CLAIM(3MADCVqL534@23:18)
- Scroll up mirrors the operation: push data at the start, evict from the end. CLAIM(3MADCVqL534@24:23)
- Variable heights are handled because every pin positions off the previous pin's translation. CLAIM(3MADCVqL534@25:03)

Perf
- Network: asset zipping then Brotli; HTTP/2; bundle split (vendor, pin grid, analytics, utilities). CLAIM(3MADCVqL534@35:08) CLAIM(3MADCVqL534@37:22)
- Images: WebP/PNG fallback, viewport-sized renditions from an image service, CDN caching of optimized results, lazy loading. CLAIM(3MADCVqL534@38:50) CLAIM(3MADCVqL534@40:20) CLAIM(3MADCVqL534@41:14)
- Rendering: inline critical CSS/JS, preconnect/preload priorities, dns-prefetch for analytics, delayed analytics, short CSS selectors, skeleton placeholders. CLAIM(3MADCVqL534@42:03) CLAIM(3MADCVqL534@44:35) CLAIM(3MADCVqL534@45:17)
- JS: async heavy work, cache, web workers. CLAIM(3MADCVqL534@46:16)
- Offline: service-worker caching of JS/CSS/pin data/images. CLAIM(3MADCVqL534@47:44)

A11y
- Keyboard shortcuts for add pin, go to top/bottom, share, like, quick menu, help. CLAIM(3MADCVqL534@48:52)
- Alternate color themes for color blindness; aria-live announcements on fields. CLAIM(3MADCVqL534@49:32) CLAIM(3MADCVqL534@49:47)
- rem-based sizing so user zoom scales text. CLAIM(3MADCVqL534@50:16)

## Trade-offs he names
- Deep-dive one area vs cover everything -> the interviewer will usually want one point (e.g. masonry + performance or API + accessibility); the full design took far longer than an interview slot. CLAIM(3MADCVqL534@51:08) CLAIM(3MADCVqL534@51:15)
- Comments embedded in pin payload vs separate fetch -> separate, by preference. CLAIM(3MADCVqL534@27:34)
- Strict browser support vs pragmatism -> drop IE11 and claim 95% coverage. CLAIM(3MADCVqL534@06:37)
- Analytics at load time vs after app load -> after, accepting the loss of bounce-only visits when the business does not need them. CLAIM(3MADCVqL534@43:53) CLAIM(3MADCVqL534@44:20)
- Three pin sizes in the interview vs the larger production set -> three is enough on the clock. CLAIM(3MADCVqL534@09:25)
- Raw DOM insert/remove in the grid vs absolute positioning with node reuse -> absolute canvas, because insert/delete is expensive. CLAIM(3MADCVqL534@20:40) CLAIM(3MADCVqL534@20:55)
- Aggressive eviction vs keeping near-viewport nodes -> keep them; render churn on scroll jitter is worse than a couple of extra mounted nodes. CLAIM(3MADCVqL534@19:57)

## Anti-patterns he warns about
- Designing before asking the interviewer about platforms and browsers. CLAIM(3MADCVqL534@01:38)
- Multi-level nested client data: hard and expensive to access. CLAIM(3MADCVqL534@33:01)
- Inserting and deleting grid DOM nodes directly: expensive tree operations. CLAIM(3MADCVqL534@20:40)
- Evicting nodes that are near the viewport, causing re-renders on every small scroll reversal. CLAIM(3MADCVqL534@19:57)
- Rendering future data as soon as it is fetched instead of just extending the canvas. CLAIM(3MADCVqL534@16:47)
- Long CSS selectors: the browser must match every selector on the page. CLAIM(3MADCVqL534@44:47)
- Synchronous heavy JavaScript blocking page loading. CLAIM(3MADCVqL534@46:26)
- Serving full-size images to small devices. CLAIM(3MADCVqL534@39:32)

## Dated / contestable
- AppCache ("application cache") with service workers (CLAIM(3MADCVqL534@47:48)) is the deprecated 2020-era pattern; today service-worker caching alone covers it.
- WebP with PNG fallback (CLAIM(3MADCVqL534@38:50)) predates AVIF as a mainstream third step in the negotiation.
- The HTTP/1 "five connections" framing (CLAIM(3MADCVqL534@36:43)) is roughly six per origin in browsers, and HTTP/2 does not make bundle strategy irrelevant (cache granularity still trades against request count).
- IE11 as the named exclusion (CLAIM(3MADCVqL534@06:40)) was a live decision in 2020; IE is now retired, so the underlying rule (name your exclusions) survives but the example does not.
- The claim that translation-based absolute positioning "doesn't trigger any reflow" (CLAIM(3MADCVqL534@22:40)) holds for position/transform updates but not when element sizes change and force layout recalculation.
- His Brotli figure of 10-20% over gzip (CLAIM(3MADCVqL534@35:35)) is a reasonable ballpark, not a guarantee; real gains depend on content type.
- He narrates the exercise as ~56 minutes (CLAIM(3MADCVqL534@51:08)) though the video runs ~52; treat the number as approximate.
