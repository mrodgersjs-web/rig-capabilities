# accessibility (fesd-a11y-i18n)

Purpose: the full accessibility law set for this stage (keyboard, focus, semantics and ARIA, announcements, color, sizing, media) with the labeled community correction on aria-live.

When to load: at the start of every S09 job, when a widget needs an ARIA decision, and when a review claims a screen is "accessible".

## Step checklist
1. Enumerate every core action and give it a keyboard path; write the shortcut list the product will ship.
2. Walk the tab order surface by surface; name where focus enters overlays and where it goes when they close.
3. Choose the native element for each widget before considering ARIA.
4. Mark only the generic-element widgets with ARIA roles (grids, custom lists), and describe columns, cells, and selections where semantics fall short.
5. Decide what gets announced to screen readers and by which mechanism; read the community correction below before touching aria-live.
6. Give every image alt text and every video subtitles.
7. Provide a color theme that works for color-blind users.
8. Convert all sizing to rem or scalable units.

## Laws

Keyboard and focus
- Provide keyboard shortcuts for the core actions (add pin, jump to top/bottom, share, like, quick menu, help). consensus. CLAIM(3MADCVqL534@48:52)
- Add hotkeys for core actions (create/post story, scroll, help, return to main menu). consensus. CLAIM(5vyKhm2NTfw@45:57)
- Provide keyboard access: a quick shortcut to open search, tab navigation across items, and a close shortcut. consensus. CLAIM(9aOXGE7wAZo@30:47)
- Provide keyboard shortcuts for the core navigation and actions (move between contacts, search, attach, help). consensus. CLAIM(LEaiGjffLEs@42:10)
- Provide keyboard shortcuts: tab between options, vote/revoke, reveal results. consensus. CLAIM(lO6GyCvbDm8@27:08)
- Ship a keyboard shortcut list and search for grid navigation. consensus. CLAIM(fmIiDLbLc_s@42:47)
- Offer color schemes for color-blind users and keyboard shortcuts for navigation, search, opening movies/descriptions, menu, and help. consensus (the color half also appears under Visual access). CLAIM(Tu-hZ6lqNtY@43:46)
- Avoid pixel sizing, add hotkeys for period navigation, search and help, and offer color schemes for color-blind users. consensus (this one source sentence covers sizing, keyboard, and color; its citations appear in each section it supports). CLAIM(leo1FZ6vu1I@56:09)
- Make every result reachable and navigable by keyboard, including list navigation keys. single-source. CLAIM(9mjsRrJYOWE@56:18, 9mjsRrJYOWE@58:57)
- Script explicit focus control for the absolutely-positioned dropdown, including moving focus on to the next input once the list ends. single-source. CLAIM(9mjsRrJYOWE@59:06)
- Rely on the table element's default keyboard navigation and help users move between rows and columns; add search and filter shortcuts. single-source. CLAIM(u6jhTo13_No@42:46)

Semantics first
- Use semantic HTML elements (real table and input tags) instead of building everything from divs, since HTML is accessible by default. consensus. CLAIM(tsGarhpWOws@53:38)
- Use HTML5 semantics (form and input elements, not divs) for screen-reader friendliness and SEO. consensus. CLAIM(lO6GyCvbDm8@27:47)
- Use real table markup, not divs: HTML5 table semantics buy SEO (Google parses column data for result previews) and screen-reader support with less ARIA. consensus. CLAIM(u6jhTo13_No@40:51)
- Prefer native accessible elements and add ARIA roles only where rendering forces generic elements. consensus. CLAIM(fmIiDLbLc_s@41:37)

ARIA where rendering forces it
- Mark an interactive generic-element grid with grid/row/cell roles so screen readers understand the structure. consensus. CLAIM(fmIiDLbLc_s@41:55)
- Mark the interactive calendar with grid semantics so screen readers know it is an interactive table, and rely on HTML5 semantics first. consensus. CLAIM(leo1FZ6vu1I@56:55)
- Add role attributes when markup semantics are insufficient. single-source (this source sentence also covers live-region announcement; its citation appears in both sections). CLAIM(9aOXGE7wAZo@33:31)
- Add targeted ARIA (labels, descriptions, announcing the changed selection) where semantics alone are not enough. consensus (the announcing half also appears under Announcements). CLAIM(lO6GyCvbDm8@28:28)
- Describe columns and cells with aria-label and aria-description where semantics fall short. consensus. CLAIM(u6jhTo13_No@44:09)
- Provide color schemes for users with visual disabilities and component-specific ARIA attributes per use case (e.g. tables). consensus (this source sentence covers color and ARIA). CLAIM(tsGarhpWOws@52:07)

Announcements and screen readers
- Mark inputs and textareas with aria-live and images with alt text so screen readers announce content changes. consensus, but see the community correction below before applying the aria-live half. CLAIM(5vyKhm2NTfw@45:19)
- Announce the typed query to screen readers via a live region, and add role attributes when markup semantics are insufficient. consensus. CLAIM(9aOXGE7wAZo@33:31)
- Mirror the typed value into a real input element so screen readers announce it, and use divs for structure only, never as the description of content. single-source. CLAIM(9mjsRrJYOWE@58:02)
- Offer color themes that work for color-blind users and announce active fields to screen readers. consensus (the color half also appears under Visual access). CLAIM(LEaiGjffLEs@42:54)
- Offer alternate color themes for color-blind users and mark live fields with aria-live for screen readers. consensus (same split as above). CLAIM(3MADCVqL534@49:32)
- Size the UI in rem so browser zoom settings scale everything consistently, and announce inputs with aria-live. consensus (this source sentence covers sizing and announcements). CLAIM(Tu-hZ6lqNtY@44:39)

