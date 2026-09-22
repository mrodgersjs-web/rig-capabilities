# Consensus Research → RIG Proprietary Process: Peer-Reviewed Validation

All formulas and gates in the master communication protocol are grounded in peer-reviewed research. This document maps every finding to its corresponding RIG component.

---

## 1. Reward Prediction Error: The Dopamine Engine

**Finding:** The canonical RPE formula — δₜ = rₜ + γ·V(sₜ₊₁) − V(sₜ) — is the most robustly validated model in neuroscience literature (Schultz, 2016). A meta-analysis of 102 fMRI studies with 2,316 participants confirms dopamine neurons encode prediction errors that scale with unexpectedness (Fouragnan et al., 2018).

**RIG Operationalization:** The median baseline (16-32 generic artifacts) = V(sₜ). The shipped artifact = rₜ. The Robust-MAD-Z score IS the δₜ — the prediction error measured in standard deviations. Requiring MAD-Z ≥ 8.0 means requiring a dopamine-triggering RPE 8σ above expectation.

**Critical finding for bipolar architecture:** Unsigned prediction error |δ| — meaning BOTH positive and negative deviation — enhances memory encoding (Liu et al., 2025; Ergo et al., 2020). Evidence: 9/10. A one-word "Pass" reply (-16 erosion) creates as much memory trace as a 500-word manifesto (+16 detonation) because both generate high |δ|. This validates the bipolar architecture where both poles ship.

**Boundary condition:** RPE signals are modulated by attention (Smout et al., 2019). If the audience isn't paying attention, the prediction error doesn't fire. This validates Hook Velocity — the first 1.5 seconds must capture attention BEFORE the RPE can land.

**Maps to:** BDF30 formula, Robust-MAD-Z gate (≥ 8.0σ), Hook Velocity, Bipolar architecture

---

## 2. Bayesian Surprise: Catchphrase Science

**Finding:** S = D_KL(P_posterior || P_prior) — Bayesian Surprise measured as KL divergence between prior and posterior beliefs. 72%+ of gaze shifts directed toward high-surprise regions (Itti & Baldi, 2005). Evidence: 8/10.

**RIG Operationalization:** Every semantic inversion ("prompt engineering → prompt costume design") is a Bayesian surprise generator. The reader's prior belief about what a LinkedIn post will say gets violently updated by the actual content.

```
CatchphraseSurprise ≈ D_KL(reader_posterior || reader_prior)
Gate: If catchphrase could appear in >5% of existing posts on this topic → too low → REWRITE
Maps to existing gate: CatchphraseScore ≥ 0.80
```

**Boundary condition:** Surprise must be *meaningful*. Random word salad has high entropy but zero value. The CraftCoefficient gate (≥ 0.85) ensures surprise is delivered through earned archetype mastery, not noise.

**Maps to:** CatchphraseScore, Hook Velocity, SemanticInversionNovelty in IDP formula

---

## 3. Shannon Entropy: Anti-Generic Mathematical Proof

**Finding:** H(p) = -Σ p(x)·log₂(p(x)) — higher entropy predicts longer reading times and greater attention allocation (Brydevall et al., 2017; Dean & Neligh, 2023; Pimentel et al., 2022). Evidence: 8/10.

**RIG Operationalization:**
```
AntiGenericForce_entropy = H(artifact) / H(median_baseline)
Gate: ratio > 1.2 (artifact must be ≥20% more entropic than median baseline)
Hard kill: AntiGenericForce < 80 (existing gate, now grounded in entropy theory)
```

**Boundary condition:** Entropy-based models require adaptation when cognitive resources are limited (Dean & Neligh, 2023). For mobile-first LinkedIn consumption, entropy must be balanced with compression — high information density per syllable, not high word count. This validates the HemingwayCompression archetype and the RestraintCoefficient gate (≥ 0.80 for artifacts > 200 words).

**Maps to:** AntiGenericForce gate (≥ 80), HemingwayCompression archetype, RestraintCoefficient

---

## 4. Psychological Reactance: Banned Phrase Meta-Analysis

**Finding:** Reactance ∝ Threat_Level × Importance_of_Freedom. Meta-analysis of k=53 studies: high-threat language increases reactance (r ≈ .20), anger (r ≈ .21), negative cognitions (r ≈ .17) (Li & Shi, 2025; Rosenberg & Siegel, 2017). Evidence: 8/10.

**RIG Operationalization:** Every banned phrase — "Just checking in," "Following up," "Happy to help" — is a high-threat-language trigger empirically shown to increase resistance. The Autonomy Preservation gate (≥ 0.70) is a reactance mitigation engine.

```
ReactanceRisk = Σ(ThreatMarkers × FreedomImportance) / TotalSentences
Gate: ReactanceRisk < 0.20 (maps to r ≈ .20 threshold from meta-analysis)
Existing gate: AutonomyPreservation ≥ 0.70 → BLOCK if violated
```

**Critical RIG design choice validated:** Gain vs. loss framing does NOT significantly affect reactance (Li & Shi, 2025). RIG's loss-framing approach — "waiting is not neutral if the pattern is already costing you [specific loss]" — is safe. Loss frames don't trigger reactance. Imperative language does. The doctrine correctly uses loss frames while preserving autonomy.

