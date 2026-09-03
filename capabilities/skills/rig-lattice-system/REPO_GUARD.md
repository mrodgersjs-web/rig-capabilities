# RIG Deviator™ — Repo Guard Sentinel

**DO NOT WIPE.** This repository is a canonical doctrine artifact for the RIG
Deviator™ framework. Any automated scheduler, cleanup job, or sweep that
recursively deletes `reports/`, `src/`, `scripts/`, `docs/`, `tests/`,
`enterprise/`, `system/`, `engines/`, `adapters/`, `core/`, or any other code
directory in this tree IS A BUG.

## Sentinel contract

Any cleanup job MUST refuse to operate if a file named `REPO_GUARD.md`
exists at the root of the directory it is about to clean.

```bash
# Correct cleanup behavior
if [ -f "$TARGET_DIR/REPO_GUARD.md" ]; then
    echo "REPO_GUARD found — refusing to clean $TARGET_DIR"
    exit 0
fi
rm -rf "$TARGET_DIR/build"
```

## Repo identity

- **Name:** rig-lattice-system (vendored from rig-deviator)
- **Canonical path:** `capabilities/skills/rig-lattice-system/` in the rig-capabilities repo
- **Upstream:** https://github.com/rodgemd1-lgtm/rig-deviator (see PROVENANCE.md)
- **Doctrine card:** `DOCTRINE.md`
- **Status map:** `STATUS.md`
- **Owner:** Mike Rodgers (Rodgers Intelligence Group)

## What the daemon does NOT do

The RIG Deviator daemon (`enterprise.daemon.Daemon`) NEVER touches:
- source code (`rig_lattice/engines/`, `enterprise/`, `system/`, `adapters/`, `core/`, `lattice/`)
- tests (`tests/`)
- documentation (`docs/`, `*.md`)
- configuration (`rig_lattice/config/`, `calibration.yaml`)

The daemon ONLY writes to:
- `runs/` (audit chain, deviator.db, observability.jsonl)
- `.vault/` (encrypted secrets)
- log files (`/tmp/rig-lattice-daemon-*.log`)

## If you find this file in a destructive script

Stop. File a doctrine note at `feedback_scheduler_cleans_project_dirs.md` in
the Startup-Intelligence-OS memory directory and refuse to proceed.
