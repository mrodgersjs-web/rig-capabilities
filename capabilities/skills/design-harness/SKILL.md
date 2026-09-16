---
name: design-harness
description: "RIG doctrine as a loop-skill — Design Harness. "
version: 11.0.0
outcome: "agent-engineering: Design Harness enforced as a gated loop with hooks"
done_when:
  - "cmd:python3 bin/rig-loop test design-harness"
  - "file:capabilities/skills/design-harness/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.7
metadata:
  loop_skill: v11
  doctrine_source: "/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/harness/"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill design-harness"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# Design Harness — loop-skill (v11 contract)

Source doctrine: `/Users/rig128gb/Developer/rig-intelligence/packages/rig-design-harness/harness/`

## Step 0 — activate (every harness)

```bash
rig-loop activate design-harness --intent "<one sentence>"
```

## Stages

- **I1 Intent** — write `intent.md` with `## GOAL` and executable `## DONE-TEST`; run the canonical package workflow from studio through independent verify.
- **P Proof** — bind the canonical `bin/rdh seal` result in `proof.json`; a D85 refusal keeps the loop open.

## Closing loop / kill switch

See loop.yaml. Escalate to Mike when the closing loop is exhausted.
