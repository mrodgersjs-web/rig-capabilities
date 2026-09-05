---
name: great-hd-03-crm-hygiene-yaml
lane: revenue-gtm
exemplar_of: hD-03-crm-hygiene.yaml
description: "Reference exemplar — a Twenty CRM cleanup with pre-write backup, live schema snapshot, dry-run mutation lines, class-scoped approval, and detector-based post-verification."
---

# hD-03 CRM hygiene — stale opportunities and duplicates

## Input

Audit people, companies, and opportunities for exact-email duplicates, fuzzy name/domain duplicates, required-field gaps, opportunities inactive over 30 days, and orphaned owners. Only safe field completion is executable; merges and deletions remain blocked without class-specific approval.

## Output

`artifacts/crm/hygiene-2026-09/` contains object counts, scope, per-object backup plus checksums, schema snapshot, executable rollback instructions, four detector reports, `mutation_plan.jsonl` with before/after values, approval log, mutation audit, and post-verification residuals. Unapproved merge/delete plan lines are skipped and logged rather than executed.

## Acceptance

```console
$ curl -sf http://localhost:3000/healthz
# expected: exit 0 before inventory
$ python3 scripts/find_duplicates.py --crm http://localhost:3000 --out duplicates.json
# expected: exit 0 with exact and fuzzy candidates ranked by confidence
$ python3 scripts/dryrun_mutations.py artifacts/crm/hygiene-2026-09/mutation_plan.jsonl
# expected: exit 0; every operation has record id and before/after values
$ ./bin/rig-capabilities goal-spec --stem hD-03-crm-hygiene
# expected: verdict OK
```

Backup row counts equal the pre-run object inventory and every checksum verifies. Post-run detectors show defect count after is no greater than before, with reason codes for all residuals. Each executed operation maps by hash to one plan line; no destructive operation appears without `APPROVE hygiene-2026-09 <class>`.