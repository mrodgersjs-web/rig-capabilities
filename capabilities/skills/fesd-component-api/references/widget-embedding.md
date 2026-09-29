# Widget embedding (cross-stage sub-skill: S03 distribution + S04 API)

Purpose: design how a reusable widget runs on third-party pages: the embed route, the iframe/script path, the provider-registry path, and the package boundary.

When to load: when the requirement list includes "embeddable", "runs on other sites", or "ships as a package" (poll widget, comment widget, badge, form).

## Step checklist

1. Treat embeddability and distribution as requirements up front, not as closing afterthoughts. CLAIM(lO6GyCvbDm8@05:34) CLAIM(lO6GyCvbDm8@05:08)
2. Serve embedding through an application route that takes an id (poll id), fetches the data, and renders the widget server-side of the host page. CLAIM(lO6GyCvbDm8@32:18)
3. Offer two embedding paths: (a) iframe plus a setup script for controlled or semi-controlled hosts, (b) a provider service (Embedly-style registry) with a JSON description for broad third-party pickup. CLAIM(lO6GyCvbDm8@33:31)
4. Keep the widget itself framework-agnostic so the embed path and the npm consumer share one core: tiny imperative API (initialize(props), destroy()). CLAIM(lO6GyCvbDm8@15:21)
5. Ship as an npm package so the widget stays decoupled from any single application. CLAIM(9aOXGE7wAZo@35:04)
6. Split the package into core, theming, and utility modules so an embedder or npm consumer installs only the core. CLAIM(lO6GyCvbDm8@22:02)
7. Keep the embed payload small and modern-targeted (minify, compress, CDN; split bundles per target). CLAIM(lO6GyCvbDm8@20:41) CLAIM(lO6GyCvbDm8@21:29)
8. Re-check the requirements list at the end; embeddability is exactly the requirement he caught himself dropping. CLAIM(lO6GyCvbDm8@31:56)

## Laws for this sub-topic

- Embed route: id-keyed application route that fetches and renders the widget. CLAIM(lO6GyCvbDm8@32:18) single-source (S03 law, detailed here).
- Two embedding paths: iframe + setup script, or provider service with JSON description. CLAIM(lO6GyCvbDm8@33:31) single-source (S03 law, detailed here).
- npm packaging for decoupling and reuse. CLAIM(9aOXGE7wAZo@35:04) consensus (lO6GyCvbDm8@05:08 makes distribution a requirement).
- Embeddability stated as a requirement, not an afterthought. CLAIM(lO6GyCvbDm8@05:34) single-source.
- Core/theming/utilities module split. CLAIM(lO6GyCvbDm8@22:02) single-source.

## Decision table

| Embed question | Pick | When |
|---|---|---|
| iframe + setup script vs provider registry | iframe for controlled hosts | You can place a script on the host page. CLAIM(lO6GyCvbDm8@33:31) |
| iframe + setup script vs provider registry | Provider registry (JSON description) | Unknown third-party sites must pick it up. CLAIM(lO6GyCvbDm8@33:31) |
| npm package vs script-only distribution | Both: shared core, two distributions | Consumers are both app developers and site embedders. CLAIM(9aOXGE7wAZo@35:04) CLAIM(lO6GyCvbDm8@15:21) |
| One universal bundle vs modular | Modular (core / theming / utilities) | Embed payloads must stay small. CLAIM(lO6GyCvbDm8@22:02) |

## Anti-patterns

- Designing the widget first and discovering embeddability at the end. CLAIM(lO6GyCvbDm8@31:56)
- Coupling the widget to one host application instead of packaging it. CLAIM(9aOXGE7wAZo@35:04)
- Shipping polyfills every embedder pays for. CLAIM(lO6GyCvbDm8@21:29)

## Worked cases

- lO6GyCvbDm8 "Design a Poll Widget": the canonical embed design (route, iframe/script, provider JSON) plus the requirements re-check that caught it.
- 9aOXGE7wAZo "Typeahead Widget": npm packaging as the closing distribution step.
- u6jhTo13_No "Data Table Component": the same package-split and bundle-target discipline for an npm-only widget.

## Dated / contestable

- Embedly-style oEmbed registries still exist but are less central than in 2021; a modern answer names oEmbed or a self-hosted script sandbox. Distiller note (not the author). CLAIM(lO6GyCvbDm8@33:31)
- ES5/ES6 dual-bundle targeting for embeds has largely expired with IE11; differential module builds are the modern form. Distiller note (not the author). CLAIM(lO6GyCvbDm8@21:29)
