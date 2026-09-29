# Case: [Front-End System Design] - Design a Poll Widget

Source: https://www.youtube.com/watch?v=lO6GyCvbDm8 (video id lO6GyCvbDm8). Paraphrased distillation; every line cites a CLAIM(<videoId>@mm:ss) timestamp in video lO6GyCvbDm8 against the local transcript.

- published 2021-01-29 / duration 2103s (~35 min) / problem type: component-design (reusable poll widget, framework-agnostic)

## Author's framework as used
1. Follow the standard plan: general requirements, then functional requirements (technical specifics like configuration). CLAIM(lO6GyCvbDm8@01:04)
2. Component architecture: draw the high-level mockup, then the dependency graph to understand the structure. CLAIM(lO6GyCvbDm8@01:23)
3. Skip generic data entities when the deliverable is a component; design the input props instead (product design of the component). CLAIM(lO6GyCvbDm8@01:40)
4. Design the component's own API (methods callers use), then the internal state (not a global store). CLAIM(lO6GyCvbDm8@02:00)
5. Optimization in the three usual buckets, network, rendering, JavaScript. CLAIM(lO6GyCvbDm8@20:08)
6. Accessibility, then extensibility as a closing stage: how the component can be extended from outside. CLAIM(lO6GyCvbDm8@02:40)
7. Finally, walk back through the requirements list to check nothing was dropped (he catches the missing embeddable requirement this way). CLAIM(lO6GyCvbDm8@31:56)

## Worked design
- Requirements: vote/revoke with single or multiple answers; logged-in voting vs read-only results; deep customization (CSS API + custom render functions); npm distribution; embeddable integration, CLAIM(lO6GyCvbDm8@03:08). Functional: all modern browsers across phones, tablets, desktops; custom render functions; configurable options, CSS extensions, callbacks; sync and async modes, CLAIM(lO6GyCvbDm8@06:23).
- Components: PollWidget root with PollTitle, OptionsList, vote/revoke buttons; OptionItem vs ViewItem for edit vs view rendering; consumer may supply their own selectable component, CLAIM(lO6GyCvbDm8@09:47).
- Props: options array, readOnly flag, onVote(option[] => void), renderEditItem(option) => HTMLElement, renderItem(option) => HTMLElement; Option = {votes, order, name}, CLAIM(lO6GyCvbDm8@11:05).
- API: initialize(props) re-renders with fresh props (e.g. after a server update); destroy() tears the widget down, CLAIM(lO6GyCvbDm8@15:21).
- State: mirrored props, root element reference, cached element array for cheap text-only updates; options sorted by their order field, CLAIM(lO6GyCvbDm8@16:23).
- Realtime: none required; updates flow in via new props (caller handles the server call in onVote), CLAIM(lO6GyCvbDm8@11:46).
- Perf: minify + compress + CDN; ES5/ES6 dual bundles; core/theming/utilities module split; DOM reuse instead of re-render; flat CSS selectors; CSS animations; skeletons; event delegation, CLAIM(lO6GyCvbDm8@20:41).
- A11y: rem sizing, keyboard shortcuts, form/input semantics, ARIA labels/descriptions and change announcements, CLAIM(lO6GyCvbDm8@26:37).
- Extensibility: public CSS class hooks (option item, read-only item, title), ES6 class inheritance, render-function overrides, CLAIM(lO6GyCvbDm8@29:55).
- Embedding: a dedicated embed route keyed by poll id, consumable via iframe+script or an Embedly-style provider registry, CLAIM(lO6GyCvbDm8@32:18).

## Trade-offs he names
- Data entities vs props: for a reusable component the "data model" is its prop contract -> design props, not entities. CLAIM(lO6GyCvbDm8@01:40)
- Global store vs local state: the widget only needs its own state -> keep a minimal internal state instead of a store design. CLAIM(lO6GyCvbDm8@02:00)
- Full re-render vs element reuse on prop updates: re-inserting nodes is expensive -> render once, update text in cached elements. CLAIM(lO6GyCvbDm8@22:57)
- Virtualization vs plain list: polls have few options -> no virtualization needed. CLAIM(lO6GyCvbDm8@22:44)
- One universal bundle vs targeted bundles: polyfills cost 40-50KB for nothing on modern targets -> dual ES5/ES6 bundles. CLAIM(lO6GyCvbDm8@21:29)
- Per-option listeners vs delegated listener: N listeners scale worse -> delegate from the root with data attributes. CLAIM(lO6GyCvbDm8@25:26)
- div-based markup vs semantic form/input: divs are simpler but screen-reader hostile -> enforce form/input semantics. CLAIM(lO6GyCvbDm8@27:47)
- iframe embed vs provider service: iframe+setup script for controlled sites, provider registry (Embedly-style JSON) for broad third-party embedding -> offer both. CLAIM(lO6GyCvbDm8@33:31)

## Anti-patterns he warns about
- Stuffing business logic into a display component instead of keeping it a pure view. CLAIM(lO6GyCvbDm8@13:49)
- Re-rendering and inserting new DOM nodes on every props update when you could update cached elements' text. CLAIM(lO6GyCvbDm8@22:57)
- Long, deeply nested CSS selectors that degrade browser performance. CLAIM(lO6GyCvbDm8@23:37)
- Adding Web Workers (or other machinery) when there are no high-cost operations to justify them. CLAIM(lO6GyCvbDm8@25:59)
- Reaching for ARIA before using HTML5 semantics that already carry the meaning. CLAIM(lO6GyCvbDm8@27:47)
- Finishing the design without re-checking it against the stated requirements (he himself forgot embeddability until the check). CLAIM(lO6GyCvbDm8@31:56)

## Dated / contestable
- The framework-agnostic initialize/destroy widget API is a 2021-era vanilla-JS pattern; today's equivalent would be typed framework components (React/Vue) with the same prop/callback shape. CLAIM(lO6GyCvbDm8@15:21)
- "Brotli" appears garbled as "broadly", "BEM" as "beam", "rem" as "ramps" in the transcript; the underlying advice stands. CLAIM(lO6GyCvbDm8@21:03)
- The claim that longer CSS selectors materially hurt performance is contested in modern engines for typical selector depths; the naming-strategy argument is stronger for maintainability than for speed. CLAIM(lO6GyCvbDm8@23:37)
- Embedly-style oEmbed registries still exist but are less central than they were in 2021; a modern answer might name oEmbed or a self-hosted script sandbox. CLAIM(lO6GyCvbDm8@33:31)
- ES5 bundle targeting is much less relevant post-IE11 deprecation. CLAIM(lO6GyCvbDm8@21:29)
