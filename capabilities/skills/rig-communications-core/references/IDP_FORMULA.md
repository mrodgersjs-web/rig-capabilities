# IdeaDeviationPotential (IDP) Formula Card

The master scoring formula for evaluating raw angles before they enter the writing pipeline.

```
IDP = 0.20 * OrthodoxyDestructionDepth
    + 0.15 * VillainClassSpecificity
    + 0.15 * FalsifiableBetStrength
    + 0.12 * SemanticInversionNovelty
    + 0.12 * WoundResonanceScore
    + 0.10 * ProofAvailability
    + 0.08 * FormatNovelty
    + 0.08 * CatchphrasePotential
```

## Component Sub-Formulas

### OrthodoxyDestructionDepth (weight: 0.20)
```
ODD = 0.35 * OrthodoxyStrength (how widely accepted is the belief being attacked?)
    + 0.25 * DestructionQuality (how thoroughly can you show it is wrong?)
    + 0.20 * ReplacementClarity (is there a clear better alternative?)
    + 0.20 * AudienceImpact (how many people will need to update their beliefs?)
```

### VillainClassSpecificity (weight: 0.15)
```
VCS = 0.30 * NamedEntityPrecision (is the villain a specific category, not a vague enemy?)
    + 0.25 * ProfitTransparency (can you show who gains from the problem persisting?)
    + 0.25 * AccountabilitySurface (can readers identify this villain in their own org?)
    + 0.20 * MemeticContagionRisk (will others adopt this term because it is useful?)
```

### FalsifiableBetStrength (weight: 0.15)
```
FBS = 0.35 * MeasurabilityScore (can the claim be verified with data?)
    + 0.25 * StakeMagnitude (is the bet large enough to signal conviction?)
    + 0.25 * TimelineSpecificity (is there a specific date or window?)
    + 0.15 * CounterConsensus (how far from consensus is the prediction?)
```

### SemanticInversionNovelty (weight: 0.12)
```
SIN = 0.30 * PriorTermFamiliarity (how well-known is the original term?)
    + 0.25 * InversionDistance (how far is the new term from the old meaning?)
    + 0.25 * CognitiveStickiness (does it immediately make sense while being surprising?)
    + 0.20 * DomainOriginality (has anyone else used this exact reframe?)
```

### WoundResonanceScore (weight: 0.12)
```
WRS = 0.35 * PainFrequency (how many people experience this exact pain?)
    + 0.25 * EmotionalCharge (how much does the pain hurt to acknowledge?)
    + 0.25 * Invisibility (how normalized or invisible is the wound?)
    + 0.15 * CostQuantifiability (can the cost be expressed as dollars, hours, or market share?)
```

### FormatNovelty (weight: 0.08)
```
FN = 0.40 * CopyCountInverse (how many times has this format been used in last 90 days?)
    + 0.30 * StructuralOriginality (is the format genuinely new or just remixed?)
    + 0.30 * AttentionAdvantage (will the format itself cause a double-take?)
```

### CatchphrasePotential (weight: 0.08)
```
CP = 0.35 * PhoneticMemorability (alliteration, assonance, consonance, rhythm)
    + 0.30 * CompressionDensity (meaning per syllable is maximized)
    + 0.25 * CrossChannelViability (works as well in speech as in text)
    + 0.10 * VisualLogoPotential (could this phrase anchor a visual identity?)
```

### ProofAvailability (weight: 0.10)
```
PA = 0.40 * AcademicEvidence (peer-reviewed support exists)
    + 0.30 * IndustryData (named companies with published numbers)
    + 0.20 * PrimaryResearchPotential (can be validated with a quick experiment)
    + 0.10 * AnecdotalStrength (compelling stories exist to humanize the data)
```

## Hard Gates

```
if IDP < 0.65 -> KILL("Angle not deviant enough to survive the assembly line.")
if IDP < 0.70 -> DEPRIORITIZE (enter tournament at lower priority)
if IDP > 0.80 -> FAST-TRACK (skip Round 2, go directly to adversarial stress test)
if signal_layers_combined < 2 -> KILL("Single-layer angle. Too shallow.")
if ProofAvailability < 0.30 -> ROUTE TO RESEARCH (not writing - build evidence first)
```

## Scoring Scale

| IDP Range | Label | Action |
|-----------|-------|--------|
| 0.90 - 1.00 | Elite | Fast-track to ensemble draft. Ship candidate. |
| 0.80 - 0.89 | Exceptional | Enter tournament at Round 3 (skip Round 2 culling) |
| 0.70 - 0.79 | Strong | Enter tournament normally |
| 0.65 - 0.69 | Marginal | Enter tournament at lowest priority |
| 0.50 - 0.64 | Insufficient | KILL - will never survive the pipeline |
| 0.00 - 0.49 | Generic | KILL - indistinguishable from median content |

## Calibration

Weights are hypotheses calibrated via expert judgment (Delphi-equivalent rounds). The Brier loop tests these weights against actual engagement outcomes. Recalibration is quarterly.

Initial calibration source: Expert judgment (Mike Rodgers, RIG Chief OS). Validated against: RIG Communication Protocol v1-v9 field outcomes. Grounded in: Consensus peer-reviewed research (see consensus-research-mapping.md).
