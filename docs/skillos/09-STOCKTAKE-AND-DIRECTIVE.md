# Stocktake and directive — store gate at `984d60f`+

## 1. Live gate state

`./bin/rig-capabilities skillos check --stores` → exit 1. One authoritative snapshot, measured
post-regen at `7f69703` in a clean worktree (§5 reproduces it):

| field | `check` (offline) | `check --stores` |
|---|---|---|
| `n` (frozen snapshot rows) | 5004 | 5004 |
| `ok_keys` | true — no `(kind,id)` lost; identity conservation holds | true |
| `ok_stores` | **false** | **false** |
| `valid_store_count` | 137 | 300 (137 blobs + 163 recipe-verified rows) |
| `invalid_store_count` | 4867 | 4704 |
| `store_counts` | blob 139, recipe 293, unresolved_bundle 2425, unresolved 2147 | same |
| `licence_denied` | `skill/codeql`, `skill/evidence-retrieval-citations-gate` | same |
| `unrestorable_blobs` | none | none |
| `recipe_group_count` / `fetch` / `verified` | not probed | 6 / 6 / 163 |
| `licence_problems` | none | none |
| process exit | 0 | 1 |

The recipe lane is a live network probe, so both totals move with it: valid = 137 + rows verified
this run, invalid = 4867 − that number (163 here; 1 and 94 observed on other runs). The blob lane
is offline and stable: **137 valid of 139 `blob` rows.**

Where the 4,704 red rows of the `--stores` run sit:

| count | why |
|---|---|
| 2425 | `descriptor_only` external skills — not in a clean origin-backed git tree, so no recipe and no licence-cleared blob |
| 2146 | no licence-cleared blob and no verified immutable retrieval |
| 130 | the one failing recipe group of §2 (293 recipe rows − 163 verified) |
| 2 | `blob` rows whose **stored** bytes the ledger denies |
| 1 | canonical asset whose content the licence ledger does not clear for archiving |

The first two rows are route B of §3 and the 130 is route A; the last two rows are the licence gate
working, in two different ways, and together they are route C's 3.

`skill/rig-lattice-system` (`source: canonical`, `payload_scope: bundle`) is refused outright: its
bytes are not cleared, so `_store_for()` declines to write it and the row stays `unresolved` with a
named reason.

`skill/codeql` and `skill/evidence-retrieval-citations-gate` keep a `blob` receipt and the
digest-bound map denies it. Each stored digest has a ledger entry carrying
`archive_allowed: false`, basis *"restored snapshot carries no frontmatter licence, no licence file
and no upstream marker; the repo grant is not extended to stored bytes"*. The gate reports them as
`licence_denied`, never `unrestorable_blobs` — the ledger refuses these bytes; they are not
cleared-but-missing. So `blob 139` counts receipts and `valid 137` counts receipts the ledger
clears. The ledger's own totals agree: 142 entries, 139 `archive_allowed`, and all three refusals
named in `needs_review`.

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
| C — clear the three licence-refused rows: `skill/rig-lattice-system` (canonical bundle refused outright) plus the stored-drift receipts `skill/codeql` and `skill/evidence-retrieval-citations-gate` (`archive_allowed: false` on the stored digest) | **3 rows** | licence evidence for *that* content, followed by a regenerated ledger (`scripts/blob_license_ledger.py`) — **or** an immutable retrieval recipe whose restore command is tested. The two drift rows also close by re-filing the warehouse blob with the cleared current content, because the map is digest-bound. A hand-written ledger row without evidence is a gate bypass |

130 + 4,571 + 3 = 4,704 = `invalid_store_count` on the 163-verified run in §1; offline the 163
recipe rows join the red and it is 4,867. Route B cannot absorb route C: vendoring an external
corpus says nothing about the licence of our own canonical bundle or of bytes already in the
warehouse. Route C cannot absorb B either — a licence grant for our content does not make
third-party corpora restorable.

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

Proof the gate can fail: `python3 scripts/check_license_gate_plant.py` → exit 0, five proofs in
isolated temporary roots — `PASS a: withdraw skill/adversarial-verification-loop; gate_exit=1
denied=True named=True`, `PASS b: restore …; regranted=True specific_complaint_cleared=True`,
`PASS c: unlicensed fixture store=unresolved warehouse_files_written=0`, `PASS d` (missing and
malformed witnesses both named in one pass), and `PASS canonical-evidence: status_delta=none
input_sha256_delta=none`. It withdraws a real grant by making `archive_allowed` non-boolean,
asserts `_licence_map` stops mapping the digest *and* that `check --stores` names it, restores the
bytes, and verifies the canonical tree against git.

## 5. Reproduce

Every store-lane input is tracked — `docs/skillos/universe.jsonl`,
`docs/skillos/blob-license-ledger.json`, and the 139 blobs under `docs/skillos/warehouse/` — so a
clean worktree of the reviewed commit reproduces §1's blob numbers exactly. `.index.json` is
gitignored, per-root, and rebuilt from the live harness roots, so prepare it explicitly rather than
inheriting whatever the shared root last wrote:

```
git worktree add --detach /tmp/stocktake-repro 7f69703
cd /tmp/stocktake-repro
git status --porcelain                          # empty — the tracked tree is the candidate
./bin/rig-capabilities reindex                  # writes THIS worktree's .index.json
python3 -m pytest tests/test_skillos_v5.py -q   # 33 passed, 10 subtests
python3 scripts/check_license_gate_plant.py     # exit 0, the five proofs quoted in §4
./bin/rig-capabilities skillos check --stores   # exit 1, the --stores column of §1
./bin/rig-capabilities skillos check            # exit 0; keys/receipts valid, stores red
```

What does and does not reproduce:

- **Reproducible:** every store field except the recipe lane — `n` 5004, `blob` 139,
  `valid_store_count` 137 offline, the same two rows under `licence_denied`, `ok_stores` false.
- **Network-dependent:** `recipe_verified_count`, and through it `valid_store_count` and
  `invalid_store_count` on any `--stores` run.
- **Not a fixed number:** the reindex total. It scans the external harness roots (`~/.claude`,
  `~/.codex`, `~/.hermes`, `~/.agents`), which move independently of this commit — 5004, 5005 and
  5006 have all been measured. The reproducible key-lane assertion is `ok_keys: true` (every
  universe key resolves in the index or a verified receipt), never an index total.

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
   The total is a live-root measurement, not a property of the commit: the shared root once read
   5006 by absorbing four untracked canonical assets while a fresh clone of the same commit read
   5004, and at `7f69703` the shared root and a fresh worktree both read 5005 with 140 canonical.
   That the number moved again is the point — pin it by reindexing inside the worktree you are
   judging (§5), and regenerate anything content-addressed (licence ledger, witnesses) only in a
   worktree whose tracked tree is the intended candidate.
