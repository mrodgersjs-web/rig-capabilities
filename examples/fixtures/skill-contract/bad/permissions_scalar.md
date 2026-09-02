---
name: bad-permissions-scalar
description: Bad fixture — permissions carries a comma string instead of a tool list. Verdict: permissions MALFORMED.
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
permissions: Read, Write, Bash, network
flow:
  - reproduce the failure and capture the resolver error verbatim
  - apply the minimal version change
  - re-run the failing suite to prove the post-state
done_when:
  - cmd:test -f examples/fixtures/skill-contract/bad/permissions_scalar.md
out_of_scope:
  - repos without a dependency lockfile
---

# bad-permissions-scalar

MALFORMED case: the P slot exists but as prose, not an enumerable tool list.
A permission manifest nobody can diff against runtime behaviour is the paper's
admitted open problem (arXiv:2608.29596, limitations) — enumerability is the
precondition for any of it, so shape is enforced first.
