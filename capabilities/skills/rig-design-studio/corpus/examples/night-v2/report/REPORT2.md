# Night lane DESIGN-STUDIO v2 — report (export loop + Stitch round 2)

Worktree: `/Users/rig128gb/orca/workspaces/rig-design-studio/night-design-studio` (no commit/push — morning landing job). Dispatch: `.rig/jake/dispatch/2026-09-30-night/design-studio-v2.md`. v1 state in REPORT.md.

working: export loop — new `app/src/export.ts` (`serializeBoard` → `rig.design-studio.dev-handoff.v1`: cards with phase/kind labels, upstream/downstream link refs, per-card deviation + out-of-budget flag, board link list, counts with per-phase breakdown, deviation min/max/outOfBudget, full token set from the new `app/src/tokens.ts` [extracted from SidePanel so panel and exporter share one source]) and `promptBundle` (board-level coding prompt first — board map per phase, dependency links, token set, anti-patterns, acceptance — then the 16 per-card prompts from `aiCodingPrompt`).
working: side panel — new "Export dev handoff" section (`SidePanel.tsx`): one action "Export dev handoff (.json + .md)" downloads both files (Blob + anchor), then shows a count note. Verified in the real Aside browser against the served app: clicking it downloaded `rig-dev-handoff.json` + `rig-ai-coding-prompts.md` (system download messages observed), and the downloaded content was inspected: schema `rig.design-studio.dev-handoff.v1`, counts `{'cards': 16, 'links': 20, 'phases': {'discover': 4, 'define': 4, 'develop': 4, 'deliver': 4}}`, deviations `{min: 0, max: 5, outOfBudget: 2}`, tokenSet `MASTER-CREATIVE-PROMPT v3.0` 14 colors; markdown bundle 621 lines with the board brief + board map + per-card prompts.
working: unit-ish check — `app/scripts/export-check.mjs` (npm script `check:export`) compiles the serializer chain with the local tsc to a temp dir, runs it on `seed.ts`, asserts card/phase/link counts match the seed source plus structure invariants (unique ids, link endpoints resolve, every card carries deviation + phase, token set bound, ≥4 artifacts per phase, board-level + 16 per-card prompts present). Output pasted below.
working: seed rebuild — `app/src/seed.ts` now derives from the LIVE Loehr sources (v1 lacked them): `/Users/rig128gb/Developer/loehr-hr-group/site/index.html` (sections #hero, #group, #sequence, #members, #operator, #pricing, #offers, #denver, #book; James Loehr 18 yrs ops / 37 locations / ~550 employees; pricing $6,600/yr company pack, $0 guest diagnostic; market context SHRM $3,995 / Hacking HR $2,000 / Mile High SHRM cap 12) and `research/JEV-AUDIT.md` (web.market FINAL 0.747 no BLOCK; named_pain_lead 0.46→0.73; diagnostic_wedge 0.17→0.69; boring_reliable_job 0.96; ui.design accessible 0.75). Board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)" — 16 artifacts, exactly 4 per diamond phase, 20 links; every artifact references real page sections and/or the audit's scores; the audit's honest non-0.9 verdict and the rubric-vs-product structural ceiling are carried as research cards, not laundered.
working: Stitch round 2 — `app/.stitch/prompts/screen-4-export-handoff-modal.md` + `screen-5-mobile-canvas-view.md` (enhanced, consistent with `.stitch/DESIGN.md`, which now documents screens 4-5 and the Loehr copy source); `app/scripts/stitch-run.mjs` extended: 2 new screens (per-screen `deviceType` DESKTOP/MOBILE), per-screen error isolation, manifest MERGE with previous state (a failed screen keeps its old entry), status semantics `STITCH-OK` / `STITCH-PARTIAL` / `STITCH-R2-BLOCKED` (any round-2 generation failure → old manifest state preserved + exact error) / `STITCH-BLOCKED`.
working: generation via the already-proven stitch-mcp route (keychain proxy, no browser): project 16298493107759969558; the 3 round-1 screens reused their saved raw responses + existing downloads untouched ("kept existing …png/html"), both new screens generated and downloaded. Manifest: STITCH-OK, 5/5 screens with real screenshots (export-handoff-modal.png 69,029 B + html 19,418 B; mobile-canvas-view.png 53,242 B + html 19,075 B; stitchScreenIds f86d3a0abf1a491b8acdff225d61da6e / 0e9b5bcef38d49b59678d766ed5ae1e8). Mockups tab is manifest-driven so it picked up the 2 new tiles; verified in the running app: 5 tiles, all badged "stitch screenshot", banner "STITCH-OK · project 16298493107759969558". Not blocked.

done: BOARD EXPORT — "Export dev handoff" action in the side panel serializes the whole board (cards, phase, links, deviation scores, token set) to `rig-dev-handoff.json` and renders the copy-paste AI-coding prompt bundle (board-level + per-card) to `rig-ai-coding-prompts.md` for download; real-browser click verified with inspected download content (see above).
done: CHECK output (`npm run check:export` → `node scripts/export-check.mjs`), pasted verbatim:

```
[export-check] compiling src/{types,seed,store,tokens,export}.ts → /var/folders/…/export-check-G1Hdfr
[export-check] board: "Iterate the Loehr HR-group landing page (JEV-audit-driven)"
[export-check] counts
  PASS  cards = 16
  PASS  links = 20
  PASS  phases = {"discover":4,"define":4,"develop":4,"deliver":4}
  PASS  serialized card rows = 16
[export-check] invariants
  PASS  unique card ids = 16
  PASS  unique link ids = 20
  PASS  all link endpoints resolve = true
  PASS  every card has deviation + phase = true
  PASS  every card has token set bound = "MASTER-CREATIVE-PROMPT v3.0"
  PASS  min 4 artifacts per phase = true
[export-check] prompt bundle
  PASS  board-level prompt present = true
  PASS  per-card prompts = 16
  PASS  bundle covers every phase = true

[export-check] PASS — serializer output matches seed.ts on cards, phases, links.
```

(Re-run after the final build: PASS again, 13/13.)
done: STITCH-R2 — 2 NEW screens generated via the stitch-mcp route (not browser): "export handoff modal" (DESKTOP) and "mobile canvas view (390px)" (MOBILE), downloaded into `app/.stitch/designs/` (png+html each), `manifest.json` merged to 5 screens STITCH-OK, Mockups tab shows all 5 as stitch screenshots. No failure occurred, so STITCH-R2-BLOCKED was not needed; the runner now enforces that path (old manifest state preserved + exact error) if a future run fails.
done: REAL CONTENT DRILL — seed board rebuilt from the live Loehr site + JEV-AUDIT.md: idea "iterate the HR-group landing page", 4 artifacts per phase (16 total, 20 links) referencing actual page sections (#hero named-pain lead, #sequence year-in-the-room, #members bring/take + JEV pain scores 6.0/6.90 from the Sept 2026 Reddit sweep, #operator credibility spine, #pricing fee-sheet + verified market context, #book accessible apply form) and the audit findings (0.747 no-BLOCK verdict kept honest, named_pain_lead/diagnostic_wedge gaps as the iteration targets, ui.accessible 0.75 as the form task, buyer-rubric structural ceiling disclosed). Loop proven end to end: research → diamond → mockup → dev handoff (Deliver cards name the Stitch mockups + export bundle as the coding contract).
done: TEST `npm run build` → exit 0 (tsc -b + vite build; 47 modules; dist bundles all 5 stitch screens). TEST serve: `python3 -m http.server 8902` (8899/8901 occupied per dispatch; 8902 found free via a python bind-scan) → `curl` index 200, title `RIG Design Studio — Double Diamond Canvas`, js 200, mobile-canvas-view.png 200, export-handoff-modal.png 200; server killed after (port confirmed closed). TEST export check: 13/13 PASS (output above). TEST UI: 16 cards render on canvas, Export button click produces both downloads with correct content, Mockups tab 5/5 stitch screenshots.
done: VISUAL — `artifacts/app.png` updated via the Aside browser from the real served app: PNG 1440×900, 331,795 bytes, sha256 769476f7e8c1ad2e612a799fb148af136b212ec64d9ce3e8cdf1c4873b385db8; visually verified (Loehr seed cards with JEV references, bezier links, token panel, zoom control). Not UNVERIFIED-VISUAL — no fakes anywhere.
note: D85 state carries over from v1 unchanged — d85_certified FAILED, not certified (BLOCK UNKNOWN_PROCESS / SUBMITTED_MALFORMED, refusal chain in REPORT.md + artifacts/d85-*.txt). v2 makes no certification claim; morning lane remediation (register process → classify → score → checklist → verify-cert) still stands.
note: `rm` of the two verified download files in `~/Downloads` (`rig-dev-handoff.json`, `rig-ai-coding-prompts.md`) was blocked by the guard as irreversible; they remain there for you to delete.
done: deliverables — app/src/{export.ts,tokens.ts,seed.ts,SidePanel.tsx} changed, app/scripts/{export-check.mjs,stitch-run.mjs} (+R2 semantics), app/.stitch/prompts/screen-{4,5}-*.md, app/.stitch/DESIGN.md (screens 4-5 + Loehr copy source), app/.stitch/designs/ (2 new screens + merged manifest), app/package.json (`check:export`), artifacts/app.png, REPORT2.md.
done: