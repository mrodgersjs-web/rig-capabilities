---
name: great-build-out-harness
lane: design-ux
source: canonical-curated
exemplar_of: build-out-harness
description: "Reference exemplar for moving a feature through prerequisite, build, runtime verification, system connection, and unattended walk-away evidence without a reality gap."
---

# Build-out: health summary component

## Input

Lock an active goal, cycle number, target, phase, and workspace. Name the exact build and run commands, expected artifacts, upstream health source, downstream consumer, and rollback path before BUILD begins.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/build-out-harness.md
$ curl -s http://localhost:<port>/health
$ grep -c "FATAL\|PANIC\|SIGKILL" ~/.rig/logs/<module>.log
```

## Output

The loop definition validates. A cycle proof captures the exact build command, exit code, artifact list, actual diff statistics, runtime response, tests, upstream/downstream checks, passthrough hash comparison, and graceful behavior when the upstream is unavailable. The claim-to-artifact delta stays within 20%. The walk-away record contains 24 hourly health entries, zero crashes, no data loss, and RSS drift within 20% before marking `walkaway_passed: true`.

## Acceptance

- The termination command exits 0 and the health response has the expected schema.
- BUILD output exists and VERIFY independently exercises it; CONNECT proves both sides of the data flow.
- Crash count is `0`; otherwise walk-away restarts from T+0.
- Missing artifacts, mismatched claims, or corruption halt the cycle instead of being summarized as success.
