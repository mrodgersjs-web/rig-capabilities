---
name: great-hB-09-content-audit-session-yaml
lane: security-review
exemplar_of: hB-09-content-audit-session.yaml
description: Reference exemplar for a reproducible content audit with immutable inventory, complete data joins, locked scoring, legal verdicts, and reversible recommendations.
---

# hB-09-content-audit-session.yaml — great example

## Input

Audit a sitemap-derived URL inventory using 90-day analytics and Search Console exports. Freeze the inventory hash and rubric weights before scoring. URLs missing both traffic and impression evidence receive `insufficient`; prune is only a recommendation and never a deletion in this session.

## Output

The run joins at least 95% of URLs or enumerates misses, deterministically scores every row, assigns exactly one of keep/refresh/consolidate/prune/insufficient, generates one brief per refresh verdict, and builds an acyclic consolidation graph whose targets are not pruned. An append-only ledger preserves every verdict.

```console
$ python3 scripts/join_check.py "$SESS/inventory.csv" "$SESS/analytics.csv" "$SESS/gsc.csv" --min 0.95
# expected: exit 0 and proof/join_report.json names any unmatched URL

$ python3 scripts/verdicts.py "$SESS/scores.csv" "$SESS/rubric.yaml"
# expected: each URL receives exactly one legal verdict

$ python3 scripts/consolidation_graph.py "$SESS/verdicts.csv"
# expected: no cycles and no canonical target marked prune
```

## Acceptance

- Inventory and rubric hashes are fixed before scoring; rubric weights total exactly 1.0.
- Two scoring runs produce byte-identical CSV output.
- Refresh brief count equals refresh verdict count and impact estimates do not exceed current totals.
- Ledger line count equals inventory count, packet hashes verify, and no prune action is executed without Gate-D.
