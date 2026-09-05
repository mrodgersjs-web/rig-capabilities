---
name: great-hd-04-pricing-test-yaml
lane: revenue-gtm
exemplar_of: hD-04-pricing-test.yaml
description: "Reference exemplar — a pricing experiment designed from baseline and MDE through eligibility, guardrails, hashed variants, rollback, and a decision that cannot override a tripped guardrail."
---

# hD-04 pricing test — annual billing fence

## Input

Test whether showing a 15% annual-billing incentive to new 5–25-location accounts improves paid conversion by at least 12% relative without increasing 30-day refunds or support contacts. Existing contracts are excluded. This run is design-only unless separately armed.

## Output

`artifacts/pricing/annual-fence-2026-09/` contains the falsifiable hypothesis and kill conditions, pre-variant baseline with query IDs, guardrail tripwires, sample-size math, hashed `variants.yaml`, eligibility exclusions, exact rollback instructions, measurement definitions, guardrail review, decision record, and ProofPacket. `variants.yaml` keeps `arm: false` because no approval was supplied.

## Acceptance

```console
$ jq 'keys | length >= 3' artifacts/pricing/annual-fence-2026-09/baseline.json
# expected: true; values include source query ids and captured_at
$ python3 scripts/validate_variants.py artifacts/pricing/annual-fence-2026-09/variants.yaml
# expected: exit 0 for price, package, segment, and traffic split
$ ./bin/rig-capabilities goal-spec --stem hD-04-pricing-test
# expected: verdict OK
```

Sizing inputs trace to `baseline.json`; every guardrail defines a metric, threshold, and alert channel. Eligibility evidence shows existing-contract exclusions. Measurement reuses the baseline query definitions byte-for-byte, and any tripped guardrail forces `kill` or `stop` regardless of the primary conversion result. Without `APPROVE annual-fence-2026-09`, the honest complete verdict is `designed`.