---
name: fesd-a11y-i18n
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Stage S09 (accessibility and internationalization) of the Front-End System Design family: the
  closing a11y pass over a front-end design (keyboard access and shortcuts, focus control, semantic
  HTML before ARIA, screen-reader announcements, color themes for color-blind users, rem sizing,
  alt text, subtitles) plus the i18n readiness of the same design (RTL, locale formatting, text
  expansion, locale and time zone as client state). Produces a per-surface accessibility pass and an
  i18n readiness table. Use when closing a design with an accessibility section, when asked "is this
  screen accessible", "how do I make this keyboard navigable", "what ARIA does this need", "will this
  layout survive RTL or German text", or when an interview asks for the accessibility pass. Cites
  corpus "37 laws from 11 Front-End Engineer videos". JEV-FIRST MANDATE, findable at task start:
  typed judgments in this stage go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED is the
  only answer when the classifier is down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, accessibility, a11y, i18n, aria, keyboard, screen-reader]
outcome: "code-engineering: a design whose accessibility and i18n behavior is specified per surface, not waved through as a checklist word"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-a11y-i18n/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S09"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Accessibility and internationalization (stage S09)

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-a11y-auditor loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate
Typed judgments this stage forces: (1) is this surface keyboard-navigable end to end, with a named focus order; (2) does this markup carry the semantics and ARIA it needs and nothing redundant; (3) will this layout survive zoom, text expansion, and RTL; (4) is this accessibility pass complete enough to call the design done. Send each to Jev first: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Nearest existing rubric: ui.design, advisory until calibrated. A pass needs every required signal above 0.9. Classifier down, erroring or rubric missing = DEFERRED, never a guessed verdict. An advisory PASS is not permission to ship or publish.

## When to use
- The closing accessibility pass of any front-end system design (this author does it last in every full-app episode).
- A review question: "is this screen accessible", "what ARIA does this widget need", "why is this div soup a problem".
- A product question about zoom, font scaling, color-blind themes, subtitles, keyboard shortcuts.
- Any design that will ship to more than one locale, or that renders user text, dates, numbers, or names.

Not the stage for: transport choice (fesd-realtime-sync), rendering cost (fesd-performance), or fixing a live implementation defect (hand off to the estate skill fixing-accessibility).

## Inputs and output contract
Consumes: the mockup or component hierarchy, the data model (which entities carry user text, dates, numbers, media), the interaction list (every action a user can take), and the target device and locale range.

Emits one artifact, the accessibility and i18n pass, with these headings:
1. Keyboard map (every core action, its shortcut, and the tab order across the surface).
2. Focus plan (how overlays open and close focus, where focus lands when content unmounts).
3. Semantics and ARIA inventory (native element chosen per widget; ARIA only where rendering forces generics).
4. Announcements (what changes get announced to screen readers and through which mechanism).
5. Visual access (themes for color-blind users, rem-based sizing, alt text, subtitles).
6. i18n readiness table (RTL behavior, locale formatting of dates/numbers/text, text expansion budget).
7. Known gaps (what this pass does not cover and who owns it).

## Procedure
1. List the core actions and give each one a keyboard path, published as a shortcut list. Load references/accessibility.md. Cite: keyboard shortcuts for the core actions in every full-app design CLAIM(3MADCVqL534@48:52, 5vyKhm2NTfw@45:57, LEaiGjffLEs@42:10); ship the shortcut list with the widget CLAIM(fmIiDLbLc_s@42:47).
2. Design focus explicitly for anything that floats or unmounts: every result keyboard-reachable including list navigation keys CLAIM(9mjsRrJYOWE@56:18, 9mjsRrJYOWE@58:57), and scripted focus control for absolutely-positioned dropdowns, moving focus on once the list ends CLAIM(9mjsRrJYOWE@59:06).
3. Choose native elements first: real form, input, and table tags instead of divs, because HTML is accessible by default CLAIM(tsGarhpWOws@53:38, lO6GyCvbDm8@27:47, u6jhTo13_No@40:51); prefer native accessible elements and add ARIA only where rendering forces generic elements CLAIM(fmIiDLbLc_s@41:37).
4. Add ARIA where the rendering genuinely forces generics: grid, row, and cell roles for interactive grids CLAIM(fmIiDLbLc_s@41:55), grid semantics for a calendar surface CLAIM(leo1FZ6vu1I@56:55), labels and descriptions for columns, cells, and selections CLAIM(u6jhTo13_No@44:09, lO6GyCvbDm8@28:28).
5. Plan announcements: live regions for changing content and the typed value CLAIM(9aOXGE7wAZo@33:31), and mirror the typed value into a real input element so screen readers can announce it CLAIM(9mjsRrJYOWE@58:02). Read the community correction in references/accessibility.md before putting aria-live on any input.
6. Handle media and visuals: alt on every image, optionally vision-generated CLAIM(tsGarhpWOws@54:03), subtitles readable by screen readers CLAIM(Tu-hZ6lqNtY@43:22), alternate color themes for color-blind users CLAIM(5vyKhm2NTfw@45:05, 3MADCVqL534@49:32).
7. Size in rem, never pixels, so user zoom and font settings scale the UI CLAIM(u6jhTo13_No@42:14, tsGarhpWOws@53:03, 9mjsRrJYOWE@56:57).
8. Build the i18n readiness table. Load references/internationalization.md. Locale and time zone belong in client state and dates convert at render CLAIM(leo1FZ6vu1I@14:29); everything else in that file is labeled distiller coverage of gaps this corpus does not teach.
9. Run the known-gaps step: name what the pass does not cover (contrast ratios, testing with real assistive tech, motion safety) and hand off.

