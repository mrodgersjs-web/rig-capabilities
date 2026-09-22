---
name: rig-tac-doctrine
description: "Tactical Agentic Coding (TAC) doctrine distilled from IndyDevDan's curriculum and public repos — the agentic layer, plans-as-prompts, template engineering, AFK loops, verification gates, LAN fleet scaling. Use as source of truth whenever RIG designs, reviews, or prices an agentic coding system, client automation, or agent workflow; complements rsi-patterns and taki-doctrine."
tags: [rig, doctrine, agentic-coding, claude-code, agent-architecture, fleet]
metadata:
  source: "Tactical Agentic Coding course (https://agenticengineer.com/tactical-agentic-coding) + disler public repos (github.com/disler)"
  extracted: "2026-09-18"
---

# TAC Doctrine

<objective>
Source of truth for the Tactical Agentic Coding school of agentic engineering as applied inside RIG.
When designing, reviewing, scoping, or pricing any agentic system (client delivery, internal automation,
fleet work), check decisions against these laws and patterns before inventing new ones.
Deterministic-before-agentic still wins when the two conflict: TAC structures the agentic half; RIG hard law governs the boundary.
</objective>

## The curriculum map (what the doctrine covers)

Core: Hello Agentic Coding - The 12 Leverage Points - Success is Planned (80-20) - AFK Agents -
Close The Loops - Agentic Review & Documentation - ZTE (Zero Touch Engineering) - The Agentic Layer.
Extended: Elite Context Engineering - Agentic Prompt Engineering - Domain-Specific Agents -
Multi-Agent Orchestration - Agent Experts (agents that learn) - The Codebase Singularity.

## The laws

1. **Stop coding.** You are a commander of compute. Hands and mind are no longer the best tool for writing code; build systems that build systems.
2. **The prompt is the fundamental unit.** A plan, spec, or PRD is a scaled prompt. Great planning is great prompting - they are one and the same.
3. **Template your engineering.** Encode workflows into reusable units (`/chore`, `/bug`, `/feature`, `/test`). Solve problem classes, not one-offs. A template encodes expertise once and executes infinitely.
4. **Plans before loops.** First prompts, then plans, then hand work off. Scout-plan-build-review is the agentic SDLC; agents ship with your best practices encoded.
5. **AFK by design.** The goal state is unattended progress: the product builds itself while you are away. Anything requiring you at every step is a phase, not a system.
6. **Close the loops.** More compute only buys confidence when loops are closed: generate, verify, feed back, re-run. Open loops are wasted compute.
7. **Agents review agents.** A read-only reviewer answers "was it what was asked"; a test command answers "does it run." Keep the two roles separate; never let the author grade its own homework.
8. **Zero Touch Engineering (ZTE).** The engineer's signature moves from writing code to writing the specs, guards, and reviews that make code appear without touch.
9. **The Agentic Layer wraps the Application Layer.** `specs/` (plans) + `.claude/commands/` (reusable prompts) + `adws/` (executable AI Developer Workflows) + `ai_docs/` (knowledge). Minimum viable first, scale when it earns.
10. **Context engineering beats model upgrades.** A focused agent is a performant agent: narrow context, curated files, explicit contracts. Reach for more model only after the context is tight.
11. **Agent Experts learn.** Persist what agents discover (specs, memories, benchmarks) so run #100 is smarter than run #1; an agent that cannot remember is a contractor you rehire daily.
12. **Codebase Singularity.** When templates, specs, gates, and reviews compound, the codebase converges on self-operation. Design for that end state from day one.

## Architecture patterns (from the public repos)

