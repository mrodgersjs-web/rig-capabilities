# Case: [Front End System Design] - Facebook News Feed

Source: https://www.youtube.com/watch?v=5vyKhm2NTfw (video id 5vyKhm2NTfw). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video 5vyKhm2NTfw against the local transcript.

- published 2020-10-27 / duration 2871s (~48 min) / problem type: product-design
- Speaker: Evgenii Ray (Front-End Engineer channel), episode 1 of his front-end system design series, framed as his own interview preparation rather than a course.

## Author's framework as used
1. State an ordered plan of the whole design up front, before designing anything: general requirements, platform-specific requirements, component architecture, data entities, data API, data store, the flagship interaction (infinite scroll), optimization, accessibility. CLAIM(5vyKhm2NTfw@01:13) CLAIM(5vyKhm2NTfw@01:28) CLAIM(5vyKhm2NTfw@03:52)
2. Impose a tight time box on the exercise (he uses about 15 minutes). CLAIM(5vyKhm2NTfw@01:09)
3. Write general requirements as the feature plus its basic user actions (feed of subscribed stories, posting with attachments). CLAIM(5vyKhm2NTfw@04:02) CLAIM(5vyKhm2NTfw@05:05)
4. Write specific requirements around devices and disability access, then stop. CLAIM(5vyKhm2NTfw@05:20) CLAIM(5vyKhm2NTfw@05:57)
5. Sketch the visual mockup, then a component dependency graph to expose data flow. CLAIM(5vyKhm2NTfw@06:11) CLAIM(5vyKhm2NTfw@07:14)
6. Describe data entities in TypeScript notation (story, comment, media, origin). CLAIM(5vyKhm2NTfw@08:51) CLAIM(5vyKhm2NTfw@09:10)
7. Enumerate API endpoints, then pick the transport style (REST vs GraphQL) explicitly. CLAIM(5vyKhm2NTfw@14:00) CLAIM(5vyKhm2NTfw@16:34)
8. Design the client store: mark fetching points on the component graph, then normalize the store. CLAIM(5vyKhm2NTfw@18:21) CLAIM(5vyKhm2NTfw@19:09)
9. Stress the design with an edge case (new stories arriving during scroll) and compare update techniques head to head. CLAIM(5vyKhm2NTfw@21:11) CLAIM(5vyKhm2NTfw@22:04)
10. Design the flagship interaction in detail (infinite scroll mechanics). CLAIM(5vyKhm2NTfw@26:02)
11. Split optimization into network, rendering, and JavaScript tracks and work each. CLAIM(5vyKhm2NTfw@33:03) CLAIM(5vyKhm2NTfw@33:28)
12. Close with accessibility: color schemes, screen-reader semantics, hotkeys. CLAIM(5vyKhm2NTfw@44:27) CLAIM(5vyKhm2NTfw@46:54)

## Worked design
Requirements
- Infinite scrollable feed where stories appear from the user's subscriptions: groups, pages, friends. CLAIM(5vyKhm2NTfw@04:08)
- User can post a story and attach comments, links, images, videos. CLAIM(5vyKhm2NTfw@04:51)
- Feature must work across a wide range of devices. CLAIM(5vyKhm2NTfw@05:32)
- Feature must be usable by people with disabilities. CLAIM(5vyKhm2NTfw@05:48)

Components
- Story card holds avatar, title, post date, text, images, and a control panel (like, comment, share). CLAIM(5vyKhm2NTfw@06:21)
- Comment list and comment input sit below each story. CLAIM(5vyKhm2NTfw@06:38)
- NewsFeed is simply a list of story components. CLAIM(5vyKhm2NTfw@06:51)
- Dependency graph: NewsFeed -> Stories -> StoryCard / CommentList / CommentInput, used to reason about data flow. CLAIM(5vyKhm2NTfw@07:52)