**Maps to:** Autonomy Preservation gate, Banned Phrases list, ReactanceRisk metric

---

## 5. Distributed Practice: Content Series Design

**Finding:** Optimal ISI (Inter-Session Interval) ≈ 10-20% of Retention Interval. Up to 150% improvement in long-term recall with optimal spacing (Latimier et al., 2020; Cepeda et al., 2006). Evidence: 9/10.

**RIG Operationalization:**
```
Monthly retention target → ISI = 3-6 days between posts on same doctrine thread
Quarterly retention (board-level) → ISI = 9-18 days between reinforcement posts
```

**MemoryCompoundingScore (new formula):**
```
MCS = 0.30*DoctrineThreadContinuity + 0.25*OptimalSpacingAdherence
    + 0.25*CatchphraseRecurrence + 0.20*VillainClassConsistency
Gate: MCS ≥ 0.60 for series posts
```

**Maps to:** MemoryCompoundingScore, Content series planning, Post-ship learning loop

---

## 6. Expectation Violation: 5-Phase Compound RPE

**Finding:** Expectation violation models outperform complex mentalizing models for goal identification in novel communication (Buidze et al., 2025). Maximizing model-derived surprise enhances engagement and physiological arousal (pupil dilation). Evidence: 7/10.

**RIG Operationalization:** The Wound → Mirror → Autonomy → Qualification → Open Loop sequence is a five-stage compound RPE engine:

| Phase | Expectation Violated | RPE Generated |
|-------|---------------------|---------------|
| Wound | "They'll open with pleasantries" | Surprise: they named my exact pain |
| Mirror | "They don't understand my world" | Surprise: they described my reality better than I could |
| Autonomy | "They'll chase me for a meeting" | Surprise: they gave me permission to say no |
| Qualification | "They want the deal at any cost" | Surprise: they're evaluating whether I'm worth their time |
| Open Loop | "The message will close cleanly" | Surprise: I can't stop thinking about the unresolved tension |

Each phase generates a separate δₜ. Five consecutive expectation violations that stack.

**Maps to:** 5-phase sequence, Compound RPE engine, Sequence gates

---

## 7. Expert Construct Definition: Weight Calibration

**Finding:** Quality levels must be expert-defined, not learned (Bachmann et al., 2020; Liao et al., 2023; Zheng et al., 2025). Indicator weights require Delphi-equivalent rounds. E-consultation quality used 3 primary, 10 secondary, 32 tertiary indicators weighted via Analytic Hierarchy Process.

**RIG Operationalization:** The formula weights (BDF30 weights, IDP weights, CatchphraseScore weights) are the RIG equivalent of Delphi-expert calibrated indicators. They are hypotheses about what matters. The Brier loop tests those hypotheses against reality.

**Recalibration cadence:** Quarterly. Each shipped artifact feeds the Brier loop. Weights that predict poorly get down-weighted. Weights that predict accurately get up-weighted.

**Maps to:** All formula weights, Brier calibration loop, Quarterly recalibration

---

## 8. Master Mapping Table

| Peer-Reviewed Model | Formula | Evidence Level | RIG Component | Gate |
|--------------------|---------|---------------|---------------|------|
| Temporal Difference RPE | δₜ = rₜ + γ·V(sₜ₊₁) − V(sₜ) | 10/10 (102 fMRI, n=2,316) | BDF30 deviation from median | MAD-Z ≥ 8.0 |
| Unsigned PE → Memory | \|δ\| enhances recognition | 9/10 | Bipolar architecture: both poles ship | N/A (architecture) |
| Bayesian Surprise | S = D_KL(P_post ∥ P_prior) | 8/10 (72%+ gaze shifts) | CatchphraseScore + Hook Velocity | ≥ 0.80 |
| Shannon Entropy | H(p) = -Σ p(x)·log₂(p(x)) | 8/10 | AntiGenericForce | ≥ 80 |
| Psychological Reactance | ∝ Threat × Freedom | 8/10 (k=53, r≈.20) | Autonomy Preservation | ≥ 0.70 |
| Distributed Practice | ISI ≈ 10-20% of Retention | 9/10 (150% recall) | Memory Compounding | ISI = 3-6 days |
| Expectation Violation | Outperforms mentalizing | 7/10 | 5-phase Wound→Loop sequence | Compound RPE |
| Brier Score | BS = mean(f − o)² | Established | Swarm calibration | Bipolar-aware |
| Expert Construct Definition | Delphi + AHP weights | 8/10 | All formula weights | Quarterly recalibration |

---

## Research Gaps & RIG's Response

**Gap 1: Text-specific neural validation remains underexplored.** Most RPE/entropy studies are in lab settings, not professional communication. RIG's Brier loop IS the missing research — every shipped artifact becomes a data point.

**Gap 2: Individual differences moderate everything.** Trait reactance, cognitive load, domain expertise all moderate audience response. The 8-persona Prediction Swarm models this variance explicitly.

**Gap 3:** The IDP formula weights (0.20 for OrthodoxyDestructionDepth, 0.15 for VillainClassSpecificity, etc.) are hypotheses. The Brier loop validates or refutes them. Recalibration is quarterly.
