---
name: phase-discipline-loop
description: "RIG doctrine — Phase Discipline as a code-enforced loop. Order phases by dependency (reversible vs one-way), build one coherent phase, adversarial-verify it, verify the real tree, commit on green, seal. Never advance on red; a red verify loops back to build (max 3)."
when_to_use: "Multi-phase builds, migrations, refactors, anything with dependency order. Say 'phase', 'build in order', 'commit on green', 'one coherent change at a time'."
version: 11.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: builds land as ordered, verified, committed-on-green phases with a decision log"
done_when:
  - "cmd:python3 bin/rig-loop test phase-discipline-loop"
  - "file:capabilities/skills/phase-discipline-loop/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  doctrine_source: "RIG-Doctrine-Repo/doctrines/PHASE-DISCIPLINE.md; ~/.claude/rules/rig-build-doctrine.md rule 7"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill phase-discipline-loop"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# Phase discipline loop

```
O Order → B Build → V Verify → T Tree → C Commit → P Proof
             ▲         │ red       │ mismatch
             └─────────┴───────────┘  (max 3 → escalate)
```

Run one loop per phase. The next phase's `O` cites the previous phase's ProofPacket.

## Step 0

```bash
rig-loop activate phase-discipline-loop --intent "phase 2: schema -> API"
```

## Stages

| Stage | Artifact | Gate | Command |
|---|---|---|---|
| **O Order** | `phases.md` | `## Phases` in dependency order, `## Dependencies`, `## Reversibility` tagging each phase reversible/one-way; code writes denied until this passes | `rig-loop stage O pass` |
| **B Build** | `build.md` | ≥1 file written this run; `## Phase`, `## Changed` | `rig-loop stage B pass` |
| **V Verify** | `verify.md` | registered checks green now + ≥1 planted failure; `## Checks`, `## Planted-failure` | `rig-loop check add "…"`, `rig-loop plant …`, `rig-loop stage V pass` |
| **T Tree** | `tree.md` | `## Tree-verified` with the real-tree command and output (`git diff --stat`, `git status`, sha256) | `rig-loop stage T pass` |
| **C Commit** | `commit.md` | `## Commit` sha, `## Decision-log` (each decision with reversibility); HEAD resolvable (degrade) | commit, `rig-loop stage C pass` |
| **P Proof** | `proof.json` | sealed | `rig-loop seal && rig-loop stage P pass` |

## Rules encoded

- Dependency order and one-way-door tagging before the first edit (O gate).
- Small coherent commits: one loop = one phase = one commit.
- Adversarial verification is inside V (planted failure required).
- "Verify the real tree" is T: the report is not evidence; the tree is.
- Commit only on green: C cannot pass before V and T.

## Honesty notes

- The engine cannot tell one phase from two; keep `## Changed` honest and small.
- `git push` after commit is still Gate-D (denied by the pre-tool hook until approved).
