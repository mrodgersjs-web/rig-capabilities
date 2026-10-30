# Communications MCP v20 — Governed Transformation Engine

The build card (`RIG Communications — Governed Transformation Engine Build Card v1.0`,
2026-09-07) is the contract. This doc is the engineering map from the v0 endpoint to
v20, in RIG systems terms. Canonical code: `rig_comms` in
`capabilities/skills/rig-communications-core/`; public mirror `RIGIntelligence/rig-communications`;
harness riding surface: rig-capabilities MCP (`comms_bridge.py`).

## What v0 is (the honest baseline, 2026-09-07)

`rig_comms/mcp.py` v17.6: 4 tools (`surfaces`, `route`, `packet`, `score`), deterministic,
PRIVACY_LOCK enforced, no LLM. It routes and scores. It does not model a recipient, keep a
claim ledger, separate generator from verifier, replay goldens, or learn. That is a
scoring endpoint, not a transformation engine. Build-card verdict against v0:
C1 partial (route), C2–C10 absent, C11 partial (ledger), C12 partial (exit-3/gates).

## What v20 is

One stdlib-first MCP server that turns `CommunicationIntent` into a sealed
`CommunicationPacket`, where:

1. **Every state transition is typed and hash-chained** (lineage events).
2. **The drafting path can never certify itself** — termination token comes only from
   `verify()` (build card: "No self-verification"; RIG: Builder≠Verifier).
3. **Selection minimizes composite energy** `E_comm` with hard floors that override the
   weighted score (unsupported claim fails regardless of beauty).
4. **Recipient-state control is the objective** — know/feel/believe/do deltas, not prose
   aesthetics.
5. **Deviation is σ = 0.3·d_struct + 0.7·d_behavior**, per-archetype distributions;
   novel language welcome, novel deception blocked (5σ → deep review).
6. **The corpus is executable**: 24 how-to channels → skills, agents, hooks, loops,
   harnesses — doctrine that runs, not doctrine that is quoted.

## The ladder (v0 → v20, each layer earns its keep)

| ver | layer | artifact in `rig_comms` |
|---|---|---|
| v1 | schemas | `models.py` — `CommunicationIntent`, `CommunicationPacket` (build-card YAML, frozen) |
| v2 | lineage | `lineage.py` — hash-chained typed events, one per stage pass |
| v3 | claim ledger | `claims.py` — claim/ provenance/ support; blocks checkable claims without source |
| v4 | audience model | `audience.py` — known/inferred/unknown split; multi-audience → variants, never averaged |
| v5 | vehicle choice | `vehicles.py` — 7 architectures (BLUF, value-first, decision memo, feedback, repair, crisis, gratitude) + `no-send` |
| v6 | E_comm | `energy.py` — 8 weighted dimensions, low/high-stakes tables, hard floors |
| v7 | gates | `gates_v2.py` — 11 release gates from the build card as executable checks |
| v8 | warmth×competence | `perception.py` — two independent axes; manipulative-warmth detector |
| v9 | compression | `compress.py` — throat-clearing ban list, 20–33% cut check, BLUF latency, mobile scan |
| v10 | voice | reuse `voice.py` fingerprint-v2; drift threshold as gate |
| v11 | channel adapt | `transcompiler.py` — semantic invariants preserved across email/DM/memo/post/spoken |
| v12 | GEV roles | `roles.py` — 11 build-card agents as prompt contracts; 4 server-enforced "cannot" rules |
| v13 | evaluator sim | `simulate.py` — recipient modes (skeptical/busy/friendly/hostile/literal) as deterministic reading probes |
| v14 | revision loop | `revise.py` — typed defects only, ≥3 Q/R cycles for consequential, max-3 latch (existing) |
| v15 | abstention | `abstain.py` — C12 stop conditions as first-class verdicts (`abstain`/`escalate`) |
| v16 | proof packet | extend `packets.py` — 12-part build-card packet, `packet_hash` |
| v17 | golden replay | `golden.py` — 10 must-pass + 10 must-fail from the card, runnable `python3 -m rig_comms.golden` |
| v18 | learning | `outcomes.py` — archetype-keyed telemetry, Brier calibration, promote-after-3-self-breeding rule |
| v19 | corpus → assets | distilled skills/agents/hooks/loops/harnesses from 24 how-to channels, sealed into the estate |
| v20 | everywhere | server v2 exposes tools+resources+prompts; installed on claude, codex, hermes, omp (orca/prime inherit) |

