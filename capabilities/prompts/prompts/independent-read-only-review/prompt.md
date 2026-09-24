---
id: independent-read-only-review
version: 1
status: draft
updated: 2026-09-24
task: Independent read-only review of a landed fix: bugs, security, violations, run the check, no source writes
category: code
domain: code
model_target: unspecified
score: null
license: first-party
source: mined corpus: candidates.jsonl line 4347 (codex-rollout) via omp task2 manifest
triggers: independent review read-only review always recheck review this fix pass with exact evidence
compose: when-shipping-code
provenance: mined corpus: candidates.jsonl line 4347 (codex-rollout) via omp task2 manifest | OMP task2 distillation, verbatim
content_sha256: 85057e42cf30817794f5921daadf9bbf3d394a989114adb1d5dc07bdec4c178a
---

Independent read-only review requested. Main fixed scripts/repair_skill_hierarchy.py to retain explicit Source markdown paths across repeated plan/apply; added 2 tests (18 total). Current canonical repair reapplied. Review current code/test bug/security/regression; run canonical --check. Do not write sources. Return concerns or pass with exact evidence. Next distribution 15 when-* across runtime skill roots + managed startup blocks, separate live verification.
