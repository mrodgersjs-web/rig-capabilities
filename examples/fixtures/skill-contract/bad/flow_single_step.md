---
name: bad-flow-single-step
description: Bad fixture — flow carries exactly one step. Verdict: flow MALFORMED (one step is not a control flow).
activation: >-
  a dependency-related build failure is detected in the repo the agent is working in
instruction: >-
  diagnose the dependency conflict from the resolver error and resolve it with the
  minimal version change, then prove the post-state by re-running the failing suite
applies_when:
  env: darwin arm64 developer workstation
  runtime: python 3.12 inside the repo virtualenv
  deps: pip plus a v2 lockfile at the repo root
  params: resolver pinned to the lockfile parser shipped with this repo
  budget: 10 minutes wall time and 40k tokens per attempt
  scale: one package repo under 5000 source files
permissions:
  - Read
  - Bash(pytest *)
flow:
  - fix the dependencies
done_when:
  - cmd:test -f examples/fixtures/skill-contract/bad/flow_single_step.md
out_of_scope:
  - repos without a dependency lockfile
---

# bad-flow-single-step

The pi slot names an outcome, not a control flow. A skill is supposed to encode
HOW state moves from pre- to post-state (a transition, not a wish); one step
carries no ordering, so the harness cannot tell where the run can go wrong or
which step the boundary conditions bind.
