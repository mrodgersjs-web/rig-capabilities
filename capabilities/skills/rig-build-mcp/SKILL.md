---
name: rig-build-mcp
description: "How to drive the capabilities_build_* MCP tools over stdio correctly: the call order (store triage -> diagnose -> run_start -> evidence -> qualify), what each refusal actually means, and the recovery path from blocked/stale/unknown states. Teaches the closed-schema rule — no argument ever carries a pass/approved/qualified/verdict or an identity."
when_to_use: "Calling any capabilities_build_* tool from any harness; when a build tool answers blocked, stale, unknown or 'unknown keys refused'; before claiming anything ran against the rig_build store."
version: 1.0.0
owner: rig-intelligence
domain: Agent engineering / build backend
status: Candidate
verified_by: UNVERIFIED
verified_on: UNVERIFIED
acl: public
relates_to: rig-build-standard, durable-build, gate-d-loop, proof-loop
outcome: "an agent reaches correct build-store states on the first try, reads refusals as instructions, and can never mint authority through an argument"
done_when:
  - cmd:python3 -m unittest tests.test_build_mcp_protocol
  - file:tests/test_build_mcp_protocol.py
  - file:runs/agentic-stack-buildout/backend/proofs/mcp-b45-scenarios.json
  - file:runs/agentic-stack-buildout/backend/proofs/mcp-b44-protocol.json
quality_floor: 0.7
---

# rig-build-mcp — calling the build backend without fighting it

The server is `python3 server.py` (repo root) over newline JSON-RPC 2.0:
`initialize` → `notifications/initialized` → `tools/list` → `tools/call`.
Every answer is either a JSON-RPC error (protocol: unknown tool/method) or a
tool result whose `isError` distinguishes refusals from states.

## Call order that works

1. `capabilities_build_store` — triage first. `configured: false` means
   UNCONFIGURED; believe it and stop, do not retry downstream tools.
2. `capabilities_build_diagnose` — validate the packet (goal, cell_id from
   the 588-cell authority, non-empty done_test, effort_budget with exactly
   cpu_minutes+usd+wallclock_seconds, evidence_refs as `kind:value`).
   Read-only; returns the normalized packet + live pack sha.
3. `capabilities_build_run_start` — same packet + `process_key` +
   `process_version`. Needs an approved rig_build target AND an owner
   binding (cell contract + process version sealed via
   `bin/rig-build-standard` / build_store, never through MCP).
4. `capabilities_build_evidence_add` — per event: `sequence` must be exactly
   max+1, `fencing_token` must EQUAL the run's current token (read it from
   `capabilities_build_run_get` → `run.fencing_token`).
5. `capabilities_build_qualify` — (cell_id, sha, manifest_path) only. The
   verdict is RECOMPUTED from commit_gate + live index; nothing you send
   can make it admit.
Read runs with `capabilities_build_run_get` / `capabilities_build_run`;
index/gap state with `capabilities_build_index` / `capabilities_build_gaps`
(state is live | empty | unknown — `empty` is honest, not failure).

## What each refusal means — and the recovery

| Answer | Meaning | Recovery |
|---|---|---|
| `unknown keys [...] refused` | closed schema (`additionalProperties:false`); identity/verdict words are never caller arguments | delete the key; identity is the server's `RIG_CAP_CALLER`, authority comes from receipts |
| `missing required arg(s): X` | schema required not satisfied | add X; nothing defaults silently |
| `state=blocked, reason="no rig_build target"` | no DSN discovered (`RIG_CAP_DSN` unset, no rig-dev-db) | ask for B11/B12 approval; the `next_action` names the migration path |
| `state=blocked, reason="no owner binding"` | cell contract/process version not sealed | run bind_cell out-of-band first; the store never invents an owner |
| `state=refused, "stale fencing token"` | your token != run's current token (B47) | `capabilities_build_run_get` → use current `run.fencing_token`; NEVER retry the old token |
| `state=refused, "sequence gap"/"duplicate"` | events are append-only, exactly max+1 | re-read max sequence from run_get, use max+1 |
| `state=unknown` on run_get | unknown run OR storage unreachable (reason names which) | if reason says storage — check store triage; a run you expected means it never started |
| `diagnosis refused: ...` | packet invalid against the 588-cell authority | fix the named field; see step 2 |
| `golden pack verification failed` / state `stale` | index handle bound to an older pack generation | re-read via `capabilities_build_index`; qualify against the CURRENT `criteria_pack_sha256` |
| `admitted: false` with refusals | recomputed gate verdict — blockers are named | satisfy each named receipt; there is no override argument |

## Hard rules

- Never send `pass`, `approved`, `qualified`, `verdict`, `admitted`,
  `requested_by`, `started_by`, or `state` as an argument. There is no
  slot; the call is refused, and that refusal is the guarantee.
- `omission_request` stages a DORMANT PENDING_HUMAN_REVIEW file only —
  approval is Gate-D/human and the pending stays open regardless.
- `configured: false` / `state: unknown` / `state: blocked` are honest
  terminal states for this session. Do not dress them up downstream.
- `capabilities_build_run_get` pages newest-first: `cursor` is an OFFSET into
  that ordering and `next_cursor = cursor + limit` (limit clamps to 100). It
  used to echo the cursor without applying it, so every page re-served page 1.

## Proof this stays true

`python3 -m unittest tests.test_build_mcp_protocol` drives the real stdio
server (handshake + tools/call), spins a throwaway Postgres for the live
paths, and refreshes the two receipts listed in `done_when`.
