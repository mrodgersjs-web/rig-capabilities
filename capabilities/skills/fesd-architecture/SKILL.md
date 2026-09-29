---
name: fesd-architecture
description: >-
  JEV-FIRST MANDATE, findable at task start and binding before any work: typed judgments go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED when the classifier is down, never a guessed verdict. Owns stage S03 (architecture) of the Front-End System Design family: the ordered design plan, the
  high-level box diagram, the rendering-engine decision (canvas vs DOM), the CSR/SSR/SPA call, the
  architecture-variant classification for reusable widgets, page-inventory planning for product
  designs, multi-window roles, and distribution/embedding boundaries. Use when a front-end design
  round needs its high-level structure decided before any component API: trigger phrases include
  "draw the architecture", "how should this app be structured", "canvas or DOM", "which rendering
  strategy", "how do the windows talk", "how is the widget shipped". Distilled from 23 laws in 9
  Front-End Engineer videos (Evgenii Ray). JEV-FIRST MANDATE, findable at task start: typed
  judgments in this stage go to rig-s1gate (Jev) BEFORE any frontier LLM call; DEFERRED is the only
  answer when the classifier is down. Child of fe-system-design-os.
owner: rig-intelligence
domain: Engineering / Front-end system design
status: Stable
acl: internal
tags: [frontend, system-design, architecture, rendering, component-architecture]
outcome: "code-engineering: a cited architecture section (plan order, box diagram, rendering decision, distribution boundary) ready for component design"
done_when:
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/claims_check.py capabilities/skills/fesd-architecture/SKILL.md
  - cmd:python3 capabilities/skills/fe-system-design-os/scripts/check_family.py
quality_floor: 0.6
metadata:
  parent: fe-system-design-os
  stage: "S03"
  corpus: "data/corpora/frontend-engineer/manifest.jsonl"
---

# Architecture (S03): high-level components, layering, rendering choice

JEV FIRST, and it binds every task under this skill: an agent whose only context is this
excerpt sends semantic triage, routing, and classification to the rig-s1gate Jev path BEFORE any
frontier LLM call (`~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`).
When the fast classifier is unavailable: DEFER, never guess a verdict locally. A required signal
passes only above 0.9; below that the step does not advance.

## Load surface

This skill is an always-loaded task-start surface, not a deep reference an agent must already know about:
the `fe-system-design-os` meta-skill (loaded first by `/fesd` and routed to by `when-shipping-code`)
names it in its routes and org chart, and fesd-architect loads it before its first action. All paths
are relative to the canonical repo `~/Developer/rig-capabilities`.

## JEV-first mandate

Typed judgments this stage forces, routed to Jev before any frontier LLM call:
1. Is this requirement list complete enough to design the architecture against (nothing promised is left undesigned)?
2. Which architecture variant does this reusable component fall into (stateless / stateful-static / hybrid)?
3. Does the rendering-engine choice (canvas vs DOM) follow from the product's resource profile?
4. Is the box decomposition sound: right layers, right single owner of state writes?

Command shape: `~/.rig/bin/rig-s1gate check <rubric> --file <artifact> --subject "<kind> <id> sha256:<hash>" --json`. Nearest existing rubric: app.stack, advisory until calibrated. A pass needs every required signal above 0.9. Classifier down, erroring, or rubric missing = DEFERRED, never a guessed verdict. An advisory PASS is not permission to ship or publish.

## When to use

- After requirements are settled and before any props, entities, or store design.
- When the interviewer (or a build) asks for the high-level design, the diagram, or the technology choice.
- For any reusable-widget question: the variant classification here decides the whole downstream API.
- Not for deep component API work (that is fesd-component-api) or state/data modeling (S05).

## Inputs and output contract

Consumes: the S02 requirements artifact (functional and non-functional requirements, scope and assumptions) for the named problem.

Emits an architecture section with these headings:
1. Design order (the plan steps, written before designing).
2. Rendering decision: engine (canvas vs DOM) and delivery shape (CSR / SSR pre-render / SPA), each with its resource argument.
3. Box diagram: application route, router, page route, page content, view components, controller/store, API client, cache; for canvases the named layers.
4. Architecture variant (reusable components only), with the condition that justifies it.
5. Page inventory and designed-page subset (product designs only).
6. Distribution and embedding boundary (npm package, embed route, iframe or provider path).
7. Multi-window roles if the problem spans windows (single writer named).

