# RIG V10 Idea Tournament Architecture

## Round 0: Signal Harvest (Continuous)
All 7 signal layers run autonomously. Each produces a **Signal Card**:

```
{
  signal_type: "orthodoxy_hardening" | "wound_frequency" | "vocabulary_drift" |
               "villain_emergence" | "proof_gap" | "format_exhaustion" | "adjacent_collision",
  raw_signal: "...",
  source: "...",
  detection_date: "...",
  confidence: 0.0-1.0,
  decay_rate: "how fast this signal is becoming consensus — high decay = write NOW"
}
```

## The 7 Signal Layers

| Layer | Source | What It Detects | Deviation Class |
|-------|--------|----------------|-----------------|
| **S1: Orthodoxy Hardening** | Industry reports, analyst decks, conference keynotes, top LinkedIn voices | Consensus calcifying into "best practices" | Orthodoxy Destruction (+15 to +30σ) |
| **S2: Wound Frequency** | Reddit, forums, support tickets, Slack communities, G2/Capterra reviews | Recurring pain with emotional charge | Wound Precision |
| **S3: Vocabulary Drift** | arXiv abstracts, product launches, VC pitch decks, new job titles | New terms before semantic inversion | Semantic Inversion |
| **S4: Villain Emergence** | Post-mortems, audit reports, public failures, regulatory actions | New categories of institutional failure | Villain Class |
| **S5: Proof Gaps** | Competitor content, thought leadership posts, keynote claims | Claims without evidence | Falsifiable Bet |
| **S6: Format Exhaustion** | LinkedIn feed analysis (90 days), newsletter formats | Formats copied to death | Format Novelty |
| **S7: Adjacent Collision** | Academic papers from unrelated fields, behavioral science, military, game theory | Frameworks never applied to this industry | Cross-Domain Transfer |

## Round 1: Angle Synthesis (50 angles)

Each layer nominates 7-8 angles. **Multi-layer combination is mandatory:**
- Single-layer: "AI governance is broken" → KILLED immediately
- 2-layer: S1+S4 → "Governance committees are Accountability Diffusion Engines"
- 4-layer: S1+S4+S5+S7 → Falsifiable bet + villain class + military doctrine proof → Elite

`if signal_layers_combined < 2 → KILL("Single-layer angle. Too shallow.")`

## Round 2: IDP Scoring (50 → 20)

Score all 50 on IdeaDeviationPotential. Kill bottom 60%.
Kill anything overlapping with last 30 days of published content (staleness filter).

```
IDP = 0.20*OrthodoxyDestructionDepth + 0.15*VillainClassSpecificity
    + 0.15*FalsifiableBetStrength + 0.12*SemanticInversionNovelty
    + 0.12*WoundResonanceScore + 0.10*ProofAvailability
    + 0.08*FormatNovelty + 0.08*CatchphrasePotential

Gate: IDP < 0.65 → KILL
Gate: IDP < 0.70 → DEPRIORITIZE (enter at lower priority)
Gate: IDP > 0.80 → FAST-TRACK
```

## Round 3: Adversarial Stress Test (20 → 8)

| Agent | Attack Vector | Kill Condition |
|-------|--------------|----------------|
| **Plagiarism Detector** | "Has this exact angle been published in 180 days?" | If yes → KILL |
| **Steelman Agent** | "What is the strongest defense of the orthodoxy you're attacking?" | If defense > attack → KILL |
| **Audience Simulator** | "Would the target audience share this or scroll past?" | If scroll probability > 0.6 → KILL |

## Round 4: Research Depth Pass (8 → 4)

Run all 10 Research Questions (Q21-Q30 from deviation-questions.md).

Kill conditions:
- ProofDensity < +3 (no verifiable claims)
- FalsificationResilience < 0.5 (Red Team destroys it)
- MechanismClarity < 0.6 (can't explain the system underneath)

## Round 5: Ensemble Draft + Max BDF Selection (4 → 1)

Each surviving angle × 5 archetypes = **20 drafts**.

Archetypes:
- **Agent E (EminemDensity):** sonic velocity, syllable flips, internal rhyme
- **Agent H (HemingwayCompression):** blunt force, short sentences, no decoration
- **Agent D (DidionCadence):** controlled dread, quiet endings
- **Agent M (McCarthyRhythm):** biblical cadence, no punctuation
- **Agent W (WallaceRecursion):** recursive footnotes, self-aware tangents

Score all 20 on:
- BDF30 (must exceed 8.0σ)
- CraftCoefficient (must exceed 0.85)
- CatchphraseScore (must exceed 0.80)
- AntiGenericForce (must exceed 80)

```
winner = max(surviving_drafts, key=lambda d: d.bdf30)
```

## Round 6: Post-Ship Learning

Track: impressions, comments, shares, profile clicks, DMs generated.
Compute Brier accuracy per swarm persona.
Update signal layer weights based on which layers produced winning angles.
Recalibrate formula weights quarterly.

The tournament gets smarter every cycle. This is the compounding intelligence layer.
