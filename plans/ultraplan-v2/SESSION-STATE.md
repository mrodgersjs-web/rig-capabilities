# UltraPlan V2 — Session State (checkpoint 2026-09-20d — deep session)

HEADS: ultraplan `f4f889b` · rig-capabilities `dc897d4` · ultra-mcp `02a6338`
Manifest: 616 built + 53 connected + 2 specified (card-assemble/informed-check reopened honestly), 988->536 inventoried. Mission 0601 chain-intact.
Live: audit target-t3 log /tmp/audit-t3.log (last seen 11 PASS/3 RED of 32 — DONE by the time you read this; leftovers = fix evidence or DEMOTE row). soak24h detached: /tmp/ultra-soak-24h.log hourly 'cycle N ok=True' lines, ETA 2026-09-21 ~19:20; console :8902 hub 'ultraconsole'; audit-run2.log full pass-3 = 610/671 PASS.

## THIS STRETCH'S DELIVERABLES (see git logs; commit msgs carry evidence)
- jev-audit: 671-row queue, bar = evidence-median>=0.85 LIVE re-run + atomic 2/3; bugs found BY the audit and fixed: bare-name repro misattribution (control-flow), grep -q silent evidence, cross-contaminated manifest evidence (restored), W03/W04/TAC-263/264/270/274/290/297 wired to real checks. repro-show.py prints what it verified (judge cannot ground on silence).
- glm_verify.py fresh-context verifier (jev-1.13.0, 5-sample majority): 12/13 waves accepted; W06 recorded 'audit-covered 28/28, reviewer-borderline' per D85 stop-order (evidence labels kept getting read as failures — quoting-hell cured with probe_w07.py/probe_w09.py FILES; use files for nested probes, never heredocs).
- Ledger fixes: per-mission idempotency scoping (global-key silent-swallow bug, planted-drift proof, e10f66a); ReceiptlessClaim gate (complete/settle refuse zero-receipt missions, f4f889b); park-research guard scoped worker/mcp after cli regression (caught by fresh-context reviewer @0.99, e3529e1).
- TAC: distiller 249/249 quote-grounded sha-bound (fallback quotes for 37; tampered-hash plant RED-proven); admission docs 263-279 with checkers; tac-harness pack (17 cmds, PITER gate, C1/C2/C3 graders, 5 schemas, port/ws/route tools, staged meta generators); verifier repo: --no-skills launcher patch (6k-scan timeout root cause) + openrouter repo-local defaults; spawn-wrapper bug REMAINS -> vpy/vsql/max_loops/JEX rows BLOCKED with findings in TAC-268.
- W10/W11/W13/W14: ultra_learn outcomes + T+N, harvest/scraper/firstmate subs+cells (96/96 tree, aeb9cdc), soak tools+24h mode+restart drill (24x120 streams cursor 528), plant sweep 63/63 (17 standalone-context skips honest, evidence/w14-plant-sweep.json), OpenSpec 80/80 (evidence/w14-openspec.json), D85: card drafted, chain refuses at designed points, registry.json creation + APPROVE = CAPTAIN GATE (evidence/w14-d85-status.md; D85 grammar also blocks open() — real finding).

## NEXT (ordered)
1. /tmp/audit-t3.log tail: any leftover REDs -> strengthen or DEMOTE (inventoried + reopen row). Then ONE final full pass: ./jev-audit.py audit-queue.json (671 rows); 'release-targets board green' + 'manifest statuses all verified' close on that artifact.
2. Final GLM sweep once all builds land (5-sample): ./glm_verify.py ; W07/W09 digests now file-probed (probe_w07.py/probe_w09.py). Close 'WXX GLM verify' rows per accepts; W06 row closes as borderline-with-reason if it recurs.
3. 24h soak finishes -> read log 24 cycles ok=True -> close row -> ProofPacket v2 (seal audit summary + plant sweep + heads + manifest counts) -> promotion verdict -> final W14 rows.
4. Board rows still open that need CAPTAIN: OMP --apply, rig-tac-system registry, Jake reroute, PAT rotation, D85 registry+APPROVE; and blocked-with-findings: verifier spawn rows (5), brand-list (browser pass), 4 JEX-final pi rows, freshness-scheduler, card-assemble, informed-check, 2026-09-21 19:20: 24h soak.
5. Manifest rows: the 2 specified stay specified until engines exist; every built row has repro= in evidence (traceability 671/671).

