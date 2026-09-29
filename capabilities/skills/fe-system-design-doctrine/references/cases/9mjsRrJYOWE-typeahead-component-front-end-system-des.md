# Case: Typeahead component, front-end system design

Source: https://www.youtube.com/watch?v=9mjsRrJYOWE (video id 9mjsRrJYOWE). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video 9mjsRrJYOWE against the local transcript.

- published 2023-10-11 / duration 3683s (61:23) / problem type: component-design

## Author's framework as used
Remake provenance (author-stated, not distiller opinion): this is a re-recording of his earlier typeahead system-design video from about two years prior (the 2021 video 9aOXGE7wAZo), done because the old one lacked a proper microphone. He says the remake is longer, carries more deep-dive material, and folds in the feedback viewers left in the older video's comments. CLAIM(9mjsRrJYOWE@00:02) CLAIM(9mjsRrJYOWE@00:24) No other statement in this video compares the two versions, so the delta is only what he claims here.

The ordered steps he actually runs:

1. Write the design plan on the board before designing anything; step one is clarifying the general requirements. CLAIM(9mjsRrJYOWE@01:14)
2. Step two is the advanced functionality: what the consumer can configure. CLAIM(9mjsRrJYOWE@01:22)
3. Sketch a quick mockup to fix the basic layout, input, result list, result item. CLAIM(9mjsRrJYOWE@01:57) CLAIM(9mjsRrJYOWE@21:05)
4. Classify the use case into an architecture variant (stateless, stateful/static, hybrid) before committing to an API. He runs this classification inside the advanced-functionality step. CLAIM(9mjsRrJYOWE@06:20)
5. Propose the API design, the property model exposed to consumers, split per architecture variant. CLAIM(9mjsRrJYOWE@21:51)
6. Design the internal state model and pick the data structure (trie for stateful; LRU-trie for hybrid). CLAIM(9mjsRrJYOWE@27:02) CLAIM(9mjsRrJYOWE@28:05)
7. Draw a data-flow diagram to surface where each architecture gets complicated. He marks this step as optional/educational. CLAIM(9mjsRrJYOWE@34:44)
8. Handle race conditions on in-flight requests. CLAIM(9mjsRrJYOWE@37:49)
9. Optimize performance along three pillars: network, rendering, JavaScript. CLAIM(9mjsRrJYOWE@40:50)
10. Cover security: DOM encapsulation plus optional content filtering. CLAIM(9mjsRrJYOWE@51:57)
11. Close with accessibility. CLAIM(9mjsRrJYOWE@55:50)

## Worked design
The case is one typeahead component designed across all three architecture variants at once, for teaching purposes; he states that in real work you pick exactly one. CLAIM(9mjsRrJYOWE@16:23)

Requirements
- Autocomplete results driven by what the user types. CLAIM(9mjsRrJYOWE@04:33)
- Generic over data types rather than one fixed entity shape. CLAIM(9mjsRrJYOWE@04:49)
- Efficient data requests with results cached where the variant needs it. CLAIM(9mjsRrJYOWE@05:04)
- Works with both asynchronous server data and static local data. CLAIM(9mjsRrJYOWE@05:35)
- Advanced: configuration flexibility (cache TTL, cache size, max results), custom item template, CSS customization, content filtering and DOM encapsulation, accessibility, network efficiency, minimal bundle size, large sync/async data sets. CLAIM(9mjsRrJYOWE@17:02) CLAIM(9mjsRrJYOWE@20:13)

Components
- Typeahead input where the query is typed. CLAIM(9mjsRrJYOWE@21:12)
- Search list containing the search items. CLAIM(9mjsRrJYOWE@21:18)
- Search item, whose representation is the customization point. CLAIM(9mjsRrJYOWE@21:24)

Data model
- Stateless: no internal state at all. CLAIM(9mjsRrJYOWE@27:30)
- Stateful: trie (prefix tree) over the vocabulary; search and insert cost about the word length; space grows with words times alphabet size. CLAIM(9mjsRrJYOWE@28:05) CLAIM(9mjsRrJYOWE@32:16) CLAIM(9mjsRrJYOWE@33:03)
- Hybrid: LRU-trie, same structure with an entry cap and least-recently-used eviction. CLAIM(9mjsRrJYOWE@28:28)

API
- maxResults: how many items the query returns to the list. CLAIM(9mjsRrJYOWE@22:07)
- minQuerySize: how many characters must be typed before any lookup. CLAIM(9mjsRrJYOWE@22:30)
- template: item renderer (framework-agnostic HTML template in his design). CLAIM(9mjsRrJYOWE@22:52)
- onItemUpdate: lazy mutation of one item's element given new data. CLAIM(9mjsRrJYOWE@23:25)
- onQuery (required for stateless): query + page size in, search behavior defined by the host. CLAIM(9mjsRrJYOWE@24:19) CLAIM(9mjsRrJYOWE@26:27)
- onItemSelected: selection callback. CLAIM(9mjsRrJYOWE@24:38)
- cacheTTL and cacheSize for the hybrid variant. CLAIM(9mjsRrJYOWE@25:00)

