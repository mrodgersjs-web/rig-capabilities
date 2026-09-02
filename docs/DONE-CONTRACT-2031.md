# DONE-CONTRACT-2031 — Fable 5.1 + IQRSQPI v10 (ultraplan v10, STAGE-1 fields)

Run `fable-2031` · owner repo `/Users/rig128gb/Developer/rig-capabilities` · branch `fable-2031`.
Derived from the approved plan; this file authorizes nothing by itself.

## Success statement
Build, install, test, and operate a governed executable IQRSQPI v10 system from the nine RIG source
cards. End state: a deterministic corpus scanner; a machine-readable M0–M5 capability register with
C_t/A_t/RobustMADZ scoring and a weekly Realign driver; an executable Known Expert OS phase harness
with a claim-typed Evidence Ledger; an anti-fabrication dispatcher layer (Orca-bound worktree leases,
rotating canary, typed handoff packet, cross-family re-execution verifier); a dormant-by-default
Claude Fable 5.1 route with an `E_stage` promotion gate; and a separate Orca terminal in which Fable
5.1 runs the 2031 strategy/planning session as generator-only. Every blocking gate is plant-failure
proven RED before it is trusted.

## Per-claim done test
One row per phase, each carrying that phase's literal `Verify:` command from the plan. A phase is
done only when its command's output matches the plan's stated expectation — not when the code
"looks finished".

**P0 — Intent**
```
python3 -m unittest tests.test_catalog.RoadmapTests -v
./bin/rig-capabilities proofchain
test -f docs/DONE-CONTRACT-2031.md
```

**P1 — Question**
```
for f in docs/ASSUMPTIONS.md docs/CONFLICT-RESOLUTIONS.md docs/TRUNCATED-SOURCES.md; do test -s "$f" || exit 1; done && echo QUESTION_ARTIFACTS_OK
```

**P2 — Research (corpus scan)**
```
python3 -m unittest tests.test_catalog.CorpusTests -v
./bin/rig-capabilities corpus --roots tests/fixtures/fable2031/corpus --json
python3 -c "from rig_capabilities.corpus import detect_truncation; from pathlib import Path; print(detect_truncation(Path('/Users/rig128gb/Downloads/PROMPT PACK — Full-Corpus Scrape → Grok Extraction → Fable 5.1 Capability Map (2031 Design Chain).md').read_text()))"
```
Expected: `ok: true` with `unclassified_rate ≤ 0.10` (planted 0.11 manifest → `ok: false`); truncation probe → `(True, '| QNA |')`.

**P3 — Solution A (register / convergence / realign)**
```
python3 -m unittest tests.test_catalog.RegisterTests tests.test_catalog.ConvergenceTests -v
./bin/rig-capabilities register --validate
./bin/rig-capabilities realign --dry
```

**P3b — Solution A₂ (Known Expert OS / Evidence Ledger)**
```
python3 -m unittest tests.test_catalog.ExpertOsTests tests.test_catalog.EvidenceLedgerTests -v
./bin/rig-capabilities expert-os phases --json
./bin/rig-capabilities evidence --validate
```
Expected: 11 phases with `11: objective_only_truncated` and `12: absent_at_source`; evidence validate on
`evidence-ledger-unverified-resume.csv` → non-zero exit naming `unverified_claim_on_resume`.

**P4 — Solution B (lease / canary / dispatcher)**
```
python3 -m unittest tests.test_catalog.LeaseTests tests.test_catalog.CanaryTests tests.test_catalog.DispatcherTests tests.test_catalog.GateDLibTests -v
python3 -c "from rig_capabilities.gate_d import evaluate; print(evaluate('Bash', {'command':'git worktree add /tmp/x -b feat'}))"
```
Expected: `('deny','unmanaged-worktree-add')`; plus the double-acquire check in plan Verification §4
(second `rig-lease acquire` on the same worktree → exit `2` with `lease_held_by`).

**P5 — Solution C (E_stage / dormant Fable route)**
```
python3 -m unittest tests.test_catalog.EStageTests tests.test_catalog.ModelRouteTests -v
./bin/rig-capabilities model-route plan --json
./bin/rig-capabilities model-route audit-fallbacks --json
./bin/rig-capabilities model-route audit-tool-choice --json
grep -n 'claude-fable-5-1\|rig-fable51' ~/.rig/agent-doctrine/registries/model_registry.yaml ~/.hermes/config.yaml ~/.rig/grokbot-router/litellm.yaml
```
The final `grep` runs only after a Gate-D-approved `apply`.

**P6 — Quality (IQRSQPI v10 + seven hermetic gates)**
```
python3 -c "from rig_capabilities.catalog import Repo; from rig_capabilities.certify import self_test; import json; r=self_test(Repo('.')); print(json.dumps({k:v['ok'] for k,v in r['gates'].items()}, indent=1)); print('verdict', r['verdict'])"
python3 -m unittest tests.test_catalog
./bin/rig-capabilities self-test --json
```

**P7 — Proof (sealing / fabrication ledger / Sentinel honesty)**
```
python3 -m unittest tests.test_catalog.AfProofTests -v
./bin/rig-capabilities proofchain
./bin/rig-capabilities fabrication --json
ls ~/.rig/convergence/sentinel-prime/proofpackets/
```

