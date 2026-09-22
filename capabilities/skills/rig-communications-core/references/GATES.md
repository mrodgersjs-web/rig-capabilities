# Universal Hard Gates — Nothing Ships Without Passing

## Sequence Integrity

```
if (WoundPhase == missing)              → BLOCK("No wound identified")
if (MirrorPhase == missing)             → BLOCK("No mirror — recipient won't feel understood")
if (AutonomyPreservation < 0.70)        → BLOCK("Chasing detected. Rewrite.")
if (BannedPhrase detected)              → BLOCK("Generic phrase: [phrase]. Remove.")
```

## Banned Phrases (Automatic Block)

| Phrase | Why It Fails |
|--------|-------------|
| "Just checking in" | Signals neediness. Removes frame. |
| "Following up" | Chasing. Zero new value. |
| "Touching base" | Vague. No purpose. |
| "Would love to chat" | No specificity. No urgency. |
| "Let me know your thoughts" | Passive. No direction. No tension. |
| "Happy to help" | Vendor behavior. No selectivity. |
| "Hope this email finds you well" | Zero information. Signals "I have nothing specific to say about you." |
| "I wanted to reach out" | Self-centered. No relevance to recipient. |
| "Quick question" | Always a lie. Never quick. Never just one. |
| "Looking forward to hearing from you" | Chasing. Pressure without value. |

## Quality Gates

```
if (WoundPrecision < 0.60)              → BLOCK("Wound is generic. Name the specific pattern.")
if (SpecificityDensity < 0.50)          → BLOCK("Too vague. Add numbers, names, or evidence.")
if (CommRawScore < 0.65)                → BLOCK("Below doctrine threshold.")
```

## Customer-Facing Gates

```
if (CustomerFacingArtifactScore < 82)   → BLOCK("Below ship threshold.")
if (AntiGenericForce < 80)              → BLOCK("Positioning is interchangeable.")
if (IdentityForce < 75)                 → BLOCK("Does not feel like RIG.")
if (RIGSignature < 75)                  → BLOCK("Could have been written by anyone.")
```

## Deviation Gates

```
if (BDF30 < 8.0)                        → BLOCK("Did not reach 8σ deviation.")
if (PredictedSuccess < 0.82)            → BLOCK("Predicted success too low.")
```

## LinkedIn-Specific Gates

```
if (SwarmConsensus < 0.65)              → BLOCK("Prediction swarm disagreement too high.")
if (HookRupture < 0.70)                 → BLOCK("Hook won't stop the scroll.")
```

## Ethical Gates

```
if (EthicalRestraint < 0.70)            → BLOCK("Manipulation risk detected.")
if (SendRisk.overExplanation > 0.30)    → WARN("Over-explaining. Cut 40%.")
if (SendRisk.manipulation > 0.20)       → BLOCK("Manipulation detected.")
```

## Peer-Reviewed Gates

```
// Entropy gate — validated: Brydevall et al. 2017; Dean & Neligh 2023; Pimentel et al. 2022
if (AntiGenericForce_entropy < 1.2)     → BLOCK("Not enough deviation from median baseline")
// AntiGenericForce_entropy = H(artifact) / H(median_baseline)

// Reactance gate — validated: Li & Shi 2025 (k=53 studies, r ≈ .20 threshold)
if (ReactanceRisk > 0.20)               → BLOCK("Reactance threshold exceeded")
// ReactanceRisk = Σ(ThreatMarkers × FreedomImportance) / TotalSentences
```
