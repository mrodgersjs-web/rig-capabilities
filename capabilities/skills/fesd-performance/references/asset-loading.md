# Asset loading

Purpose: get the critical bytes to the screen first and everything else later, with a bundle and image pipeline that stays small per consumer and per device.

## When to load

Bundle shape and code-splitting decisions, image format and sizing, lazy loading, preload/preconnect hints, critical-path inlining, fonts, offline caching of assets, and any "first paint is slow because of assets" complaint.

## Step checklist

1. List what blocks first paint. Inline that set (critical CSS/JS) and defer or lazy-load everything else.
2. Split bundles along stability and usage: vendor code that rarely changes caches separately; rarely needed features load on demand.
3. For a published package, split core / theming / utilities so consumers install only the core.
4. Decide the runtime target, then the payload: one modern bundle where the support matrix allows, legacy split only where old runtimes really remain.
5. Build the image pipeline: modern format with fallback, per-device resize behind the CDN, lazy load on intersection, placeholder while loading.
6. Add hints: preconnect or preload for the high-priority next fetch, dns-prefetch for late small ones.
7. Check dependency weight before adding anything: never pull a heavy library for one helper.
8. Offline requirement: cache code, styles, data, and images in a service worker.

## Laws

**Bundle shape**

- Split bundles along stability lines: vendor (rarely changes, cache friendly), page code, analytics, and utilities that load later. **consensus** CLAIM(3MADCVqL534@37:22, LEaiGjffLEs@29:50, 5vyKhm2NTfw@37:11)
- Split by usage as well: vendor libraries, on-demand player, profile/sign-up, dashboard; lazy-load the rarely needed chunks. **single-source** CLAIM(Tu-hZ6lqNtY@33:48)
- Maximize splitting under HTTP/2 and lazy-load component code a given page does not use. **single-source** CLAIM(tsGarhpWOws@47:07)
- Bundle-split over HTTP/2 and ship separate legacy and modern bundles. **single-source** CLAIM(leo1FZ6vu1I@52:00)
- For a distributed component package, make the package modular: split core, theming, and utility modules so consumers install only the core. **consensus** CLAIM(lO6GyCvbDm8@22:02, u6jhTo13_No@28:08)
- Keep the package and CSS footprint minimal and never pull a heavy dependency just for a single helper function. **consensus** CLAIM(9mjsRrJYOWE@43:51, 9mjsRrJYOWE@44:34)
- Scope the JavaScript features you use: fewer next-generation features means fewer polyfills in the bundle. **single-source** CLAIM(u6jhTo13_No@27:28)
- Minify as well as compress, and serve the package from a CDN. **consensus** CLAIM(u6jhTo13_No@29:28, lO6GyCvbDm8@20:41)

**Runtime target (the ES5/ES6 question)**

- Ship separate ES5 and ES6 bundles so modern environments skip polyfills and save tens of kilobytes. **consensus (dated, see below)** CLAIM(lO6GyCvbDm8@21:29, u6jhTo13_No@26:39)
- Ship a modern-format payload (modern JS target, modern image formats with fallbacks) instead of one lowest-common-denominator bundle. **consensus** CLAIM(LEaiGjffLEs@31:06)
- Ship modern-runtime targets a minified ES6+ module bundle without polyfills when the user base runs modern browsers (his case: Chromium-based smart TVs). **consensus** CLAIM(Tu-hZ6lqNtY@45:23, tsGarhpWOws@46:36)

**Images**

- Serve images as a modern format with a PNG fallback and resize them through an image service that takes the image URL and the viewport as parameters. **consensus** CLAIM(3MADCVqL534@38:50, tsGarhpWOws@47:55)
- Let the image service size assets per device; never ship retina-size files to phones. **single-source** CLAIM(LEaiGjffLEs@33:14)
- Cache the optimized renditions at the CDN edge so the optimization service is hit once and each user gets the nearest copy. **consensus** CLAIM(3MADCVqL534@40:20, 5vyKhm2NTfw@34:42, Tu-hZ6lqNtY@35:01, LEaiGjffLEs@33:14)
- Lazy-load images only when the viewport intersects them. **consensus** CLAIM(3MADCVqL534@41:14, 5vyKhm2NTfw@42:42)
- Use animated GIF rather than heavy video for hover promos to save traffic (dated, see below). **single-source** CLAIM(Tu-hZ6lqNtY@32:17)
- Route uploads through an optimization service that converts to the modern format and resizes. **single-source** CLAIM(tsGarhpWOws@47:55)

**Critical path**

- Inline critical CSS and JS into the HTML so first render never waits on those fetches; load the rest async or deferred. **consensus** CLAIM(3MADCVqL534@42:03, 5vyKhm2NTfw@39:14, LEaiGjffLEs@32:32, Tu-hZ6lqNtY@38:48)
- Inline critical resources and lazy-load non-critical ones, analytics last, showing placeholders while loading. **single-source** CLAIM(leo1FZ6vu1I@54:27)
- Separate critical from non-critical resources and defer what does not block first paint. **single-source** CLAIM(LEaiGjffLEs@32:32)

**Hints**

- Use rel=preconnect and rel=preload for high-priority follow-up bundles, and dns-prefetch for late, small ones like analytics. **single-source** CLAIM(3MADCVqL534@42:44)
- Preload likely-next pages in the background (for example profile scripts) so navigation does not block on fetches. **single-source** CLAIM(Tu-hZ6lqNtY@39:59)
- Preload non-critical resources in the background after the critical assets have loaded, to save network time later. **single-source** CLAIM(tsGarhpWOws@45:39)

