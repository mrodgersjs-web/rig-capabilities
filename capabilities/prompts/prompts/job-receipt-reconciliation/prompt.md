---
id: job-receipt-reconciliation
version: 1
status: draft
updated: 2026-09-24
task: Read-only application receipt reconciliation in a bounded window, sqlite readonly only
category: job-search
domain: job-search
model_target: unspecified
score: null
license: first-party
source: mined corpus: candidates.jsonl line 927 (aside) via omp task2 manifest
triggers: reconcile application receipts new application evidence check submissions read only receipt check application ledger audit
compose: when-running-the-job-search
provenance: mined corpus: candidates.jsonl line 927 (aside) via omp task2 manifest | OMP task2 distillation, datetimes and ids slotted
content_sha256: e48d6d31c9af707e7db3c1555971ffb24fa743d34b96ad5920fee950a2e24ec5
---

READ-ONLY job-application receipt reconciliation. Do NOT write to any file, database, memory, or setting. Do NOT send anything. Use only `sqlite3 -readonly`, read_file/code-mode reads, and at most ONE browse read if strictly needed.

GOAL: determine whether any new evidence arrived between <WINDOW-START> MDT and now (<WINDOW-END> MDT) that changes application outcomes.

Check exactly these, and report FOUND / ABSENT for each with the observation path:

1. Canonical ledger drift: `sqlite3 -readonly /Users/rig128gb/.applypilot/applications.sqlite3`. Report: total row count; rows whose `updated_at >= '<DATE>'`; rows with `ats_submitted_at >= '<DATE>'`; rows with any of warm_sent_at/hm_sent_at/recruiter_sent_at >= '<DATE>'; full `lifecycle_logs` count and any row created >= '<DATE>'. Report exact numbers, not interpretations.
2. The Held pilot application: row `<HELD-APP-ID>` — report stage, ats_submitted_at, ats_receipt_ref, gmail_status, and the last 300 chars of `notes`. It was HELD and not submitted as of <DATE>.
3. The two protected no-retry records: `<APP-ID-1>` and `<APP-ID-2>` — report stage and whether any new field became non-null. Do not recommend retry.
4. New daily discovery feed: list directories under `/Users/rig128gb/.applypilot/imports/` newest first and report whether a `<DATE>` folder exists. If it does, read its `WAVE-supply.json` and report ONLY: generated_at, unique, with_stated_range, posting_open, from_ats_api. Do NOT dump jobs.
5. Any job-application-related new file created since <WINDOW-START> MDT anywhere under `/Users/rig128gb/.applypilot/` (use `find /Users/rig128gb/.applypilot -newermt '<WINDOW-START-DATETIME>' -type f` but EXCLUDE the venv symlink target and any *.lock, *.db-wal, *.db-shm). Report paths and mtimes, or ABSENT.
6. `/Users/rig128gb/.aside/u/0/memory/routines/<ROUTINE-ID>/MEMORY.md` — confirm it exists and report its byte size and mtime.
7. Do NOT open Gmail, do not open LinkedIn, do not open employer portals. Mail reconciliation is out of scope for this subagent because a signed-in session is required and this task must stay read-only and cheap.

HONESTY RULES: report ABSENT with the exact command output when empty. A zero is a valid answer; do not pad. Never describe a generic acknowledgment as a requisition match. Do not infer a submission from a stage label.

OUTPUT: short structured text, sections 1-7, each with FOUND/ABSENT + exact numbers/paths + observation timestamp.
