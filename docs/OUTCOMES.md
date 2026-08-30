# Outcome views — browse the estate by what you want to achieve

The monorepo question, answered: one git-versioned hub (`~/Developer/rig-capabilities`)
holding **canonical** assets, indexing every installed harness root in place, and
now projecting the whole estate (4,559 capabilities) into **outcome lanes** so an
agent can go from intent → files without knowing 2,400 skill names.

## Lanes

`security-review`, `revenue-gtm`, `content-publishing`, `design-ux`,
`media-production`, `docs-knowledge`, `research-intel`, `data-analytics`,
`infra-ops`, `code-engineering`, `business-ops`, `agent-engineering`, `misc`.

Classification is deterministic (`rig_capabilities/taxonomy.py`): ordered
id-token rules — first match wins, rule order is precedence — then a
description-regex fallback, then kind defaults (hooks/loops → agent-engineering).
Nothing is dropped: unclassifiable assets land in `misc` (regression-tested).

## Surfaces

| surface | what |
|---|---|
| `./bin/rig-capabilities outcomes` | lane × kind counts |
| `./bin/rig-capabilities tree` | rebuild `tree/<outcome>/<kind>/<id>` symlink farm + per-lane INDEX.md |
| `./bin/rig-capabilities route "<intent>"` | intent → ranked lanes + top capabilities (idf-weighted) |
| MCP `capabilities_route` / `capabilities_outcomes` | same, for any wired agent |

`tree/` is generated (gitignored); rebuild after `reindex`. Start at
`tree/AGENT-INDEX.md`; every leaf symlink points at the real asset directory,
so reads follow through to exactly what the harnesses load.

## Honest limits

- Token rules are heuristic; `misc` (≈900, mostly one-off commands) is a
  backlog signal, not a filing error. Add a token to `RULES` to promote.
- Routing ranks lanes by peak idf-weighted id match; it is a compass, not a
  ranking oracle — follow with `capabilities_search` / reading the INDEX.md.
- Cross-root duplicates are resolved by source preference
  (canonical > claude-skills > agents-skills > …), so the tree shows the copy
  the loader would win with.
