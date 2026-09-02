# CONFLICT-RESOLUTIONS — eight source-vs-reality conflicts, each with its receipt

Every receipt below was re-read from disk on 2026-09-01 on branch-checked working state.
Where the approved plan's cited line number has moved, this file records the **current**
number and marks the drift. Line numbers in live config drift mid-session (conflict 7),
so these receipts are snapshots, not guarantees — address live config by key path.

## 1. `claude-fable-5-1` is absent from the three governed registries but Fable is already bound, ungoverned, in OMP

**Receipt (governed registries, absence):**
- `~/.rig/agent-doctrine/registries/model_registry.yaml` — grep `fable` returns only the
  unrelated `blackwell-deepseek-v4-fable` entries (:436-456) and the `fable_training_candidates`
  dataset id `armand0e/claude-fable-5-claude-code` (:799). No `claude-fable-5-1` route entry.
- `~/.hermes/config.yaml` — `claude-fable-5` appears at :133 (OpenRouter model map), the
  `rig-fable5` provider block :338-350, `claude-lab` at :574-576, and an alias at :1119-1121;
  the exact id `claude-fable-5-1` appears nowhere.
- `~/.rig/grokbot-router/litellm.yaml` — zero matches for `fable` in any form.

**Receipt (ungoverned binding, present):** `~/.omp/agent/config.yml`
- :168 `designer: anthropic/claude-fable-5`
- :210 `name: claude-fable-5` (under the `designer:` agent-display block, :209)
- :342 `designer: anthropic/claude-fable-5:high` (in `task.agentModelOverrides`)
- :347 `- anthropic/claude-fable-5` (in `enabledModels`)

**Drift note:** the plan cited the designer binding at `:159` and the override at `:335`;
current positions are `:168` and `:342`. The plan's prose wrote the bound string as
`anthropic/claude-fable-5.1`; the literal value on disk is `anthropic/claude-fable-5`
(with `:high` on the override line). Either reading — the Fable family binding, or the
exact id `claude-fable-5-1` — matches none of the three governed registries.

**Resolution:** the plan's "dormant by default" claim is **scoped to the three governed
route registries only**. The OMP designer binding is disclosed via `model_route.plan()`'s
`ungoverned_route_detected` field and is **not edited** by this plan; bringing it under the
dormancy policy is a named Gate-D follow-up.

## 2. `rig-fable5` is output-starved: `max_tokens: 512` against an adapter advertising 128 000

**Receipt:** `~/.hermes/config.yaml:338-350` — provider `rig-fable5`
(`default_model: anthropic/claude-fable-5` at :344); its model-map entry
`anthropic/claude-fable-5:` (:347) carries `max_tokens: 512` at **:349**. The 128 000
output figure is the adapter's advertised capability for the `claude-fable` prefix per the
source card ("Claude Fable 5.1 — RIG Fleet Install, Routing Policy & Breaking-Change
Audit", card 2) as recorded in the approved plan. 512-token completions are a live
starvation bug, not a policy.

**Resolution:** `model_route.apply()` — one value everywhere — corrects `rig-fable5`'s
`max_tokens` from `512` to `128000` and gives the new `rig-fable51` provider `128000`,
each write preceded by a `<file>.bak-<UTC ts>` backup, all under a `route-projection`
Gate-D approval. Never applied by a test, gate, or dry-run.

## 3. LiteLLM fallback chains speak deployment aliases, not model ids

**Receipt:** `~/.rig/grokbot-router/litellm.yaml:80` `fallbacks:` and :91
`context_window_fallbacks:`; every entry in both chains is a `model_name:` deployment
alias — `- rig-local-first:` (:81, :92) whose children include `rig-blackwell-flash`,
`rig-blackwell-uncensored`, `rig-grok` (:82-90). Real model ids live only under
`litellm_params.model`; chains never reference raw ids.

**Resolution:** `model_route.audit_fallback_ladders()` fails when the deployment alias
`rig-fable51` (`FABLE_DEPLOYMENT`) appears in either chain, **and additionally** when any
alias referenced by the chains resolves through `model_list[].litellm_params.model` to a
string containing `claude-fable-5-1`. The audit matches the alias first; matching only the
raw model id would miss the actual wiring.

## 4. ROADMAP's `—` packet cell is skipped by `proofchain`, never reported missing

**Receipt:** `docs/ROADMAP.md:10` is the five-column header
`| V | commit | packet (sha256 prefix) | what shipped | proof |`; :4 documents
`—` as "no packet was sealed for that increment". `proofchain._packet_prefixes` reads
`cols[3]` and collects only `sha256:`/8-hex values, so an `—` cell is silently skipped.

**Resolution:** new rows `| 41 |`…`| 49 |` ship in the same five-column shape with packet
column `—` until P7 seals real hashes. Until then the increment is honest-but-unproven —
`proofchain` will not flag it, and this file is the place that says so out loud.

## 5. `tac` on PATH is coreutils, not the TAC CLI

**Receipt:** observed 2026-09-01: `command -v tac` → `tac`; `type -a tac` → shell builtin,
then `/Users/rig128gb/.rig/bin/tac`, then `/Users/rig128gb/.homebrew/bin/tac` — all
tail-inversion utilities. The TAC CLI exists, executable, at
`/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac`.

**Resolution:** every reference in docs, tests, and scripts uses the absolute path
`/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac` (conventionally `TAC=…`). Bare
`tac` is never invoked for `close-gate` or `route` commands.

## 6. The hook blocks worktree creation while the guard denies writes in unregistered worktrees

**Receipt:** `/Users/rig128gb/.rig/bin/rig-build-gate.py:74-77` —
`REPOSITORY_CREATION_PATTERN` hard-blocks `git init`, `git clone`, `git worktree add`
(and `gh repo create`). `/Users/rig128gb/.rig/bin/rig-repo-guard` execs
`/Users/rig128gb/Developer/rig-intelligence/scripts/rig_repo_guard.py`, whose `decision()`
denies an "unregistered Git worktree inside control plane" at **:124** and "path is
outside every registered writable root" at **:127** (plan cited `:118-127`; current lines
confirmed inside that range, no drift).

