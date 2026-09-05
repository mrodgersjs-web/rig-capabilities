---
outcome: agent-engineering:
done_when:
  - file:capabilities/loops/adversarial-agent-orchestration.md
  - file:rig_capabilities/topology.py
  - file:tests/test_topology.py
  - cmd:python3 -m unittest tests.test_topology
  - cmd:python3 -m rig_capabilities.topology validate capabilities/loops/adversarial-agent-orchestration.md
  - cmd:python3 -m rig_capabilities.topology validate capabilities/loops/adversarial-agent-orchestration.md --mutate cycle --expect cycle_at
  - cmd:python3 -m rig_capabilities.topology validate capabilities/loops/adversarial-agent-orchestration.md --mutate ghost --expect undefined_edge
  - cmd:python3 -m rig_capabilities.topology validate capabilities/loops/adversarial-agent-orchestration.md --mutate contract --expect contract_mismatch
  - cmd:python3 -m rig_capabilities.topology validate capabilities/loops/adversarial-agent-orchestration.md --mutate unreachable --expect unreachable_agent
  - cmd:python3 -m rig_capabilities.topology dispatch capabilities/loops/adversarial-agent-orchestration.md orchestrator adversarial-1 artifact
  - cmd:python3 -m rig_capabilities.topology dispatch capabilities/loops/adversarial-agent-orchestration.md adversarial-1 adversarial-2 findings --expect undefined_edge
  - grep:capabilities/loops/adversarial-agent-orchestration.md:does not silently reorder
  - grep:capabilities/loops/adversarial-agent-orchestration.md:Z90xlttVx3Y
  - grep:capabilities/loops/adversarial-agent-orchestration.md:arXiv:2608.21156
great_example: examples/great/agent-engineering/adversarial-agent-orchestration.md
quality_floor: 0.6
---

# Adversarial Agent Orchestration Harness

**Source:** "The Ideal Agentic Setup" by Yaron Been — https://www.youtube.com/watch?v=NRrj6qEymBY
**Extracted:** 2026-07-22 · **Revised:** 2026-09-02 (declared topology + edge-checked dispatch)
**Type:** gate-loop

## Purpose

Govern the pattern of using multiple LLM providers as adversarial reviewers.
The primary agent produces work, then sends it to 1-2 other providers for
independent critique before finalizing. This prevents single-model blind spots
and catches issues the primary model would miss.

**The 2026-09-02 delta:** this loop used to fix a linear five-gate chain in
prose — primary → adversarial 1 → adversarial 2 → merge → human — with model
routing by role and kill switches as English conditions. It never declared a
topology or a set of legal message edges, so *who-may-talk-to-whom was
emergent, not structural*: a runner could hand adversarial 1's findings
straight to adversarial 2 (silently colluding the "independent" reviewers),
or wire a reviewer back into primary and deadlock the round, and nothing
would notice. Below, the topology is **declared** in this file as a machine-
readable graph, dispatch is **edge-checked** against it before any agent is
invoked, and the kill switches are **declared knobs**, not vibes.

## Gates

| Gate | Name | Evidence Required | Pass Condition |
|------|------|-------------------|----------------|
| 00 | Primary Output | Artifact produced by primary model | Non-empty, structured |
| 01 | Adversarial Review 1 | Feedback from secondary model (e.g., Codex) | At least 1 finding OR explicit "no issues" |
| 02 | Adversarial Review 2 | Feedback from tertiary model (e.g., Gemini) | At least 1 finding OR explicit "no issues" |
| 03 | Merge & Prioritize | Combined findings in tiered format | Findings categorized by severity |
| 04 | Human Decision | Mike reviews prioritized findings | GO / NO-GO / REVISE |

## Loop

```
Primary model produces artifact
  ↓
[Gate 00] → artifact exists and is structured → PASS/FAIL
  ↓
[Gate 01] → send to secondary model via MCP → collect findings   ← dispatch edges, not prose
  ↓
[Gate 02] → send to tertiary model via MCP → collect findings    ← dispatch edges, not prose
  ↓
[Gate 03] → merge, deduplicate, prioritize → tiered action list
  ↓
[Gate 04] → human reviews → GO (proceed) / NO-GO (abandon) / REVISE (next round)
```

Each arrow Gate 01–04 must traverse exists in the declared graph below before
the hop is allowed to happen.

## Declared Topology

The loop declares its team graph in this file. `rig_capabilities.topology`
(stdlib, pure) is the single adjudicator: `validate(graph)` returns
machine-readable verdicts and never writes anything; the CLI exits 1 on any
verdict.

