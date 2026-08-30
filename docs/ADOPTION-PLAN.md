# Agent Ecosystem Upgrade — Audit, Adoption Matrix, Execution Plan

Date: 2026-08-30. Method: full local inventory + five parallel research scouts
(skill libraries, hooks/guardrails, goal-harness/eval, self-improvement/memory,
orchestration frameworks) against live GitHub state; every claim below verified
by command output on this machine or the GitHub API. Scout cross-corrections
are folded in and marked; two initial scout claims were **retracted after
re-verification** — final numbers are the verified ones.

## 1. Estate as it actually stands

| harness | skills | agents | commands | hooks | notes |
|---|---|---|---|---|---|
| ~/.claude | 1,735 | 953 | 923 | 45 scripts, 14 wired events | + 56 goal harnesses (hA/hB/hC/hD/mh) |
| ~/.codex | 1,407 | 653 | 1,636 | hooks.json | MCP already wired |
| ~/.hermes | 2,251 | 124 | — | crons: 146 jobs | third+largest skill root |
| ~/.agents | 17 | — | — | — | shared root (omp/claude/pi) |
| ~/.rig/departments | — | 45 dept owners | — | — | the JTBD staff model |

**Four structural findings.**

1. **No version control anywhere.** 1,735+ Claude skills, all 56 goal
   harnesses, all 45 hooks: zero git. This is why `rig-capabilities` exists.
2. **Root collision is real.** `verification-before-completion` exists in
   three roots; superpowers skills are vendored in `~/.claude/skills/pi-superpowers/`
   *while the plugin is installed on disk but dormant in `enabledPlugins`* —
   so today's loaders come from vendored copies, not the plugin. Deleting
   vendored copies without enabling the plugin first removes capability.
3. **Live guardrail hole.** `permissions.defaultMode: bypassPermissions` is
   global and **no PreToolUse dangerous-command or secret-scan guard exists
   anywhere**. Hooks today are guidance (doctrine gates, pushback, session
   hygiene) — nothing deterministic blocks `rm -rf` / secret exfil. Highest
   severity finding of the audit.
4. **"Exists on disk" never proves "is running."** Four scouts hit this one
   layer apart: plugins installed but absent from the live 11-entry
   `enabledPlugins` map (superpowers/wshobson) while ruflo is affirmatively
   enabled; a git-guardrails *installer skill* with no registered hook
   (45 scripts, zero guard coverage); 35 matt-pocock skills installed but not
   adopted across roots; ~6 runnable eval surfaces on disk that the 56
   harness YAMLs bind to none of. **Consequence for rig-capabilities: the
   index proves existence, which is exactly the claim class that was wrong
   four times. Canonical entries need live-state probes bound to them** —
   `claude plugin list` for plugins, hook-config parse for hooks, `which`/
   port-bind for binaries — or the index records dormancy as capability.
   Tracked as the repo's next feature.

## 2. Retire / dedupe (with evidence)

