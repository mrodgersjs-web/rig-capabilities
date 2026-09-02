---
name: git-push-safety-loop
description: "RIG doctrine — Gate-P (git push safety) as a code-enforced loop. Before any git push: record repo visibility, what the push would overwrite (deliberate teaser?), the public-leak test, Mike's typed approval, then push and prove remote == HEAD by command, then a secret sweep. The pre-tool hook denies `git push` until approval is on the run."
when_to_use: "Any git push, force-push, or PR merge to a remote. Say 'push', 'publish the branch', 'force push', 'sync to github'."
version: 11.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: zero private-source or teaser-overwrite pushes to public repos; every push proven remote == HEAD and secret-swept"
done_when:
  - "cmd:python3 bin/rig-loop test git-push-safety-loop"
  - "file:capabilities/skills/git-push-safety-loop/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  doctrine_source: "~/.claude/rules/git-push-safety.md; RIG-Doctrine-Repo/doctrines/GIT-PUSH-SAFETY.md"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill git-push-safety-loop"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# Git push safety loop (Gate-P)

```
V Visibility → D Divergence → L Leak-test → A Approve (typed) → X Push (remote==HEAD by cmd) → S Sweep → P Proof
                                    │ STOP → park for Mike           │ mismatch → back to V (max 2)
```

## Step 0

```bash
rig-loop activate git-push-safety-loop --intent "push <branch> to <owner>/<repo>"
```

## Stages

| Stage | Artifact | Gate | Command |
|---|---|---|---|
| **V Visibility** | `visibility.md` | `## Repo`, `## Visibility` PUBLIC/PRIVATE (`gh repo view --json visibility`), `## Remote`, `## Branch` | `rig-loop stage V pass` |
| **D Divergence** | `divergence.md` | `## Overwrite` (`git log --oneline HEAD..<remote>/<branch>`), `## Deliberate-teaser` yes/no | `rig-loop stage D pass` |
| **L Leak-test** | `leak.md` | `## Private-source-to-public` yes/no, `## Verdict` PROCEED — STOP means park and present the fork to Mike | `rig-loop stage L pass` or `rig-loop park --reason "GATE-P STOP: …"` |
| **A Approve** | `approval.md` | typed approval on the run | `rig-loop gate-d request --action "push …"`; Mike: `rig-loop gate-d approve --phrase "APPROVE <run_id>"`; `rig-loop stage A pass` |
| **X Push** | `push.md` | `## Command`, `## Remote-equals-HEAD`; engine runs `git fetch && HEAD == @{u}` in the run's cwd | push, `rig-loop stage X pass` |
| **S Sweep** | `sweep.md` | `## Secret-sweep` (secret-scanning alerts + history filename/content sweep), `## Result` clean/rotated | `rig-loop stage S pass` |
| **P Proof** | `proof.json` | sealed | `rig-loop seal && rig-loop stage P pass` |

## The three laws

- **L1 pre-push public-leak guard** — V/D/L must be written before A can even be requested; PUBLIC + (teaser or leak) = STOP.
- **L2 canonical-remote routing** — `## Remote` names the exact remote; X proves `remote == HEAD` with a command, never a claim.
- **L3 post-public secret sweep** — S is mandatory on every push through this loop.

## Honesty notes

- The X gate runs `git` in the run's cwd; activate the loop inside the repository.
- `--force` pushes still need the same loop; the engine does not distinguish them — you must, in D.
