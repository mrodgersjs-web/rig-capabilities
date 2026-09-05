---
name: great-hd-06-nps-analysis-yaml
lane: revenue-gtm
exemplar_of: hD-06-nps-analysis.yaml
description: "Reference exemplar — a reconciled NPS wave with deterministic score math, predeclared segments, PII-safe row-anchored verbatims, quantified themes, caveats, and owned follow-up."
---

# hD-06 NPS analysis — Q3 customer wave

## Input

Analyze the Q3 survey wave for active customers collected 2026-08-01 through 2026-08-31. Preserve the raw export, predeclare plan tier, tenure, and company-size cuts, and mask all direct identifiers before extracting themes or quotations.

## Output

`artifacts/nps/q3-2026/` contains cohort definition, original and working-copy hashes, `integrity.json`, deterministic `score.json`, `responses_redacted.csv`, the fixed segment spec and results, counted themes with row IDs, `verbatim_map.json`, `report.md` with response-rate/sample caveats and owned recommendations, plus detractor and promoter routing files.

## Acceptance

```console
$ python3 scripts/nps_score.py --in responses.csv --out artifacts/nps/q3-2026/score.json
# expected: exit 0; p, n, d and round(100*(p-d)/total, 1) are present
$ python3 scripts/redact_pii.py --in responses.csv --out artifacts/nps/q3-2026/responses_redacted.csv
$ grep -cE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+' artifacts/nps/q3-2026/responses_redacted.csv
# expected: 0
$ ./bin/rig-capabilities goal-spec --stem hD-06-nps-analysis
# expected: verdict OK
```

Export and platform row counts reconcile or the exact delta is explained. Every reported theme covers counted comments and has at least two masked quotes whose row IDs exist in the redacted export; themes plus `misc` cover at least 80% of comments. Recommendations name owner and due date, and contactable detractors are represented by Twenty task receipts.