## Core laws
Single-author corpus: "consensus" means he repeats the point in 2 or more videos, not that the industry agrees.

Semantics first, ARIA second
- Use semantic HTML elements (real form, input, and table tags) instead of building everything from divs, since HTML is accessible by default. consensus. CLAIM(tsGarhpWOws@53:38, lO6GyCvbDm8@27:47, u6jhTo13_No@40:51, fmIiDLbLc_s@41:37)
- Mark an interactive generic-element grid with grid/row/cell roles so screen readers understand the structure, and mark the calendar as an interactive table with grid semantics. consensus. CLAIM(fmIiDLbLc_s@41:55, leo1FZ6vu1I@56:55)
- Add targeted ARIA (labels, descriptions, announcing the changed selection) where semantics alone are not enough. consensus. CLAIM(lO6GyCvbDm8@28:28, u6jhTo13_No@44:09)

Keyboard and focus
- Provide keyboard shortcuts for the core actions of the surface and publish the shortcut list. consensus. CLAIM(3MADCVqL534@48:52, 5vyKhm2NTfw@45:57, 9aOXGE7wAZo@30:47, LEaiGjffLEs@42:10, lO6GyCvbDm8@27:08, fmIiDLbLc_s@42:47)
- Make every result reachable and navigable by keyboard, including list navigation keys. single-source. CLAIM(9mjsRrJYOWE@56:18, 9mjsRrJYOWE@58:57)
- Script explicit focus control for the absolutely-positioned dropdown, including moving focus on to the next input once the list ends. single-source. CLAIM(9mjsRrJYOWE@59:06)
- Rely on the table element's default keyboard navigation, help users move between rows and columns, and add search and filter shortcuts. single-source. CLAIM(u6jhTo13_No@42:46)

Screen readers
- Announce the typed query and changing content through live regions, and mirror the typed value into a real input element so screen readers announce it; use divs for structure only, never as the description of content. consensus. CLAIM(9aOXGE7wAZo@33:31, 9mjsRrJYOWE@58:02, LEaiGjffLEs@42:54)
- Give every image an alt attribute, optionally generated by vision models. consensus. CLAIM(tsGarhpWOws@54:03, 5vyKhm2NTfw@45:19)
- Provide subtitles and make them readable by screen readers. single-source. CLAIM(Tu-hZ6lqNtY@43:22)

Visual access
- Offer alternate color schemes and themes that work for color-blind users and users with visual disabilities. consensus. CLAIM(3MADCVqL534@49:32, 5vyKhm2NTfw@45:05, LEaiGjffLEs@42:54, Tu-hZ6lqNtY@43:46, leo1FZ6vu1I@56:09, tsGarhpWOws@52:07)
- Size in rem (scalable units), not pixels, so the UI tracks the user's browser zoom and font settings. consensus. CLAIM(3MADCVqL534@50:16, 9aOXGE7wAZo@32:57, 9mjsRrJYOWE@56:57, LEaiGjffLEs@41:44, Tu-hZ6lqNtY@44:39, fmIiDLbLc_s@42:31, lO6GyCvbDm8@26:37, leo1FZ6vu1I@56:09, tsGarhpWOws@53:03, u6jhTo13_No@42:14)

## Sub-skills
| sub-skill | file | load when |
|---|---|---|
| accessibility | references/accessibility.md | every S09 job; keyboard, focus, ARIA, color, announcements, plus the labeled community correction on aria-live |
| internationalization | references/internationalization.md | the product ships to more than one locale or renders locale-sensitive text, dates, numbers, or direction |

