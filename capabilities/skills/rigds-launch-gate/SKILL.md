---
name: "rigds-launch-gate"
description: "Pre-launch gate for a design build: v1.1 dev-handoff assertions, pageIndex, redirects, perf/a11y budget, taste >=8, Gate-D for prod. Use before launch, go-live, ship."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - 'grep:capabilities/skills/rigds-launch-gate/SKILL.md:[N]othing goes live on adjectives'
  - 'grep:capabilities/skills/rigds-launch-gate/SKILL.md:[c]ounts.pages === pageIndex.length'
  - 'grep:capabilities/skills/rigds-launch-gate/references/rigds-dev-handoff-v1.1.schema.json:[x]-new-assertions-for-export-check'
  - 'cmd:python3 -m json.tool capabilities/skills/rigds-launch-gate/references/rigds-dev-handoff-v1.1.schema.json >/dev/null'
---

# rigds-launch-gate (spine 5 of 8)

Nothing goes live on adjectives. This gate extends `rigds-export-check` (v1, 13 assertions) with the v1.1 assertions and the ship bar.

Sources: `references/rigds-dev-handoff-v1.1.schema.json` (`x-new-assertions-for-export-check`), TASTE.md scoring (ship = taste >=8 AND a dual product gate; one RED blocks; "pretty does not override a buyer PASS"), scraper Deliver steps (performance budget with Lighthouse CI, accessibility report), `jev-site-gate`.

## Checks (all CODE unless marked)

1. `schema === "rig.design-studio.dev-handoff.v1.1"`.
2. `counts.pages === pageIndex.length` (derived, never typed).
3. Every `pageIndex[].cardId` resolves to a card; every `url` unique; every card with a url appears exactly once.
4. `metric.direction` in `increase|decrease|any`; any `measured != null` row has >=1 `evidence[]`.
5. `tokenSet.provenance.source` present (`rigds-token-pipeline`).
6. All 7 phase ids present (a 4-phase export needs an explicit legacy flag).
7. Baseline gaps (`baseline: null`) listed in the report, not skipped.
8. Redirect map from `rigds-content-seo` resolves: zero 404s on old URLs.
9. Lighthouse mobile perf >= 80, a11y >= 90 on the served preview (budget from the run's brief).
10. Taste: vision critique of real 1440 + 390 screenshots, `SCORE >= 8/10`, no TASTE RED (T1-T6).
11. Site gate PASS (`jev-site-gate`, gate-result.json verdict PASS).

## Verdict

- `PASS` only when every check executed and passed. A check that could not run = FAIL with the reason.
- PASS clears the build for production **review**, not production. A prod deploy, domain alias, DNS change or client send is Gate-D: Mike approves the exact action.

## Missing sources

- No runnable v1.1 export-check script exists yet; v1's lives at `corpus/examples/night-v2/scripts/export-check.mjs` (per `rigds-export-check`). Port it before claiming checks 1-7 ran.
- The "dual product gate / 3-persona buyer panel" from TASTE.md is not encoded here beyond requiring the site gate.
