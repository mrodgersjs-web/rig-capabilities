---
name: great-working-memory-commit-gate-sh
lane: agent-engineering
source: canonical-curated
exemplar_of: working-memory-commit-gate.sh
description: Reference exemplar — a completion claim with no observation-backed receipt row exits 2; a receipt-backed completion exits 0
---

# working-memory-commit-gate.sh — reference

Canonical asset `working-memory-commit-gate.sh` (hook). Path: `capabilities/hooks/working-memory-commit-gate.sh`.

## What it gates

The gap it closes: RIG graded completions post-hoc (`capabilities/loops/doer-checker-validator.md` runs in a later cron) and nothing blocked a DONE claim **inside the turn** that has no observation behind it. This hook makes a completion write a two-party act: the model may propose, but only a harness-committed, observation-backed receipt row in the working-memory ledger can flip a goal to DONE.

Mechanism source: Recuris — *Recursive Experiential-Working Memory Evolution for Long-Horizon Agent Harnesses*, `arXiv:2608.24876` (verified in `.context/discover-ai/link-verdicts.json`); reference repo `Gen-Verse/Recuris` (verified, same file); video `F1XqqVNBa4o`. Verbatim caption quotes (all three grep-verified as substrings of `.context/discover-ai/transcripts/F1XqqVNBa4o.txt`, 2026-09-02):

> "the working memory maintains a verified task state all the time"

> "working memory proposes that the state changed, the checkers compares now the proposal with the external evidence"

> "a goal is acknowledged here as completed only if the environment observation supports it"

## Contract

PreToolUse-style, house stdin-JSON/exit-2 convention (same shape as `guard-dangerous-commands.sh`): JSON payload on stdin; exit 2 + stderr = block; exit 0 = allow. Bash, `set -uo pipefail`, extraction with `tr`/`sed`/`grep` only — no jq, no python inside the hook.

- **Claim detection** (deterministic): `"done"|"status"|"state"|"task_status"` key set to `true|DONE|done|complete|completed|COMPLETE`; in-content/YAML form `status: DONE` / `state: COMPLETE` / `done: true` / `complete: true` (also catches a Bash-tool `echo 'status: DONE' >> state.json`); `TASK_COMPLETE` sentinel. Everything that is not a claim passes untouched.
- **Proposal escape hatch**: a claim payload carrying `proposed: true` / `proposal: true` is a proposal, not a commit — allowed. This is the model-facing path; the gate blocks the commit step only.
- **Ledger**: `$RIG_WM_LEDGER` (JSONL; default `$HOME/.rig/wm/ledger.jsonl`). A row counts as a receipt iff it has a non-empty `"receipt"` id, a non-empty `"observation"`, an `"evidence"` path that **exists on disk**, and a `"session_id"` matching the payload session or `"*"`. A receipt row naming a missing evidence artifact is a **synthetic receipt** — registered as rejected, mirroring the reference repo's synthetic-receipt handling.
- No ledger file, or ledger with no matching receipt row → a completion claim is blocked. The claim check fails CLOSED; extraction errors fail open (the fleet is never bricked).

## The three fixtures (both directions proven, 2026-09-02)

The `done_when` line carries three `cmd:` fixtures; run_asset ANDs them, so the asset is only green when the gate both BLOCKS the bad cases and PASSES the good one. An always-block hook cannot look green here.

| fixture | payload | ledger state | raw hook exit | fixture exit |
|---|---|---|---|---|
| BLOCK 1 | `Write` content `status: DONE` | ledger exists, zero rows | 2 | 0 (asserts `rc -eq 2`) |
| BLOCK 2 | content `done: true` | receipt row planted, evidence file absent (synthetic) | 2 | 0 (asserts `rc -eq 2`) |
| PASS | content `status: DONE` | receipt row with `observation` + evidence file on disk | 0 | 0 (asserts `rc -eq 0`) |

Observed block message (fixture 1, stderr, verbatim):

```
wm-commit-gate: BLOCKED — completion claim with no observation-backed receipt row (session 'wm-gate-fixture').
  ledger: /var/folders/.../T//wm-gate-red-46908/ledger.jsonl
  A DONE write requires a harness-committed row:
  {"session_id":"<run>","receipt":"r-<n>","observation":"<what the environment showed>","evidence":"<path that exists and proves it>"}
  Model-facing path: write the state change as a proposal ("proposed": true) and let the checker commit it on real observation.
```

Negative controls also run green: empty payload → 0; `status: IN_PROGRESS` content → 0; `proposed: true` claim → 0; claim + nonexistent ledger + no session → 2.

## Why this shape is the right one

- It sits beside `guard-dangerous-commands.sh` and `guard-secret-write.sh` as a third deterministic deny guard, but this one guards a *state transition*, not an I/O pattern — the first asset in the estate that blocks a completion claim in-turn.
- The evidence-path-exists check is RIG's ProofPacket discipline imported into the ledger: a receipt that names no real artifact buys nothing.
- Plantable failure for harness gates: gate `mh-01`-style 3.3 red-path on any DONE-claiming session is now expressible as this hook exiting 2.

## Ceiling and wiring status (honest)

- Inherited Recuris ceiling: the checker is only as good as its external evidence. The hook cannot authenticate **who** wrote a ledger row — an agent with shell write to the ledger could forge a row and create its evidence file. The `evidence`-exists check raises the cost (the claim must at least name a real artifact); writer identity stays a harness-kernel concern outside any PreToolUse hook.
- Wiring this hook into any harness settings file is a **Gate-D action staged separately** — the hook currently ships unwired. Suggested matcher: `Write|Edit|MultiEdit|Bash`.
- Session-id matching uses `grep -E` after sanitizing the id to `[A-Za-z0-9._-]`; a `.` inside an id is a regex metachar and can over-match one character (theoretical false-pass only, never a false-block).
