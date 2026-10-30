# RIG Communications OS — v0→v20 Master Plan

**Status:** v0 audit complete (2026-09-06). Design baseline for the unified writing system.
**Owner:** Mike Rodgers. Execution body: Jake PAI fleet under TAC v2/v3 doctrine.
**Scope:** Every surface Mike writes on, driven by coding agents from one canonical home:
prompts, film/movie scripts, resumes, LinkedIn (Alfred), songs, work emails, Substack,
novels, engineering specs, code, love notes to James, and the research/prompt-writing that
feeds all of them.

---

## 0. What v0 Found (audit of record, 2026-09-06)

### 0.1 Asset census

| Layer | Reality | Path / evidence |
|---|---|---|
| Writing skills (Hermes) | ~100 installed (alfred×7, rig-content-atelier, rig-marcus-long-form, rig-yara-short-form, rig-cyrus-line-editor, rig-eleanor-editor-in-chief, rig-voice-engineering, content-voice-fingerprint-extractor, voice-builder, newsletter-voice, linkedin-studio, 40+ gtm-content-*) | `~/.hermes/skills/` |
| Writing skills (Claude) | ~75, near-parity with Hermes minus alfred suite | `~/.claude/skills/` |
| Writing skills (agents root) | **6 — severe drift** (content-command-center, head-of-content, rig-linkedin-agent, rig-sales-outreach, yara-rule-authoring) | `~/.agents/skills/` |
| Behavioral science suite | 13 bx-* skills + council-of-high-intelligence, installed in ALL four roots (claude, codex, hermes, agents) | `~/.hermes/skills/bx-*` |
| rig-communications (public) | `rodgemd1-lgtm/rig-communications` — "RIG Communication Protocol V10": `rig_comm` Python package (core, formulas, gates, scoring, swarm, tournament, doctrine, prompt, cli, integrations: autogen/crewai/langgraph/mcp/openai_style), 7 templates, 15 doctrine docs, agentforge workflows, tests | GitHub, last push 2026-06-15 |
| rig-intelligence departments | `behavioral-science/`, `content/`, `linkedin/`, `film/`, `gtm/` exist as departments | `rig-intelligence/departments/` |
| rig-capabilities (canonical home) | 29 canonical skills, **zero communications capabilities** registered; docs/ conventions established; `bin/rig-capabilities add/install` is the registration path | `/Users/rig128gb/Developer/rig-capabilities` |

### 0.2 Knowledge census (Recall — app.recall.it, 853+ cards)

