# UltraPlan V2 — wave operations state (Main = manifest authority)

## Writable-root gate (contract rule 1)

- ultraplan + ultra-mcp NOT yet registered → **no source writes** into either repo until Gate-D clears.
- Pending Gate-D: `gd_1789930021263` (ultraplan local-only root), `gd_1789930021306` (ultra-mcp local-only root). Ledger: ~/.rig/gate-d/requests.jsonl. Approval form used by precedent: typed `APPROVE <request_id>` by Mike.
- rig-capabilities IS registered (write_enabled, local commits allowed via steward). All spec/plan work proceeds there: `plans/ultraplan-v2/`.

## Status updates

Builders update their own item rows IN PLACE in BUILD-MANIFEST.yaml (status + evidence fields) at wave close; `gen_manifest.py` regenerates from scratch only for schema changes (regeneration resets statuses — do not re-run it after work starts; it is the genesis tool).

## Crew (2026-09-20)

- Jake (tmux firstmate:2) — conductor, W01 acceptance specs → plans/ultraplan-v2/w01/
- Firstmate (tmux firstmate:1) — dispatch + lease authority (fm-lease.sh), spawn via fm-spawn.sh
- Main (OMP) — manifest authority, wave dispatch, verification
- GLM 5.3 — fresh-context verification per wave (not yet dispatched)

## Wave board

- W00: DONE (evidence in w00/, hashes verified; 292 shapes; contract falsifications: 864→904, "4 missing repos" false, no Earendil surface found)
- Manifest: DONE 904 items, sha256 30043e06e689689827b970196228ba8ed558c11c75d1fd3c66037c0fbeab9c3b (pre-status-update genesis hash)
- W01: specs in flight (Jake); Gate-D CLEARED (APPROVE both, 2026-09-20) → ultraplan + ultra-mcp registered local-only; baselines committed ultraplan 1a43ed8 (219 paths preserved), ultra-mcp 00052be
- W04: codex-routed scouts hit usage limit; JEV surface mapped inline by Main (tools/{gen_cells,canvas_cells,build_status,canvas_gates}.py are the JEV call sites; ui/server.mjs + tools/build_status.py are the state writers)
- TAC fold-in (captain directive 2026-09-20 #2): /Users/rig128gb/Desktop/TAC-Technology-Operating-System is a complete execution plan — 303 atomic tasks, P0-P7 packets, target ~/Developer/rig-tac-system NOT bootstrapped (preflight expected BLOCKED). All 303 folded into BUILD-MANIFEST.yaml as UP.W06.TAC.TAC-001..303 → 1207 total. TAC packet: first_mate_dispatch_allowed=false, OMP-supervised, needs a third Gate-D registry write before P0. Port 8918 = static dashboard over the planning folder; checkbox state browser-local, manifest remains truth.

## JEX live-gate status (2026-09-20, captain rule: <0.85 = not built)
- `jex.sh` = per-item live gate: rig-ultra route --live; PASS = code checks cleared AND rule-polarity-corrected goodness >= 0.85 on every JEV question. Polarity derived from the pack's own rules, not names.
- Two real defects found BY the gate in its first hour: (1) `check_done_test_executable` matched command NAMES, never executed — now executes all assertions, exit!=0 routes REWORK (commit 0b6cc1d, 3 regression tests, RED shown live via cmd:exit-3 route). (2) blind-judge: route() showed JEV only artifact bytes, never the claim — identical scores for different claims; fixed in 0b6cc1d, judged state now includes declared text facts.
- CALIBRATION BLOCKER (evidence in evidence/jex/w04-executor-v{3..6}.json): semantically equivalent claims score noul 0.31-0.75 across runs — ultra.* packs are uncalibrated (zero labelled decisions) and every item ESCALATES below 0.85. The captain's rule stands; the consequence is W04 (calibration fixtures + labelled seeds + per-rule calibration + held-out eval) is the critical path before mass item-closing. Gate stays strict meanwhile; nothing closes on JEV-advisory alone.
- PiAgents: lead-agents E2E SMOKE-OK (openrouter team, orchestrator answered), ceo-agents booted (kimi-k2.5 model switch verified 262k footer), ui-agents vite :5299 http=200, verifier booted with glm-5.2 route error (model-fix item). All JEX-scored attempts recorded; none ≥0.85 yet (same calibration blocker).


## Wave state 2026-09-20 ~15:10 (Main)
- GATE MACHINERY LIVE: jex.sh v7 (executed assertions + receipts + certified thresholds + single-field atomic.claim 3/3 median) — PASSed & closed: schemas, studio-resolution, executor, polarity, calibration, crash-atomicity, CLI authority, MCP adapter, console origin.
- JEV: ultra.proof {claim_atomic 0.490, evidence 0.4425} certified; atomic.claim pack certified 0.4968 (68 labels); done_test_is_vacuous REFUSED calibration (separation 0.19) -> annotate-only; corpus keeps growing with every live decision (rig-ultra now logs by default).
- BUILD STATE: ultraplan @ 1e800a5+ (policy layer pending bg commit): schemas/v1 (7), runtime/{ledger,commands,cli,console_server}.py; :8902 = durable console (hub-managed 'ultraconsole', static file behavior preserved, /api/{session,command,events,health}). ultra-mcp @ 02a6338: ultraplan_execute/query thin tools, smoke asserts idempotency (plant-proven). rig-capabilities @ 355085f: W04 slices, calibration machinery, JEX.
- Console authz: ui sessions cannot create; human elevation = possession of data/console.secret (local operator). 8/8 console e2e incl. Last-Event-ID resume + gap path + foreign-origin + traversal refusals.
- NEXT: W02 effects-dispatch to rig-loop (claim/execute/complete), budgets JEX-close, W05 vertical slice through :8902 (W01 remaining slots after Jake/GPT lane frees or Main continues), W12 CONSOLE.html data-binding to /api/events.
