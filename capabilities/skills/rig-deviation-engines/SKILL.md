---
name: rig-deviation-engines
description: "The 40 RIG deviation engines — 20 cognitive, 10 nature, 10 physics — with the σ ladder (±20σ cognitive/nature, ±30σ physics), Robust-MAD-Z scoring, the RIG-L composite and the physics-first short-circuit rule. Use when asked to audit or score an artifact, run a named engine (GRAVITON, ANCHOR, COLLIDER, KELVIN, ...), find which gate is blocking a draft, or explain what a σ score means. Pointer skill: the implementation lives in the rig-lattice-system payload."
allowed-tools: Bash Read Grep
owner: rig-intelligence
domain: Agent engineering / artifact scrutineering
status: Stable
verified_by: jake
verified_on: 2026-09-02
acl: public
relates_to: rig-lattice-system, rig-idea-generator
outcome: "agent-engineering: an artifact's quality is a per-engine σ score against a calibrated baseline with a named blocking gate, not an adjective the author chose for their own work"
done_when:
  - grep:capabilities/skills/rig-lattice-system/rig_lattice/core/registry.py:CollisionCollider
  - cmd:capabilities/skills/rig-lattice-system/bin/rig-lattice engines --json | python3 -c "import json,sys; e=json.load(sys.stdin); assert len(e)==40, len(e); assert sum(1 for x in e if x['layer']=='cognitive')==20; assert sum(1 for x in e if x['layer']=='nature')==10; assert sum(1 for x in e if x['layer']=='physics')==10; assert all(x['is_gate'] for x in e if x['layer']=='physics')"
  - cmd:python3 -c "import sys; sys.path.insert(0,'capabilities/skills/rig-lattice-system'); from rig_lattice.engine_aliases import resolve_codename as r; assert r('GRAVITON')=='e01' and r('COLLIDER')=='e06' and r('ZEROPOINT')=='e40'"
  - cmd:python3 capabilities/skills/rig-lattice-system/ --check
great_example: examples/great/agent-engineering/rig-deviation-engines.md
quality_floor: 0.7
---

# RIG Deviation Engines

40 engines. Three layers. One composite verdict.

This skill is a **pointer**: it carries the roster and the invocation
contract. The implementation — registry, criteria packs, σ ladder, auditor —
is the `rig-lattice-system` payload at
`capabilities/skills/rig-lattice-system/`.

## activation

Fires on: "audit this", "score this artifact", "run the engines", "what's
blocking this draft", "run GRAVITON / ANCHOR / COLLIDER / <codename>",
"what does +12σ mean", "why is this a HARD_BLOCK".

## instruction

Run `rig-lattice audit <path>` and read the verdict, not the prose. Each engine
returns a σ deviation from a calibrated 10-sample baseline via Robust-MAD-Z;
the 10 physics engines are **gates** — any one of them at `HARD_BLOCK` blocks
the artifact regardless of how well the other 30 scored. That is the
physics-first short-circuit rule: check the gates before spending effort on
the scoring layer. Every engine below threshold must leave the session with
either a patch or a named reason; "close enough" is not a disposition.

## applies_when

```yaml
env: any POSIX shell; no network for the deterministic path
runtime: python3 >= 3.11
deps: stdlib only (the audit path reads compiled JSON criteria)
params:
  artifact: a file path or '-' for stdin
  engines: optional list of slugs to limit the run
  llm: opt-in flag; only the llm_judge questions call out
budget:
  A1: $0.00   # the deterministic audit path
  A2: $0.10
  A3: $0.50
  A4: $0.00
scale: 44 criteria packs per artifact, seconds per run
```

## permissions

Bash Read Grep

## flow

1. `rig-lattice audit <path> --json` → per-engine σ, status, RIG-L, BDF.
2. Read the physics layer first: any `HARD_BLOCK` is the whole verdict.
3. For each engine below threshold, take the failed-required question ids —
   they name the exact criterion that failed, with the evidence quote.
4. Patch the artifact, or record the named reason the criterion does not apply.
5. Re-audit. The σ delta is the proof the patch worked.

## done_when

- `rig-lattice engines --json` reports 40 engines split 20/10/10
- every physics engine reports `is_gate: true`
- the alias table resolves every documented codename to its engine id
- a re-audit after a patch shows a σ change on the engine that was patched

## out_of_scope

- **Changing thresholds to pass.** The calibration ladder in
  `rig_lattice/calibration.yaml` is the contract; moving a threshold to clear a
  gate is the failure this skill exists to prevent.
- **Implementing engines here.** This skill holds no code. Edits go to
  `rig-lattice-system`.
- **The `llm_judge` path by default.** It is opt-in via `--llm` and needs
  `RIG_LATTICE_LLM_URL`; the 40-engine deterministic score does not.

## The σ ladder

