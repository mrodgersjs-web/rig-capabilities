---
name: iqrsqpi-v11
description: "RIG doctrine — IQRSQPI v11, the gated loop. Intent → Question → Research → Solution → Quality → Proof → Integrate as a code-enforced state machine: one artifact per stage, deterministic gates, refuse-to-advance, Builder→Verifier closing loop (max 3), kill switch, Gate-D on outward actions, sealed ProofPacket. Use for any meaningful build, fix, migration, or research deliverable. Sister of iqrsqpi-v10 (single-pass fast lane)."
when_to_use: "Say 'run iqrsqpi', 'gated loop', 'safe lane', 'v11', 'walk me through the stages', or start any build that should not ship on vibes. Prefer v10 only for throwaway ideation."
version: 11.0.0
owner: rig-intelligence
domain: Agent engineering / operating doctrine
status: Stable
verified_by: jake
verified_on: 2026-09-01
outcome: "agent-engineering: IQRSQPI enforced as a gated loop — no stage advances on a red gate, no done without a sealed ProofPacket"
done_when:
  - "cmd:python3 bin/rig-loop test iqrsqpi-v11"
  - "file:capabilities/skills/iqrsqpi-v11/loop.yaml"
  - "grep:capabilities/skills/iqrsqpi-v11/loop.yaml:closing_loop"
great_example: examples/great/agent-engineering/iqrsqpi-v11.md
quality_floor: 0.8
metadata:
  loop_skill: v11
  engine: rig-loop
  doctrine_source: "~/.claude/rules/rig-unified-doctrine.md §5; RIG-Doctrine-Repo/doctrines/IQRSQPI-ENGINEERING.md"
hooks:
  PreToolUse:
    - matcher: "Write|Edit|MultiEdit|NotebookEdit|Bash"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook pre-tool --format claude --skill iqrsqpi-v11"
          timeout: 20
  Stop:
    - matcher: "*"
      hooks:
        - type: command
          command: "python3 ~/Developer/rig-capabilities/bin/rig-loop hook stop --format claude"
          timeout: 20
---

# IQRSQPI v11 — the gated loop

v10 emits a whole plan in one turn and trusts the agent with the gates. **v11 gives
the gates to code.** Every stage has one artifact and a deterministic gate; the
`rig-loop` engine refuses `stage X pass` while any gate is red, refuses to skip a
stage, runs the Builder→Verifier closing loop when Quality or Proof fails, and
blocks "done" until a ProofPacket is sealed. Hooks fire on every prompt, tool
call and stop in Claude, Codex, OMP and Prime; in Hermes the CLI is the gate.

```
I1 Intent → Q1 Question ⇄ R Research (≥2 passes) → S Solution → Q2 Quality → P Proof → I2 Integrate
                                                        ▲            │  fail → closing loop (max 3) → escalate
                                                        └────────────┘
```

## Step 0 — activate (every harness, first thing)

```bash
rig-loop activate iqrsqpi-v11 --intent "<one sentence>"        # mode auto (default)
rig-loop activate iqrsqpi-v11 --mode walk --intent "..."        # interactive walker: stop after each stage for Mike
rig-loop path                                                    # where stage artifacts live
```

In Claude Code the frontmatter hooks also auto-activate the loop on your first
write if you forgot. Until stage **S** passes, the hooks deny code writes (Write/
Edit and shell redirects) outside plan/spec paths — write the stage artifact instead.

## The seven stages — artifact · gate · command

| Stage | Artifact (in `rig-loop path`) | Gate (code checks this) | Advance |
|---|---|---|---|
| **I1 Intent** | `intent.md` | headings `## GOAL` `## METRIC` `## DONE-TEST` `## OUT-OF-SCOPE` `## COORDINATE`; DONE-TEST has ≥1 executable line (`- cmd:` / `- file:` / `- grep:` / `- mcp:`); no TBD/TODO | `rig-loop stage I1 pass` |
| **Q1 Question** | `questions.md` | `## Questions`; every line tagged `[BLOCKING]` or `[ASSUMED]`; no BLOCKING line without `-> ANSWER:` (park and ask Mike if one stays open) | `rig-loop stage Q1 pass` |
| **R Research** | `research.md` | `## Findings` `## Sources` (≥1 source — no source, no number) `## Gaps`; counter `qr_passes ≥ 2` | `rig-loop counter qr_passes --inc` per Q⇄R pass, then `rig-loop stage R pass` |
| **S Solution** | `spec.md` | `## Approach` `## Files` (paths/globs you will touch — becomes the scope fence) `## Det-vs-Prob` (AUTO/DRAFT/FLAG) `## Test-plan` `## Rollback` | `rig-loop stage S pass` — code writes unlock here |
| **Q2 Quality** | `quality.md` | ≥1 file written; every registered check green **now**; ≥1 planted failure proven RED→GREEN; drift ≤10 (degrade); `## Checks` `## Planted-failure` `## Verifier` naming an independent verifier family | `rig-loop check add "<cmd>"` · `rig-loop plant "<name>" --red "<cmd>" --green "<cmd>"` · `rig-loop stage Q2 pass` |
| **P Proof** | `proof.json` (copy of the sealed ProofPacket) | Q2 passed; `rig-loop seal` succeeded and the packet hash still matches | `rig-loop seal && rig-loop stage P pass` |
| **I2 Integrate** | `integrate.md` | `## Shipped` `## Not-shipped` `## Hand-offs` `## Next-slice`; outward actions (push/deploy/send/spend) blocked until Gate-D | `rig-loop stage I2 pass` → run **done** |