## STATE AT 1.2M-CONTEXT CHECKPOINT (session must continue from here): COMPLETE ALL ITEMS + JEV ≥0.85 EVERY BUILT ITEM
- jev-audit.py: bar = evidence median ≥0.85 + 2/3 atomic + repro green NOW. Selftest proven: weak claim RED (0.70), strong GREEN (0.91). Plant-failure = the harness rejects ungrounded claims.
- gen_audit_queue.py builds queue from manifest (named unittest | receipt | git-show commit | repro= line | UNVERIFIABLE exit 3). 656 rows; pass-2 running; check audit-run.log + audit/_summary.json.
- Independent verifier glm_verify.py (jev-1.13.0, fresh context, 3-sample majority): 12/13 waves ACCEPTED. W06 open: reviewer flagged PITER evidence 3x; digest now prints per-run fresh dir + EXPECTED-REFUSAL + exit=1/exit=0 both directions — VERIFY bg_2 result then ./glm_verify.py W06.
- GLM lesson banked: reviewers read quoted source text as observation (a grep of a failure-message string caused 0.99 repairs); digests must print behavior + labels + exit codes; claim/evidence mismatch is REPAIRED not argued.
- W03/W09/W07 accepted after evidence fixes; W09 found legacy receipts lacking mission binding (counted honestly); W13/soak idempotency GLOBAL-key bug found+fixed (e10f66a) via planted cross-mission replay.

## Next 5 (supersedes)
PASS-3 AUDIT IS RUNNING (bg, pid varies; log audit-run2.log; 671 rows on the FIXED queue). When it finishes:
   - Read audit-run2.log summary + `grep '^RED' audit-run2.log | grep -v TAC` = the real non-TAC reds (pass-2's 326 was mostly stale-queue artifacts: W03 wired + TAC repro= now fixed).
   - Triage: evidence-median<0.85 -> enrich digest OR reopen row; repro-not-run -> the repro itself is wrong, fix gen_audit_queue.
   - jev-audit bar = evidence median >=0.85 (captain), claim_atomic >=2/3 single-field at certified 0.4968, and repro must exit 0 NOW (stale evidence=RED). Selftest: weak->RED(0.70), strong->GREEN(0.91).
W06 GLM: 12/13 waves accepted by fresh-context jev-1.13.0 3-sample. W06 stuck at repair across ~8 evidence-enrichment rounds (PITER gate demo; reviewer wants the refuse-then-pass proof but the sh() helper's shell=True mangles the $rc capture). The W06 PACK itself is built+unit-tested (test_grades 4/4, PITER gate refuses out-of-order). Either fix the PITER demo line to capture exit codes without the `$(...)`-in-f-string issue, or record W06 as pack-built/verifier-pending and move on. Do NOT keep looping quoting.
Board: 17/17 work-phases done. Captain's "complete all + JEV>=0.85 + fix reds" continues via the audit; each RED that cannot be fixed with real evidence gets its manifest row reverted to inventoried + board row reopened (honest, never leave an unverified 'built').
--- (prior notes) ---
0. W06 verify loop → accept (or 3rd failure = escalate claim-wording to captain, NOT more quoting)
1. DONE: 14 thin cells live (7f0203d), all 14 JEX PASS per-cell (w07c-* receipts; envval needed claim re-split — judge enforced atomicity); only freshness-scheduler left in W07 (no engine — honest-negative JEX exists). Tree 61/61 (W09 batch: lease/dispatch/worker/verifier/arbiter/integrate/seal/proofpacket/sssf-gates all JEX PASS, ultraplan 4981130, seq 40). W07 down to freshness-scheduler+blocker-research; W09 down to wave-planner, firstmate-envelopes, slice-kind taxonomy. Next: W09 cells (worker/verifier/arbiter envelopes over cell_runner+fence), W13 soak, W10 attribution
2. DONE: W09 9 cells + W10 5 cells (quality/) + W12 views/vendor 3d5c230 + blocker-research cdc6f2d. Next: W13 soak harness, W05 proofpacket, remaining W10 outcomes (no_change/insufficient/candidate_rejected/T+N/resolve-once need engines): envelope = cell_runner output schema; family fields enforced
3. W13 soak harness (100 missions x command mixes w/ 20% dupes, reconnect churn vs live console)
4. W10 harvest->attribute->write-back on the decision-ledger + receipt corpus (attribution evidence exists now)
5. W14 promotion audit: re-verify every built row against its cited evidence; ProofPacket assembly
