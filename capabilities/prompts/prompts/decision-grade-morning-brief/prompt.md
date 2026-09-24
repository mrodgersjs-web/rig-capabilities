---
id: decision-grade-morning-brief
version: 1
status: draft
updated: 2026-09-24
task: Decision-grade morning brief sized for a phone, gathering read-only inputs before ranking decisions
category: planning-strategy
domain: planning-strategy
model_target: unspecified
score: null
license: first-party
source: mined corpus: candidates.jsonl line 4114 (codex-rollout) via omp task2 manifest
triggers: morning brief decision grade brief brief for today what needs deciding today phone length brief
compose: projects/workstream-kanban.md
provenance: mined corpus: candidates.jsonl line 4114 (codex-rollout) via omp task2 manifest | OMP task2 distillation, fired 10x across 2 stores
content_sha256: f7df741e9d3f5e9d697d950533c127f2fc5e224f71f2ddc00b004c261f8a8d17
---

Produce Mike a decision-grade morning brief. Be terse; he reads this on a phone.

Gather (read-only):
1. bash ~/.orca/ops/bin/fleet-health.sh
2. Newest files in ~/.orca/ops/reports/ from the last 24h.
3. For each repo in `orca repo list`, run `git -C <path> status --porcelain` and `git -C <path> log --oneline -3` to see uncommitted work and recent commits.

Write ~/.orca/ops/reports/brief-$(date +%F).md with exactly these sections:
## Needs you today       (max 3 bullets, each an action Mike must personally take, or "nothing")
## Broken               (anything RED/DOWN/EXPIRED, with the one command that fixes it)
## Quota watch          (any provider above 80%, and how long until reset)
## Work in flight       (repos with uncommitted changes, one line each)

Rules: no filler, no praise, no summaries of what you did. Every claim must come from a command you actually ran. If a section is empty write "nothing". Never modify the repo. Under 35 lines total.

MANDATORY RECEIPT. As your final action, append exactly one JSON line to /Users/rig128gb/.rig/automation-receipts/receipts.jsonl (this append is the only file write you may perform): {"lane":"<LANE-ID>","run":"completed","at":"<current UTC time, ISO 8601 with Z>","artifact":"<path of your primary output file, or the state field you verified>","note":"<result in under 120 chars>"}. A run with no receipt counts as failed.
