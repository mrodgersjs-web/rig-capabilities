---
name: d85-compliance-checklist
description: "Determinism-85 build-quality checklist for RIG solutions, applications, and durable systems in OMP. Load for build certification and place its five gate phases last. Ordinary startup, research, reads, diagnostics, Python execution, memory capture, and authorized local edits do not require D85 admission. Gates run via rig-determinism-85 (inventory/classify/score/checklist/verify-cert/gate-d/d85-run); grounding via reverify where applicable; registration via a process registered in authority/registry.json."
version: 1.0.4
tags: [d85, determinism, enforcement, coding, gate-d, checklist]
metadata:
  author: RIG / Mike Rodgers
---

# D85 Compliance Checklist — Build Quality and Certification

**Authority:** D85 chain = released `rig-determinism-85/SKILL.md` (inventory → classification →
four-ratio score → checklist build-binding → exact-action Gate-D → surface wiring). Lattice/BMS/
altitude taxonomy = `CODING_AGENT_STANDARD.md` — CURRENTLY CANDIDATE-ONLY (uncommitted
d85-hardening worktree, not production authority): treat A/L/BMS obligations below as candidate
doctrine until that document is released. Where this checklist and a RELEASED authority file
disagree, the released file wins — re-read it, patch this one.

**Current scope (Mike, 2026-09-11):** D85 gates build certification for RIG solutions,
applications, and durable systems. It does not gate ordinary startup, research,
file access, diagnostics, Python execution, memory capture, or authorized local edits.
Do not infer build scope from a shell verb or directory. A failed or unknown gate
prevents certified completion or promotion, not repair work. This scope supersedes
older universal-admission wording below. Before building, record a canonical
Lattice cell and recomputed BMS through `rig-lattice-system`; retain the Lattice
audit with tests and artifact hashes. Before certification, run `checklist
<build-file> --process-id <id>` and `verify-cert <build-file> <certificate-file>`.
Use current source-derived inventory and all four ratios at or above 0.85.
Self-authored failure JSON is not trusted execution evidence. Existing approval,
privacy, repository-placement, and active-loop boundaries remain independent.

**Rule zero:** D85 eligibility (may this process exist durably?) is separate from Gate-D
authorization (may this ONE exact outward effect happen now?). Both gates must pass;
neither substitutes for the other. Exit-2 BLOCK is terminal for the current version —
remediation requires a NEW immutable process version, never a retry of the same bytes.

---

## Phase 0 — Classify the build (build missions only)

- [ ] Run startup: `rig-meta-harness startup --agent <runtime> --cwd <repo> --format json` — honor `hard_stop`; only `status: PASS` counts (`null` is not a PASS).
- [ ] Declare the coordinate BEFORE the first source edit: one cell `L{n}-D{d}-A{m}-{step}`. L1–L7 are ALTERNATIVE complexity altitudes, never sequential stages; advancing IQRSQPI changes the step, not level or mode. L0 is outside the lattice.
- [ ] Compute BMS confidence: `raw = (1 - failure_cost)*0.4 + reversibility*0.3 + mechanism_clarity*0.3` plus the coordinate `altitude_bonus` (L1 +.35, L2 +.28, L3 +.12, L4 0, L5 −.08, L6 −.20, L7 −.35). Risk must DECREASE as failure cost rises. Reject NaN/inf/bool/out-of-range.
- [ ] **Mismatch rule:** the coordinate's declared mode must equal the evidence-computed mode; a mismatch BLOCKS admission. A new level or mode requires new evidence and a new immutable attempt.
- [ ] Classify every operation into one runtime kind + one taxonomy category (Phase 1). HUMAN is reserved for separately bound human events and is excluded from BOTH numerator and denominator — never a label for source-executed call sites.
- [ ] State durability: runs more than once, schedules itself, persists state, or produces effects → durable → full checklist. Otherwise the stateless fast path still owes: owner, input schema, acceptance test, error surface, no silent effects.

## Phase 1 — Component determinism audit (all components, all categories)

Deterministic CODE owns ALL of: scheduling, state transitions, arithmetic, deduplication,
retries, timeouts, cancellation, compensation, permissions, budgets, idempotency keys,
approval validation, effect dispatch, acceptance checks, gate verdicts, proof sealing.

Taxonomy weights (fixed):

