---
name: rig-top100-agent-context
description: "Allocate the context window deliberately instead of truncating at the limit: a small always-loaded core, hierarchical summaries of older turns, retrieval-on-demand for bulk material, and an explicit budget per section. Use when a long conversation loses the original instruction, when compaction produced a summary that dropped a constraint, or before loading a big corpus into a task's window."
tags: [rig, top100, agentic-systems, context, summarization, compaction, retrieval]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 18
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-context/SKILL.md
outcome: "A task's window is a budgeted set of sections with provenance and dates, the binding constraints survive any compaction, and anything dropped can be re-retrieved by reference rather than remembered."
activation: "Load when a session is long enough to compact, when a summary has lost a decision or a number, when a task needs material bigger than the window, and when writing the L1 index any agent always loads."
instruction: "Split the window into fixed core, rolling summary, and retrieval slots, with a word budget each. The core holds identity, hard floors, and current objectives and never gets summarised. Summaries are lossy by design, so every superseded detail keeps a pointer to its source page. Compress by abstraction, not by deletion: state what changed, what is still open, and where the originals live. Re-read a constraint from its page whenever an exact value matters."
applies_when:
  env: "any agent with a bounded window: chat sessions, routine runs, subagent dispatches"
  deps: "durable memory pages or a store the summaries can point into"
  runtime: "provider compaction, a hand-written summary step, or RAG retrieval"
  params: "section budgets, summary cadence, retention of originals, retrieval top-k"
  budget: "core plus summaries under 20 percent of the window"
  scale: "one long conversation to a multi-day task resumed across sessions"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Define the fixed core: identity, hard floors, current objective, and the constraints that must survive.
  - Give every section an explicit budget in words, and check the total against the window.
  - Summarise older turns by abstraction: what was decided, what changed, what is still open.
  - Keep pointers, not paraphrases, for anything exact: file paths, ids, quotes, hashes.
  - Move bulk material to retrieval slots loaded on demand instead of pasting it in.
  - After compaction, re-read the objective and the approvals from their source, not from the summary.
  - Log what was dropped and where it still lives, so the next turn can go get it.
  - Rebalance budgets when a section repeatedly overruns; an overrun is a signal about the task shape.
done_when:
  - "cmd:jq -e '.core_words > 0 and .core_words < 2000 and .sections | length >= 3' ${RUN_DIR:-./out/rig-top100-agent-context}/budget.json"
  - "cmd:jq -e '(.sections[] | select(.name==\"core\") | .always_loaded) == true' ${RUN_DIR:-./out/rig-top100-agent-context}/budget.json"
  - "cmd:jq -es -e 'all(.[]; .dropped[] | .location != null)' ${RUN_DIR:-./out/rig-top100-agent-context}/dropped.jsonl"
  - "cmd:grep -Eq 'objective|Objective' ${RUN_DIR:-./out/rig-top100-agent-context}/handoff.md"
  - "grep:SKILL.md:pointers"
out_of_scope:
  - treating a compaction summary as a faithful record of an approval
  - loading a whole corpus because retrieval has not been set up
  - deleting detail without leaving a pointer to the original
  - an always-loaded index that grows until it is the whole context
---

# Context Window Management

## Why this exists

Every long agent task fails the same way: the window fills, the oldest thing in it was the
instruction that mattered, and truncation removes it silently. Context is a budgeted resource
like money. Managed deliberately it looks like a small core, dated summaries, and pointers;
unmanaged it looks like an agent confidently working to a constraint it never got to keep.

## Outcome contract

- Why: Long conversations exceed context limits and must compress intelligently
- Baseline: Truncate at limit
- Target: Hierarchical summarization, RAG retrieval, and dynamic context allocation

## Method

### 1. Three sections with budgets

Fixed core (identity, hard floors, objective, approvals): never summarised, always loaded,
under about 2 thousand words. Rolling summary (what was decided, what changed, what is open):
rewritten on a cadence, not on a panic. Retrieval slots (bulk material pulled by reference):
loaded per step and released afterwards. Write the numbers down; an unfunded section quietly
takes the whole window.

### 2. Compress by abstraction, not deletion

A good summary states the decision and the reason, and keeps the artifact path. A bad one keeps
the prose and loses the path. The rule: keep what changes behaviour, point at what only explains
it. Anything numeric, named, or approved keeps a pointer plus its value.

### 3. Pointers survive, paraphrases rot

A summary saying "the user approved the batch" is worthless two turns later; "approval id A-118,
`outward-guard/ledger.json`, batch of 15" can be re-read and defended. Retrieval-backed
detail is safe to lose from the window; unbacked detail is a permanent loss.

### 4. Compaction is a checkpoint, not a rewind

Right after compaction, re-read from source: the objective, the exact approvals, the paths
already written. This is where a task silently changes direction, because the summary is
plausible and the constraint that would have contradicted it is gone.

### 5. Retrieval instead of pasting

Material bigger than the window does not belong in it. Chunk, index, and load top-k per step;
summarise on ingest so the window sees the abstraction, not the raw. This is what lets a task
touch 16K videos without ever holding them.

## Failure modes

- L1 index creep: always-loaded files grow until they are the budget.
- Summary drift: each re-summary loses a little more, and nobody notices for a week.
- An approval restated from memory, then acted on, then discovered to have been narrower.
- Retrieval added late, so early decisions were made on a partial view and never revisited.
- Compression that drops the failed approaches, so the agent redoes the work that did not work.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-context}
r=0
jq -e '.core_words > 0 and .core_words < 2000' "$RUN_DIR/budget.json" >/dev/null || { echo "BLOCK core over budget"; r=1; }
jq -e '[.sections[] | select(.name=="core")][0].always_loaded == true' "$RUN_DIR/budget.json" >/dev/null || { echo "BLOCK core not pinned"; r=1; }
jq -es -e 'all(.[]; .location != null)' "$RUN_DIR/dropped.jsonl" 2>/dev/null || { echo "BLOCK dropped detail with no pointer"; r=1; }
grep -Eq '(^# |^)[^\n]*[Oo]bjective' "$RUN_DIR/handoff.md" || { echo "BLOCK handoff without objective"; r=1; }
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Take the same task twice: once with the summary only, once with the summary plus re-reads from
source. Any divergence in the output is a constraint the summary lost, and goes into the core or
gets a pointer. Then ask the agent to name what it dropped and where it still lives; if it
cannot, the pointers are not there.

## Related

`rig-top100-agent-memory` (the pages the pointers address), `rig-top100-rag-pipeline` (the
retrieval slots), `rig-top100-content-summarization` (chunk-level abstraction),
`rig-top100-agent-planning` (the resumable state a handoff must carry).