- **Code owns the loop, agents own the phases** (super-simple-software-factory). Deterministic Python sequences phases; agents are bounded nodes. Typed JSON "envelopes" carry context across seams; every event lands in a trace DB. "Agent proposes, code disposes."
- **Gates verify claims, not guesses.** `artifacts_exist`, `files_non_empty`, `json_parses`, `diff_matches_claims`, `verdict_consistent` (reject approved=true with blocking items). Every phase defaults to fail; success is earned. On failure: re-prompt the SAME session with a correction - never restart.
- **Synced triad rule.** An output contract lives in 3 places that must change together: the type in `data_types.py`, the JSON example in the agent's `user.md`, the `output_type=` at the call site.
- **Hooks as deterministic guardrails** (claude-code-hooks-mastery). Lifecycle events (PreToolUse, PostToolUse, Stop...) exit-code-gate every dangerous action (2 = block, stderr = feedback). Self-validating command frontmatter: a command's Stop hook refuses to let the agent finish until required sections exist.
- **Independent verifier loop** (the-verifier-agent). Silent builder + locked-input verifier that re-checks every claim against real state. Atomic-claim decomposition, confidence ladder, cited evidence only - "without evidence, verdict is unsure." Escalate to human after N loops.
- **Policy-as-code firewall** (claude-code-damage-control). One `patterns.yaml`: zeroAccessPaths / readOnlyPaths / noDeletePaths + blocked & ask regexes; allow / block / ask as the only three outcomes. Peer-review the policy file; regression-test gates with adversarial prompts before loosening any.
- **Three autonomy tiers** (install-and-maintain). Tier-0 deterministic (script is the artifact, CI-safe), Tier-1 supervised (agent reads the log, reports), Tier-2 human-in-the-loop (clarify before mutate). The log is the artifact; the agent annotates it.
- **Sandbox + screenshot evidence** (agent-sandbox-skill). Every agent action in a disposable environment; validate results with screenshots on pass AND fail. Blast-radius isolation per agent.
- **Single-writer lease** (fusion-harness). Fan N models out on the same problem (AND not OR), merge through ONE writer holding an O_EXCL lease per checkout. Read-only opinions are cheap; writes are scarce.
- **Wave batching** (infinite-agentic-loop). Job schema = (spec, output-dir, count). Fixed-size waves of parallel sub-agents, disjoint output dirs, no writer collisions.
- **Stateless single-file agents** (single-file-agents). One job, one `uv`-runnable `.py`, version-suffixed. The portable unit of parallel dispatch - scatter across machines, compose results.
- **Declarative drop zones** (agentic-drop-zones). `drops.yaml` maps file patterns + prompt template + agent; drop a file, fire a job. Folders become typed work queues; routing is config, not code.
- **LAN fleet substrate** (mac-mini-agent). Listen (HTTP job server per Mac) + Direct (cross-machine client) + Drive (tmux fanout with sentinel completion) + Steer (OCR/click for GUI apps). One operator, many Macs, full autonomy.
- **Knowledge stores** (pocket-pick / marimo-prompt-library / indydevtools). SQLite FTS5 with sync triggers behind MCP for retrieval; folder-namespace + variant files as the git-native prompt library; alias + typed-variable template registry as the callable frontmatter.

## RIG mapping

| TAC law / pattern | RIG surface |
|---|---|
| Gates verify claims | ProofPacket: evidence or it didn't happen |
| Verifier loop, cited evidence | Pre-Gate-D self-check schema for every fleet agent |
| Damage-control patterns.yaml | Client-scoped guardrails; per-client policy artifact |
| Three autonomy tiers | Client delivery pricing ladder (build vs supervise vs HIL) |
| Single-writer lease + drop zones | RIG LAN fleet: N minis read-only, one writer per repo |
| Listen/Direct substrate | Fleet node standard install |
| Templates encode problem classes | Client repeatable-service productization |
| AFK + closed loops | Unattended routines only count when they reach `completed` |

## Field tools (from the course loot)

