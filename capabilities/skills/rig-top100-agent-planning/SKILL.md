---
name: rig-top100-agent-planning
description: "Turn an ambitious one-liner into an executable plan: goal decomposed into a dependency graph with estimates, each node carrying a done-test, rollback named before execution, and the unknowns listed instead of hidden. Use when a request is too big to attempt in one shot ('build me a 1000x knowledge pipeline'), when a plan is a list of verbs with no tests, or when a run stalled halfway with no way to resume."
tags: [rig, top100, agentic-systems, planning, decomposition, dependency-graph]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 15
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-planning/SKILL.md
outcome: "A plan where every node has an owner, an estimate, a done-test, and a rollback; the critical path is identified; unknowns are listed with the cheapest probe for each; and executing the graph produces the objective without a re-plan mid-run."
activation: "Load for any task with three or more dependent steps, before committing to an epic, when a plan needs to be handed to another agent, and whenever a past run stalled with no resumable state."
instruction: "Write the objective as an artifact plus a check, then decompose into nodes that each finish in one sitting. Give every node a done-test, an estimate, and a named rollback. Wire dependencies, find the critical path, and schedule the cheapest probes for the unknowns first so they resolve before the expensive nodes. A node without a test is a wish. Re-plan at node boundaries, never mid-node, and keep the plan file as the resumable state."
applies_when:
  env: "the repo or working directory that will hold the plan file and its artifacts"
  deps: "a plan format the executor can read; a place to record node status; git for rollback"
  runtime: "planning pass by a capable model; execution may be split across agents"
  params: "objective, constraints, deadline or token budget, known unknowns"
  budget: "planning cost under 10 percent of estimated execution"
  scale: "one epic to a multi-agent build; a 2-step task does not need this ceremony"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - State the objective as one artifact and one executable check that proves it exists and is right.
  - Decompose to nodes that each complete in one sitting; if a node needs hours, split it.
  - Give every node: owner, inputs, outputs, estimate, done-test, and rollback.
  - Wire dependencies and identify the critical path; put float on the non-critical branches.
  - List unknowns explicitly and attach the cheapest experiment that resolves each one.
  - Run the probes first; a probe that changes the graph invalidates the plan and gets re-planned.
  - Order so irreversible steps come after their evidence exists.
  - Track node status in the plan file so any agent can resume without a verbal handoff.
done_when:
  - "cmd:test -f ${RUN_DIR:-./out/rig-top100-agent-planning}/plan.json && jq -e '.nodes | length >= 3' ${RUN_DIR:-./out/rig-top100-agent-planning}/plan.json"
  - "cmd:jq -es -e 'all(.[]; .done_test != null and .rollback != null and .estimate != null)' ${RUN_DIR:-./out/rig-top100-agent-planning}/nodes.jsonl"
  - "cmd:jq -e '[.nodes[].id] as $ids | all(.nodes[].deps[]; IN($ids[]))' ${RUN_DIR:-./out/rig-top100-agent-planning}/plan.json"
  - "cmd:jq -e '.unknowns | length >= 1 and all(.[]; .probe != null)' ${RUN_DIR:-./out/rig-top100-agent-planning}/plan.json"
  - "grep:SKILL.md:critical path"
out_of_scope:
  - a plan of verbs with no test per step
  - re-planning mid-node instead of finishing or stopping the node
  - hiding unknowns so the plan looks certain
  - planning depth that costs more than the work it organises
---

# Goal Decomposition and Planning

## Why this exists

Single-shot prompting works on small tasks and quietly fails on large ones: the agent produces
a plausible partial and calls it done. The plan earns its keep by making each step falsifiable
before anyone starts, so "done" is a set of passed tests rather than a feeling.

## Outcome contract

- Why: 'Build me a 1000x knowledge pipeline' requires multi-step planning
- Baseline: Single-shot prompting
- Target: Tree-of-thought planning with dependency graphs, resource estimation, and rollback

## Method

### 1. Objective as artifact plus check

"Build the pipeline" is unfalsifiable. "16K transcripts in Supabase, 95 percent coverage,
searchable by phrase, verified by a count query and three spot checks" can be judged by someone
who was not there. Write that line first; it is what the graph serves.

### 2. Nodes that finish in one sitting

A node is the smallest unit someone would defend on its own. Size by context, not by topic: a
node that needs the whole repo in the window will fail half-finished. Every node carries an
owner, inputs, outputs, an estimate, a done-test, and a rollback.

### 3. Dependencies and the critical path

Draw the edges, find the longest chain, and put the probes for uncertain nodes on it. Anything
off the critical path is where an estimate error is survivable, so that is where to put the
optional work. A cycle is not a plan detail; it means a node is doing two jobs.

### 4. Unknowns get probes, not optimism

List what is not known and attach the cheapest experiment that resolves it: an hour of
measurement beats a day of argument. Run probes before the expensive nodes they unblock. A probe
that changes the graph is a success: re-plan at the node boundary.

### 5. Rollback and resume

Name the revert before the change, especially for irreversible steps (migrations, deletes,
outward sends). Status lives in the plan file, so a different agent tomorrow picks up at the
next ready node without asking what was happening.

## Failure modes

- Ceremony: a plan whose only purpose is to justify not starting.
- Nodes too big to finish, producing a permanent 80 percent.
- Done-tests written after the work, then shaped to fit what got built.
- Unknowns omitted, so the first surprise is mid-run and the re-plan is a panic.
- Re-planning mid-node, which destroys the resume property and hides which step actually failed.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-planning}
r=0
jq -e '.nodes | length >= 3' "$RUN_DIR/plan.json" >/dev/null || { echo "BLOCK too few nodes"; r=1; }
jq -es -e 'all(.[]; .done_test != null and .rollback != null and .estimate != null)' "$RUN_DIR/nodes.jsonl" >/dev/null || { echo "BLOCK node without test or rollback"; r=1; }
jq -e '[.nodes[].id] as $i | all(.nodes[].deps[]; IN($i[]))' "$RUN_DIR/plan.json" >/dev/null || { echo "BLOCK dangling dependency"; r=1; }
jq -e '.unknowns | length >= 1 and all(.[]; .probe != null)' "$RUN_DIR/plan.json" >/dev/null || { echo "BLOCK unprobed unknown"; r=1; }
jq -es -e '[.[] | select(.status==\"done\") | .test_output] | all(. != null)' "$RUN_DIR/nodes.jsonl" >/dev/null || { echo "BLOCK done node with no test output"; r=1; }
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Hand the plan to someone who did not write it and ask which node they would run first and how
they would know it passed. Then check the graph: every node reachable from a root, no cycles,
critical path named. After execution, confirm every done node has its stored test output and
that the objective check from section 1 actually passes; a green graph over a failed objective
means the tests were wrong.

## Related

`rig-top100-agent-orchestration` (execute the graph in parallel), `rig-top100-okrs` (which
objectives deserve a plan), `rig-top100-scenario-planning` (premortems on the risky branch),
`rig-top100-agent-observability` (node evidence rows).
