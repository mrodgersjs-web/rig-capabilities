# Determinism 85 Doctrine

Status: **TARGET CONTRACT — BLOCKED / NOT ENFORCED**

Source contract: `/Users/rig128gb/Desktop/Projects/rig-lattice-live/D85_AGENT_PROCESS_CONTRACT.json`

This doctrine defines the admission rules. It does not claim the compiler, hooks, authenticated approval service, or four-surface wiring exist.

## 1. Invariant

Every production process must prove all four ratios at or above `0.85`:

- aggregate unweighted
- aggregate weighted
- minimum reachable root-to-terminal path unweighted
- minimum reachable root-to-terminal path weighted

Critical controls must be `100% CODE` regardless of aggregate ratios. Critical controls include scheduling, state transitions, arithmetic, deduplication, retries, timeouts, cancellation, compensation, permissions, budgets, idempotency, approval validation, side-effect dispatch, acceptance, gate verdicts, and proof sealing.

Only `CODE` receives deterministic credit. `MODEL`, `MODEL_AGENT`, and `MIXED` receive zero. `HUMAN` is excluded from numerator and denominator.

Weights are fixed:

| Taxonomy | Weight |
|---|---:|
| control plane | 5 |
| side effect | 5 |
| decision | 3 |
| transformation | 2 |
| retrieval | 1 |
| presentation | 1 |

No process may change taxonomy, weights, identities, or graph structure to improve its score.

## 2. Authority-generated operation inventory first

No D85 score is admissible from caller-authored nodes.

A deterministic authority must first extract structural symbols and realized call-site stages from current source and adapter evidence. Each provisional inventory ID binds:

- canonical source root
- source call-site span and SHA-256
- adapter path, SHA-256, and operation
- full execution path, predecessors, and successors
- locked external-module origin, SHA-256, resolver fingerprint, initialization evidence, and symbol when present

A separate authority-owned classification must bind one runtime kind and taxonomy to every provisional inventory ID. The classified ID set must equal the extracted inventory ID set. Classification mints the final operation identity from the provisional inventory ID, runtime kind, taxonomy, and remapped graph bindings. No caller supplies classification, and no D85 score exists before both gates pass.

The submitted provisional inventory must equal the extracted inventory exactly. Reject missing or extra stages, duplicate source bindings, zero-work operations, aliases (including an external artifact bound to an already-hashed inode), decorative nodes, and node splitting. A model boundary cannot hide several decisions behind one stage; harmless code cannot be split into padding.

Planned and realized manifests are the only states. Crystallization creates a new planned manifest and cannot waive D85 or Gate-D.

## 3. Geometry

The canonical lattice is:

- `7` levels × `3` diamonds × `4` BMS modes = `84` primary coordinates
- `84` coordinates × `7` IQRSQPI steps = `588` execution cells
- `4` modes × `7` IQRSQPI steps = `28` reusable archetypes
- `40` engines score work inside cells; they are not an axis

`L0` is external intake and is excluded from the 588 cells. `L1–L7` are alternative complexity altitudes, not sequential execution stages. Select exactly one `L/D/A` coordinate; run IQRSQPI inside it.

The conflicting `L1 CAPTURE → L7 AUTONOMIZE` subsystem is migration debt. It must be renamed as lifecycle phases before clean cutover; it cannot define lattice levels.

## 4. Level gates

- **L0 Intake:** immutable intent, scope, executable done-test, authority, risk, source hashes, and out-of-scope.
- **L1 Mechanical:** reproducible algorithm and no model decision.
- **L2 Structured:** versioned typed schema, bounded parameters, deterministic validation, explicit defaults.
- **L3 Workflow:** explicit state graph; code-owned retry, timeout, cancellation, compensation, and idempotency.
- **L4 Bounded Agentic:** model necessity, typed boundary, allowlisted tools, hard budgets, deterministic validator/fallback, independent checkpoint.
- **L5 Mechanism:** causal pathway, alternatives, tradeoffs, constraints, falsifier, sources.
- **L6 Strategy:** multi-source synthesis, contradiction register, scenarios, uncertainty, human decision for high-stakes choices.
- **L7 Doctrine:** version, blast radius, migration, rollback, adversarial review, human ratification; no direct execution from exploration.

A selected level either passes or returns `BLOCK_LEVEL_FIT`.

## 5. BMS

Independent inputs:

- `failure_cost`: `0` no material consequence → `1` catastrophic
- `reversibility`: `0` irreversible → `1` complete immediate rollback
- `mechanism_clarity`: `0` unknown → `1` fully specified and testable
- selected `L1–L7` altitude
- `past_failure_rate`, default `0`, versioned override
- `data_volume`, default `0.5`, versioned override

Target formula:

```text
raw = (1 - failure_cost) * 0.4
    + reversibility * 0.3
    + mechanism_clarity * 0.3

final = clamp(
    raw
    - past_failure_rate * 0.2
    + (data_volume - 0.5) * 0.1
    + altitude_bonus[level],
    0,
    1
)
```

