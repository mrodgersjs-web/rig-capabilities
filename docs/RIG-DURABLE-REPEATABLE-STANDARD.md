# RIG Durable & Repeatable Standard — Umbrella (A01–A06, frozen)

Frozen 2026-09-12. This is the one-page authority binding the durable/repeatable
standard together. Everything named here exists on this branch or is explicitly
listed as an open seam. Where this page and a named artifact disagree, the
artifact plus its test output wins — patch this page.

## The standard in one law

A build is **durable** when its state survives a crash at any instruction
(append-only records, idempotent effects, fenced leases) and **repeatable**
when a fresh setup reproduces the warm outcome from recorded inputs alone
(no memory, no ambient state). Neither is claimed from a feeling: each is a
named test on a real path (`tests/test_durable_fixtures.py` V07/V17).

## Frozen contracts (names, not prose)

| Contract | Carrier | Frozen shape |
|---|---|---|
| Owner/routing precedence | `authority/standards/tool_selection.v2.json` (sha `c8e6f6fec6e5f042…`) + `rig_capabilities/tool_selection.py` | clock/recovery → resident → genuine graph → human coordination → ordinary schedule → pure computation; missing or contradictory facts BLOCK, never default |
| Record plane schema | `build_store.portable_ddl_sqlite()` | same DDL ships SQLite and Postgres; schema `rig_build` |
| Measurement contract | `measure_store.py` | n≥72, durable≥10, wall≥24h, cross-model, cross-day, human 5/5; attempt key `(cell, trial_id, attempt_seq)` |
| Context packet | `context_packet.py` (schema `rig.context-packet.v1`) | diagnosis-bounded budgets; stale source hash stops the build (`BLOCKED`) |
| Certificate | `rig-determinism-85 verify-cert` | four ratios recomputed ≥ 0.85; A1-only; refusal recomputed, not cached |

## Roles that cannot merge

Builder ≠ approver ≠ certifier ≠ verifier. `rig-stackwright` (builder agent)
cannot approve, self-certify, claim assurance, certify A2–A4, or launder
staleness. The `d85_certified` gate is halt-tier: `advance(force=…)` is
refused (plant-proven, `rig-loop test durable-build` 6/6). Gate-D eligibility
(D85) and authorization (one exact outward effect) never substitute.

## Components

- Standard docs: this page + `docs/BACKEND-SYSTEMS-MAP.md` (T0–T3 owner tiers).
- Skills: `durable-build` (v1.1.0, done_tests 7/7), `rig-build-standard`,
  `d85-compliance-checklist` (canonical, sha `f92d4a85117d`).
- Code: `build_store` / `measure_store` / `build_intake` (B31) /
  `build_corpus` (30-URL manifest-v1 freeze, no add verb) / `build_migrate`
  (identity-proof receipts) / `context_packet` / `surfaces_render`.
- Service: `server.py` `capabilities_*` handlers (typed-error, never raise).

## Four-runtime wiring (A14–A22 honest state)

`surfaces_render check` renders and verifies the managed block per surface;
`install` splices once **and consumes a signed approval** read from the
signed gate registry (unsigned `approvals.jsonl` is not trusted). Current
verdict: mechanism complete, all surfaces **UNWIRED** pending typed per-surface
Gate-D approvals. The four-runtime launcher compare has NOT been
re-run this cycle — the existing wiring receipts are partial.

## Open seams (named, never hidden)

T3 cadence has no owner or runner; zero live trials recorded; Supabase target
pending live key; the external receipt's `bin/hooks/*d85*` and
`rig-d85-admission hook-manifest` claims are not reproducible here — live
`[d85]` enforcement is OMP-integrated (flagged unverified).
