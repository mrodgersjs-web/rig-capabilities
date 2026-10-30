---
name: "rigds-token-pipeline"
description: "Design token pipeline with provenance: extract or export tokens (DTCG, Figma variables, Tokens Studio), compile with Style Dictionary, prove built CSS matches handoff."
meta: "rig-design-studio"
owner: "theo-design"
done_when:
  - 'grep:capabilities/skills/rigds-token-pipeline/SKILL.md:[n]ever by hand-editing output'
  - 'grep:capabilities/skills/rigds-token-pipeline/SKILL.md:[T]aste constraints the tokens must encode'
---

# rigds-token-pipeline (spine 3 of 8)

Closes `tokenSet.provenance` in `rig.design-studio.dev-handoff.v1.1`. v1 declared tokens by hand; nothing proved the built site used them.

Sources: v1.1 schema (`rigds-launch-gate/references/rigds-dev-handoff-v1.1.schema.json`), concept file (`tokens` MCP tool of ux-design-scraper emits DTCG / css-vars / tailwind-v4 / figma-vars / style-dictionary; scraper Deliver step `generate-figma-tokens`), TASTE.md T2-T4 (type, color restraint, 8px spacing grid).

## Flow

1. **Source** (pick one, record it as `provenance.source`): `figma-variables` (Figma remote MCP `mcp.figma.com/mcp`), `tokens-studio` (JSON export), `scraper-extract` (scraper `tokens` tool), `style-dictionary`, or `hand-declared` (legal, but says so out loud).
2. **Normalize** to DTCG JSON at `tokens/tokens.json`. Record `provenance.extractedAt` and `provenance.sha256` of that file.
3. **Compile** with Style Dictionary to `tokens/build/vars.css` (and tailwind theme if used). Build runs in CI or a script, never by hand-editing output.
4. **Prove**: a check script greps the built CSS/served page computed styles and asserts every color/font/spacing value used is a token value. Report off-token values with file:line.

## Taste constraints the tokens must encode (TASTE.md)

- T2: one UI face (+ at most one display face). T3: accent used in <=3 places per screen. T4: 8px grid, card radius 12, pill 999.

## Rules

- Never hand-edit generated token output to fix a value; fix the source and rebuild.
- `sha256` mismatch between handoff and build = FAIL.

## Missing sources

- The scraper's `tokens` tool implementation was not read (full repo not local). Style Dictionary/Tokens Studio specifics come from the concept file's tooling notes, not a tested RIG pipeline. No worked example exists yet.