## MCP surface (v20 server)

**Tools** (deterministic core; nothing here calls an LLM):
`comms.surfaces`, `comms.route`, `comms.packet`, `comms.score` (v0, kept), plus
`comms.intent_check` (C1 schema validation + state-delta proof obligation),
`comms.audience` (C2 model assembly from supplied facts), `comms.vehicle` (C3/C22 choice +
no-send advisory), `comms.energy` (E_comm + floors), `comms.claims` (C5 ledger lint),
`comms.compress` (C7 mechanical pass), `comms.gates` (v7 stack), `comms.golden` (v17 suite),
`comms.verdict` (v10 sole-termination check over an evaluator transcript),
`comms.outcome` (v18 append), `comms.doctor`.
Private lane: unconditional PRIVACY_LOCK on scoring; `human:true` only unlocks drafting.

**Prompts** (where the LLM work belongs — the harness agent runs them):
`draft` (Message Architect), `voice` (Voice Smith), `sim-skeptical|busy|friendly|hostile|literal`
(Recipient Simulator modes), `critic-clarity`, `critic-warmth`, `redteam`,
`verify` (Communications Verifier — never rewrites). GEV separation is text-enforced in
each prompt and code-enforced in `roles.py` (`role_cannot()`).

**Resources:** `comms://doctrine`, `comms://fingerprint`, `comms://rejected-patterns`,
`comms://archetypes` (7 architectures + weights), `comms://golden` (suite + expected verdicts).

## Systems thinking (the loop that makes it 1000x, not 2x)

Stocks: corpus (transcripts), skill library, claim provenance graph, outcome history,
voice fingerprint, golden set.
Flows: scrape→distill→skill; intent→packet→delivery→outcome→weight update.
Reinforcing loops: **R1 outcome→calibration→routing** (Brier-scored per archetype),
**R2 golden-set ratchet** (every shipped failure becomes a permanent must-fail case),
**R3 self-breeding** (pattern ×3 → anti-unification → replay → meta-eval → versioned skill).
Balancing loops: **B1 GEV separation** (drafters can't certify), **B2 hard floors**
(beauty can't buy an unsupported claim), **B3 PRIVACY_LOCK**, **B4 max-3 revision latch**.
The 1000x claim lives in R2+R3 running unattended on evidence; a faster prose generator
would be 2x.

## Install topology (four writes, six surfaces)

| surface | integration | mechanism |
|---|---|---|
| claude | entry `rig-communications` in `~/.claude.json` `mcpServers` | direct |
| codex | `[mcp_servers.rig-communications]` in `~/.codex/config.toml` | direct |
| hermes | `mcp_servers.rig-communications` in `~/.hermes/config.yaml` | direct |
| omp | entry in `~/.omp/agent/mcp.json` | direct |
| orca | inherits — Orca spawns omp/claude sessions which read the two above | verified at v20 |
| prime-agent | inherits — `prime-jake-code` spawns claude/codex/omp workers | verified at v20 |

Launch spec (all four): `python3 -m rig_comms.mcp` with `cwd` =
`<cap-root>/capabilities/skills/rig-communications-core` (stdlib-only; uv python 3.11
where the harness needs ≥3.10 for `X | Y` typing syntax).

## Corpus lane (v19)

24 how-to channels × ≤25 recent videos, full transcripts (metadata+text only),
`data/corpora/how-to/`. Distillation targets per transcript cluster: SKILL.md (sealed
skill form: contract, inputs, procedure, tools, outputs, tests, risk_class, version),
agent role defs (11-role topology extended by corpus-found roles), hooks (pre/post
deterministic checks), loops (builder-verifier, revision, self-breeding), harnesses
(sealed goal-harnesses with done-tests). Every distilled asset carries source video_ids —
no unsourced doctrine.

## Non-negotiables carried from prior waves

Private lane never machine-scored, never autonomous, never federated. No commit in CAPS
by the campaign. Gate-D before push/send. Honest gaps name their unblocker.
