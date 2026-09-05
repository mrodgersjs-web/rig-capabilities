---
name: great-hA-01-code-review
lane: code-engineering
exemplar_of: hA-01-code-review.yaml
description: >-
  A commit-range review that captures baseline and static evidence, stops on secrets, anchors every finding, and issues one schema-valid verdict with a rebuttal path.
---

# hA-01 code review — evidence before verdict

## Input

Review immutable range `4d2a910...8a7f1ce` for the checkout service. Scope is `src/checkout/**` and its tests; generated lockfile churn is explicitly excluded. The preamble records the startup phrase, coordinate, and `H_codereview(diff_scope, gates, verdict, improvement)` tuple before opening the diff.

## Output

The session runs and records the harness's concrete gates:

```console
$ git rev-parse 4d2a910 8a7f1ce
4d2a910...
8a7f1ce...
$ git diff --stat 4d2a910...8a7f1ce > .rig/review/diff-stat.txt
$ gitleaks detect --source . --no-git --report-format json --report-path .rig/review/gitleaks.json
Finding: 0
```

`.rig/review/findings.md` uses `SEV | path:line | problem | suggested fix`; `.rig/review/verdict.md` declares exactly `approve-with-nits`, includes baseline/static exit codes, and records `no response in window 24h` under Rebuttals.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-01-code-review | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-01-CODE-REVIEW" and any(.goal.gates[]; .id == "2.1" and .failure_tier == "stop")'
true
```

The review cannot emit an approval when baseline tests are red, when a secret stop gate fires, or when a blocker/major finding remains outside the verdict's blocking list.
