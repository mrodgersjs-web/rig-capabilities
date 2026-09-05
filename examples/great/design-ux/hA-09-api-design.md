---
name: great-hA-09-api-design
lane: design-ux
exemplar_of: hA-09-api-design.yaml
description: >-
  A contract-first REST change that proves error-envelope reuse, per-operation security, compatibility, examples, and consumer behavior before handler code exists.
---

# hA-09 API design — contract is the product

## Input

Design `GET /orders` and `POST /orders` for the checkout service, consumed by `web-checkout` and `ops-console`. Author `openapi.yaml` before handlers. Lists use cursor pagination with a fixed maximum; mutations support `Idempotency-Key`; every public or authenticated operation declares security explicitly.

## Output

```console
$ spectral lint openapi.yaml | tee .rig/api/lint.txt
No results with a severity of 'error' found!
$ oasdiff breaking published/openapi.yaml openapi.yaml | tee .rig/api/breaking.txt
No breaking changes
$ pytest -q tests/consumer/test_orders_contract.py | tee .rig/api/consumer-test.txt
4 passed
```

One `Error` component containing `code`, `message`, `details`, and `requestId` is referenced by every 4xx/5xx response. `pagination-audit.txt` lists the cursor, default order, filter fields, and max page size per list operation. `security-audit.txt` proves operation and `security` counts match; request and response examples validate against the schemas.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-09-api-design | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-09-API-DESIGN" and any(.goal.gates[]; .id == "2.2" and .required == true) and any(.goal.gates[]; .id == "2.4" and .required == true)'
true
```

A breaking change without a version or sunset disposition, anonymous-by-omission operation, or consumer test failure blocks the contract verdict.
