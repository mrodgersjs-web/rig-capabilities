# Deviate Engine System (DES) — Canonical Doctrine Card

> **This card is the single source of truth.** Hermes drives. Tenacity loops. Cloud Code executes. The DES is the pressure layer that makes every other RIG OS component honest.

## 0. Mission

The Deviate Engine System (DES) is the **quality-pressure substrate** of RIG OS. It is the single mechanism by which every artifact, mission packet, and skill candidate is forced to escape generic gravity, expose mechanism, survive falsification, and earn a sigma-graded right to be integrated.

This card is the **single source of truth** for Cloud Code to construct the entire DES — every engine, every formula, every gate, every sigma band, every escalation tier, every Hermes hook, every adversarial review path, and the IQRSQPI² amplification overlay — in one autonomous build pass.

```text
DES = 3 Layers × 40 Engines × Robust-MAD-Z × Sigma Ladder × Composite Gates × Hermes Hooks
```

Do not fragment this build. Cloud Code executes the entire spec end-to-end with the Hermes orchestrator + Tenacity /goal loop until every acceptance gate passes. Mirrors the Fioma build pattern: one card → one autonomous run → green `make verify-engines`.

---

## 1. The Complete Engine Matrix

### 1.1 The three true axes

| Axis | Name | Values | Cardinality |
| --- | --- | --- | --- |
| **X** | Layer | Cognitive · Nature · Physics | 3 |
| **Y** | Engine ID within Layer | 01–20 · 21–30 · 31–40 | 40 total |
| **Z** | Target / Sigma Band | OUTPUT ±20σ · PROCESS ±20σ · STATE ±30σ | 3 |

### 1.2 Cell math (canonical)

```text
40 engines × 6 audience tiers × 7 IQRSQPI steps = 1,680 evaluation cells
40 engines × 4 BMS modes (A1–A4)                = 160 dispatch routes
```

Every artifact produced by RIG OS resolves to a (Layer, Engine, Tier, IQRSQPI-step) coordinate and emits a Robust-MAD-Z score + gate verdict.

### 1.3 The three Layers (X-axis)

| Layer | Engines | Target | Band | Role |
| --- | --- | --- | --- | --- |
| **L1 Cognitive** | 01–20 | OUTPUT | ±20σ | Detects whether the artifact escapes generic gravity, exposes mechanism, ruptures the frame, and creates memory residue. |
| **L2 Nature** | 21–30 | PROCESS | ±20σ | Detects whether the *process* that produced the artifact is adaptive, diverse, exploitative-vs-exploratory balanced, and resilient. |
| **L3 Physics** | 31–40 | STATE | ±30σ | **Hard constraints**. Detects whether the system *state* violates physics-derived invariants (tunneling, exclusion, entropy leakage, fine-tuning, causality, vacuum fluctuation). A single L3 fail short-circuits the pipeline. |

### 1.4 The 40 Engines (canonical roster)

**Layer 1 — Cognitive (01–20, target OUTPUT, ±20σ)**

01 Gravity Escape · 02 Reality Anchor · 03 Feynman X-Ray · 04 Mechanism Furnace · 05 Rupture Engine · 06 Collision Collider · 07 Voltage Reactor · 08 Evolutionary Memory Flywheel · 09 Memory Residue · 10 Temporal Horizon Integrity · 11 Autonomy Calibration · 12 Predictive Error Calibration · 13 Anti-Slop Auditor · 14 Specificity Gate · 15 Source-Per-Claim · 16 Falsification Pre-Register · 17 Dissent Recorder · 18 Brier Calibrator · 19 Cognitive Sovereignty · 20 Compounding Edge

**Layer 2 — Nature (21–30, target PROCESS, ±20σ)**

21 Ant Colony Pheromone · 22 Bee Foraging Allocator · 23 Slime Mold Network · 24 Genetic Diversity Pump · 25 Particle Swarm Cohesion · 26 Firefly Synchronization · 27 Resource Allocator (need×trust) · 28 Whale Spiral (WOA) · 29 Cuckoo Parasite · 30 Coral Reef Evolver (CRO-SL)

**Layer 3 — Physics (31–40, target STATE, ±30σ HARD)**

31 Quantum Tunneling · 32 Pauli Exclusion · 33 Casimir Pressure · 34 Fine-Tuning Ratio · 35 Hawking Radiation (information leak) · 36 Speed-of-Light Causality · 37 Absolute Zero Floor · 38 Phase Transition (with hysteresis) · 39 Bell Entanglement (|S| > 2) · 40 Vacuum Fluctuation

