---
name: great-mh-04-deviation-expedition-session
lane: agent-engineering
source: canonical-curated
exemplar_of: mh-04-deviation-expedition-session
description: "Reference exemplar for a three-tail deviation expedition whose conservative sigma band is recomputed and certified by a separate verifier."
---

# Deviation expedition: onboarding promise

## Input

Start with at least five non-identical baseline scores for an onboarding promise. Generate three engine-tagged positive candidates, three named-failure anti-candidates, and a one-to-one repaired tail. Preserve the raw baseline so a separate verifier can recompute the winner.

```console
$ ./bin/rig-capabilities goal-spec --stem mh-04-deviation-expedition-session
$ python3 ~/Developer/needle-haystack/artifacts/meta/mathexec_substrate.py self-test
$ python3 ~/Developer/needle-haystack/artifacts/meta/mathexec_substrate.py deviation --score <s> --baseline <b>
```

## Output

The first command serves the expedition goal spec; the second proves the estimator includes working planted failures. Each finalist receives JSON containing `certified_z`, calculated as the conservative minimum across applicable estimators, plus a routing row with `z_cert`, `band`, `action`, and `target`. Any `|z| >= 10` candidate also carries adversarial stability evidence. The generating pass proposes a winner but does not certify it.

## Acceptance

- Three tail files exist, and negative-to-repaired mappings are one-to-one.
- Every finalist has a saved deviation JSON and a routed band.
- `verdict.md` names a distinct verifier and its recomputation matches within float tolerance.
- An `expedition_run` event round-trips with the winning band and certified z; disagreement voids the verdict, not the retained tails.
