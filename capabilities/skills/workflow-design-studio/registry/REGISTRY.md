# REGISTRY — single source of truth for every workflow (human view)

Machine SSOT: the design rows themselves — `registry/<id>.yaml` (authored) +
`registry/imported/aside-routines.yaml` (reverse-extracted) + `out/*/registry/row.yaml` (compiled
row per workflow). This file is the readable index; drift verdicts come from
`python3 compiler/drift_doctor.py` (exit 2 on drift).

## Row schema
`id | name | surface[] | schedule | owner | done-test | last-drift-check | embed_state | routes`
(definitions in SPEC.md section 2)

## Rows

| id | name | surface | schedule | owner | done-test | last-drift-check | embed_state |
|---|---|---|---|---|---|---|---|
| daily-scorecard-loop | Daily Scorecard Loop | 7 (all) | `3 7 * * 1-5` America/Denver | jake | `compile_workflow.py registry/daily-scorecard-loop.yaml --check` + MANIFEST sha256 | never — run drift_doctor | draft (7 surfaces compiled, nothing installed) |
| aside-routines-imported (122 rows) | live Aside routines | [aside-routine] | per-row rrule | aside-runtime | none-recorded (imported) | never — run drift_doctor | live (87 active + 35 other) |

## Rules
- One design row per LIVE workflow. A workflow that exists on three surfaces is still ONE row.
- A row is created by a design card (plain language) and only changed through the design card.
- `last-drift-check` is written by drift_doctor only. `never` means unchecked — a visible gap.
- Import rows keep `done-test: none-recorded` until their owner writes one; we do not invent done-tests.