## Procedure

1. Write the design order before any design talk: requirements, components, entities, API, store, flagship feature, optimization, accessibility. CLAIM(5vyKhm2NTfw@01:28) Load references/component-architecture-diagram.md.
2. Decide the rendering engine first, because it rewrites every downstream decision. CLAIM(fmIiDLbLc_s@07:35) Apply the resource rule: canvas only for mass-market products with real engineering resources; DOM for internal or cost-sensitive builds. CLAIM(fmIiDLbLc_s@11:08) Load references/rendering-strategy.md.
3. Product designs: assume the shared design system (typography, primitives, grid, common components), CLAIM(Tu-hZ6lqNtY@07:44) enumerate the page inventory, design only key-flow pages, CLAIM(Tu-hZ6lqNtY@08:40) treat the sign-up page as first-class because it converts, CLAIM(Tu-hZ6lqNtY@08:55) and show structural reuse between pages instead of drawing a second page. CLAIM(Tu-hZ6lqNtY@14:42)
4. Reusable components: classify the use case into one of three architecture variants before designing anything else. CLAIM(9mjsRrJYOWE@06:20) Default to stateless (roughly nine of ten cases); CLAIM(9mjsRrJYOWE@15:03) take stateful/static only for a small, rarely changing vocabulary; CLAIM(9mjsRrJYOWE@12:00) take hybrid only when an unchangeable slow API forces client caching, and name the cache complexity it costs. CLAIM(9mjsRrJYOWE@13:31)
5. Draw the box diagram top-down: application route, router, page route, page content, then widget detail. CLAIM(tsGarhpWOws@08:47) For a reconfigurable 2D layout choose CSS grid over flexbox, CLAIM(HR2jXy_wPg4@07:48) and separate the canvas into grid container, draggable-cell layer, and a content layer spanned onto the grid. CLAIM(HR2jXy_wPg4@16:55)
6. Multi-window problems: name one host window that owns all state writes and fetching, with other windows as extensions. CLAIM(HR2jXy_wPg4@57:01) Discover roles through shared localStorage (host id plus extension id array), CLAIM(HR2jXy_wPg4@57:42) and pass structured events between windows over BroadcastChannel. CLAIM(HR2jXy_wPg4@58:58)
7. Set the distribution boundary: ship reusable widgets as an npm package so no single application owns them, CLAIM(9aOXGE7wAZo@35:04) and decide embedding early: a dedicated route keyed by an id that fetches and renders, CLAIM(lO6GyCvbDm8@32:18) offered as iframe-plus-setup-script and/or a provider service with a JSON description. CLAIM(lO6GyCvbDm8@33:31) Detail lives in the widget-embedding sub-skill of fesd-component-api.
8. Close with the AI-era stance when the build will use generated code: own the architecture and engineer the spec, then let AI execute in fast iterations, CLAIM(v4Dt4FalMOA@41:31) and accept generated code only under supervision with good requirements. CLAIM(v4Dt4FalMOA@40:14)
9. Hand the section to component design (fesd-component-api) or state/data design (S05) per the problem class.

## Core laws

Design order and diagram
- Write the design order first (requirements, components, entities, API, store, flagship feature, optimization, accessibility) and work it in order. CLAIM(5vyKhm2NTfw@01:28) consensus (the same plan skeleton runs in 9mjsRrJYOWE@01:14, u6jhTo13_No@01:06, lO6GyCvbDm8@01:04).
- Start the component schema at the application route and descend through router, page route, and page content before any widget detail. CLAIM(tsGarhpWOws@08:47) single-source.
- Prefer a single-page application shape when selecting an item on one side must instantly render content in the center. CLAIM(tsGarhpWOws@09:48) single-source (stated as implied).

Rendering choice
- Decide the rendering engine (canvas vs DOM) before component and data design, because the choice rewrites the whole downstream design. CLAIM(fmIiDLbLc_s@07:35) single-source.
- Choose canvas only for mass-market products with large engineering resources; choose DOM for internal or cost-sensitive builds. CLAIM(fmIiDLbLc_s@11:08) single-source.