Data model
- Story: id, comments array, media array, creation timestamp, content text, origin, share id, plus optional custom data (avatar or group info). CLAIM(5vyKhm2NTfw@09:25) CLAIM(5vyKhm2NTfw@11:33)
- Origin: type (page, group, ...) plus name, replacing a plain user reference. CLAIM(5vyKhm2NTfw@10:52)
- Comment: id, type, author as user id, media array, date, content. CLAIM(5vyKhm2NTfw@12:05)
- Media: type (link, video, ...) plus url. CLAIM(5vyKhm2NTfw@13:14)
- Store: id-keyed maps for feeds, users, media, origins, comments; components look up by feed id. CLAIM(5vyKhm2NTfw@20:01) CLAIM(5vyKhm2NTfw@20:32)

API
- get posts: api key, user id, exclude-comments flag, cursor/timestamp, page size, min id. CLAIM(5vyKhm2NTfw@14:14) CLAIM(5vyKhm2NTfw@15:18)
- create post: api key, user id, post data. CLAIM(5vyKhm2NTfw@15:51)
- create comment: api key, user id, post id, comment data. CLAIM(5vyKhm2NTfw@16:04)
- Transport: REST chosen over GraphQL, either being defensible. CLAIM(5vyKhm2NTfw@17:47)
- Live updates: a subscribe-style endpoint fed by server-sent events. CLAIM(5vyKhm2NTfw@25:31)

Realtime
- Problem stated: naive re-fetch of get posts while scrolling wastes traffic. CLAIM(5vyKhm2NTfw@21:41)
- Options weighed: long polling, WebSockets, SSE, with their trade-offs. CLAIM(5vyKhm2NTfw@22:04)
- SSE picked: HTTP/2 support, payload overhead near zero, load-balances better than the alternatives. CLAIM(5vyKhm2NTfw@25:00)

Infinite scroll
- Motivation: entertainment content wants continuous scrolling; pagination and show-more add friction and are meant for analysis-oriented data. CLAIM(5vyKhm2NTfw@26:37)
- Mechanism: top and bottom sentinel nodes observed via IntersectionObserver. CLAIM(5vyKhm2NTfw@28:18)
- Sliding window example: viewport shows 10 stories; on scroll the window moves from 1-10 to 5-15 and only that set is mounted. CLAIM(5vyKhm2NTfw@30:07)
- Padding trick: growing top padding on scroll down and bottom padding on scroll up preserves perceived page size. CLAIM(5vyKhm2NTfw@31:39)

Perf
- Network: compression (Brotli named), WebP/PNG image negotiation, viewport-sized images from an image service cached on CDN with geographic locality. CLAIM(5vyKhm2NTfw@34:01) CLAIM(5vyKhm2NTfw@35:11)
- HTTP/2 multiplexing replaces the HTTP/1 connection limit that motivated bundling. CLAIM(5vyKhm2NTfw@36:23)
- Bundle split: feed, header, vendor libs, analytics scripts. CLAIM(5vyKhm2NTfw@37:22)
- Rendering: SSR pre-render for some feeds to cut time-to-first-content, inline critical CSS/JS, async/defer the rest. CLAIM(5vyKhm2NTfw@38:27) CLAIM(5vyKhm2NTfw@39:52)
- JS: do less, work async, cache, use web/service workers to escape the single-thread constraint. CLAIM(5vyKhm2NTfw@41:05)
- Images: lazy-load on viewport intersection, placeholders for perceived speed. CLAIM(5vyKhm2NTfw@43:13)
- PWA offline via service-worker resource caching. CLAIM(5vyKhm2NTfw@43:54)

A11y
- Alternate color schemes for color blindness. CLAIM(5vyKhm2NTfw@45:05)
- aria-live on inputs/textareas and alt on images for screen readers. CLAIM(5vyKhm2NTfw@45:19)
- Hotkeys: new story, post story, scroll down/top, help, quick-access main menu with sharing options. CLAIM(5vyKhm2NTfw@46:05) CLAIM(5vyKhm2NTfw@46:40)