### 1.5 Sigma anchors (canonical, shared by all three layers)

| σ | Meaning |
| --- | --- |
| −10 | Extreme inverse / anti-concept; dangerous unless deliberate |
| −8 | World-class restraint OR severe under-indexing |
| −5 | Strong negative deviation, often a hard fail |
| −3 | Below acceptable; usually blocked |
| −1 | Slightly below median |
| 0 | Generic median (default LLM output) |
| +1 | Slightly above median |
| +3 | **Minimum RIG pass** (escaped generic gravity) |
| +5 | RIG signature artifact |
| +8 | Frontier / experimental artifact |
| +10 | Category creation / doctrine artifact |

Physics layer extends the same anchors to **±30σ** as hard state constraints.

### 1.6 Threshold tiers (audience-graded gates)

| Tier | Min σ | Patent Examiner | Doctrine Council | Cost band |
| --- | --- | --- | --- | --- |
| Internal note | +1 | no | no | $0 |
| Internal artifact | +3 | no | no | $0.01 |
| Client artifact | +3 | conditional | no | $0.05 |
| Published artifact | +5 | yes | no | $1 |
| Doctrine artifact | +8 | yes | yes | $10 |
| Civilization artifact | +10 | yes | yes (≤72h) | $50 |

---

## 2. The Core Math Primitives (all formulas implemented)

### 2.1 Robust-MAD-Z (the scoring core)

```text
rawMAD       = median(|score_i − median(scores)|)
RobustMADZ   = 0.6745 · (score − median(baselineScores)) / rawMAD
```

The 0.6745 constant restores standard-normal scale under MAD. **All 40 engines emit RobustMADZ — never raw z-scores, never mean/stdev.** Outliers in the generic-baseline corpus must not contaminate the median.

### 2.2 Sigma score (structural + behavioral blend)

```text
SigmaScore   = 0.3 · structural + 0.7 · behavior
Patent Examiner trigger: SigmaScore ≥ 5σ
```

### 2.3 Escalation ladder (cost-of-review scales with σ)

```text
for |n| ≤ 10:           cost = 2^|n|
for 10 < |n| ≤ 20:      cost = 1024 · 3^(n−10)
for 20 < |n| ≤ 30:      cost = 1024 · 3^10 · 5^(n−20)
```

The ladder enforces that civilization-tier artifacts cost orders of magnitude more to validate than internal notes — exactly as in the Fioma A4 mandatory-approval band.

### 2.4 BDF — Build / Defend / Falsify composite

```text
BDF = intent · |MADZ| · craft · restraint
```

Four positive multipliers. If any factor → 0, the artifact is blocked regardless of headline score.

### 2.5 RIG-L composite (the headline number)

| RIG-L | Meaning |
| --- | --- |
| < 3.0 | Block. Generic, shallow, unsafe, fake-understanding, or non-compounding. |
| 3.0–3.9 | Pass. Proprietary edge exists. Needs strengthening. |
| 4.0–4.9 | Category rupture. Strong enough to publish, ship, test aggressively. |
| 5.0–7.9 | RIG signature. Distinctive, believable, mechanistic, memorable. |
| 8.0–9.9 | Frontier artifact. Hard to copy, high residue, creates new behavior. |
| 10+ | Doctrine artifact. Creates a new frame, vocabulary, category, or OS pattern. |

### 2.6 THRESHOLDS dict (6-tier audience map, used by detonation_gate)

```python
THRESHOLDS = {
  "internal_note":         {"minSigma": 1,  "requiresPatentExaminer": False, "requiresDoctrineCouncil": False},
  "internal_artifact":     {"minSigma": 3,  "requiresPatentExaminer": False, "requiresDoctrineCouncil": False},
  "client":                {"minSigma": 3,  "requiresPatentExaminer": "conditional", "requiresDoctrineCouncil": False},
  "published":             {"minSigma": 5,  "requiresPatentExaminer": True,  "requiresDoctrineCouncil": False},
  "doctrine":              {"minSigma": 8,  "requiresPatentExaminer": True,  "requiresDoctrineCouncil": True},
  "civilization":          {"minSigma": 10, "requiresPatentExaminer": True,  "requiresDoctrineCouncil": True},
}
```

---

## 3. The DES² 25× Amplification Layer (mirrors Fioma's IQRSQPI²)

