---
name: great-mh-03-agent-composition-session
lane: agent-engineering
source: canonical-curated
exemplar_of: mh-03-agent-composition-session
description: "Reference exemplar for composing an agent only when every capability, skill gate, harness coordinate, estimator, and memory surface resolves."
---

# Agent composition: evidence triage operator

## Input

Compose `evidence-triage-operator` from a declared capability list, one governing harness, bounded coordinates, and the four memory surfaces: record, retrieve, propose, and predict. Reject the manifest if any capability is silently dropped or if two skills overlap without precedence.

```console
$ ./bin/rig-capabilities goal-spec --stem mh-03-agent-composition-session
$ python3 ~/Developer/needle-haystack/artifacts/meta/mathexec_substrate.py self-test
```

## Output

The goal spec resolves with the canonical composition gates. The session writes `resolution.txt`, `cert-check.txt`, `harness-bind.txt`, `coords.txt`, `memory-coverage.txt`, and a final traceability join. The agent manifest names one installed harness, a supported estimator such as `certified_z`, only existing paths, and no placeholder tokens. A round-tripped `agent_composed` event records the exact role, skill count, harness id, and `traceability=1.0`.

## Acceptance

- Both commands exit 0 and MathExec reports `SELF-TEST PASS`.
- Declared capability count equals the traceability-join row count, with zero unresolved columns.
- Every skill has a done-test and planted-failure fixture.
- Agent and harness coordinates form valid subsets; partial composition is refused rather than shipped.
