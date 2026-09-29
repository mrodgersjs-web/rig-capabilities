# Pagination

Purpose: define how a client walks a growing list deterministically, and which paging style fits feeds versus analyzed data.

When to load: when designing any list that loads in chunks (feeds, comment threads, tables, search results), or when asked offset versus cursor.

## What he actually states

He does not use the phrase "offset paging" in these videos. He states the contrast as two concrete
parameter styles:

1. Feed paging: a timestamp or cursor, a page size, and a min-id range. The cursor marks the point
   the client already has (data before that cursor), and the id range pins the window so a page is
   deterministic (CLAIM(5vyKhm2NTfw@14:48, 5vyKhm2NTfw@15:18)). The Pinterest read is the same
   shape: api key, user id, optional include-comments flag, timestamp cursor, min id
   (CLAIM(3MADCVqL534@28:35, 3MADCVqL534@29:28)).
2. Page paging: page number plus page size, held in widget state, used where the user wants an exact
   page of complex data (CLAIM(u6jhTo13_No@19:52, u6jhTo13_No@30:46)), and a related client-side
   variant that keeps more fetched data than visible and extends on scroll
   (CLAIM(9aOXGE7wAZo@18:11)).

So the reconstruction is: cursor-plus-id-range for append-heavy feeds where rows move under the
reader, page-size paging for data the user analyzes page by page. The offset-versus-cursor
vocabulary is the industry's; the parameter shapes above are his.

## Step checklist

1. Classify the list: append-heavy feed, or analyzed data set the user pages through.
2. For feeds: write the read as identity + cursor (or timestamp) + page size + min-id range; say in
   one sentence what "the next page" means.
3. For analyzed data: write page number + page size, and decide what the total count comes from.
4. Keep a child read minimal: parent id + page size (CLAIM(3MADCVqL534@30:21)).
5. On the client, keep fetched data larger than visible data and hold page size + current page in
   state (CLAIM(9aOXGE7wAZo@18:11)).
6. Match the scroll behavior to the content: continuous scroll for consumption, pagination for
   analysis (CLAIM(5vyKhm2NTfw@26:37)).
7. If the list is virtualized instead of paged, size the page per device class and keep a buffer so
   chunk swaps are invisible (CLAIM(fmIiDLbLc_s@15:00, fmIiDLbLc_s@15:37)).

## Laws

- Parameterize feed reads with a cursor or timestamp, a page size, and a min-id range so paging is
  deterministic. Consensus. (CLAIM(5vyKhm2NTfw@14:48, 3MADCVqL534@28:35))
- Keep the comment endpoint minimal: api key, pin id, page size. Single-source.
  (CLAIM(3MADCVqL534@30:21))
- Keep fetched data larger than visible data and page through it: store page size and current page,
  extend on scroll. Single-source. (CLAIM(9aOXGE7wAZo@18:11))

## Decision table

| Situation | Paging style | Why | Cites |
|---|---|---|---|
| Append-heavy feed, rows inserted while reading | cursor / timestamp + min-id range | the cursor pins the boundary; offsets shift as rows arrive | CLAIM(5vyKhm2NTfw@14:48) |
| Comment thread under a record | parent id + page size | child reads stay minimal | CLAIM(3MADCVqL534@30:21) |
| Table of data the user analyzes | page number + page size | the user wants an exact page of complex data | CLAIM(u6jhTo13_No@30:46) |
| Entertainment consumption list | infinite scroll over the cursor scheme | friction-free consumption | CLAIM(5vyKhm2NTfw@26:37) |
| Very large grid, both axes grow | virtualization with per-device page size + buffer | keeps node count constant | CLAIM(fmIiDLbLc_s@15:00, fmIiDLbLc_s@15:37) |
| Search results with repetition | fetched > visible, page state in the widget | extend on scroll without refetch | CLAIM(9aOXGE7wAZo@18:11) |

## Anti-patterns

- Paging a feed by numeric offset while rows are being inserted (CLAIM(5vyKhm2NTfw@14:48)).
- Omitting the id range so two pages can overlap or skip (CLAIM(5vyKhm2NTfw@15:18)).
- Fetching only what is visible, so every scroll tick becomes a request (CLAIM(9aOXGE7wAZo@18:11)).
- Defaulting to virtualization for analyzed table data when an exact page is what the user wants
  (CLAIM(u6jhTo13_No@30:46)).

## Worked cases

- 5vyKhm2NTfw, [Front End System Design] - Facebook News Feed: the cursor + page size + min-id read, and the infinite-scroll-versus-pagination product rule (CLAIM(5vyKhm2NTfw@14:48, 5vyKhm2NTfw@26:37)).
- 3MADCVqL534, [Front-End System Design] - Pinterest: cursor paging on pin reads, minimal comment reads (CLAIM(3MADCVqL534@28:35, 3MADCVqL534@30:21)).
- u6jhTo13_No, [Front-End System Design] - Data Table Component: pagination controls as props, page state in the widget (CLAIM(u6jhTo13_No@19:52, u6jhTo13_No@30:46)).
- 9aOXGE7wAZo, [Front-End System Design] - Typeahead Widget: fetched-larger-than-visible paging (CLAIM(9aOXGE7wAZo@18:11)).

## Dated / contestable

- The pagination-over-virtualization call for tables is opinionated. Distiller note (not the author):
  modern data grids routinely virtualize with frozen headers and keyboard nav, so treat his call as
  the "exact page of complex data" case he names, not a universal rule.
  (CLAIM(u6jhTo13_No@30:46))
- Manual chunking with IntersectionObserver is valid but hand-rolled. Distiller note (not the
  author): off-the-shelf virtual list libraries are the modern default for the rendering side.
  (CLAIM(9aOXGE7wAZo@24:41))
