---
name: great-hc-08-dashboard-design-yaml
lane: design-ux
exemplar_of: hC-08-dashboard-design.yaml
description: "Reference exemplar — a renewal-risk dashboard where every widget drives a named decision, binds to real data, and survives loading, error, empty, and stale states."
---

# hC-08 dashboard design — renewal risk

## Input

Design a customer-success dashboard for weekly renewal triage. The primary viewer is the CSM lead; the primary decision is which accounts need intervention before the next renewal window.

## Output

`artifacts/dashboard/renewal-risk/metric-map.yaml` maps each metric to viewer, decision, threshold, query or endpoint, and chart rationale. `states.md` defines the 12-widget grid at 1440px and 1024px plus loading, empty, error, and stale-data behavior. `interactions.md` gives every summary metric a row-level drill-down and specifies URL-shareable filter persistence. `perf-budget.yaml` declares query, payload, and render budgets.

## Acceptance

```console
$ grep -rEo '#(e|f)[0-9a-fA-F]{5}' artifacts/dashboard/renewal-risk/ --include='*.css'
# expected: every hit is status-semantic or dispositioned in the decision log
$ sha256sum artifacts/dashboard/renewal-risk/dashboard-final.png > artifacts/dashboard/renewal-risk/FREEZE.txt
$ ./bin/rig-capabilities goal-spec --stem hC-08-dashboard-design
# expected: verdict OK
```

The metric map contains no "nice to know" entry and no unbound widget. A named reviewer identifies the declared primary metric within five seconds. Red, amber, and green are reserved for status; stale widgets show timestamps; the KPI rubric meets its threshold; and final captures exist at both declared breakpoints.