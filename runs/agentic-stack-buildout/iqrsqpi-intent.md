# Intent — durable-repeatable RIG coding standard buildout

Run: iqrsqpi-v20-20260912T091037Z-e5142d
Source plan: /Users/rig128gb/.omp/agent/sessions/-Desktop-Projects/2026-09-12T07-09-29-711Z_01a09473-26ef-7102-81f2-1b96e46f37c1/local/agentic-stack-buildout-plan.md (sha256 a3bda1240125525389ebbbebf707841b49fc89a4fe79de3c162c148b4d078d58)

## GOAL

Every one of the 588 Lattice cells has expanded, profession-usable criteria that are either qualified by evidence (verifiable by the next agent) or carry an explicit owner-approved non-build decision; and the estate runs a repeatable commit-gate flow admitting only D85-eligible builds (4 ratios >= 0.85) with joint durable+repeatable claims (combined Wilson lower bound >= 0.95).

## METRIC

Primary metric: fraction of the 588-cell claim set that is evidence-qualified or owner-approved non-build, with the estate commit-gate jointly (durable+repeatable Wilson LB) >= 0.95. Current honest value: 0/588 qualified; gate not yet built.

## DONE-TEST

- cmd:cd /Users/rig128gb/Developer/rig-capabilities && python3 runs/agentic-stack-buildout/scripts_wave_check.py
- file:runs/agentic-stack-buildout/inventory/C18-runtime-inventory.md
- file:runs/agentic-stack-buildout/inventory/C17-C19-estate-schedulers.md
- file:runs/agentic-stack-buildout/inventory/C20-process-surfaces.md
- grep:runs/agentic-stack-buildout/scoring/scoring-contract-v0.md:DRAFT
- cmd:cd /Users/rig128gb/Developer/rig-capabilities && /Users/rig128gb/.local/bin/graft check

Per-section acceptance (phase gates):

- Section I: three estate inventories exist with Claims+Gaps (runs checker exits 0); C20-C23 qualitative diagnosis cites receipts; graft FRESH.
- Section II (S08): bms.py raw formula computes 0.4*(1-failure_cost)+0.3*recovery_value+0.3*mvp_compression; planted-failure tests prove sign repair and band mapping; measurement rules (scoring-contract-v0.md) verifier-frozen.
- Section III: criteria pack exists only when inputs resolve; 588-row expansion regenerable from frozen pack via named command.
- Section IV: bin/rig-build-standard verbs diagnose/index/check/commit-gate run with --help; rig-loop verify --family claude returns cross-family verdict; omp -p --no-session probe documented.
- Section V: rig-determinism-85 score reports all four ratios; per-build verify-cert passes; commit-gate admits only 4-ratio >= 0.85; L7-A1 rejected as unreachable (max 0.70).
- Section VI: every done/commit carries 4 receipts (fresh 4-ratio D85, joint durable+repeatable lower bound, cross-family verdict, Gate-D SHA approval + git ls-remote proof); sealed ProofPacket per build.

## COORDINATE

Process coordinate (qualitative; numeric BMS UNKNOWN pending S08 — see runs/agentic-stack-buildout/diagnosis/C24-blocked-diagnosis.json): read-only diagnosis unit; altitude candidate L3 (multi-source evidence gathering with handoff artifacts); mode NOT CLAIMED (A1 unclaimed; no build in this stage).

## CONFIDENCE
0.8

The 0.8 is the probability the stage DONE-TEST passes first time (mechanical checkers exist; scouts dispatched with self-verification instructions). Confidence for the full 6-section buildout inside tool budget: 0.5, blocked externally on S08 scalar measurement, criteria-owner approvals, and per-build Gate-D. No 0.95 claim is made anywhere in this run.
## UNCERTAINTY-LEVEL
3

Rationale: estate surfaces are documented and local (familiar), but OMP skill-source resolution, live scheduler ownership, and pre-built criteria pack status are genuinely unresolved.

## OUT-OF-SCOPE (declared)

Supabase schema/workers, scheduler enablement or restarts, live-provider sends, Hermes profile changes, credential rotation, public exposure — each requires its own scoped Gate-D approval. No canonical capability installation before its 4 receipts exist.

## Known UNKNOWNs (declared, not substituted)

failure_cost, recovery_value, mvp_compression, prediction_failure_rate, deviation_quality = UNKNOWN until measurement rules produce trial rows (scoring/scoring-contract-v0.md; diagnosis/C24-blocked-diagnosis.json). OMP skill-source resolution UNRESOLVED pending runtime receipt.
