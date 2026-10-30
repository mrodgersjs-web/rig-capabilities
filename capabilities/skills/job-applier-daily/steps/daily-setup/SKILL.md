---
name: job-daily-daily-setup
description: Check daily dependencies, schedule scope and bounded execution before job discovery.
metadata:
  version: 1.3.0
---

# Daily setup

## Inputs
Disabled profile, current user scope, host adapter inventory, source Word selection, tracker mapping.

## Actions
Load the profile. Verify adapters and actual current access without claiming configuration is proof. Inventory existing schedule ownership; validate timezone, start time and window. Keep disabled until current schedule scope and real scheduler tests exist.

## Outputs
Preflight report, source hash, dependency states, bounded run ID and explicit missing requirements.

## Gates
No arming with enabled false, missing schedule values, unknown owner or unverified adapter. No outreach.

## Recovery
Preserve preflight and fix only authorized local configuration. Do not restart services or fabricate credentials.

## Required skills and contracts
[Meta-skill](../../SKILL.md) and [execution contract](../../references/execution-contract.md).
[Scheduling subskill](../../subskills/scheduling/SKILL.md).
