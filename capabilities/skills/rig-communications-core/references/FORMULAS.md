# RIG Communication Protocol — All 8 Scoring Formulas

## Formula 1: Communication Raw Score (Universal)

```
CommRawScore =
  0.14 * WoundPrecision +
  0.12 * MirrorAccuracy +
  0.11 * AutonomyPreservation +
  0.10 * QualificationTension +
  0.09 * SpecificityDensity +
  0.09 * OpenLoopResidue +
  0.08 * RPE_Strength +
  0.08 * RealityAnchor +
  0.07 * AntiGenericForce +
  0.06 * TonePrecision +
  0.04 * MemoryResidue +
  0.02 * EthicalRestraint
```

Gate: CommRawScore ≥ 0.65

## Formula 2: Email Voltage Score

```
EmailVoltageScore =
  0.22 * WoundPrecision +
  0.18 * StakesClarity +
  0.16 * DesireActivation +
  0.14 * TensionRelease +
  0.12 * ReliefClarity +
  0.10 * IdentityResonance +
  0.08 * PeakEndMemory
```

## Formula 3: Email Reply Score

```
EmailReplyScore =
  0.20 * WoundIdentification +
  0.15 * Specificity +
  0.15 * Restraint +
  0.15 * AutonomyPreservation +
  0.12 * MirrorAccuracy +
  0.10 * QualificationFrame +
  0.08 * OpenLoopStrength +
  0.05 * CloseQuality
```

## Formula 4: LinkedIn BDF30 (Bipolar Deviation Formula)

```
BDF30 = 0.25*SemanticInversion + 0.20*ProofDensity + 0.15*EnemySpecificity
      + 0.15*CatchphraseVoltage + 0.10*StructuralNovelty + 0.10*NegativeSpaceWeight
      + 0.05*IdentityForce
```

Target: MAD-Z > 8.0σ. Aspiration: +22σ.
Gate: BDF30 < 8.0 → BLOCK

## Formula 5: CraftCoefficient (Multi-Archetype)

```
CraftCoefficient = max(
  EminemDensity   = 0.30*InternalRhymeRate + 0.25*SyllabicPercussion
                   + 0.20*SemanticInversion + 0.15*MultiSyllabicMatch
                   + 0.10*EnjambmentLeverage,
  HemingwayCompression,
  DidionCadence,
  McCarthyRhythm,
  WallaceRecursion
)
```

Gate: CraftCoefficient ≥ 0.85

## Formula 6: CatchphraseScore

```
CatchphraseScore = 0.25*Memorability + 0.20*SonicEdge + 0.20*EnemyClarity
                 + 0.15*CrossChannelSurvival + 0.10*CompressionElegance
                 + 0.10*IdentityStamp
```

Gate: CatchphraseScore ≥ 0.80

## Formula 7: CustomerFacing Artifact Score

```
CustomerFacingArtifactScore =
  0.18*Evidence + 0.18*AntiGenericForce + 0.14*IdentityForce + 0.14*RIGSignature +
  0.12*ArtifactCompleteness + 0.10*EmotionalVoltage + 0.08*MechanismClarity +
  0.06*MemoryCompounding
```

Gate: CFAS < 82 → BLOCK

## Formula 8: Reward Prediction Error (Dopamine Engine)

```
RPE = δₜ = rₜ + γ · V(sₜ₊₁) − V(sₜ)

rₜ = actual reward (value delivered by THIS communication)
γ = discount factor (future value weight)
V(sₜ) = expected value (generic vendor email = the median baseline)
V(sₜ₊₁) = predicted future value from the relationship
```

Goal: δₜ > 0 — deliver MORE than expected.

Validated: Schultz 2016 (n=102 fMRI studies, N=2,316) — Evidence 10/10.
Unsigned |δ| enhances memory (Liu et al. 2025; Ergo et al. 2020) — Evidence 9/10.