## Trade-offs he names
- REST vs GraphQL -> GraphQL is more agile for multi-level data (client picks fields) but REST inherits HTTP caching and scales simply; for this feed he picks REST, saying either is defensible. CLAIM(5vyKhm2NTfw@17:01) CLAIM(5vyKhm2NTfw@17:47)
- Long polling vs WebSockets vs SSE -> polling is simplest but heavy per request and slower; WebSockets are fastest and truly real-time but he rejects them partly on HTTP/2 and load-balancing grounds; SSE wins at ~60ms latency tolerance. CLAIM(5vyKhm2NTfw@22:28) CLAIM(5vyKhm2NTfw@23:43) CLAIM(5vyKhm2NTfw@25:23)
- Pagination vs show-more vs infinite scroll -> pagination is for data you analyze; show-more adds a user action; infinite scroll keeps the user consuming entertainment content. CLAIM(5vyKhm2NTfw@26:44)
- Keeping all loaded stories mounted vs a sliding window -> the window keeps DOM size constant and mobile performance intact at the cost of re-render management and padding tricks. CLAIM(5vyKhm2NTfw@28:46) CLAIM(5vyKhm2NTfw@29:21)
- One giant bundle vs bundle splitting -> HTTP/1's connection limits justified bundling; HTTP/2 multiplexing removes that reason, so split bundles load in parallel. CLAIM(5vyKhm2NTfw@36:23) CLAIM(5vyKhm2NTfw@37:11)
- Client-only render vs SSR pre-render for some feeds -> pre-render cuts time-to-first-content. CLAIM(5vyKhm2NTfw@38:24)
- Placeholder vs loader vs nothing for pending images -> placeholders plus lazy loading; he notes research that a visible loader changes perceived load time. CLAIM(5vyKhm2NTfw@42:49)

## Anti-patterns he warns about
- Nested multi-level structures and large-array filtering in the client store; flatten and normalize instead. CLAIM(5vyKhm2NTfw@19:36)
- Mounting every loaded story: hundreds of stories means thousands of DOM elements and mobile performance collapse. CLAIM(5vyKhm2NTfw@28:46)
- Repeated get-posts calls just to catch new stories; that is pure traffic overhead. CLAIM(5vyKhm2NTfw@21:41)
- Deep, multi-level CSS selectors: the browser pays to parse and match them. CLAIM(5vyKhm2NTfw@42:07)
- Heavy synchronous JavaScript on the render path: it blocks all interaction on a single-threaded runtime. CLAIM(5vyKhm2NTfw@40:56)
- Sending a full request (headers, tokens) for every tiny update via polling. CLAIM(5vyKhm2NTfw@22:44)

## Dated / contestable
- The claim that WebSockets do not support HTTP/2 (CLAIM(5vyKhm2NTfw@23:50)) is contested by RFC 8441 (extended CONNECT), though browser/server support is still uneven; the load-balancing argument against them remains directionally valid.
- He describes SSE payloads as binary (CLAIM(5vyKhm2NTfw@24:35)); the EventSource stream is text-based, so this detail looks wrong even if the efficiency point stands.
- HTTP/1 connection limit stated as five (CLAIM(5vyKhm2NTfw@36:23)) is roughly six per origin in browsers, and HTTP/2 does not make bundling worthless (cache granularity, fewer requests still help).
- Caching "application cache" with service workers (CLAIM(5vyKhm2NTfw@40:02)) refers to AppCache, already deprecated by 2020 and since removed; service-worker caching alone is the current answer.
- WebP-with-PNG fallback (CLAIM(5vyKhm2NTfw@34:25)) predates AVIF as a practical option; today AVIF belongs in that negotiation.
- Passing an api key as an endpoint parameter (CLAIM(5vyKhm2NTfw@14:21)) is interview shorthand, not a production auth design.
