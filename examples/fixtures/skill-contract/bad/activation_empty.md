---
name: bad-activation-empty
description: Bad fixture — the activation key is present but carries no value; every other slot is complete. Verdict: activation EMPTY.
activation:
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
  - cmd:test -f examples/fixtures/skill-contract/bad/activation_empty.md
out_of_scope:
  - repos without a dependency lockfile
---

# bad-activation-empty

EMPTY case: `activation:` is written, the value was never filled in. The most
common authoring bug in a template-driven flow, and the one an ABSENT/EMPTY
collapse would misreport as "key not in frontmatter".
