# ASSUMPTIONS — named assumptions, each with the observation that would falsify it

Every assumption the build rests on, with an explicit falsifier. A falsifier is not a
worry; it is the concrete command or file inspection that, if it returns the stated
result, retires the assumption and triggers the named contingency. Receipts re-read
2026-09-01 where marked.

## A1 — The owner of this build is `rig-capabilities`

`/Users/rig128gb/Developer/rig-intelligence/registry/workstation-repositories.json:832-839`
registers `rig-capabilities` with `write_enabled: true`, `write_mode: code`,
`disposition: CANONICAL` (receipt re-read 2026-09-01). Registry policy sets
`repository_creation_default: deny`, so no new repository is created under any
circumstance.

**Falsifier:** the registry entry flips to `write_enabled: false` or
`disposition` leaves `CANONICAL`, or the registry names a different owner for this
capability class. Then stop and ask — the plan says a different owner needs an explicit
registry policy revision first; do not create a repo.

## A2 — Weekly scheduling stays dormant in-repo

The weekly Realign job ships as `.context/realign/cron-job.json`, staged DORMANT.
`~/.hermes/cron/jobs.json` and `~/.hermes/scripts/rig-weekly-evolution.sh` are never
modified: the fleet is frozen and registering or unpausing a recurring job is a separate
Gate-D action.

**Falsifier:** an enabled weekly-realign entry appears in `~/.hermes/cron/jobs.json`, or
`rig-weekly-evolution.sh` references `realign` without a Gate-D approval on record. Then
the scheduler was mutated without approval — revert the scheduler change, keep the
dormant in-repo artifact.

## A3 — The three truncated cards stay `TRUNCATED_AT_SOURCE` unless a longer exact-title copy is recovered

Cards 1, 6, and 9 end mid-content on disk (tails verified 2026-09-01; see
`docs/TRUNCATED-SOURCES.md`). Recovery is Recall or
`/Users/rig128gb/.rig/bin/riglake-mount-ensure` + search of `~/mnt/RIGLake`.

