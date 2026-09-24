---
id: worktree-unit-spec-packet
version: 1
status: draft
updated: 2026-09-24
task: Parallel worker packet: isolated worktree, read the spec in full, run tests and paste real output, commit
category: code
domain: code
model_target: unspecified
score: null
license: first-party
source: mined corpus: candidates.jsonl line 6562 (codex-history) via omp task2 manifest
triggers: worktree worker prompt isolated track handoff assign track builder spec in full sealed unit of work
compose: when-shipping-code
provenance: mined corpus: candidates.jsonl line 6562 (codex-history) via omp task2 manifest | OMP task2 distillation, slotted worker/team/path names
content_sha256: 8224e08786c366a86e6269a556388765fedb05d47e62a8dd9e06076baef5ba25
---

## Identity

- Name: <WORKER-NAME>
- ID: <WORKER-ID>
- Type: general-purpose
- Team: <TEAM>
- Leader: leader

## Workspace
- Working directory: <WORKSPACE>
- Branch: clawteam/<TEAM>/<WORKER-NAME>
- This is an isolated git worktree. Your changes do not affect the main branch.

## Task

Read <SPEC-PATH> IN FULL and execute it completely in this Hermes worktree. You are building Track 1 — the A1 anti-fake-green done-gate (the most important component: deterministic decision, NO LLM in the gate path, fail-closed). Ground the real APIs first (agent/verification_evidence.py ledger, agent/verification_stop.py, agent/conversation_loop.py seam ~4658, the 3 deviator hooks). Build agent/done_contract.py, wire it additively+flag-guarded, write tests/test_done_gate.py with plant-failure-FIRST non-vacuity (each layer must go RED on a planted failure), RUN pytest yourself, paste the REAL output. Do NOT fake green. When truly done: clawteam task update <TEAM> <task-id> --status completed; clawteam inbox send <TEAM> leader 'T1 done: files=... pytest=...'.

## Coordination Protocol

- Use `clawteam task list <TEAM> --owner <WORKER-NAME>` to see your tasks.
- Starting a task: `clawteam task update <TEAM> <task-id> --status in_progress`
- Before marking a task completed, commit your changes in this repository with git.
- Use a clear commit message, e.g. `git add -A && git commit -m "Implement <task summary>"`.
- Finishing a task: `clawteam task update <TEAM> <task-id> --status completed`
- When you finish all tasks, send a summary to the leader:
  `clawteam inbox send <TEAM> leader "All tasks completed. <brief summary>"`
- If you are blocked or need help, message the leader:
  `clawteam inbox send <TEAM> leader "Need help: <description>"`
- After finishing work, report your costs: `clawteam cost report <TEAM> --input-tokens <N> --output-tokens <N> --cost-cents <N>`
- Before finishing, save your session: `clawteam session save <TEAM> --session-id <id>`
