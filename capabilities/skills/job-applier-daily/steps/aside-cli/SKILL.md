---
name: job-daily-aside-cli
description: Delegate one bounded browser step from Grokbot to the actual installed Aside CLI, with explicit ownership and readback.
metadata:
  version: 1.4.0
---

# Aside CLI worker

## Inputs
One logical step, exact target, account/host/profile selected by the operator, verified model/provider, source/checkpoint paths and hashes, remaining attempt budget, and approved action scope.

## Actions
Read [Aside CLI commands and limits](../../references/aside-cli.md). Grokbot is the caller and conductor; `aside exec` is the actual browser-agent worker. Discover the destination CLI with `--help` and `guide`; never use bare `aside help`, which is a task prompt. Check single ownership and token budget before dispatch. Start a separate owned session for one step, record its returned ID, and require durable artifact paths/hashes and a bounded checkpoint. Read back those files and verify the target and current hashes before advancement.

## Outputs
CLI version/help evidence, selected account/host/profile/model, owner record, exact step prompt hash, session ID, full private run log, bounded result, artifact/checkpoint hashes, attempt history and outcome status.

## Gates
Use at most 8,000 source-pack tokens and 1,500 displayed characters per ordinary tool output. Preserve complete local originals. No active user-tab attachment, frontmost-window automation, account switch, profile mutation, routine activation or unspecified external action. An isolated conversation does not prove isolated browser tabs. Hold when owned browser resources cannot be established. No fictitious `aside run`, session-read API, JSON flag, native token flag or model availability claim.

## Recovery
Inspect existing session and durable receipts after timeout or disconnect. Never redispatch an uncertain operation. Context-limit failures require reconciliation and a fresh owned session for the same logical step; carry attempts and `submission_unknown` forward. A missing CLI, authenticated account, safe browser workspace, model/provider or readback remains a named hold.

## Required skills and contracts
[Meta-skill](../../SKILL.md), [execution contract](../../references/execution-contract.md), [JEV decision](../jev-decision/SKILL.md) and [JEV image](../jev-image/SKILL.md). Each first-five resume needs individual exact-version review; each submission needs separate exact-packet approval.
