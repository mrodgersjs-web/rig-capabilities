---
name: bad-activation-absent
description: Bad fixture — the activation key is not written at all; every other slot is complete. Verdict: activation ABSENT.
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
  - cmd:test -f examples/fixtures/skill-contract/bad/activation_absent.md
out_of_scope:
  - repos without a dependency lockfile
---

# bad-activation-absent

ABSENT case: nobody ever wrote the `activation:` key. The router cannot tell
when this skill may fire. Contrast `activation_empty.md`, where the key was
typed and the value never filled in — a different authoring bug, and the
contract must name it differently.
