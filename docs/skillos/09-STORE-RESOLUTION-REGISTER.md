# Store Resolution Register — `skillos check --stores`

Snapshot under conservation: `docs/skillos/universe.jsonl`, n=**5004** rows at `984d60f`.
The independent frozen-U check parsed both `git show HEAD:docs/skillos/universe.jsonl` and
the working copy: each had 5004 rows, their ordered `(kind,id,sha)` sequences matched, and
the Goal Card formula
`sha256("\n".join(sorted(f"{kind}\t{id}\t{sha}")) + "\n")` produced
`c3c5879fd6f3a23b64a2c2aa7295d00e2cba38ac66c5e7e0d10287ac037bb9af` for both.
`git show 984d60f:docs/skillos/universe.jsonl` produced the same sequence and digest.
The whole-file hash is deliberately not used because `store` is mutable.

The committed-history portion reproducible here is 4993 rows at `71af341` (digest
`4fa6a635c8e70d76d56c2080243fbffcc3bb223bc2dc7a8f9fc11688e7e04a05`) to 5004 at
`984d60f`: 188 triples retired, 199 introduced, net +11. The Goal Card's earlier 4919
live-walk point is not independently reproducible from committed universe history because
`docs/skillos/universe.jsonl` does not exist at `71af341^`. The Goal Card remains locked;
this register records that evidence boundary instead of editing it.

Gate state after this register: **still RED**, honestly.

| current field | live value |
|---|---|
| `valid_store_count` | **300** — 137 licence-cleared blobs + 163 recipe-verified rows |
| `invalid_store_count` | **4704** |
| `store_counts` | blob 139, recipe 293, unresolved_bundle 2425, unresolved 2147 |
| `licence_denied` | `skill/codeql`, `skill/evidence-retrieval-citations-gate` — `blob` receipts whose *stored* bytes the ledger refuses |
| `unrestorable_blobs` | `[]` — nothing cleared is missing from the warehouse |
| recipe groups / fetches / verified rows | 6 / 6 / 163 |
| `licence_problems` | `[]` |

Measured post-regen at `7f69703` in a clean worktree. The recipe lane is a live network probe, so
`valid` = 137 + rows verified that run and `invalid` = 4867 − that number; the blob lane is offline
and stable at 137 of 139 receipts. `09-STOCKTAKE-AND-DIRECTIVE.md` §1 carries the offline column
beside this one and §5 the worktree recipe that reproduces both.

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

## Unresolved-origin/status bucket and the full denominator

The origin/status probe reports **4,571 rows with unresolved status** for store resolution:
2,425 `descriptor_only` rows plus 2,146 rows with no origin-backed store. This is not the
full count of rows with no currently restorable store.

| current classification | rows | what the probe established |
|---|---:|---|
| `descriptor_only` | 2,425 | descriptor/status classification only |
| no origin-backed store | 2,146 | origin/status classification only |
| pinned recipe, fetch fails | 130 | `git fetch` cannot retrieve the pinned commit |
| licence-refused canonical bundle | 1 | the licence ledger does not clear these bytes for archiving |
| stored-drift `blob` receipts | 2 | the ledger denies the *stored* digest (`archive_allowed: false`); the live content is cleared, the archived bytes are not |

Therefore **4,704** rows have no currently restorable store:
4,571 unresolved-origin/status + 130 pinned-but-unfetchable + 1 licence-refused + 2 stored-drift.
The universe's raw store statuses contain 2,425 `unresolved_bundle` and 2,147 `unresolved`;
the latter includes the one licence-refused row. The two drift rows sit in `blob` 139, **not** in
`unresolved` — which is exactly why the earlier 4,702 came up two short of the gate's own count.
The probe assigns no cause beyond the reported origin/status classifications.

For the 4,571 unresolved-origin/status rows, two lawful routes exist, both owner decisions:

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

- All 130 payloads match their snapshot SHA12 **from the pinned commit itself**:
  2026-09-05 re-probe ran `git show 0a54375…:<store.path>` for all 130 rows in the local
  clone — 130/130 SHA12 digest-match, 0 mismatch. Bytes are provable; only the server
  refuses the object.
- Origin was fetched read-only; **24 published refs** scanned with `git ls-tree -r`.
  Blob-level comparison (`git hash-object` vs tree OID): **0 of 130 paths exist at any
  published ref**. The pinned commit exists locally only; the lineage lives on the local
  branch `feat/studio-monorepo` — re-probed 2026-09-05 at tip `865a1eb6` (earlier
  observation `cc37fdd8`; branch has moved), with
  `git merge-base --is-ancestor 0a54375 feat/studio-monorepo` true. Never pushed.
- No `LICENSE` file at that repo root → no licence-cleared blob path either.
- 2026-09-05: the one branch-push closure route was Gate-P-scanned and **fails**:
  gitleaks over `0a54375 --not --remotes=origin` (68 commits, ~117 MB) reports 1,639
  findings over a 72-commit / 7,390-object blast radius (gitleaks exits 0 with leaks —
  the report, not the rc, is the evidence). Redacted triage: 1,623 generic-api-key hits
  over 157 distinct strings in proof/registry JSONs (class unverified); two
  linkedin-client-secret (16-char) + two jwt-shape hits in test/probe files would be
  NEWLY exposed; one **sk_live-prefixed** string is already reachable on published refs
  of that private repo (rotate-or-prove-fake owed regardless of any push). Route
  BLOCKED, no Gate-D filed, push not executed. This group stays red.
  Detail: `~/.rig/state/loops/runs/git-push-safety-loop-20260905T184000Z-p19/artifacts/`.


