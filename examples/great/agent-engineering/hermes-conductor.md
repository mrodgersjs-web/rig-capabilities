---
name: great-hermes-conductor
lane: agent-engineering
source: canonical-curated
exemplar_of: hermes-conductor
description: "Reference exemplar for a conducted session that selects the right harness, preserves IQRSQPI order, routes specialists, and binds every claim to proof."
---

# Hermes conduction: Factory documentation mission

## Input

Classify a Factory documentation task, state `Hermes conducting`, select the matching BMS mode and RIG Studio, and load the relevant doctrine and expert category. Because the mission touches Factory docs and `.factory/*`, route through the existing Factory adjunct rather than inventing a parallel workflow.

```console
$ python3 scripts/assert_loop_termination.py capabilities/loops/hermes-conductor.md
$ cd "${FACTORY_DOCTRINE_ROOT:-$HOME/Developer/RIG-Factory-Doctrine}" && bash scripts/factory.sh status
```

## Output

The loop contract validates and Factory status is captured. The session trace shows Intent, Question, Research, Solution, Quality, Proof, and Integrate in order. Specialist work is tied to named assignments, state updates carry timestamps, and every meaningful claim cites a command result, source URI, or hash-sealed ProofPacket. The closing record states coordinate, verdict, and next safe action, then appends one concrete capability improvement.

## Acceptance

- Both commands exit 0.
- The chosen harness and Studio match the mission; no IQRSQPI stage is silently skipped.
- Gate failures identify the exact missing evidence and stop at the defined tier.
- Outward artifacts stay dormant without typed approval, and Factory remains additive to—not a replacement for—the goal-loop system.
