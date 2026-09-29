# internationalization (fesd-a11y-i18n)

Purpose: the i18n readiness of a front-end design (RTL direction, locale formatting, text expansion, locale and time zone as state), honestly marking which parts this corpus teaches and which parts are labeled distiller coverage.

When to load: when the product ships to more than one locale, when user text, dates, numbers, or names render in the UI, and when a review asks "will this survive RTL or longer translations".

## Step checklist
1. Inventory every place the UI renders locale-sensitive output: dates, times, numbers, currency, names, plurals, sorting.
2. Put locale and time zone in client state, store dates as timestamps, convert at render.
3. Check each layout against RTL: no hard-coded left/right, logical properties, mirrored icons where meaning is directional.
4. Budget for text expansion in every fixed-size container (buttons, tabs, badges, table headers).
5. Keep strings out of components (string tables or ICU messages), and design for plurals and interpolation from the start.
6. Separate what the corpus supports (cited laws) from what is distiller guidance, and say so in the record.

## Laws the corpus gives (this stage and adjacent)
- Size in rem, not px, so the UI scales with the user's browser zoom and font settings. consensus; this is the corpus's one sizing law and it also carries the text-scaling half of i18n. CLAIM(3MADCVqL534@50:16, tsGarhpWOws@53:03, u6jhTo13_No@42:14)
- Provide subtitles and make them readable by screen readers: the corpus's only media-localization hook. single-source. CLAIM(Tu-hZ6lqNtY@43:22)
- Use timestamps as the canonical date representation and convert to local time zone at render time. (stage S05) CLAIM(leo1FZ6vu1I@14:29)
- Keep client state minimal but name it precisely: the Calendar design stores selected view, language, and time zone as client state. (stage S05) CLAIM(leo1FZ6vu1I@13:33)
- Keep entities JSON-serializable in both directions so export and import come for free. (stage S02) CLAIM(leo1FZ6vu1I@10:15)

## RTL (direction)
Corpus status: not covered. No episode in this corpus designs a right-to-left layout.

Distiller note (not the author): use logical CSS properties (inline-start and inline-end instead of left and right), mirror directional icons and progress indicators but not symmetric ones, and test the densest surface (tables, calendars) in an RTL locale early. The corpus's grid-role and semantic-table work (CLAIM(fmIiDLbLc_s@41:55), CLAIM(u6jhTo13_No@40:51)) survives direction changes better than div-based layouts, which is an indirect reason to follow those laws.

## Locale formatting (dates, numbers, names, plurals)
Corpus status: partial. Dates as timestamps converted to local time at render is on record CLAIM(leo1FZ6vu1I@14:29); language as client state is on record CLAIM(leo1FZ6vu1I@13:33); everything else is gap.

Distiller note (not the author): format through the platform's locale-aware APIs (Intl-style date, number, and plural formatting) rather than hand-built string templates; never concatenate translated fragments into a sentence; design message catalogs with interpolation and plural rules from the first string. Export and import must stay locale-neutral, which the JSON-serializability law supports CLAIM(leo1FZ6vu1I@10:15).

## Text expansion (and text scaling)
Corpus status: partial. The rem-sizing law is the corpus's real contribution: text and UI must scale with user settings, which is the same flexibility that absorbs longer translations. consensus. CLAIM(3MADCVqL534@50:16, 9aOXGE7wAZo@32:57, 9mjsRrJYOWE@56:57, LEaiGjffLEs@41:44, fmIiDLbLc_s@42:31, lO6GyCvbDm8@26:37, leo1FZ6vu1I@56:09, tsGarhpWOws@53:03, u6jhTo13_No@42:14)

Distiller note (not the author): budget roughly 30 to 40 percent expansion for German- and Finnish-class locales in buttons, tabs, badges, and table headers; avoid fixed heights on text containers; let labels wrap instead of truncating silently. None of this is stated in the corpus.

## Decision table
| i18n question | corpus answer | source |
|---|---|---|
| how are dates stored | timestamps, converted to local time at render | CLAIM(leo1FZ6vu1I@14:29) |
| where does locale live | client state, named alongside view and time zone | CLAIM(leo1FZ6vu1I@13:33) |
| how does export survive locales | entities stay JSON-serializable in both directions | CLAIM(leo1FZ6vu1I@10:15) |
| how does text scale | rem sizing, never px | CLAIM(u6jhTo13_No@42:14, tsGarhpWOws@53:03) |
| how are videos localized | subtitles, readable by screen readers | CLAIM(Tu-hZ6lqNtY@43:22) |
| RTL layout | not covered; use labeled distiller guidance above | gap |
| plural and interpolation rules | not covered; use labeled distiller guidance above | gap |

## Worked cases
- leo1FZ6vu1I: [Front-End System Design] - Google Calendar. The only episode that puts language and time zone in client state and converts dates at render.
- Tu-hZ6lqNtY: [Front-End Product Design] - Netflix. Subtitles as the media-localization hook.
- u6jhTo13_No: [Front-End System Design] - Data Table Component, and tsGarhpWOws: Frontend System Design - Notion-like editor. Rem sizing and text-scaling resilience.

## Dated / contestable
- Distiller note (not the author): the corpus is English-first and its i18n content is one data-model decision plus one media rule; treat everything in the RTL, locale-formatting, and text-expansion sections without a CLAIM as distiller material, not doctrine.
