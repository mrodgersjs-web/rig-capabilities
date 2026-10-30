---
name: job-daily-schema-mapping
description: Map the actual Airtable schema to required tracker semantics without altering it.
metadata:
  version: 1.3.0
---

# Schema mapping

## Inputs
Authorized schema read, exact base/table/view IDs and empty or prior field mapping.

## Actions
Verify table and view membership. Inspect every field ID/type and select choices. Map required semantics to existing compatible fields. Save schema fingerprint/read receipt and mapping revision. Re-read schema after drift or write type errors.

## Outputs
Verified mapping or explicit missing/ambiguous-field report.

## Gates
Never auto-create fields/options or coerce unknown statuses. schema_verified true requires real schema evidence, not configuration editing alone.

## Recovery
Leave existing mapping history intact; hold writes until drift is reconciled.

## Required skills and contracts
[Airtable contract](../../references/airtable-contract.md) and [mapping](../../config/airtable-mapping.json).
