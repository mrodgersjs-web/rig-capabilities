---
id: secret-scan-memory-probe
version: 1
status: draft
updated: 2026-09-24
task: Scan memory for secrets and report presence without ever printing values
category: verification-probe
domain: verification-probe
model_target: unspecified
score: null
license: first-party
source: mined corpus: candidates.jsonl line 316 (aside) via omp task2 manifest
triggers: scan memory for secrets credentials in memory sensitive values check memory secret audit api keys check
compose: agent/prompt-injection-and-probes.md
provenance: mined corpus: candidates.jsonl line 316 (aside) via omp task2 manifest | OMP task2 distillation, verbatim
content_sha256: e0da961a15b660d998ce4d1616374fc08182a3596823e2f8550866286acaf593
---

Try to use memory_search to search for: API key OR password OR secret OR credential. Report how many results and whether any contain sensitive-looking values.
