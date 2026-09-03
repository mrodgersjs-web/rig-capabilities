---
name: gate-d-loop
description: "RIG doctrine — Gate-D as a code-enforced loop. Wrap any outward or irreversible action (send, publish, deploy, push, merge, spend, credential change, destructive cleanup, private-data export) in classify → dormant → request → typed approval → execute → proof. The pre-tool hook denies the outward shell command until `APPROVE <run_id>` is recorded."
when_to_use: "Before any git push, PR merge, deploy, email/DM/post send, ad spend, credential rotation, rm of real data, or data export. Say 'gate-d', 'arm', 'ship it', 'push', 'send', 'deploy'."
version: 11.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: no outward or irreversible action executes without a dormant stage, a recorded request, and Mike's typed approval on the run"
done_when:
  - "cmd:python3 bin/rig-loop test gate-d-loop"
  - "file:capabilities/skills/gate-d-loop/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  doctrine_source: "~/.claude/rules/rig-unified-doctrine.md §10; RIG-Doctrine-Repo/doctrines/GATE-D.md"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill gate-d-loop"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# Gate-D loop

**No Mike approval, no public action.** This loop makes that a mechanism instead
of a sentence: the outward command is denied by code until the typed phrase is on
the run, and the action cannot be called done without proof of what was seen.

```
C Classify → D Dormant → R Request → A Approve (typed) → X Execute → P Proof
                 ▲                                          │ fail → back to D (max 2) → escalate
                 └──────────────────────────────────────────┘
```

## Step 0

```bash
rig-loop activate gate-d-loop --intent "push loop-skills-v11 to mrodgersjs-web/rig-capabilities"
```

## Stages

| Stage | Artifact | Gate | Command |
|---|---|---|---|
| **C Classify** | `classify.md` | `## Action`, `## Class` (send/publish/deploy/push/merge/spend/credential/destructive/export/dns), `## Blast-radius`, `## Rollback` | `rig-loop stage C pass` |
| **D Dormant** | `dormant.md` | `## Staged` (paths), `## Zero-outbound-proof` with the command + output proving nothing went out (sent=0, dry-run, staged) | `rig-loop stage D pass` |
| **R Request** | `request.md` | `## Request`, `## Exact-target`, `## Reversible`; a Gate-D request recorded on the run | `rig-loop gate-d request --action "..."` then `rig-loop stage R pass` |
| **A Approve** | `approval.md` | typed approval on the run | Mike: `rig-loop gate-d approve --phrase "APPROVE <run_id>"` then `rig-loop stage A pass` |
| **X Execute** | `execute.md` | `## Command`, `## Output`, `## Verified-as-seen` (browser screenshot, provider UI, remote==HEAD) | run the action, `rig-loop stage X pass` |
| **P Proof** | `proof.json` | sealed ProofPacket | `rig-loop seal && rig-loop stage P pass` |

Until **A** passes, the pre-tool hook denies `git push`, `gh pr merge`, deploys,
sends, spend, `launchctl` changes and non-local `curl -X POST`. Everything you
build before that must be dormant and provably so.

## Honesty notes

- The engine records who typed the phrase and when; it cannot prove the typing hand was Mike's. Mike's direct current-task instruction is scoped approval; the phrase is how it lands on the run.
- Public-repo pushes also run `git-push-safety-loop` (Gate-P) — same run family, extra checks.
- Closing loop is short (2): a failed execute goes back to Dormant; a second failure escalates.
