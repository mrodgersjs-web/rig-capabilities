---
name: great-hd-08-expansion-play-yaml
lane: revenue-gtm
exemplar_of: hD-08-expansion-play.yaml
description: "Reference exemplar — an expansion cohort earned by account-level usage thresholds, suppression, playbook matching, numeric ROI, concrete pricing, CRM records, and dormant outreach."
---

# hD-08 expansion play — reporting module

## Input

Find existing customers whose seat utilization exceeds 85%, advanced-report usage exceeds 20 runs per month, and tenure exceeds 90 days. Suppress churn-risk, unresolved escalation, and active-negotiation accounts. Draft a reporting-module expansion only for accounts with evidence.

## Output

`artifacts/expansion/reporting-2026-09/` contains the reproducible eligibility query, metric series and thresholds, reason-coded suppressions, engaged champions or nurture-track designations, playbook IDs and selection rules, account-specific ROI narratives, priced proposal drafts, objections, Twenty opportunity receipts, confidence-weighted forecast delta, and inert Gate-D state.

## Acceptance

```console
$ jq 'length >= 1' artifacts/expansion/reporting-2026-09/eligible.json
# expected: true, or the run records an explicit empty-cohort outcome
$ grep -c 'hours\|seats\|%\|\$' artifacts/expansion/reporting-2026-09/roi/acme-dental.md
# expected: at least 3 numeric value references tied to signals.jsonl
$ python3 scripts/ask_scan.py artifacts/expansion/reporting-2026-09/drafts/
# expected: exit 0; every play-track draft names module, price, or seat ask
$ ./bin/rig-capabilities goal-spec --stem hD-08-expansion-play
# expected: verdict OK
```

Every observed signal meets its declared threshold and every play ID exists in the expansion playbook. Opportunity count equals play-track account count; forecast weighting is stated. No account-facing draft is armed without `APPROVE reporting-2026-09`, so the complete safe verdict is `plays-staged`.