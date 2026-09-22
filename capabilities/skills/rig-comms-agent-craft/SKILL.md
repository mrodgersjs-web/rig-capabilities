---
name: rig-comms-agent-craft
description: Agent craft translated into message engineering — job contracts, control graphs, earned autonomy, verifier separation, durable state, bounded parallelism, costed proof. Distilled from a 17-transcript, 12-channel sample. Use when explaining, designing, demoing, or critiquing an AI agent, loop, swarm, workflow, or agent team.
outcome: agent narratives and designs that expose the job, state, boundaries, verification, cost, and receipts instead of selling autonomy by adjective or agent count
done_when:
  - file:capabilities/skills/rig-comms-agent-craft/SKILL.md
  - grep:capabilities/skills/rig-comms-agent-craft/SKILL.md:uncertainty in
  - grep:capabilities/skills/rig-comms-agent-craft/SKILL.md:S2sjyokoxeE
  - cmd:python3 -c "import json; m=[json.loads(l) for l in open('data/corpora/how-to/manifest.jsonl') if json.loads(l).get('surface')=='agent-craft']; assert len(m)==248; ids={r['video_id'] for r in m}; body=open('capabilities/skills/rig-comms-agent-craft/SKILL.md').read(); cited={i for i in ids if i in body}; assert len(cited)>=12, cited; print('OK', len(cited))"
quality_floor: 0.65
great_example: capabilities/skills/rig-comms-agent-craft/SKILL.md
metadata:
  source_corpus: data/corpora/how-to/agent-craft (248 transcripts, 12 channels; sha256-verified in data/corpora/how-to/manifest.jsonl)
---

# rig-comms-agent-craft

Ten patterns from the selected corpus. Each pattern is supported by at least two
transcripts. The review unit is an agent brief, architecture, demo, or launch claim.

## P1 — Open with the job contract: input → outcome
IndyDevDan reduces the CEO-and-board system to “uncertainty in, decision out” and then
to the concrete interface “brief” in, “memo” out (TqjmTZRL31E). AI Jason makes the same
boundary mechanical: define each agent node’s input and output, then enforce the output
with an agreed schema so the next node receives usable state (_9OT25ZvrWs).
**Mechanism:** a bounded transformation lets the reader judge whether an agent is the
right machine before meeting its tools or persona. **Craft rule:** the first diagram or
two sentences must name the trigger/input, the observable output, and the decision that
output enables. If the explanation begins with a model, framework, or character name,
move that detail below the contract.

## P2 — Draw node → edge → state before naming the cast
AI Jason defines a control graph with three parts: node = action, edge = what happens
next, state = data carried between steps (_9OT25ZvrWs). 1littlecoder gives the outer-loop
version: a trigger wakes the agent; investigation and action produce artifacts or signals;
the next run reads them, reprioritizes, and learns (9pj3-zDw4eU). Cole Medin’s dark factory
makes the edges visible with issue states such as accepted, in progress, needs review,
and needs fixing before deployment (eecUhBpTz_g).
**Mechanism:** roles describe who; transitions explain how work advances and where it can
stop. **Craft rule:** show the smallest state machine that accounts for every handoff.
Every node gets one verb, every edge gets a condition, every persisted state gets one
owner. Agent names come last.

## P3 — Compile the known path; spend intelligence only at forks
“Try to use code when things make sense”: prewrite scripts for repeated data fetching,
dev-server startup, evaluation, and end-to-end checks instead of asking an agent to
rediscover those steps (_9OT25ZvrWs). In First Mate, deterministic coordination steps are
bundled into scripts so the agent “does not need to spend tokens” walking them again
(8ZgpAXe5V5w). Cole Medin similarly makes workflow progression deterministic and reserves
LLM reasoning for classification, implementation, and review (UztrFXaSWv0).
**Mechanism:** code removes variance and context tax from solved steps; the model stays
available for choices that actually require judgment. **Craft rule:** annotate each step
`CODE` or `JUDGMENT`. If a `JUDGMENT` step has one valid path on every run, replace the
agent instruction with a command or constraint.

