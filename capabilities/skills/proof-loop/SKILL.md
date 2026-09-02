---
name: proof-loop
description: "RIG doctrine — Honest Completion + Proof-or-it-didn't-happen as a code-enforced loop. Turn a claim of 'done' into: executable done-test → checks green now → planted failure proven RED→GREEN → independent verifier verdict → sealed ProofPacket. The Stop hook refuses 'done' until the packet is sealed."
when_to_use: "Whenever you are about to say done, verified, shipped, fixed, or green. Say 'prove it', 'proof packet', 'honest completion', 'seal'."
version: 11.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: fake-completion escape rate = 0 — no done without command evidence, a planted failure, an independent verdict, and a sealed packet"
done_when:
  - "cmd:python3 bin/rig-loop test proof-loop"
  - "file:capabilities/skills/proof-loop/loop.yaml"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  doctrine_source: "~/.claude/rules/honest-completion-doctrine.md; RIG-Doctrine-Repo/doctrines/PROOF-OR-IT-DIDNT-HAPPEN.md"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill proof-loop"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# Proof loop

**Done is proven, never claimed.** The decision is made by code from real
evidence: `rig-loop stage E pass` re-runs every registered check right now;
`stage N pass` needs a planted failure that went RED and then GREEN; `stage V pass`
needs a verdict from a verifier that is not the builder; `seal` hash-binds it all.

```
C Claim → E Evidence → N Non-vacuity → V Verify → P Proof
   ▲          │ fail          │ fail        │ FAILED/FEEDBACK
   └──────────┴───────────────┴─────────────┘   (max 3 → escalate)
```

## Step 0

```bash
rig-loop activate proof-loop --intent "prove: <the claim>"
```

## Stages

| Stage | Artifact | Gate | Command |
|---|---|---|---|
| **C Claim** | `claim.md` | `## Claim`, `## Done-test` with executable lines (`- cmd:` `- file:` `- grep:`), `## Artifacts`; `cmd:true`/`cmd:echo` refused as vacuous | `rig-loop stage C pass` |
| **E Evidence** | `evidence.md` | ≥1 registered check, all green when re-run **now**; `## Commands`, `## Output` | `rig-loop check add "pytest -q"` … `rig-loop stage E pass` |
| **N Non-vacuity** | `planted.md` | ≥1 planted failure with red exit≠0 and green exit=0; `## Planted-defect`, `## Red`, `## Green` | `rig-loop plant "name" --red "<cmd that must fail>" --green "<cmd that must pass>"` |
| **V Verify** | `verify.md` | `## Verifier` naming a different family/model/agent, `## Verdict` ∈ PERFECT/VERIFIED/PARTIAL, `## Gaps` | `rig-loop stage V pass`; FAILED/FEEDBACK → `rig-loop stage V fail` (closing loop) |
| **P Proof** | `proof.json` | sealed | `rig-loop seal && rig-loop stage P pass` |

## Rules encoded

1. **A1 decides** — the gate reads exit codes and files, not the agent's sentence.
2. **Verify the artifact, not the report** — checks run at gate time, not from a pasted log.
3. **Non-vacuity** — a green that won't go red is theater; N stage enforces it.
4. **GEV separation** — V stage requires a named independent verifier.
5. **Fail-closed** — any gate error is RED.
6. **Fail loud** — the Stop hook says NOT DONE with the red gate, twice, then yields with the same words.
7. **Define done before building** — C stage refuses a vacuous done-test.

## Honesty notes

- The verifier's independence is recorded, not proven; name the real agent/model you used.
- Use this loop standalone to seal existing work; inside IQRSQPI v11 the same checks run at Q2/P.
