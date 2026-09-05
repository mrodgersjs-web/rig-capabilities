---
name: great-hd-05-launch-prep-yaml
lane: revenue-gtm
exemplar_of: hD-05-launch-prep.yaml
description: "Reference exemplar — a tiered product launch reduced to owned, hashed checklist evidence with staging analytics, full-path exercise, rollback proof, and an unarmed go-live gate."
---

# hD-05 launch prep — reporting workspace

## Input

Prepare a Tier 2 launch of the reporting workspace across landing page, lifecycle email, LinkedIn, sales enablement, and docs. The launch may become ready, but no deploy, publish, or send occurs without approval for `reporting-workspace-2026-09`.

## Output

`artifacts/launch/reporting-workspace-2026-09/` contains tier rationale, complete ownership map, evidence-linked checklist, approved asset hashes, support FAQ/macros, messaging consistency report, staging analytics for signup/conversion/share, an end-to-end trace from landing to first value, tested feature-flag rollback, CRM/email plumbing evidence, five owned risks, compliance review, and `verdict.json`.

## Acceptance

```console
$ shasum -a 256 -c artifacts/launch/reporting-workspace-2026-09/assets.sha256
# expected: all approved assets report OK
$ python3 scripts/consistency_check.py artifacts/launch/reporting-workspace-2026-09/assets.json
# expected: exit 0 and positioning_match: true
$ scripts/e2e_launch.sh
# expected: exit 0 with evidence for landing -> signup -> first value
$ python3 scripts/launch_verdict.py artifacts/launch/reporting-workspace-2026-09/checklist.yaml
# expected: Tier 2 score is at least 0.95 or named shortfalls force no-go
```

The rollback log proves the prior state returns on staging, plumbing records a real test-enrollment message ID, and every checklist item has status plus evidence. With no typed approval, `verdict.json` says `ready-unarmed`; `./bin/rig-capabilities goal-spec --stem hD-05-launch-prep` returns verdict OK.