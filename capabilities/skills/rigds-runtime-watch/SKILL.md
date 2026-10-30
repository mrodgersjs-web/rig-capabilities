---
name: "rigds-runtime-watch"
description: "Post-launch runtime watch for a live site: uptime, synthetic Playwright checks, backups, CMS updates, alerts. Use for site monitoring, maintenance, uptime, support phase."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - 'grep:capabilities/skills/rigds-runtime-watch/SKILL.md:[m]issed heartbeat alerts'
  - 'grep:capabilities/skills/rigds-runtime-watch/SKILL.md:[P]erf drift'
---

# rigds-runtime-watch (spine 6 of 8)

Preface Phase 6/7 (Maintenance / Support) has no home in the scraper model or `rig-design-studio`; no uptime, backup or CMS-update step exists in either (concept file).

Sources: concept file tooling findings: Better Stack (MCP server, heartbeats for cron/backups, REST API), Checkly (Playwright monitors-as-code from CI), scraper measure step `performance-monitoring` (generates a guide only).

## Watch set per live site (keyed on `pageIndex[].url`)

1. **Uptime**: HTTP check per primary URL, 1-5 min.
2. **Synthetic**: one Playwright check that the primary CTA is visible and clickable (`[data-cta="primary"]`), run from CI or Checkly.
3. **Backups**: CMS/database backup job with a heartbeat; a missed heartbeat alerts.
4. **Updates**: CMS/dependency update cadence with a preview deploy + gate before prod.
5. **Perf drift**: weekly Lighthouse on the live URL feeding `rigds-measure-loop`.

## Rules

- Runner: browser-free checks go on launchd, CI or n8n per `runner-selection`, not an Aside routine.
- Alert channel is Telegram (Mike) only after he approves the routing.
- Paid monitoring plans and any change on a client's production = Gate-D.

## Missing sources

- No monitoring account (Better Stack, Checkly) is confirmed set up on this estate. Nothing here has run.
