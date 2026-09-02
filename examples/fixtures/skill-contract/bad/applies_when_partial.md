---
name: bad-applies-when-partial
description: Bad fixture — applies_when is a mapping but drops the runtime and budget boundary fields. Verdict: applies_when MALFORMED.
activation: >-
  a dependency-related build failure is detected in the repo the agent is working in
instruction: >-
  diagnose the dependency conflict from the resolver error and resolve it with the
  minimal version change, then prove the post-state by re-running the failing suite
applies_when:
  env: darwin arm64 developer workstation
  deps: pip plus a v2 lockfile at the repo root
  params: resolver pinned to the lockfile parser shipped with this repo
  scale: one package repo under 5000 source files
permissions:
  - Read
  - Bash(pytest *)
flow:
  - reproduce the failure and capture the resolver error verbatim
  - apply the minimal version change
  - re-run the failing suite to prove the post-state
done_when:
  - cmd:test -f examples/fixtures/skill-contract/bad/applies_when_partial.md
out_of_scope:
  - repos without a dependency lockfile
---

# bad-applies-when-partial

The compression leak, in its most plausible form: the author declared SOME
boundaries and silently dropped the runtime and the budget. A skill run outside
the tuned runtime or past the budget is exactly where environment-mismatch and
excessive-procedure failures come from (arXiv:2608.11888). Partial declarations
must not read as complete ones.
