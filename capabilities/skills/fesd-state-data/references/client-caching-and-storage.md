# Client caching and storage

Purpose: decide what lives in memory, what lives on disk (IndexedDB) or in localStorage, how records are keyed, what each cache costs in bytes, and how every cache is bounded.

When to load: when choosing storage tiers, designing keys or time buckets, sizing storage with arithmetic, bounding a cache, or assigning shared-storage write ownership.

## Step checklist

1. Split the data: runtime state holds only what the view needs; bulk history goes to disk in IndexedDB.
2. Run the byte math before committing: points per day x bytes per point x days, per asset and per year.
3. Choose the record granularity: fixed time buckets beat one row per point for range queries.
4. Design the key so a range query scans buckets, not points: compound key of entity id, bucket id, time frame.
5. Derive bucket ids arithmetically (timestamp divided by bucket size) instead of storing explicit ranges.
6. Decide the durability trade explicitly: reduced IndexedDB durability for throughput is acceptable only when losing a small fraction of committed data is tolerable.
7. Bound every in-memory cache: size cap plus eviction (oldest out, or least-recently-used).
8. Set write ownership for shared storage: one writer, everyone else read-only.

## Storage tiers he uses

| Tier | What goes there | Cites |
|---|---|---|
| Runtime state (memory) | only what the visible view needs | CLAIM(HR2jXy_wPg4@26:25) |
| IndexedDB (disk) | bulk history, bucketed time series | CLAIM(HR2jXy_wPg4@29:56, HR2jXy_wPg4@31:47) |
| localStorage | small shared markers such as window roles between tabs of one domain | CLAIM(HR2jXy_wPg4@57:42) |
| In-widget cache maps | query results, rendered elements | CLAIM(9aOXGE7wAZo@17:14, u6jhTo13_No@20:27) |
| Dedicated structure | prefix search over a vocabulary (trie), capped and LRU-evicted | CLAIM(9mjsRrJYOWE@28:05, 9mjsRrJYOWE@28:28) |

## Laws

- Split storage: keep only what the view needs in runtime state and put bulk history on disk in
  IndexedDB. Single-source. (CLAIM(HR2jXy_wPg4@26:25))
- Bucket time-series points into fixed windows (5 minutes, 1 hour, 1 day) and store several bucket
  sizes in parallel, accepting the disk overhead. Single-source. (CLAIM(HR2jXy_wPg4@29:56))
- Key IndexedDB records with a compound key of asset id, bucket id and time frame so a range query
  scans buckets, not points. Single-source. (CLAIM(HR2jXy_wPg4@31:47))
- Compute bucket ids arithmetically from timestamp divided by bucket size instead of storing
  explicit ranges. Single-source. (CLAIM(HR2jXy_wPg4@33:45))
- Compute worst-case storage (points per day, bytes per point, per year) before committing to a
  storage scheme. Single-source. (CLAIM(HR2jXy_wPg4@35:15))
- Accept reduced IndexedDB durability in exchange for throughput when losing a small fraction of
  committed data is tolerable. Single-source. (CLAIM(HR2jXy_wPg4@41:05))
- Store points as minimal open/close pairs so each entry costs a fixed small number of bytes.
  Single-source. (CLAIM(HR2jXy_wPg4@21:22))
- Let extension windows read shared storage but never write it; route every write and fetch through
  the host window. Single-source. (CLAIM(HR2jXy_wPg4@60:03))
- Cache search results inside the widget so repeated queries do not refetch. Single-source.
  (CLAIM(9aOXGE7wAZo@05:51))
- Store results in a fixed-size map keyed by query, evicting the oldest entry when the cache size
  (default 5) is exceeded. Single-source. (CLAIM(9aOXGE7wAZo@17:14))
- Keep fetched data larger than visible data and page through it: store page size and current page,
  extend on scroll. Single-source. (CLAIM(9aOXGE7wAZo@18:11))
- For static data, hold the data in a closure inside the results function and filter it per query.
  Single-source. (CLAIM(9aOXGE7wAZo@19:58))
- Store the searchable vocabulary in a trie so prefix lookups cost about the length of the typed
  word, not the size of the data set. Single-source. (CLAIM(9mjsRrJYOWE@28:05, 9mjsRrJYOWE@32:16))
- Bound the hybrid variant with an LRU-trie that evicts least-recently-used entries once the entry
  limit is exceeded. Single-source. (CLAIM(9mjsRrJYOWE@28:28))
- Cache rendered HTML elements in state and update their text on prop changes instead of
  re-inserting nodes. Consensus. (CLAIM(lO6GyCvbDm8@18:07, u6jhTo13_No@20:27))
- Keep internal state minimal: the passed props, a root element reference, and a reusable element
  cache. Single-source. (CLAIM(lO6GyCvbDm8@16:23))
- Store registered listeners, the searchable flag, class names, current page and page size in the
  same widget state. Single-source. (CLAIM(u6jhTo13_No@19:52))
