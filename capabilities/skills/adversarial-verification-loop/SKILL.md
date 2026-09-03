---
name: adversarial-verification-loop
description: "RIG doctrine — Adversarial Verification (non-vacuity) as a code-enforced loop. For every gate you trust: name it → plant a defect and prove the gate goes RED → restore and prove GREEN → keep the planted failure as a regression fixture → seal. A green that won't go red is theater."
when_to_use: "After adding any test, gate, hook, guard, or checker; before trusting a 'green'. Say 'plant a failure', 'red-team the gate', 'non-vacuity', 'does this test actually test anything'."
version: 11.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: every trusted gate is proven able to go RED, then GREEN, with the planted failure kept as a fixture"
done_when:
  - "cmd:python3 bin/rig-loop test adversarial-verification-loop"
  - "file:capabilities/skills/adversarial-verification-loop/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  doctrine_source: "RIG-Doctrine-Repo/doctrines/ADVERSARIAL-VERIFICATION.md; ~/.claude/rules/rig-build-doctrine.md rule 3"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill adversarial-verification-loop"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# Adversarial verification loop

```
G Guard → R Red (plant, expect FAIL) → N Green (restore, expect PASS) → K Keep fixture → P Proof
   ▲            │ red did not fail          │ green did not pass
   └────────────┴───────────────────────────┘  (max 3 → escalate: the gate is theater)
```

## Step 0

```bash
rig-loop activate adversarial-verification-loop --intent "prove <gate> is non-vacuous"
```

## Stages

| Stage | Artifact | Gate | Command |
|---|---|---|---|
| **G Guard** | `guard.md` | `## Gate-under-test`, `## What-it-guards`, `## Green-command` with `- cmd:<shell>` | `rig-loop stage G pass` |
| **R Red** | `red.md` | a planted failure recorded whose red command exited ≠0; `## Planted-defect`, `## Red-output` | `rig-loop plant "<defect>" --red "<cmd with defect planted>" --green "<cmd restored>"` then `rig-loop stage R pass` |
| **N Green** | `green.md` | registered checks green now; `## Restored`, `## Green-output` | `rig-loop check add "<green cmd>"` then `rig-loop stage N pass` |
| **K Keep** | `fixture.md` | `## Regression-fixture` with `- file:<test path>` or `- cmd:<test cmd>` | `rig-loop stage K pass` |
| **P Proof** | `proof.json` | sealed | `rig-loop seal && rig-loop stage P pass` |

## Why the engine, not the prose

`rig-loop plant` runs both commands itself and records the exit codes. If the
"red" command exits 0 the plant is recorded as `red_ok: false` and stage R stays
red — the gate you trusted does not catch the defect. That is the finding; report
it, fix the gate, loop.

## Honesty notes

- Plant a real defect in the code or data the gate guards, not a `false` command.
- Keep the fixture in the repo's test suite; the K gate only checks you named where.