Standard scoring runs each engine once. **DES² runs a second nested scoring pass inside each of the 40 engines**, gated by amplifier checks. Net result: each engine becomes 5× more rigorous on quality + 5× more rigorous on proof = **25× system strength** when overlaid on Fioma's IQRSQPI loop.

### 3.1 The five amplifiers per engine

| # | Amplifier | What it adds | Multiplier |
| --- | --- | --- | --- |
| 1 | **Mechanism Map** | Causal chain from inputs → output with named mechanisms | 1.5× rigor |
| 2 | **Source-Per-Claim** | Every assertion bound to a structured source URI + hash | 1.4× grounding |
| 3 | **Falsification Check** | Pre-registered conditions that would prove the score wrong | 1.6× robustness |
| 4 | **Anti-Generic Gate** | Specificity threshold ≥80 customer-facing, ≥75 internal | 1.3× precision |
| 5 | **Brier-Calibrated Confidence** | Predicted σ vs actual outcome σ tracking | 1.5× calibration |

Product: 1.5 · 1.4 · 1.6 · 1.3 · 1.5 ≈ **6.55×** per axis (quality and proof axes) → **25×** compoundly when applied per cell, per layer.

### 3.2 The inner amplification loop per engine

```text
A1' — Inner Mechanism:     What is the causal chain producing this score?
A2' — Inner Sources:       Bind every metric input to a URI + hash
A3' — Inner Falsifier:     What pre-registered condition would invalidate this verdict?
A4' — Inner Specificity:   Does the score survive the Anti-Generic Gate?
A5' — Inner Brier:         Compare predicted σ to historical realized σ; recalibrate
```

---

## 4. Composite Gate Logic (the build's central kernel)

Gate ordering is **non-negotiable**: a single physics-state failure short-circuits everything below.

```text
1. Physics State Gates (L3, ±30σ)   → if any BLOCK → short-circuit
2. Cognitive Output Gates (L1, ±20σ) → score & gate
3. Nature Process Gates (L2, ±20σ)   → score & gate
4. Composite RIG-L                   → headline verdict
5. Detonation Gate (tier × patent × council)
```

### 4.1 Reference detonation_gate

```python
def detonation_gate(robust_mad_z, patent_verdict="not_required", tier="client"):
    t = THRESHOLDS[tier]
    if abs(robust_mad_z) < t["minSigma"]:
        return BLOCK(f"Below {t['minSigma']}σ for tier {tier}.")
    if t.get("requiresPatentExaminer") and patent_verdict != "novel":
        return BLOCK("Patent Examiner verdict required.")
    return PASS
```

### 4.2 Hard-block list (banned outputs regardless of engine math)

- Median LLM phrasing ("unlock," "transform," "seamless," "scale effortlessly," "Get Started," "Learn More," "Book a Demo")
- Claims without sources at tier ≥ client
- Mechanism-free strategic recommendations
- Black-box artifacts violating Hawking Radiation gate (InternalVolume > 10·SurfaceArea)
- Artificially silent telemetry violating Vacuum Fluctuation gate
- Coupled-system claims with |BellS| ≤ 2
- Self-reviewed artifacts (Adversarial Reviewer must be independent)

---

## 5. The Engine Archetype Resolver (mirrors Fioma's 28-file archetype tree)

Every engine resolves to exactly one implementation file. The resolver: `resolve_engine(layer, engine_id) → file_path`. All 40 files live under `rig_engines/engines/`.

