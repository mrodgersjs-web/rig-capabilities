# Stocktake and directive — store gate at `984d60f`+

## 1. Live gate state

`./bin/rig-capabilities skillos check --stores` → exit 1.

| field | value |
|---|---|
| `n` (frozen snapshot rows) | 5004 |
| `ok_keys` | true — no `(kind,id)` lost; identity conservation holds |
| `ok_stores` | **false** |
| `valid_store_count` | 302 (139 blobs + 163 recipe-verified rows) |
| `invalid_store_count` | 4702 |
| `store_counts` | blob 139, recipe 293, unresolved_bundle 2425, unresolved 2147 |
| `recipe_group_count` / `fetch` / `verified` | 6 / 6 / 163 |
| `licence_problems` | none |

Three `missing_evidence` groups carry the whole red:

| count | why |
|---|---|
| 2425 | `descriptor_only` external skills — not in a clean origin-backed git tree, so no recipe and no licence-cleared blob |
| 2146 | no licence-cleared blob and no verified retrieval recipe |
| 1 | canonical asset whose content the licence ledger does not clear for archiving |

The third row is the licence gate working. The refused asset is `skill/rig-lattice-system`
(`source: canonical`, `payload_scope: bundle`): its bytes are not cleared by the ledger, so
`_store_for()` declines to write it and the row stays `unresolved` with a named reason. The
139 blobs counted by the gate exclude this licence-denied asset.

## 2. The one failing recipe group

```
url    https://github.com/mrodgersjs-web/rig-gtm-studio-v2.git
commit 0a54375578e0592157920f0d76778955b912dae0
keys   130
stderr fatal: remote error: upload-pack: not our ref 0a543755…
```

Checked read-only, not assumed:

- the commit exists locally in a `rig-gtm-studio-v2` checkout beside this repo (detached, on
  `feat/studio-monorepo`), and 130/130 payloads still hash-match their snapshot SHA12 on disk;
- `git branch -r --contains 0a543755` → no remote branch contains it;
- 24 published refs on `origin` were scanned with `git ls-tree -r` + `git hash-object`:
  **0 of 130** paths exist at any published ref;
- no `LICENSE` file in that checkout.

So the recipe is red and cannot be repaired without publishing that history, and the blob route
needs licence evidence that does not exist. GitHub ownership is not a licence.

## 3. The three lawful closing routes

| route | covers | needs |
|---|---|---|
| A — publish the pinned history (push `0a543755` so it is reachable from a published ref on the remote the recipe names) | **130 rows** — the one failing recipe group, `keys: 130` | Gate-P + Gate-D on a *different* repo |
| B — vendor the external corpora into a licence-backed, origin-clean checkout | **4,571 rows** — 2,425 `descriptor_only` + 2,146 with no origin-backed tree | licence evidence per corpus, then `skillos restock` |
| C — resolve `skill/rig-lattice-system` (canonical bundle the ledger refuses) | **1 row** | licence evidence for that content, followed by a regenerated ledger (`scripts/blob_license_ledger.py`) — **or** an immutable retrieval recipe whose restore command is tested. A hand-written ledger row without evidence is a gate bypass |

130 + 4,571 + 1 = 4,702 = `invalid_store_count`. Route B cannot absorb route C: vendoring an
external corpus says nothing about the licence of our own canonical bundle. Route C cannot
absorb B either — a licence grant for our content does not make third-party corpora restorable.

Anything else — loosening the gate, counting `descriptor_only` as stored, re-pointing existing
`blob`/`recipe` rows at today's tree — is redefining the metric, not closing it.

## 4. Licence gate (what the code now guarantees)

- `_licence_map()` maps `blob_sha256 → catalog_sha` only for entries that are well-formed and
  `archive_allowed is True`; malformed, duplicated-conflicting, or non-boolean values deny and
  are named. Absent ledger clears nothing.
- `_universe_store_valid()` refuses a blob row unless the ledger maps *that content* to
  *that* snapshot sha — an old grant cannot bless new bytes under the same id.
- `_store_for(root, asset, licence=…)` refuses **before writing**: no warehouse byte is
  canonicalised without a grant, so `dump_universe()` and `restock_stores()` cannot
  resurrect a denied asset.

Proof the gate can fail: `python3 scripts/check_license_gate_plant.py` → exit 0, printing
`planted on agent/rig-lattice-router.md -> denied=True named=True`, then
`restored -> re-granted=True problems=(none)`, tree clean. It withdraws a real grant by making
`archive_allowed` non-boolean, asserts `_licence_map` stops mapping the digest *and* that
`check --stores` names it, restores the bytes, and verifies against git.

## 5. Reproduce

```
python3 -m pytest tests/test_skillos_v5.py -q
python3 scripts/check_license_gate_plant.py            # exit 0, RED→GREEN shown above
./bin/rig-capabilities skillos check --stores          # exit 1, numbers in §1
./bin/rig-capabilities skillos check                   # exit 0; keys/receipts valid, stores remain red
```

## 6. Directive

1. v5 stays open until `ok_stores` is true. No metric redefinition.
2. Do not run `skillos dump` to "fix" stores: it re-derives receipts from today's tree.
   Receipts and `store` are the only mutable fields; `(kind,id,sha)` is frozen.
3. Route A is the smaller lift — 130 rows for one push to another repo, under Gate-P/Gate-D
   there. Route B requires per-corpus licence evidence before any vendoring. Route C requires
   licence evidence for `skill/rig-lattice-system`, followed by a regenerated ledger, or an
   immutable retrieval recipe whose restore command is tested. A hand-written ledger row is a bypass.
4. Verify `git status` and `git log` before committing on a shared branch. Give each concurrent
   agent its own Git worktree checkout of the same commit. `.lanes.json` does not do this — it is a
   semantic `asset id -> outcome lane` overlay (`{"ads-meta": "data-analytics", …}`). Neither it nor
   `.index.json` is tracked here. The hazard is the per-root `.index.json`: two agents sharing one
   root share one index, and whichever `reindex` lands last decides the other's key-gate result.
   Measured here: the shared root's index reached
   5006 assets by absorbing four untracked canonical assets, while a fresh clone of the same
   commit yields 5004 with 140 canonical. Regenerate anything content-addressed (license ledger,
   witnesses) only in a worktree whose tracked tree is the intended candidate.
