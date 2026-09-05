---
name: great-hA-03-code-test-writing
lane: content-publishing
exemplar_of: hA-03-code-test-writing.yaml
description: >-
  A parser-contract test session that proves assertion-level RED, repeated deterministic GREEN, isolation, and a planted production mutation caught by the new suite.
---

# hA-03 test writing — prove the test can fail

## Input

Add behavior tests for `parse_limit(value)` in `src/query.py`: positive integers return an integer; empty, zero, negative, and nonnumeric values raise the public validation error. Follow `tests/test_query.py` and its pytest assertion style; do not expose private state or add production test hooks.

## Output

The same focused command is captured before and after the implementation change:

```console
$ git rev-parse HEAD
7e31b65...
$ pytest -q tests/test_query.py -k parse_limit
FAILED tests/test_query.py::test_parse_limit_rejects_zero - AssertionError: expected ValidationError
$ pytest -q tests/test_query.py -k parse_limit
5 passed
```

`.rig/tests/red-runs.txt` contains the first assertion failure and pre-change SHA. Five consecutive focused runs populate `determinism.txt`; the file passes standalone and in the full suite. `mutation.txt` records a planted `value <= 0` to `value < 0` change, the zero-boundary test failing, and restoration before closure.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-03-code-test-writing | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-03-CODE-TEST-WRITING" and any(.goal.gates[]; .id == "3.4" and .failure_tier == "halt")'
true
```

Import errors, fixture failures, and green-only tests do not satisfy the RED or mutation gates.
