---
name: great-coding-harness
lane: agent-engineering
source: canonical-curated
exemplar_of: coding-harness
description: "Reference exemplar for a minimal coding change proved by types, behavior, security review, build output, an honest diff, and a sealed session record."
---

# Coding loop: fix a parser boundary

## Input

Lock the GL-BI objective and repository scope, then change the shared parser at the root cause. Add a behavior-level regression for the malformed boundary, preserve explicit types, and keep unrelated formatting out of the diff.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/coding-harness.md
$ python -m py_compile path/to/changed_python_file.py
$ git diff
```

## Output

The loop contract and project compile step exit 0. The regression fails against the old behavior and passes after the fix; the existing focused suite remains green. The diff shows only necessary imports and logic, no secret-shaped values, no unparameterized shell or SQL input, and an initialization/error path that works without state from a prior run. The proof packet records changed files, diff stats, test and build outputs, gate evidence, verdict, and SHA-256 proof hash.

## Acceptance

- The termination and compile commands exit 0, and the focused regression passes.
- The actual diff matches the stated file and line counts and has been reviewed in full.
- No deploy, push, merge, or irreversible migration is performed without typed Gate-D approval.
- A failed build, security scan, or required test blocks completion rather than being listed as a warning.