## P4 — Put memory in artifacts, not conversation length
1littlecoder separates three durable surfaces: artifacts carry findings, each loop
contract carries goal/workflow/backlog/timeline, and a global work log carries cross-domain
changes; agents read recent entries before acting (9pj3-zDw4eU). AI Jason recommends a
latest-status Markdown artifact plus an append-only run log so a new node can recover
state quickly (_9OT25ZvrWs). Cole Medin stores loop events and conversations in Postgres
so a cancelled run resumes at the exact workflow step rather than reconstructing intent
from chat (UztrFXaSWv0).
**Mechanism:** external state makes sessions replaceable and recovery inspectable.
**Craft rule:** for every fact the next run needs, point to its durable field or file.
Conversation is transport, not the system of record.

## P5 — Autonomy is a promotion ladder, not a launch setting
The First Mate operator says “trust takes time to build”: early runs misrouted tasks and
sent multiple crewmates into conflicting work, so he observed, corrected routing rules,
and only then stopped inspecting most children (8ZgpAXe5V5w). Cole Medin calls human-led
level three the most reliable default and explicitly says not to jump straight to a
level-four/five dark factory; the setup interview chooses autonomy and escalation points
(eecUhBpTz_g). Liam Ottley’s makeover closes by teaching the owner to run the system
without the builders present (BMSvmzJuMiM).
**Mechanism:** trust comes from a history of bounded correct runs, not from model rank.
**Craft rule:** state the current rung — observe, approve, exception-only, or autonomous —
and the evidence required for promotion. Always name the condition that returns control
to a human.

## P6 — Builder and verifier must hold different information
Cole Medin’s validator is a separate session: the builder cannot see holdout scenarios,
and the validator does not inherit the implementation plan (eecUhBpTz_g). 1littlecoder’s
PR contract says not to let the agent self-verify; it spawns a read-only verifier with the
spec and asks for visible evidence (9pj3-zDw4eU). The First Mate “No Mistakes” pipeline
reconstructs user intent, then gives a different model the adversarial review; the speaker
reports that review caught most of the rare edge cases in its measured runs
(8ZgpAXe5V5w). Wes Roth’s GPT Red example makes the attack role explicit: the red model is
rewarded for eliciting a valid defender failure, and those failures train the defender
(OPuD-UeQGY8).
**Mechanism:** fresh priors and asymmetric information break the builder’s confirmation
bias. **Craft rule:** name what the verifier can see, what it is deliberately denied, the
failure it must try to produce, and the artifact that records RED or GREEN.

## P7 — Route by work shape, not model prestige
First Mate keeps routing rules in a file: deep technical/product design goes to the model
with the desired depth, routine work uses the default, and quota state affects selection
(8ZgpAXe5V5w). Cole Medin uses a small model for issue classification, a stronger coding
agent for implementation, and a different provider for review (UztrFXaSWv0). Sonny Sangha
shows an orchestrator model launching cheaper subagents, then verifies the actual models
in the session trace (p5F__7VQ1zM). Matt Wolfe’s B-roll skill maps script moments to shots,
routes each shot to the fitting media model, and uses deterministic FFmpeg normalization
at assembly (EOCRtSnvNNE).
**Mechanism:** role-fit raises disagreement quality and prevents cheap work from consuming
premium reasoning. **Craft rule:** every routed role names its work shape, model/tool
choice, and why the cheaper or deterministic option does not hold.

## P8 — Isolation and ownership precede fan-out
In the swarm demo, several agents initially claim the same rendering work; coordination
improves only after agents deconflict and claim/release files, while deadlocks visibly burn
budget (S2sjyokoxeE). Cole Medin requires one worktree per parallel coding session and
separate database branches so code and schema changes do not collide (UztrFXaSWv0).
Claude Workflows are reserved for work such as a 500-file migration or independent
research angles, then split into named find, verify, and fix phases (W6x-hb44C0c).
**Mechanism:** concurrency multiplies ownership mistakes before it multiplies throughput.
**Craft rule:** before showing an agent count, show the unit of ownership, isolation
boundary, conflict rule, and integration owner. No four fields, no fan-out.

## P9 — Budget and bailout belong in the specification
Claude Workflows can consume millions of tokens, so the demo recommends runtime caps and
size classes — small means fewer than five agents — rather than unrestricted launch
(W6x-hb44C0c). The CEO-and-board harness places both time and dollar constraints in config;
once the limit is reached, the CEO requests final positions and writes the memo
(TqjmTZRL31E). The swarm harness requires a definition of done plus a way to say “I can’t
do this”; the transcript contrasts that with impossible goals that supplied no exit
(S2sjyokoxeE).
**Mechanism:** an optimization loop without a stop rule converts uncertainty into spend
or unsafe improvisation. **Craft rule:** every agent brief states success, maximum rounds,
time/token/money ceiling, no-progress condition, and terminal artifact. “Keep going” is
invalid without all five.