| Category | Weight | Must be CODE |
|---|---|---|
| control plane | 5 | always (critical control) |
| side effect | 5 | always (critical control) |
| decision | 3 | CODE verdict; MODEL may only propose (A2+) |
| transformation | 2 | CODE unless proven model-only |
| retrieval | 1 | CODE orchestration; opaque externals earn no credit |
| presentation | 1 | CODE rendering |

- [ ] Every operation emitted by source is in the DENOMINATOR. Only eligible CODE earns numerator credit. MODEL, MODEL_AGENT, MIXED, ineligible CODE, and opaque external-module operations earn ZERO.
- [ ] Every MODEL operation carries a typed necessity record: falsifiable claim, deterministic alternative, `expected_improvement` ∈ (0,1], non-empty typed input/output schemas, positive attempt/tool/token and time/cost ceilings, reachable CODE validator + fallback + failure-state operations.
- [ ] No credit padding: repeated call sites, trivial builtin normalization (one credit segment max), wrapper indirection, default-bound parameters, or classification-authored topology do NOT raise the score.
- [ ] Source topology inventoried as-is with bounded, fail-closed ceilings: source size, structural nodes, emitted operations, recursive expansions, path expansions. Classification ID set must EQUAL the extracted inventory exactly (missing/unknown/duplicate/stale-bound = BLOCK). Edges mirrored, acyclic, self-edge-free, reachable from roots.

## Phase 2 — Score and certify the build

- [ ] `rig-determinism-85 score <process_id>`: ALL FOUR ratios ≥ 0.85 with `REALIZED_PASS` — aggregate unweighted, aggregate weighted, minimum-path unweighted, minimum-path weighted. Exit 2 = BLOCK = terminal for this version; produce a new version, never a retry.
- [ ] Fresh bindings, no stored PASS strings, no caller-supplied booleans: `inventory_sha256`, `classification_sha256`, `realized_sha256` on the current (v1) certificate schema; re-check anytime with `verify-cert`.
- [ ] `checklist <build-file> --process-id <id>` bound to the exact `inventory_sha256` snapshot: unbound / mismatched / stale = BLOCK.
- [ ] Effects: `gate-d <process_id> --action <exact-action-file>` — signed, one-time, exact-action; expired/replay/unapproved/mismatch/corrupt = BLOCK. Durable runs launch via `d85-run <script>`: released guarantee = `sandbox-exec` denies writes to all protected roots except exact admitted literals. Network/process-fork isolation is CANDIDATE hardening, not a released guarantee — do not treat `d85-run` as a full sandbox.
- [ ] Explicit legacy admission is only for deliberate admission/launcher consumers. It is not a prerequisite for ordinary tools or local edits. Never set `RIG_D85_DISABLE` to implement this scope.
- [ ] Authority paths never come from caller HOME/env/sys.path. Security-sensitive invocations use the fixed hash-bound Python with `-I -B -S`.

## Phase 3 — Archetype conformance (A1–A4; one mode per attempt, thresholds bind)

Mode thresholds and budgets (ceilings, not permission to spend):

| Mode | confidence | Rule | Mission budget |
|---|---|---|---|
| A1 CODE | ≥ .75 | code implements and accepts; no model in the deployed decision path | $0 |
| A2 HYBRID | ≥ .45, < .75 | model proposes through typed boundaries; code accepts or blocks | $0.10 |
| A3 BOUNDED AGENT | ≥ .25, < .45 | candidate-only bounded runtime with independent checkpoints | $0.50 |
| A4 HUMAN DECISION | < .25 | human decides; model cannot self-ratify or arm Gate-D | $0 |

- [ ] A1 also requires the tool-selection predicate test: on-demand `native_typed_code` allowed only with no scheduler and no higher-precedence predicate (clock_critical → resident_service → non_engineer_surface → multi_agent_graph → agent_reasoning → on_demand_command).
- [ ] The current certifier supports A1 only. A2–A4 certification remains blocked until a trusted execution-receipt verifier exists. Ordinary work in those modes remains available; do not mislabel it as A1.
- [ ] A4 binds an authority-declared human identity, exact scope, real UTC time, immutable build attempt, and process/cell/intent/BMS/inventory hashes; rechecked before final acceptance. A4 ≠ Gate-D.

## Phase 4 — Level conformance (L1–L7 altitudes; one selected, IQRSQPI runs inside it)

Canonical altitude names: L1 Mechanical … L7 Doctrine.

