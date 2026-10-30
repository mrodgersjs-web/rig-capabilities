# Authoritative Airtable tracker

Use base appjHReyFuIAyEZXI, table tbl450GyKwBLxGQvK, and review view viwQZBD5gESWLqp0I. The view is a presentation filter, never the dedupe universe. Read all pages of the full table with authorized access before admission or a submission reservation. Incomplete pagination, access failure, or ambiguous prior identity holds admission and submission.

[The mapping](../config/airtable-mapping.json) starts empty and unverified. Discover real schema and field types first; bind mappings to stable field IDs and a schema fingerprint with the actual read receipt. Map job key, employer, title, requisition, canonical URL, workflow state, last observation, artifact/approval/receipt references, and next action to existing compatible fields. If the table cannot represent required state, stop and report the exact gap. Do not auto-create fields, rename existing fields, or invent select options.

Preserve unrelated fields and existing records. Only the coordinator writes. Confirm supplied scope for tracker writes, use a mutation intent with target record and expected prior values, and retain real response plus subsequent readback. Detect stale/concurrent updates and reconcile before overwriting. A single local writer is not a distributed lock against outside editors.

Persist the intended stable job key before create. After timeout search the full table by stable identity and reconcile the original operation. Zero matches after incomplete reads proves nothing. Multiple matches remain a duplicate hold. No blind create retry. Track local pending operations until verified Airtable state matches; do not report successful sync from HTTP acceptance alone.

Do not put raw credentials, private transcripts, or unnecessary personal data in tracker fields. Store scoped artifact references and minimum state. Final status and totals derive from reconciled receipt evidence, not a scheduled target or a checkbox.
