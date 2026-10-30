---
name: "rigds-build-target"
description: "Pick and hand off the build target for an approved design: static Vite, Next.js, CMS (Sanity, Directus, Payload), Vercel preview. Use for stack choice, build handoff, CMS."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - 'grep:capabilities/skills/rigds-build-target/SKILL.md:[D]ecision .first match wins.'
  - 'grep:capabilities/skills/rigds-build-target/SKILL.md:[S]ingle offer page, no editor'
---

# rigds-build-target (spine 4 of 8)

The handoff contract is app-independent (`rig-design-studio` rule). This skill chooses the target after the handoff, not before.

Sources: concept file tooling findings (agent-addressable CMS: Sanity `mcp.sanity.io`, Directus native MCP, Payload schema-as-code MIT; Vercel MCP), `client-mirror-site` Develop phase (static Vite or plain HTML/JS by default, Next.js only if needed), `UX_UI_SOURCE_OF_TRUTH.md` (scraper runtime code never ships in product code).

## Decision (first match wins)

1. Single offer page, no editor -> static Vite / plain HTML+JS.
2. Several pages, client edits copy -> static + agent-writable CMS (Payload if self-hosted and schema-as-code matters; Sanity or Directus if hosted MCP access matters).
3. App behavior, auth, or server data -> Next.js.

Record the choice and reason in `develop.md`.

## Handoff to a coding agent

- Input: the dev-handoff v1.1 export, token build (`rigds-token-pipeline`), keyword/meta map (`rigds-content-seo`).
- Markup contract for probing: `client-mirror-site/references/PROBE.md`.
- Deploy: preview only (`npx -y vercel deploy --yes`). Prod, domain, DNS, paid plans = Gate-D.

## Missing sources

- No RIG decision record compares the three CMS options in practice; the order above is from capability notes, not a trial. No worked CMS build exists.