- [ ] **L1 Mechanical:** same input + version → same result; executable done-test; no model decision; stdlib-first; acceptance = the command's own exit + output.
- [ ] **L2 Module:** typed IO, explicit error surface, one runnable check that FAILS if the logic breaks.
- [ ] **L3 Service/feature:** state schema + migration declared; retries/timeouts/idempotency in CODE; structured failure signals for the next agent at 3am.
- [ ] **L4 Job/program:** scheduler-owned cadence, budget, kill switch, durable state, `d85-run` execution, proof per cycle.
- [ ] **L5 Product/flow:** all L4 + acceptance gates that provably go RED (plant the failure; a green that won't go red is theater), compensation/rollback, north-star lock with logged drift checks.
- [ ] **L6 Program/estate:** named ownership map per boundary, one writer per shared boundary, ≤3 concurrent workers, single integration owner, cross-component contracts frozen before fan-out.
- [ ] **L7 Doctrine:** versioned policy, cross-surface impact analysis, migration + rollback, independent review, human ratification; report installed / configured / consented / loaded / exercised / enforced SEPARATELY (never conflated).

## Phase 5 — Verification and proof (grounded evidence per claim type)

- [ ] Every load-bearing claim bound to command + exit code / test / artifact hash — never an adjective. A text audit is not build proof.
- [ ] Ground each claim with the tool that fits it: reverify `verify` judges FILE/BINARY claims (bytes_at, instructions, patterns, emulation) and `equiv` checks PYTHON/C implementations against a reference — it is NOT a universal code verifier. Everything else: bound the claim to a command + exit code, a test, or an artifact hash. Report only VERIFIED/OBSERVED; REFUTED + `evidence.actual` overrides any model prior; non-zero exit gates agents/CI. Restore session state from the `.reverify/` ledger (`re_ledger`); never re-propose KNOWN FALSE.
- [ ] Plant-failure per trusted gate: proven RED → restored GREEN → kept as regression fixture.
- [ ] Independent verifier (different model family) issues the terminal PASS/REVISE/ESCALATE; Builder never self-certifies (GEV lock).
- [ ] ProofPacket sealed: commands, exit codes, artifact sha256s, verifier verdict, approval IDs. `done` without a sealed packet did not happen.
- [ ] Outward/irreversible effects (send, publish, deploy, push, spend, delete, credential change, restart, scheduler activation, instruction-surface edits): fresh exact Gate-D per action file. Approval in one context does not extend to the next. Same-UID file replacement remains an explicit trust boundary — hashes give identity/freshness, not ownership.

## Todo-integration contract (instruction-surface mandate; OMP only)

Mechanism honestly stated: this is a PERSISTENT INSTRUCTION in `~/.omp/agent/AGENTS.md`, obeyed
by each OMP session at the instruction level. The `todo` tool does not read it — entries are not
mechanically injected, and other harnesses (Claude/Codex/Hermes/Pi/Prime) are NOT covered until
mirrored or the doctrine is released to them.
Within OMP solution, application, and durable-system build sessions: the `todo` init ENDS with the phase group
`D85-Classify → D85-Score → D85-Archetype+Level → D85-Verify → Seal`, placed last after all
work phases; none marked done without its named artifact (startup packet JSON, score output,
coordinate record, fresh command evidence, sealed ProofPacket). The group gates the done-claim,
not ordinary tool access or the first edit. Unrelated tasks do not require this group. Solution/app loops declare a final `d85_certified` gate bound to the build record, certificate, and root.
(Mike directive 2026-09-15: gate group moved from todo head to todo tail.)

## Enforcement surfaces (code, not prose)

- `rig-determinism-85 inventory|compare|classify|score|select|checklist|verify-cert|estate-validate|gate-d|wiring|admit-request|admit-approve|admit-status|d85-run` (exact released command set) — production reads only `authority/registry.json`; no env/CLI override. Registration = process registered there with SOURCE-DERIVED inventory + authority classification; hand-authored JSON notes (including anything under `~/.rig/d85/processes/`) have zero gate standing.
- Ordinary pre-tool dispatch does not require D85 admission. Explicit admission/launcher consumers still validate their configured boundaries. A failed build gate withholds certification or promotion; repair tools remain available.
- `reverify` hooks + MCP — context rollover/ledger for long sessions; claim grounding where a file/binary artifact exists.
