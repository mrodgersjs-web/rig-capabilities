---
name: great-rail-registry-four-way-gate-sh
lane: agent-engineering
source: canonical-curated
exemplar_of: rail-registry-four-way-gate.sh
description: Reference exemplar — an action clears an ordered, visibility-gated four-way rail set at a declared boundary; taxonomy drift, order collisions, and every leg denial exit non-zero with a named refusal
---

# rail-registry-four-way-gate.sh — reference

Canonical asset `rail-registry-four-way-gate.sh` (hook). Path: `capabilities/hooks/rail-registry-four-way-gate.sh`.

## What it gates

The gap it closes: `capabilities/hooks/` held six unregistered one-off guards (`guard-dangerous-commands.sh`, `guard-secret-write.sh`, `tac-plan-gate.sh`, `goal-loop-startup.sh`, `jake-pushback.sh`, `session-size-guard.sh`) with **no event taxonomy, no ordering guarantee, and no per-agent visibility gate**. `jake-pushback.sh`'s decision model is binary allow/block, so the *remembered* and *returned* legs of HELIX's decision are untracked, and nothing routes side-effecting actions to a deterministic executor. RED for this asset means exactly that condition: boundary taxonomy and rail ordering are conventions in someone's head, not enforced state.

Mechanism sources (per `.context/discover-ai/capability-matrix.json`, row `rail-registry-four-way-gate`):

- **openJiuwen: Beyond Static Harnesses for Long-Horizon Coding Agents**, `arXiv:2608.27969` (openJiuwen Team, Huawei; repo `openJiuwen-ai/jiuwenswarm`), video `lNlMXsUQggc`. Verbatim caption quotes (grep-verified substrings of `.context/discover-ai/transcripts/lNlMXsUQggc.txt`):

  > "A rail is a capability attached to a specific life cycle event"

  > "the rail mechanism for attaching here capabilities through life hooks or the composition and visibility gating"

- **HELIX: Model-Harness Co-evolution for Recursive Self-Improvement**, `arXiv:2608.13951` (HKUDS; repo `HKUDS/HELIX`), video `USEk7F9GIZk`: the harness "determines which action of the LLM were now exposed, permitted, executed, remembered, and returned" — and anything with side effects executes *outside the model* on a deterministic surface (sandbox, or an API to real infrastructure) whose result returns as the next observation.

## Contract

House stdin-JSON convention (same shape as `working-memory-commit-gate.sh`): JSON payload on stdin, registry at `$RAIL_REGISTRY` (default `~/.rig/rails/registry.json`), bash `set -uo pipefail`, JSON handled by `/usr/bin/python3` stdlib only (precedent: `guard-secret-write.sh`).

A rail is the tuple **(event, order, capability, visibility, gated)**. The registry declares an event taxonomy; the validator refuses:

| Named denial | Exit | Fires when |
|---|---|---|
| `REGISTRY_INVALID_EVENT:<e>` | 1 | a rail registers against an event outside the declared taxonomy |
| `REGISTRY_INVALID_ORDER:<e>:<n>` | 1 | two rails collide on the same `(event, order)` slot |
| `REGISTRY_INVALID_LEGSET:<e>:missing=<legs>` | 1 | a boundary carries some but not all four gate legs — a partial four-way set is invalid state |
| `RAIL_DENIED_EXPOSED` | 2 | agent role not visible to the rail (or explicitly gated) |
| `RAIL_DENIED_PERMITTED` | 2 | `action.tool` off the rail's allowlist |
| `RAIL_DENIED_EXECUTED` | 2 | side-effecting action names no declared deterministic surface |
| `RAIL_DENIED_RETURNED` | 2 | action declares no observation channel — its result would never return |
| `RAIL_DENIED_UNREGISTERED` | 2 | unknown mode/event/agent/action, invalid registry during a gate, malformed payload, or unwritable decision record — denial, never silence |
| `RAIL_DENIED_VISIBILITY_LEAK` | 1 | `visible_rails` enumeration escapes visibility-minus-gated (superset) |

Gate mode runs the event's four rails **in declaration order** and refuses on the first red rail, naming it. `visible_rails` mode enumerates exactly an agent's visibility set minus gated entries in declaration order. With `$RAIL_DECISION_LOG` set, every decision appends one JSONL row with the per-rail verdict **and per-rail duration in ms** (a slow rail is then visible as a global stall, the row's known risk) plus the final verdict — that row is the *remembered* leg; every leg is recorded even on denial.

## The done_when proves each leg separately

Fixtures live in `capabilities/hooks/fixtures/rail-registry-four-way-gate/`. Ten checks, each asserting concrete exit codes:

1. `payload-allowed.json` → **0**, and the decision record carries `"verdict": "allow"` with four `"ms":` durations.
2–5. one payload per rail (`payload-denied-{exposed,permitted,executed,returned}.json`) → **2** AND the named refusal on stderr — a denial that doesn't name its rail fails the suite.
6. `payload-unknown-action.json` (mode `teleport`) → **2** `RAIL_DENIED_UNREGISTERED` — the fail-closed case asserts *denial, not silence*.
7. `registry-bad-event.json` → validator **1** `REGISTRY_INVALID_EVENT`.
8. `registry-order-collision.json` → validator **1** `REGISTRY_INVALID_ORDER`.
9–10. `visible_rails` for `main` and `delegated` diffed **byte-exact** against `expected-visible-{main,delegated}.txt` — delegated's set is `main`'s minus the gated `mem-recall` rail; any superset fails the diff.

Plant-failure (2026-09-02): making `leg_check` unable to refuse flipped exactly the four per-rail checks to `pass: false`; the allow/validator/visibility checks stayed green — each rail's denial is guarded by its own check, not by luck.

## What RED means operationally

- `REGISTRY_INVALID_EVENT` on a live deploy: someone wired a hook to a boundary nobody declared — the capability would never run (or run everywhere). The registry refuses the drift *before* it becomes a silent no-op.
- `REGISTRY_INVALID_ORDER`: two rails claim one slot; composition order becomes file-order-dependent and one refactor reorders side effects. Fix the ladder, don't pick a winner by luck.
- `RAIL_DENIED_EXPOSED` for a delegated agent: it was handed a capability its role must not see — the corpus's named failure, "a delegated agent handed inappropriate capabilities", stopped at the boundary instead of mid-run.
- `RAIL_DENIED_PERMITTED`: tool outside the boundary's allowlist.
- `RAIL_DENIED_EXECUTED`: a side effect tried to run inside the stochastic core (`executor: "model:improvise"`). Non-determinism stays quarantined inside the model; real effects go to a declared sandbox/API surface.
- `RAIL_DENIED_RETURNED`: a side effect with no observation channel — exactly how the corpus's harness-level failures happen ("the decisive evidence was never shown here in the context window to the LLM"); here the action never starts instead.
- `RAIL_DENIED_UNREGISTERED` at a gate: unregistered ≠ allowed. An action the registry doesn't know is denied loudly, so new action classes show up as named gaps, not as silent passes.

## Ceiling

The hook validates what the payload **declares** — `executed` checks that a declared deterministic surface is *named*, not that it truly ran; registry writer identity is a harness-kernel concern outside any hook. Wiring this into a harness settings file is a separate Gate-D action.
