---
name: "rigds-measure-loop"
description: "Post-launch measure loop: fetch each page's primary metric, write measured + evidence back to pageIndex, compare to baseline, route to the card. Use for post-launch results."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - 'grep:capabilities/skills/rigds-measure-loop/SKILL.md:[n]ever compute a delta'
  - 'grep:capabilities/skills/rigds-measure-loop/SKILL.md:[r]eport as a gap'
---

# rigds-measure-loop (spine 7 of 8)

New work, not a port: the scraper's Measure phase (ab-test-generation, heatmap-analysis, performance-monitoring, iteration-roadmap) generates plans and a roadmap but never fetches results or writes them back. This loop does.

Sources: concept file gap analysis, v1.1 schema `pageIndex[]`, `workflow-constants.ts` measure steps.

## Loop (per run, per page in `pageIndex[]`)

1. Read the page's `metric.name` and `source` from the handoff.
2. Fetch the current value from that source (GA4, Search Console, PostHog, CrUX, Lighthouse on the live URL). Save the raw output to `measure/<date>/<path-slug>.json` and its sha256.
3. Write back `measured`, `measuredAt`, `source`, and append `evidence[{kind:"api"|"command"|"export", ref, sha256}]`.
4. Compare: `baseline: null` -> report as a gap ("no baseline, delta unknown"), never compute a delta. Otherwise delta and direction vs `metric.direction` and `target`.
5. Route: the result joins to `cardId`, so the finding lands on the board card that produced the design. Write one line per page into `measure/<date>/report.md`.
6. Iterate: pages off target become candidate experiments (one change, one metric). An experiment that touches a live site goes through `rigds-launch-gate` again.

## Rules

- A measured number without an evidence entry is not written.
- Never hand-edit a measured value. Re-fetch.
- Measurement windows are stated (e.g. 28d). A comparison across different windows is invalid.
- Scheduling: browser-free fetches belong on launchd/n8n per `runner-selection`, not an Aside routine.

## Missing sources

- No live site in the RIG estate has a v1.1 handoff yet, so this loop has never run end to end. API auth for GA4/GSC/PostHog on client properties is not set up.