Wound Protocol (8 core wounds, depth L1–L5) · Euphoria Protocol (8 states E1–E8 + Emotional
Symphony scoring, target EAS ≥15) · Master Composition System (20 criteria, 6 formulas) ·
**RIG OS Master Communications Protocol V1** (unified email/LinkedIn/Slack/DM, 8σ scoring,
per-output-type sigma targets) · Email Drafting+Reply Protocol (Wound→Mirror→Autonomy→
Qualification→Open Loop) · Email Reply Scoring Algorithm (W1 "I'm Not Enough", W2 "I Don't
Belong", …) · SUNO Billboard Engine (song architecture) · Communications Deviation Engine V2
(craft layer: Eminem / DFW / Didion / McCarthy) · Domain Deviation Registry (18 domains,
-10→+10) · LinkedIn Protocol V2 (8σ depth + prediction swarm) · Chase Score (website +
LinkedIn platform math).

**The wound IP lives ONLY in Recall.** Nothing on disk. That is the single biggest
resilience gap this plan closes (v3).

### 0.3 Tooling census (probed live)

- `yt-dlp` 2026.08.19 ✓ · `youtube-transcript-api` ✓ · `scrapling` 0.4.12 ✓
- EXA_API_KEY present (`~/.hermes/.env`); exa MCP configured in Claude + Codex
- youtube-transcript MCP configured in Claude
- Consensus: NO API key on disk; consensus.app usage pattern documented in
  `rodgemd1-lgtm/rig-communications/docs/CONSENSUS_RESEARCH.md` — web access only until keyed
- Proven corpus pipeline: `~/.rig/corpus/sonny-sangha/` (1.6 GB, 351 transcripts, 7.39M words)
  — manifest.jsonl → cleaned transcripts → 30 extraction workers → EXTRACTIONS.json.
  `rig-dept-substrate-intake/scripts/clean_auto_subs.py` is the auto-sub cleaner.

### 0.4 Gap register (v0 → must close)

1. No canonical communications domain in rig-capabilities (the connective tissue is missing).
2. Wound/Euphoria/Comms-Protocol IP exists only inside Recall (no disk durability, no agent access at write time).
3. No writing-craft transcript corpus (sonny-sangha covers agentic coding, not writing craft).
4. `~/.agents/skills` drift (6 vs ~100 writing skills).
5. Three things named "rig-communications" (this workspace branch, the rodgemd1-lgtm repo, the target domain) — naming collision.
6. No per-surface engines for: resumes, songs, novels, specs, code-as-writing, love notes.
7. No closed-loop verification or measurement on any writing lane (alfred publishes; nobody scores outcomes back into design).
8. No Gate-D-consistent private lane for James notes (must never ride the public stack).

### 0.5 Naming resolution (decided here, binding)

- `rig-communications` (skill domain) → canonical home: `rig-capabilities/capabilities/skills/rig-communications*/`.
- `rodgemd1-lgtm/rig-communications` → becomes the **public mirror** (federated release target, v17).
- This workspace (`orca/workspaces/rig-intelligence/rig-communications`) → just a branch of rig-intelligence; departments stay put and get **wired**, not moved.

### 0.6 North star

> Every artifact any agent writes for Mike — a prompt, a post, a scene, a chorus, a resume
> bullet, a love note — is generated from ONE voice fingerprint, grounded in ONE wound +
> behavioral corpus, scored by ONE deterministic gate stack, and its outcome feeds back into
> the corpus. Agents stop "writing"; they operate the communications engine.

---

## 1. Design method

- **RIG systems thinking:** the estate is one stock-and-flow system — corpus (stock) →
  engines (flow) → artifacts (stock) → outcomes (flow) → calibration (feedback into corpus).
  Every version strengthens a stock, a flow, or a feedback loop; none is decoration.
- **Strategy Studio (A4 routing):** lattice OK (588 cells). Baseline weakness: the current
  estate is a *median ensemble* — many strong skills, no shared state, no feedback. The
  v0→v20 ladder is the deviation candidate set; v20 is the +σ survivor. Prediction
  limitation: outcome calibration is UNMEASURED until v10/v11 produce real resolutions
  (frozen multiclass Brier). Full harness run (`rig-strategy-studio harness run` with this
  plan as candidate A vs. "upgrade alfred only" as candidate B vs. "do nothing" as baseline)
  is scheduled as a **v1 gate**, not executed at design time.
- **TAC v2/v3:** plan-artifact-persist (this doc), foundation-before-fanout (v1–v3 before
  engines), workflow-first (deterministic scrapers/gates before agent judgment),
  correction-to-memory (every repeated writing correction lands in the voice fingerprint,
  not in chat), closing-loop (nothing is "written" until verified).

---

## 2. The version ladder (21 versions × 10 layers = 210 layers)

Each version lists its 10 layers. Layers are capabilities, not tasks; the todo list carries
the executable tasks.

### v0 — Reality Audit *(complete)*
1. Writing-skill census across 4 harness roots with drift map
2. Repo census: rig-capabilities / rig-intelligence / rig-communications public
3. Recall wound-IP census (36+ cards identified)
4. bx-suite install map (13 skills × 4 roots)
5. Tooling probes (yt-dlp, youtube-transcript-api, scrapling, exa, MCP configs)
6. Corpus census (sonny-sangha pattern as reference implementation)
7. 12-surface enumeration of Mike's writing life
8. Gap register (8 gaps, §0.4)
9. Naming collision resolution (§0.5)
10. North-star definition + this plan persisted

### v1 — Canonical Home
1. `capabilities/skills/rig-communications-core/` seeded from `rig_comm` V10 (formulas, gates, scoring, swarm, tournament)
2. Registration via `bin/rig-capabilities add` (index-fresh, capability_register.csv row)
3. PROVENANCE.md → rodgemd1-lgtm upstream + license
4. Outcome-lane mapping: `content-publishing` lane entries
5. `capabilities/skills/rig-communications-doctrine/` — the 15 doctrine docs normalized
6. `capabilities/commands/write.md` — `/write <surface>` slash command stub
7. done_when checks per capability (executable: gate CLI exits, import tests)
8. ACL policy entries (internal; love-notes lane marked private from day one)
9. Concept tags for context-fabric (writing, voice, wounds, behavioral, per-surface)
10. First `capability_install` into `claude` harness as wiring proof + strategy-studio harness gate run

### v2 — Writing-Craft Corpus
1. Target list `data/corpora/writing-craft/TARGETS.md` — 8 surfaces × 3–4 channels, exa-validated
2. Scraper: yt-dlp primary, youtube-transcript-api fallback (per rig-dept-substrate-intake)
3. scrapling lane for non-YouTube supplements (author blogs, Substack craft posts)
4. Corpus folder `data/corpora/writing-craft/<surface>/<channel>/<video_id>.txt` in rig-capabilities
5. `manifest.jsonl` per surface (video_id, channel, surface, url, words, fetched_at, sha256)
6. Auto-sub overlap-collapse cleaning (`clean_auto_subs.py` pattern, vendored)
7. Substrate sidecars per rig-substrate-format-builder (substrate.json v1 schema)
8. GBrain source registration `writing-craft` (rig-gbrain-substrate)
9. Obsidian/JakeStudio mirror via memory bridge
10. Coverage + freshness report (per-surface transcript counts, word counts, last-fetch)

### v3 — Wound Injection (Recall → disk)
1. Export the 8-wound protocol cards (jake_recall `get` on wound card ids) → `wounds/core-wounds.md`
2. Depth layers L1–L5 per wound → `wounds/depth-layers.md`
3. Euphoria Protocol E1–E8 + Emotional Symphony scoring → `euphoria/`
4. Wound→Mirror→Autonomy→Qualification→Open Loop sequence card → `sequences/wmaqo.md`
5. Master Communications Protocol V1 → `doctrine/master-comms-v1.md` (sigma targets per output type)
6. Email Reply Scoring Algorithm (W1/W2… reply strategies) → `gates/email-reply-scoring.md`
7. SUNO Billboard Engine → `surfaces/songs/suno-architecture.md`
8. Craft archetypes (Eminem/DFW/Didion/McCarthy) → `voice/craft-archetypes.md`
9. Domain Deviation Registry (18 domains) → `voice/sigma-targets.md`
10. Wound-detection classifier spec (bx-need-architect × wound library) → `behavior/wound-classifier.md`
11. *(delta-sync cron spec: weekly Recall re-export so disk never goes stale — feeds v15)*

### v4 — Behavioral-Science Fusion
1. bx-need-architect → audience need-hierarchy generator per surface
2. bx-emotion-cartographer → emotional journey template per artifact class
3. bx-decision-modeler → reader choice model (reply / scroll-past / book / buy)
4. bx-committee-simulator → B2B surfaces (proposals, specs, PE memos)
5. bx-influence-designer → persuasion strategy with effect-size discipline
6. bx-intervention-designer → COM-B mapping for every CTA
7. bx-measurement-steward → trustworthiness ranking of comms metrics
8. bx-falsifier → adversarial refutation of predicted artifact performance (pre-ship)
9. bx-wren → decision-lattice orchestration per high-stakes artifact
10. council-of-high-intelligence → persona panel for flagship pieces

### v5 — Voice Fingerprint v2
1. Merge content-voice-fingerprint-extractor + voice-builder + rig-voice-engineering into one `voice/` module
2. 12-surface register map (operator/LinkedIn, intimate/James, recruiter-professional, novelist, screenwriter, songwriter, engineer-spec, prompt-engineer, email-work, Substack-essayist, code-documenter, job-seeker)
3. Banned-word audit (locked list, deterministic check)
4. Signature-vocab frequency targets
5. Sentence-length distribution per surface
6. Hook-strength scoring model
7. Manifesto-fit check (RIG doctrine alignment)
8. Wound-authenticity gate (Mike's real wounds only; manufactured pain = red)
9. Writing-sample corpus per surface → `voice/samples/<surface>/`
10. Voice drift detector (per-artifact delta vs fingerprint, shipped in gate stack)

### v6 — Surface Engines (the 12 writers)
1. `prompts` engine — agent prompts (tac-v2/v3 patterns + CO-STAR + RIG prompt doctrine)
2. `film-scripts` engine — screenplay format, beat sheets, corpus-grounded scene craft
3. `resumes` engine — per-target variants from LinkedIn + job-cockpit data (julie integration)
4. `linkedin` engine — alfred suite re-platformed onto engines (chaos pipeline, drafter, publisher unchanged in behavior)
5. `songs` engine — SUNO architecture + lyric craft corpus
6. `emails` engine — work-context email (his actual jobs, per resume/LinkedIn)
7. `substack` engine — marcus long-form + eleanor editorial direction
8. `novels` engine — long-form fiction with wound-depth character architecture
9. `specs` engine — engineering specs, OpenSpec BDD format
10. `code` engine — code-as-writing: naming, comments, docs, commit messages
11. `love-notes` engine — James lane; private ACL; authenticity gate supreme; **never autonomous, never federated**
12. `rig-comm` runtime — one CLI routing surface → template → voice → corpus → gates

### v7 — Quality Gates
1. AGF (AntiGenericForce) threshold per surface (default ≥85)
2. Voice score vs fingerprint v2
3. Wound-resonance ≥1 named wound (exempt: specs, code)
4. Behavioral-fit: bx-falsifier pass
5. Per-surface rubrics wired: BDF30 (email), Chase Score (LinkedIn/web), EAS (songs), screenplay beat coverage
6. Sigma targets enforced per output type (Master Comms Protocol table)
7. Fabrication detector: every number needs a source or gets struck
8. Gate-D wiring on all outward lanes (publish/send/spend)
9. Deterministic gate CLI (stdlib, exit codes, JSON envelopes — rig-capabilities style)
10. Planted-failure self-test per gate (adversarial-verification-loop: red-capable or theater)

### v8 — Closed Loops
1. Builder/Verifier split per surface engine (tac-closing-loop)
2. Cross-family verifier dispatch (iqrsqpi-v20 engine-dispatched)
3. Max-3 correction loops then human escalation
4. `tac close-gate` sealed claims — no "shipped" without sealed evidence
5. SWS stage machine for long projects (novel chapters, feature scripts)
6. Stochastic coverage for voice-critical pieces (N≥2 drafts, distinct frames, convergence read)
7. Review gate before publish (v3.review-before-merge)
8. Real-path verification (published URL fetched logged-out; email open/reply event observed)
9. ProofPacket per shipped artifact (proofpacket_seal, sha256-bound)
10. Loop telemetry: red rates, correction counts, per-surface loop cost

### v9 — Harness Wiring
1. `capability_install` → claude, codex, hermes, agents, omp (ledgered)
2. Comms card in `capabilities_context_pack` (auto-surfaced for writing intents)
3. Route-table entries: intent → surface engine (`capabilities_route`)
4. agents-root drift repair (6 → parity via canonical installs)
5. Session-start detection: writing task → surface engine auto-load
6. MCP exposure of write/score/route tools from rig-capabilities server
7. Prime Jake fleet contract: writing workers inherit comms context (no re-derivation)
8. OMP + pi surfaces compiled (tac surfaces pattern)
9. Doctor: every harness loads identical comms version (drift = red)
10. Live-status probes: wired ≠ loaded ≠ running (capabilities_live_status per lane)

### v10 — Measurement
1. LinkedIn outcome telemetry (rig-linkedin-scrape engagement → scoreboard)
2. Email funnel join (outbound_funnel.db funnel_events)
3. Resume pipeline tracking (job cockpit application outcomes)
4. Substack metrics ingestion
5. Song feedback lane (SUNO plays, James/friend feedback where shareable)
6. Per-surface scoreboard JSONs (dated, append-only)
7. Weekly aggregate report (tac weekly-report pattern)
8. Drafted-vs-shipped delta tracking (what gates actually filter)
9. Data-quality gates (rig-honest-scoring: no stale, no fake-zero scorecards)
10. Public dashboard surface (rigds backend pattern)

### v11 — Calibration
1. Brier scoring on predicted artifact performance (per surface, frozen multiclass)
2. Calibration ledger (prediction → resolution, append-only)
3. Sigma-target recalibration from observed outcomes
4. Voice fingerprint versioning from winning artifacts
5. Wound efficacy ranking (which wounds measurably land per audience)
6. bx model validation vs observed reader behavior
7. Template kill/keep decisions from performance data
8. Monthly calibration report
9. Prediction-swarm weight updates
10. Honest UNMEASURED state until ≥N resolutions per surface (no premature confidence)

### v12 — Audience Lattice
1. James persona model (private lane only)
2. Recruiter/hiring-manager models per target role family
3. LinkedIn ICP personas (8 verticals, wound-mapped)
4. Film producer/reader models (coverage-style rubrics)
5. LLM-as-reader model for the prompts surface
6. Substack reader segments
7. B2B committee maps (bx-committee-simulator outputs persisted)
8. Need-state hierarchies per persona (bx-need-architect, disk-persisted)
9. Emotional journey templates per persona × surface
10. Persona-conditioned generation (one draft per persona, tournament selection)

### v13 — Deviation Integration
1. 40 deviation engines mapped to writing surfaces
2. Per-surface polar cards (-σ/+σ definitions)
3. ±30σ ladder for drafts (physics gates for outward claims)
4. Physics-first short-circuit on factual/outward artifacts
5. Robust-MAD-Z scoring vs corpus baselines
6. Mesh synthesis: 3–7 candidates → survivor (REEF+CUCKOO+LÉVY)
7. Engine rotation schedule for recurring content
8. Deviation budget per artifact class (novel > post > email)
9. Anti-median statistics computed from the writing-craft corpus
10. Deviator doctor for the comms lane (rig-deviator-status extension)

### v14 — Multimodal
1. Image per artifact (rig-image-atelier hooks)
2. Film scripts → rig-film-studio pre-viz handoff
3. Song demos via SUNO generation
4. LinkedIn cards/thumbnails (rig-thumbnail-card)
5. Novel cover/mockup lane
6. Spec diagrams auto-generated (mermaid/SVG)
7. Code→docs→video explainers (pr-to-video for his repos)
8. Voice memo → polished text lane (transcription → surface engine)
9. Love notes → physical/letterpress artifacts (Gate-D, private)
10. Media ledger for every generated asset (media-use resolve)

### v15 — Cron Fleet
1. Daily LinkedIn ops re-platformed (alfred crons → engine calls, same cadence)
2. Weekly Substack cycle
3. Resume-variant refresh per live job target
4. Corpus freshness scrape (new videos from target channels, weekly)
5. Recall wound-library delta sync (weekly re-export)
6. Calibration rollup (weekly)
7. Scoreboard publishing (daily)
8. Self-healing monitor over all comms crons (jake-sprint-monitor pattern)
9. Cron registry + proof files per run (hermes jobs.json)
10. Kill switches + cooldowns on every loop (tac agent-loop-bound)

### v16 — Memory Flywheel
1. Every artifact → GBrain (semantic recall at next write)
2. Every artifact → Obsidian JakeStudio mirror
3. Memory OS events per publish/draft
4. Winners → exemplar library (great_example per surface skill)
5. Losers → rejected-patterns library
6. Session learnings → refinements ledger (rlm_refine_record)
7. Cross-harness consistency (memory-drift-sentinel)
8. Corpus distillation → doctrine candidates (rig-doctrine-forge)
9. Context-pack regeneration from fresh memory
10. Pruning policy (library-surgeon: unverifiable/unused assets amputated)

### v17 — Federation & API
1. `rodgemd1-lgtm/rig-communications` upgraded to v2.0 (engines + gates back-ported)
2. MCP endpoints: write / score / route / voice-check
3. CLI `rig-comm write --surface <s> --brief <b>`
4. Template API (render surface template + voice fingerprint)
5. Scoring-as-a-service (gate stack callable)
6. Publish webhooks
7. Fleet/partner ACL policy (public vs internal vs private lanes)
8. Docs site (website/ → full surface docs)
9. Versioned releases + changelogs (rig-doctrine-versioner)
10. Public proof surface (case studies + sealed ProofPackets)

### v18 — Self-Improvement
1. RLM traces on every engine run (run_start / step_record / run_finish)
2. rlm_analyze per surface engine (quality trends, failure modes)
3. Staged improvement candidates (rlm_improve — never auto-applied)
4. round-amplifier rounds on weakest comms capabilities
5. skill-crystallizer: 3× success → executable procedure
6. determinism-miner: repeated agent writing behavior → deterministic code
7. Weekly convergence gate (capabilities_converge five-condition verdict)
8. Honest quality scores in traces (82 > fabricated 97)
9. Promotion only through verifier
10. Doctrine evolution loop (versioner + drift detector)

### v19 — Singularity Prep
1. System drafts, scores, verifies, and iterates without per-artifact human input
2. Human position collapses to Gate-D approval only (outward lanes)
3. Z-thread earned-trust ladder per surface (evidence-gated promotion)
4. Auto-research → auto-draft → auto-score loops live
5. Long-form autonomous projects (novel arcs, feature scripts — B-threads, days)
6. **Love-notes lane permanently exempt from autonomy (hard rule, coded)**
7. Kill-switch drills (quarterly, proven)
8. Adversarial red team per release
9. Codebase-runs-itself audit (codebase singularity checklist)
10. Singularity readiness gate (63-gate strategy-studio core applied to the comms system itself)

### v20 — Communications OS (end state)
1. **One brain** — unified comms context pack in every agent session, all harnesses
2. **One voice** — fingerprint v2 enforced on every artifact, drift-checked
3. **One corpus** — writing-craft + wounds + behavioral + exemplars, queryable by any agent
4. **Twelve engines** — every surface live, routing through `rig-comm`
5. **Deterministic gates** — the full stack runs as code, red-capable, self-tested
6. **Closed loops everywhere** — nothing ships unverified; every outcome returns
7. **Measured + calibrated** — Brier-scored predictions, honest UNMEASURED when dry
8. **Compounding memory** — every artifact makes the next one better
9. **Federated** — public engine shared, private lanes sealed
10. **Self-improving** — the system that writes the system that writes, with proof

---

## 3. Contracts

### 3.1 Canonical layout (rig-capabilities)

```
capabilities/skills/rig-communications-core/      # rig_comm V10 seed (formulas/gates/scoring)
capabilities/skills/rig-communications-doctrine/  # 15 doctrine docs normalized
capabilities/skills/rig-communications-wounds/    # v3 wound+euphoria library
capabilities/skills/rig-communications-voice/     # v5 fingerprint v2
capabilities/skills/rig-communications-behavior/  # v4 bx fusion specs
capabilities/skills/rig-write-<surface>/          # v6, one per surface (12)
capabilities/commands/write.md                    # /write <surface>
data/corpora/writing-craft/                       # v2 transcripts + TARGETS.md + manifest.jsonl
```

### 3.2 Registration discipline

- Everything added via `bin/rig-capabilities add` (never hand-copied).
- Installed to harnesses only via `capability_install` (ledgered).
- Search before authoring: `capabilities_search` — no second convention beside an existing one.
- Every capability carries executable `done_when` checks.

### 3.3 Lane discipline (ACL)

| Lane | Surfaces | Rules |
|---|---|---|
| public | LinkedIn, Substack, public specs, federation | Gate-D before publish |
| internal | emails, resumes, prompts, code, film, songs, novels | Gate-D before send/share |
| private | love notes to James | Never federated, never autonomous, never in public corpus; excluded from GBrain public sources |

### 3.4 Tooling chain (per user directive)

- **scrapling** — non-YouTube craft supplements + anti-bot-resilient fetching
- **exa** (MCP + API key) — channel/video discovery + validation, trend grounding
- **consensus.app** — research claims in writing-craft doctrine (web access until key lands; key acquisition is a v2 task)
- **orchestrate + workflowz** — all multi-step execution runs as workpool fan-outs under this plan

---

## 4. Execution order (dependency-driven)

```
v0 ✓ → v1 (home) → v2 (corpus) ‖ v3 (wounds) → v4 (bx fusion) → v5 (voice)
     → v6 (engines, needs v1–v5) → v7 (gates) → v8 (loops) → v9 (wiring)
     → v10 (measurement) → v11 (calibration) → v12 (personas) ‖ v13 (deviation) ‖ v14 (multimodal)
     → v15 (crons) → v16 (memory) → v17 (federation) → v18 (self-improvement)
     → v19 (singularity prep) → v20 (OS)
```

v2 and v3 run in parallel after v1. v12–v14 parallelize after v11. Everything else is
dependency-serial. Foundation before fanout, always (v3.foundation-before-fanout).

---

*Plan sealed as design baseline 2026-09-06. Changes require a named-cost amendment per
north-star-lock-loop. Execution tracked in the OMP todo list.*