| target | evidence | action |
|---|---|---|
| **ruflo ×5 plugins** | `~/.claude/settings.json:402-406` all `true`; ruvnet/ruflo#1514 (~290 stub MCP tools), #1670/#2078 (silent `Co-Authored-By: claude-flow` trailer injection) | **Retire, 4 ordered edits**: (1) settings.json enabledPlugins false ×5 (the only edit that stops loading); (2) drop 5 entries from `installed_plugins.json`; (3) drop `ruflo` from `known_marketplaces.json` + delete `marketplaces/ruflo/` (it's `source: directory` — why audit findings never surfaced); (4) rewrite `~/.claude/skills/rig-agent-team/SKILL.md` :3/:43/:114/:115 to name only live capabilities. Jobs already covered by ralph, rig-agent-swarms, Temporal/Kestra/Prefect, rig-memory-os. **Retire now**: the stub-tool finding means it never provided observability — removal of a no-op is not a regression, and trailer injection into real commits is a live liability. Langfuse (below) lands the real tracing. |
| **ruflo-observability retirement** | it was a stub (#1514) — never provided observability. The real backend **already exists**: Langfuse deployed via rig-docker-stack at localhost:3000, pinned `langfuse:2`, while doctrine mandates v3+ OTel-native — version-wrong and unwired, not absent | Retire regardless (removing a no-op is not a regression). The coverage fix is **upgrade Langfuse v2→current + wire Claude Code OTLP**, not mourning ruflo or standing up something new |
| **superpowers + wshobson dormancy** | correction (two independent greps + two harness load surfaces): live `enabledPlugins` has 11 entries; superpowers/wshobson/hookify absent = dormant | **Enable-verify-delete order**: (1) authoritative `claude plugin list`; (2) enable what's actually wanted (superpowers, wshobson `agent-teams`/`agent-orchestration`/`team-collaboration` — already in `plugins/cache/`, zero download cost); (3) confirm skills resolve from cache; (4) **only then** delete vendored duplicates (pi-superpowers ×11 nested, stray brainstorming/systematic-debugging/using-superpowers, 3× verification-before-completion → keep one canonical). Re-enabling cached plugins beats installing oh-my-claudecode for the same capability. |
| **mattpocock/skills** | CORRECTION after re-verify: **fully installed** — 35 `matt-pocock-*` in `~/.hermes/skills` + `~/.agents/skills` + `~/.claude/skills/code-review`. Initial "18 missing" scout claim was wrong (missed the hermes root; incomplete README capture) | **No install.** Dedup instead: canonicalize each into rig-capabilities with the `matt-pocock-*` prefix (already the working convention), install into missing roots, delete strays. |
| **anthropics document-skills** | VERDICT (upstream `skills/docx/LICENSE.txt` read 2026-08-30): © Anthropic PBC; use governed by Consumer/Commercial ToS **plus additional restrictions**: no retention of copies outside the Services, no reproduction, **no derivative works**, no distribution, no reverse engineering. The vendored copies (`~/.hermes/skills/{docx,pdf,xlsx,pptx}` + `~/.codex/skills/productivity/{docx,powerpoint,xlsx}`, "adapted by Nous Research" = derivative) **already breach those terms** — and the vendoring dropped the referenced LICENSE.txt itself (SKILL.md-only copies), so every copy points at terms it doesn't contain. Generated *outputs* (client .docx/.pptx) are not themselves restricted; the *skill copies* are. Upstream licensing is **per-skill**: `skill-creator`/`mcp-builder` = Apache-2.0, the four doc skills = proprietary (docx/pdf LICENSE hashes identical) | **Remediation (GO item #5):** quarantine-move the 7 vendored copies to `~/quarantine/anthropic-doc-skills/` (reversible, restores compliance); generate docs either via Anthropic **services** (official plugin path — permitted) or a clean-room self-authored rig-capabilities skill over MIT `python-docx`/`python-pptx`/`openpyxl`. Until then: stop doc-skill use for client deliverables. Policy: license-check **per skill** from `skills/<name>/LICENSE.txt`, never per repo |
| **kepano/obsidian-skills** | installed ×3 roots (codex/claude/hermes) | Dedup only. |
| **ECC** | vendored in TWO roots with disjoint sets: `~/.claude/skills/ecc` 71 + `~/.codex/skills/ecc` 50 ≈ 121/286 upstream | Re-sync via the official plugin path (upstream is self-distributed); reconcile vendored stragglers into the repo. |
| **pi/loopme stray skills** | `loop-me`, `ralph`, `ask-matt` etc. unversioned | First canonicalization batch for rig-capabilities. |
| **`rig-memory-os` / `rig-goal-engine` memory claims** | SelfImproveMemoryScout: `mem0_integration.py` is a JSONL stub mislabeled "Mem0 vector memory integration" | Delete or wire real — name must not lie about capability. |

## 3. Install (verified live, ranked; all license-checked)

### 3.1 Safety layer — FIRST, nothing else ships before this

| item | license | install |
|---|---|---|
| **kenryu42/cc-safety-net** | MIT | `npx -y cc-safety-net@latest install` — one guard for Claude+Codex+Hermes+Pi: AST rm detection, secret scanning (gitleaks-based + custom patterns), config-tamper watch; writes `~/.codex/hooks.json` natively |
| **karanb192/claude-code-hooks** | MIT, 491★ | `/plugin marketplace add karanb192/claude-code-hooks` → guard-hooks (block `rm -rf /`, `sudo rm`), env-check, format-code (ruff/prettier/biome), protect-tests, instructions-audit (catches agent editing its own CLAUDE.md) |
| **security-saved** (same author) | MIT | pre-push secret scan |
| **config-guard / config-watch** (same author) | MIT | **install LAST** — freezes config so plugin managers can't add plugins; enable only after all installs land |

Pattern source (no install): NVIDIA skills security pack (6-agent threat pipeline: STRIDE, CAPEC, CoC), Pimzino harden, ramsis bothi/claude-code-guardrails (Go, single static binary, TOML policies), YuUuit15/Routa (12 lifecycle events incl. SubagentStart/Stop), Decisive-AI/redzone (match_fail model), trailofbits/skills `writing-safe-skills` (SKILL.md audit).

### 3.2 New capability libraries (the only genuine gaps)

| item | license | why |
|---|---|---|
| **trailofbits/skills** | CC-BY-SA — **consume in place, never rebrand** | verified zero coverage today: no CodeQL, Semgrep, SARIF, differential review, supply-chain audit. `/plugin marketplace add trailofbits/skills` → static-analysis, differential-review, supply-chain-risk-auditor, goal-prompt, property-based-testing, second-opinion, git-cleanup |
| **openai/skills** | MIT | gh-fix-ci, gh-address-comments, security-threat-model, security-ownership-map — GitHub-inbound lane |
| **Graphify-Labs/graphify** | MIT | codebase→knowledge-graph (AST + Leiden); optional complement to Recall |

### 3.3 Improvement engine (upgrades loops/goal harnesses/self-improve)

| item | license | use |
|---|---|---|
| **GEPA** (MIT) | **already built on this machine** (HarnessEvalScout final correction) — no install | Wire the existing GEPA into the `rlm_improve` ledger as candidate generator (staged only — Gate-D preserved). Metric contract: GEPA must score RIG's L2 composite (GEV vector + AGF/RobustMAD-Z), never a generic judge |
| **ACE** (`ace-agent/ace`, Apache-2.0) | vendor `~/vendor/ace` | Curator + Reflector delta-bullets with helpful/harmful counters — replaces hand-rolled rotation in `alfred-weekly-hook-update`, `rig-doctrine-versioner` |
| **AWM** (`zorazrw/agent-workflow-memory`, MIT; the widely-cited `zhenghailin2000/AWM` is **404**) | nightly Hermes cron | traces → induced sub-agent workflows → Gate-D → SKILL.md; feeds rig-capabilities |
| **MemPalace** (`MemPalace/mempalace`, MIT, 58.7k★ — real repo, beware impostor domains) | pip/uvx | MIT replacement for the mem0 stub: verbatim layer + "quit loop" (stops at target score). `memory-drift-sentinel` skill's done-test references a nonexistent module — rewrite against it or retire |
| DGM (`jennyzzt/dgm`), SICA (`MaximeRobeyns/self_improving_coding_agent`) | Apache/MIT | **patterns only**: synthetic curriculum, and benchmark-gated self-edit + `agent_change_log.md` + sandbox. The sandbox-gate requirement is the fix for the `jake-self-healing` doctrine's no-sandbox gap |

Skipped on evidence: Reflexion (no framework), EvoAgentX, MIP, AgentEvolver/letta (overlap with rig-agent-department-builder), Claude-Terminal-Reporter & skill-evolution (private repos — 404).

### 3.4 Goal-harness execution & eval layer — REVISED (final scout correction)

**The gap is not missing tools.** Six eval surfaces already run here; the 56
`~/.claude/harnesses/*.yaml` are bound to **none of them**. Verified present:

| surface | state |
|---|---|
| `~/.local/bin/harbor` | installed; fork cloned at `~/Developer/harbor-fork/`. **Path trap: `~/Developer/harbor/` is the personal agent-infra monorepo (searxng/perplexica/ollama/opencode), NOT the eval framework — `which harbor` is the only valid check** |
| `~/.local/bin/promptfoo` + `pf` | installed but **unwired** — `~/Developer/harbor/promptfoo/` is a README-only stub; `~/.rig/evals`, `~/.rig/harness-tasks` do not exist. Value = wiring YAMLs to the binary, not installing |
| `~/.local/bin/prime` + `prime-agent` + `~/.prime/` + `~/Developer/prime-intellect-lab/` | **collides head-on with Harbor.** `~/.hermes/skills/evaluate-environments/SKILL.md` documents `prime eval run <ENV> --dry-run`, `prime eval validate --runtime.type subprocess`, model-free gold validation, zero-reward trace inspection as the CANONICAL env-eval path. Harbor-vs-prime is a choose-one decision, not an install |
| `~/rig-goal-engine/` | real PydanticAI engine: **73 loops, `yaml_loader.py` (YAML→GoalSpec), typed ProofPacket model, 7-layer SQLite memory, metrics/improve/observability, doctor, dashboard** — ProofPackets are code here, not just a skill |
| `@pai/skill-evals` v1.1.0 (`~/.claude/skills/evals/`) | bun+TS runner, 3 grader types (code/model/human), pass@k/pass^k via `ScenarioRunner.ts --trials N`, EvalRun JSON → `Results/`. Lacks: real-agent execution in isolated envs, failure_tier semantics, re-scoring, skill attribution. Hygiene: mandates curl to `localhost:31337/notify` before any action — guard, don't delete |
| Langfuse | **already deployed** at localhost:3000 via rig-docker-stack (`langfuse/langfuse:2`, pinned to v2 to avoid ClickHouse) — while `rig-multi-tenant-ai-runtime` doctrine + OBSERV-RULE say v3+ OTel-native. Action: **upgrade v2→current** (compose = `langfuse/langfuse-worker:4` + clickhouse + minio + redis) and wire Claude Code OTLP (`CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_LOG_USER_PROMPTS=1`, `OTEL_LOG_TOOL_DETAILS=1` → `skill_name` per call). This is the ruflo-observability replacement and it is an upgrade, not an adoption |

**Decision required (Gate-D):** pick ONE runner to compile the 56 harness YAMLs
into. Recommendation: **rig-goal-engine** — its `yaml_loader.py` already consumes
YAML GoalSpecs and ProofPackets are code there; keep `prime eval` as the
environment-validation layer; harbor only if containerized sandboxes are needed.
Gate semantics carry over: `failure_tier: halt|stop` → blocking verifier;
`degrade` → weighted. Pilots: hA-01, hA-03, hD-03. Batches on mounted
Kestra/Prefect/Temporal.

Remaining NET-NEW installs (verified absent): **Inspect AI** (epochs/
`--epochs-top-k` pass@k for σ-ladders; `inspect score` re-scores old `.eval`
logs free; Scanners catch evaluation-awareness) and **deepeval agentic
metrics** (TaskCompletion/StepEfficiency/ToolCorrectness in per-department
pytest; skip paid cloud). The 4 `inspect_evals` skills are **retracted**
pending independent verification. Earlier install commands for promptfoo/
harbor/langwatch must NOT ship — `langwatch` remains a dep of the evals skill,
not a self-host recommendation until the runner decision lands.

Skipped: SWE-bench (Harbor covers if chosen), HELM/openai/evals/METR (stale —
patterns only; EleutherAI lm-eval already vendored at
`~/.claude/skills/evaluation/evaluating-llms-harness`), phoenix (ELv2 —
Langfuse preferred), HAL (archived, no license file).

### 3.5 Orchestration: zero framework installs

Orca (`stablyai/orca`, running now — this session's terminal) already owns
worktrees/parallel terminals/automations, and `~/.hermes/skills/
herdr-workspace-orchestration/` (HERDR: split-pane spawn of Claude/Codex/Hermes,
send-to-pane, read-pane-output) plus `using-git-worktrees`, `tac-worktree-lanes`,
`acs-how-i-use-worktrees` already cover pane-spawned parallel agents →
claude-squad (AGPL), vibe-kanban (stale 4mo), crystal (deprecated), claudecodeui
(AGPL) **flat skip** (initial "claude-squad helps headless tmux" exception
retracted — HERDR pre-empts it). A kanban orchestration suite also already
exists: `kanban-orchestrator` v3.0.0 + `kanban-worker` + `brain-dump-to-kanban` +
`weekly-mission-kanban` in `~/.hermes/skills`, incl. orchestrator/worker role
split, decompose-don't-execute rule auto-injected via `KANBAN_GUIDANCE`,
`kanban_create` fan-out, and hallucination gates blocking `kanban_complete` on
nonexistent card ids with persisted audit events. CrewAI, LangGraph, MetaGPT
(stale Jan 2026), CAMEL, AG2, omnara skip — the hand-rolled surface is denser
than counted (agent-swarm-execution, dispatching-parallel-agents,
orchestration-governance, agentic-parallelization, parallel-feature-development,
fleet-cron-orchestration, predictive-swarm, intel/research-swarm, …): RIG has
no framework gap, it has an **unbundled-duplication problem across four roots**.
Temporal/Kestra/Prefect are mounted.

| item | license | role |
|---|---|---|
| **anthropics/claude-agent-sdk-python** | MIT | replace shell-wrapped `claude` in `~/.rig/departments`; **permission callbacks make Gate-D enforceable in code, not convention**; CLI bundled (no interactive/scripted drift) |
| **anthropics/claude-code-action** | MIT | GitHub-inbound triggers (issues/PRs/scheduled) with validated-JSON outputs — a trigger class RIG's cron fleet can't reach |
| **Untrivial-ai/agent-orchestrator** (the `abladerhufnal/...` name is 404) | Apache-2.0 | **borrow one thing, extend existing**: derive card status from external facts (PR/CI/merge/review state) instead of worker self-reported lifecycle → extend the installed `kanban-orchestrator` suite. Rest of AO's Kanban model is already pre-empted by it (`arbor-agent-orchestrator` checked: vendored AutoResearch re-creation, not a session manager — no conflict) |
| **deepagents** | MIT | borrow composition shape (planning tool, virtual FS, sub-agents, context offload); vendor only if LangGraph dep accepted |
| **agno** | Apache-2.0 | interface-only borrow: JWT-RBAC AgentOS control plane + Postgres trace store + UI over agents |
| **@openhands/agent-canvas** | MIT | trial on one node: ACP protocol = vendor-neutral, multi-backend server control plane for the Mac fleet |
| oh-my-claudecode | MIT | trial **only if** re-enabling wshobson's cached `agent-teams`/`agent-orchestration` doesn't already cover team orchestration (cheap test, run first); autopilot stage profiles need Linux+flock → dead on M5 Max anyway |
| **win4r/claude-code-webui-hooks** | MIT | pattern: Stop+SessionEnd `.hook-lock` dedupe → Hermes headless cron completion |

## 4. Memory & substrate fixes

- Three parallel memory systems with cross-links (rig-memory-os 90k+
  observations / GBrain 93k pages / claude-mem+mem0 stubs). One rule:
  **real or deleted, never renamed-to-lie.** mem0 JSONL stub → wire real or
  remove. `memory-drift-sentinel` done-test → rewrite against real substrate.
- Patterns only: DGM (synthetic curriculum), SICA (benchmark-gated
  self-edits + agent-change-log + sandbox).
- `claude-obsidian` (6,538★ MIT) — watch-only candidate for Recall/Obsidian
  bridge; graph-view + ontology schema before committing.

## 5. Dead / wrong links caught (do not chase)

`abladerhufnal/agent-orchestrator` 404 (real: Untrivial-ai) · `zhenghailin2000/AWM` 404 (real: zorazrw) · "swyxhq SICA" wrong attribution (real: MaximeRobeyns) · `laude-institute/terminal-bench` → `harbor-framework/*` · `ruvnet/claude-flow` → `ruvnet/ruflo` · `stravu/crystal` deprecated → `nimbalyst` · skill-evolution & claude-terminal-reporter = private · NVIDIA/skills star count inflated ~2.5–3× by shields.io (still real) · `textgrad` stale 4mo · openai/evals stale ~6mo · METR repo stale.

## 6. License policy (house line, applied throughout)

MIT/Apache → fork/vendor/rebrand freely into RIG-branded canonical assets.
CC-BY-SA (Trail of Bits) → consume in place as marketplace plugins; never
rebrand. AGPL (claude-squad, claudecodeui) → internal only, never in anything
shipped to the 8 ICP verticals. Proprietary (vendored doc-skills) → **verify
permitted-use before client deliverables.** No-license (oh-my-codex,
claude-agent-sdk-typescript repo) → trial/patterns only, use published packages.

## 7. Execution order

0. Read doc-skills LICENSE.txt (compliance).
1. **Safety layer** (3.1) — cc-safety-net install → karanb192 guard pack → saved → config-guard last.
2. **rig-capabilities live**: wire all 5 harnesses, reindex, seed first canonical batch (harnesses, live hooks, jake goal-harnesses, stray RIG skills). *(in progress this session)*
3. **ruflo retirement** (4 ordered edits, §2).
4. **Plugin re-enable + dedup sweep**: authoritative `claude plugin list` → enable wanted dormant plugins → verify load → delete vendored duplicates.
5. **trailofbits + openai/skills** marketplace installs; canonicalize chosen picks.
6. **Improvement engine**: wire the already-built GEPA into `rlm_improve` (staged, metric contract locked); vendor ACE; AWM nightly cron; MemPalace replace-or-delete decision on mem0 stub.
7. **Eval layer**: runner decision (rig-goal-engine recommended; prime/harbor explicit) → compile 56 harness YAMLs into it + pilots → Inspect + deepeval only → Langfuse v2→current upgrade + Claude Code OTLP wiring. No re-installs of harbor/promptfoo/prime.
8. **Headless**: claude-agent-sdk-python in `~/.rig/departments`; claude-code-action on RIG repos.
9. **Governance habits**: search-before-build via capabilities_search (MD blocks land via wiring); one owner per name via canonicalization; new hooks/harnesses authored in the repo from day one.

Each step verified with command output before the next. No outward/irreversible
action without explicit Gate-D approval.
