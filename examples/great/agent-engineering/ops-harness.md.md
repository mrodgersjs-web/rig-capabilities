---
name: great-ops-harness
lane: agent-engineering
source: canonical-curated
exemplar_of: ops-harness
description: "Reference exemplar for a LAN-first rolling operation that proves node health, backup integrity, dry-run safety, and a tested rollback before deployment."
---

# Operations loop: rolling service update

## Input

Lock the active goal, cycle, operator, target nodes, and `deploy` operation. Enumerate all changed artifacts, require healthy LAN routes, create a backup, and name both deploy and rollback verification commands before touching the first node.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/ops-harness.md
$ hostname
$ ping -c 3 -W 2 <node_ip>
$ tar tzf <backup>.tar.gz | wc -l
$ shasum -a 256 <backup>.tar.gz
```

## Output

The loop contract validates. The proof packet records the verified node identity, health responses, private route, backup path/hash/byte count, deployment dry-run, 300-second timeout, rollback dry-run, and post-rollback verification command. Deployment proceeds one node at a time, verifying service health after each. A failed node is quarantined only when the healthy-subset rule permits; WAN fallback, missing backup, or untestable rollback halts the operation.

## Acceptance

- The termination command exits 0; target checks show 0% packet loss and required services healthy.
- The backup is non-empty, lists the expected file count, and has a recorded SHA-256 digest.
- Rollback is tested before deployment and can restore the pre-change state within its bounded timeout.
- No destructive operation runs without the required operator confirmation; every cycle emits `ops-proof-<cycle>.json`.
