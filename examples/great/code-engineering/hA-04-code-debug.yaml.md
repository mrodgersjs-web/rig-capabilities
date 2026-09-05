---
name: great-hA-04-code-debug
lane: code-engineering
exemplar_of: hA-04-code-debug.yaml
description: >-
  A reproducible stale-cache failure reduced through competing hypotheses to one causal mechanism, fixed at that mechanism, and locked with red-then-green regression evidence.
---

# hA-04 code debug — mechanism before patch

## Input

Observed: a second checkout request returns the first customer's tax total. Expected: totals are keyed by customer and cart. Environment: Python 3.13 with the recorded lockfile hash. Before editing, write two killable hypotheses: cache key omits customer ID, or request context leaks between workers.

## Output

```console
$ pytest -q tests/test_tax.py::test_cache_separates_customers
FAILED ... assert 1900 == 2400
$ git log --oneline -20 -- src/tax/cache.py > .rig/debug/history.txt
$ pytest -q tests/test_tax.py::test_cache_separates_customers
1 passed
```

`.rig/debug/root-cause.md` states: “Customer totals collide because `make_key` hashes only cart line IDs at `src/tax/cache.py:47`.” The fix adds customer identity to that shared key mechanism; it does not catch the error, special-case the fixture, or extend a timeout. `regression-proof.txt` contains assertion RED at the pre-fix SHA and GREEN at the fixed SHA.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-04-code-debug | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-04-CODE-DEBUG" and any(.goal.gates[]; .id == "3.2" and .required == true)'
true
```

The exact repro command must pass after the fix, the full suite must be green, and temporary instrumentation must be absent from the final diff.