## P10 — Demo one closed path and attach receipts
Liam Ottley’s business demo follows one path: 19 recorded sales calls are analyzed, stale
conversations become a ranked top-five outreach list, and the operator reports the first
$10K payment before the later business result (BMSvmzJuMiM). Sonny Sangha traces prompt →
template → isolated workspace → running app, then opens the audit view showing user,
model, tokens, prompts, and tool calls (p5F__7VQ1zM). Claude Workflows reports phase count,
agent count, tokens, elapsed work, and an estimated dollar cost instead of saying the
“army” was merely powerful (W6x-hb44C0c). Even the small Snobify example explains the
behavioral change as a specific prompt context and perspective, not “better prompting”
(qdTdU4uhUUk).
**Mechanism:** a closed trace exposes both value and hidden cost; adjectives expose
neither. **Craft rule:** every demo must show the exact input, at least one intermediate
state, the observable output, verification, and spend/latency. Label source-reported
business outcomes as reported, not independently proven.

# Anti-patterns (named in the corpus)
- **Agent-count theater** — thirty agents with overlapping claims spend the first phase inventing coordination (S2sjyokoxeE). Lead with divided work and receipts; count is metadata.
- **Autonomy by announcement** — moving directly from prototype to dark factory skips the observed-runs ladder (8ZgpAXe5V5w, eecUhBpTz_g). State the current rung and promotion evidence.
- **One immortal chat** — repeated slash-loops bloat one context and make recovery depend on conversation survival (UztrFXaSWv0). Persist step state, then start replaceable sessions.
- **Builder marks its own exam** — shared plans and visible holdouts let implementation bias the verdict (eecUhBpTz_g, 9pj3-zDw4eU). Split roles and information.
- **No-exit hero prompt** — “at all costs” plus an impossible goal makes rule-breaking a locally rational continuation (S2sjyokoxeE). Give done, blocked, budget, and no-progress exits.

# Provenance
- `9pj3-zDw4eU` — demonstrated compounding business loops built from triggers, shared artifacts, contracts, logs, executable repos, and read-only verification.
- `W6x-hb44C0c` — demonstrated large Claude Workflows split into find/verify/fix phases with agent, token, runtime, and dollar costs exposed.
- `eecUhBpTz_g` — demonstrated a spec-to-deploy dark factory with mission boundaries, state labels, independent validation, and hidden holdout scenarios.
- `TqjmTZRL31E` — demonstrated brief-in/memo-out agent design, adversarial board roles, persistent expertise, and time/cost-constrained deliberation.
- `8ZgpAXe5V5w` — demonstrated one coordinator over many projects, earned trust, task/model routing, deterministic scripts, adversarial review, and measurable receipts.
- `BMSvmzJuMiM` — demonstrated an AI operating system grounded in existing customer conversations, ranked actions, visible revenue events, and owner handoff.
- `EOCRtSnvNNE` — demonstrated a reusable agent skill that maps a script to media tasks, routes generation by shot type, and assembles outputs deterministically.
- `p5F__7VQ1zM` — demonstrated isolated agent workspaces, provider and MCP allowlists, centralized credentials, per-user cost traces, audit logs, and health checks.
- `OPuD-UeQGY8` — demonstrated adversarial self-play through GPT Red and the danger of treating repeated model success as permission to remove safeguards.
- `qdTdU4uhUUk` — demonstrated how a specific context and perspective changes a model from generic policy-shaped output to task-relevant judgment.
- `_9OT25ZvrWs` — demonstrated node-edge-state control graphs, LLM-as-graph versus code-as-graph, typed handoffs, scripts, and append-only state.
- `UztrFXaSWv0` — demonstrated loop-engineering trade-offs, deterministic multi-session workflows, model-per-node routing, durable state, worktree isolation, and human gates.
- `S2sjyokoxeE` — demonstrated swarm coordination overhead, message threads, file claims, observability, hard budgets, definitions of done, bailout paths, and sandboxing.
