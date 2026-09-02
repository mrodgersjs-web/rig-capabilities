---
name: iqrsqpi
category: agent-engineering
acl: public
description: IQRSQPI v20 — the engine-gated loop (Intent → Question ⇄ Research → Solution → Build slices → Quality → Proof → Integrate). Activates a rig-loop run for this directory; every stage is a code-checked gate, the verifier is dispatched from another model family, and "done" needs a sealed ProofPacket. Argument = the intent. Global in Claude, Codex, Hermes, OMP and Prime Agent.
argument-hint: "<intent in one sentence> [--mode walk]"
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Agent
outcome: "agent-engineering: /iqrsqpi runs the v20 engine-gated loop in every harness"
done_when:
  - "file:capabilities/commands/iqrsqpi.md"
  - "grep:capabilities/commands/iqrsqpi.md:RIG_LOOP_IQRSQPI_V20_COMMAND"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
---

# /iqrsqpi — IQRSQPI v20 (engine-gated)

You are running IQRSQPI v20 under the `rig-loop` engine. The engine decides every gate from
files and exit codes; your job is to produce the stage artifact, then ask the engine to advance.
Full contract: `~/Developer/rig-capabilities/capabilities/skills/iqrsqpi-v20/SKILL.md`.

## SENTINEL: RIG_LOOP_IQRSQPI_V20_COMMAND — DO NOT REMOVE

## 0. Activate (do this first, verbatim)

```bash
rig-loop activate iqrsqpi-v20 --intent "$ARGUMENTS"
rig-loop path
```

If `$ARGUMENTS` contains `--mode walk`, activate with `--mode walk` and stop after every stage
pass for Mike's confirmation. If a run is already active here, `rig-loop status` and continue it.

## 1. Walk the stages — write the artifact, then `rig-loop stage <id> pass`

- **I1** `intent.md`: `## GOAL` (outcome, Mike's words) · `## METRIC` (buyer/outcome terms) ·
  `## DONE-TEST` (executable `- cmd:` / `- file:` / `- grep:` lines — they will be run at Q2/P) ·
  `## OUT-OF-SCOPE` · `## COORDINATE` (L-D-A) · `## CONFIDENCE` (0–1).
- **Q1** `questions.md`: `## Panel` (≥3 `- [lens:…]` personas) · `## Questions` (`[BLOCKING] … -> ANSWER:` or `[ASSUMED] … (assumption: …)`). Park and ask Mike if a BLOCKING stays open.
- **R** `research.md`: `## Findings` · `## Sources` (each graded HIGH/MED/LOW) · `## Gaps`. After each Q⇄R pass: `rig-loop qr pass --new-unknowns N`. Loop until N = 0 (≥2 passes).
- **S** `spec.md`: `## Approach` · `## Acceptance` (Given/When/Then) · `## Files` (globs) · `## Slices` (`- name — done: <cmd>`) · `## Det-vs-Prob` (AUTO/DRAFT/FLAG) · `## Test-plan` · `## Rollback`. Code writes unlock after S.
- **B** for each slice: `rig-loop slice start "<name>"` → write code → `slice.md` → `rig-loop stage B pass` → `rig-loop check add "<test>"` → `rig-loop plant "<defect>" --red "<cmd>" --green "<cmd>"` → `verify.md` → `rig-loop stage V pass` → commit → `commit.md` → `rig-loop stage C pass`. Then `build.md` (`## Slices-done` `## Changed`) → `rig-loop stage B pass`.
- **Q2** `quality.md` (`## Checks` `## Planted-failure` `## Verifier`) → `rig-loop verify --family <not yours: codex|claude|hermes|omp|prime-agent>` → `rig-loop stage Q2 pass`. A FAILED/FEEDBACK verdict: fix, then re-verify or `rig-loop stage Q2 fail`.
- **P** `rig-loop seal && rig-loop stage P pass`.
- **I2** `integrate.md` (`## Shipped` `## Not-shipped` `## Hand-offs` `## Next-slice`) → `rig-loop handoff --to HANDOFF.md` → `rig-loop stage I2 pass`. Outward actions (push/deploy/send) need Mike's `rig-loop gate-d approve --phrase "APPROVE <run_id>"`.

## 2. Rules the engine will enforce on you

No code before S. No stage skip. No pass on a red halt-tier gate. Closing loop on Q2/P failure
(max 3, then escalate). Stop refused twice while a stage is unmet, then a NOT-DONE banner.
Tool-call budget 800 (slice 300). Park honestly with `rig-loop park --reason "…"`; resume with
`rig-loop resume <run_id>`.

## Anti-unification

`/iqrsqpi` (v20, engine-gated) ≠ `/ultraplan` (v11 conversational walker) ≠ `/ultraplan-v10`
(single pass). Pick by job: v20 for anything that must survive sessions and ship with proof.
