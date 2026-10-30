---
name: traject-dedupe-checker
description: "SUB-AGENT: CODE-gate dedupe — checks employer+role+req against ~/.applypilot/applications.sqlite3 and Gmail receipts, deduping Gmail by message id across offset-paginated pages. A duplicate returns its receipt id; no classifier needed. Parent: traject-apply-operator."
allowed-tools: Bash Read Grep Glob
owner: rig-intelligence
domain: business-ops / application dedupe
status: Stable
verified_by: jake
verified_on: 2026-09-28
acl: internal
relates_to: traject-apply-operator, traject-target-qualify, traject-os
outcome: "dedupe: a clean/dupe verdict per role with the receipt id, deduped by message id across Gmail pages so a repeated page is never double-counted"
done_when:
  - file:capabilities/agents/traject-dedupe-checker.md
  - grep:capabilities/agents/traject-dedupe-checker.md:message id
quality_floor: 0.8
---

# traject-dedupe-checker

Parent: `traject-apply-operator`. Sub-skill: `traject-target-qualify`. This is a **CODE gate**
(deterministic, no classifier). Harness: `traject-apply-one-role`.

## Procedure

1. Look up employer+role+req in `~/.applypilot/applications.sqlite3`; a row (applied/receipt) is a
   duplicate — return its receipt id.
2. Search Gmail receipts, deduping by **message id** across offset-paginated pages (TL-06: Gmail
   offset pagination repeats the same page). Verify the count against the source of truth; a
   suspiciously small total is re-measured by a second method before reporting.
3. Return clean (proceed) or dupe (drop with the receipt id).

## Output shape

```json
{"role": "<company>-<role>", "verdict": "clean|dupe", "receipt_id": "…|null", "pages_seen": 3, "unique_messages": 5}
```
