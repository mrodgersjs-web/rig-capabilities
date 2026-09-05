---
name: great-hA-10-schema-design-yaml
lane: design-ux
exemplar_of: hA-10-schema-design.yaml
description: Reference exemplar for an access-pattern-led PostgreSQL schema design with reversible migration and query-plan evidence.
---

# hA-10-schema-design.yaml — great example

## Input

Design an alteration for a PostgreSQL 16 order service. The two dominant reads, write rate, twelve-month row growth, and live-table status are recorded in `.rig/schema/access-patterns.md` before any DDL is authored. The migration adds constrained columns and an index without accepting an unplanned table rewrite.

## Output

The session produces reviewed DDL, `.rig/schema/index-map.md`, `.rig/schema/lock-analysis.md`, and one plan per top query under `.rig/schema/plans/`. It captures a scratch-database up/down/up cycle in `.rig/schema/reversibility.txt` and explicitly names any irreversible operation.

```console
$ migrate up && migrate down && migrate up
# expected: all three commands exit 0 on the named scratch database

$ psql "$SCRATCH_DSN" -c 'EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE account_id = 42 ORDER BY created_at DESC LIMIT 50'
# expected: the saved plan uses the access-pattern-derived index, not an unexpected Seq Scan

$ ./bin/rig-capabilities goal-spec --stem hA-10-schema-design
# expected: the canonical harness resolves with its schema-design gates
```

## Acceptance

- Every top read/write maps to an index or a written sequential-scan justification.
- Every foreign key has explicit `ON DELETE` behavior and each nullable or JSONB column has a reason.
- The migration is green up/down/up, live locks are analyzed, and representative `EXPLAIN (ANALYZE, BUFFERS)` output is retained.
- No live migration is applied; that remains a Gate-D action.
