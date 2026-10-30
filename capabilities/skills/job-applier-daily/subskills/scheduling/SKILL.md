---
name: job-daily-scheduling
description: Define bounded daily scheduling and recovery without enabling an unverified runtime.
metadata:
  version: 1.3.0
---

# Scheduling

## Inputs
Disabled daily profile, explicit user-selected first/last run dates and timezone/start/window and known scheduler owner.

## Actions
Validate first_run_date <= last_run_date, named timezone and local calendar behavior. Require explicit arming scope, verified owner/worker and real restart/overlap tests. Use SKIP overlap and at most the latest missed run within 24 hours. Enforce 90-minute/350-call limits, at most three workers, one coordinator ledger writer, and active-lineage cap.

## Outputs
Validated disabled configuration or actual authorized scheduler receipt plus bounded run/recovery evidence.

## Gates
Configuration/installation is not activation. No inferred timezone/window, catchup quota, duplicate daemon, unlimited human wait, or quota override of approval.

## Recovery
Persist each job independently of daily coordinator closure. Resume same checkpoints after restart; stop dispatch on exhausted budget and report handoff.

## Required skills and contracts
[Daily profile](../../config/daily-profile.json) and [inherited Temporal contract](../../../job-applier/references/temporal-daily-workflow.md).
