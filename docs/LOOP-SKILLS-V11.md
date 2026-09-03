# Loop-Skill Contract v11

Date: 2026-09-01 · Owner: Mike Rodgers · Engine: `bin/rig-loop` (`rig_capabilities/loops.py`, stdlib)

## Why

Doctrine that lives as prose is loaded as context and enforced by nothing. The RIG estate
had ~30 always-on rules and ~60 doctrine files, all advisory. This contract turns a doctrine
into a **loop-skill**: a skill directory whose loop is machine-readable, whose gates are
decided by code, and whose hooks fire in every harness the moment the skill is in use.

```
capabilities/skills/<id>/
  SKILL.md         narrative + quality contract + Claude `hooks:` frontmatter
  loop.yaml        the loop: stages, gates, closing loop, kill switch, outward policy
  tests/cases.json planted-failure cases (non-vacuity) run by `rig-loop test <id>`
```

## The contract

1. **One artifact per stage.** Each stage names a file. The agent writes it; code reads it.
2. **Deterministic gates.** `rig-loop stage <id> pass` evaluates the stage's gates and
   refuses while any non-`degrade` gate is red. Gate types: `file_exists`, `file_contains`,
   `regex`, `regex_absent`, `no_unanswered_blocking`, `min_counter`, `checks_green`
   (re-runs registered commands now), `planted_failure` (red exit≠0 then green exit=0),
   `sealed`, `gate_d_requested`, `gate_d_approved`, `cmd`, `stage_passed`, `drift_within`,
   `files_written_min`. Gate errors are RED (fail-closed).
3. **Refuse-to-advance.** A stage can only be marked when every prior stage is `pass`/`park`.
4. **Closing loop.** `closing_loop.from` stages that `fail` reopen `closing_loop.to`, bump the
   iteration, and after `kill_switch.max_iterations` the run becomes `escalated` (hooks stop
   enforcing; the agent reports the red gates to Mike).
5. **Kill switch.** `max_wall_minutes` parks the run from the prompt hook; `max_stop_blocks`
   caps how many times the Stop hook may refuse "done" before yielding with a NOT-DONE banner.
6. **Write policy per stage.** `artifacts_only` denies Write/Edit and shell redirects outside
   plan/spec/scratch paths; `declared` allows writes and records scope drift against the
   spec's `## Files`; `open` allows.
7. **Outward policy.** `git push`, PR merge, deploys, sends, spend, `launchctl`, non-local
   `curl -X POST` are denied by the pre-tool hook until a typed `APPROVE <run_id>` is on the run.
8. **Seal.** `rig-loop seal` writes a `rig.proofpacket.v1` packet to `~/.rig/proof/` with
   artifact hashes, check results, planted failures, files written, drift, Gate-D record and
   history, and hash-binds it to the run.
9. **Non-vacuity.** Every loop-skill ships `tests/cases.json`; `rig-loop test <id>` runs the
   cases in a throwaway state root and must show each gate going RED and then GREEN.
10. **No active run, no cost.** Every hook is a silent no-op unless a run is active for the
    working directory (or a parent). A hook in an unrelated directory never attaches to
    another directory's run.

## Runtime

- State: `~/.rig/state/loops/{active.json, runs/<run_id>/{run.json, events.jsonl, artifacts/}}`
  (override `RIG_LOOP_STATE`; proofs `RIG_LOOP_PROOF_DIR`).
- Hooks: `rig-loop hook <session-start|prompt|pre-tool|post-tool|stop> --format claude|codex|pi|text`
  reads one JSON payload on stdin. Claude/Codex: deny = `hookSpecificOutput.permissionDecision`
  JSON + exit 2; stop-block = stderr + exit 2; inject = stdout. pi: `{block, reason, inject}`.
