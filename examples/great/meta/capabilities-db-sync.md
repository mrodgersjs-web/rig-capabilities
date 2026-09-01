# Great example — capabilities-db-sync

Run: db-sync after a 4,687-asset reindex.

- Upserts: assets 4687, packs 118, ratings 41. Post-count via psql: 4687. Delta: 0.
- When the db was briefly down, the run printed pg_isready output and returned RED — no silent SKIP, no "will retry later" fiction.
- Drift check baked in: `.index.json count` vs `select count(*)` quoted side by side.

Mirror discipline: numbers come from the database query, never from the sync log's self-report.