**Falsifier:** Recall or a file under `~/mnt/RIGLake` yields an exact-title copy whose
tail extends beyond the recorded anchor (content after `| QNA |`, after gap 3's `Z`, or
after Phase 11's objective line). Then re-hash, update `docs/TRUNCATED-SOURCES.md` and
the source manifest, and rescore. If no such copy exists: only directly evidenced
capabilities are scored, the Phase-11 offering row stays pinned at `maturity_M0_5: 0`,
Phases 1-10 run against their real gates, and no Phase 11 body, Phase 12, Gate 11, Gate
12, or the four-letter expansion of the `QNA` table fragment is ever authored — `GATES[11]`/`GATES[12]` stay `KeyError`s.

## A4 — Claude Code's own auth can reach `claude-fable-5-1`

The Fable strategy session runs headless (`-p`) without `RIG_TASK=orca-workspace-session`,
so the 8768 subscription-gateway env is not injected and the launch uses Claude Code's own
auth; installed Claude Code 2.1.257 ≥ the required 2.1.255.

**Falsifier:** the headless `claude --model claude-fable-5-1 -p …` invocation in the P8
terminal returns an auth or unknown-model rejection (`FABLE2031_EXIT` non-zero with such
a message in `/tmp/fable-2031-result.json`). Then keep the route installed and DORMANT,
record the rejection as evidence, leave Opus 5 default, and do not improvise a gateway
binding or substitute a model. Sub-contingency: if `--effort high` alone is rejected,
retry once at the model's accepted level and record the substitution.

## A5 — Gate-D approval is action-scoped and never reused

Each gated action class (`route-projection`, `cross-harness-install`, `grok-extraction`,
`fable-strategy-session`) needs its own `~/.rig/proof/gate-d-<run_id>.json` carrying
`{status:"APPROVED", action, max_budget_usd?, model_id?}` after Mike types `APPROVE <run_id>`.
The P0 intake envelope declares intent and authorizes nothing.

**Falsifier:** any action executes while consuming an approval file whose `action` field
names a different class, or a second action class succeeds reusing one `run_id`. That is
a bypass bug: the consumer must check `action` equality and refuse a consumed run_id; the
first such observation is a fabrication-grade incident, not a convenience.

## A6 — `git archive` can materialise the claimed commit

The verifier's clean tree comes from
`git -C /Users/rig128gb/Developer/rig-capabilities archive <commit_sha> | tar -x -C <tmpdir>` —
not blocked by the hook, creates no repo, needs no registry entry, and yields exactly the
claimed commit's tree.

**Falsifier:** the pipeline exits non-zero for a commit that `git cat-file -e` confirms
exists, or the extracted tree's contents differ from `git show <sha>:<path>` for a
sampled file. Then the verifier emits `BLOCKED`, never PASS. Never fall back to raw
`git clone` / `git worktree add`, never edit in an unregistered worktree.

## A7 — The 20-card corpus fixture's 0.05 unclassified rate exercises the 0.10 halt meaningfully

`tests/fixtures/fable2031/corpus/` holds exactly 20 synthetic cards with exactly 1
unclassifiable → `unclassified_rate = 0.05`, comfortably under `UNCLASSIFIED_HALT_RATE =
0.10`; the planted variant flips 2 more committed `{key, classified}` entries to false →
`3/20 = 0.15 > 0.10` → RED. The band between pass and halt is genuinely crossed by the
plant, so GREEN is not an artifact of a degenerate denominator.

**Falsifier:** the planted manifest yields `unclassified_rate` ≤ 0.10 (plant too weak), or
the unplanted fixture yields > 0.10 (baseline broken), or `unique == 0` makes the rate a
division the code papers over. Any of these means the gate is theater or the halt is
unreachable — repair the fixture before trusting any corpus verdict; no week is scored
while `score_week()` raises `CorpusRefusal`.

## A8 — Every new `certify` gate can be made hermetic (Law L1)

All seven new gates resolve inputs only from repo-rooted files (committed fixtures plus
`capability_register.csv`), because `self_test` runs live module code against a copied
tree and `WholeRepoCertifyTests` runs every non-suite gate against the live repo.

**Falsifier:** a gate's only honest input provably lives outside `repo.root`
(`~/.hermes/config.yaml`, live `litellm.yaml`, `~/.rig/leases`). Then it ships as a CLI
audit verb plus a unittest, **not** as a `certify` gate — a gate that reads live state
either flakes or lies.

## A9 — `normalize_stage()` will not move any compiled coordinate anchor

The compiler migration normalizes only the emitted `"steps"` list; the coordinate anchor
at `scripts/compile_harnesses.py:395` keeps using the raw `steps[0]` exactly as today.

**Falsifier:** snapshotting `out/harness-goalspecs/` (56 specs), recompiling from the 64
harness YAMLs, and diffing shows any coordinate anchor changed. Anchor drift is a
regression, not an upgrade: keep the raw anchor and normalize only `steps`.

## A10 — The three-decoy red team catches every fabrication

`tests/fixtures/fable2031/redteam/decoy-{1,2,3}.json` exist to prove the canary detector
fires; the `canary_detection` gate goes RED when a decoy is replaced with an all-green
packet.

**Falsifier:** a decoy escapes detection — the red-team packet is admitted `HONEST` or
the gate stays GREEN under the plant. Then halt dispatch and repair the detector before
any dispatcher work continues; an undetected canary is a fabricated green.

## A11 — A single registered lane is enough; no second worktree is needed

All implementation lands in the one registered writable root on branch `fable-2031`.

**Falsifier:** the work genuinely requires a second concurrent lane on the same repo.
Then register the Orca worktree in `workstation-repositories.json` as a temporary
`PRODUCT_WORKTREE` entry first — that registry edit is its own Gate-D action, never an
implementation detail, and until it lands the guard at `rig_repo_guard.py:124/:127` will
(deny and) rightly deny writes there.

## A12 — The live corpus roots are mounted and scannable when a week is scored

`corpus.CORPUS_ROOTS` points at mounted corpora, so an operator can score a real week with
`realign --root` / `capabilities_converge({"roots": …})` and the unbounded default stays
available to the CLI, where a minutes-long scan is acceptable.

**Falsifier:** a root that `is_dir()` reports true for then dies mid-walk. Observed on this
build: `~/mnt/RIGLake` passes `is_dir()` and its walk raises `TimeoutError` at ~130–160 s.
That is why no read-only MCP tool may default to those roots — `capabilities_converge({})`
scores the committed 20-card fixture and labels the answer `corpus_scope: "fixture_snapshot"`
with `live_corpus_scanned: false`. If a mount is repaired, the label changes; a tool that
quietly inherited the live default would report a snapshot as a corpus.

## A13 — A `done_when` check means what its file says

Frontmatter list items are stored as written, so a `cmd:` whose value ends in a closing
quote keeps that quote. `catalog._unquote()` strips only *paired* surrounding quotes; the
previous `.strip("\"'")` deleted the closing quote of any single-quoted `python3 -c '…'`.

**Falsifier:** an indexed `cmd:` item has an odd number of quote characters, or a check
passes as authored but fails under `run_asset`. That happened here — two realign checks died
with `unexpected EOF while looking for matching ''`, and a third pre-existing asset
(`skill-upgrades.md`) was already mangled. Assert: zero odd-quote `cmd:` items in
`.index.json` after `reindex`.

## A14 — `test_live_roundtrip` failing on this branch is contention, not regression

`sync()` is upsert-only (`rig_capabilities/sync.py:83-124`), so `capabilities.assets` in the
shared `rig-dev-db` is the union of every branch that ever synced; the assertion
`scan == count(*)` can only hold for whichever branch synced last.

**Falsifier:** the surplus rows turn out to belong to *this* branch — i.e. `git ls-files`
plus `.index.json` account for them, or `reindex` on a clean `fable-2031` worktree reproduces
the DB count. Then it is a real sync bug in this branch's lane and must be fixed here, not
documented. See conflict 8 for the receipts (4735 scanned here vs 4750 in the DB; 15 surplus).
