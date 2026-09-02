---
name: scheduler-migration-procedure
description: Example genesis skill distilled from the r-18 gamma diagnosis — procedure for migrating legacy cron payloads to a new scheduler API without retrying schema errors.
status: draft
source: "gamma trace r-18 RED diagnosis, run 2026-09-02 (skill_missing_or_wrong)"
gamma_provenance: [g-18-1, g-18-2]
---

# scheduler-migration-procedure (genesis example)

Trigger: a scheduler API rejects a legacy payload with 422 and the believed
state says the API contract is unknown.

Body: (1) stop retrying — a schema 422 is deterministic; (2) fetch the API's
payload schema before any further call; (3) migrate one job as a probe and let
the checker accept the shape before migrating the rest.

Provenance law: this file exists only because rows g-18-1 and g-18-2 show an
empty delivery set against an unknown-contract state and a blanket-retry card
against a deterministic schema error. Delete the citation and this skill is
undeletable-by-evidence: a card nobody can trace is a card nobody can decide
to delete.
