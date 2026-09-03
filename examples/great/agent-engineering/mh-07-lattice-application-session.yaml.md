---
name: great-mh-07-lattice-application-session
lane: agent-engineering
source: canonical-curated
exemplar_of: mh-07-lattice-application-session.yaml
description: Reference exemplar — a session harness whose G1 gate compares log offsets so the coordinate must precede the first edit, whose G5 gate requires a planted defect shown RED then GREEN, and whose 22 compiled gates each carry an executable command
---

# mh-07-lattice-application-session — reference

Canonical asset `mh-07-lattice-application-session.yaml` (harness). Path:
`capabilities/harnesses/mh-07-lattice-application-session.yaml`.

> Applying the lattice to an application is a gated session: a coordinate and
> a BMS result exist before the first edit, the work is attempted A1-first,
> and the artifact leaves with a 40-engine verdict and a sealed ProofPacket
> instead of a claim that it went well.

## What good looks like

Six named gates, each bound to a concrete gate id that survives compilation:

| named | gate | requirement | tier |
|---|---|---|---|
| **G1** | 1.1 | canonical cell id + the `BMSResult` that produced its mode, **before any edit** | halt |
| **G2** | 2.1 | every unit attempted in the A1 band first | halt |
| **G3** | 2.4 | diff inside `BMS_BUDGET_USD[mode]` and the declared scope | halt |
| **G4** | 3.1 | `rig-lattice audit` with zero `HARD_BLOCK` | halt |
| **G5** | 4.1 | a planted defect shown RED, then restored GREEN | halt |
| **G6** | 4.3 | ProofPacket: commands, exit codes, artifact sha256 | halt |

```
$ python3 scripts/compile_harnesses.py compile
OK  mh-07-lattice-application-session.yaml  gates=22 blocking=21 no_proof=0

$ compiled goalspec → goals[0].gates
22 gates, 22 with a command, G1..G6 each matching exactly one gate id
```

## G1 is checked by ordering, not by presence

The weak version of "coordinate before code" asks whether a cell id appears
in the log. This one compares positions:

> assert the log offset of the CELL line is lower than the offset of the first
> EDIT line

A coordinate written after the work is a coordinate reconstructed to fit the
work. Offsets catch that; presence does not.

## G2 makes escalation cost something

```
A1-ATTEMPT: <command>            exit=<code>     # one per unit of work
ESCALATE: A1->A2 after <command> exit=1          # must name a FAILED attempt
```

The gate parses each escalation line, asserts the referenced command appears
in an earlier `A1-ATTEMPT` line, and asserts its exit code is non-zero. "This
felt ambiguous" produces no such line and therefore no escalation.

## G5 is the anti-theater gate

```
1. introduce one deliberate defect into the logic this session wrote
2. run the session's own check          → non-zero exit   (RED)
3. revert the defect
4. run the same check                   → exit 0          (GREEN)
```

Both outputs go in the log and gate 4.2 asserts the planted diff's path is
inside the SCOPE declared at 0.1 — so the defect must be planted in the new
logic, not in some unrelated file where it is cheap to break.

A gate that has never been observed going red is a gate nobody has tested.

## The tier partition is closed-world

```yaml
halt_gates:    [1.1,1.2,1.3, 2.1,2.2,2.3,2.4, 3.1,3.2,3.3, 4.1,4.2,4.3,4.4]
degrade_gates: [5.3]
stop_gates:    [5.1, 5.2]
```

A test asserts set equality between the gates' own `failure_tier` fields and
these lists — no orphans, no unknowns. The two stop gates mark the boundaries
only a human crosses: an outward action with no configured reviewer (5.1), and
a scope change, threshold change, or A4 execution (5.2).

Gate 3.3 is the one that protects the verdict itself:

```
git diff --exit-code -- .../calibration.yaml .../criteria/     # exit 0 required
```

You cannot clear an engine gate by moving its threshold.

## Why it is not a checklist

The RIG delta: a checklist is read and ticked. Every gate here names a command
whose output is the receipt — a regex assertion over the log, a `git diff
--exit-code`, a `shasum -a 256` compared to the packet, an `env -u
RIG_DV_AUTO_APPROVE` probe proving the approval client refuses when no
reviewer is configured. The harness's own `self_improvement` clause closes the
loop the honest way: when a gate fails three times, the check is absorbed into
the payload as a test so the next session inherits it as **code**, not as a
reminder.

Verified: `compile_harnesses.py parse` and `compile` both succeed; 22 gates,
0 without proof; `tests/test_lattice_bundle.py::TestCompiledGoalSpec` asserts
the G1..G6 → gate-id mapping.