| layer | count | range | role |
|---|---|---|---|
| cognitive | 20 | ±20σ | output scoring |
| nature | 10 | ±20σ | process scoring |
| physics | 10 | ±30σ | **gates** — one HARD_BLOCK blocks the artifact |

`RIG-L` is the composite; `BDF` is the deviation-from-floor aggregate.
`hard_blocks` counts the physics gates tripped.

## Roster

Codenames are what the ~40 `rig-<codename>` skills and the Alfred pipeline
use. Machine-readable twin: `rig_lattice/engine_aliases.py`.

### Cognitive (01–20, output, ±20σ, threshold +3.0σ)

| id | codename | slug | registry name |
|---|---|---|---|
| e01 | GRAVITON | gravity_escape | GravityEscape |
| e02 | ANCHOR | reality_anchor | RealityAnchor |
| e03 | XRAY | feynman_xray | FeynmanXRay |
| e04 | FORGE | mechanism_furnace | MechanismFurnace |
| e05 | BREAKER | rupture | RuptureEngine |
| e06 | COLLIDER | frame_collision | CollisionCollider |
| e07 | VOLT | voltage | VoltageReactor |
| e08 | DARWIN | darwinian_selection | EvolutionaryMemoryFlywheel |
| e09 | ECHO | memory_residue | MemoryResidue |
| e10 | HORIZON | temporal_horizon_integrity | TemporalHorizonIntegrity |
| e11 | SOVEREIGN | autonomy_calibration | AutonomyCalibration |
| e12 | SURPRISE | predictive_surprise | PredictiveErrorCalibration |
| e13 | AntiSlopAuditor | anti_slop_auditor | AntiSlopAuditor |
| e14 | GLYPH | kolmogorov_originality | SpecificityGate |
| e15 | WITNESS | hermeneutic_density | SourcePerClaim |
| e16 | FalsificationPrereg | falsification_prereg | FalsificationPrereg |
| e17 | REBOUND | opponent_process | DissentRecorder |
| e18 | BAYES | bayesian_calibration | BrierCalibrator |
| e19 | SHIELD | cognitive_sovereignty | CognitiveSovereignty |
| e20 | CompoundingEdge | compounding_edge | CompoundingEdge |

`e15`'s criteria pack is labelled `WELLSPRING` upstream while the engine is
`SourcePerClaim` (per-claim source weighting = WITNESS). Both codenames
resolve to `e15`; the mislabel is recorded in the payload's PROVENANCE.md.

### Nature (21–30, process, ±20σ)

| id | codename | slug | registry name |
|---|---|---|---|
| e21 | SWARM | pheromone_swarm | AntColonyPheromone |
| e22 | BeeForagingAllocator | bee_foraging | BeeForagingAllocator |
| e23 | SLIME | physarum_prune | SlimeMoldNetwork |
| e24 | CLONAL | clonal_refinement | GeneticDiversityPump |
| e25 | ALBATROSS | levy_flight | ParticleSwarmCohesion |
| e26 | LUMINA | bioluminescent_attraction | FireflySynchronization |
| e27 | COLI | chemotaxis_gradient | ResourceAllocator |
| e28 | HUMPBACK | humpback_spiral | WhaleSpiral |
| e29 | CUCKOO | cuckoo_parasitic | CuckooParasite |
| e30 | REEF | coral_reef_synthesis | CoralReefEvolver |

### Physics (31–40, state, ±30σ, **all gates**)

| id | codename | slug | registry name |
|---|---|---|---|
| e31 | TUNNEL | quantum_tunnel | QuantumTunneling |
| e32 | PAULI | pauli_exclusion | PauliExclusion |
| e33 | CASIMIR | casimir_force | CasimirPressure |
| e34 | PARSEC | fine_structure | FineTuningRatio |
| e35 | HORIZON-GATE | hawking_horizon | HawkingRadiation |
| e36 | LUMEN | speed_of_lumen | SpeedOfLightCausality |
| e37 | KELVIN | absolute_zero | AbsoluteZeroFloor |
| e38 | CRITICAL | critical_phase | PhaseTransition |
| e39 | BELL | bell_entanglement | BellEntanglement |
| e40 | ZEROPOINT | vacuum_zeropoint | VacuumFluctuation |

## Invocations

```bash
SKILL=capabilities/skills/rig-lattice-system

# full 40-engine audit
$SKILL/bin/rig-lattice audit draft.md --json

# one engine by slug
$SKILL/bin/rig-lattice audit draft.md --engines gravity_escape --json

# the roster
$SKILL/bin/rig-lattice engines

# codename -> engine id
python3 -c "import sys; sys.path.insert(0,'$SKILL'); \
  from rig_lattice.engine_aliases import resolve_codename; \
  print(resolve_codename('COLLIDER'))"

# the five rigor amplifiers (DES²)
$SKILL/bin/rig-lattice des2 draft.md

# deviation patch pipeline, offline and deterministic
RIG_DV_OFFLINE=1 $SKILL/bin/rig-lattice deviate draft.md --sigma 20
```