```text
rig_engines/
├── core/
│   ├── robust_mad_z.py        # 0.6745·(x−median)/rawMAD
│   ├── sigma.py               # structural+behavior blend, Patent trigger
│   ├── escalation.py          # 2^|n| / 3^(n−10) / 5^(n−20) ladder
│   ├── bdf.py                 # intent · |MADZ| · craft · restraint
│   ├── thresholds.py          # 6-tier THRESHOLDS dict
│   ├── rig_l.py               # composite headline
│   └── base.py                # DeviationEngine dataclass
├── engines/
│   ├── cognitive/             # 01–20 (output, ±20σ)
│   │   ├── e01_gravity_escape.py
│   │   ├── e02_reality_anchor.py
│   │   ├── e03_feynman_xray.py
│   │   ├── e04_mechanism_furnace.py
│   │   ├── e05_rupture_engine.py
│   │   ├── e06_collision_collider.py
│   │   ├── e07_voltage_reactor.py
│   │   ├── e08_evolutionary_memory_flywheel.py
│   │   ├── e09_memory_residue.py
│   │   ├── e10_temporal_horizon_integrity.py
│   │   ├── e11_autonomy_calibration.py
│   │   ├── e12_predictive_error_calibration.py
│   │   ├── e13_anti_slop_auditor.py
│   │   ├── e14_specificity_gate.py
│   │   ├── e15_source_per_claim.py
│   │   ├── e16_falsification_prereg.py
│   │   ├── e17_dissent_recorder.py
│   │   ├── e18_brier_calibrator.py
│   │   ├── e19_cognitive_sovereignty.py
│   │   └── e20_compounding_edge.py
│   ├── nature/                # 21–30 (process, ±20σ)
│   │   ├── e21_ant_colony.py
│   │   ├── e22_bee_foraging.py
│   │   ├── e23_slime_mold.py
│   │   ├── e24_genetic_diversity.py
│   │   ├── e25_particle_swarm.py
│   │   ├── e26_firefly_sync.py
│   │   ├── e27_resource_allocator.py
│   │   ├── e28_whale_spiral.py
│   │   ├── e29_cuckoo_parasite.py
│   │   └── e30_coral_reef.py
│   └── physics/               # 31–40 (state, ±30σ HARD)
│       ├── e31_quantum_tunneling.py
│       ├── e32_pauli_exclusion.py
│       ├── e33_casimir_pressure.py
│       ├── e34_fine_tuning.py
│       ├── e35_hawking_radiation.py
│       ├── e36_speed_of_light.py
│       ├── e37_absolute_zero.py
│       ├── e38_phase_transition.py
│       ├── e39_bell_entanglement.py
│       └── e40_vacuum_fluctuation.py
├── pipeline/
│   ├── orchestrator.py        # gate ordering: physics → cognitive → nature → RIG-L
│   ├── baseline.py            # generic-baseline corpus generator + weekly recal cron
│   ├── audit.py               # append-only result-packet writer (UPDATE/DELETE revoked)
│   ├── mutate.py              # skill-candidate promotion based on engine scores
│   └── report.py              # FINAL_REPORT.md emitter
├── adapters/
│   ├── llm.py                 # LiteLLM router for fuzzy-metric scoring
│   ├── embeddings.py          # for collision/distance metrics
│   ├── uqlm.py                # uncertainty quantification
│   └── langsmith.py           # learning-loop hooks
└── hooks/
    ├── hermes_completion_scorer.py
    ├── hermes_circuit_breaker.py
    ├── hermes_adversarial_review.py
    └── hermes_cron.py
```

### 5.1 Reference DeviationEngine base class

```python
from dataclasses import dataclass
from typing import Callable, Sequence
from core.robust_mad_z import robust_mad_z

@dataclass
class DeviationEngine:
    id: int
    name: str
    layer: str                # cognitive | nature | physics
    target: str               # output | process | state
    raw_fn: Callable          # artifact → raw score
    baseline_fn: Callable     # () → list[float] generic baseline
    threshold: float = 3.0
    hard_blocks: Sequence[Callable] = ()

    def score(self, artifact):
        for hb in self.hard_blocks:
            if hb(artifact):
                return {"status": "BLOCK", "reason": hb.__name__}
        raw = self.raw_fn(artifact)
        z   = robust_mad_z(raw, self.baseline_fn())
        return {
            "engine": self.name,
            "raw": raw,
            "madz": z,
            "status": "PASS" if z >= self.threshold else "BLOCK",
        }
```

### 5.2 Example engine formulas (canonical, must be implemented verbatim)

```text
MechanismFurnaceRaw = 0.25·CausalLinkDensity + 0.20·FeedbackLoopClarity
                    + 0.20·ConstraintVisibility + 0.15·FailureModeCoverage
                    + 0.10·OperationalSpecificity + 0.10·Testability
Gate: if MechanismFurnaceMADZ < 3.0 → BLOCK "No mechanism. Only claims."

RuptureRaw = 0.25·AssumptionRemoval + 0.20·CategoryFrameBreak
           + 0.20·OrthodoxyViolation + 0.15·ReframeStrength
           + 0.10·FirstPrinciplesRebuild + 0.10·IrreversibilityOfInsight
Gate: if RuptureMADZ < 3.0 → BLOCK "No rupture. Artifact preserves the old frame."

CollisionColliderRaw = 0.25·DomainDistance + 0.25·StructuralAlignment
                     + 0.20·PracticalTransfer + 0.15·EmergentPropertyCreation
                     + 0.15·MetaphorNonDecorativeness
Gate: if CollisionColliderMADZ < 3.0 → BLOCK "No real collision. Only decorative metaphor."

# Physics — Fine-Tuning (L3, ±30σ HARD)
FineTuningRatio   = ViableBand / ParameterSpace
FineTuningEntropy = −Σ pᵢ·log(pᵢ)
State gate: if FineTuningRatio > 0.10 → BLOCK "Parameters generic, not fine-tuned."

# Physics — Hawking Radiation (information must escape opaque boundary)
State gate: if InternalVolume > 10·SurfaceArea → BLOCK "Black-box artifact."
State gate: if ObservedEntropy < 0.4·ExpectedEntropy → BLOCK.

# Physics — Bell Entanglement
BellParameterS = E(a,b) − E(a,b') + E(a',b) + E(a',b')
State gate: if claim = "systems are coupled" and |BellS| ≤ 2
          → BLOCK "Claimed entanglement is classical correlation."

# Physics — Vacuum Fluctuation
State gate: if BaselineVariance < ε_vacuum and SystemClaim = "operating"
          → BLOCK "Vacuum-fluctuation violation: artificially silent telemetry."
```

