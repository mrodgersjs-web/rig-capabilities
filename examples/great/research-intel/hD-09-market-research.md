---
name: great-hd-09-market-research-yaml
lane: research-intel
exemplar_of: hD-09-market-research.yaml
description: "Reference exemplar — a decision-bound market study with tiered sources, independent corroboration, explicit contradictions, traceable sizing math, sensitivity, uncertainty labels, and local provenance."
---

# hD-09 market research — dental group operations software

## Input

Estimate the US serviceable market for operations analytics sold to dental groups with 5–25 locations, and determine whether a focused vertical offer merits a six-month GTM allocation. State which evidence would reverse the decision.

## Output

`artifacts/market/dental-ops-2026-09/` contains a decision question, tiered source inventory, claim map with two independent sources per load-bearing claim, contradiction log, TAM/SAM/SOM formulas and inputs, dominant sensitivity, dated/stale input flags, tagged synthesis, top-three refutation pass, and locally hashed source snapshots. At least two primary sources underpin the recommendation.

## Acceptance

```console
$ jq -e '[.[] | select(.tier == "primary")] | length >= 2' artifacts/market/dental-ops-2026-09/sources.json
# expected: true
$ python3 scripts/verify_sizing.py artifacts/market/dental-ops-2026-09/sizing.md
# expected: exit 0; every layer has method, formula, inputs, and computed value
$ python3 scripts/uncertainty_lint.py artifacts/market/dental-ops-2026-09/synthesis.md
# expected: exit 0; forward-looking claims are FACT, INFERENCE, or SPECULATION
$ shasum -a 256 -c artifacts/market/dental-ops-2026-09/snapshots.sha256
# expected: every source snapshot reports OK
```

No load-bearing claim rests on a single publisher or a citation chain. Conflicting values remain visible instead of being averaged away; stale inputs are flagged; and the most sensitive assumption includes a quantified swing. The verdict is `answered`, `provisional`, or `insufficient-evidence`, with `./bin/rig-capabilities goal-spec --stem hD-09-market-research` returning OK.