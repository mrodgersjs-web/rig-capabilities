---
name: skill-upgrades
description: Upgrade RIG skills/harnesses/loops/hooks via the rig-capabilities MCP. Hermes exposes this as /skill-upgrades. Runs the quality report, packs the target, applies the upgrade, and verifies with done-tests.
owner: rig-intelligence
domain: Meta capability engineering
status: Stable
verified_by: jake
verified_on: 2026-08-31
outcome: "meta: continuously raise the quality bar of the RIG capability estate"
done_when:
  - "mcp:capabilities_quality_report"
  - "grep:capabilities/skills/skill-upgrades/SKILL.md:capabilities_context_pack"
great_example: examples/great/meta/skill-upgrades.md
quality_floor: 0.7
---

# skill-upgrades

The Hermes-facing twin of the `/skill-upgrades` command. Hermes registers every
installed skill as `/<skill-name>`, so installing this skill yields
`/skill-upgrades` in Hermes without touching the (inert) commands dir.

## Flow

1. `capabilities_quality_report` → read `weakest`.
2. Pick the target (arg = id | `weakest` | a task description).
3. `capabilities_context_pack {intent: "upgrade <id>"}` → load lane + reference.
4. Fill missing quality fields, tighten description, add runnable `done_when`.
5. `rig-capabilities test <id>` → done_when green.
6. `rig-capabilities quality` → confirm score rose.

Never claim capability the asset lacks. Done = the target's done_when passes.