---

## 6. Hermes Integration Surface (the hooks)

The DES is useless unless Hermes calls it at the right moments. Required hooks:

| Hook | Trigger | Behavior |
| --- | --- | --- |
| `completion_scorer` | Every mission packet completion | Run full 40-engine pass on the result_packet artifact; attach scorecard. |
| `circuit_breaker` | Pre-integration | Block integration if any L3 physics gate fails or composite RIG-L < tier minimum. |
| `adversarial_review` | All tier ≥ published artifacts | Spawn independent Adversarial Reviewer (never self-review). |
| `cron` | Weekly | Recalibrate generic baselines + Brier delta + engine weights. |
| `kanban_event` | Skill promotion candidate | Run 40-engine doctrine pass; promote only if RIG-L ≥ 5 and risk_tier ≠ critical. |

### 6.1 Result-packet JSON schema (the framework's emit contract)

```json
{
  "mission_id": "...",
  "artifact": "...",
  "tier": "client",
  "engines": { "GravityEscape": 88, "RealityAnchor": 91, "...": "..." },
  "madz":    { "GravityEscape": 4.2, "...": "..." },
  "physics_state_gates": { "QuantumTunneling": "PASS", "FineTuning": "BLOCK" },
  "rig_l": 5.8,
  "bdf":  6.4,
  "status": "needs_rework",
  "weakest_gate": "FineTuning",
  "escalation_cost": 1024,
  "next_action": "narrow viable-parameter band; add hysteresis evidence"
}
```

### 6.2 Three-mode review depth (matches Fioma BMS bands)

| Mode | Engines Run | Use Case | BMS Analog |
| --- | --- | --- | --- |
| **Quick** | 3 engines (Gravity Escape, Reality Anchor, Memory Residue) | Small edits, low-risk internal artifacts | A1 |
| **Standard** | 10 engines (Cognitive 01–10) | Briefs, specs, normal missions | A2/A3 |
| **Doctrine** | All 40 engines | Production releases, doctrine changes, agent promotion, civilization artifacts | A4 |

---

## 7. The Adversarial Review Path (independence is non-negotiable)

The Adversarial Reviewer **must never self-review**. It is a separate agent persona that attacks artifacts for:

