---
name: references
description: Master RIG communication engine — cold email, warm email, reply, LinkedIn post, LinkedIn comment, Slack, DM, proposal, follow-up. Loads Wound→Mirror→Autonomy→Qualification→Open Loop protocol, 8 scoring formulas, 50 deviation-engine questions, 20 GitHub signal repos, Consensus-validated formulas, BDF30/CraftCoefficient/CatchphraseScore gates, prediction swarm, tournament architecture, and channel-specific protocols. Use when writing or evaluating any RIG external communication. The complete V10 doctrine in one slash command.
version: 10.0.0
license: Proprietary
metadata:
  hermes:
    tags: [communication, email, linkedin, scoring, content, writing, rig, doctrine, v10]
    related_skills: [rig-operator-doctrine, rig-creative-context, rig-fleet-execution]
  author: RIG / Mike Rodgers
---

# RIG Communication Protocol V10 — Unified Master Skill

Slash command: `/rig-communication-protocol` — loads the complete executable communication engine.

## CORE BELIEF

Every communication either advances a relationship, builds authority, or wastes two people's time. There is no neutral. The goal is to make every written communication function as a small emotional composition — **Wound → Mirror → Autonomy → Qualification → Open Loop** — producing a measurable Reward Prediction Error (δₜ > 0) relative to the median baseline.

The median (0σ) is what ChatGPT produces when you say "write a professional email." Everything RIG produces must be measurably above that median across every scored dimension. **Peer-reviewed validation:** 102 fMRI studies (N=2,316) confirm dopamine neurons encode prediction errors scaling with unexpectedness (Schultz 2016; Fouragnan et al. 2018). Your BDF30 formula is literally an RPE engine.

---

## PART 1: THE FIVE-PHASE SEQUENCE (Executable)

### Phase 1: WOUND
Name the specific, expensive pattern the recipient is living inside but hasn't articulated.

- **Specific** — not "many companies struggle" but "your team spends 4 hours/day on leads that never close"
- **Evidenced** — based on observable signals (website, LinkedIn, job postings, tech stack)
- **Systemic** — not a surface symptom but the underlying pattern

Gate: `if Wound Precision < 0.6 → BLOCK("Wound is generic")`
Gate: `if Phase missing → BLOCK("No wound identified")`

### Phase 2: MIRROR
Reflect the recipient's current reality with enough precision they feel *seen* — not handled, not diagnosed.

- **Accurate** — if wrong, trust collapses instantly
- **Non-judgmental** — observation, not accusation
- **Specific enough to feel personal**

Gate: `if Phase missing → BLOCK("No mirror — recipient won't feel understood")`
Test: Recipient should think "How did they know that?" — not "That's a nice thing to say."

### Phase 3: AUTONOMY
Explicitly preserve the recipient's freedom to say no, walk away, or do nothing.

- "If this resonates, here's what I'd suggest"
- "You're the best judge of whether this is the right time"
- "If the timing isn't right, no need to respond"

Gate: `if AutonomyPreservation < 0.70 → BLOCK("Chasing detected. Rewrite.")`

**BANNED PHRASES (any use = automatic BLOCK):**
"Just checking in" | "Following up" | "Touching base" | "Would love to chat" | "Let me know your thoughts" | "Happy to help" | "Hope this email finds you well" | "I wanted to reach out" | "Quick question" | "Looking forward to hearing from you"

### Phase 4: QUALIFICATION
Flip the frame — you are evaluating THEM, not begging for their attention.

- Name who this is NOT for
- Define conditions under which you'd walk away
- Force an identity choice: after reading, they decide who they are

Gate: `if QualificationTension < 0.5 → WARN("No selective pressure")`
Test: Recipient feels they need to *earn* the next step, not be *sold* it.

### Phase 5: OPEN LOOP
End with unresolved tension — a diagnostic question, a cost-of-inaction frame, or a next step so specific that NOT responding feels like a tangible loss.

- Do NOT close with generic CTA
- Leave a specific thread unresolved
- Frame inaction as a decision with a named cost
- Peer-reviewed backing: Zeigarnik effect — incomplete tasks create persistent cognitive tension

Gate: `if ends with generic CTA ("let me know" / "looking forward") → BLOCK`

---

## PART 2: THE SCORING FORMULAS (All 8)

### Formula 1: Communication Raw Score (Universal)
```
CommRawScore =
  0.14 * WoundPrecision + 0.12 * MirrorAccuracy + 0.11 * AutonomyPreservation +
  0.10 * QualificationTension + 0.09 * SpecificityDensity + 0.09 * OpenLoopResidue +
  0.08 * RPE_Strength + 0.08 * RealityAnchor + 0.07 * AntiGenericForce +
  0.06 * TonePrecision + 0.04 * MemoryResidue + 0.02 * EthicalRestraint
```
Gate: `CommRawScore ≥ 0.65 || BLOCK`