**Resolution:** Law L2. Implementation edits happen **directly in the registered canonical
repo** `/Users/rig128gb/Developer/rig-capabilities` (registry
`registry/workstation-repositories.json:832-839`: `write_enabled: true`,
`disposition: CANONICAL`) — no agent-created checkout, ever, for editing. Verifier trees
at a claimed commit are materialised with
`git -C <repo_root> archive <commit_sha> | tar -x -C <tmpdir>`: not blocked, creates no
repo, needs no registry entry. `gate_d` gains only the **deny** rule
`unmanaged-worktree-add`; no `git clone → allow` case is added.

## 7. Live-config line numbers drift mid-session

**Receipt:** the plan itself recorded `rig-fable5` moving from `~/.hermes/config.yaml:321`
to `:338` while the plan was being written; this session re-located it at `:338-350`.
This session additionally observed `~/.omp/agent/config.yml` designer bindings at `:168`
and `:342` where the plan had cited `:159` and `:335` — drift found and recorded in
conflict 1.

**Resolution:** never edit live config by remembered line number. Address by key path
(`providers.rig-fable5.models["anthropic/claude-fable-5"].max_tokens`) and re-locate with
a fresh `grep -n` immediately before any edit; `model_route.apply()` re-verifies each
target's precondition hash and aborts before the first write if it is stale.

## 8. Two sessions share one working tree, one `.index.json`, and one Postgres mirror

**Receipt:** on 2026-09-01 this session found `HEAD` on `loop-skills-v11` (`c3c2032`,
pushed, tree clean except an uncommitted edit to
`docs/HANDOFF-2026-09-01-loop-skills-v11.md`), nine commits ahead of `main`, while every
fable-2031 file sat untracked. `.index.json` is gitignored (`.gitignore:1`), so it is one
file shared by every branch: the sibling's reindex left `stale=3` here —
`iqrsqpi-v11.md` (skill), `rig-loop-gate` (hook), `rig-loop-hooks.ts` (hook) — three assets
that exist on its branch and not on this one, which reddened `certify`'s `index_fresh` gate
and `WholeRepoCertifyTests.test_non_suite_gates_green` on a tree this session never broke.
Deeper: `sync()` upserts and never deletes (`rig_capabilities/sync.py:83-124`), so
`capabilities.assets` in `rig-dev-db` is the *union* of every branch that ever synced. It
holds 4737 rows; a clean worktree of `loop-skills-v11` scans 4725 and this branch scans
4723. `SyncTests.test_live_roundtrip` asserts `scan == count(*)`, so that assertion can only
ever be true for the one branch whose index the shared DB last happened to mirror.

**Resolution:** never mutate shared state to make a local branch look green. The sibling's
WIP edit was preserved twice (`stash@{0}` and `/tmp/fable2031-backup/loops-handoff-wip.patch`)
rather than discarded; this branch's 89 uncommitted files were tarred to
`/tmp/fable2031-backup/pre-commit.tar` before the branch switch and restored after. The
index was rebuilt for this tree (`bin/rig-capabilities reindex` → `missing=0 stale=0`) and
the shared DB was left alone: the 14 surplus rows belong to a sibling branch's work, and
deleting them to satisfy an assertion is data loss dressed as a green check. `docs/proof/`
is gitignored so that branch's Gate-D packets cannot be committed as this branch's evidence.
`test_live_roundtrip` is left RED here, with this receipt as its explanation. The durable
fix belongs to whichever branch merges last and is one of: (a) have `sync()` delete rows
absent from the scanned index, which makes the mirror a mirror and the assertion true by
construction; or (b) add a `branch` column, key the upsert on it, and assert equality
per-branch, which lets both branches coexist in one database.

**Follow-up (2026-09-02, after Wave-3 registration):** the contention is unchanged and now
larger. Registering this branch's eight canonical assets moved the local scan 4723 → 4735,
and `sync()` pushed the shared DB 4737 → 4750. The surplus is 15 rows — the sibling branch's
`rig-loop` assets plus earlier branch unions — none of them `fable-2031`'s, so
`test_live_roundtrip` (4735 != 4750) stays RED here on the same argument, with A14 in
`docs/ASSUMPTIONS.md` carrying the observation that would prove it a real bug instead. No
shared row was deleted to buy a green.