- Median output / generic gravity
- Fake mechanism (chains that look causal but aren't)
- Unsupported claims
- Low specificity
- Business irrelevance
- Approval bypass
- Credential risk
- Audit gaps

Coherence Scorer runs in parallel: if coherence across an artifact set < 0.70 → alert operator. Outcome Observer compares predicted σ to realized σ and feeds Brier deltas back into engine weights.

---

## 8. Build Sequence for Cloud Code (paste this as the implementation order)

### Day 1 — Core math + base class + registry
- Implement `core/robust_mad_z.py` with the 0.6745 constant
- Implement `core/sigma.py`, `core/escalation.py`, `core/bdf.py`, `core/thresholds.py`, `core/rig_l.py`
- Implement `DeviationEngine` dataclass in `core/base.py`
- Build registry of all 40 engines with `{id, name, layer, target, threshold}`
- Unit tests on the math primitives (anchor cases: σ = −10, 0, +3, +5, +10, +30)

### Day 2 — Pipeline orchestrator + audit + Hermes hooks
- Implement `pipeline/orchestrator.py` with the canonical gate ordering (physics → cognitive → nature → RIG-L)
- Stand up append-only audit substrate (UPDATE/DELETE revoked); Supabase migrations
- Implement all five Hermes hooks (`completion_scorer`, `circuit_breaker`, `adversarial_review`, `cron`, `kanban_event`)
- ApprovalClient (AionUI) integration for tier ≥ published
- Intent map + fallback routing

### Day 3 — Layer 1 Cognitive (engines 01–20)
- Implement all 20 cognitive engines with `raw_fn` + `baseline_fn`
- LLM adapters via LiteLLM for fuzzy metrics (specificity, mechanism clarity, memory residue)
- Unit tests + ProofPacket → Action → Result writes for every engine
- Generic-baseline corpus seeded (10 baseline types per engine)

### Day 4 — Layer 2 Nature (engines 21–30)
- Implement all 10 nature engines with exact bio-inspired formulas (Lévy flights, pheromone evaporation, whale spiral annealing, etc.)
- Process-gate wiring into orchestrator
- Reef-diversity / starvation-floor / replacement-probability boundary tests

### Day 5 — Layer 3 Physics (engines 31–40, ±30σ HARD)
- Implement all 10 physics engines with literal physics formulas (WKB tunneling, |BellS| > 2, Heisenberg ΔE·Δt ≥ ℏ/2, Pauli exclusion, Casimir F/A = −π²ℏc/240d⁴, Hawking S = k_B·A/4ℓ_P², fine-tuning ratio, third-law floor, light-cone causality, phase-transition hysteresis)
- Wire short-circuit logic: any L3 BLOCK halts the pipeline
- Worked test case: artifact that passes L1+L2 but fails Fine-Tuning gate → must short-circuit

### Day 6 — DES² amplification overlay
- Implement the 5 amplifiers as inner-loop wrappers (Mechanism Map, Source-Per-Claim, Falsification Check, Anti-Generic Gate, Brier-Calibrated Confidence)
- Verify 6.55× per axis on canonical benchmark artifacts
- Brier delta tracking enabled

### Day 7 — Adversarial review + outcome observer + verify-engines
- Spin up Adversarial Reviewer as independent agent persona (separate context, no self-review)
- Coherence Scorer + Outcome Observer wired to Hermes audit log
- `make verify-engines` green: all 40 engines emit a scorecard on a fixture artifact; physics short-circuit fires on the canonical failing fixture; RIG-L composite within ±0.1 of expected value
- FINAL_REPORT.md emitted with full coverage metrics + Brier calibration + outstanding unknowns

---

## 9. Baseline Generation Protocol

Each engine needs a **generic baseline corpus** to score against. Seed 10 baseline types per engine, drawn from:

1. Default Claude/GPT/Gemini outputs on the engine's prompt class
2. Top 100 LinkedIn posts in the artifact's category
3. Top 100 Medium articles in the artifact's category
4. Generic SaaS landing pages
5. Default consultant deliverables
6. Stock photography / template designs (for visual engines)
7. Wikipedia-style summaries
8. AI agency website copy
9. Generic GTM playbooks
10. Default agent-loop outputs from unmodified GenericAgent

Weekly recalibration cron: refresh medians, drift-detect, update engine weights via Brier deltas.

---

## 10. Final Definition of Done

The Deviate Engine System is complete when:

- All 40 engines implemented, registered, and emitting RobustMADZ on every artifact
- All 10 physics engines functioning as hard state gates that short-circuit on violation
- Composite gate ordering enforced: physics → cognitive → nature → RIG-L → detonation
- DES² 5-amplifier inner loop active on every engine (25× compound rigor verified)
- All five Hermes hooks live (`completion_scorer`, `circuit_breaker`, `adversarial_review`, `cron`, `kanban_event`)
- Adversarial Reviewer running as independent persona; Coherence Scorer + Outcome Observer wired to audit log
- Quick / Standard / Doctrine review modes selectable per mission tier
- Generic-baseline corpus seeded (10 types × 40 engines = 400 baseline sets); weekly recal cron green
- `make verify-engines` passes: 40-engine fixture run + physics short-circuit fixture + RIG-L within ±0.1
- Result-packet JSON schema emitted on every completion; append-only audit substrate writing
- FINAL_REPORT.md generated with coverage metrics, Brier calibration, escalation costs, outstanding unknowns
- System can autonomously gate any artifact through 3 layers → 40 engines → composite verdict → integrate-or-block without human intervention except where tier requires Patent Examiner or Doctrine Council approval

This card is the contract. Hermes drives. Tenacity loops. Cloud Code executes. The Deviate Engine System is the pressure layer that makes every other RIG OS component honest.