### Formula 2: Email Voltage Score
```
EmailVoltageScore =
  0.22 * WoundPrecision + 0.18 * StakesClarity + 0.16 * DesireActivation +
  0.14 * TensionRelease + 0.12 * ReliefClarity + 0.10 * IdentityResonance +
  0.08 * PeakEndMemory
```

### Formula 3: Email Reply Score
```
EmailReplyScore =
  0.20 * WoundIdentification + 0.15 * Specificity + 0.15 * Restraint +
  0.15 * AutonomyPreservation + 0.12 * MirrorAccuracy + 0.10 * QualificationFrame +
  0.08 * OpenLoopStrength + 0.05 * CloseQuality
```

### Formula 4: LinkedIn BDF30 (Bipolar Deviation Formula)
```
BDF30 = 0.25*SemanticInversion + 0.20*ProofDensity + 0.15*EnemySpecificity
      + 0.15*CatchphraseVoltage + 0.10*StructuralNovelty + 0.10*NegativeSpaceWeight
      + 0.05*IdentityForce
```
Target: MAD-Z > 8.0σ. Aspiration: +22σ.
Gate: `BDF30 < 8.0 → BLOCK`

### Formula 5: CraftCoefficient (Multi-Archetype)
```
CraftCoefficient = max(
  EminemDensity   = 0.30*InternalRhymeRate + 0.25*SyllabicPercussion + 0.20*SemanticInversion + 0.15*MultiSyllabicMatch + 0.10*EnjambmentLeverage,
  HemingwayCompression,
  DidionCadence,
  McCarthyRhythm,
  WallaceRecursion
)
```
Gate: `CraftCoefficient ≥ 0.85`

### Formula 6: CatchphraseScore
```
CatchphraseScore = 0.25*Memorability + 0.20*SonicEdge + 0.20*EnemyClarity
                 + 0.15*CrossChannelSurvival + 0.10*CompressionElegance + 0.10*IdentityStamp
```
Gate: `CatchphraseScore ≥ 0.80`
Also: `CatchphraseSurprise ≈ D_KL(reader_posterior || reader_prior)` — if catchphrase appears in >5% of existing posts on this topic, too low → REWRITE.

### Formula 7: CustomerFacing Artifact Score
```
CustomerFacingArtifactScore =
  0.18*Evidence + 0.18*AntiGenericForce + 0.14*IdentityForce + 0.14*RIGSignature +
  0.12*ArtifactCompleteness + 0.10*EmotionalVoltage + 0.08*MechanismClarity + 0.06*MemoryCompounding
```
Gate: `CFAS < 82 → BLOCK`

### Formula 8: Reward Prediction Error (Dopamine Engine)
```
RPE = δₜ = rₜ + γ · V(sₜ₊₁) − V(sₜ)

rₜ = actual reward (value delivered by THIS communication)
γ = discount factor (future value weight)
V(sₜ) = expected value (generic vendor email = the median baseline)
V(sₜ₊₁) = predicted future value from the relationship
```
Goal: δₜ > 0 — deliver MORE than expected. That delta IS the RPE. That's the dopamine signal.
Validated by: Schultz 2016 (n=102 fMRI studies, N=2,316) — Evidence 10/10.
Unsigned |δ| enhances memory (Liu et al. 2025; Ergo et al. 2020) — Evidence 9/10.

---

## PART 3: UNIVERSAL HARD GATES (Ship-Stopping)