The current positive `failure_cost * 0.4` implementation is blocked migration debt: higher catastrophic risk must not increase confidence.

Thresholds are sharp: `A1 ≥ 0.75`, `A2 ≥ 0.45`, `A3 ≥ 0.25`, otherwise `A4`. Code selects the mode. Agents cannot override it.

## 6. Execution modes

### A1 CODE

No model in the decision path. Code implements and accepts.

### A2 HYBRID

A model may propose through typed boundaries. Code validates and decides. Every model node requires:

- falsifiable necessity claim
- recorded deterministic alternative or probe
- numeric expected improvement in `(0, 1]`
- nonempty typed input and output schemas
- positive integer attempt, tool, and token ceilings
- positive bounded time and cost ceilings
- reachable CODE validator node
- reachable CODE fallback node
- reachable CODE failure-state node

Validator, fallback, and failure references must be reachable from the model node in the realized graph. Provider, budget, schema, timeout, and offline errors are explicit failures; none becomes a neutral score.

### A3 BOUNDED AGENT

A3 requires persisted versioned state, typed boundaries, tool allowlist, code-owned retries/timeouts/cancellation/budgets, independent checkpoints, and candidate-only output. The current missing A3 runtime returns `BLOCK_A3_RUNTIME_UNAVAILABLE`. No same-attempt A3→A1 or A3→A4 fallback exists.

### A4 HUMAN DECISION

A4 presents evidence and options. A human decides. Agents cannot decide, approve, or arm Gate-D. A4 is not Gate-D.

## 7. Admission sequence

1. Startup hard-stop: `PASS | BLOCK`
2. L0 intake: `PASS | BLOCK`
3. Level, diamond, BMS, and mode lock: `PASS | BLOCK`
4. Planned D85: `PLAN_ADMISSIBLE | BLOCK`
5. Agent candidate: `CANDIDATE | BLOCK`
6. Independent verifier plants the guarded defect, proves RED, restores, proves GREEN: `VERIFIED | BLOCK`
7. Build D85: `REALIZED_PASS | BLOCK`
8. Runtime/release D85 freshness: `REALIZED_PASS | BLOCK`
9. Internal hash-bound proof: internal terminal
10. Separate effect request only for outward or irreversible work
11. Gate-D: `ARMED | BLOCK`
12. Code dispatch, state readback, and receipt

Gate-D is never on the default internal coding path.

## 8. Failure rule

Every failed gate:

- returns `BLOCK`
- ends the current attempt
- preserves the exact inputs, diagnostics, and observed state
- permits no forward progress
- creates no hidden fallback
- requires a new immutable version to re-enter the failed gate

Only code-classified transient execution errors may retry within an attempt and only within the declared budget.

## 9. Tool calls

The agent proposes an immutable envelope containing process/version, exact tool and adapter versions, typed arguments, expected postcondition, operation identity, risk, authority, source/graph/necessity/artifact/proof hashes, timeout/retry/cancellation/token/cost budgets, mutation idempotency key, and evidence sink.

Separate principals:

1. Agent proposal
2. Deterministic registry/schema gate
3. Deterministic scope/authority/D85 gate
4. Human Gate-D only when outward or irreversible
5. Deterministic versioned adapter execution
6. Deterministic readback, postcondition validation, state commit, and receipt

Malformed events and missing/corrupt authority records return BLOCK. Models cannot call unadmitted adapters, choose an authority path, mutate state directly, own retries, commit transitions, or accept their output.

## 10. Gate-D authority

The current mutable `rig-loop` `run.json`, caller-supplied `by`, and visible phrase do not authenticate the human hand and are insufficient for enterprise enforcement.

Target authority requires:

- separate authenticated human front door
- append-only signed approval record
- exact binding to process, manifest, graph, necessity, artifact, proof, and canonical action-envelope hashes
- issue and expiry times with a maximum 24-hour lifetime
- fixed production authority root; production rejects `RIG_LOOP_STATE` override
- test override only under explicit test mode and inside the resolved test sandbox
- pre-tool derivation of the action envelope from the actual event
- atomic `O_EXCL` consumption keyed by approval, proof, and action hashes
- distinct missing, corrupt, unapproved, expired, mismatch, consumed, and root-override BLOCK reasons

D85 eligibility never authorizes an effect.

## 11. One-time build block

An experiment may exist but cannot be scheduled, installed globally, productized, offered to clients, or described as durable until it has executable capability plus owner, state store, schema, idempotency, retry, timeout, cancellation, observability, rollback, runbook, acceptance, proof, and every required admission. Missing evidence returns `BLOCK_INCOMPLETE_ONE_TIME_BUILD`.

## 12. Four coding-agent surfaces

Required surfaces:

