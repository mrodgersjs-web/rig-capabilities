---
name: great-36h-gtm-sprint
lane: revenue-gtm
source: canonical-curated
exemplar_of: 36h-gtm-sprint
description: "Reference exemplar for a bounded six-outcome GTM sprint whose staged work, proof counters, blocklist checks, and closeout remain independently inspectable."
---

# 36-hour GTM sprint closeout

## Input

Run one cycle against an active sprint goal and state the current outcome O1-O6. For the pipeline lane, count staged packets, require `gate_d_approved: false`, and quarantine any blocked prospect. For the department lane, verify the fleet doctor and GBrain health before claiming progress.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/36h-gtm-sprint.md
$ cat outbound/calls/2026-07-0{6,7,8}.json | jq '.calls | length'
$ rig-department-pai doctor --format json
$ curl http://localhost:3131/health
```

## Output

The loop contract validates, and the cycle proof names its cycle number, one applied upgrade, counters, blocklist result, and the artifact paths behind every count. Prepared outreach and ads stay dormant; the report distinguishes staged touches from sent touches. At closeout, the goal proof compares all six outcomes with targets, records final proof hashes and incidents, and changes goal status only after the closeout artifact is sealed.

## Acceptance

- The termination command exits 0, the doctor reports PASS, and GBrain returns HTTP 200.
- O1 packets remain unarmed and contain zero blocked prospects.
- Every claimed outcome count resolves to its JSON or proof packet.
- Operator `EXTEND`, `PAUSE`, and `STOP` are honored; no automatic send, spend, or public exposure occurs.