```
// Sequence integrity
if (WoundPhase == missing)              → BLOCK("No wound")
if (MirrorPhase == missing)             → BLOCK("No mirror")
if (AutonomyPreservation < 0.70)        → BLOCK("Chasing detected")
if (BannedPhrase detected)              → BLOCK("Generic phrase: [phrase]")

// Quality thresholds
if (WoundPrecision < 0.60)              → BLOCK("Wound is generic")
if (SpecificityDensity < 0.50)          → BLOCK("Too vague — add numbers, names, evidence")
if (CommRawScore < 0.65)                → BLOCK("Below doctrine threshold")

// Customer-facing
if (CustomerFacingArtifactScore < 82)   → BLOCK("Below ship threshold")
if (AntiGenericForce < 80)              → BLOCK("Positioning interchangeable")
if (IdentityForce < 75)                 → BLOCK("Does not feel like RIG")
if (RIGSignature < 75)                  → BLOCK("Could have been written by anyone")

// 8σ gate
if (BDF30 < 8.0)                        → BLOCK("Did not reach 8σ deviation")
if (PredictedSuccess < 0.82)            → BLOCK("Predicted success too low")

// LinkedIn gates
if (SwarmConsensus < 0.65)              → BLOCK("Swarm disagreement too high")
if (HookRupture < 0.70)                 → BLOCK("Hook won't stop the scroll")

// Ethical gates
if (EthicalRestraint < 0.70)            → BLOCK("Manipulation risk detected")
if (SendRisk.overExplanation > 0.30)    → WARN("Over-explaining. Cut 40%.")
if (SendRisk.manipulation > 0.20)       → BLOCK("Manipulation detected")

// Entropy gate
if (AntiGenericForce_entropy < 1.2)     → BLOCK("Not enough deviation from median baseline")
// AntiGenericForce_entropy = H(artifact) / H(median_baseline)
// Validated: Brydevall et al. 2017, Dean & Neligh 2023, Pimentel et al. 2022

// Reactance gate
if (ReactanceRisk > 0.20)               → BLOCK("Reactance threshold exceeded")
// ReactanceRisk = Σ(ThreatMarkers × FreedomImportance) / TotalSentences
// Validated: Li & Shi 2025 meta-analysis k=53 studies, r ≈ .20 threshold
```

---

## PART 4: CHANNEL-SPECIFIC PROTOCOLS (Quick-Reference)

### Cold Email
Subject: [Specific curiosity gap — name THEIR situation, not your product]
Structure: Wound → Mirror → Mechanism hint → Autonomy + Qualification → Open Loop → Specific CTA
Deviation targets: E1-E4: +5 to +7 | E5: +3 to +5 | All E ≥ +3 to ship
Example (+7σ): "Your board deck is missing slide 11"

### Email Reply
Pre-reply analysis (run before writing):
A) What did they literally ask?
B) What are they actually worried about? (hidden fear)
C) What is the specific business wound underneath?
D) What would a generic vendor reply look like? (this is what we DON'T do)
E) What would make them feel understood without being diagnosed?
F) What tension should remain unresolved?

Reply arcs: Pattern Recognition | Criteria-Tension | Autonomy-Loss Frame | Praise-Filter
Deviation targets: E1: +1 to +3 | E2-E5: +3 to +5 | E3 ≥ +3 to ship

### LinkedIn Post (Thought Leadership)
8-step structure: Hook → Wound Mirror → Authority Frame → Mechanism → Evidence → Diagnostic Question → Open Loop → CTA
Before posting: run 8-persona prediction swarm (consensus > 0.65)
Deviation targets: L1: +5 to +8 | L2-L5: +5 to +7 | L1 ≥ +5 to ship

### LinkedIn Comment
Formula: CommentValue = 0.30*AddedInsight + 0.25*SpecificEvidence + 0.20*DisagreementQuality + 0.15*QuestionAsked + 0.10*AuthoritySignal
Gate: `if Comment == generic agreement → DON'T POST`

### Follow-Up Email
Structure: New wound or new evidence (NOT "just following up") → New insight → Autonomy → Open Loop
Gate: `if repeats previous email content → BLOCK`

### Internal (Slack/Team/Memo)
Structure: What you need from them → Context (only what they need) → Deadline → Link to detail
Deviation targets: E1: -3 to +1 | E2: -3 to +1 | E3-E5: +1 to +3

### Proposal/Pitch
Structure: The Wound → The Mechanism → The Proof → The Offer → The Open Loop
Target: All criteria +5 to +7 | CFAS ≥ 82 | AntiGenericForce ≥ 80

---

## PART 5: PREDICTION SWARM (8 Personas)

| Persona | Tests |
|---------|-------|
| **Skeptical Buyer** | Does this feel like a pitch? Will they dismiss? |
| **Busy Founder** | Will they read past line 2? Is value immediate? |
| **Technical Evaluator** | Is mechanism credible? Are claims verifiable? |
| **Budget Holder** | Is ROI clear? Is cost-of-inaction quantified? |
| **Industry Lurker** | Would they share this? Does it make them look smart? |
| **Competitor Analyst** | Does this reveal too much? Makes competitors uncomfortable? |
| **Junior Employee** | Is it accessible? Would they forward to their boss? |
| **Senior Executive** | Does it respect their time? Does it signal peer-level thinking? |

