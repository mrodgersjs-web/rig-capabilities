---
name: bad-missing-three
description: Bad fixture — the DONE-TEST case: activation, applies_when and permissions are all missing; the validator must exit 1 naming each.
instruction: >-
  diagnose the dependency conflict from the resolver error and resolve it with the
  minimal version change, then prove the post-state by re-running the failing suite
flow:
  - reproduce the failure and capture the resolver error verbatim
  - apply the minimal version change
  - re-run the failing suite to prove the post-state
done_when:
  - cmd:test -f examples/fixtures/skill-contract/bad/missing_three.md
out_of_scope:
  - repos without a dependency lockfile
---

# bad-missing-three

The matrix DONE-TEST asset: an indexed asset here is loadable today with no
activation predicate, no declared boundary conditions, and no permission
manifest. The validator must name `activation`, `applies_when` and `permissions`
in its findings for this file.
