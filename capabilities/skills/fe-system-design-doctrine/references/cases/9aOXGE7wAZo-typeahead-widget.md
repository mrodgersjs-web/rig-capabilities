# Case: [Front-End System Design] - Typeahead Widget

Source: https://www.youtube.com/watch?v=9aOXGE7wAZo (video id 9aOXGE7wAZo). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video 9aOXGE7wAZo against the local transcript.

- published 2020-12-29 / duration 2190s (~37 min) / problem type: component-design (reusable typeahead/search-suggestions widget)

## Author's framework as used
1. Note the difference first: component design is not product design, think about how the component is reused across an app and what API it exposes, not about server APIs and data entities. CLAIM(9aOXGE7wAZo@00:33)
2. Requirements in two tiers: general (core functionality) then functional (technical specifics like cache size and configuration). CLAIM(9aOXGE7wAZo@01:38)
3. Component architecture: high-level mockup, then dependency graph. CLAIM(9aOXGE7wAZo@02:02)
4. Drop data-entity design entirely for a component problem and replace it with prop/API design, how the consumer uses the widget in different places. CLAIM(9aOXGE7wAZo@02:18)
5. Store design scoped to the widget's own state, not the whole application. CLAIM(9aOXGE7wAZo@02:58)
6. Optimization across three pillars (network, rendering, JavaScript), then accessibility. CLAIM(9aOXGE7wAZo@20:34)
7. Close with distribution: extract as an npm package so the component is decoupled and reusable. CLAIM(9aOXGE7wAZo@35:04)

## Worked design
- Requirements: search items for a typed query; customizable item look; any data format with static or async sources; network efficiency; internal result caching; configuration (cache size, filter function, item representation, min query); wide device range + keyboard access; performance optimized, CLAIM(9aOXGE7wAZo@03:27).
- Components: SearchSuggestions root with SearchInput and SuggestionList; SuggestionResult is a user-supplied template (marked as the customizable slot), CLAIM(9aOXGE7wAZo@09:15).
- Props: getResults(query) => Promise<T[]>, minQuery (default 3), maxResults (default 10), renderItem(datum) => HTMLElement, optional updateItem(el) => void, className, cacheSize (default 5), CLAIM(9aOXGE7wAZo@10:55).
- Data model / state: fixed-size result map (query -> previous result, evict oldest), data array of current fetched results, page size = max visible results, current page, cached config (cache size, min query), the template function, and the current query, CLAIM(9aOXGE7wAZo@15:25).
- API/consumer flow: state data array feeds the suggestion list; each datum goes through the user's renderItem/updateItem template; static mode filters closure-held data inside getResults, CLAIM(9aOXGE7wAZo@19:32).
- Realtime: none; updates arrive via debounced fetches and cache hits, CLAIM(9aOXGE7wAZo@22:01).
- Perf: debounce; multi-level caching with a cacheTime TTL (~10s default); node virtualization with data swaps; CSS animations; flat selectors; Web Workers for big client-side filters; server-side filtering for large datasets, CLAIM(9aOXGE7wAZo@22:01).
- A11y: keyboard shortcuts and tab navigation, rem sizing, live-region announcements, ARIA roles on items, CLAIM(9aOXGE7wAZo@30:47).
- Distribution: npm package, fully decoupled from the host app, CLAIM(9aOXGE7wAZo@35:04).

## Trade-offs he names
- Data entities vs prop contract: a component has no server entity design -> delete the entities stage and design props instead. CLAIM(9aOXGE7wAZo@02:18)
- Remove-and-reinsert DOM vs node reuse: re-creating nodes per query is wasteful -> keep a constant DOM set and update in place via updateItem. CLAIM(9aOXGE7wAZo@13:32)
- Fixed result map vs unbounded cache: queries repeat and memory grows -> fixed-size map evicting the oldest entry. CLAIM(9aOXGE7wAZo@17:14)
- Fetch 100 show 10 vs fetch 10: fetching more but rendering a page at a time keeps DOM constant while allowing scroll-to-load-more. CLAIM(9aOXGE7wAZo@18:11)
- Client filtering vs worker filtering: filtering 1000 items on the UI thread lags -> Web Worker for large static sets. CLAIM(9aOXGE7wAZo@28:34)
- Client vs server filtering for large data: the widget only supplies the API -> prefer server-side filtering when the dataset is large. CLAIM(9aOXGE7wAZo@29:31)
- Widget-level network control vs app-level: a widget cannot own app-wide compression/CDN -> optimize what it does own (debounce + its cache) and leave the rest to the app. CLAIM(9aOXGE7wAZo@21:28)
- Default item template vs consumer template: item looks vary wildly (people, groups) -> no default, the user provides the template. CLAIM(9aOXGE7wAZo@03:59)

## Anti-patterns he warns about
- Firing a search request on every keystroke. CLAIM(9aOXGE7wAZo@05:30)
- Deleting and recreating DOM nodes on each result update instead of reusing them. CLAIM(9aOXGE7wAZo@13:32)
- Letting the result cache grow without eviction. CLAIM(9aOXGE7wAZo@17:14)
- JavaScript-driven animation and frequent width/height changes that trigger reflows. CLAIM(9aOXGE7wAZo@26:01)
- Filtering large static datasets synchronously on the UI thread. CLAIM(9aOXGE7wAZo@28:34)
- Assuming the widget owns whole-application network performance (compression, bundling) instead of its own slice. CLAIM(9aOXGE7wAZo@21:28)

## Dated / contestable
- Framework-agnostic prop design described in TypeScript notation over vanilla DOM elements; today's interviews usually expect React-style controlled components, though the prop shapes translate directly. CLAIM(9aOXGE7wAZo@09:59)
- "ramps" in the transcript is rem; "rattles" is Brotli; "tabular items" is tabbable items, transcription artifacts, not different concepts. CLAIM(9aOXGE7wAZo@32:57)
- Manual virtualization via IntersectionObserver remains valid, but off-the-shelf virtual list libraries are the modern default answer. CLAIM(9aOXGE7wAZo@24:41)
- The minQuery default of 3 is conventional but product-dependent; search-as-you-type products often use 1 with aggressive debouncing. CLAIM(9aOXGE7wAZo@11:45)
