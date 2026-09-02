---
name: iqrsqpi-v20
description: "RIG doctrine — IQRSQPI v20, the fractal self-verifying loop. Intent (executable done-tests + declared confidence) → Question (persona panel) ⇄ Research (until DRY) → Solution (BDD acceptance + slices) → Build (child slice runs, each with its own kill switch) → Quality (checks green, planted failure, cross-family verifier dispatched by the engine) → Proof (seal + calibration) → Integrate (handoff). Every gate is code. Successor of iqrsqpi-v11; use for any meaningful build, fix, migration or research deliverable."
when_to_use: "Say '/iqrsqpi', 'v20', 'run the loop', 'slice it', 'verify with another model', 'gated build', or start any work that must survive sessions and ship with proof. Use iqrsqpi-v11 for small single-context tasks, iqrsqpi-v10 for throwaway ideation."
version: 20.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: intent executed as proof, research proven dry, build sliced to context size, quality verified by another model family, calibration measured — with no stage advancing on a red halt-tier gate"
done_when:
  - "cmd:python3 bin/rig-loop test iqrsqpi-v20"
  - "cmd:python3 bin/rig-loop test iqrsqpi-v20-slice"
  - "file:capabilities/skills/iqrsqpi-v20/loop.yaml"
  - "grep:capabilities/skills/iqrsqpi-v20/loop.yaml:independent_verdict"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  design: docs/IQRSQPI-V20-DESIGN.md
  doctrine_source: "~/.claude/rules/rig-unified-doctrine.md §5; docs/IQRSQPI-V20-DESIGN.md"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill iqrsqpi-v20"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# IQRSQPI v20 — the fractal, self-verifying loop

v11 gave the gates to code. v20 closes the three loops v11 still trusted the agent with:
the **done-test written at Intent is executed** at Quality and Proof; **research runs until
DRY** (recorded pass by pass); the **independent verifier is dispatched by the engine** from a
different model family and its `VERDICT:` is parsed, not pasted. It also adopts the two
patterns the 2026 field converged on: the spec broken into **context-sized slices** run as
child loops, and a **handoff** so the loop survives sessions. Design and sources:
`docs/IQRSQPI-V20-DESIGN.md`.

```
I1 Intent ─► Q1 Question ⇄ R Research (DRY) ─► S Solution (spec + slices) ─► B Build (child slices)
   done-tests registered · confidence declared                                       │ all done
                                                                                     ▼
I2 Integrate (handoff) ◄─ P Proof (seal + calibration) ◄─ Q2 Quality (checks · planted · other-family VERDICT)
                                        ▲                          │ fail → closing loop → S (max 3) → escalate
```

## Step 0 — activate

```bash
rig-loop activate iqrsqpi-v20 --intent "<one sentence>"     # or: /iqrsqpi <intent>
rig-loop activate iqrsqpi-v20 --mode walk --intent "..."    # stop after each stage for Mike
rig-loop path                                                 # artifacts dir
```

## Stages — artifact · gate · command

