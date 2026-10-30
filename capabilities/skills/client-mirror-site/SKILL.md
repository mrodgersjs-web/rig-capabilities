---
name: "client-mirror-site"
description: "Build a client-mirrored offering website end to end: Pinterest board, buyer pains, 7-phase Discover-to-Measure run, JEV gate, Vercel preview deploy. Use for offer sites."
meta: "rig-design-studio"
owner: "theo-design"
status: "Candidate; production trust and rendered outcome verification pending"
done_when:
  - "cmd:python3 -m unittest tests.test_site_gate_evidence"
---

# client-mirror-site

One offering = one site = one folder `sites/<slug>/`. Every phase leaves executed artifacts and native Miro item evidence. File presence alone does not advance a phase.
Canonical run doc (copied here): `references/DESIGN-PROCESS.md`. Agent brief: `references/BUILDER-BRIEF.md`. Probe: `references/PROBE.md`.
Live workspace the scripts assume: `/Users/rig128gb/Developer/rig-client-mirror-sites/` (`ROOT` in `scripts/gate.py`; change it if you run elsewhere).

"Client-mirrored" means a named client or explicitly user-named project owns the offering's brand. Its solution addresses a source-supported problem. Category evidence must be labeled category evidence and reviewed for applicability; never claim an anonymous comment came from that client's customer or employee. Multiple distinct offerings for one client can count. RIG-branded offers and renamed clones cannot count. TransformFit may be a user-named private project; a public domain is not required and must never be invented.

Before visual work, create `offering.json` with the v2 identity, solution, raw source/run chain and Pinterest visual provenance described in `../jev-site-gate/references/EVIDENCE-V2.md`. Preserve proposed/unverified status. Cached Pinterest counts describe that extraction only, not full-board coverage. Inspect actual images; captions alone cannot establish palette or layout.

## Inputs (check all exist before phase 1)

| Input | Where |
|---|---|
| Offering identity and source chain | `sites/<slug>/offering.json`; actual client/project, client branding, source-located pains, run receipts, proposed mechanism, pin/image hashes and observed visual decisions |
| Board pins | `_inputs/pinterest/<board>/index.json` + images (pull: `pinterest-board-pull`) |
| Buyer pains | Airtable RIG Command Center `app0aAXlSUFPbuTBL`: STRAT · Demand Screen `tbli1s5mwhZ7To7gz`, Verified Stories `tblUaVHxqaiGtxd5m`, Social Comments `tblPTqaduGtfmHvWH`, Collected Comments `tblwcDWTMudQ2ehez` |
| Offer + price basis | `~/Developer/strategy-studio-pro/2026-10-03-market-strategy-v2/pinterest_candidates.csv` (+ opportunity_trees.csv, sources_and_assumptions.csv) |
| Taste law | `~/Developer/transformfit-flutter/design/TASTE.md` (T1-T6) |
| Landing bar | `~/Developer/transform-fit-launch/docs/design/LANDING_PAGE_60_POINT_SCORING_RUBRIC.md` |
| Phase model | 7-phase Double Black Box, `RIGForge/repos/ux-design-scraper/src/shared/workflow-constants.ts` (partial clone; the GitHub/Gitea repo is canonical) |
| Gate row | `_gate/airtable-rows.json` maps slug -> DO · Today record id |

## Phases -> files

1. **Discover** -> `discover.md`, `demand.md`. Open every pin image, write what it teaches (layout, type, color, motion, imagery). 3-5 live mirror sites of the buyer's category (URLs + hero screenshots from the served page). 3+ award references (Awwwards SOTD, godly, motionsites). demand.md: each pain line carries its Airtable record id. Social Fetch only if the tables are empty for this buyer: max 30 credits/site, key `SOCIALFETCH_API_KEY` from `~/.hermes/.env`, never printed, every call logged.
2. **Define** -> `define.md`, `claims.md`. One buyer, top 3 pains with ids, the offer (price only from `price_basis`), one-sentence promise, one CTA, section map, named wow section id, the 3D moment, the scroll story. claims.md: every number on the page with its source path. No source, not on the page.
3. **Gate** -> `gate.md`. JEV `noul` on (a) promise addresses a listed pain (b) CTA is one concrete next step. Below 0.85: rewrite define.md, re-run. See `jev-site-gate`.
4. **Diverge** -> `diverge.md` + `evidence/diverge-*.png`. Three directions, each mapped to named pins and mirror sites, rendered as hero mocks on the served dev server. Pick one for a buyer reason.
5. **Develop** -> `develop.md`, `app/`. Static Vite or plain HTML/JS (Next.js only if needed). GSAP+ScrollTrigger, Lenis, three.js, Motion One. Must: full-bleed hero >=50% vh with `data-pinterest-source`, scroll story, one real 3D moment reacting to scroll/pointer, a wow section, `prefers-reduced-motion` fallback, <=2 font families, accent <=3 places/section, CTA usable <1s. Markup contract in `references/PROBE.md`. Banned: fake logos, testimonials, client names, invented stats, lorem, stock-icon rows, the gate's banned words. Never pass another brand's product UI off as ours: generate original imagery instead.
6. **Deliver** -> `deliver.md`. `cd app && npx -y vercel deploy --yes`. PREVIEW ONLY: never `--prod`, never alias a domain (Gate-D). Record URL, confirm HTTP 200.
7. **Measure** -> `measure.md`, `critique.md`, actual browser/Lighthouse captures and an independent verifier receipt. Follow `references/PROBE.md` and the v2 contract. The human-readable score is commentary; acceptance reads bound structured findings. Run `python3 scripts/gate.py <slug> --root <workspace> --verifier-key <already-authorized-public-key>`. Missing approved trust means FAIL. Only pass `--airtable-record` when that provider write is scoped and authorized. Loop Develop > Deliver > Measure until accepted or the bounded fix budget ends. No award or superiority guarantee.

## Hard rules

- Only `gate.py` checks an Airtable row off. A FAIL stays In progress with reasons; never mark Done by hand.
- No Pinterest writes, no outward sends, no `git push`, no prod deploy. Never mention James, Jacob, Avis or comp.
- Dead tool (bash, REPL, Vercel auth, Lighthouse) = `[blocked]` with the exact error. Never fake a capture or a score (`rigds-capture-honesty`).
- This candidate does not enroll a signer or grant trust to a caller-selected key. Permanent trust or signing credential changes require review. The production gate remains under its existing writer until coordinated propagation and real QA are complete.
- MotionSites MP4/WebP previews are references. They cannot prove scroll interaction, CSS 3D depth, reduced motion, mobile usability or performance on the built offering.
- Final report per site: preview URL, gate score, JEV scores, critique score, resolved model read from runtime.

## Known gaps

- No `rigds-content-seo` pass is wired in yet; the run has no keyword map.
- No post-launch loop: Measure stops at the gate. `rigds-measure-loop` is the follow-on.
