# RIG Communications V10 — Long-Term Roadmap (V13 → V15)

## V13: Ensemble Writer System

**Goal:** Full parallel draft generation across 5 archetypes with automated scoring and selection.

### AutoGen Ensemble Architecture

```
AutoGen Group Chat:
  Orchestrator Agent (round-robin manager)
    ├── EminemDensity Worker
    │   Optimizes: InternalRhymeRate, SyllabicPercussion, SemanticInversion, MultiSyllabicMatch, EnjambmentLeverage
    │   Prompt injection: "Write with sonic velocity. Syllable flips. Internal rhyme. Multi-syllabic density."
    │
    ├── HemingwayCompression Worker
    │   Optimizes: Compression, Restraint, BluntForce, SentenceLength
    │   Prompt injection: "Short sentences. No decoration. Wound lands clean. Cut every word that can be cut."
    │
    ├── DidionCadence Worker
    │   Optimizes: ObservationSpecificity, SocialDetail, ImplicationDelay, QuietEnding
    │   Prompt injection: "Cool observation → social detail → uncomfortable implication → quiet devastating ending."
    │
    ├── McCarthyRhythm Worker
    │   Optimizes: BiblicalCadence, PunctuationRemoval, ForwardMotion, Repetition
    │   Prompt injection: "No punctuation unless absolutely necessary. Biblical cadence. Relentless."
    │
    └── WallaceRecursion Worker
        Optimizes: Recursion, Footnotes, SelfAwareness, MetaCommentary, Digression
        Prompt injection: "Recursive footnotes. Self-aware tangents. The footnote becomes more important than the main text."
```

### Implementation Plan

- [ ] Deploy AutoGen group chat with 5 worker agents
- [ ] Implement archetype-specific prompt injection from docs
- [ ] Deploy parallel generation (all 5 draft simultaneously)
- [ ] Implement CraftCoefficient scoring (max across archetypes)
- [ ] Implement BDF30 scoring on all drafts
- [ ] Implement max-BDF winner selection
- [ ] Add draft comparison report (what each archetype produced differently)
- [ ] Store all drafts in tournament memory for learning

### Key Files
```
src/writers/orchestrator.py      # AutoGen group chat manager
src/writers/scoring.py           # BDF30 + CraftCoefficient on drafts
src/writers/comparison.py        # Cross-archetype draft comparison
```

---

## V14: Self-Calibrating Brier Loop

**Goal:** Every shipped artifact recalibrates the formulas. The system gets smarter with every communication.

### Architecture

```
Post-Ship Pipeline:
  1. Artifact ships (LinkedIn post, cold email, reply)
  2. Engagement data collected (impressions, comments, shares, DMs, conversions)
  3. Brier Score computed: mean((prediction - outcome)^2) per persona
  4. Persona weights updated (accurate personas up-weighted)
  5. Formula weights flagged for recalibration (quarterly review)
  6. Winning patterns stored in institutional memory
```

### Brier Calibration Formula

```
BrierScore = mean((forecastProbability - actualOutcome)^2)

Per-persona tracking:
  - Skeptical Buyer: reply_probability vs actual reply rate
  - Technical Evaluator: share_probability vs actual share rate
  - Industry Lurker: share_probability vs actual share rate

Weight update rule:
  new_weight = old_weight * (1 - BrierScore)  // Lower Brier → higher weight
  Renormalize all weights to sum to 1.0
```

### Implementation Plan

- [ ] Deploy Langfuse integration for LLM observability
- [ ] Implement engagement data collection pipeline (LinkedIn API, email tracking)
- [ ] Implement Brier Score computation per artifact
- [ ] Implement persona weight updates (rolling 90-day window)
- [ ] Implement quarterly formula recalibration (human-reviewed)
- [ ] Build calibration dashboard
- [ ] Store calibration history for audit trail

### Key Files
```
src/calibration/brier_tracker.py     # Brier Score computation
src/calibration/persona_weights.py   # Persona weight recalibration
src/calibration/formula_weights.py   # Formula weight recalibration
src/calibration/dashboard.py         # Calibration visualization
```

### Repos to Integrate
- Langfuse: Full pipeline observability
- Papr: Institutional memory
- LinkedIn API: Engagement tracking
- Consensus.app: Research validation

---

## V15: Studio-Grade Content Pipeline

**Goal:** Signal → Idea → Research → Draft → Score → Swarm → Ship → Learn. Zero human bottleneck except final approval gate.

### Architecture