Architecture variants (reusable components)
- Classify the use case into one of three architecture variants before designing anything else. CLAIM(9mjsRrJYOWE@06:20) single-source (his own taxonomy).
- Default to the stateless variant driven by an external controller (about nine cases in ten); use stateful/static only for a small, rarely changing vocabulary searchable locally; use hybrid only when a slow legacy API you cannot change forces client-side caching. CLAIM(9mjsRrJYOWE@15:03) CLAIM(9mjsRrJYOWE@12:00) CLAIM(9mjsRrJYOWE@13:31) single-source.

Product page architecture
- For a large multi-team application, start from an assumed shared design system, then enumerate the whole page inventory and design only the pages carrying key flows. CLAIM(Tu-hZ6lqNtY@07:44) CLAIM(Tu-hZ6lqNtY@08:40) single-source.
- Treat the acquisition (sign up) page as first-class, because that is where users convert. CLAIM(Tu-hZ6lqNtY@08:55) single-source.

Multi-window
- Designate one host window that owns all state writes and data fetching with the other windows as extensions; discover roles through shared localStorage; pass structured events (name, payload, source) over BroadcastChannel rather than a custom channel. CLAIM(HR2jXy_wPg4@57:01) CLAIM(HR2jXy_wPg4@57:42) CLAIM(HR2jXy_wPg4@58:58) single-source.

Distribution boundary
- Ship the reusable widget as an npm package so it stays decoupled from any single application. CLAIM(9aOXGE7wAZo@35:04) consensus (lO6GyCvbDm8@05:08 makes npm distribution a stated requirement).
- Serve embedding through an application route that takes an id, fetches the data, and renders the widget; offer two embedding paths: iframe with a setup script, or a provider service with a JSON description. CLAIM(lO6GyCvbDm8@32:18) CLAIM(lO6GyCvbDm8@33:31) single-source.

AI-era architecture ownership
- Own the architecture and engineer the spec yourself, then let AI execute in fast iterations; accept generated code only when you supervise it and feed it good requirements. CLAIM(v4Dt4FalMOA@41:31) CLAIM(v4Dt4FalMOA@40:14) single-source.

## Sub-skills

| Sub-skill | File | Load when |
|---|---|---|
| Component architecture diagram | references/component-architecture-diagram.md | You must draw or judge the high-level box diagram, the layer split, page inventory, or multi-window roles |
| Rendering strategy | references/rendering-strategy.md | You must choose canvas vs DOM, CSR vs SSR pre-render vs SPA, or state the AI-era architecture stance |

## Decision tables

Rendering engine (CLAIM(fmIiDLbLc_s@08:16), CLAIM(fmIiDLbLc_s@11:08))
| Option | Pick when | Cost |
|---|---|---|
| Canvas | Mass-market product, large engineering resources, FPS and memory are the product | Own a primitive library, specialized skills, and a mixed DOM layer for accessibility |
| DOM | Internal tool or cost-sensitive build where development cost dominates | CPU/memory load, two-axis virtualization is hard |

Architecture variant (CLAIM(9mjsRrJYOWE@15:03), CLAIM(9mjsRrJYOWE@12:00), CLAIM(9mjsRrJYOWE@13:31))
| Variant | Pick when | Cost |
|---|---|---|
| Stateless (host-driven) | Reusable component with an external controller; default | Host owns search logic; query callback mandatory |
| Stateful / static | Small, rarely changing vocabulary searched locally | Caps dataset size |
| Hybrid (client cache) | Slow legacy API you cannot change | Cache TTL, eviction, invalidation work |

Delivery shape (CLAIM(Tu-hZ6lqNtY@38:15), CLAIM(5vyKhm2NTfw@38:24), CLAIM(LEaiGjffLEs@38:50), CLAIM(tsGarhpWOws@09:48))
| Shape | Pick when |
|---|---|
| SSR pre-render of clean HTML | The page is the conversion surface and first paint decides (sign up) |
| SSR pre-render of some feed pages | Time-to-first-content is the metric for consumption content |
| Client render | An app is interaction-heavy and the extra server-render infrastructure does not pay off (chat) |
| SPA with instant pane swaps | Selection in one pane must render another pane immediately (editor) |

