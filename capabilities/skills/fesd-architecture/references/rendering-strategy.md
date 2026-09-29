# Rendering strategy (S03 sub-skill)

Purpose: capture the author's stated rendering trade-offs (engine choice canvas vs DOM, delivery shape CSR vs SSR pre-render vs SPA, and where hydration and SSG are simply not covered), plus his architectural AI-era remarks.

When to load: when the design must name a rendering engine or delivery shape, or when AI-generated code is part of the proposed build.

## Step checklist

1. Decide the engine before anything else: canvas vs DOM rewrites the component and data design downstream. CLAIM(fmIiDLbLc_s@07:35)
2. Run the resource test: canvas only for mass-market products with large engineering resources (GPU-accelerated rendering, best FPS, no per-element memory cost, but a primitive library, specialized skills, and a mixed DOM layer for accessibility); DOM for internal or cost-sensitive builds where development cost dominates. CLAIM(fmIiDLbLc_s@08:16) CLAIM(fmIiDLbLc_s@08:53) CLAIM(fmIiDLbLc_s@09:44) CLAIM(fmIiDLbLc_s@11:08)
3. State which one the problem earns. In the spreadsheet case he picks DOM for exactly that reason. CLAIM(fmIiDLbLc_s@11:41)
4. Pick the delivery shape per surface, not per app: SSR pre-render clean HTML where first paint converts (sign up), CLAIM(Tu-hZ6lqNtY@38:15) SSR pre-render of some feed pages where time-to-first-content is the metric, CLAIM(5vyKhm2NTfw@38:24) stay client-rendered when the extra server-rendering infrastructure does not pay off (chat). CLAIM(LEaiGjffLEs@38:50)
5. Prefer a single-page application shape when selection in one pane must instantly render another. CLAIM(tsGarhpWOws@09:48)
6. If generated code is in the plan, state the supervision rule (below) as an architecture constraint, not a preference.

## Laws for this sub-topic

- Engine before design. CLAIM(fmIiDLbLc_s@07:35) single-source.
- Canvas for resourced mass-market products; DOM for internal or cost-sensitive builds. CLAIM(fmIiDLbLc_s@11:08) single-source.
- SSR pre-render some consumption pages to cut time-to-first-content. CLAIM(5vyKhm2NTfw@38:24) consensus with the sign-up case (Tu-hZ6lqNtY@38:15).
- Skip SSR where the infrastructure cost does not pay off for the product. CLAIM(LEaiGjffLEs@38:50) single-source.
- SSR clean HTML (minimal JS) for the conversion page. CLAIM(Tu-hZ6lqNtY@38:15) single-source.
- SPA shape when cross-pane rendering must be instant. CLAIM(tsGarhpWOws@09:48) single-source (implied).

## What he does not state (coverage honesty)

- Hydration: the word and the problem (server markup becoming interactive, hydration cost, selective/island hydration) never appear in this corpus. If the round asks, say the corpus covers the CSR/SSR choice but not hydration mechanics, and answer from first principles or another source.
- SSG: no static-generation discussion appears; the closest statements are SSR pre-render of pages or feeds. CLAIM(5vyKhm2NTfw@38:24) CLAIM(Tu-hZ6lqNtY@38:15)
- Streaming SSR, RSC-style server components, and edge rendering: not covered.

## AI-era architecture remarks (v4Dt4FalMOA, tagged S03)

These are architectural, so they belong in this stage's decisions:

- Own the architecture and engineer the spec yourself, then let AI execute in fast iterations; prompt-and-hope generation does not scale to production. CLAIM(v4Dt4FalMOA@41:31) single-source.
- Accept AI-written code only when you supervise it and feed it good requirements; unsupervised generation becomes unmaintainable. CLAIM(v4Dt4FalMOA@40:14) single-source.

Distiller note (not the author): treat these as the stage's rule on who owns the rendering decision. The engine and delivery-shape calls are exactly the decisions the author keeps for the human and hands to the model only as execution.

## Decision table

| Surface | Pick | Why (as he states it) | Citation |
|---|---|---|---|
| Spreadsheet-class canvas, internal or cost-sensitive | DOM | Dev cost dominates; DOM is cheap and accessible | CLAIM(fmIiDLbLc_s@11:08) |
| Spreadsheet-class canvas, mass-market with resources | Canvas | GPU rendering and FPS, no element memory cost | CLAIM(fmIiDLbLc_s@08:16) |
| Sign-up / conversion page | SSR clean HTML, minimal JS | First paint is what converts | CLAIM(Tu-hZ6lqNtY@38:15) |
| Entertainment feed pages | SSR pre-render of some pages | Time-to-first-content | CLAIM(5vyKhm2NTfw@38:24) |
| Chat / interaction-heavy app | Client render | Server-render infrastructure does not pay off | CLAIM(LEaiGjffLEs@38:50) |
| Editor with list-to-pane navigation | SPA shape | Instant center render on selection | CLAIM(tsGarhpWOws@09:48) |

## Worked cases

- fmIiDLbLc_s "Google Sheets": the canvas vs DOM elimination and the DOM pick.
- 5vyKhm2NTfw "Facebook News Feed": SSR pre-render of some feeds inside a client app.
- LEaiGjffLEs "Chat application": the explicit "do not pay for SSR" verdict.
- Tu-hZ6lqNtY "Netflix (product design)": SSR for the sign-up surface only.
- tsGarhpWOws "Notion-like editor": SPA shape for instant pane swaps.
- v4Dt4FalMOA "FAANG engineer podcast": architecture ownership in the AI-execution era.
