---
id: nightly-memory-consolidation
version: 1
status: draft
updated: 2026-09-24
task: Nightly Memory OS consolidation: set the memory budget, run consolidation, record what changed
category: ops-automation
domain: ops-automation
model_target: unspecified
score: null
license: first-party
source: mined corpus: candidates.jsonl line 6676 (claude) via omp task2 manifest
triggers: nightly memory consolidation consolidate memories memory budget memory os maintenance run the consolidation
compose: agent/orca-omp-terminal-control.md
provenance: mined corpus: candidates.jsonl line 6676 (claude) via omp task2 manifest | OMP task2 distillation, fired 8x
content_sha256: 1bf4d438eef5b7938abc8877be37d0a490df687d7a466f5f48a1b9bd78083354
---

Nightly memory consolidation for the RIG memory OS.

1. ~/.rig/orca/bin/rig-memory budget --set 1.0     (probing burns the write budget; restore it)
2. ~/.rig/orca/bin/rig-memory status
3. Read todays reports in ~/.orca/ops/reports/ and ~/.rig/orca/v100/*/PROOF.md if present.
4. For each DURABLE lesson - something a future session would be worse off not knowing - call:
   ~/.rig/orca/bin/rig-memory record --kind lesson --text "<specific claim>"
   Record claims, not activity summaries. "<SPECIFIC-CLAIM>" is a claim. "<ACTIVITY-SUMMARY>" is not. Maximum 5 records.
5. Write ~/.orca/ops/reports/memory-$(date +%F).md listing what you recorded and each receipt_id.

Rules: read-only except the memory records and that one report. No git commits. If a record returns accepted:false, report the reject_reason - do not retry blindly. Under 25 lines.