**Deferral**

- Delay analytics until after the app loads to cut time-to-first-content, when the business accepts losing bounce-only visits. **single-source** CLAIM(3MADCVqL534@43:53)

**Loading UX (perceived speed)**

- Show skeleton placeholders for loading images and cards; visible progress reduces perceived load time. **consensus** CLAIM(3MADCVqL534@45:17, Tu-hZ6lqNtY@40:53)
- Render placeholders rather than empty screens so the wait feels shorter to the user. **consensus** CLAIM(9mjsRrJYOWE@46:14, lO6GyCvbDm8@24:45, LEaiGjffLEs@37:01)
- Show skeleton screens whenever loading is slow to cut perceived load time. **consensus** CLAIM(LEaiGjffLEs@37:01, 5vyKhm2NTfw@42:42)

**Server-side rendering for the pages where speed sells**

- Server-side pre-render some feed pages to reduce time-to-first-content. **single-source** CLAIM(5vyKhm2NTfw@38:24)
- Server-render the conversion page as clean HTML without JS bundles to minimize time-to-first-content and time-to-interactive. **single-source** CLAIM(Tu-hZ6lqNtY@38:15)
- Skip server-side rendering when the extra infrastructure does not pay off (his case: a chat app). **single-source** CLAIM(LEaiGjffLEs@38:50)

**Offline assets**

- Support offline mode by caching code, styles, data, and images through a registered service worker. **consensus** CLAIM(3MADCVqL534@47:44, 5vyKhm2NTfw@43:40, LEaiGjffLEs@40:13)
- Cache scripts, styles, data, and images in a service worker and combine that with HTTP caching semantics such as ETag. **single-source** CLAIM(Tu-hZ6lqNtY@42:13)
- Enable HTTP/2 and a service worker that caches fetched assets so the app boots fast and works offline. **single-source** CLAIM(tsGarhpWOws@45:00)

**Fonts**

The corpus has no font law; nothing about font subsetting, font-display, or preloading font files is claimed by the author here. Distiller note (not the author): subset fonts to the glyphs used, set font-display so text is visible before the font arrives, preload the one or two faces the first screen needs, and count font files in the same critical-path list as CSS and JS.

## Decision table

| question | pick when | citation |
|---|---|---|
| one bundle or many | separate whenever stability or usage differs (vendor / page / analytics / rare features) | CLAIM(3MADCVqL534@37:22, Tu-hZ6lqNtY@33:48) |
| bundle granularity | weigh splitting against cache granularity: every small change invalidates a whole bundle | CLAIM(gxF9fLo5XQw@21:51) |
| legacy bundle | only when the real support matrix contains old runtimes | CLAIM(lO6GyCvbDm8@21:29, tsGarhpWOws@46:36) |
| SSR or client render | SSR where time-to-first-content decides conversion; skip it when infra cost outweighs the gain | CLAIM(Tu-hZ6lqNtY@38:15, LEaiGjffLEs@38:50) |
| eager or lazy image | lazy on intersection, placeholder while fetching | CLAIM(3MADCVqL534@41:14, 3MADCVqL534@45:17) |
| inline or fetch | inline what blocks first paint, defer everything else | CLAIM(3MADCVqL534@42:03) |

## Worked cases

- 3MADCVqL534 [Front-End System Design] - Pinterest: full asset section (bundle split, image service, CDN edge cache, hints, skeletons, offline).
- Tu-hZ6lqNtY [Front-End Product Design] - Netflix: usage-based chunk split for a media catalog and a clean-HTML conversion page.
- LEaiGjffLEs [Front-End System Design] - Chat application: modern-format payload, critical/deferred split, and the no-SSR counter-case.
- 5vyKhm2NTfw [Front End System Design] - Facebook News Feed: SSR pre-render for some feed pages plus lazy images.
- lO6GyCvbDm8 [Front-End System Design] - Design a Poll Widget and u6jhTo13_No [Front-End System Design] - Data Table Component: small-package economics (modular package, minify, CDN, polyfill budget).
- tsGarhpWOws [Front-End System Design] - Notion-like editor: aggressive splitting under HTTP/2 plus the optimizer service for uploads.

## Dated / contestable

- Separate ES5/ES6 bundles with polyfill economies (CLAIM(lO6GyCvbDm8@21:29, u6jhTo13_No@26:39, leo1FZ6vu1I@52:56)) are 2020-2022 advice. Distiller note (not the author): post-IE11, drive one modern build from browserslist and transpile or polyfill only where the measured support matrix demands it.
- "WebP with PNG fallback" (CLAIM(3MADCVqL534@38:50, LEaiGjffLEs@31:06)) predates AVIF. Distiller note (not the author): keep the fallback pattern and the image-service idea, update the format pair; AVIF is often smaller than WebP.
- Animated GIFs for hover promos (CLAIM(Tu-hZ6lqNtY@32:17)) are the heavy option. Distiller note (not the author): a muted short MP4/WebM loop or animated WebP/AVIF delivers the same effect at a fraction of the bytes.
- The application-cache plus service-worker offline story (CLAIM(3MADCVqL534@47:48, 5vyKhm2NTfw@40:02, Tu-hZ6lqNtY@42:13)) names a removed browser API. Distiller note (not the author): service-worker caching alone is the answer today.
