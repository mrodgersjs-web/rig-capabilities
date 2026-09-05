---
name: great-autonomous-operation
lane: agent-engineering
source: canonical-curated
exemplar_of: autonomous-operation
description: "Reference exemplar for an unattended run with measured liveness, expiring authority, content binding, append-only evidence, and stop gates that the run cannot clear itself."
---

# Autonomous operation: five-day engagement window

## Input

Declare the daemon, time-boxed grant, per-batch payload digest, telemetry ledger, named healers, and candidate-only improvement path. Start from the ledger's actual baseline, including zero, and compute grant expiry from data rather than code.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/autonomous-operation.md
```

## Output

The loop contract validates. Operational evidence includes two cadence-correct ticks, a supervisor restart that preserves the cycle counter, and bidirectional kill-switch proof: missing kill file yields HALT, restoration yields OK. Backdated authority yields DENY, while a valid grant still refuses an unreviewed digest. Placeholder payloads are refused, blocklist hits are quarantined with audit rows, and a dead provider produces no retry storm. Reported action totals exactly equal append-only ledger rows.

## Acceptance

- The command exits 0.
- No stop-tier violation occurs and no capability survives grant expiry.
- Each claimed action has one resolvable ledger row; a PID or launch record alone is not liveness.
- Healers are idempotent on a clean system, and improvements land only in the candidate directory, never production.
