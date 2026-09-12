# Scoring Contract v0.1 (DRAFT — Section II freeze candidate; NOT frozen)

Run: iqrsqpi-v20-20260912T091037Z-e5142d · Author: OMP (Builder) · Date 2026-09-12
Status: DRAFT. S01-S07 freeze happens only after verifier sign-off. Every rule below is **PROPOSED** until then. Cite-ready facts are separated from proposals. v0.1 corrects v0's field-name error (v0 used recovery_value/mvp_compression/prediction_failure_rate/deviation_quality — those names do not exist in source; source names are below).

## A. Canonical-current (verifiable in source TODAY; safe for BLOCKING answers)

File `capabilities/skills/rig-lattice-system/rig_lattice/lattice/bms.py`, sha256 ba5749f87cda731adbf18acacf7751f98b641fcce6f70d8761749c14158ecf47:
- `raw_score` (L133-142): `raw = failure_cost*0.4 + reversibility*0.3 + mechanism_clarity*0.3`, all three inputs defaulted 0.5, each validated to [0,1].
- `compute_bms` (L145-167): `final = clamp01(raw + adj_failure + adj_volume + adj_altitude)` where `adj_failure = -past_failure_rate*0.2`, `adj_volume = (data_volume-0.5)*0.1`, `adj_altitude = ALTITUDE_BONUS[level]`; defaults past_failure_rate=0.0, data_volume=0.5, level=L2.
- Thresholds (module docstring L6-14): A1 >=0.75, A2 0.45-0.74, A3 0.25-0.44, A4 <0.25; sharp boundaries (0.75 is A1).
- BMS_BUDGET_USD (L48-53): A1 0.00, A2 0.10, A3 0.50, A4 0.00.
- Defaults are 0.5 — **the scorer silently answers when inputs are unknown** (defaults masquerade as knowledge). S08 must add an explicit missing-input error or a provenance-checked input object.
- Documented **semantic defect**: raw increases when failure_cost increases — for an irreversible unit (failure_cost=0.95, reversibility=0.0, mechanism_clarity=1.0, level=L1) raw = 0.38+0.0+0.30 = 0.68, plus L1 bonus 0.35 clamps to 1.0 -> A1: maximum predicted-failure risk raises confidence toward the deterministic mode. Frozen intent (plan): `raw = (1-failure_cost)*0.4 + reversibility*0.3 + mechanism_clarity*0.3`. S08 flips the fc term only; adjustments/thresholds/band table stay.

## B. PROPOSED measurement rules (NOT evidence; each needs S01-S07 freeze + receipts)

Inputs needing measurement remain UNKNOWN until rows exist — never substituted (no 0.5 default acceptance, no hand-entered values):

- failure_cost ∈[0,1]: severity-weighted failure rate over >=72 recorded attempts; PROPOSED severity map crash/data-loss=1.0, wrong-output=0.7, timeout=0.5, degraded-but-correct=0.2; estimator = mean severity with Wilson-style upper bound.
- reversibility ∈[0,1]: PROPOSED measured as fraction of committed state changes revertible by scripted undo to a sealed prior hash without human edit, over >=20 replantings; 1.0 = pure function/dry-run-only.
- mechanism_clarity ∈[0,1]: PROPOSED = fraction of the unit's done-tests whose pass/fail is decided by a deterministic check (no LLM judge), computed from the unit's declared gate list; 1.0 = fully deterministic causal account.
- past_failure_rate: existing unit history from trials.jsonl (same attempt grammar below); no history -> UNKNOWN, and the S08 scorer must refuse the 0.0 default.
- data_volume: PROPOSED log-scaled measured corpus/rows size mapped to [0,1] with the mapping formula declared per unit before trial 1.

Sampling frame (PROPOSED): one trial = one recorded attempt appended to runs/agentic-stack-buildout/scoring/trials.jsonl `{ts, scalar, unit_id, attempt_seq, outcome, evidence_ref}`; retries are distinct attempts and count against. Sequential test alpha_j = 0.05/(m*2^j); zero-failure claim needs >=72 first-attempt successes at m=1, >=197 at m=588. Wilson 95% lower bound for favorable rates, upper bound for costs; verbatim command output + sha256 saved as receipt.

Joint durable+repeatable commit gate (PROPOSED): repeatable LB over >=72 real-path done-test runs; durable = fraction re-passing in fresh runtime >=24h apart (>=10 such re-runs), Wilson LB; joint = min(LB-durable, LB-repeatable) >= 0.95; commit additionally requires all four D85 ratios >=0.85 recomputed fresh, cross-family verdict, Gate-D SHA approval + `git ls-remote` proof.

Mode-claim rule: A1 = deterministic path passed. A2-A4 claims additionally require a runner-produced execution receipt that the deterministic path failed; self-authored failure JSON is not proof. No such receipt -> claims cap at A1 regardless of band.

## C. Registration path (S08+)
1. S08 flips the fc sign term with planted-failure tests: irreversibility->A1 must go RED; restored goes GREEN; test retained as regression.
2. Verifier revises this file -> scoring-contract-v1 freeze -> capability_add registration.
3. Criteria-pack build (C01-C16) re-attempted only after freeze; per-cell numbers come from trials.jsonl rows only.

## D. Measured today (2026-09-12)
- Source facts in section A read directly from bms.py L133-167 + docstring; defect demonstrated by the worked example above (arithmetic from constants in the same file).
- trials.jsonl: ABSENT -> every measured scalar is UNKNOWN today. Honest baseline, not a blocker for S08.