```rig-topology
{
  "topology": "orchestrator",
  "root": "orchestrator",
  "agent_count": 6,
  "agents": [
    {"id": "orchestrator",  "family": "harness",
     "input_contract": ["artifact", "findings", "tiered_findings", "verdict"],
     "output_contract": ["brief", "artifact", "findings", "tiered_findings"]},
    {"id": "primary",       "family": "claude",
     "input_contract": ["brief"], "output_contract": ["artifact"]},
    {"id": "adversarial-1", "family": "codex",
     "input_contract": ["artifact"], "output_contract": ["findings"]},
    {"id": "adversarial-2", "family": "gemini",
     "input_contract": ["artifact"], "output_contract": ["findings"]},
    {"id": "merger",        "family": "claude",
     "input_contract": ["artifact", "findings"], "output_contract": ["tiered_findings"]},
    {"id": "human",         "family": "human",
     "input_contract": ["tiered_findings"], "output_contract": ["verdict"]}
  ],
  "edges": [
    {"from": "orchestrator",  "to": "primary",       "payload": "brief",           "kind": "dispatch"},
    {"from": "primary",       "to": "orchestrator",  "payload": "artifact",        "kind": "deliver"},
    {"from": "orchestrator",  "to": "adversarial-1", "payload": "artifact",        "kind": "dispatch"},
    {"from": "adversarial-1", "to": "orchestrator",  "payload": "findings",        "kind": "deliver"},
    {"from": "orchestrator",  "to": "adversarial-2", "payload": "artifact",        "kind": "dispatch"},
    {"from": "adversarial-2", "to": "orchestrator",  "payload": "findings",        "kind": "deliver"},
    {"from": "orchestrator",  "to": "merger",        "payload": "artifact",        "kind": "dispatch"},
    {"from": "orchestrator",  "to": "merger",        "payload": "findings",        "kind": "dispatch"},
    {"from": "merger",        "to": "orchestrator",  "payload": "tiered_findings", "kind": "deliver"},
    {"from": "orchestrator",  "to": "human",         "payload": "tiered_findings", "kind": "dispatch"},
    {"from": "human",         "to": "orchestrator",  "payload": "verdict",         "kind": "deliver"}
  ],
  "knobs": {
    "max_rounds": 3,
    "budget_exceeded": "stop dispatching reviewer edges this round; record the skip",
    "time_pressure": "skip only the adversarial-2 dispatch edge; never skip the merge edge",
    "all_reviewers_agree": "merger auto-tiers; the merger edge is still traversed"
  }
}
```

Declaration fields:

| Field | Meaning | Enforced by |
|-------|---------|-------------|
| `topology` | `boss` \| `orchestrator` \| `flat-swarm` — the closed enum | `topology_undeclared:<value>` |
| `root` | The hub agent. Required by `boss`/`orchestrator`; the orchestrator here is the loop harness itself | `root_undeclared:<value>` |
| `agent_count` | The count is **fixed** by the declaration — an unplanned fifth "helper reviewer" is a declaration violation, not a favor | `agent_count_mismatch:<n>!=<m>` |
| `agents[].input_contract` / `output_contract` | What each agent accepts / may emit, as message types | `contract_mismatch:...` |
| `edges[].kind` | `dispatch` opens a wait (sender holds for the answer); `deliver` closes one (a response travelling back) | `edge_kind_invalid:...` |
| `knobs` | Declared runtime dials. A knob may **suppress** a dispatch, never invent an edge | (knob discipline, below) |

## Edge-Checked Dispatch — Refusal Semantics

Before an agent is invoked, `topology.check_dispatch(graph, src, dst, payload)`
asserts the hop. Dispatch is legal only if **all** hold:

1. **The edge exists.** `(src → dst : payload)` is one of the declared edges.
   A hop not in the graph — e.g. `adversarial-1 → adversarial-2` — is
   `undefined_edge:<from>-><to>`. Reviewers talking to each other is precisely
   what the declaration makes impossible.
2. **The callee's contract matches.** What is about to be passed is in the
   receiver's declared `input_contract` (and in the sender's declared
   `output_contract`): otherwise `contract_mismatch:<from>-><to>:<payload>:<not_in_input|not_in_output|payload_missing>`.
3. **No cycle is introduced.** Cycles are computed over **dispatch** edges
   only — a `deliver` edge releases a wait, it never opens one — so a node
   waiting on its own descendant reports `cycle_at:<node1,node2,...>`. A graph
   that validates clean is acyclic-on-waiting by construction.

**Refusal is refusal.** When any of the three fails, the dispatch exits 1,
names the verdict, and **stops**. It does not silently reorder the plan,
drop the hop, re-route through a different agent, or downgrade to a
"best-effort" send — a loop that quietly works around a rejected edge has
just made who-may-talk-to-whom emergent again, which is the bug this whole
section exists to kill. The operator fixes the **declaration** (and eats the
re-validation), or the round ends blocked with the verdict recorded.

Round iteration is loop control, not a message edge: Gate 04's REVISE starts
round N+1 (fresh dispatch from the root); it is never drawn as an edge back
into an ancestor node, because that edge — if it existed as a dispatch —
would be a deadlock, and if drawn as a deliver — it would lie about what
closes a wait.

