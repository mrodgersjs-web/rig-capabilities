---
name: skill-contract-complete
description: Fixture SKILL.md whose six-slot contract and boundary list are complete — the validator must exit 0 on it.
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
  - Bash(pip install *)
  - Bash(pytest *)
flow:
  - reproduce the failure and capture the resolver error verbatim
  - map each conflict to its lockfile entry
  - apply the minimal version change
  - re-run the failing suite to prove the post-state
done_when:
  - cmd:test -f examples/fixtures/skill-contract/complete.md
out_of_scope:
  - repos without a dependency lockfile
  - interpreter or OS-level runtime upgrades
  - monorepos beyond the declared scale
---

# skill-contract-complete

The GREEN fixture for `rig_capabilities.skill_contract`. Every slot of the
six-tuple is filled with the shape its rule requires, and `out_of_scope` names
what the run that produced this skill did NOT cover. The worked example follows
the paper's dependency-failure skill (arXiv:2608.29596, video Kbxg-_CXs78); the
boundary fields follow the lossy-compression finding (arXiv:2608.11888, video
TA5QzGTQU_U).