**P8 — Integrate (canonical assets + Fable strategy terminal)**
The plan carries no literal `Verify:` line for P8; its done test is plan Verification §5:
`/tmp/fable-2031-result.json` exists, `FABLE2031_EXIT=0`, `modelUsage` names `claude-fable-5-1`,
`total_cost_usd` ≤ approved cap, S7 citations re-verified by the cross-family verifier, sealed
packet's `verify_seal` returns `True`. Plan Verification §6 closes the run:
`$TAC close-gate seal --draft <draft>.json --out <claim>.json && $TAC close-gate check --claim <claim>.json`
over production command records only (canary excluded), exit 0. `TAC=/Users/rig128gb/.hermes/skills/tac-v2-doctrine/bin/tac`
(never bare `tac`).

## Proof path
- Roadmap ladder: `docs/ROADMAP.md` rows `| 41 |`…`| 49 |` (five-column shape); packet column `—`
  until P7 seals real hashes — `proofchain` skips `—` rows, so the increment is honest-but-unproven
  until a `sha256:`/8-hex prefix appears there.
- Sealed packets: `afproof.seal_packet` under `~/.rig/proof/fable2031/`, `previous_hash` chained
  per `task_id` (`"genesis"` for a task's first packet); discovered by `proofchain._hashes()` via
  `rglob("*.json")`. `verify_seal` mismatch → `(False,'seal_mismatch')` → no PASS may derive from it.
- Weekly evidence: `.context/realign/<week>/` (register diff, `convergence_report.md`,
  `proof/*.json`, `doctrine-update-phrase.md`, `operators-weekly.md`); until P7 `run_week` returns
  `sealed: false` rather than fabricating a hash.
- Fabrication record: `<LEASE_DIR>/fabrication-ledger.jsonl` (one `O_APPEND` line per verdict);
  a ledger append failure raises rather than dropping an event.
- Sentinel: `~/.rig/convergence/sentinel-prime/proofpackets/` packets stamped
  `sentinel_prime_status:"SPECIFICATION_ONLY"`, `termination_authority:"UNIMPLEMENTED"` — fleet
  status stays `BLOCKED_PENDING_SENTINEL` even when a task verdict is PASS.
- Fable session: `/tmp/fable-2031-result.json` is authoritative; sha256 the artifact, seal it,
  and a different-family verifier re-opens every S7 `path:line` citation.
- Verdict ladder: `tac close-gate check` is a deterministic prefilter (GREEN/RED only, never PASS);
  `dispatcher.admit()` run by a different family over a `git archive` tree at the exact claimed
  commit is the only emitter of PASS.

## Rollback path
- P0–P4, P6–P8 code/docs/fixtures are purely additive files in the registered repo on branch
  `fable-2031`: rollback = do not merge / revert the branch commits. No existing behavior is
  modified destructively; `out/harness-goalspecs/` anchors must stay byte-identical (anchor drift
  = revert the compiler change).
- P5 `model_route.apply()` is one transaction over three targets, each backed up as
  `<file>.bak-<UTC ts>` immediately before its atomic write; unwritable target or stale
  precondition hash → abort before the first write; mid-transaction failure restores every backup.
  Manual rollback = restore those `.bak-` files. Explicitly never touched:
  `~/.claude/settings.json`, `~/.rig/lobe-gateway/rig_lobe_gateway.py`,
  `~/.rig/config/omp-flash-default.yml`, `~/.rig/route-table.json`, `~/.omp/agent/config.yml`.
- Gate-D denial rolls back itself: dry-run artifacts remain, state reads
  `BLOCKED_PENDING_GATE_D`, nothing partial is applied.
- The weekly cron ships as dormant in-repo `.context/realign/cron-job.json`;
  `~/.hermes/cron/jobs.json` and `~/.hermes/scripts/rig-weekly-evolution.sh` are never modified,
  so there is no scheduler state to unwind.
- Verifier trees are throwaway `/tmp` dirs from `git archive <sha> | tar -x`; delete the dir.
  No clones, no worktrees, no registry entries exist to remove (L2).

## Gate-D boundary
- Gated action classes, each needing its own `~/.rig/proof/gate-d-<run_id>.json` carrying
  `{status:"APPROVED", action, max_budget_usd?, model_id?}` after Mike types `APPROVE <run_id>`:
  `route-projection`, `cross-harness-install`, `grok-extraction`, `fable-strategy-session`.
  Approval is action-scoped and never reused; this contract and `.context/iqrsqpi/fable-2031/00-intake.json`
  declare intent and authorize nothing.
- With `declared_budget_usd: 0` the paid branch (Grok extraction, Fable strategy session) is
  `BLOCKED_PENDING_GATE_D`; unpaid phases proceed regardless.
- `model_route.apply()` without a valid `route-projection` approval raises
  `RouteGateError('gate_d_required')` and writes nothing.
- No install, provider call, route projection, cron change, send, publish, or payment happens
  without its own typed approval; no `--yes`/env/non-interactive bypass is honored.
- Mechanical floor independent of Gate-D: `gate_d` denies `git worktree add`
  (`unmanaged-worktree-add`), `rig-build-gate.py` hard-blocks `git init|clone|worktree add`, and
  `rig_repo_guard.py` denies writes outside registered writable roots. Bringing the ungoverned
  `~/.omp/agent/config.yml` designer binding under the dormancy policy is a named Gate-D follow-up,
  not an implementation detail.
