---
name: capabilities-dispatch-verify
description: Adjudicate a dispatcher handoff packet offline — schema lock, stdout hashes, rotating canary, red-team decoys — and name the verdict; only the full cross-family ladder may ever say PASS.
argument-hint: "PACKET [--offline] [--verify --checkout DIR --verifier-family F]"
allowed-tools: Read, Bash
category: meta
outcome: "meta: a claim is admitted by re-execution in a clean tree, not by the confidence of the agent that made it — and an honest non-zero is evidence, not failure"
done_when:
  - file:capabilities/commands/capabilities-dispatch-verify.md
  - grep:capabilities/commands/capabilities-dispatch-verify.md:SUBMITTED_FOR_VERIFICATION
  - cmd:./bin/rig-capabilities dispatch-verify --packet tests/fixtures/fable2031/handoff-fabricated.json --offline; test $? -eq 2
  - cmd:./bin/rig-capabilities dispatch-verify tests/fixtures/fable2031/handoff-phantom.json; test $? -eq 2
  - cmd:./bin/rig-capabilities dispatch-verify tests/fixtures/fable2031/handoff-tampered.json; test $? -eq 2
  - cmd:./bin/rig-capabilities dispatch-verify tests/fixtures/fable2031/handoff-honest.json --offline; test $? -eq 3
great_example: capabilities/commands/capabilities-dispatch-verify.md
acl: public
quality_floor: 0.7
---

# capabilities-dispatch-verify

The admission node for dispatched work: `rig_capabilities.dispatcher.admit` over a handoff packet
(schema `rig.dispatch.handoff.v1`). Exit codes: **0** PASS (full ladder only), **2** FABRICATED or
ISOLATION_BREACH, **3** PREFILTER_CLEAR, **1** BLOCKED/FAIL. Verdicts are `PASS`, `FAIL`, `BLOCKED`,
`FABRICATED`, `ISOLATION_BREACH`, `PREFILTER_CLEAR` — nothing else, never a bare "looks fine". Exit 3
is deliberately not 0: `estage` scores a non-zero exit as not-passed, so a rung that re-executed
nothing cannot be mis-read as a verified green.

1. Offline prefilter (the default; `--offline` is an explicit no-op):
   `./bin/rig-capabilities dispatch-verify <packet.json>` — schema lock, stdout/file sha256 hashes,
   rotating-canary evaluation. It finishes inside the 15 s `cmd:` budget and never re-executes.
2. An honest packet says `SUBMITTED_FOR_VERIFICATION` and never certifies itself: a missing or
   altered claim is `claim_locked_violation` → BLOCKED; canary reported green, a phantom canary,
   or `tests.failed == 0` is FABRICATED — the canary's truthful non-zero is the admission evidence.
3. Offline never answers PASS. It answers `PREFILTER_CLEAR` (exit 3): nothing was refuted, nothing
   was verified. The clean verdict is the full ladder only:
   `--verify --checkout <dir>` where the tree was materialised at the claimed commit with
   `git -C <repo> archive <sha> | tar -x -C <tmpdir>` — never a clone, never a worktree — replayed by
   a verifier whose `--verifier-family` differs from the `--dispatcher-family`; same family is
   BLOCKED as `same_family_collusion`, and divergence in exit code or stdout hash is FABRICATED.
4. Red team is permanent regression: the decoys under `tests/fixtures/fable2031/redteam/` and the
   fabricated / phantom / tampered / isolation packets must keep going RED. A decoy that escapes
   detection halts dispatch until the detector is repaired — 2-of-3 caught is a red gate.
5. Raw dispatcher logs live under `~/.rig/proof/fable2031/dispatch/<task>/`, never in the tracked
   checkout; fabrication events append to the ledger, and the sealed packet chain is per task.

A truthful canary non-zero is never fed to the TAC close-gate: `$TAC close-gate check` is a
deterministic prefilter over production command records only (canary records are structurally
excluded from `normalize_records`) and it emits GREEN/RED, never PASS. The verdict ladder is
prefilter → `admit` → and above all of it, Sentinel Prime holds fleet termination authority and is
specification-only today, so fleet status stays BLOCKED_PENDING_SENTINEL even on a task PASS. The
read-only `capabilities_dispatch_verify` MCP tool is deliberately absent from `done_when`: `mcp:`
parses as a form but is only runnable when the handler answers `{}` without raising, while every
check above is a `cmd:` that runs now.