Artifact paths can be bound elsewhere (e.g. the repo's `docs/plans/`):
`rig-loop artifact S docs/plans/2026-09-01-feature.md`.

## Closing loop (TAC tactic 5, built in)

`rig-loop stage Q2 fail` or `stage P fail` reopens **S** and bumps the iteration.
Iteration 4 does not exist: the run becomes `escalated`, the hooks stop enforcing,
and you report to Mike with the red gates. Builder and Verifier must be different
model families — name the verifier in `quality.md`.

## Kill switch

- `max_iterations: 3` closing-loop passes, then escalate.
- `max_wall_minutes: 480` — the prompt hook parks the run after 8h.
- `max_stop_blocks: 2` — the Stop hook refuses "done" twice, then yields with a
  NOT-DONE banner so an agent can never be trapped. Park honestly instead:
  `rig-loop park --reason "..."`; resume later with `rig-loop resume <run_id>`.

## Gate-D (outward actions)

Any stage: `git push`, `gh pr merge`, deploys, sends, spend, `launchctl` changes
are denied by the pre-tool hook until Mike's typed approval is on the run:

```bash
rig-loop gate-d request --action "push loop-skills-v11 to private origin"
rig-loop gate-d approve --phrase "APPROVE <run_id>"      # Mike types this, exact phrase
```

The engine records who/when/phrase in the ProofPacket. It cannot prove a human
typed it — that is Mike's discipline, stated honestly.

## What the hooks inject

- **prompt** — one banner: run id, stage n/7, iteration, gate-d state, next gate, the exact command to advance.
- **pre-tool** — deny with the artifact you should be writing instead.
- **stop** — NOT-DONE with the red gate, twice; then a yield banner.
- **session-start** — resume banner if a run is active for this directory.

## Modes

- `auto` — code gates decide; humans only at I1 (open BLOCKING) and I2 (Gate-D).
- `walk` — after each stage pass the Stop hook lets you stop; Mike confirms before the next stage.

## Anti-unification

- v10 = single-pass plan (fast lane). v11 = code-gated loop (safe lane). Different jobs.
- The production-studio IQRSQPI (`rig-iqrsqpi`: Intake/Synthesize/Quantify/Produce/Iterate) is the same spine for creative briefs; v11 uses the canonical I1/Q1/R/S/Q2/P/I2 codes from the RIG lattice.
- v11 does not replace goal harnesses (hA/hB/…); a harness can name `iqrsqpi-v11` as its spine.

## What the engine actually enforces (verified adversarially, 2026-09-01)

- **Halt-tier gates block; degrade-tier gates do not.** A stage passes only when every
  halt-tier gate is green. A red `degrade` gate (Q2's drift ceiling) lets the stage pass but
  stamps `DEGRADED: …` into the stage note, the history and the ProofPacket.
- **Park is a pause, not a skip.** `stage X park` then `resume` leaves X unmet.
- **Closing loop discards iteration evidence.** A fail from Q2/P reopens S and clears planted
  failures, the seal, and check results; the new iteration must re-prove and re-seal.
- **Proof binding is re-verified after P.** Every stage after P (and the final pass) checks the
  packet still exists, hash-matches, is from this iteration, and that every artifact it recorded
  is byte-identical; otherwise P is reopened and you must re-seal.
- **Every path a write touches is checked**, including MultiEdit `edits[]` and `apply_patch`
  envelopes; a write-class call with no determinable path is denied before S (fail-closed).
- **The outward guard is pattern-based, not a sandbox.** It tolerates git/gh global options
  (`git -C dir push`, `git -c k=v push`) but a determined agent can evade any regex; the guard
  is a tripwire, Gate-D is the doctrine.
- **`--run` never crosses directories.** A hook told to use a specific run still has to be in
  that run's directory tree.

## Honesty notes

- Hermes gateway hooks cannot block or inject; there the loop is enforced only by `rig-loop stage … pass` refusing red gates.
- `qr_passes` is agent-reported; the artifacts are what the gate reads.
- `--force` on `stage pass` exists for emergencies and is recorded as **FORCED** in history and the ProofPacket.
- Shell writes are caught by redirect/`tee`/`sed -i` heuristics only; Python or editor writes inside a shell command are not seen.