- Modes: `auto` (code gates; humans at blocking questions and Gate-D) and `walk`
  (`stop_after_stage`: stop after each stage pass for Mike's confirmation).

## Harness wiring (`rig-loop wire --apply`, backups, managed marker `RIG_LOOP_MANAGED`)

| Harness | Skills root | Hook surface | Can block | Can inject |
|---|---|---|---|---|
| Claude Code | `~/.claude/skills` | settings hooks (SessionStart, UserPromptSubmit, PreToolUse, Stop) + per-skill `hooks:` frontmatter that auto-activates the loop on first write | yes | yes |
| Codex | `~/.codex/skills` | Claude-compatible hooks manifest (needs hook trust on next start) | yes | yes |
| OMP (pi) | `~/.omp/agent/skills` (+ `includeSkills` allowlist entry) | `~/.omp/agent/extensions/rig-loop-hooks.ts` — `tool_call` blocks, `before_agent_start` injects | yes | yes |
| Prime Agent (pi) | `~/.prime/agent/skills` | `~/.prime/agent/extensions/rig-loop-hooks.ts` | yes | yes |
| Hermes | `~/.hermes/skills` (registers `/<id>`) | `~/.hermes/hooks/rig-loop-gate` (gateway only, telemetry) | **no** | **no** — CLI-level: `rig-loop stage … pass` still refuses red gates |

## Loop-skills in this wave

| id | spine | replaces / encodes |
|---|---|---|
| `iqrsqpi-v20` (`/iqrsqpi`) | I1 Q1⇄R S B Q2 P I2 | v20: done-tests executed, Q⇄R dryness, slices as child runs, cross-family verifier dispatch, calibration, handoff — `docs/IQRSQPI-V20-DESIGN.md` |
| `iqrsqpi-v20-slice` | B V C | one context-sized slice (child of v20) |
| `iqrsqpi-v11` | I1 Q1 R S Q2 P I2 | IQRSQPI (unified doctrine §5, IQRSQPI-ENGINEERING); v10 stays the single-pass sibling |
| `gate-d-loop` | C D R A X P | Gate-D (§10, GATE-D.md) |
| `proof-loop` | C E N V P | Honest Completion + Proof-or-it-didn't-happen |
| `adversarial-verification-loop` | G R N K P | Adversarial Verification / build doctrine rule 3 |
| `north-star-lock-loop` | L D S C P | North-Star doctrine + North-Star Lock + Anchor |
| `phase-discipline-loop` | O B V T C P | Phase Discipline / build doctrine rule 7 |
| `git-push-safety-loop` | V D L A X S P | Gate-P (git-push-safety) |

Remaining doctrines convert with `rig-loop scaffold <id> --name … --source <doctrine.md>`
then fill stages/gates/cases (see BACKLOG in `docs/ROADMAP.md`).

## Enforcement semantics (precise)

- `halt` gates block a pass; `degrade` gates never block but are stamped `DEGRADED` into the
  stage note, history and ProofPacket. Say "no stage advances on a red halt-tier gate".
- `park` is a pause: a parked stage is still unmet after `resume`.
- A closing-loop iteration clears planted failures, the seal and check results.
- After P passes, every later stage re-verifies proof binding (packet hash, iteration, every
  recorded artifact byte-identical); a stale proof reopens P.
- Write checks cover every path a call touches (single field, `edits[]`, `files[]`,
  apply_patch envelopes) and fail closed when a write-class tool declares no path.
- The outward guard is a regex tripwire tolerant of git/gh global options; it is not a sandbox.
- An explicit `--run` must own the caller's cwd.

Independent verification: commit 3a87acc was reviewed adversarially by a Codex verifier; its
seven findings drove the semantics above and are covered by regression cases in
`capabilities/skills/iqrsqpi-v11/tests/cases.json` and `tests/test_loops.py`.

## Honesty

- The engine cannot prove a human typed the Gate-D phrase; it records who/when/phrase.
- Counters like `qr_passes` and `drift_checks` are agent-reported; artifacts are what gates read.
- Hermes CLI sessions get no hook enforcement; the CLI gate is the only mechanism there.
- `--force` on `stage pass` is allowed for emergencies and is stamped FORCED in history and proof.
