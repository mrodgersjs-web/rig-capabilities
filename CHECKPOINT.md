# CHECKPOINT — B1 Capability Atlas (commit blocked by git guard)

Date: 2026-10-01 (commit attempt 2026-10-02T02:2xZ UTC)
Branch: fm/rig-car-b1-capability-atlas (current, pre-existing)
Worktree: /Users/rig128gb/Developer/rig-capabilities-worktrees/rig-car-b1

## Status

All B1 work is complete, verified, and STAGED. `git commit` is blocked by the
RIG git guard: this worktree path is outside every registered canonical root.
Per instruction, the refusal is recorded verbatim below and everything is left
staged. No push attempted. Registration of the worktree (or a commit from the
canonical rig-capabilities checkout) is the owner's call.

## Verbatim guard refusal (git commit, exit 1)

```json
{
  "code": "unregistered_repository",
  "event": "pre-commit",
  "evidence": {},
  "message": "Git operation is outside every registered canonical root.",
  "repository": null,
  "repository_id": null,
  "schema": "rig.github_steward.git_guard.v1",
  "status": "BLOCK"
}
```

## Staged files

- `bin/rig-capabilities` (modified) — `atlas resolve` CLI
- `rig_capabilities/server.py` (modified) — `capabilities_atlas` MCP tool
- `data/control_plane_owners.csv` (new) — 8 planes, one owner per state, real artifact evidence paths
- `rig_capabilities/atlas.py` (new) — resolve() + AtlasConflict
- `tests/test_atlas.py` (new) — 6 tests incl. planted failures
- `proof/atlas-b1-proofpacket.json` (new) — sealed ProofPacket
- `proof/atlas-b1-d85-classification.json` (new) — D85 stateless A1 fast-path classification
- `CHECKPOINT.md` (this file)

## Verification recap (all run this session)

1. First proof exits 0, 3 non-empty keys, real register ids, one owner per state
2. `grep -c` plane names = 8
3. Planted dual-owner → exit 3, conflict packet names both claimants
4. Planted zero-owner → exit 3
5. Register regression 59/59 OK; `register --help` exit 0; no new db/index artifacts
6. `capabilities_atlas` live on MCP stdio tools/list + tools/call
7. All 8 evidence_path values verified to exist on disk
8. ProofPacket `proof/atlas-b1-proofpacket.json`, proof_hash
   `sha256:5ecd5ab7ae3e3c06537a75ef8008a421df1259223fb98c760fca9e81cdf2bb74`,
   recomputes (sort_keys JSON minus proof_hash field), verdict TRUE
