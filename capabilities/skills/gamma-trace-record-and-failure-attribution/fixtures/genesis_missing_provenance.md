---
name: scheduler-migration-procedure
description: Planted genesis skill missing its gamma provenance — the done-test must refuse it.
status: draft
source: "gamma trace r-18 RED diagnosis, run 2026-09-02 (skill_missing_or_wrong)"
---

# scheduler-migration-procedure (planted: no gamma provenance)

This is the genesis failure the class exists to prevent: a plausible procedure
with no `gamma_provenance:` field, so no one can decide which failure it
closed, and therefore no one can ever decide to delete it. The validator must
exit 2 on this file even though `source:` is present — provenance to the
motivating gamma rows is the load-bearing field.
