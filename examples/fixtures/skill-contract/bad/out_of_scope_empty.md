---
name: bad-out-of-scope-empty
description: Bad fixture — the out_of_scope key is present with no items. Verdict: out_of_scope EMPTY.
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
  - reproduce the failure and capture the resolver error verbatim
  - apply the minimal version change
  - re-run the failing suite to prove the post-state
done_when:
  - cmd:test -f examples/fixtures/skill-contract/bad/out_of_scope_empty.md
out_of_scope: []
---

# bad-out-of-scope-empty

The boundary list is present as a key and empty as a claim — `[]` asserts the
skill has nothing it refuses to do, which no run of finite scope can support.
An empty boundary list is a missing boundary list wearing punctuation.
