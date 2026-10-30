---
name: rig-top100-agent-orchestration
description: "Run many RIG agents on one mission without collisions: split work into claimed slices, give every agent exclusive writable paths, dispatch with a role contract, and have the coordinator merge only outputs that passed a done-test. Use when a job needs parallel agents, when agents have overwritten each other's files, or when the fleet grows past what one person can hand-drive."
tags: [rig, top100, agentic-systems, orchestration, multi-agent, coordination]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 6
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-orchestration/SKILL.md
outcome: "A swarm run where every agent held an exclusive claim, no two agents wrote the same path, and the coordinator produced one reconciled artifact plus a receipt naming every child, its claim, and its verdict."
activation: "Load before spawning more than two agents on one mission, when a run produced write conflicts or duplicated work, or when roles must be reassigned mid-run."
instruction: "Write a mission brief with one measurable objective, partition it into disjoint slices, make each agent claim its slice and writable paths before it acts, dispatch with an explicit role contract, and merge only children that returned a passing done-test. Unproven children are re-run or dropped, never quietly merged."
applies_when:
  env: "local fleet (laptop cockpit plus workers) and any harness that can spawn child sessions"
  runtime: "child sessions, subagents, or queue workers driven by a coordinator task"
  deps: "a shared filesystem or store the coordinator can read; somewhere to record claims"
  params: "mission brief, slice list, per-slice writable paths, concurrency cap, deadline"
  budget: "one coordinator pass plus one attempt per slice; a second attempt only on a named failure"
  scale: "3 to 100 agents; below 3 the coordination cost usually exceeds the gain"
permissions:
  - fs.read
  - fs.write
  - bash
  - agent.spawn
  - gate-d-required:outward-actions-by-children
flow:
  - Restate the mission as one measurable objective with a path-shaped or numeric done-test.
  - Partition into disjoint slices where each slice owns its own output paths; write the partition table before dispatch.
  - Give each slice a role contract: reads, allowed writes, forbidden writes, done-test, budget, deadline, evidence format.
  - Acquire an exclusive claim per slice and per writable path; a slice that cannot claim waits instead of writing.
  - Dispatch children under the concurrency cap; children never go outward without their own approval id.
  - Poll children between the deadline and the cap; re-dispatch only after naming why the first attempt failed.
  - Reconcile: merge only children whose done-test passed, and record a verdict for every child.
  - Retire claims and write the reconciled artifact plus the run receipt in the same step.
done_when:
  - "cmd:test -f ${RUN_DIR:-./out/rig-top100-agent-orchestration}/receipt.json"
  - "cmd:jq -e '.slices | length >= 1' ${RUN_DIR:-./out/rig-top100-agent-orchestration}/receipt.json"
  - "cmd:jq -e '[.slices[].writes[]] | length == ([.slices[].writes[]] | unique | length)' ${RUN_DIR:-./out/rig-top100-agent-orchestration}/receipt.json"
  - "grep:SKILL.md:claim"
  - "grep:SKILL.md:role contract"
out_of_scope:
  - free-text agent chat as the primary coordination mechanism
  - letting a child push, email, publish, or spend without an approval id
  - merging an unverified child output because the run was already long
  - spawning agents to avoid deciding the partition yourself
---

# Multi-Agent Orchestration

## Why this exists

RIG's throughput ceiling is how many agents Mike can supervise at once, and manual prompt
switching caps that at a handful. The fix is not more agents, it is a partition with
exclusive claims: agents collide on writes and on duplicated thinking, never on read volume.

## Outcome contract

- Why: RIG needs to run 86+ agents simultaneously without conflicts
- Baseline: Manual prompt switching between agents
- Target: Self-organizing agent swarm with dynamic role assignment, conflict resolution, and shared memory

## Method

### 1. Mission brief before partition

One objective, one done-test. "Improve the skills" cannot be partitioned because any slice
looks like progress. Write it as an artifact plus a check: "15 built-out SKILL.md files under
$RUN_DIR, each passing its own done-test."

### 2. Disjoint slices, owned paths

Partition on output paths, not on topics. Two slices that both touch `MEMORY.md` are one
slice. Each slice declares `reads`, `writes`, `must_not_write`. Overlapping reads are free;
overlapping writes are the bug.

### 3. Claims are locks, not intentions

A child takes its claim before it edits: a lock file, a row in a claims table, an index
entry. If the claim is held it waits or takes another slice. It does not "merge carefully
afterwards". Single-writer is the rule the rest of RIG already runs on.

### 4. Role contract

Every dispatch carries the slice, input paths, allowed writes, done-test, token or cost
budget, deadline, and evidence format. Dynamic role assignment means the coordinator may
hand a finished child a new slice, but only by issuing a new contract with a new claim,
never by silently extending the old one.

### 5. Reconcile on proof

Accept a child output only when its done-test passes on the real artifact. Verdicts are
`pass`, `fail` (re-run with a named cause), or `dropped`. A dropped slice stays in the
receipt so the gap survives instead of vanishing into an "everything looks fine" summary.

## Failure modes

- Fan-out as a substitute for thinking: 20 agents rediscovering the same three facts.
- Write collisions found after the fact, patched into a worse artifact.
- A coordinator accepting a confident summary with no artifact behind it.
- Children going outward because the parent had already been approved.
- Claims still held after the children died, so the next run blocks.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-orchestration}
r=0
test -f "$RUN_DIR/receipt.json" || { echo "BLOCK no receipt"; r=1; }
jq -e '.slices | length >= 1' "$RUN_DIR/receipt.json" >/dev/null || { echo "BLOCK no slices"; r=1; }
jq -e '[.slices[].writes[]] | length == ([.slices[].writes[]] | unique | length)' "$RUN_DIR/receipt.json" >/dev/null || { echo "BLOCK double claim"; r=1; }
jq -e 'all(.slices[]; (.verdict | IN("pass","fail","dropped")))' "$RUN_DIR/receipt.json" >/dev/null || { echo "BLOCK missing verdict"; r=1; }
while read -r p; do test -f "$p" || { echo "BLOCK missing $p"; r=1; }; done < <(jq -r '.slices[] | select(.verdict=="pass") | .outputs[]' "$RUN_DIR/receipt.json")
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

Receipt shape: `{mission, dispatched_at, slices: [{id, role, reads, writes, must_not_write, verdict, outputs, cost}]}`.

## Verification

Read the receipt back from disk, not from the coordinator's own message. Two eyeball checks:
no two slices share a writable path, and every `pass` output actually contains the substance
the slice claimed. If every child passed and nothing differs from the input, the partition
was wrong, not the run.

## Related

`rig-top100-agent-communication` (message shapes), `rig-top100-agent-safety` (what a child
may do unattended), `rig-top100-agent-observability` (proof per child),
`rig-top100-agent-cost` (per-slice budgets).
