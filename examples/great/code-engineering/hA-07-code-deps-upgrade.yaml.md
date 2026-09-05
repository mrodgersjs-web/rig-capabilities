---
name: great-hA-07-code-deps-upgrade
lane: code-engineering
exemplar_of: hA-07-code-deps-upgrade.yaml
description: >-
  A dependency upgrade separated into risk tiers, with security census, per-tier verification, lockfile review, and one-at-a-time runtime majors.
---

# hA-07 dependency upgrade — tiers before velocity

## Input

Upgrade a pnpm application using `package.json` and `pnpm-lock.yaml`. Capture outdated packages and audit findings, classify each package once into dev-only, patch, minor, or runtime-major, and review the changelog and callers for the lone runtime major.

## Output

```console
$ pnpm outdated --format json > .rig/deps/outdated-before.json
$ pnpm audit > .rig/deps/audit-before.txt
$ pnpm install --frozen-lockfile
Lockfile is up to date, resolution step is skipped
$ pnpm test && pnpm typecheck && pnpm build
```

Commits appear in dev-only → patch → minor → single runtime-major order. `verify-runs.txt` records the three verification exits after each tier. `lockfile-review.txt` accounts for additions, removals, duplicate majors, and the final lockfile SHA; `audit-after.txt` shows HIGH/CRITICAL `2 -> 0`; `smoke.txt` captures the application health path.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-07-code-deps-upgrade | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-07-CODE-DEPS-UPGRADE" and any(.goal.gates[]; .id == "2.4" and .failure_tier == "degrade")'
true
```

No `--force`, `--legacy-peer-deps`, or mixed-major batch is hidden. A red tier is reverted or dated in `LEDGER.md`, never forced through.
