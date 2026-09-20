# SESSION STATE — UltraPlan V2 build (resume from compaction)

Updated: 2026-09-20 ~17:40 MT. Authoritative board: `BUILD-MANIFEST.yaml` (this dir). Todos mirror it.

## Repo HEADs
- ultraplan `386ad34` — + runtime/cell_runner.py (done_when executor, theater-refusal, ledger receipts), runtime/subs.py (16 W11 prims), runtime/w13/{migrate,rehearsal}.py (WAL-safe snapshot/rollback), features/, data/shape-map.json, data/ledger.db (mission 0601 with persona-panel receipt) — schemas/v1 (7), runtime/{ledger,commands,cli,console_server,effects,approvals}.py, features/ (80 BDD), data/shape-map.json (292/292), tests/ (61 green via discover)
- ultra-mcp `02a6338` — ultraplan_execute/query thin MCP tools over the shared handler; smoke asserts idempotency (plant-proven)
- rig-capabilities `cc44a21`+ (W04 forecast floors MIN_FAMILIES=3, asymmetric fixture) — W04 slices (polarity fix 886e8d4, executor 0b6cc1d, per-rule calibration 0665b93, JEX v7 111dd88), ultra_cell studio/cycle fixes, MIN_FAMILIES=3 cc44a21
- Manifest: 125/1207 past inventoried (88 built, 35 connected, 2 specified)
- Live: console `hub` process `ultraconsole` on :8902 (/api/{session,command,events,missions,health}); grill sessions 61398-61400 preserved (node pids 9871/67242/12766)

## Crew
- Jake (tmux firstmate:2, GPT-5.6-Sol): RATE-STARVED since ~13:00, W01 spec draft 0/4 — absorbed by Main
- Firstmate (firstmate:1): dispatch+lease authority, acknowledged
- Codex subagent pool: usage_limit_reached (all task/scout spawns fail) — builders run in Main

## Captain decisions OPEN (asked 3x)
1. OMP 18.1.17→18.2.6 repair `--apply` (TAC preflight blockers: omp_version, omp_local_route, meta_doctor, jake_l8)
2. rig-tac-system registry write (3rd Gate-D) to bootstrap TAC target repo
3. Jake pane model re-route (openrouter/kimi proven live)

## Gate machinery (working, use it)
- `jex.sh <item> <gate> <artifact> <atomic-claim> <cmd...>` — executes the assertion itself, median-of-3 JEV, certified thresholds (claim_atomic 0.49, evidence 0.4425), atomic.claim single-field pack 2-of-3. Exit 0 = built. Receipts in `evidence/jex/`.
- `gc.sh <repo> <test...> --staged <paths...> -- <git-args>` — test-first commit, EXPLICIT paths only (no -A; land-grab lesson)
- Calibration corpus: every live decision auto-logs to `~/.rig/s1gate/decisions.db`; label via seed scripts in this dir. done_test_is_vacuous REFUSES calibration (separation 0.19) — stays annotate-only.

## Next 5 runnable items (in order — updated 17:50)
1. W07 replication: cell runner + live model output for bank-harvest, tag-and-route, corpus-first, forecast-brief (pattern established: 386ad34, one JEX per op)
2. W12 Architecture/Cells readable panels; local frontend deps bundle (tldraw vendoring check)
3. W09: worker envelope = cell_runner + fence + verifier family separation (verifier via atomic.claim/proof gate, worker != verifier) — most exist (schema validator=schemas/v1, hasher=ledger._h, budget checker=_policy_check, approval validator=runtime/approvals, writer-fence=ledger.check_fence, SSE cursor=console sse(), route resolver=ultra_cell, plant runner=ultra_cell.plant_failure). Map + build the missing (lens instances, angle generation, scraper instances, liveness, model-family ladder, lens pack, JEV noul/choice/score subs, order-swap, memory append, variant proposal, envelope builder, Firstmate registration)
4. TAC P0 remaining (263-279): run the planning packet's own checkers (TRANSCRIPT-COVERAGE recompute, SECRET-SCAN rescan) — artifacts exist in 07-evidence
5. W13: migration rehearsal (legacy JSON → events import with provenance), then the soak harness (background, 24h)

## Hard-won lessons (do not relearn)
- NEVER `git add -A` in shared dirty repos; `| tail` masks exit codes — use `gc.sh`
- JEV blind-judge: claims scored inside multi-part blobs read compound — single-field pack exists
- pi needs `-ne -nc --no-skills` for headless smoke; team extension needs TUI (tmux)
- PAT from disler repos was scrubbed from all 4 remotes; repos are private, clones pinned in manifest `pi_agent_repos`
