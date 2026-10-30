---
name: "rigds-discovery-instrument"
description: "Instrument design discovery: baseline every page's one primary metric before redesign, build the pageIndex url join key, record sources. Use for discovery, baselines, audits."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - 'grep:capabilities/skills/rigds-discovery-instrument/SKILL.md:[R]ecord provenance'
  - 'grep:capabilities/skills/rigds-discovery-instrument/SKILL.md:[U]ntrusted data never lands without a source'
---

# rigds-discovery-instrument (spine 1 of 8)

Discovery that measures nothing leaves launch with nothing to compare against. This skill makes the Discover phase produce the join key and the baseline.

Sources: `memory/concepts/design-workflow-taste-gates.md` (gap analysis), `rigds-dev-handoff-v1.1.schema.json` (copy in `rigds-launch-gate/references/`), scraper Discover steps in `ux-design-scraper/src/shared/workflow-constants.ts` (deep-search, multi-site-scrape, heatmap-fetch, trend-search, knowledge-enrichment, research-synthesis, inspiration-analysis).

## Output: `discovery/page-inventory.json`

One row per page that exists today or will exist, shaped as v1.1 `pageIndex[]`:
`{url, path, cardId, phaseId:"discover", metric:{name, unit, direction}, baseline, target:null, measured:null, source, evidence:[{kind, ref, sha256?}]}`

## Steps

1. **Inventory URLs.** Existing site: crawl (Screaming Frog CLI headless, or sitemap.xml + link walk). New site: the section/page map from define. Every URL unique.
2. **One primary metric per page.** Exactly one. A page with two primary metrics has none. Direction is `increase|decrease|any`.
3. **Baseline before any design change.** Pull from the source that owns the metric (GA4, Search Console, PostHog, CrUX, Lighthouse). Store the command or export path in `evidence[]`. If no source exists, `baseline: null` and list it under `gaps` in the inventory. Null is legal; skipping the row is not.
4. **Bind each page to a board card** (`cardId`). Cards that are not pages (persona, decision, risk) carry `url: null`.
5. **Record provenance** of every number: `source` like `gsc:clicks-28d`. Untrusted data never lands without a source.

## Rules

- A number with no `evidence[]` entry is not a measurement.
- Behavioral tools: PostHog is the one that automates replay, flags and experiments with API access; Clarity replays expire in 30 days; Hotjar merged into Contentsquare (Jul 2025). Prefer PostHog where a new install is needed (install = Gate-D if paid).
- Reads only. No tracking snippet goes onto a client site without approval.

## Missing sources

- The full `ux-design-scraper` repo is not local (`RIGForge/repos/ux-design-scraper` is a single-commit partial clone); the scraper's own discovery engine code was not read. This skill encodes the phase steps and the v1.1 schema only.
