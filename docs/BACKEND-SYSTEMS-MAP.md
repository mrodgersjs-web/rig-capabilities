# Backend Systems Map — RIG Durable/Repeatable Standard (B01–B11)

Owner tiers per the plan: **T0** pure deterministic code · **T1** request-scoped
service · **T2** durable state + crash-recovery · **T3** cadence + human owner.
Nothing in this repo runs T3: no scheduler, no cron, no model is wired into a
write path. Cadence remains an open owner decision.

All components are stdlib-only. External engines (Postgres, Supabase) are
reached through drivers already installed; nothing here bundles a scheduler,
ORM, or client library.

## Record plane — `rig_capabilities/build_store.py` (T2)

- **Inputs:** cell coordinates `L{n}-D{d}-A{m}-{step}`, immutable
  `(process_key, process_version)`, idempotency keys, fencing tokens.
- **Outputs:** append-only rows in schema `rig_build` — portable DDL
  (`portable_ddl_sqlite()`, prefix stripped) ships to SQLite and Postgres;
  live database selected by `RIG_BUILD_DATABASE_URL`.
- **Invariants:** events reject duplicate/out-of-order sequence; artifacts are
  content-addressed (sha recomputed, dedupe by hash); outbox leases carry
  `claim_fence` (zombie settle refused); one effect per idempotency key
  (replay returns the existing run; effect ids derive from the result hash);
  intake never self-advances run state.
- **Verified by:** `tests/test_build_store.py`, `tests/test_durable_fixtures.py`
  (V07 determinism/exactly-one-effect, V17 fresh-setup reopen).

## Measurement plane — `rig_capabilities/measure_store.py` (T2/T3 data)

- **Inputs:** trials with `(cell, trial_id, attempt_seq)` keys, build/seed/
  runtime/model identity, verdict `PERFECT|VERIFIED|PARTIAL|FEEDBACK|FAILED`.
- **Invariants:** frozen joint contract — n≥72, durable≥10, wall≥24h,
  cross-model, cross-day, human 5/5; attempts accumulate, trials never
  duplicate; qualification and assurance are recomputed from evidence rows,
  never asserted; `record_trial` refuses an empty/absent contract.
- **Verified by:** `tests/test_measure_store.py`.

## Intake worker — `rig_capabilities/build_intake.py` (T1, B31)

- **Flow:** closed packet → validate (schema/cell/route/hash) → hash →
  `put_source_document` (dedupe by url-hash; FETCHED requires the content
  hash) → idempotency-keyed `start_run` → route via named `ROUTES` table.
- **Invariants:** no default route — ambiguous packets are refused; tampered
  content refused; replay never double-routes. CLI exit codes are the
  contract. **Verified by:** `tests/test_build_intake.py`.

## Corpus freeze — `rig_capabilities/build_corpus.py` (T1)

- Manifest-v1: 30 practitioner-URL seeds, PENDING rows + `.sha256` sidecar;
  `freeze(v1)` refuses re-freeze; deliberately **no** add/fetch verb.
  A36 keyed-practitioner and A37 provenance rules travel on every row.

## Migrations — `rig_capabilities/build_migrate.py` (B12/B13)

- `build_migrate.py plan` emits an identity-proof receipt (sha256-pinned
  artifacts + decisions + rollback notes); apply is never implicit;
  `verify` re-proves identity against the receipt.

## Deterministic gates — `tool_selection.py`, `d85.py`, `d85_gates.py`,
`estate_ledger.py`, `estate_validator.py` (T0/T1)

- Deterministic eligibility/verdict machinery; D85 four-ratio score,
  exit-2 BLOCK terminal per version; signed gate registry under
  `authority/` (`registry.json`) is the approval authority — unsigned
  `approvals.jsonl` is no longer trusted by surface install (forgery gap
  closed by the surfaces-approval-binding receipt).
- **Verified by:** `tests/test_d85*.py`, `tests/test_estate_ledger.py`.

## Surfaces — `surfaces_render.py` + `authority/surfaces.json` (T1)

- `check|render|stage|install` per surface; `install` splices the managed
  block once and consumes its signed approval (reads the signed gate
  registry). Current honest state: mechanism wired, surfaces UNWIRED pending
  typed per-surface approvals (Gate-D).

## Service handlers — `server.py` `capabilities_*` (T1)

- Read/write handlers over both stores (record write/read, measure write,
  quorum, build run/contract reads); sqlite/PG dialect adapter
  (`%s → ?`); handlers never raise — typed error dicts, `configured:false`
  when unconfigured.

## Loop harness — `loops.py` durable-build (T2, single-process file state)

- Builder cannot certify itself; candidate binding + TOCTOU checks; run-state
  durability; `rig-loop test durable-build` is the executable check.
  Single-process only: cross-process claims belong to the record plane, not
  loop files.

## Open seams (named, not hidden)

- **T3 unowned:** no cadence runner exists; outbox consumers and daily loops
  await an owner decision (Kestra/Temporal/Prefect were explicitly deferred).
- **Live trials:** assurance numbers require ≥72 recorded trials (none yet).
- **Supabase:** single-role schema target `mfcflrfhvfahwpirdytz` pending live
  key via keychain (never env/echo).
- **Hook manifest:** the external receipt claiming `bin/hooks/*d85*` scripts
  and a `rig-d85-admission hook-manifest` is NOT reproducible in this repo —
  the live `[d85]` enforcement is OMP-integrated. Treat that receipt section
  as unverified.
