# ULTRA Judgment slice — signal inventory

Advisory Jev packs + a deterministic consumer-routing contract for the seven ULTRA
studios, built on the existing `s1gate` engine (no second engine). Everything here is
**advisory** (`calibrated: false`) and **offline-tested only**; live Jev and semantic
calibration are NOT claimed. See "Not tested" at the bottom.

Packs: `capabilities/harnesses/s1gate/rubrics/ultra.{questioning,research,forecasting,judgment,execution,proof,learning}.json`
Router + gates + computed metrics: `rig_capabilities/ultra_gates.py` (`GATES`, `route()`, `coverage` / `information` / `trimmed_mean`)
Tests: `tests/test_ultra_gates.py` (29 offline tests)
Source of signals: `/Users/rig128gb/Developer/ultraplan/studios/*/STUDIO.md` ("Jev in this studio").

## Reconciling the docs' "39 signals" claim

The studios README claims 39 rubrics. That figure is **context, not an acceptance count**,
and it mixes three different things. Split honestly:

| Bucket | Count | What it is |
|---|---|---|
| Unique Jev classifiers shipped | **37** | a `noul` / `choice` / `score` question in a pack |
| Deferred classifier | **1** | `q.duplicate_of` — needs a call-time dynamic option list |
| Computed metric counted as a "rubric" in the 39 | **1** | `dq.information = min(class_resolved)` — deterministic code, not a classifier |
| **Total vs README "39"** | **39** | 37 + 1 deferred + 1 computed = the 39, reconciled |

`v.verdict_consistent` appears in both the Execution and Proof studio tables; it is one
classifier, defined once (in `ultra.execution`), so it is counted a single time (this is why
the README lists Proof as "3"). Verified on disk: 7 packs, 37 unique question ids, all
`calibrated: false`.

## Unique classifiers by studio (37)

| Studio pack | Classifiers (question id = doc signal) |
|---|---|
| `ultra.questioning` (6) | shape=q.shape, decision_critical=q.decision_critical, leading=q.leading, cls=q.class, class_resolved=q.class_resolved, is_decision=card.is_decision |
| `ultra.research` (6) | claim_supported=r.claim_supported, source_grade=r.source_grade, is_primary=r.is_primary, contradicts_settled=r.contradicts_settled, novelty=r.novelty, stale_risk=r.stale_risk |
| `ultra.forecasting` (5) | reason_quality=f.reason_quality, reference_class_named=f.reference_class_named, anchored_on_author=f.anchored_on_author, disagreement_is_factual=f.disagreement_is_factual, cause_is_testable=pm.cause_is_testable |
| `ultra.execution` (5) | diff_matches_claims=b.diff_matches_claims, claim_has_evidence=b.claim_has_evidence, scope_creep=b.scope_creep, verdict_consistent=v.verdict_consistent, tripwire_fired=x.tripwire_fired |
| `ultra.proof` (3) | done_test_is_vacuous=p.done_test_is_vacuous, claim_atomic=p.claim_atomic, evidence_is_command_output=p.evidence_is_command_output |
| `ultra.learning` (4) | attribution=l.attribution, regression_risk=l.regression_risk, lesson_is_general=l.lesson_is_general, rubric_wording_defect=l.rubric_wording_defect |
| `ultra.judgment` (8) | frame=dq.frame, alternatives=dq.alternatives, values=dq.values, reasoning=dq.reasoning, commitment=dq.commitment, question_is_atomic=j.question_is_atomic, genuinely_different=alt.genuinely_different, spec_complete=s.spec_complete |

Grouping note: the README's separate "Plan (DQ chain)" and "DECOMP" rows are folded into
`ultra.judgment`, because judgment-jev/STUDIO.md owns the rubric registry and the
decision-quality chain is itself a judgment. They are not extra studios.

## Deterministic derived metrics — deliberately NOT Jev questions

These read like signals but are arithmetic or code gates. Asking a probability model to do
what code does exactly is the mistake this split prevents. Each is a function in
`ultra_gates.py` or a `computed_not_classifier` note in the owning pack.

- `dq.information` = `min(class_resolved)` over 14 classes — `information()`, weakest link
  not mean; refuses to default high on a missing class.
- coverage = answered classes / 14 — `coverage()`; an unreported class is missing, not free credit.
- swarm aggregate = trimmed mean + spread — `trimmed_mean()`; warns below 3 forecasts.
- Research bar counting (only HIGH), liveness (HTTP+archive), dry marginal value — code.
- Forecasting median p_done_test band, Brier — code.
- Execution fences-disjoint, lease-held, done-cmd-green + planted RED-to-GREEN, verifier-family != worker — code checks.
- Proof hash-chain / attestation digests; Learning taxonomy reweight / write-back target — code.

## Deferred with reason

- `q.duplicate_of` (Questioning): a `choice` over a *dynamic* recent-bank-id set (up to 255);
  its criteria are call-time, not a static registry field, so a fixed pack cannot carry it.
  Dedup stays in normalize-dedup code. Recorded in `ultra.questioning.notes`.

## Consumer routing contract (`ultra_gates.py`)

`GATES` declares each studio gate with its pack, the code checks that run BEFORE Jev, the
required facts, and whether it `requires_human` or is a kill switch (`escalate_is_blocking`).
`route()` returns one explicit next move. Its tests guarantee: an offline run (`live=False`,
the default) is `offline_code_only` with `cleared:false`, so an unattended caller can never
read a code-only check as a cleared gate; a machine PASS on a `requires_human` gate becomes
`human_card`, never `advance` (Gate-D unchanged; `outward.gate_d` has no pack — Jev cannot
authorise an outward action); a provider error, undecidable rule, missing fact, or unknown
gate halts fail-closed; an advisory pack annotates rather than halts, except kill-switch gates.

## Provenance of this build (honest)

A concurrent process dropped the seven `ultra.*` packs (~15:19) while the First Mate task
`t_ultra_judgment_slice_20260918T210300Z` still read `waiting` and declared no dispatch; it
then wrote `ultra_gates.py` + `tests/test_ultra_gates.py`. Mid-write it transiently broke the
repo-wide pack validator (`options` vs `criteria`; a malformed `p.source_grade.MED` rule); the
settled on-disk state is correct and the validator is green. This session was a **duplicate**:
it first added its own router (`s1gate_ultra.py`) + tests, then **retired them** once
`ultra_gates.py` was confirmed strictly more complete (full GATES registry, human-authority /
kill-switch semantics, computed metrics as functions, 29 passing tests over the whole
acceptance matrix). The surviving addition here is this reconciliation doc only. No pack was
forked to a competing name set; no pre-existing pack or unrelated dirty work was touched.
Nothing is committed, pushed, deployed, or made enforcing.

## Not tested (do not claim)

- Live Jev responses and semantic calibration — no provider calls; all tests mock the
  provider. Mocks prove routing and fail-closed behaviour only.
- Threshold correctness — every threshold is provisional and advisory until `s1gate
  calibrate` sweeps it against labelled decisions (needs >= 20 labelled rows each).
- Option strings carrying `/` or spaces (e.g. `cls`, `novelty`, `attribution`) are not
  exercised against the live `criteria`-to-Jev request shape.
