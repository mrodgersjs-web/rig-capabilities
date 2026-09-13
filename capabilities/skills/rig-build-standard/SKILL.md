---
name: rig-build-standard
description: "RIG build standard (umbrella) — the one always-loaded policy for OMP, Claude Code, Hermes and Prime Agent: diagnose before building, score determinism with D85 (all four ratios >= 0.85), route the work to its owner with the T1-T8 contract, and never call a coding build done or push it until the four commit-gate receipts exist. Load for ANY code, config, schema, skill or owner-authority change in any runtime. Specialist execution lives in the rig-stackwright agent; this skill is the standard, not the worker."
when_to_use: "Starting or finishing any coding/build task in OMP, Claude Code, Hermes or Prime Agent; before any git push, deploy or 'done' claim; when asked which tool/scheduler owns a piece of work; when a build or loop reports UNKNOWN_PROCESS, BUILT_UNVERIFIED, exit 2, or a missing certificate."
version: 1.0.0
owner: rig-intelligence
domain: Agent engineering / build standard
status: Candidate
verified_by: UNVERIFIED
verified_on: UNVERIFIED
acl: public
relates_to: rig-stackwright, durable-build, iqrsqpi-v20, iqrsqpi-v20-slice, rig-lattice-system, gate-d-loop, git-push-safety-loop, adversarial-verification-loop, proof-loop
outcome: "code-engineering: every runtime inherits the same build standard without being told, no owner is chosen by keyword, and 'done' is four recomputed receipts on one record rather than an adjective"
done_when:
  - file:capabilities/skills/rig-build-standard/SKILL.md
  - file:capabilities/data/rig-build-standard/policy.md
  - file:capabilities/data/durable-repeatable-index/SCHEMA.md
  - cmd:bin/rig-build-standard --help
  - cmd:bin/rig-build-standard packet --help
  - cmd:bin/rig-build-standard surface --help
  - cmd:bin/rig-build-standard test
  - cmd:python3 -m unittest tests.test_build_standard
  - grep:capabilities/skills/rig-build-standard/SKILL.md:d85_certified
quality_floor: 0.7
---

# rig-build-standard — the standard, in one page

Thin always-loaded policy. Everything below is a pointer to code that already
decides; nothing here is a table to memorise, and nothing here is enforced by a
trigger regex. The enforcement boundary is the CLI, the loop engine and the
commit gate (see `capabilities/data/rig-build-standard/policy.md`).

## Who owes what

| Question | Authority (read it; do not restate it) |
|---|---|
| Which coordinate is this work? | `bin/rig-build-standard diagnose --input FILE` → `rig_capabilities/build_diagnose.py` against the frozen 588-cell pack |
| Which tool owns it (T1–T8)? | `capabilities/skills/rig-determinism-85/authority/standards/tool_selection.v2.json`, admitted by `tool_selection.select_framework` — it BLOCKS on missing/ambiguous facts instead of defaulting |
| How deterministic is the build? | `capabilities/skills/rig-determinism-85/bin/rig-determinism-85 inventory → classify → score` (all four ratios ≥ 0.85, A1-only certification) |
| May this loop advance? | the loop's own gates; for build loops the final `d85_certified` gate is non-forceable (`rig_capabilities/loops.py`) |
| May I say done / may I push? | `bin/rig-build-standard check --repo . --sha SHA --manifest FILE` → `rig_capabilities/commit_gate.py` |
| What is the shared context for one build? | `bin/rig-build-standard packet --diagnosis FILE --out FILE` → `rig_capabilities/context_packet.py` |
| What is the estate status per cell? | `capabilities/data/durable-repeatable-index/SCHEMA.md` + `bin/rig-build-standard index` |

## The four receipts (the whole done/commit gate)

A coding build — any code, config, schema, skill or owner-authority change, from
any runtime, including this repo's own machinery — is `done` only when ONE build
record holds all four, at the claimed commit SHA:

1. **Fresh D85** — `verify-cert` re-run for that exact build, all four ratios
   recomputed ≥ 0.85. A stored PASS is not evidence.
2. **Joint assurance ≥ .95** — the bound index row's predeclared one-sided lower
   bound on (durable setup AND repeatable results) inside its frozen envelope,
   with mandatory fault/recovery coverage exercised. `INSUFFICIENT_EVIDENCE` is
   the honest answer until enough independent trials exist.
3. **Independent verdict** — a cross-family `rig-loop verify` verdict sealed to
   the same record, files and trial profile.
4. **Outward-effect receipt** — the exact Gate-D approval ID for that commit/push
   plus `git ls-remote` proof the remote ref equals that SHA.

No two receipts substitute for another. Missing any → the record stays
`BUILT_UNVERIFIED`. Local `git commit` may exist as work state; the gate binds the
human "done" and the push.

## Sequence (never three independent label-choices)

level assessment → A1–A4 necessity assessment → BMS computation → reconciliation
→ owner (T1–T6) + T7 always + T8 on effects → build → receipts. A mismatch halts
that unit; refine the decomposition or get the missing evidence. Do not tune a
scalar to reach a mode, and do not relabel an A2/A3/A4 process as A1 to obtain a
certificate — the certifier supports A1 only.

## Escalation and refusals are the product

- `UNKNOWN_PROCESS` → the process has no authority record; register an immutable
  version (S10), never run the same bytes again hoping for a different verdict.
- exit 2 / BLOCK → terminal for that version; produce a genuinely revised
  immutable process version.
- `INSUFFICIENT_EVIDENCE`, `UNAVAILABLE`, `DEGRADED` → report them. An honest
  unavailable is never written as PASS.
- Research, reads, diagnosis and authorized repair stay available while a build
  gate is red. The gate blocks *advancement and certification*, not investigation.

## Out of scope for this skill

Executing outward actions (needs typed Gate-D per action), enabling paused
services, credential or scheduler changes, and any A2–A4 certification claim.
The `rig-stackwright` agent diagnoses, routes and builds; it cannot approve,
self-certify, or mark its own promotion.
