---
id: ops-fleet-reliability-sweep
version: 1
status: draft
updated: 2026-09-24
task: Read-only fleet reliability sweep reporting only new breakage since the last report
category: ops-automation
domain: ops-automation
model_target: unspecified
score: null
license: first-party
source: claude: .claude/projects/-Users-rig128gb-Desktop-NeoMatrix/0cb40979-c01c-477f-9b40-5a3aaaceb72e.jsonl (fired 26x)
triggers: reliability sweep read-only report watchdog report fleet status new failures cron health
compose: agent/orca-omp-terminal-control.md projects/workstream-kanban.md
provenance: claude: .claude/projects/-Users-rig128gb-Desktop-NeoMatrix/0cb40979-c01c-477f-9b40-5a3aaaceb72e.jsonl (fired 26x) | standing read-only watchdog procedure
content_sha256: da0670f147e698138126c960ae50eff6c712b000d5cf10a33241b60c8efbb0d5
---

Read-only reliability sweep. Do NOT fix anything, only report.

1. Run: bash ~/.orca/ops/bin/fleet-health.sh
2. Read ~/.hermes/cron/jobs.json and count jobs by state (scheduled / paused / disabled) and by last_status.
3. Compare against the newest previous report in ~/.orca/ops/reports/watchdog-*.md if one exists.

Write ~/.orca/ops/reports/watchdog-$(date +%F-%H%M).md with:
- VERDICT line: STABLE / NEW-FAILURES / DEGRADED
- Only jobs whose last_status became error SINCE the previous report (new breakage). If no previous report exists, say "baseline run".
- Any endpoint that flipped UP to DOWN.
- Nothing else.

Rules: read-only. Never edit the git repo you run in. Never unpause, enable, disable, or run a Hermes cron job. Never restart a service. Report facts from files only; if a number is not in a file, say "unknown". Under 30 lines.
