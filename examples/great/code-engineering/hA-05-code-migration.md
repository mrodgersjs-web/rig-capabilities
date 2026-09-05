---
name: great-hA-05-code-migration
lane: code-engineering
exemplar_of: hA-05-code-migration.yaml
description: >-
  A clean client-library cutover whose callers are counted before edits, mechanically migrated, proven free of the old surface, and rollback-checked on a scratch branch.
---

# hA-05 code migration — every caller named

## Input

Migrate `payments.v1.Client` to `payments.v2.Client` using the versions pinned in the manifest and lockfile. Census production, test, and tooling imports with both direct-import and module-reference patterns. Choose a big-bang cutover only because the complete caller set is local and the target API is backward compatible.

## Output

```console
$ grep -rn 'payments\.v1\|from payments import v1' src tests scripts > .rig/migrate/callers.txt
$ grep -rn 'payments\.v1\|from payments import v1' src tests scripts > .rig/migrate/cutover-proof.txt; test ! -s .rig/migrate/cutover-proof.txt
$ pytest -q
312 passed
```

The AST-aware recipe and dry-run sample live under `.rig/migrate/codemods/` and `codemod-samples/`. `shims.md` is empty. `rollback.txt` records a scratch-branch revert of the migration range and a successful build; three named payment flows are captured in `smoke.md`.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-05-code-migration | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-05-CODE-MIGRATION" and any(.goal.gates[]; .id == "3.4" and .failure_tier == "halt")'
true
```

Any residual old import, terminal compatibility shim, red verification command, or unexercised rollback blocks a complete-cutover verdict.
