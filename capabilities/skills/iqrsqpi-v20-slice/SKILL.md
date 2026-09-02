---
name: iqrsqpi-v20-slice
description: "RIG doctrine — the child loop of IQRSQPI v20: one context-sized slice, Build → Verify (checks green + planted failure) → Commit on green, with its own kill switch. Opened by `rig-loop slice start` from an active iqrsqpi-v20 run; usable standalone for a bounded fix."
when_to_use: "Inside an iqrsqpi-v20 Build stage, or for any bounded single-slice change that must end in a verified commit. Say 'slice', 'one slice', 'build this slice'."
version: 20.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: every slice ends in a verified, planted-failure-proven, committed change or an honest park"
done_when:
  - "cmd:python3 bin/rig-loop test iqrsqpi-v20-slice"
  - "file:capabilities/skills/iqrsqpi-v20-slice/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  parent: iqrsqpi-v20
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill iqrsqpi-v20-slice"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# IQRSQPI v20 slice

One slice fits one context window (the Ralph/Anthropic long-running-agent rule). The slice
is a three-stage loop with its own kill switch (3 iterations, 240 min, 300 tool calls).

```bash
rig-loop slice start "<name>"        # from an active iqrsqpi-v20 run (child becomes active)
rig-loop activate iqrsqpi-v20-slice --intent "<bounded fix>"   # standalone
```

| Stage | Artifact | Gate | Command |
|---|---|---|---|
| **B Build** | `slice.md` | ≥1 file written; `## Slice` `## Changed` | `rig-loop stage B pass` |
| **V Verify** | `verify.md` | registered checks green now; ≥1 planted failure RED→GREEN; `## Checks` `## Planted-failure` | `rig-loop check add "<cmd>"`, `rig-loop plant …`, `rig-loop stage V pass` (red → `stage V fail`, back to B) |
| **C Commit** | `commit.md` | `## Commit` with the sha | commit, `rig-loop stage C pass` → run done, parent active again |

Outward actions (push, deploy, send) are still denied without Gate-D. A slice's planted
failures and written files roll up to the parent's Quality gate.
