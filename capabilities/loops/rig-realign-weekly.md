---
outcome: "meta: the week ends with a signed delta on a weighted register or with a named FAIL — never with prose that could describe anything"
done_when:
  - file:capabilities/loops/rig-realign-weekly.md
  - grep:capabilities/loops/rig-realign-weekly.md:BASELINE_ONLY
  - grep:capabilities/loops/rig-realign-weekly.md:BLOCKED_PENDING_SENTINEL
  - cmd:test BASELINE_ONLY = $(python3 -c 'from rig_capabilities import convergence as C; print(C.weekly_gate(None, dict(c_t="0.5", a_t="0.5"), [], 0, unclassified_rate="0.05")["verdict"])')
  - cmd:test 0 -eq $(python3 -c 'from rig_capabilities.register import load_bookings as L; print(L("tests/fixtures/fable2031/bookings-zero.json")["count"])')
  - cmd:python3 -c 'from rig_capabilities import convergence as C; g = C.weekly_gate(None, dict(c_t="0.5", a_t="0.5"), [], 0, unclassified_rate="0.05"); assert "booked_qualified_conversations" in g["causes"] and g["verdict"] != "PASS"'
  - grep:capabilities/loops/rig-realign-weekly.md:enabled: false
state: DORMANT
gate_d_required: true
cadence: "0 17 * * 0"
great_example: capabilities/loops/rig-realign-weekly.md
quality_floor: 0.7
---

# RIG Realign Loop v1 — H_realign(week, register_delta, gate_verdict, doctrine_phrase)

**Cadence:** weekly, ISO week key `%G-W%V` from `rig_capabilities.realign.week_id()` — never typed by hand.
**Owner:** the register (data at repo root), scored by `rig_capabilities.convergence`, driven by `rig_capabilities.realign`.
**Harness:** `capabilities/harnesses/rig-realign-v1.yaml` — coordinate `L4-D1-A1-Intent`, IQRSQPI-10 vocabulary
(Intent, Question, Research, Solution, Quality, Proof, Integrate).
**Mode:** dry by default. `realign` without `--apply` writes nothing. Scheduling is staged dormant
(`state: DORMANT`, `gate_d_required: true`, `enabled: false` in this spec; the staging file
`.context/realign/cron-job.json` is a local pointer, not the contract); registering the
recurring job is a Gate-D action,
and `~/.hermes/cron/jobs.json` / `~/.hermes/scripts/rig-weekly-evolution.sh` are not modified by this loop.

> A weekly review that produces prose is a diary. A weekly review that produces a signed delta on a
> weighted capability register, gated by a node that can say FAIL, is an operating system.

## Inputs (everything the week reads; nothing else)

1. `capability_register.csv` at the repo root — M0–M5 rows in the criteria-card field order, including the
   mandatory `booked_qualified_conversations` row (weight 5, Studio GTM).
2. The prior sealed week's register state under `.context/realign/` — if none exists, there is no delta.
3. `data/fable2031/bookings-<YYYY-Www>.json` — `{week, records:[{id, date, account, source_record_id,
   qualification_evidence_path}]}`. **Bookings are ZERO by evidence today**: a record counts only when its
   `qualification_evidence_path` resolves to a file on disk, and a generic `booked_call` row without
   qualification evidence is zero.
4. The corpus scan — deterministic, manifest-first, no model in the classification path
   (`rig_capabilities.corpus.corpus_report`). Bound it with `--root` in interactive runs; the unbounded
   live roots scan takes minutes and an unreported rate makes the week FAIL, never PASS.

## The five weekly-gate conditions (all five, or it is not a PASS)

`convergence.weekly_gate` passes only when **all** of these hold:

1. **ΔC_t > 0** — convergence strictly improved: `C_t = 1 − E_cap/Σw`, `E_cap = Σ w_i·(1 − min(M_i,T_i)/T_i)`
   over active non-duplicate rows with `T_i = target_M_2031 > 0`, in exact Decimal arithmetic.
2. **ΔA_t ≥ 0** — the automation ratio `Σ w_i·1[band ∈ {A1,A2}]/Σw_i` did not regress.
3. **unclassified_rate ≤ 0.10** — the corpus halt. Past it, the week is `CORPUS_REFUSAL`: the classifier is
   rebuilt against the held-out set and no score is published; an unreported rate is not a zero rate.
