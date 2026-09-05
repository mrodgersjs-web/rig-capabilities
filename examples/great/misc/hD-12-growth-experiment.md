---
name: great-hD-12-growth-experiment
lane: misc
source: canonical-curated
exemplar_of: hD-12-growth-experiment
description: "Reference exemplar for a pre-registered growth experiment with live tracking proof, sizing, guardrails, uncertainty, and a rule-bound decision."
---

# Growth experiment: checkout proof-strip test

## Input

Test whether replacing generic checkout reassurance with three sourced proof points improves completed checkouts by at least 8% for first-time mobile visitors. Record the cohort, primary metric, two guardrails, MDE, sample size, checkpoints, variant hash, and scale/iterate/kill rules before arming the variant.

```console
$ ./bin/rig-capabilities goal-spec --stem hD-12-growth-experiment
$ jq -e 'all(.[]; .fired_on_staging)' artifacts/experiments/checkout-proof/tracking_proof.json
```

## Output

The served goal spec identifies `GL-MH-D12-GROWTH-EXPERIMENT` and exposes the experiment gates. The run directory contains a numeric five-slot hypothesis, pre-registration hash, analytics query id, sizing inputs, at least two owned guardrails, a hashed eligibility configuration, and staging event evidence. Results report the effect interval and guardrail status; the decision cites the unchanged pre-registration rules. The variant remains `arm: false` without `APPROVE <run_id>`.

## Acceptance

- Both commands exit 0; the tracking query prints `true`.
- `results.json` contains `effect`, `interval_low`, `interval_high`, and `guardrail_statuses`.
- The proof packet binds the pre-registration and variant hashes.
- A kill or inconclusive result is logged with the same evidence as a win; no post-hoc threshold change is hidden.
