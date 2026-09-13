# Durable Setup & Repeatable Results Index — schema (v1, canonical location)

Canonical asset: this directory. Execution snapshots go to
`runs/agentic-stack-buildout/` and never overwrite prior evidence. The index is a
**reproducible projection** of versioned criteria plus operational receipts: Git
(`rig-capabilities`) is authority for criteria, code, skills and tool definitions;
the `rig_build` Postgres schema (see `scripts/ddl_rig_build.sql`) is authority for
runs, events, artifacts and approvals references. A mutable JSON mirror must never
become a competing authority — `rig_capabilities/build_index.py` therefore stores
records bound to the current criteria-pack sha and rejects stale-hash writes.

## Row identity

One row per cell, `cell_id` from the frozen pack
`runs/agentic-stack-buildout/packs/criteria-v1.jsonl` (588 rows, sha
`f463e960137723d13021fd169b00167d781dcfaee4a5fd7b15de4380c9bbc7c5`).
Process-specific child records hang off a row when several processes use the cell;
a grouped display is never a grouped waiver.

## Required field groups (per row)

| Group | Contents | Produced by |
|---|---|---|
| identity | cell id; derived L/D/A/step; `criteria_version` + criteria hash; process id/version; source + environment hashes | `criteria_pack.py`, `build_standard` index build |
| criteria | fully expanded durable-setup, repeatable-result, level, diamond, mode and step criteria as observable pass/fail assertions — not a pointer to a generic checklist | frozen pack rows |
| diagnosis | all seven level fits, four mode-necessity assessments, BMS inputs + provenance + `BMSResult`, unresolved contradictions | `build_diagnose.py` + D85 `score` |
| tools | T-rule decisions, carrier + supporting libraries, canonical skill/agent ids, dependency readiness, installed versions | `tool_selection.select_framework` |
| durability | state schema/store, checkpoints, retention/backup/restore, deadline + overlap policy, idempotency, cancellation, compensation evidence | run/event records |
| repeatability | workload/profile/version, trial records, expected invariants, output/effect comparison, fault matrix, time bounds | `measure.Recorder` ledgers |
| d85 | inventory/classification bindings, the four ratios, certificate + fresh consumer verification; unsupported scope stated explicitly | `rig-determinism-85` |
| assurance | joint successes/trials, predeclared sampling assumptions, one-sided bound, α allocation, fault-coverage verdict, freshness | `commit_gate.py` joint arm |
| gaps | missing work, consequence, dependency impact, why not build, alternative, reconsideration trigger, exact cell ids, human approval id/scope | omission records (reference only) |
| runtime_use | OMP / Claude / Hermes / Prime: `installed`, `configured`, `loaded`, `exercised`, `enforced` as five separate states with receipts | `surfaces_render.py` + install ledger |
| learning_proof | RLM run/step ids, frozen baseline/candidate links, reviewer verdict, proof hash, promotion/rollback receipts | RLM tools + ProofPacket |

## Statuses

`PLANNED`, `BUILDING`, `BUILT_UNVERIFIED`, `QUALIFIED`, `BLOCKED`,
`NOT_BUILD_PROPOSED`, `NOT_BUILD_APPROVED`, `STALE`.

- Missing criteria or unknown dependencies never imply non-applicability.
- `NOT_BUILD_APPROVED` requires Mike's approval of the **exact** cell list,
  reasons and consequences. Approved omissions stay in the 588 denominator and can
  never satisfy another cell's dependency.
- `QUALIFIED` requires all four D85 ratios ≥ 0.85 on a fresh verification **and**
  the joint one-sided lower bound ≥ .95 at the allocated α with mandatory
  fault/recovery coverage **and** no stale binding. A material code, config, skill,
  model or policy change makes affected qualification `STALE`.

## Two gates that are never merged

1. **D85 determinism**: aggregate unweighted, aggregate weighted, minimum-path
   unweighted, minimum-path weighted — each ≥ 0.85; weights control 5, effect 5,
   decision 3, transformation 2, retrieval 1, presentation 1; source-executed
   MODEL/MIXED/opaque operations earn no deterministic credit.
2. **Outcome assurance**: a trial succeeds only when durable setup AND repeatable
   results hold inside the frozen envelope. Sampling rule: `α_j = .05/(m·2^j)`;
   first attempt needs 72 trials for one claim, 197 for m = 588. These are
   requirements, not evidence. No independent representative trials ⇒
   `INSUFFICIENT_EVIDENCE`, and no 95 % number anywhere in the row.
