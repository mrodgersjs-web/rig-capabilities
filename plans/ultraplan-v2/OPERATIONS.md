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
