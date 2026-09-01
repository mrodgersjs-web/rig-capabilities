---
name: capabilities-round
description: Run a 1000x improvement round in one capability lane — weakest canonicals first, deterministic contract upgrades, applied only when done-tests stay green.
argument-hint: "[<lane> [n]] [dry]"
allowed-tools: Read, Bash, Task
category: meta
outcome: "meta: every round raises the lane's weakest contract without breaking a green"
done_when:
  - file:capabilities/commands/capabilities-round.md
  - file:examples/great/meta/capabilities-round.md
  - grep:capabilities/commands/capabilities-round.md:Never fabricate a round score
great_example: examples/great/meta/capabilities-round.md
quality_floor: 0.7
---

# capabilities-round

1. Parse args: lane (default = the lane with the lowest mean trust), n (default 3), and `dry` if the word appears.
2. Call the `capabilities_round` MCP tool with `{lane, n, dry}`. Dry prints the plan; apply writes only what passes.
3. Every accepted upgrade must show: old done_when, new done_when, and the green done-test run that justified it.
4. If any candidate fails its done-tests, it stays untouched — a round never converts red to silent.
5. After apply, call `capabilities_quality_report` and quote the movement on the assets touched.

Never fabricate a round score. If n assets were skipped for missing evidence, say so.
