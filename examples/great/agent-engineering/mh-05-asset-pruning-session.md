# What good looks like: retention you can compute, revocation you cannot undo

Source asset: `capabilities/harnesses/mh-05-asset-pruning-session.yaml` (25 gates)
Adjudicator: `rig_capabilities/lifecycle.py` — `rules`, `plan --assets FILE
--now YYYY-MM-DD [--plant NAME]`. `plan` is advisory and write-free; nothing in
this module applies a transition.
Attribution: Discover AI videos `Kbxg-_CXs78`, `nnDAaPpXgOY`; arXiv 2608.29596
(the library as an equation recomputed each cycle, never appended), arXiv
2608.12851 (skill misevolution; reuse attribution as the safety feed). Every
output below is a real run in this repo.

Two feeds decide an asset's fate, and neither may overrule the other.
**Utility** asks whether the asset helps: counterfactual gain of injecting it,
minus retrieval, token footprint and execution overhead — a subtraction, which is
why a well-written asset can carry a negative U(s). **Attribution** asks whether
it has ever hurt: negative reuse attribution accumulates independently of how
useful the asset is, because "it keeps helping me complete tasks" is precisely how
a misused skill survives a utility filter. Eviction is restorable. Revocation is
a tombstone with no edge back to a loadable state, and it is utility-blind.

## 1. The table is printed, not remembered

```
$ python3 -m rig_capabilities.lifecycle rules
states: active, dormant, deprecated, evicted, revoked
loadable (routed): active, deprecated
never loadable: dormant, evicted, revoked

rules:
  attribution_quarantine   active,deprecated   -> dormant
  attribution_repair       active,dormant      -> deprecated
  decay_evict              dormant             -> evicted
  decay_quarantine         active              -> dormant
  ...
legal transitions: 15  (no exit from 'revoked' to a loadable state)
plants: revocation, utility_evict, decay_evict, decay_quarantine, one_way_door,
        record_reason, tombstone, state_record
```

`LOADABLE = active | deprecated` is the whole routing contract: a deprecated
asset still answers a query, a dormant one does not. The test suite asserts the
derived edge table against the rule table, so a new legal transition cannot be
added by intuition — it has to come from a rule.

## 2. A plan reports violations, not a mood

```
$ python3 -m rig_capabilities.lifecycle plan --assets estate.json --now 2026-09-02
{
 "verdict": "INSOLVENT",
 "transitions": [],
 "violations": [
  { "id": "b",
    "violation": "state_unrecorded",
    "detail": "state 'active' carries no recorded reason/timestamp — retention may
               be computed, but the state it lands in still has to be attributable" } ],
 "plants_inert": [],
 "loadable_after": ["b"] }                                                          rc=2
```

A five-state machine whose state is not attributable is a five-state machine that
gets re-litigated every cycle, so an unrecorded state is a violation rather than
a default. The knobs are printed with the verdict (`evict_utility_below: 0.0`,
`decay_half_life_days: 45`, `activity_floor: 0.5`, `park_max_days: 90`,
`min_trials: 3`, `neg_repair_at: 2`, `neg_quarantine_at: 4`, `neg_revoke_at: 6`),
so any proposal can be re-derived instead of trusted.

`unmeasured` is reported as blind, never as zero. `min_trials: 3` stands between
"no data" and "worthless" — treating absence of evidence as evidence of
worthlessness is how a pruning session deletes the asset it has not run yet.

## 3. A healthy estate still moves

```
$ python3 -m rig_capabilities.lifecycle plan --example --now 2026-09-02
verdict OK
  rig-scraper-retry-shortcut      active   -> revoked   by revocation
  rig-deprecated-api-driver       active   -> evicted   by utility_evict
  rig-meeting-notes-formatter     active   -> dormant   by decay_quarantine
  rig-legacy-sftp-upload          dormant  -> evicted   by decay_evict
```

Precedence is fixed and stated: safety (revocation) first, then the attribution
ladder (2 → repair, 4 → quarantine, 6 → revoke), then computed utility, then
activation decay, then the failing-test tail mh-05 already carried. An asset that
is both useless and revoked lands in `revoked`, and `utility_evict` never
manufactures a tombstone.

## 4. Every rule is proven capable of going RED

```
$ python3 -m rig_capabilities.lifecycle plan --example --now 2026-09-02 --plant revocation
verdict INSOLVENT
  rig-scraper-retry-shortcut  active -> dormant  by attribution_quarantine
  reason: quarantine: negative reuse attribution 7 >= 4 — unrouted until repaired     rc=2
```

Naming a guard disables it exactly as a regression would; the estate then reports
INSOLVENT instead of proceeding quietly, and the asset that should have been
tombstoned is still in `loadable_after`. `plants_inert` names any plant that
changed no decision — an inert plant is a finding, never counted as proof. All
eight declared plants are exercised in `tests/test_lifecycle.py` (33 tests), each
reddening its own invariant.

## 5. Input is read-only, and refusals are named

`plan` never writes: the tests patch `open`/`write`/`unlink`/`rename`/`rmtree` and
hash a sentinel tree before and after the call. Malformed input is a named
refusal with the plan's exit code, not a stack trace:

```
$ python3 -m rig_capabilities.lifecycle plan --assets broken.json --now 2026-09-02
assets_unreadable:broken.json: record 1 is not a JSON object (Expecting property
name enclosed in double quotes, column 26); expected a JSON array, an
{"assets": [...]} object, or one record per line                                       rc=2
```

Three shapes load: a JSON array, an `{"assets": [...]}` object, and one record
per line. A pretty-printed object used to traceback here, because the loader only
knew "starts with `[`" and "one record per line", and the failure mode a user
actually hits was a traceback ending in a JSON parser message.

## 6. Not claimed

The counterfactual gain this machine consumes is produced elsewhere — the
with/without A/B runner is a separate row — and `plan` goes RED rather than
inventing the number when the finding is absent. And no transition is applied
here: executing a transition is a different step, under Gate-D, on a different
day. A plan that also pruned would not be reviewable.
