---
name: great-hA-02-code-refactor
lane: code-engineering
exemplar_of: hA-02-code-refactor.yaml
description: >-
  A behavior-preserving module extraction conducted as one refactoring pattern per pass, with characterization, API-surface, parity, and rollback evidence.
---

# hA-02 code refactor — shape changes, behavior does not

## Input

Extract invoice formatting from `billing/render.py` without changing exported symbols, output bytes, error messages, or side-effect order. Before edits, pin the file list and behavior claim, record `H_refactor(behavior_lock, transform_steps, parity_proof, improvement)`, and run the repository's existing pytest convention.

## Output

```console
$ pytest -q | tee .rig/refactor/baseline.txt
184 passed
$ python -m pydoc billing.render > .rig/refactor/api-surface-before.txt
$ pytest -q
184 passed
$ python -m pydoc billing.render > .rig/refactor/api-surface-after.txt
$ diff .rig/refactor/api-surface-before.txt .rig/refactor/api-surface-after.txt
```

The characterization-test commit precedes the extraction commit. `.rig/refactor/parity-runs.txt` has one `PASS` row per commit SHA; `transforms.log` names only “extract function”; `summary.md` records the risk register and rollback range. An empty `diff` is affirmative API parity evidence.

## Acceptance

```console
$ ./bin/rig-capabilities goal-spec --stem hA-02-code-refactor | jq -e '.verdict == "OK" and (.provenance.stale | not) and .goal.id == "GL-HA-02-CODE-REFACTOR" and any(.goal.gates[]; .id == "3.4" and .required == true)'
true
```

A failing parity run forces immediate revert of that single pass; it is never explained away as refactor noise.
