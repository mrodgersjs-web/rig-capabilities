# RIG Communications V10 — Near-Term Roadmap (V11 → V12)

## V11: Autonomous Signal Detection

**Goal:** Replace manual topic selection with 7 autonomous signal-layer agents running continuously.

### Architecture

Each signal agent is a specialized CrewAI/LangGraph agent that monitors one signal layer:

```
Signal Agent Fleet:
├── S1: Orthodoxy Scanner — monitors industry reports, conference keynotes, top LinkedIn voices
├── S2: Wound Listener — monitors Reddit, forums, G2 reviews, Slack communities
├── S3: Vocabulary Tracker — monitors arXiv abstracts, product launches, VC decks
├── S4: Villain Spotter — monitors post-mortems, audit reports, public failures
├── S5: Proof Gap Detector — monitors competitor content for unsupported claims
├── S6: Format Exhaustion Monitor — monitors LinkedIn feed for format cloning frequency
└── S7: Adjacent Collision Scanner — monitors academic papers from unrelated fields
```

### Implementation Plan

**Phase 1: Infrastructure (Week 1-2)**
- [ ] Deploy CrewAI orchestrator (`src/signal_orchestrator.py`)
- [ ] Implement SignalCard persistence in SQLite (`src/signal_store.py`)
- [ ] Deploy STORM integration for research depth (L1-L2 layers)
- [ ] Deploy Alibaba DeepResearch for automated synthesis
- [ ] Implement daily signal harvest cron job

**Phase 2: Agents (Week 3-4)**
- [ ] Build Orthodoxy Scanner agent with Consensus.app integration
- [ ] Build Wound Listener agent with Reddit/forum APIs
- [ ] Build Vocabulary Tracker agent with arXiv API
- [ ] Build Villain Spotter agent with news/regulatory APIs
- [ ] Build Proof Gap Detector with semantic analysis
- [ ] Build Format Exhaustion Monitor with feed analysis
- [ ] Build Adjacent Collision Scanner with cross-domain paper search

**Phase 3: Integration (Week 5-6)**
- [ ] Wire signal agents → tournament pipeline
- [ ] Implement SignalCard confidence scoring
- [ ] Implement decay rate detection ("write NOW" urgency)
- [ ] Add signal quality feedback loop (did this signal produce a winner?)

### Key Files to Build
```
src/signal_orchestrator.py   # CrewAI fleet manager
src/signal_store.py          # SignalCard persistence
src/agents/s1_orthodoxy.py   # Orthodoxy Scanner
src/agents/s2_wound.py       # Wound Listener
src/agents/s3_vocabulary.py  # Vocabulary Tracker
src/agents/s4_villain.py     # Villain Spotter
src/agents/s5_proof_gap.py   # Proof Gap Detector
src/agents/s6_format.py      # Format Exhaustion Monitor
src/agents/s7_adjacent.py    # Adjacent Collision Scanner
```

### Repos to Integrate
- STORM (Stanford): Multi-perspective research agent
- Alibaba DeepResearch: Automated synthesis
- SpaCy + Transformers: NLP pipeline
- arXiv API: Vocabulary drift tracking

---

## V12: Automated Idea Tournament

**Goal:** Automate the full 6-round tournament pipeline using CrewAI + LangGraph.

### Architecture

```
CrewAI Tournament Orchestrator
├── Round 1: Angle Generator Agent (transforms SignalCards → AngleCards)
├── Round 2: IDP Scorer Agent (scores and culls by IDP formula)
├── Round 3: Adversarial Trio
│   ├── Plagiarism Detector Agent
│   ├── Steelman Agent (defends the orthodoxy)
│   └── Audience Simulator Agent
├── Round 4: Research Validator Agent (proof density + mechanism check)
├── Round 5: Ensemble Writer (5 archetype agents in parallel via AutoGen)
│   ├── EminemDensity Agent
│   ├── HemingwayCompression Agent
│   ├── DidionCadence Agent
│   ├── McCarthyRhythm Agent
│   └── WallaceRecursion Agent
└── Round 6: Learning Agent (Brier calibration)
```

### Implementation Plan

**Phase 1: LangGraph Tournament Graph (Week 1-2)**
- [ ] Build LangGraph state machine for tournament rounds
- [ ] Implement conditional branching (kill → skip remaining rounds)
- [ ] Implement IDP scoring with formula registry
- [ ] Implement adversarial agents with structured debate prompts

**Phase 2: AutoGen Ensemble Writer (Week 3-4)**
- [ ] Deploy AutoGen group chat with 5 archetype agents
- [ ] Implement parallel draft generation
- [ ] Implement BDF30 scoring on all 20 drafts
- [ ] Implement max-BDF winner selection

**Phase 3: Pipeline Integration (Week 5-6)**
- [ ] Wire V11 signal agents → V12 tournament
- [ ] Implement tournament logging + reporting
- [ ] Add manual override capability (human picks winner)
- [ ] Deploy tournament results to memory layer

### Key Files to Build
```
src/tournament_orchestrator.py    # CrewAI orchestrator
src/tournament_graph.py           # LangGraph state machine
src/agents/idp_scorer.py          # IDP scoring agent
src/agents/plagiarism_detector.py # Plagiarism check
src/agents/steelman.py            # Orthodoxy defense
src/agents/audience_simulator.py  # Scroll/engagement prediction
src/agents/research_validator.py  # Proof density validation
src/writers/ensemble_writer.py    # AutoGen ensemble orchestrator
src/writers/eminem_density.py     # Archetype agent
src/writers/hemingway.py          # Archetype agent
src/writers/didion.py             # Archetype agent
src/writers/mccarthy.py           # Archetype agent
src/writers/wallace.py            # Archetype agent
```

### Repos to Integrate
- CrewAI: Multi-agent orchestration
- LangGraph: Stateful graph-based workflows
- AutoGen: Parallel agent conversation framework
- OpenPrompt: Structured prompt templates for angle generation

### Target Metrics
- Tournament completes in < 10 minutes (50 angles → 1 winner)
- BDF30 selection rate: > 0.85 (winner exceeds gate)
- Adversarial kill rate: 40-60% (healthy — not all survive)
- Ensemble diversity: All 5 archetypes produce measurably different drafts (CraftCoefficient spread > 0.15)