- **Template commands**: `/chore "desc"` then `/implement specs/plan.md` - the minimum viable agentic layer in two commands.
- **Context commands**: `/context` (measure window state), `/prime` (prime context), `claude --mcp-config <file>` (scoped MCP loading).
- **Claude Agent SDK**: `pip install claude-agent-sdk`; `query()` for one-shot exchanges, `ClaudeSDKClient` for session reuse. Skills, commands, and memory auto-load from `.claude/` and `~/.claude/` exactly like Claude Code - so every skill installed here also powers SDK-built agents. Hooks, subagents, MCP, permissions, sessions, and plugins are all SDK surfaces.

## Extended-lesson specifics (Agentic Horizon)

- **R&D Framework = Reduce & Delegate** (context window mastery). The only two verbs for managing a context window: **Reduce** (prime dynamically over static memory files, control output tokens, load MCP servers per-invocation not globally) and **Delegate** (sub-agents with isolated windows, architect/editor split). Measure first (`/context`), then reduce or delegate. (Corrected 2026-09-20 against the elite-context-engineering repo README — not a role/docs/task budget-allocation model.)
- **Seven levels of agentic prompt formats.** Prompts mature from ad-hoc text through structured templates to self-improving formats; classify every prompt you own by level and upgrade the top revenue-bearing ones first.
- **Domain-specific agents.** One identity per domain (`system.md` + `user.md` + report JSON); a generic assistant is a cost center, a domain agent is a product.
- **The O Agent / multi-agent orchestration.** One orchestrator owns the loop and delegates bounded tasks; sub-agents never talk to each other directly, only through typed envelopes.
- **Agent Experts.** Agents that learn: persist discovered context, specs, and benchmark results between runs so each engagement compounds.
- **Building agentic layers.** Grow from minimum viable layer (specs + commands + one ADW) to scaled layer (deep specs, e2e templates, trace DB) only when the thin layer is measurably working.

## Verified system state (2026-09-20)

- All 14 member repos cloned at `~/Developer/external/` with HEADs re-verified (tac-1 `24a6ca3` … orchestrator-agent-with-adws `fb99cd2`); full inventory + sanitized remotes in the TAC system pack (`tac-system/repository-inventory.json`).
- Claude Agent SDK, verified from live docs 2026-09-20: `query()` / `ClaudeSDKClient` split as above; `setting_sources` unset loads user + project + local filesystem settings exactly like the Claude Code CLI, so skills, commands, hooks and MCP config in `~/.claude/` and `<repo>/.claude/` auto-load into SDK-built agents; setting `skills` without `setting_sources` narrows to user + project only. `pip install claude-agent-sdk` (Python ≥0.2.129 for skill-name validation).
- The executable TAC stack lives in the source repos, not this doctrine: tac-3 has the 5-command template layer; tac-4/5/6/7 grow the same `adws/` Python driver from plan-build to ZTE iso (worktree isolation + explicit approve-and-merge ship step that refuses without `--approve`); tac-8 has five minimal agentic-layer apps; agent-experts defines the ACT→LEARN→REUSE expertise.yaml loop; orchestrator-agent-with-adws is the swimlane ADW orchestrator (Postgres + typed envelopes).
- Cross-stack carrier order (all four verified present): TAC doctrine → OpenSpec BDD (`/Users/rig128gb/Developer/rig-intelligence/platform/openspec-bdd/bin/rig-openspec-bdd`, `rig-bdd-zone-check`) → Jake L8 (`jake-l8 list/show/doctor`) → RIG L10 (`rig-l10 doctor`, `rig-l10-test`) → ProofPacket closeout. First Mate dispatch is via `jake send` + receipt, not OMP.
- Live backlog owner: First Mate via Gate-D-approved dispatch; this doctrine stays the standard, the repo carries the scripts.

## Hard rules when applying TAC here

- RIG hard law outranks TAC: no public/destructive/financial/irreversible action without explicit approval, raw secrets never stored, ProofPacket or it didn't happen.
- Deterministic before agentic: if a phase can be a script, it must be a script; agents get the judgment calls only.
- Never restart on failure - re-prompt the same session with the correction.
- One writer per checkout; everyone else read-only.
- Wave parallelism needs disjoint output dirs before it needs more machines.