Embedding path (CLAIM(lO6GyCvbDm8@33:31))
| Path | Pick when |
|---|---|
| iframe + setup script | You control or semi-control the host page |
| Provider service (oEmbed-style JSON registry) | Broad third-party embedding is the goal |

## Anti-patterns

- Drawing detailed diagrams during the round instead of spending the time on decisions. CLAIM(fmIiDLbLc_s@12:14)
- Trying to design every page of a large application in one sitting. CLAIM(Tu-hZ6lqNtY@09:02)
- Deep-diving one component's internals in a product-design round where the whole-app view is scored. CLAIM(Tu-hZ6lqNtY@13:30)
- Designing before asking about platforms and browsers. CLAIM(3MADCVqL534@01:38)
- Letting multiple windows write application state; extensions must be read-only replicas of one writer. CLAIM(HR2jXy_wPg4@60:03)
- Prompt-and-hope generation ("just do it well") with no architecture or spec behind it. CLAIM(v4Dt4FalMOA@41:31)
- Accepting piles of generated code from unsupervised, non-engineering authors because it looks fine visually. CLAIM(v4Dt4FalMOA@40:14)
- Adding network optimization overhead to an application that is meant to run offline. CLAIM(fmIiDLbLc_s@41:04)

## Worked cases

| Video | Title | Steal this |
|---|---|---|
| fmIiDLbLc_s | Google Sheets | The rendering-engine elimination: count elements, bound one axis, virtualize the other; canvas-vs-DOM resource argument |
| 9mjsRrJYOWE | Typeahead component | The three-variant classification and its default (stateless) |
| HR2jXy_wPg4 | Financial Dashboard / TradingView | Three-layer grid canvas, single-writer multi-window design, BroadcastChannel event shape |
| Tu-hZ6lqNtY | Netflix (product design) | Design-system precondition, page inventory with a designed subset, sign-up as the performance-critical page |
| tsGarhpWOws | Notion-like editor | Top-down schema descent from app route, SPA shape justification |
| lO6GyCvbDm8 | Poll Widget | Embed route plus iframe/provider embedding paths |
| 5vyKhm2NTfw | Facebook News Feed | The canonical design order; SSR pre-render of some feed pages |
| LEaiGjffLEs | Chat application | The counter-case: skipping SSR because the infrastructure does not pay off |
| v4Dt4FalMOA | FAANG engineer podcast | AI-era stance: architecture and spec are yours; generation is execution |

## Dated / contestable

- Provider-registry embedding (Embedly-style oEmbed) named as one of the two paths is less central in 2026 than it was in 2021. Distiller note (not the author): a modern answer names oEmbed or a self-hosted script sandbox. CLAIM(lO6GyCvbDm8@33:31)
- The WebTransport browser-support snapshot (roughly 60% of browsers, mid-2025) is a dated number; re-check coverage before designing on it. Distiller note (not the author). CLAIM(HR2jXy_wPg4@52:55)
- SSR of a zero-JavaScript sign-up page remains good first-paint advice; a fully JS-less form today needs progressive-enhancement care. Distiller note (not the author): keep the spirit (minimal JS on the conversion page). CLAIM(Tu-hZ6lqNtY@38:15)
- "Basic layout is already almost automated" and the related AI-progress claims are 2026 snapshots in a fast-moving area. Distiller note (not the author): treat as dated within months. CLAIM(v4Dt4FalMOA@44:31)
- The canvas-vs-DOM resource argument assumes canvas work needs a hand-built primitive library; 2026 canvas frameworks and WebGPU change the cost line but not the elimination logic. Distiller note (not the author). CLAIM(fmIiDLbLc_s@11:08)

## Hand-off

- Next stage: fesd-component-api (S04 component design: tree, reusable-widget API, UX states) for component problems; the S05 state/data-model stage skill for entity and store design.
- Adjacent estate skills: app-web-frontend for build slices, emil-design-eng for UI polish, fixing-accessibility, fixing-motion-performance, app-data-layer, and the api design harness hA-09 where an API surface is part of the architecture.
