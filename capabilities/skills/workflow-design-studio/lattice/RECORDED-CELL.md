# Recorded lattice cell — Workflow Design Studio (recorded BEFORE build)

Recorded 2026-10-26 by Jordan Jr (AI Engineering) under Jake's conductor, before any file was built.
Tool: `capabilities/skills/rig-lattice-system/bin/rig-lattice` (rig-capabilities checkout).

## Route

```json
{
  "intent": "workflow design studio: deterministic compiler from a plain-language agentic workflow registry entry to Aside routine, grokbot behavior, and Jake loop draft artifacts",
  "cell_id": "L4-D3-A1-I1",
  "primary_coordinate": "L4-D3-A1",
  "level": "L4",
  "diamond": "D3",
  "mode": "A1",
  "step": "I1",
  "archetype": "A1.1",
  "budget_usd": 1.0,
  "deterministic": false,
  "rationale": "diamond D3 (owns: feedback loops); complexity score 6 -> L6; routing default A3 (heuristic, unscored)"
}
```

## Recomputed BMS context (why the build is A1, overriding the unscored A3 heuristic)

```json
{
  "confidence": 0.89,
  "mode": "A1",
  "mode_name": "PYTHON_ONLY",
  "threshold": ">=0.75",
  "cost_band": "$0.001",
  "budget_usd": 0.001,
  "approval": "conditional",
  "deterministic": true,
  "model_in_decision_path": false,
  "approval_required": false,
  "level": "L4",
  "raw": 0.93,
  "adjustments": {"past_failure": -0.0, "data_volume": -0.04, "altitude": 0.0}
}
```

Inputs: failure_cost=0.1 (drafts only, nothing outward), reversibility=0.95 (draft files, delete to revert),
mechanism_clarity=0.95 (pure template compiler, no model in the decision path), past_failure_rate=0.0 (new
component), data_volume=0.1 (three small artifact families), level=L4 (compiler + schema + one pilot).

**Canonical cell for this build: `L4-D3-A1-I1`, BMS A1 PYTHON_ONLY (0.89 >= 0.75), deterministic.**
The compiler is code only. Any future step that puts a model in the decision path (e.g. free-text
normalization) is a separate, explicitly labeled A2 step and is NOT certified here (A2-A4 certifier blocked).

Cell contract (`rig-lattice lattice cell L4-D3-A1-I1 --json`): diamond 3_Nature (feedback loops, cycles,
regeneration, resilience, behavior patterns), bms threshold >=0.75, escalation policy UNKNOWN_OR_LOW_CONFIDENCE.
