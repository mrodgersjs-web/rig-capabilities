# Store Resolution Register — `skillos check --stores`

Snapshot under conservation: `docs/skillos/universe.jsonl`, n=**5004** rows at `984d60f`.
Identity digest — sha256 over sorted `kind\tid\tsha` triples —
`c3c5879fd6f3a23b64a2c2aa7295d00e2cba38ac66c5e7e0d10287ac037bb9af`.
Deliberately not the whole-file hash: `store` is a mutable column (this run wrote 93 of
them) and a file hash would stale on the next legitimate `restock`.
History read from the committed files: 4919 (2026-09-04 live walk) → 4993 at `71af341`
(digest `4fa6a635c8e70d76…`) → 5004 at `984d60f`; net +11 keys, 188 triples retired /
199 introduced (91 renames, ~95 edited canonical assets, +11 new keys).

Gate state after this register: **still RED**, honestly.

| | before | after |
|---|---|---|
| valid stores | 210 | **303** |
| invalid stores | 4794 | **4701** |
| blob | 140 | 140 |
| recipe (verified by fetch) | 70 keys / 5 groups | **163 keys / 6 groups** |
| unresolved + unresolved_bundle | 4664 | **4571** |

`./bin/rig-capabilities skillos restock` produced the delta: 93 `great` exemplars moved
from `unresolved_bundle` to a verified `git` recipe. They are files of this repository
(`examples/great/**`), committed and published at `984d60f`, so the recipe
(`https://github.com/mrodgersjs-web/rig-capabilities.git` @ `984d60f…` + path) fetches
and the archive hash-matches the snapshot SHA12.

## What `restock` may and may not touch

`restock_stores()` (in `rig_capabilities/skillos.py`) writes a `store` only when it is
proven by restore/fetch at that moment, and:

- **`(kind,id,sha)` is never rewritten.** Order and identity verified byte-comparable
  against the committed file after the run.
- **Already-pinned receipts are immutable.** Rows already `blob` or `recipe` are skipped
  outright — a recipe that has since gone unfetchable stays pinned exactly as recorded
  and is reported red by `check --stores`. It is never silently re-pointed at today's
  tree. Verified: all 200 previously pinned recipe rows came back byte-identical.
- Candidates are only `unresolved`, `unresolved_bundle`, `missing_store`.

Invariant is pinned by `tests/test_skillos_v5.py::test_restock_never_rewrites_pinned_receipts`.

## Rows with no lawful store, by source

4571 rows have no restorable store. Probed payload-by-payload (`_payload_path` →
`_git_top` → `_git_meta`), not inferred from counts:

| source | rows | payload state on disk | missing evidence | who can supply it |
|---|---|---|---|---|
| `claude-skills` | 1699 | installed copies, **no git root** | upstream `git url + commit + path`, or a licence-cleared blob | installer provenance / upstream repo owner |
| `claude-commands` | 887 | no git root | same | same |
| `claude-agents` | 582 | no git root | same | same |
| `codex-agents` | 549 | no git root | same | same |
| `hermes-skills` | 544 | no git root | same | same |
| `hermes-agents` | 123 | no git root | same | same |
| `codex-skills` | 85 | no git root | same | same |
| `intel-corpus` | 73 | no git root | derived notes: ours → licence is ours, but needs a per-path grant statement | RIG (Mike) |
| `agents-skills` | 21 | no git root | same as `claude-skills` | upstream |
| `claude-hooks` | 5 | no git root | same | upstream |
| `great` | 0 | 93 resolved this pass | — | — |
| 2 stragglers | 1+1 | inside this repo, dirty at probe time | clean path at a published commit | re-run `restock` once those paths are committed |

4568 of the 4571 have **no git root at all**: path+SHA12 alone, which the Goal Card
explicitly refuses as a receipt. Two lawful routes exist, both owner decisions:

1. **Upstream provenance.** Record `git url + commit + path` from wherever each asset was
   installed. `scripts/` has no install-time origin ledger for these roots today; the
   `.install.json` ledger records harness targets and SHAs, not origins. Needs the
   provenance recorded at install time, retro-fit from the vendor's registry.
2. **Licence-cleared blob.** Only for content whose licence permits local archiving
   (`docs/SOURCE-LICENSE.md` is the standing doctrine). GitHub-account ownership is **not**
   licence evidence; a per-source licence citation or owner grant is.

## The 130-row `rig-gtm-studio-v2` recipe group — unrecoverable as pinned

```
url    https://github.com/mrodgersjs-web/rig-gtm-studio-v2.git
commit 0a54375578e0592157920f0d76778955b912dae0
error  fetch failed: remote error: upload-pack: not our ref
```