Visual access and media
- Provide alternate color schemes so color-blind users can use the site. consensus. CLAIM(5vyKhm2NTfw@45:05)
- Give every image an alt attribute, optionally generated by vision models. consensus. CLAIM(tsGarhpWOws@54:03)
- Provide subtitles and make them readable by screen readers. single-source. CLAIM(Tu-hZ6lqNtY@43:22)

Sizing
- Size text in rem, not px, so it scales with the user's browser zoom settings. consensus. CLAIM(3MADCVqL534@50:16, 9aOXGE7wAZo@32:57, 9mjsRrJYOWE@56:57, LEaiGjffLEs@41:44, fmIiDLbLc_s@42:31, lO6GyCvbDm8@26:37, tsGarhpWOws@53:03, u6jhTo13_No@42:14)

## Community correction (not the author)
Labeled: community correction, top-voted comment on 5vyKhm2NTfw. The episode's a11y pass says to mark inputs and textareas with aria-live (CLAIM(5vyKhm2NTfw@45:19)). The top-voted correction on that video says aria-live should not be put on all inputs: live regions belong on the containers whose content changes (results list, status area, selection summary), and putting them on every form control makes screen readers announce keystrokes and noise, which is worse than silence. Apply the law's intent (changes get announced) through targeted live regions, and keep the mirror-into-a-real-input technique (CLAIM(9mjsRrJYOWE@58:02)) for typed values. This note is the community's correction, not Evgenii Ray's position.

## Decision table
| widget | native element | ARIA added | keyboard | announce | cite |
|---|---|---|---|---|---|
| form field | input / textarea / select | none if the label element exists | native tab order | typed value via real input | CLAIM(tsGarhpWOws@53:38, 9mjsRrJYOWE@58:02) |
| data table | table / thead / td | aria-label or aria-description per column when needed | default table navigation plus row/column help | row changes if they matter | CLAIM(u6jhTo13_No@40:51, u6jhTo13_No@42:46, u6jhTo13_No@44:09) |
| custom grid (spreadsheet-like) | none; generics forced | grid, row, cell | shortcut list plus search | selection changes | CLAIM(fmIiDLbLc_s@41:55, fmIiDLbLc_s@42:47) |
| calendar surface | none; generics forced | grid semantics | period navigation hotkeys | date selection | CLAIM(leo1FZ6vu1I@56:55, leo1FZ6vu1I@56:09) |
| autocomplete list | input plus list structure | roles where markup is insufficient | list navigation keys, focus hand-off at list end | typed query via live region | CLAIM(9aOXGE7wAZo@33:31, 9mjsRrJYOWE@56:18, 9mjsRrJYOWE@59:06) |
| poll widget | form and input elements | labels, descriptions | tab, vote/revoke, reveal | changed selection | CLAIM(lO6GyCvbDm8@27:47, lO6GyCvbDm8@28:28) |
| image | img | alt attribute | n/a | alt text read aloud | CLAIM(tsGarhpWOws@54:03) |
| video | video with subtitles | subtitles track | n/a | subtitles readable by screen readers | CLAIM(Tu-hZ6lqNtY@43:22) |

Theme and sizing decision:

| question | answer | cite |
|---|---|---|
| default theme enough? | no; ship at least one color-blind-friendly theme | CLAIM(5vyKhm2NTfw@45:05, 3MADCVqL534@49:32) |
| px sizing acceptable? | no; rem or scalable units only | CLAIM(u6jhTo13_No@42:14, tsGarhpWOws@53:03) |
| contrast ratios? | not covered by this corpus; use WCAG and fixing-accessibility | distiller note |

## Worked cases
- 9mjsRrJYOWE: Typeahead component - front-end system design. Best keyboard and focus treatment in the corpus.
- u6jhTo13_No: [Front-End System Design] - Data Table Component. Real table semantics plus targeted ARIA.
- fmIiDLbLc_s: [Front-End System Design] - Google Sheets. Native-first, grid roles, shortcut list.
- 5vyKhm2NTfw: [Front End System Design] - Facebook News Feed. The closing a11y pass the community corrected.
- Tu-hZ6lqNtY: [Front-End Product Design] - Netflix. Subtitles and themes on a media surface.
- 3MADCVqL534, 9aOXGE7wAZo, LEaiGjffLEs, lO6GyCvbDm8, leo1FZ6vu1I, tsGarhpWOws: the remaining surfaces each contribute shortcuts, themes, semantics, or alt text as cited above.

## Dated / contestable
- aria-live on inputs (2020). Community correction above. CLAIM(5vyKhm2NTfw@45:19)
- Vision-generated alt text presented as an aside. Distiller note (not the author): generated alt needs human review before it ships. CLAIM(tsGarhpWOws@54:03)
- Distiller note (not the author): this corpus names no WCAG success criterion and no measured contrast ratio; if the deliverable needs conformance language, source it from WCAG and the fixing-accessibility skill, and say that these videos did not supply it.