4. **bookings > 0** — at least one qualified booked conversation with a resolvable qualification evidence
   path. A perfect infrastructure week with zero calls scores FAIL. That is the current honest state.
5. **no unresolved flag ≥ 5σ** — score movement passes `RobustMADZ = 0.6745·(score − median)/MAD` against the
   C_t series of prior sealed weeks; `MAD == 0` is reported `mad_zero`, never treated as a perfect score, and
   a ≥5σ flag goes to deep review and blocks PASS until resolved.

## BASELINE_ONLY semantics

With no prior sealed week (`previous_metrics` null), the verdict is **`BASELINE_ONLY`**: this week's C_t/A_t
are a baseline, never a delta, never an improvement. The first real week reported, honestly, on
2026-W36:

```
verdict: BASELINE_ONLY · causes: [unclassified_rate_unreported, booked_qualified_conversations] · bookings: 0
```

`causes` depends on which roots were scanned: bare roots cannot report an unclassified rate, and an
unreported rate is not a zero rate, so it appears as its own cause. W36 is now on disk under
`.context/realign/`, so a later week has a prior week and is no longer BASELINE_ONLY — scored against
the same unchanged register it is `FAIL` with `causes: [booked_qualified_conversations,
c_t_not_improving]` and `d_c_t: 0E-34`, which is the honest reading of a week that did not move.

A zero-booking week against a real baseline is **FAIL with its cause named** — complete, never retried, never
back-filled. Escalations fire on streaks, not mood: three consecutive FAIL weeks → `LOOP_REBUILD_REQUIRED`
(the loop itself is the worst-performing harness); three weeks of rising C_t with zero bookings →
`WEIGHTS_INVALID` (re-derive `w_i`).

## Per-week output (five artifacts under `.context/realign/<YYYY-Www>/`)

1. `register-diff.json` — this week's rows against the prior state;
2. `convergence_report.md` — C_t, A_t as Decimal strings, deltas or the absence of them, MADZ flags, causes;
3. `proof/*.json` — convergence, weekly-gate, bookings, register validation, register rows;
4. `doctrine-update-phrase.md` — Artifact 27, the phrase committed back to the system (on FAIL it names the cause);
5. `operators-weekly.md` — Operator's Weekly, quoting the proof JSON, not the conversation.

Sealing is explicit, not default: `realign --apply --seal` hashes the week's files, lands a real
`proof_hash` through `afproof`, and records it in `proof/sealing.json` — written **after** the hashing
and excluded from its own hash list, so the receipt can be recomputed by anyone. That receipt is the only
file in the week directory permitted to state `sealed: true`, and it states it only beside a hash
`afproof.verify_seal` recomputes. Without `--seal` every artifact says `sealed: false` and names the
missing step in `seal_reason`; a seal failure leaves the week unsealed and says so in words.
`./bin/rig-capabilities realign` is dry; `--apply` is the only mode that writes.

## What may never be claimed

- **No booking, meeting, account, revenue number, or conversion** may appear in any weekly artifact unless
  `register.load_bookings` reported it from a file whose qualification evidence resolves. Today that count is
  zero, so today the truthful report is zero.
- **No convergence improvement** may be claimed without a prior sealed week: `BASELINE_ONLY` is not a rise,
  and quoting C_t next to the word "improved" without a ΔC_t in the gate JSON is a fabrication.
- **No sealing** may be implied: a typed-in hash is forgery, and so is prose that claims a seal the
  receipt does not carry. The receipt decides — read `proof/sealing.json`, not the artifact text.
- **No fleet completion**: Sentinel Prime holds termination authority and is specification-only, so fleet
  status stays `BLOCKED_PENDING_SENTINEL` even when a task-level verdict is PASS.
- **No system-build bleed into business claims**: a green `certify` on this loop says nothing about bookings,
  revenue, or convergence. System-build PASS never implies business PASS.
- **No invented criteria for truncated sources**: where a source card ends mid-section, the honest entry is a
  status marker (`objective_only_truncated`, `absent_at_source`), not plausible gate text.

## Termination

The week terminates when the five artifacts exist and the gate has spoken — PASS, FAIL with named causes,
BASELINE_ONLY, CORPUS_REFUSAL, or a named escalation — and Operator's Weekly quotes exactly that. Silence is
not a verdict, and a verdict typed by hand is not a verdict at all: the node (`weekly_gate`) says it, or the
week has no verdict.
