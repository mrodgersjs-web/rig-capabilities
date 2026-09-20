# UltraPlan V2 — Session State (checkpoint 2026-09-20b)

HEADS: ultraplan `0c87a89` · rig-capabilities `fb7ce33` (branch ultraplan-v2) · ultra-mcp `02a6338`
Manifest: 1207 items — 164 built, 53 connected, 2 specified, 988 inventoried. Board ~444 open.
Live: console hub process `ultraconsole` :8902; ledger ultraplan/data/ledger.db mission 0f516f4a-…-0601 seq 17 chain-intact; JEV decision ledger ~/.rig/s1gate/decisions.db; tmux firstmate (pane 2 jake stale — codex pool limited).

## Committed this stretch (all gc.sh, gates green)
- W13: migration v1->v2 (M-1..M-8), backup/verify/rollback rehearsal incl. WAL-resurrection test (cd430dd); handle leak fix (ad46cd1)
- W07 cell runner (386ad34) + parse_done_when yaml-native + 5 new op cells (dfa7eb9): coverage-meter, aggregate, ledger-register, resolve-and-score wrap REAL engines (rig-ultra metrics coverage|information; rig-memory-forecast aggregate|ledger-register|settle --dry-run)
- Batch run 9 existing cells: 5 pass+receipt (corpus-waves, gap-mining, convergence, prompt-optimization + prior 4), 4 honest RED: altitude-walk (all-file done_when -> theater rule fired), slicing/done-contract/frontier-rounds/worker-dispatch (no workspace satisfies their greps)
- Receipts: mission_id+producer+workspace_sha256 provenance; ledger-refused receipt surfaces receipt_error, never vanishes (0c87a89, 8/8 tests)
- W09: writer==verifier family refusal test (c929db8) + distinct-families pass + missing-holder ESCALATES-not-passes (fb7ce33)
- rig-ultra metrics information refuses nested facts by name (was TypeError)
- W04 closure discipline: 36 W04 rows closed ONLY against test names/commits in test_ultra_gates.py; 3 rows stay open (escalation-during-claim, cross-run persistence, ledger-write-failure)

## THE PATTERN for remaining 14 W07 ops (D85: stay thin)
cell = tree-compliant dir (SKILL.md w/ done_when cmd: wrapping an existing engine; parent routes.yaml children += name else ORPHAN-red; validator requires agent.md frontmatter + 8-slot + harness/loop schema_version "1" + routes {phase, entry, children:[]}) → run_cell() executes own done_whens → receipt on 0601 → JEX single claim via plans/ultraplan-v2/jex.sh.
Engines to wrap: normalize_dedup (sub or ultra.questioning) for tag-and-route/value-rank/card-assemble; ultra_forecast.resolve_and_score for forecast-brief/dry-check; ultra.questioning classify for source-grade/informed-check; rig-capabilities bin/* only. NO model-dependent prompts in done_whens.
Fix the 4 RED cells: rewrite their done_whens to be red-capable (altitude-walk) or accept they need W08 workspaces (leave open, honest).

## Gates/rules that fired this session (keep enforcing)
- gc.sh refuses red commits (caught my wrong-premise test live); sole commit path.
- JEX: claim_atomic certified thr 0.490 (median-of-3 single-field packs); 5 JEX receipts in evidence/jex/ incl. 2 ESCALATE-then-clean re-runs.
- run_cell: all-file-existence done_whens self-refuse.
- pi -p openrouter/kimi-k3 ~5s; ULTRA_MODEL=kimi-k3 in bin/rig-ultra persona-panel; console :8902 hub-managed.

## Captain decisions pending (asked 5x)
1. OMP 18.1.17 -> 18.2.6 `--apply` repair  2. rig-tac-system registry write approval  3. Jake reroute
4. **ROTATE PAT github_pat_11ABZYK6Y0… NOW** (in transcript history; remotes scrubbed, token not).

## Next 5
1. Build 14 thin W07 cells per pattern above (2-3 batches), tree green before each commit
2. W09 worker/verifier/arbiter cells: envelope = cell_runner output schema; family fields enforced
3. W13 soak harness (100 missions x command mixes w/ 20% dupes, reconnect churn vs live console)
4. W10 harvest->attribute->write-back on the decision-ledger + receipt corpus (attribution evidence exists now)
5. W14 promotion audit: re-verify every built row against its cited evidence; ProofPacket assembly