Evidence gathered, not assumed:

- All 130 payloads still hash-match their snapshot SHA12 on disk in the `rig-gtm-studio-v2` working copy.
- Origin was fetched read-only; **24 published refs** scanned with `git ls-tree -r`.
  Blob-level comparison (`git hash-object` vs tree OID): **0 of 130 paths exist at any
  published ref**. The pinned commit exists locally only; the working branch
  (`feat/studio-monorepo`, HEAD `cc37fdd8`) was never pushed.
- No `LICENSE` file at that repo root → no licence-cleared blob path either.

So the pinned recipe stays pinned and red. Closing it needs either a push of that
commit to an HTTPS origin (Gate-D, and it is a different repository) or a licence
grant. Not: re-pointing the row at a commit that happens to be published today — that
would rewrite a receipt to make a gate go green.

## Deliberately not done

- No `skillos dump` against the locked snapshot. `dump` re-derives rows from today's tree;
  conservation is defined against the frozen file.
- No owner⇒licence inference for **external** assets: RIG owning an account says nothing
  about the licence of someone else's repository. For canonical paths the root MIT grant is
  used as an authorship claim — see "Canonical assets: the warehouse archive gate" in
  `docs/SOURCE-LICENSE.md`, including what that claim does and does not prove.
- No self-referential `file:`/`grep: SKILL.md` witnesses to make `witness --strict` green.
  `witness --strict` is red with `missing_fixtures: [prime-jake-pai, rig-memory-os]` —
  both directories are **untracked work from other sessions** (untracked as of this
  writing), and their stated capability is a live authenticated call
  (`memory.get_context_package`), not a text pattern. `run_asset` reports
  `pass=false, ran=0` — honestly unrunnable. A real bounded smoke test against the
  registered Memory OS connection is the only acceptable witness; it belongs to whoever
  owns those skills.

## Archive gate: clearance is bound to bytes

`scripts/blob_license_ledger.py` → `docs/skillos/blob-license-ledger.json` → consumed by
`_licence_map` in `rig_capabilities/skillos.py`. Every entry states its basis; the counts are
from the committed ledger:

| basis | entries | archive allowed |
|---|---|---|
| repo `LICENSE` (MIT, RIG / mrodgersjs-web), no upstream marker in or beside the asset | 144 | yes |
| asset's own `LICENSE.txt` (security-threat-model, Apache-2.0) | 1 | yes |
| frontmatter `license: MIT` (rig-office-docs) | 1 | yes |
| upstream marked, no licence found (`rig-lattice-system` → `github.com/rodgemd1-lgtm/rig-deviator`) | 1 | **no — needs_review** |

Residual risk, named: 144 of those entries rest on the repo's own MIT grant with no
upstream marker nearby. That is authorship by absence of counter-signal, not proof. If any
of them is shown vendored, the flip is mechanical — ledger entry to `archive_allowed: false`,
blob out of the warehouse, universe row back to `unresolved`, all in one commit — and the
store gate goes red on that row rather than quietly keeping the bytes.

The ledger is keyed by `blob_sha256 → catalog_sha`, never by `(kind,id)`, so an old grant can
never bless different bytes filed under the same asset id. The gate fails closed and names
the reason: absent or unparseable ledger, digest/catalog_sha of the wrong width or alphabet,
`archive_allowed` that is not a real boolean, and the same digest granted twice against
conflicting snapshots. A grant is honoured only when `licence[blob_sha256] == row.sha`.

Archival IS the write, so the ledger runs first everywhere a blob could be created:
`dump` and `restock` pass the licence map into `_store_for`, which returns `unresolved` for
uncleared content instead of filing it. Nothing unlicensed ever reaches
`docs/skillos/warehouse/`. To keep that from freezing the pipeline, the generator inventories
**live canonical assets** (144) and computes the digest `_store_for` would file, without
writing; it also classifies every stored blob whose content has since drifted (3: codeql,
sarif-parsing, semgrep) from the bytes actually filed — file blobs at `<tmp>/payload`, not at
the directory, which is where frontmatter is readable.

Executed today: the denied blob `92aad1c6…` was removed from the warehouse and its universe
row returned to `unresolved` (identity `(kind,id,sha)` untouched). `check --stores` reports
**302 of 5004** stores restorable — 139 licence-cleared blobs, 163 recipe-verified — and
stays red until every remaining row is either cleared with a licence basis or given a tested
immutable recipe. `github.com/mrodgersjs-web/rig-gtm-studio-v2@0a54375…` (130 rows) is still
red: that commit is unpublished, so no recipe can fetch it and none was invented.
