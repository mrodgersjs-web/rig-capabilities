---
name: great-hC-01-design-system-audit-yaml
lane: security-review
exemplar_of: hC-01-design-system-audit.yaml
description: Reference exemplar for an evidence-led design-system audit covering inventory, token debt, variant states, accessibility, bundle weight, and ranked remediation.
---

# hC-01-design-system-audit.yaml — great example

## Input

Audit a component library against its existing `DESIGN.md` and token source. The scope includes every component, story, and consumer, plus raw color/spacing literals, near duplicates, interaction-state coverage, documentation, accessibility, and bundle impact. The session records a goal card before collecting evidence.

## Output

`artifacts/ds-audit/` contains the sorted component inventory, raw-literal report, duplicate scan, state-gap matrix, accessibility JSON, bundle snapshot, severity-ranked report, deprecation map, and dependency-ordered remediation plan. Every finding points to an inventory line, scan record, or file diff.

```console
$ npx jscpd src/components --min-tokens 50 --reporters json --output artifacts/ds-audit/jscpd
# expected: JSON report records duplicates at the declared threshold

$ npx axe http://localhost:6006 --save artifacts/ds-audit/axe.json
# expected: scan artifact exists and impact-level counts appear in the report

$ npx source-map-explorer dist/*.js --json > artifacts/ds-audit/bundle.json
# expected: bundle JSON parses and total component-library KB is recorded
```

## Acceptance

- Inventory accounts for every component, story, and consumer; token coverage is calculated from actual literals and references.
- Interactive components are checked for default, hover, active, focus, disabled, loading, and error states.
- Naming and docs gaps are dispositioned; each deprecation names a migration target and consumer count.
- The final report has severity, owner, evidence pointer, effort, and dependency order for every remediation item.