- Offer an optional per-column update function (element plus new data to HTML element); without one
  the column must be fully re-rendered. Single-source. (CLAIM(u6jhTo13_No@21:06))

## The byte-level storage math (HR2jXy_wPg4)

His worst case is one point per second: 86,400 points per day. At 8 bytes per point that is roughly
0.7 MB per asset per day and roughly 255 MB per asset per year
(CLAIM(HR2jXy_wPg4@36:57)). The same video's lookup win: a 60-minute range that would scan 3,600
points becomes about 12 bucket reads once records are bucketed and compound-keyed
(CLAIM(HR2jXy_wPg4@30:08)). Do this arithmetic in the answer, in front of the interviewer or the
reviewer: it is what turns a storage opinion into a checkable claim.

## Decision table

| Decision | Pick | When to deviate | Cites |
|---|---|---|---|
| Memory only vs memory + disk | split | memory only when the whole dataset fits the view with headroom | CLAIM(HR2jXy_wPg4@26:25) |
| One row per point vs time buckets | buckets | per-point only for tiny fixed ranges | CLAIM(HR2jXy_wPg4@29:56) |
| One bucket size vs several | several in parallel | one size when the visible range never changes | CLAIM(HR2jXy_wPg4@33:45) |
| Stored ranges vs computed bucket ids | computed ids | stored ranges only when buckets are irregular | CLAIM(HR2jXy_wPg4@33:45) |
| Durability vs throughput | throughput with accepted loss | full durability when losing committed data is unacceptable | CLAIM(HR2jXy_wPg4@41:05) |
| Cache eviction | oldest out past cap, or LRU past entry limit | no unbounded option exists | CLAIM(9aOXGE7wAZo@17:14, 9mjsRrJYOWE@28:28) |
| Search over vocabulary | trie | linear scan only for tiny lists | CLAIM(9mjsRrJYOWE@28:05) |
| Row update | cached element text update | full column re-render when no updater function exists | CLAIM(u6jhTo13_No@21:06) |
| Shared storage writes | host window only | never multi-writer | CLAIM(HR2jXy_wPg4@60:03) |

## Anti-patterns

- Storing one row per second and scanning linearly for a range query (CLAIM(HR2jXy_wPg4@29:20)).
- Committing to a storage scheme before the byte math is written down (CLAIM(HR2jXy_wPg4@35:15)).
- Writing the bucket formula inverted (timestamp over bucket size is the correct form; he corrected
  this live) (CLAIM(HR2jXy_wPg4@33:39)).
- Letting a query cache grow past its cap (CLAIM(9aOXGE7wAZo@17:14)).
- Regenerating every row element on each data arrival (CLAIM(u6jhTo13_No@20:27)).
- Letting every window write shared storage (CLAIM(HR2jXy_wPg4@60:03)).

## Worked cases

- HR2jXy_wPg4, Frontend System Design - Financial Dashboard / TradingView: buckets, compound keys, durability, and the storage arithmetic. Steal the math habit (CLAIM(HR2jXy_wPg4@35:15, HR2jXy_wPg4@36:57)).
- 9aOXGE7wAZo, [Front-End System Design] - Typeahead Widget: query-keyed cache with oldest-out eviction and fetch-more-than-visible paging state (CLAIM(9aOXGE7wAZo@17:14, 9aOXGE7wAZo@18:11)).
- 9mjsRrJYOWE, Typeahead component: trie vocabulary store and its capped LRU variant (CLAIM(9mjsRrJYOWE@28:05, 9mjsRrJYOWE@28:28)).
- u6jhTo13_No, [Front-End System Design] - Data Table Component: cached row elements with per-column update functions (CLAIM(u6jhTo13_No@20:27, u6jhTo13_No@21:06)).
- lO6GyCvbDm8, [Front-End System Design] - Design a Poll Widget: element cache inside minimal widget state (CLAIM(lO6GyCvbDm8@16:23, lO6GyCvbDm8@18:07)).

## Dated / contestable

- The IndexedDB quota framing (about 30 percent of disk, roughly 2 GB per domain) is approximate.
  Distiller note (not the author): quotas are origin- and browser-specific and eviction behavior
  differs, so measure in the target browser. (CLAIM(HR2jXy_wPg4@27:08))
- "LRU trie" is his own label for a capped, LRU-evicting trie. Distiller note (not the author): use
  an existing capped cache or LRU library rather than implementing the label.
  (CLAIM(9mjsRrJYOWE@06:12, 9mjsRrJYOWE@34:23))
- The default cache size of 5 and min-query of 3 are conventional, product-dependent numbers.
  Distiller note (not the author): tune from measured query repetition and product behavior.
  (CLAIM(9aOXGE7wAZo@11:45))
- The claim that caching is unneeded in most scenarios is a heuristic he offers. Distiller note (not
  the author): argue it per product; it is not a measurement. (CLAIM(9mjsRrJYOWE@05:14))
