---
name: great-rig-lattice-router
lane: agent-engineering
source: canonical-curated
exemplar_of: rig-lattice-router.md
description: Reference exemplar — a routing sub-agent that returns exactly seven contract keys and nothing else, has no write permission by construction, and reports missing criteria instead of inventing the numbers that would justify a band
---

# rig-lattice-router — reference

Canonical asset `rig-lattice-router.md` (agent). Path:
`capabilities/agents/rig-lattice-router.md`.

> Prose in, coordinate out. Nothing else.

## What good looks like

The whole output surface, fixed at seven keys:

```json
{
  "cell_id": "L3-D2-A2-I1",
  "mode": "A2",
  "archetype": "A2.1",
  "budget_usd": 0.10,
  "approval_required": false,
  "evidence_required": ["measured failure_cost", "a p95 baseline"],
  "next_step": "attempt the deterministic path and record its exit code"
}
```

No `summary`, no `recommendation`, no paragraph explaining the choice. The
CLI's own `rationale` string is the explanation, and it is a byproduct of the
computation rather than a narration of it.

## Two routes, opposite ends of the lattice

```
$ rig-lattice route "memoize a pure lookup helper"
→ L1-D1-A1-I1   A1   budget $0.00   approval_required false   deterministic true

$ rig-lattice route "delete the legacy payments table after backfilling"
→ low reversibility + high failure cost → A3/A4, approval_required true
```

The second route is the one that matters: an irreversible data operation lands
in a band that *requires a human*, and it lands there because
`reversibility` scored low in a formula — not because an agent felt cautious.

## The permission list is the enforcement

```yaml
allowed-tools: Bash Read
```

There is no Write and no Edit. The agent cannot build even if a caller asks it
to, so "it routes; it never builds" is a property of the manifest rather than
an instruction the model may drift from. One `done_when` asserts no file was
created or modified by the agent.

## Refusing to invent the inputs

The failure mode this agent is shaped against: a confidence score with nothing
behind it selects a band that *looks* earned. So when the task text does not
support a criteria estimate, the criteria go into `evidence_required` and the
mode is reported provisional:

> If failure cost, reversibility, or mechanism clarity cannot be read off the
> task description, they go in `evidence_required` and the mode is reported as
> provisional.

An unjustified confidence score is worse than a missing one.

## Escalation is priced, not chosen

| step | what it costs |
|---|---|
| A1 → A2 | a recorded A1 failure **with the failing command's exit code** |
| A2 → A3 | an agent runtime this bundle does not ship — `archetype_runner("A3")` raises |
| A3 → A4 | a human decision path, model-free, mandatory approval |

The A3 rung raising rather than falling back is deliberate: the vendored
source degraded to the A1 code path on ImportError and reported the result as
A3, which is a green that cannot go red.

## Why it is not a planner

The RIG delta: a planning agent returns a plan you must trust. This one
returns a coordinate you can check — the cell id matches a regex, the mode is
reproducible from the criteria by `bms score`, the budget is a table lookup,
and `approval_required` is true for exactly A3 and A4. Every field is
verifiable by a second command, which is why the agent is allowed to be
terse.

Installed to `.claude`, `.codex`, `.hermes` — the three roots the installer
supports for kind `agent`; `.agents` and `.omp` refuse the kind and are
recorded as such rather than reported as installed.

Verified: 5 `done_when` entries, 0 unrunnable; the routed cell id matches
`^L[1-7]-D[1-3]-A[1-4]-(I1|Q1|R|S|Q2|P|I2)$`.
