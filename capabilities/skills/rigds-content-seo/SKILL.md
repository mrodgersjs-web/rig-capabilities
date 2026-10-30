---
name: "rigds-content-seo"
description: "Content and SEO phase for a site build: keyword-to-URL map, content inventory and migration, metadata, claims sourcing. Use for SEO, keywords, content plan, page copy."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - 'grep:capabilities/skills/rigds-content-seo/SKILL.md:[B]anned words per the site gate'
  - 'grep:capabilities/skills/rigds-content-seo/SKILL.md:[z]ero orphaned 404s'
---

# rigds-content-seo (spine 2 of 8)

Preface Studios Phase 2 (Content and SEO) has no home in the scraper's 7-phase model and no step in `rig-design-studio`. This skill fills it, keyed on `pageIndex[].url`.

Sources: `memory/concepts/design-workflow-taste-gates.md` (gap + tooling findings), Preface Studios board in Miro `https://miro.com/app/board/uXjVEez017g=/` (Content column), v1.1 schema.

## Outputs (in the site folder)

- `content/keyword-map.csv`: `url, primary_keyword, secondary_keywords, intent, source, volume_source_ref`. One primary keyword per URL; no two URLs share a primary (cannibalization).
- `content/inventory.csv`: existing page -> action (`keep|rewrite|merge|redirect|drop`) -> target URL. Every `redirect` has a 301 target.
- `content/meta.json`: per URL title (<=60 chars), description (<=155), h1, canonical, OG image.
- `claims.md`: every number in copy with its source path (shared with `client-mirror-site`).

## Steps

1. Start from `discovery/page-inventory.json` (`rigds-discovery-instrument`).
2. Keyword data from a real source and cite it: Search Console (free), Semrush MCP, Ahrefs API v3 (60 req/min), Screaming Frog CLI (`--headless`, exports to Sheets). No source = no volume number; leave it blank.
3. Copy uses the buyer's own words from demand evidence (record ids), not invented phrasing. Banned words per the site gate.
4. Migration: map every live URL before launch so `rigds-launch-gate` can check zero orphaned 404s.

## Rules

- No invented search volumes, rankings or traffic figures.
- Paid tool signups are Gate-D.

## Missing sources

- No RIG-authored SEO doctrine file was found; the Preface Content-phase step list lives only on the Miro board and was not re-read here. Steps above are from the concept file's gap analysis and tooling findings, not from a Preface document.