**Knob discipline:** a kill switch may suppress dispatches this round (skip
adversarial-2 under time pressure) but must **record the skip** as a
first-class state — never undeclare the agent, never rewire around it.
Suppressing dispatches is always graph-legal; the declaration is invariant
across rounds. `unreachable_agent:<id>` guards the declaration itself: an
agent that no legal edge can ever reach (the corpus test case: a handoff
packet naming a reviewer unreachable on every allowed edge of the topology)
goes RED at `validate`, before any dispatch is attempted.

## Plant-Failure Guarantees

The `done_when` checks above are not the happy path only — each verdict class
is asserted against a planted defect **on this file's own graph**, via
`--mutate <defect> --expect <verdict>` (mutations run on a deep copy; the
declared graph is never touched):

| Planted defect | Verdict that must fire | Check |
|----------------|------------------------|-------|
| dispatch cycle closed along the agent order | `cycle_at:...` | `--mutate cycle --expect cycle_at` |
| edge from an undeclared node | `undefined_edge:...` | `--mutate ghost --expect undefined_edge` |
| input type stripped from a declared agent | `contract_mismatch:...` | `--mutate contract --expect contract_mismatch` |
| all dispatch edges into a reviewer removed | `unreachable_agent:...` | `--mutate unreachable --expect unreachable_agent` |

If cycle detection (or any other guard) is ever broken, the corresponding
check goes RED by exit code — the gate cannot be theater.
`tests/test_topology.py` exercises every verdict class, a legal star graph,
a legal flat-swarm, and the purity of `validate` (same input object,
unchanged, before and after).

## Model Routing (from video)

| Role | Model | Why |
|------|-------|-----|
| Primary (planning) | Opus 4.6 | Best reasoning for plans and architecture |
| Primary (execution) | Sonnet 4.6 | Fast, good for code generation |
| Adversarial 1 | Codex (via MCP) | Different training data, catches different issues |
| Adversarial 2 | Gemini (via MCP) | Third perspective, also provides image generation |
| Quick tasks | Haiku | Fast, cheap, good enough for simple operations |

The `family` field on each declared agent names the model family; the value
of declaring it is that the independence of Gate 01/02 is inspectable in the
graph (adversarial-1 ≠ adversarial-2 family) instead of assumed.

## Kill Switches (declared knobs)

All three are the `knobs` block above — machine-readable, and each one only
suppresses declared dispatch edges:

- **Budget exceeded** → stop dispatching reviewer edges this round, proceed
  with primary only, record the skip.
- **Time pressure** → skip only the `adversarial-2` dispatch edge (one
  adversarial review is better than none); the merge edge is never skippable.
- **All reviewers agree** → merger auto-tiers; the merge edge is still
  traversed, because findings reaching the merger is a contract, not a
  convenience.

## Solo-Loop Baseline Clause

The single-execution-core story (one harness — identity lock, gate
evaluation, proof writing, stopping rule — reused across single agent,
delegated sub-agent, and agent-inside-graph) is **a refactor hypothesis, not
an adopted result**: the source itself states no component ablation exists.
So any graph-organized orchestration built on this loop must carry a recorded
**solo-loop baseline score on the same done-test** and report a **positive
delta** to keep its gates green; with no baseline on record, the loop wins by
default and the graph overhead is rejected. This clause is the source's own
critique applied to the source's own claim.

## Integration

- **Goal loops served:** GL-VQ (Verification & Quality), GL-BI (Build & Implementation)
- **Agents governed:** Any agent that produces artifacts for review
- **Doctrine reference:** RIG Convergence Core (GEV Separation — Maker ≠ Grader)
- **Skills used:** rig-triple-review, rig-stress-test
- **Code:** `rig_capabilities/topology.py` (`validate`, `check_dispatch`,
  CLI `python3 -m rig_capabilities.topology validate|dispatch`);
  tests in `tests/test_topology.py`
- **Sibling gate:** `commands/capabilities-dispatch-verify.md` adjudicates
  packet *integrity* (schema lock, stdout hashes, rotating canary, family
  separation); this loop's topology adjudicator answers the prior question —
  whether the packet's hop exists at all in a declared topology.

## Mechanism Attribution (2026-09-02 upgrade)

Derived mechanism text only; creator transcripts/descriptions stay gitignored
under `.context/`.

- **Declared team topology + communication routing along graph edges**
  (topology kind, fixed agent count, routing edges; "communication is only
  allowed along graph edges, so who-may-talk-to-whom becomes a structural
  property rather than emergent"): video `Z90xlttVx3Y`, commentary on
  **arXiv:2608.21156** — *Graph Engineering in the Era of LLM Agents: From
  Individual Intelligence to System Intelligence* (repo `DEEP-JLU/Awesome-Graph-Engineering`).
- **Topology-portable execution core + the baseline/ablation critique**
  (one shared execution core across single-agent/sub-agent/swarm; composability
  and adaptivity claims **not** established by the paper — no component
  ablation): video `lNlMXsUQggc`, commentary on **arXiv:2608.27969** —
  *openJiuwen: Beyond Static Harnesses for Long-Horizon Coding Agents*
  (repo `openJiuwen-ai/jiuwenswarm`).
