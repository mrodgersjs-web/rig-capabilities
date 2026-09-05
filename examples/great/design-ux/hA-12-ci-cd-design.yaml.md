---
name: great-hA-12-ci-cd-design-yaml
lane: design-ux
exemplar_of: hA-12-ci-cd-design.yaml
description: Reference exemplar for a least-privilege, SHA-pinned CI pipeline proven by lint, local execution, and a planted failure path.
---

# hA-12-ci-cd-design.yaml — great example

## Input

Design a GitHub Actions pull-request pipeline whose declared graph is lint → typecheck/test in parallel → build → package → deploy gate. It checks out untrusted PR code, so triggers, cache isolation, permissions, secrets, action pins, timeouts, and concurrency are reviewed before the workflow is enabled.

## Output

The session writes `.rig/cicd/stage-graph.md`, trigger and permissions reviews, pin and secret inventories, `actionlint`/`zizmor` reports, local dry-run output, and expected-versus-actual behavior for an intentional test failure. The live workflow remains disabled.

```console
$ actionlint .github/workflows/ci.yml
# expected: exit 0 and output retained in .rig/cicd/actionlint.txt

$ zizmor .github/workflows/ci.yml
# expected: zero undispositioned security findings

$ act pull_request -W .github/workflows/ci.yml
# expected: the critical path runs locally; a planted failing test stops build/package as specified
```

## Acceptance

- Every third-party `uses:` reference is a full commit SHA with a version comment.
- Top-level permissions begin at `contents: read` or `{}`, and job elevation is justified.
- Cache keys include the lockfile hash and untrusted PR jobs cannot poison main caches.
- Every job has a timeout; concurrency behavior is deliberate; no live dispatch or deployment is triggered.