Realtime / race handling
- With a slow API, debouncing alone can still let several requests go out and return out of order. CLAIM(9mjsRrJYOWE@38:23)
- Cancel earlier requests when a newer query is issued, keeping only the latest. CLAIM(9mjsRrJYOWE@39:33)
- This cancellation is framed as part of the network-efficiency requirement set up front. CLAIM(9mjsRrJYOWE@39:55)

Performance
- Network: layered caching, debouncing, small dependency and CSS footprint, CDN plus compression. CLAIM(9mjsRrJYOWE@41:17) CLAIM(9mjsRrJYOWE@43:24) CLAIM(9mjsRrJYOWE@45:15)
- Rendering: placeholders, lazy DOM updates, virtualization for long lists, flattened CSS class names, GPU-composited CSS animations, no reflows. CLAIM(9mjsRrJYOWE@46:14) CLAIM(9mjsRrJYOWE@48:43)
- JavaScript: server does expensive search, no synchronous blocking jobs, web workers for big client-side filtering. CLAIM(9mjsRrJYOWE@50:46)

Security
- Shadow DOM encapsulation to limit external DOM access. CLAIM(9mjsRrJYOWE@53:01)
- Only limited, class-based customization exposed to consumers. CLAIM(9mjsRrJYOWE@54:04)
- Filter hook for untrusted third-party data. CLAIM(9mjsRrJYOWE@55:05)

Accessibility
- Keyboard reachability for all items plus shortcut configuration. CLAIM(9mjsRrJYOWE@56:18)
- Scalable (rem) units. CLAIM(9mjsRrJYOWE@56:57)
- Accessible HTML tags; a hidden input can carry the value so screen readers read it. CLAIM(9mjsRrJYOWE@57:55) CLAIM(9mjsRrJYOWE@58:30)
- Focus control over the absolutely-positioned dropdown. CLAIM(9mjsRrJYOWE@59:06)

## Trade-offs he names
- Stateless vs stateful/static: stateless wins on integration and reusability but depends on an external controller for data; static wins on search speed and zero network round trips but caps your data-set size. CLAIM(9mjsRrJYOWE@08:44) CLAIM(9mjsRrJYOWE@11:07)
- Static vs hybrid: static has simpler configuration (no cache TTL/size to manage); hybrid adds cache invalidation and server sync work. CLAIM(9mjsRrJYOWE@11:28) CLAIM(9mjsRrJYOWE@13:18)
- Hybrid vs walking away: he says you take the hybrid only when an unchangeable slow legacy API makes it worthwhile, and rarely otherwise. CLAIM(9mjsRrJYOWE@13:31) CLAIM(9mjsRrJYOWE@16:09)
- Client cache only vs client + browser + server cache: decide per use case; managing all three together is the hard part. CLAIM(9mjsRrJYOWE@43:04)
- Web workers vs overhead: potentially useful for large client-side filtering, but probably overhead for a typeahead. CLAIM(9mjsRrJYOWE@51:15)
- Virtualization vs design: if you need to render a thousand rows, either the design or the use case is wrong, virtualization is the mitigation, not the fix. CLAIM(9mjsRrJYOWE@48:33)

## Anti-patterns he warns about
- Loading millions of values into client-side state, it blocks the UI thread and is not a UI-side workload. CLAIM(9mjsRrJYOWE@11:50)
- Rendering a thousand rows inside a typeahead; he calls it either bad design or a mis-shaped use case. CLAIM(9mjsRrJYOWE@48:33)
- Re-rendering the whole component when one item's data changes. CLAIM(9mjsRrJYOWE@23:37)
- Letting in-flight responses land in whatever order they return, showing stale results to the user. CLAIM(9mjsRrJYOWE@39:09)
- Pulling in a large npm package for a single function. CLAIM(9mjsRrJYOWE@44:13)
- Importing an entire CSS framework where a small subset would do. CLAIM(9mjsRrJYOWE@44:46)
- Keeping the search value only in JavaScript state so a screen reader encounters a bare div. CLAIM(9mjsRrJYOWE@58:13)
- Fixed pixel sizing that ignores user zoom settings. CLAIM(9mjsRrJYOWE@57:29)
- Deep, unflattened CSS class-name structures that slow DOM tree building at scale. CLAIM(9mjsRrJYOWE@48:51)

## Dated / contestable
- His prediction that web components still need something like five years to be widely adopted is a 2023 guess; browser support is now broad, though framework-first teams still debate shadow DOM styling workflows. The security motivation for encapsulation stands regardless. CLAIM(9mjsRrJYOWE@53:26)
- He deliberately skips newer CSS sizing units because adoption was low at the time; adoption has grown since. CLAIM(9mjsRrJYOWE@57:38)
- The "caching is unneeded in 90% of scenarios" line is a heuristic he offers, not a measured claim. CLAIM(9mjsRrJYOWE@05:14)
- "LRU trie" is his own naming for the capped, LRU-evicting variant; he notes the naming convention is invented and libraries exist rather than expecting you to implement it. CLAIM(9mjsRrJYOWE@06:12) CLAIM(9mjsRrJYOWE@34:23)