```
RIG Communications Studio:
┌─────────────────────────────────────────────────────────────┐
│ SIGNAL LAYER: 7 autonomous agents scanning continuously     │
│   S1-S7 produce SignalCards daily with confidence scores    │
├─────────────────────────────────────────────────────────────┤
│ TOURNAMENT LAYER: 6-round automated pipeline               │
│   50 angles → 20 IDP-scored → 8 adversarial → 4 validated  │
├─────────────────────────────────────────────────────────────┤
│ RESEARCH LAYER: 5 depth layers                             │
│   L1:Surface → L2:Adjacent → L3:Academic → L4:Contrarian → │
│   L5:Primary (your own data)                               │
├─────────────────────────────────────────────────────────────┤
│ WRITING LAYER: 5 archetype ensemble                       │
│   Eminem | Hemingway | Didion | McCarthy | Wallace          │
│   → 20 drafts scored on BDF30 + CraftCoefficient            │
├─────────────────────────────────────────────────────────────┤
│ SWARM LAYER: 8-persona prediction                          │
│   Skeptical Buyer → Senior Executive → Trust Delta → Ship? │
├─────────────────────────────────────────────────────────────┤
│ CALIBRATION LAYER: Self-improving                          │
│   Brier loop → quarterly recalibration → compounding memory│
├─────────────────────────────────────────────────────────────┤
│ STUDIO DASHBOARD: Visual pipeline                          │
│   Signal feed → Tournament → Drafts → Scores → Swarm → Ship│
│   Human decision gate: "Approve" or "Reroute"              │
└─────────────────────────────────────────────────────────────┘
```

### Dashboard Features

**Signal Feed Panel:**
- Live feed of SignalCards from 7 layers
- Color-coded by urgency: RED (decaying fast, write NOW), YELLOW (growing), GREEN (stable)
- Click to promote signal to tournament

**Tournament Panel:**
- Live view of current pipeline: 50 → 20 → 8 → 4 → 1
- Each round shows survivor count and kill reasons
- Click any angle to see full AngleCard details

**Draft Panel:**
- Side-by-side view of all 5 archetype drafts
- Sortable by BDF30, CraftCoefficient, CatchphraseScore
- Click to expand full draft text
- "Approve" or "Reroute to different archetype"

**Swarm Panel:**
- 8-persona prediction grid with Trust Delta heatmap
- Consensus score with history trend
- Individual persona Brier accuracy display

**Calibration Panel:**
- Formula weight history (last 4 quarters)
- Brier Score trend per persona
- Winning pattern registry (top hooks, villain classes, catchphrases)

### Implementation Plan

- [ ] Build Studio Dashboard (React/Next.js or Streamlit)
- [ ] Wire all pipeline components to dashboard API
- [ ] Implement human approval gate (Approve/Reroute buttons)
- [ ] Deploy real-time signal monitoring
- [ ] Implement cross-node pipeline sync (fleet-wide)
- [ ] Deploy to Cloudflare tunnel (studio.rigcommunications.ai)
- [ ] Add multi-user support for team content operations

### Key Files
```
src/studio/dashboard.py            # Streamlit app
src/studio/api.py                  # FastAPI backend
src/studio/components/             # Dashboard UI components
src/studio/approval_gate.py        # Human-in-the-loop approval
website/studio.html                # Public-facing studio landing page
```

### Target Metrics
- Time from signal detection to draft: < 5 minutes
- Pipeline throughput: 10+ full tournament runs per day
- Brier calibration accuracy: > 0.85 (quarterly rolling average)
- Human approval rate: > 70% (pipeline produces shippable artifacts)
- Content output: 20-30 artifacts per day across all channels

---

## Total Build Summary

| Version | Components | Status |
|---------|-----------|--------|
| V10 | Protocol, formulas, questions, templates, scoring.py, gates.py, formulas.py, tournament.py, swarm.py | ✅ DONE |
| V11 | 7 signal agents, STORM, DeepResearch, SignalCard persistence | 🔨 NEXT |
| V12 | CrewAI tournament, LangGraph graph, AutoGen ensemble writer, 5 archetype agents | 📋 PLANNED |
| V13 | Parallel draft generation, max-BDF selection, CraftCoefficient optimization | 📋 PLANNED |
| V14 | Langfuse observability, Brier loop, quarterly recalibration, Papr memory | 📋 PLANNED |
| V15 | Studio dashboard, Cloudflare deployment, human approval gate, fleet sync | 🎯 TARGET |