```
PredictedSuccess = 0.22*ReplyProbability + 0.18*PositiveIntentProbability
                 + 0.16*TrustBuildProbability + 0.14*MeetingConversionProbability
                 + 0.12*ForwardProbability + 0.10*MemoryRetentionProbability
                 + 0.08*RelationshipAdvanceProbability

BrierScore = mean(prediction - outcome)²  // Track every prediction against actual outcomes
if (any persona predicts trust decay) → BLOCK
if (PredictedSuccess < 0.82) → ITERATE until passing
```

---

## PART 6: DEVIATION LADDERS (Quick-Reference)

### Email Deviation
| Lv | Subject | Opening | CTA |
|----|---------|---------|-----|
| **-10** | [No subject] | No greeting, pure command | No CTA — statement only |
| **-5** | Single word: "Tuesday" | Name only (Sarah —) | Implicit — next step obvious |
| **0** | "Quick question" / "Following up" | "Hope this finds you well" | "Let me know your thoughts" |
| **+3** | Specific curiosity gap + number | Names something proving research | Specific + time-bound + friction-removed |
| **+5** | Pattern interrupt — insider knowledge | Reframes their situation in 12 words | Behavioral voltage: loss + scarcity |
| **+7** | Reframes recipient's reality | Changes emotional state in 12 words | Not responding feels like a loss |
| **+10** | Becomes a meme people forward | Changes their emotional state in 12 words | CTA becomes something others study |

### LinkedIn Deviation
| Lv | Perspective | Evidence | Structure |
|----|------------|----------|-----------|
| **-10** | Silence as positioning | Pure assertion | Single period |
| **0** | "5 lessons I learned" | "In my experience" | Wall of text |
| **+3** | Contrarian + evidenced | Named companies + metrics | Hook→story→lesson→CTA |
| **+5** | Original framework | Primary data you collected | Document carousel |
| **+7** | Reframes industry conversation | Contradicts consensus + verifiable | Format that doesn't exist yet |
| **+10** | Creates new industry term | Evidence becomes cited resource | Invented post type others adopt |

---

## PART 7: TARGET PROFILES BY OUTPUT TYPE

| Output | E1 | E2 | E3 | E4 | E5 | L1 | L2 | L3 | L4 | L5 | Min to Ship |
|--------|----|----|----|----|----|----|----|----|----|----|-------------|
| Cold email | +5-7 | +5-7 | +5-7 | +5-7 | +3-5 | — | — | — | — | — | All E ≥ +3 |
| Warm follow-up | +3-5 | +3-5 | +3-5 | +3-5 | +3-5 | — | — | — | — | — | E3 ≥ +3 |
| Client reply | +1-3 | +3-5 | +3-5 | +3-5 | +3-5 | — | — | — | — | — | E3 ≥ +3 |
| Internal | -3+1 | -3+1 | +1-3 | +1-3 | +1-3 | — | — | — | — | — | E3 ≥ +1 |
| Proposal | +3-5 | +5-7 | +5-7 | +5-7 | +5-7 | — | — | — | — | — | All E ≥ +5 |
| Thought leadership | — | — | — | — | — | +5-8 | +5-7 | +5-7 | +5-7 | +5-7 | L1 ≥ +5 |
| Quick take | — | — | — | — | — | +3-5 | +1-3 | +1-3 | +3-5 | +3-5 | L1 ≥ +3 |
| Comment | — | — | — | — | — | +3-5 | +3-5 | — | +3-5 | +3-5 | L4 ≥ +3 |
| DM / text | +1-3 | +1-3 | +3-5 | +1-3 | +3-5 | — | — | — | — | — | E3 ≥ +3 |

---

## PART 8: ANTI-PATTERN REGISTRY

| Anti-Pattern | Why It Fails | Do Instead |
|-------------|-------------|-----------|
| "Hope this finds you well" | Zero information. Signals "I have nothing specific to say about you." | Name something specific about their situation |
| "Just checking in" | Signals neediness. Removes frame. | Add new value or don't send |
| "Would love to chat" | Vague. No specificity. No urgency. | "15 minutes Thursday at 2pm. Agenda: [one specific question]" |
| "Let me know your thoughts" | Passive. No direction. No tension. | "Reply with the part that feels most expensive to leave unchanged" |
| Listing features/services | Vendor behavior. Removes diagnostic frame. | Name the wound. Let them ask about solution |
| Over-explaining | Removes reason to meet. Kills open loop. | Say less. Save diagnosis for the call |
| Exclamation marks | Signals eagerness/neediness. | Period. Always period. |
| "I/we" as first word | Self-centered. | Start with THEIR situation |
| Long paragraphs | Signals "I value my words more than your time" | 1-2 sentences per paragraph. White space is respect |
| Generic subject lines | Won't open. Invisible in inbox. | Specific curiosity gap with number or named situation |

