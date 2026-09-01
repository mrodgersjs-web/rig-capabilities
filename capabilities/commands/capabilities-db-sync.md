---
name: capabilities-db-sync
description: Upsert the capability index, agent packs, and ratings into the Postgres mirror (rig-dev-db) so SQL-side analytics see the same truth the index serves.
argument-hint: ""
allowed-tools: Read, Bash
category: meta
outcome: "meta: index and database agree on asset counts within one sync"
done_when:
  - file:capabilities/commands/capabilities-db-sync.md
  - file:examples/great/meta/capabilities-db-sync.md
  - grep:capabilities/commands/capabilities-db-sync.md:The DB is a mirror
great_example: examples/great/meta/capabilities-db-sync.md
quality_floor: 0.7
---

# capabilities-db-sync

1. Call `capabilities_db_sync` (optional `dsn` override; default reads the local dev-db).
2. Report per-table upsert counts — assets, packs, ratings — and the Postgres row count for `capabilities.assets` after sync.
3. If the count diverges from `.index.json`'s `count`, that drift is the finding: name it, do not pad numbers to match.
4. A failed connection is a RED result, not a SKIP: quote pg_isready output.

The DB is a mirror. The repo remains the source of truth.
