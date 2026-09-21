---
name: rig-typesafe-verifier
description: >-
  Use before trusting an agent's factual claims, citations, file or URL references,
  completion claims, or semantic tool decisions in OMP and Orca sessions. Run
  deterministic evidence checks first, then use the TypeSafe verifier only as an
  advisory risk signal. Trigger on hallucination checks, claim verification,
  citation verification, proof review, completion review, and evidence-gated output.
license: MIT
---

# RIG TypeSafe verifier

Jev is an advisory semantic verifier, not proof and not an execution authority.

## Required order

1. Verify deterministic facts with the owning tool. Use LSP for symbols, real commands for behavior, exact source lookup for citations, and runtime checks for completion.
2. Build a bounded state from the user request, the candidate response, and only the evidence needed to judge it. Remove secrets and private material that does not need to leave the machine.
3. Use the `typesafe_verify` tool only after the user approves the external call. The tool sends the supplied text to `api.typesafe.ai`.
4. Read every raw probability. Treat `review`, `uncertain`, and `unavailable` as non-pass signals. A `pass` is still advisory and cannot replace deterministic proof.
5. Keep Gate-D, real-path verification, tests, and ProofPackets authoritative. Jev never approves an outward action or certifies its own result.

## Automatic OMP shadow mode

The OMP extension runs in shadow mode under Gate-D `gd_1789593625550`: a bounded, secret-redacted, advisory-only export of the latest turn. Console balance was $5.00 at 2026-09-17T00:10Z and is not checked per-call; the local ledger is the containment ceiling, not a balance check. Shadow mode checks the final main-session response, stores only hashes and probabilities in the session receipt, and warns on risk. It never blocks or forces a continuation.

Automatic checks have two independent ceilings. Each OMP process stops after 25 calls by default (`RIG_TYPESAFE_MAX_SHADOW_CALLS`, clamped to 0-100). All direct and Orca-launched OMP processes share an owner-token file lock and a daily ledger under `~/.rig/typesafe-verifier/state`. The lock is removed only by its PID/token owner; a stale lock is reclaimed only after its recorded PID is confirmed dead. Corrupt or busy lock and quota state fail closed without an API call.

Each attempt reserves the full 32,000-token request ceiling at the configured input price. At the default `$0.042` per million input tokens, that is `$0.001344` per attempt. Failed calls remain reserved deliberately; the ledger therefore overstates rather than understates possible spend. The shared defaults stop at 100 attempts or `$0.10` reserved cost, whichever comes first (`RIG_TYPESAFE_DAILY_MAX_CALLS`, `RIG_TYPESAFE_DAILY_BUDGET_USD`). The receipt records actual input tokens when TypeSafe returns them. Reaching any ceiling records a budget verdict and makes no network call.

Enforcement is intentionally absent. A safe enforcement loop must prove RED, revise, re-run verification, and reach PASS under a bounded retry limit before it may ship.

## Output contract

Report:

- resolved Jev model version
- all five risk probabilities
- advisory verdict
- deterministic evidence that still governs the claim
- any missing evidence or privacy boundary
