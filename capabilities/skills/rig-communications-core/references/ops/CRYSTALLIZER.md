# Crystallizer (v18.9) — determinism spec

What becomes a procedure: a loop trajectory that succeeded **three times** with
zero corrections. Source of truth: `data/comms/loops.jsonl` (append-only).

## Deterministic extraction rule
1. Group loop rows by `(surface, template-or-artifact-family)`.
2. A family qualifies when ≥3 families-distinct artifacts reached `ship` with
   0 correction events between start and ship.
3. Emit a DRAFT procedure (SKILL.md skeleton + done_when from the ship packets'
   gate JSONs) into `data/comms/crystallizer-candidates/`. The emitter is pure
   file arithmetic — no LLM, no judgment.

## Gates before anything installs
- Every done-test in the draft must have a demonstrated RED path
  (adversarial-verification-loop: plant the failure, prove red, restore).
- Cross-family verifier verdict before install; install only into the harness
  the verifier names, with the sha256 of the draft bound in the ledger.
- Recalibration proposals (v11) stay PROPOSALS: the crystallizer may draft a
  sigma change as a procedure, never apply one.

## Honest ceiling (ponytail comment lives in the future emitter code)
Today `ships/` holds test-path packets with `real_path_status: PENDING` — zero
families qualify yet. The candidate directory being empty is the correct state,
not a missing feature; it fills only as measured ships accumulate.
