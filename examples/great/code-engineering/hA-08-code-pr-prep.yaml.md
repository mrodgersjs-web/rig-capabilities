---
name: great-hA-08-code-pr-prep
lane: code-engineering
exemplar_of: hA-08-code-pr-prep.yaml
description: >-
  A reviewer-ready PR packet built from the exact branch diff, binding self-review, risk flags, test commands, rollout notes, and CI evidence to one HEAD SHA.
---

# hA-08 PR preparation — exact-tree evidence

## Input

Prepare branch `fix/idempotency-key` against `main` for issue `#418`. This session may inspect and package the change, but the push remains an A4 outward action requiring explicit human instruction.

## Output

```console
$ git branch --show-current
fix/idempotency-key
$ git log --oneline origin/main..HEAD > .rig/pr/commits.txt
$ git diff --stat origin/main...HEAD
 6 files changed, 91 insertions(+), 24 deletions(-)
$ git rev-parse HEAD
be1313d...
```

Every changed file appears in `.rig/pr/self-review.md` with per-hunk verdicts. `DESCRIPTION.md` contains summary, file-mapped changes, `Closes #418`, exact test commands from `verify.txt`, and `N/A — no ops surface` for rollout. The risk section points reviewers to the idempotency-store concurrency hunk. Read-only `gh pr checks` output is captured in `ci.txt` only after a PR exists.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-08-code-pr-prep | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-08-CODE-PR-PREP" and any(.goal.gates[]; .id == "4.1" and .failure_tier == "halt")'
true
```

The SHA in `verify.txt` must equal the prepared HEAD. Red CI needs a root-cause note; no push is performed by this preparation exemplar.
