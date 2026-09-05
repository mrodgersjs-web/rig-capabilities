---
name: great-hd-07-churn-prevention-yaml
lane: revenue-gtm
exemplar_of: hD-07-churn-prevention.yaml
description: "Reference exemplar — an evidence-scored churn cohort matched to governed save plays, excluding false positives and staging personalized drafts without discount or customer-contact shortcuts."
---

# hD-07 churn prevention — September renewals

## Input

Identify accounts renewing within 90 days that show usage decline, support pressure, billing risk, or stakeholder change. Exclude accounts with active expansion motions or resolved tickets. Customer contact and any commercial concession remain draft-only.

## Output

`artifacts/churn/renewals-2026-09/` contains the reproducible cohort query and hash-stable results, versioned health scores with inputs, reason-coded exclusions, two or more root-cause pointers per account, governed play matches, evidence-linked drafts, escalation owners/dates, Twenty task receipts, and measurable save/kill tracking. Every commercial term is labeled with its approval requirement.

## Acceptance

```console
$ python3 scripts/health_score.py --cohort artifacts/churn/renewals-2026-09/cohort.json --out artifacts/churn/renewals-2026-09/scores.json
# expected: exit 0 with script_version and per-account inputs
$ python3 scripts/concession_scan.py artifacts/churn/renewals-2026-09/drafts/
# expected: exit 0; every concession has REQUIRES APPROVAL and a limit
$ ./bin/rig-capabilities goal-spec --stem hD-07-churn-prevention
# expected: verdict OK
```

No account enters the save queue from score alone: root-cause evidence and an existing play ID are both present. CRM task count equals save-queue count; each tracker has metric threshold, kill criterion, and review date. With no batch approval, drafts retain `arm: false` and the verdict is `plays-staged`, never contacted.