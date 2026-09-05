---
name: great-swarm-harness
lane: agent-engineering
source: canonical-curated
exemplar_of: swarm-harness
description: "Reference exemplar for an isolated multi-agent run that proves divergent angles, evidence-backed convergence, calibrated confidence, and preserved disagreement."
---

# Swarm loop: three-angle architecture review

## Input

Lock an active GL-SW goal, one architecture question, and three isolated agents. Assign one agent to failure domains, one to operability, and one to migration risk. Require structured `{claim, evidence, confidence, source}` output and at least one unique claim per agent.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/swarm-harness.md
$ diff "$OUT_A" "$OUT_B"
$ comm -12 "$SORT_A" "$SORT_B" | wc -l
```

## Output

The loop contract validates. Registry evidence shows exactly three responsive, uniquely identified agents with separate state. Pairwise analysis stays below 70% similarity and identifies each agent's unique claim. Every agent contributes at least three sourced claims; high-confidence claims have the required independent support. The conductor writes `swarm-synthesis-<cycle>.md` with consensus, contested, unique, confidence-weighted, and open-question sections instead of flattening disagreement.

## Acceptance

- The termination command exits 0 and all assigned agents reach a terminal result or an explicitly isolated failure.
- No two agents share context, target the same angle, or become a subset of another output.
- Claims above 0.8 have two sources; claims above 0.9 have terminal or log proof.
- Every detected contradiction appears with both positions and evidence; a simple concatenation does not pass synthesis.
