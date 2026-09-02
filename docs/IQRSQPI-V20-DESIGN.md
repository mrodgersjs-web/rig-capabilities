# IQRSQPI v20 — design

Date: 2026-09-01 · Owner: Mike Rodgers · Builder: Claude (Jake) · Engine: `rig-loop` (Loop-Skill Contract v11)

## Why a v20

v11 made the seven stages a code-gated state machine. It still trusts the agent for three
things the estate keeps getting burned by: the done-test written at Intent is never executed,
"research until dry" is a counter the agent bumps, and the independent verifier is a sentence
in `quality.md`. v20 closes those three loops with mechanism, and adds the two patterns the
2026 field converged on: the spec as the unit of work broken into context-sized slices, and a
fresh-context handoff so the loop survives sessions.

## What was scraped (sources)

| Pattern | Source | Taken into v20 as |
|---|---|---|
| Initializer + coding agent; `feature_list.json` with `passes:false`; `claude-progress.txt`; `init.sh`; "feature list prevents premature victory" | [Anthropic — Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | slices with done-tests (`## Slices` in spec.md), `rig-loop handoff`, session-start resume banner |
| Fresh context per iteration; only git + progress + PRD status persist; max-iterations kill switch; story sized to one context window | [snarktank/ralph](https://github.com/snarktank/ralph), [ghuntley.com/loop](https://ghuntley.com/loop/) | child slice runs with their own kill switch; `max_tool_calls`; one slice = one context |
| constitution → specify → clarify → plan → tasks → implement → converge; repeat tasks/implement until Converged | [github/spec-kit](https://github.com/github/spec-kit) | Q⇄R dryness gate (`qr_dry`), `## Slices` as tasks, B stage converges when every child run is done |
| Deltas against current behaviour in brownfield; ~4 files per change; specs and code in separate zones | [OpenSpec vs Spec Kit — Hashrocket](https://hashrocket.com/blog/posts/openspec-vs-spec-kit-choosing-the-right-ai-driven-development-workflow-for-your-team), local `platform/openspec-bdd` | spec.md carries `## Acceptance` (Given/When/Then) and `## Files`; write policy stays `artifacts_only` until S |
| Builder-validator chain: validator sees the contract, never the builder's reasoning; +15.6% task success with an objective-level verification step (MAST) | [MindStudio — Verifier pattern](https://www.mindstudio.ai/blog/verifier-pattern-multi-agent-systems-independent-review), [Augment — Adversarial code review](https://www.augmentcode.com/guides/adversarial-code-review) | `rig-loop verify --family <other>` spawns a headless verifier of a different family with the artifacts only; Q2 gate `independent_verdict` |
| Model-as-judge is the hardened exception; objective checks preferred (22% lean on judge) | [arXiv 2607.00038 — engineering the loops](https://arxiv.org/pdf/2607.00038) | done-tests from intent.md are registered as checks and executed at Q2/P; the verdict is one gate among deterministic ones |
| Four-phase Analysis → Planning → Solutioning → Implementation; scale-adaptive planning | [BMAD workflow map](https://docs.bmad-method.org/reference/workflow-map/) | modes `auto` / `walk`; slices scale with the spec |
| Evidence before claims; 11 failure modes ("writer does not approve", "validation is a system", "compact is not memory") | local `superpowers:verification-before-completion`, `~/.rig/agent-doctrine/CODING_AGENT_11_FAILURE_MODES.md` | proof binding re-verified after P; handoff instead of compaction; GEV separation enforced by dispatch |
| Calibration-v2 energy gates; Brier-style eval | local `~/.claude/rules/jake.md`, RIG unified doctrine §4 | `## CONFIDENCE` at I1, actual at seal, Brier ledger `~/.rig/state/loops/calibration.jsonl` |

## The v20 loop

```
I1 Intent ─► Q1 Question ⇄ R Research (until DRY) ─► S Solution (spec + slices)
   │ done-tests registered                                   │
   │ confidence declared                                     ▼
   │                                              B Build = child slice runs (B→V→C each)
   │                                                         │ all children done
   │                                                         ▼
   │                            Q2 Quality: checks green · planted failure · independent verdict (other family)
   │                                                         │
   └──────────── done-tests executed at ─────────────► P Proof (seal, calibration record)
                                                             │
                                                             ▼
                                                  I2 Integrate (handoff.md, Gate-D on outward)
   closing loop: B / Q2 / P fail ─► S, max 3 ─► escalate
```

### Stage contract (engine-enforced)

| Stage | Artifact | New in v20 |
|---|---|---|
| I1 | `intent.md` | `## CONFIDENCE 0.xx` required; every `- cmd:/file:/grep:` DONE-TEST line is registered as a check tagged `done_test` |
| Q1 | `questions.md` | `## Panel` with ≥3 `- [lens:…]` lines (persona panel) |
| R | `research.md` | sources graded `(HIGH|MED|LOW)`; gate `qr_dry`: ≥2 recorded Q⇄R passes and the last pass reported 0 new load-bearing unknowns (`rig-loop qr pass --new-unknowns N`) |
| S | `spec.md` | `## Acceptance` with Given/When/Then; `## Slices` ordered list, each `- <name> — done: <cmd>` |
| **B** | `build.md` | gate `children_done`: ≥1 child `iqrsqpi-v20-slice` run and all children `done`; `rig-loop slice start "<name>"` opens one (B→V→C, own kill switch); the child is the active run for the cwd until it closes |
| Q2 | `quality.md` | gate `independent_verdict`: ≥1 verification from a family ≠ builder with verdict PERFECT/VERIFIED/PARTIAL, produced by `rig-loop verify --family codex|claude|hermes|omp|prime-agent` (headless dispatch, `VERDICT:` parsed, output saved) |
| P | `proof.json` | seal runs every check including done-tests; calibration record predicted vs actual (Brier) appended |
| I2 | `integrate.md` + `handoff.md` | `rig-loop handoff` renders the structured HANDOFF from run state |

### Kill switch v20

`max_iterations 3` · `max_wall_minutes 720` · `max_stop_blocks 2` · `max_tool_calls 800` (pre-tool hook counts; park + deny past the budget) · `max_children 12`. Slice runs: `max_iterations 3`, `max_wall_minutes 240`, `max_tool_calls 300`.

### Surfaces

- Skill dirs `iqrsqpi-v20` and `iqrsqpi-v20-slice` in all five harness skill roots (Claude `hooks:` frontmatter auto-activates on first write).
- Slash command `/iqrsqpi` (canonical `~/.rig/universal-slash-commands/commands/iqrsqpi.md` → Claude, Codex, Hermes, `.agents` via `rig-slash sync`; OMP reads the Claude commands dir; Prime via `rig-capabilities install iqrsqpi.md --harness prime-agent`). `$ARGUMENTS` is the intent.
- `/ultraplan` stays the v11 conversational walker (anti-unification: `/iqrsqpi` is engine-gated).

## Honesty

- The verifier dispatch proves a *different family produced a verdict*; it cannot prove the verifier was competent. Objective checks remain primary gates.
- `qr pass --new-unknowns` is agent-reported; the dryness gate makes the report explicit and auditable, not true.
- Calibration is only as good as the done-tests written at I1.
- Hermes: CLI-level gating only.