| Stage | Artifact | Gate (code checks) | Advance |
|---|---|---|---|
| **I1 Intent** | `intent.md` | `## GOAL` `## METRIC` `## DONE-TEST` (≥1 `- cmd:` / `- file:` / `- grep:` — **registered as checks and executed later**) `## OUT-OF-SCOPE` `## COORDINATE` `## CONFIDENCE` (0–1, your probability the done-test passes first time); no TBD | `rig-loop stage I1 pass` |
| **Q1 Question** | `questions.md` | `## Panel` with ≥3 `- [lens:<persona>]`; `## Questions` lines tagged `[BLOCKING]` (must carry `-> ANSWER:`) or `[ASSUMED]` | `rig-loop stage Q1 pass` |
| **R Research** | `research.md` | `## Findings` `## Sources` (each `(HIGH\|MED\|LOW)`) `## Gaps`; **DRY**: ≥2 recorded passes and the last reported 0 new load-bearing unknowns | per pass `rig-loop qr pass --new-unknowns N`; `rig-loop stage R pass` |
| **S Solution** | `spec.md` | `## Approach` `## Acceptance` (Given/When/Then) `## Files` (scope fence) `## Slices` (`- <name> — done: <cmd>`, each fits one context) `## Det-vs-Prob` `## Test-plan` `## Rollback` | `rig-loop stage S pass` — code writes unlock |
| **B Build** | `build.md` | ≥1 slice run and **all slices done**; `## Slices-done` `## Changed` | `rig-loop slice start "<name>"` → child loop B→V→C (below) → `rig-loop stage B pass` |
| **Q2 Quality** | `quality.md` | files written (slices count); every check green **now** incl. done-tests; ≥1 planted failure (slices count); **independent verdict** from a family ≠ builder in PERFECT/VERIFIED/PARTIAL; drift ≤10 (degrade); `## Checks` `## Planted-failure` `## Verifier` | `rig-loop verify --family codex` (or claude/hermes/omp/prime-agent) then `rig-loop stage Q2 pass` |
| **P Proof** | `proof.json` | Q2 passed; sealed; calibration record written (predicted vs done-test outcome, Brier) | `rig-loop seal && rig-loop stage P pass` |
| **I2 Integrate** | `integrate.md` + `handoff.md` | `## Shipped` `## Not-shipped` `## Hand-offs` `## Next-slice`; handoff rendered | `rig-loop handoff [--to HANDOFF.md]`; `rig-loop stage I2 pass` |

### The slice loop (`iqrsqpi-v20-slice`)

`rig-loop slice start "<name>"` opens a child run that becomes the active run for the
directory; hooks enforce the slice until it closes, then the parent is active again.

| Stage | Artifact | Gate |
|---|---|---|
| B Build | `slice.md` | ≥1 file written; `## Slice` `## Changed` |
| V Verify | `verify.md` | registered checks green; ≥1 planted failure; `## Checks` `## Planted-failure` |
| C Commit | `commit.md` | `## Commit` with the sha (commit on green) |

Kill switch per slice: 3 iterations, 240 min, 300 tool calls. Parent: 3 iterations, 720 min,
800 tool calls, 12 children. A slice's planted failures and files roll up to the parent.

## Verifier dispatch (GEV as mechanism)

```bash
rig-loop verify --family codex            # builder claude → codex verifies
rig-loop verify --family claude           # builder codex/omp/prime → claude -p verifies
rig-loop verify --family hermes|omp|prime-agent
rig-loop verify --family codex --dry-run  # print the prompt the verifier receives
```

The engine builds the prompt from the artifacts and registered checks only (never the
builder's reasoning), runs the harness headless, saves the transcript beside the run, parses
`VERDICT:` and `GAPS:`, and refuses a family equal to the builder's. FAILED/FEEDBACK → fix →
`rig-loop stage Q2 fail` (closing loop) or re-verify.

## Calibration

`## CONFIDENCE` at I1 is the prediction; at seal the done-tests decide the outcome; the Brier
score lands in `~/.rig/state/loops/calibration.jsonl`. `rig-loop calibration [--loop iqrsqpi-v20]`
shows mean Brier and hit rate. Over-confident loops are a doctrine finding, not a footnote.

## What the engine enforces (precise)

Everything v11 enforces (halt gates block, degrade gates stamp DEGRADED, park is a pause,
closing loop discards iteration evidence, proof binding re-verified after P, every write path
checked, outward tripwire, `--run` cwd ownership) plus: done-tests executed at Q2/P; Q⇄R
dryness from recorded passes; ≥1 slice with all slices done before Q2; cross-family verdict
from dispatch; tool-call budget parks the run and denies the call; handoff required at I2.

## Honesty notes

- Dispatch proves a different family produced a verdict; it does not prove the verifier was competent. Objective checks stay primary.
- `qr pass --new-unknowns` and the panel are agent-written; the gate makes them explicit and auditable.
- Calibration is only as honest as the done-tests written at I1.
- Hermes: CLI-level gating only (gateway hooks cannot block or inject).
- `/ultraplan` remains the v11 conversational walker; `/iqrsqpi` is this engine-gated loop.
