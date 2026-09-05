---
name: great-codeql
lane: security-review
exemplar_of: codeql
description: >-
  A database-backed CodeQL scan that proves extraction quality, resolves an explicit query suite, and treats zero findings as a result to investigate rather than a security verdict.
---

# CodeQL — quality-gated scan

## Input

Scan a Python service at `/work/payments-api` in `important-only` mode. Put the database, diagnostics, suite, raw SARIF, and filtered SARIF under one resolved `OUTPUT_DIR`; reuse no database until its language and creation metadata are shown.

## Output

The run records the build method in `build.log`, verifies `codeql.db/codeql-database.yml`, creates project-specific source/sink extensions, and analyzes an explicit `important-only.qls`. A successful transcript includes both database-quality evidence and a nonzero suite query count:

```console
$ python3 capabilities/skills/codeql/scripts/check_db_quality.py "$OUTPUT_DIR/codeql.db" --source-root /work/payments-api
Database quality: PASS
$ uv run --no-project capabilities/skills/codeql/scripts/verify_query_suite.py "$OUTPUT_DIR/raw/important-only.qls"
Resolved 143 queries from .../important-only.qls
```

Analysis uses the suite path, never a pack name whose default filters can silently drop queries:

```console
$ codeql database analyze "$OUTPUT_DIR/codeql.db" "$OUTPUT_DIR/raw/important-only.qls" --format=sarifv2.1.0 --output="$OUTPUT_DIR/raw/results.sarif"
```

## Acceptance

- `check_db_quality.py` exits 0 and reports extracted source counts consistent with the target.
- `verify_query_suite.py` exits 0 with at least one resolved query.
- `results/results.sarif` parses as SARIF 2.1.0; zero alerts are reported only with both quality checks attached.
