---
name: great-hA-06-code-perf-audit
lane: security-review
exemplar_of: hA-06-code-perf-audit.yaml
description: >-
  A profile-led latency audit with stable baseline runs, one optimization per measured delta, and explicit memory and cold-start guardrails.
---

# hA-06 performance audit — the claim is the ratio

## Input

Audit `GET /orders` p95 latency at 50 concurrent clients over a fixed 100k-order dataset. Budget is `p95 <= 400 ms`. Record architecture, CPU count, seed data, load, and warmup before modifying code.

## Output

```console
$ hyperfine --warmup 3 --runs 10 '.rig/perf/bench/orders.sh' > .rig/perf/baseline-runs.txt
$ py-spy record -o .rig/perf/profiles/orders.svg -- python -m app.benchmark_orders
$ jq . .rig/perf/baseline.json >/dev/null
```

The two baseline runs differ by 2.1%. The profile ranks an N+1 query at 61% self-time, row decoding at 18%, and serialization at 9%. One eager-load change is applied and measured alone: `p95 812 ms -> 341 ms = 2.38x`. `guardrail-check.txt` shows memory +4.2% and cold start +1.1%, both inside the 10% gate.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-06-code-perf-audit | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-06-CODE-PERF-AUDIT" and any(.goal.gates[]; .id == "3.3" and .required == true)'
true
```

`REPORT.md` cites the nonempty profile and exact benchmark command. No speed claim is accepted when the harness, environment, dataset, or guardrail comparison changed.