## Decision tables
| question | pick | when | cite |
|---|---|---|---|
| native element or ARIA-built widget | native | any time a real form, input, table, or button fits | CLAIM(tsGarhpWOws@53:38, fmIiDLbLc_s@41:37) |
| ARIA or nothing | ARIA | rendering forces generic elements (canvas-like grids, custom lists) | CLAIM(fmIiDLbLc_s@41:55, leo1FZ6vu1I@56:55) |
| announce or stay quiet | announce | the change matters to a user who cannot see it (results, selections, new content) | CLAIM(9aOXGE7wAZo@33:31, lO6GyCvbDm8@28:28) |
| aria-live on every input | no | put it on the regions that change, not on all form controls | community correction, references/accessibility.md |
| px or rem | rem | always; user zoom and font settings must scale the UI | CLAIM(u6jhTo13_No@42:14, tsGarhpWOws@53:03) |
| subtitles optional or required | required | any video content the product ships | CLAIM(Tu-hZ6lqNtY@43:22) |

## Anti-patterns
- Building UI from divs when semantic tags exist: it breaks default accessibility. CLAIM(tsGarhpWOws@53:38)
- Adding ARIA attributes when HTML5 semantics already cover it. CLAIM(fmIiDLbLc_s@41:23)
- Pixel-based sizing that ignores user browser settings. CLAIM(leo1FZ6vu1I@56:09, u6jhTo13_No@42:14)
- Relying on divs to describe content to screen readers instead of mirroring values into real inputs. CLAIM(9mjsRrJYOWE@58:02)
- Shipping a widget with no keyboard path and no shortcut list. CLAIM(9mjsRrJYOWE@56:18, fmIiDLbLc_s@42:47)
- Unmanaged focus on an absolutely-positioned overlay. CLAIM(9mjsRrJYOWE@59:06)

## Worked cases
- 3MADCVqL534: [Front-End System Design] - Pinterest. Keyboard shortcuts, color themes, rem sizing, aria-live on live fields.
- 5vyKhm2NTfw: [Front End System Design] - Facebook News Feed. The closing accessibility pass: themes, announcements, hotkeys.
- 9aOXGE7wAZo: [Front-End System Design] - Typeahead Widget. Keyboard open/close shortcuts, live-region announcement of the typed query.
- 9mjsRrJYOWE: Typeahead component - front-end system design. The deepest keyboard and focus treatment in the corpus (list keys, focus hand-off, input mirroring).
- LEaiGjffLEs: [Front-End System Design] - Chat application. Navigation shortcuts, themes, active-field announcements.
- Tu-hZ6lqNtY: [Front-End Product Design] - Netflix. Subtitles for screen readers, color schemes, media-heavy surface.
- fmIiDLbLc_s: [Front-End System Design] - Google Sheets. Native elements first, grid roles for a custom grid, shortcut list; he flags spreadsheet a11y as hard.
- lO6GyCvbDm8: [Front-End System Design] - Design a Poll Widget. HTML5 semantics plus targeted ARIA on a small widget.
- leo1FZ6vu1I: [Front-End System Design] - Google Calendar. Grid semantics on an interactive calendar surface.
- tsGarhpWOws: Frontend System Design - Notion-like editor. Semantic tags, alt text (vision-model aside), themes.
- u6jhTo13_No: [Front-End System Design] - Data Table Component. Real table markup for screen readers and SEO, aria-label on columns and cells.

## Dated / contestable
- The 2020 advice to mark inputs and textareas with aria-live is contested by the community. Distiller note, community correction (not the author): the top-voted correction on 5vyKhm2NTfw points out that aria-live should not be put on all inputs; live regions belong on the content that changes, and putting them on every form control makes screen readers noisy and slow. See references/accessibility.md. CLAIM(5vyKhm2NTfw@45:19)
- Vision models generating alt text is an aside, not a designed pipeline; treat generated alt as unverified until reviewed. Distiller note (not the author). CLAIM(tsGarhpWOws@54:03)
- This corpus almost never quotes WCAG numbers. Distiller note (not the author): contrast ratios, target sizes, and status-role announcements come from WCAG and the estate skill fixing-accessibility, not from these videos.
- i18n coverage in the corpus is thin (locale and time zone as client state, subtitles). Distiller note (not the author): RTL and text-expansion practice in references/internationalization.md is labeled distiller material.

## Hand-off
- Hand off implementation-level audits and fixes to the estate skill fixing-accessibility; this stage specifies behavior, that skill repairs real markup and proves it with cited checks.
- Adjacent estate skills: app-web-frontend for build slices; fixing-motion-performance when animated UI must stay perceivable; app-ui-design for the design lane that consumes this pass.
- Family neighbors: fesd-performance takes the same surface and prices its cost; fesd-component-api owns UX and product states; the accessibility pass should run after the component and state design it audits.
