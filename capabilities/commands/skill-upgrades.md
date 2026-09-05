---
name: skill-upgrades
description: Upgrade RIG skills/harnesses/loops/hooks via the rig-capabilities MCP — quality report, weakest assets, context pack for the target, apply with done-tests, verify.
argument-hint: "[<skill-id> | weakest | <task you're about to do>]"
allowed-tools: Read, Bash, Task
category: meta
outcome: "meta: continuously raise the quality bar of the RIG capability estate"
done_when:
  - "mcp:capabilities_quality_report"
  - cmd:./bin/rig-capabilities test iqrsqpi-v10
great_example: examples/great/meta/skill-upgrades.md
acl: public
quality_floor: 0.7
---

# /skill-upgrades

Drive the rig-capabilities MCP to find and raise the weakest capabilities.

1. **Report.** Call `capabilities_quality_report` (or `rig-capabilities quality
   --weakest 10`). Read the `weakest` list — each row has `id`, `kind`, `score`,
   `missing`, `has_done_test`.
2. **Pick.** If an argument names a skill id, target it. If the argument is
   `weakest`, take the top of the list. Otherwise treat the argument as the task
   you're about to do and call `capabilities_context_pack {intent: "<arg>"}` to
   pull the right assets first.
3. **Pack.** For the chosen asset, call
   `capabilities_context_pack {intent: "upgrade <id> — <its outcome>"}` to load
   its outcome lane, graph neighbours, and the lane's reference implementation.
4. **Upgrade.** Fill missing quality fields, tighten the description, add
   runnable `done_when` entries (`cmd:` / `file:` / `grep:` / `mcp:` forms).
   Never invent capability the asset does not have.
5. **Verify.** `rig-capabilities test <id>` — done_when must pass. Then
   `rig-capabilities quality` to confirm the score rose.
6. **Certify (optional).** `rig-capabilities certify <id> --apply` graduates
   Draft → Stable when done-tests are green, a great_example exists, and the
   plant-failure check goes red.

The MCP is loaded at session start; this command is the front door to it.