---

## PART 9: MASTER PROMPT (Paste into any LLM)

```
You are the RIG Communications Engine. You produce written communications
that follow the RIG OS doctrine: Wound → Mirror → Autonomy → Qualification → Open Loop.

CHANNEL: [email / LinkedIn post / LinkedIn comment / reply / follow-up / proposal / internal / DM]
RECIPIENT: [description — role, company, situation, what they said/did]
CONTEXT: [what prompted this communication]
DEVIATION TARGET: [+3 / +5 / +7 for each relevant criterion]

RULES:
1. Follow the 5-phase sequence: Wound → Mirror → Autonomy → Qualification → Open Loop
2. BANNED: "just checking in," "following up," "touching base," "would love to chat," 
   "let me know your thoughts," "happy to help," "hope this finds you well," 
   "I wanted to reach out," "quick question," exclamation marks
3. Every sentence earns its place. If removing it changes nothing, remove it.
4. Name the specific wound — not "many companies struggle" but the exact pattern costing THIS recipient money
5. Preserve autonomy — never chase, never pressure, never remove agency
6. Maintain qualification frame — you are evaluating THEM
7. End with open loop — something unresolved creating forward pull
8. Recipient should receive MORE value than expected (RPE > 0)
9. Communication should be shorter than they expect
10. Score output against all relevant criteria before presenting

OUTPUT FORMAT:
1. The communication itself
2. Scoring: [each criterion with score]
3. Prediction: [what each buyer persona would do with this]
4. Improvement notes: [what would push each criterion +1 higher]
```

---

## PART 10: ENSEMBLE WRITER ARCHITECTURE

When producing flagship content, use the 5-agent ensemble:

1. **Agent E (EminemDensity):** sonic velocity, syllable flips, internal rhyme
2. **Agent H (HemingwayCompression):** blunt force, short sentences, no decoration
3. **Agent D (DidionCadence):** controlled dread, quiet endings
4. **Agent M (McCarthyRhythm):** biblical cadence, no punctuation
5. **Agent W (WallaceRecursion):** recursive footnotes, self-aware tangents

Each drafts the same angle. Score all 5 on BDF30. Ship max BDF30. Only swarm the winner.

---

## PART 11: COMPOUNDING MEMORY

Every shipped artifact records:
```
{
  archetype_used, bdf30_score, actual_engagement, brier_accuracy,
  winning_hook, villain_class_used, catchphrase, what_worked, what_failed
}
```

**MemoryCompoundingScore** for content series:
```
MCS = 0.30*DoctrineThreadContinuity + 0.25*OptimalSpacingAdherence
    + 0.25*CatchphraseRecurrence + 0.20*VillainClassConsistency
```
Optimal ISI (Inter-Session Interval) for LinkedIn series: 3-6 days. Validated: Latimier et al. 2020 — 150% recall improvement with optimal spacing. Evidence: 9/10.

---

## PART 12: REACTANCE MITIGATION

Validated by Li & Shi 2025 meta-analysis (k=53 studies, r ≈ .20 threshold).

```
ReactanceRisk = Σ(ThreatMarkers × FreedomImportance) / TotalSentences
Gate: ReactanceRisk < 0.20
```

Gain vs loss framing does NOT significantly affect reactance — RIG's loss-framing approach ("waiting is not neutral") is safe. Imperative commands ARE the threat. The banned phrases list is a reactance mitigation engine.

---

## PART 13: OPERATIONAL SUMMARY

**To write any RIG communication:**
1. Identify the wound (specific, systemic, evidenced)
2. Mirror their reality (accurate, non-judgmental)
3. Preserve autonomy (no chasing, no banned phrases)
4. Qualify (they earn the next step, not you)
5. Open loop (unresolved tension, NOT generic CTA)
6. Score against formulas (CommRawScore ≥ 0.65, relevant channel gates)
7. Run prediction swarm (consensus > 0.65)
8. Ship if all gates clear

**For idea generation (full pipeline):**
Load `tournament-architecture.md` for the 6-round tournament.
Load `deviation-questions.md` for the 50 forcing-function questions.
Load `signal-detection-repos.md` for 20 GitHub signal detection tools.
Load `consensus-research-mapping.md` for peer-reviewed formula validation.
Load `idp-formula-card.md` for the IdeaDeviationPotential scoring card.

**The governing principle:** The recipient expected a generic vendor email — they received a diagnostic insight. That delta IS the Reward Prediction Error. That's what creates the dopamine signal. If it could have been written by any competent consultant, it fails.
