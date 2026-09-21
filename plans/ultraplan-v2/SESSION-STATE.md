# UltraPlan V2 — Session State (checkpoint 2026-09-20b)

HEADS: ultraplan `8ac6deb` · rig-capabilities (latest: W06 pack + verifier hardening) · ultra-mcp `02a6338`

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

## Captain order (2026-09-20T19:00): COMPLETE ALL ITEMS + JEV ≥0.85 EVERY BUILT ITEM
- jev-audit.py: bar = evidence median ≥0.85 + 2/3 atomic + repro green NOW. Selftest proven: weak claim RED (0.70), strong GREEN (0.91). Plant-failure = the harness rejects ungrounded claims.
- gen_audit_queue.py builds queue from manifest (named unittest | receipt | git-show commit | repro= line | UNVERIFIABLE exit 3). 656 rows; pass-2 running; check audit-run.log + audit/_summary.json.
- Independent verifier glm_verify.py (jev-1.13.0, fresh context, 3-sample majority): 12/13 waves ACCEPTED. W06 open: reviewer flagged PITER evidence 3x; digest now prints per-run fresh dir + EXPECTED-REFUSAL + exit=1/exit=0 both directions — VERIFY bg_2 result then ./glm_verify.py W06.
- GLM lesson banked: reviewers read quoted source text as observation (a grep of a failure-message string caused 0.99 repairs); digests must print behavior + labels + exit codes; claim/evidence mismatch is REPAIRED not argued.
- W03/W09/W07 accepted after evidence fixes; W09 found legacy receipts lacking mission binding (counted honestly); W13/soak idempotency GLOBAL-key bug found+fixed (e10f66a) via planted cross-mission replay.

## Next 5 (supersedes)
0. W06 verify loop → accept (or 3rd failure = escalate claim-wording to captain, NOT more quoting)
1. DONE: 14 thin cells live (7f0203d), all 14 JEX PASS per-cell (w07c-* receipts; envval needed claim re-split — judge enforced atomicity); only freshness-scheduler left in W07 (no engine — honest-negative JEX exists). Tree 61/61 (W09 batch: lease/dispatch/worker/verifier/arbiter/integrate/seal/proofpacket/sssf-gates all JEX PASS, ultraplan 4981130, seq 40). W07 down to freshness-scheduler+blocker-research; W09 down to wave-planner, firstmate-envelopes, slice-kind taxonomy. Next: W09 cells (worker/verifier/arbiter envelopes over cell_runner+fence), W13 soak, W10 attribution
2. DONE: W09 9 cells + W10 5 cells (quality/) + W12 views/vendor 3d5c230 + blocker-research cdc6f2d. Next: W13 soak harness, W05 proofpacket, remaining W10 outcomes (no_change/insufficient/candidate_rejected/T+N/resolve-once need engines): envelope = cell_runner output schema; family fields enforced
3. W13 soak harness (100 missions x command mixes w/ 20% dupes, reconnect churn vs live console)
4. W10 harvest->attribute->write-back on the decision-ledger + receipt corpus (attribution evidence exists now)
5. W14 promotion audit: re-verify every built row against its cited evidence; ProofPacket assembly