- Claude Code: `~/.claude/CLAUDE.md`; registered hooks in `~/.claude/settings.json`
- Hermes: `~/.hermes/SOUL.md`; adapter at `~/.hermes/hooks/rig-loop-gate` is observational and cannot block.
- OMP: `~/.omp/agent/AGENTS.md`; adapter at `~/.omp/agent/extensions/rig-loop-hooks.ts`.
- Prime-Agent: `~/.prime/agent/AGENTS.md`; adapter at `~/.prime/agent/extensions/rig-loop-hooks.ts`.

Every surface must load the same doctrine hash and call the same authority-owned pre-tool compiler. Missing, divergent, or unregistered bindings return BLOCK. Filesystem directories are not registration proof.

## 13. Required non-vacuity proof

Before activation:

- valid planned and realized fixtures pass
- below-threshold fixture fails
- critical-control model fixture fails
- terminal-with-outgoing-edge fixture fails
- node-splitting/padding fixture fails
- hidden-model/transitive-boundary fixture fails
- malformed and unresolved necessity fixtures fail
- missing/corrupt/unapproved/expired/mismatched/replayed Gate-D fixtures fail
- each agent surface blocks a planted violation and passes after restore
- the synthetic job workflow exercises discovery, dedupe, candidate, verifier, build/runtime proof, and dormant effect request without a real submission

A green gate that cannot be made red is theater.

## 14. Current implementation boundary

Implemented and non-vacuously tested: the source-derived realized-operation inventory (`d85.py`, 51-test suite), authority classification, four-ratio D85 scoring, signed exact-action Gate-D with atomic consumption, and surface-wiring verification (`d85_gates.py`, 28-test suite). The synthetic Julie workflow exercises the full chain — inventory, classification, `REALIZED_PASS`, dormant Gate-D arm, replay BLOCK — without a real submission.

Still open: live harness invocation on every surface, clean isolated-loader proof for external modules (`runtime_loader_proven: false`), planned-manifest admission, and sealed release/effect receipts. `rig-loop doctor --json` verifies canonical adapter bytes and managed JSON entries, not just markers; parity is not proof that a running harness loaded the new adapter. `rig-loop wire` prepares changes without applying them. Live security wiring requires approval.

### Trust model and admitted limits

- The Gate-D signing key is an operator-held local secret under the authority root (`gate_d/key`). The threat model is a coding agent, not an attacker with local file access; root or local-file compromise defeats every local gate by definition. The signature's job is binding one approval to one exact action hash so it cannot be reused, replayed, or retargeted — not replacing the operator's authority.
- Approval lifetime is measured against the local system clock; clock rollback is outside the threat model. Consumption is atomic `O_EXCL` on local APFS; crash between verify and consume can at worst double-report, never double-authorize a different action.
- Scoring weights are code in `d85_gates.py`; they are covered transitively because every approval binds the realized-score hash, and weight changes alter ratios and therefore the realized hash, invalidating outstanding approvals as `BLOCK_GATE_D_MISMATCH`.
- "Exact" extraction means exact within the closed grammar: admitted programs are extracted fully and in execution order, and any construct outside the grammar fails closed (`SOURCE_UNSUPPORTED_GRAMMAR` or `SOURCE_DYNAMIC_CALL`). There is no best-effort path.
- `d85-run` checks signed launcher content, unchanged build bytes, and a live certificate before entering an OS sandbox. Launchers anywhere are gated while protected roots are active. `--launcher` is identity only; writable outputs require separate exact `--path` literals. At least one path or launcher is required, and TTL must be finite, positive, and no more than 24 hours. Canonicalize protected-root aliases before emitting sandbox rules; a writable directory literal does not admit its descendants.

### Recovery and remaining boundaries

The source gate and extension fail closed for mutation calls when the engine
is unavailable or its result lacks a valid verdict. Read-only recovery remains
available. Arbitrary-code tools remain denied while protected roots are active,
even with path admissions. Do not restore the regex scanner.

Break-glass repairs require Mike's scoped authorization and verification that
the actual writing process inherited `RIG_D85_DISABLE=1`. Do not inject the
variable, change enforcement settings, or switch tool aliases after a denial.
Compile a uniquely matched candidate in memory before atomic replacement,
preserve the original and permissions, then verify the installed source and
the actual hook. Enforcement-test children must remove the override and use
isolated state. Assert JSON `block`, not merely exit zero.

Estate timestamps carry source path, mtime field, and raw value. Numeric
`launcher_epoch` values are UTC Unix seconds. Only dated pre-epoch jobs remain
the legacy retrofit backlog; unknown dates cannot exempt new jobs indefinitely.
The installed Hermes scheduler defines `<profile-home>/cron/jobs.json`; verify
that definition and the actual stores rather than trusting prior path advice.

Shell parsing remains a heuristic. Interpreter, expansion, quoting, and indirect
write behavior are not contained by a command scanner. The OS boundary applies
to scheduled `d85-run` execution, not every interactive harness shell call.
No source repair alone completes the remaining D85 rollout.
