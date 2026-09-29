# UX states (S11 sub-skill)

Purpose: specify the user-facing states of a widget or page (loading, empty, error, optimistic) and the product-level feature trade-offs the author actually states, with an honest gap list where the corpus is silent.

When to load: whenever the design must say what the user sees while data is missing, slow, wrong, or being written.

## Step checklist

1. Design the loading state first: skeletons, loaders, and placeholders so a slow load still feels fast. CLAIM(9aOXGE7wAZo@27:24)
2. Apply the same rule at the page level: show placeholders while server data loads; perceived load time drops even when actual time does not. CLAIM(u6jhTo13_No@34:26)
3. Never render an empty shell where a placeholder bucket can carry the shape (example: placeholder buckets while coarser data upsamples). CLAIM(HR2jXy_wPg4@44:19)
4. Treat extensibility as a design stage of its own, not a footnote: CSS API classes, class-based inheritance, render hooks. CLAIM(lO6GyCvbDm8@29:55)
5. Name the three extensibility surfaces explicitly: a CSS API, custom render functions, and class inheritance. CLAIM(u6jhTo13_No@39:44)
6. Add product-level coordination as a feature on top of independent widgets: charts synchronized through selectable parameters (interval, symbol). CLAIM(HR2jXy_wPg4@01:22)
7. Bridge web features to native capabilities through web push or deep links, and state the dependency: both need user consent or target-app support. CLAIM(leo1FZ6vu1I@49:20)
8. For write paths, say who owns the optimistic decision: the widget emits the callback and the caller decides local mutation vs a server call. CLAIM(lO6GyCvbDm8@11:46)

## Laws for this sub-topic (the S11 set)

- Skeletons, loaders, placeholders for perceived speed. CLAIM(9aOXGE7wAZo@27:24) consensus (u6jhTo13_No@34:26 says the same for tables).
- Placeholders on slow server data: perceived load time is its own metric. CLAIM(u6jhTo13_No@34:26) consensus.
- Extensibility as its own design stage (CSS API classes, class inheritance, render hooks). CLAIM(lO6GyCvbDm8@29:55) consensus (u6jhTo13_No@39:44 names the same three surfaces).
- Extensibility = three named surfaces: CSS API, custom column render functions, ES6 class inheritance. CLAIM(u6jhTo13_No@39:44) consensus.
- Product-level sync as a feature layered on independent widgets (selectable parameters propagated). CLAIM(HR2jXy_wPg4@01:22) single-source.
- Native capability bridging through web push or deep links, both gated on consent or app support. CLAIM(leo1FZ6vu1I@49:20) single-source.

## What the corpus covers vs not (coverage honesty)

- Loading: covered (skeletons, loaders, placeholders). CLAIM(9aOXGE7wAZo@27:24)
- Empty: covered only in its anti-form (never show a bare empty shell when a placeholder can hold the shape). CLAIM(HR2jXy_wPg4@44:19) Distiller note (not the author): a dedicated empty-state design (first-run content, no-results copy) is not in this corpus.
- Error: not covered. No error-state or retry law appears in these videos. Distiller note (not the author): answer error states from first principles or another doctrine.
- Optimistic UI: not named as such. The closest statements are the caller-decides-mutation-policy callback, CLAIM(lO6GyCvbDm8@11:46) and the read-only mode for unauthenticated users. CLAIM(lO6GyCvbDm8@03:47)

## Decision tables

| State question | Pick | Citation |
|---|---|---|
| Loader spinner vs skeleton | Skeleton / placeholder carrying the content shape | CLAIM(9aOXGE7wAZo@27:24) CLAIM(u6jhTo13_No@34:26) |
| Empty shell vs placeholder buckets while data is coarse | Placeholder buckets | CLAIM(HR2jXy_wPg4@44:19) |
| Optimistic local update vs wait for server | Caller's policy, widget only emits the callback | CLAIM(lO6GyCvbDm8@11:46) |
| Restyle via CSS API vs fork | CSS API / render hooks / inheritance as declared surfaces | CLAIM(u6jhTo13_No@39:44) |
| Web push vs deep link for native bridging | Offer both; both need consent or app support | CLAIM(leo1FZ6vu1I@49:20) |
| Independent widgets vs synced | Independent, with selectable parameters as the sync feature | CLAIM(HR2jXy_wPg4@01:22) |

## Worked cases

- 9aOXGE7wAZo "Typeahead Widget": placeholders as a named performance column.
- u6jhTo13_No "Data Table Component": perceived load time, and extensibility named as three surfaces.
- lO6GyCvbDm8 "Poll Widget": extensibility as its own design stage; read-only mode for non-voters.
- HR2jXy_wPg4 "Financial Dashboard": chart sync as a product feature; placeholder buckets during upsampling.
- leo1FZ6vu1I "Google Calendar": web-to-native reminder bridging and its consent constraints.