So the pinned recipe stays pinned and red, and the push route is itself blocked by
the secret scan above: reviving it needs a human class verdict on the flagged strings
first — rotating or proving-fake includes the sk_live-shaped string already published
on that repo's live refs. Not: re-pointing the row at a commit that happens to be
published today — that would rewrite a receipt to make a gate go green.

## Deliberately not done

- No `skillos dump` against the locked snapshot. `dump` re-derives rows from today's tree;
  conservation is defined against the frozen file.
- No owner⇒licence inference for **external** assets: RIG owning an account says nothing
  about the licence of someone else's repository. For canonical paths the root MIT grant is
  used as an authorship claim — see "Canonical assets: the warehouse archive gate" in
  `docs/SOURCE-LICENSE.md`, including what that claim does and does not prove.
- No self-referential `file:`/`grep: SKILL.md` witnesses to make `witness --strict` green.
  This bullet recorded `witness --strict` red with
  `missing_fixtures: [prime-jake-pai, rig-memory-os]` — both **untracked work from other
  sessions**, whose stated capability is a live authenticated call
  (`memory.get_context_package`), not a text pattern. **Status changed by their owner, not
  by us:** both directories are now absent from disk (`ls capabilities/skills/prime-jake-pai`
  → No such file), so the witness set is the 29 tracked canonical skills and
  `witness --strict` reports `ok: true, ran: 29, missing_fixtures: []`, exit 0. The same
  removal is why the shared root and a fresh worktree now both index 5005: the four untracked
  canonical assets that pushed it to 5006 are gone. Nothing was made green by writing a
  witness; if those skills return, the honest witness is still a bounded smoke test against
  the registered Memory OS connection, owned by whoever owns them.
- Store-gate consequence: with doors 50, `witness --strict`, `orphan-replay` and
  `provenance --deny tesslio/cli` all exit 0, **`check --stores` is the only red DONE-TEST
  left** in the Goal Card's five-command block.

## Archive gate: clearance is bound to bytes

`scripts/blob_license_ledger.py` → `docs/skillos/blob-license-ledger.json` → consumed by
`_licence_map` in `rig_capabilities/skillos.py`. Every entry states its basis. Counts below are
from the ledger as committed now: 142 rows over 140 distinct `(kind,id)` canonical assets,
139 archive-cleared. It was regenerated in a detached worktree of the committed tree —
tracked files only, the shared 139-blob warehouse copied in — not in the shared worktree,
because the shared `.index.json` had absorbed four canonical assets that are not tracked here
(`prime-jake-pai`, `rig-memory-os`, `prime-jake-memory.ts`, `rig-prime.ts`), and the shared
directory additionally holds ambient untracked files inside otherwise-clean asset
directories, which shifts dir-scope digests. A ledger generated against either would license
content this repository does not contain.

| basis | entries | archive allowed |
|---|---|---|
| repo `LICENSE` (MIT, RIG / mrodgersjs-web), no upstream marker in or beside the asset | 137 | yes |
| asset's own `LICENSE.txt` (security-threat-model, Apache-2.0) | 1 | yes |
| frontmatter `license: MIT` (rig-office-docs) | 1 | yes |
| upstream marked, no licence found (`rig-lattice-system` → `github.com/rodgemd1-lgtm/rig-deviator`) | 1 | **no — needs_review** |
| restored snapshot; no licence evidence travels with the bytes (`skill/codeql`, `skill/evidence-retrieval-citations-gate` drift blobs) | 2 | **no — needs_review** |

The last row is the M1 fix biting its own artifact: under the old classifier these two drift
blobs cleared via the repo MIT fallback, which a restored single file can always reach because
a restored file has no sibling `LICENSE` by construction. The committed artifact — the thing
`_licence_map` actually trusts — had to be regenerated for the fix to be real at runtime.

Residual risk, named: 137 of those rows rest on the repo's own MIT grant with no
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
**live canonical assets** (140 distinct `(kind,id)`, tracked-only) and computes the digest
`_store_for` would file, without writing. Stored content whose live bytes have since drifted is
reported by the generated `stored_content_drift` field rather than prose — today two rows,
`skill/codeql` and `skill/evidence-retrieval-citations-gate`, both carried as
`content: "stored_snapshot"` and both denied. File blobs are
classified at `<tmp>/payload`, not at the directory, which is where frontmatter is readable.

Executed today: the denied blob `92aad1c6…` was removed from the warehouse and its universe
row returned to `unresolved` (identity `(kind,id,sha)` untouched). `check --stores` reports
**300 of 5004** stores restorable — 137 licence-cleared blobs of the 139 filed, 163
recipe-verified — and stays red until every remaining row is either cleared with a licence basis
or given a tested immutable recipe. `github.com/mrodgersjs-web/rig-gtm-studio-v2@0a54375…`
(130 rows) is still red: that commit is unpublished, so no recipe can fetch it and none was
invented.
