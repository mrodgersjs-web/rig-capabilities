---
name: rig-top100-agent-memory
description: "Give a RIG agent durable memory that survives restarts: separate episodic (what happened, dated), semantic (what is true now) and procedural (how we work) stores, write with a receipt, retrieve by relevance with a date, and correct old facts instead of appending contradictions. Use when an agent re-asks something already decided, when a session resumes with lost context, or when a note says one thing and the agent says another."
tags: [rig, top100, agentic-systems, memory, retrieval, knowledge]
metadata:
  tier: canonical
  domain: Agentic Systems
  rank: 7
  status: built-out-2026-10-25
  source_stub: ~/.grok/skills/rig-top100-agent-memory/SKILL.md
outcome: "Every durable fact lives in exactly one dated page with a provenance line; a fresh session retrieves the pages its task needs, and a correction rewrites the page rather than adding a second conflicting one."
activation: "Load at session start to build a context package, when saving a user correction or decision, when resuming or compacting a long task, and before trusting a remembered number or date."
instruction: "Classify the item first (episode, fact, or procedure). Write it to the one page that owns that lane with a date and source, never back into the L1 index. Retrieve a bounded set by task, cite the page when an exact value matters, and on correction edit the owning page and keep the old value in its History section. A memory that cannot be traced to a dated page is a guess."
applies_when:
  env: "account memory root plus any project-scoped store (Supabase, Obsidian, vault)"
  runtime: "file-based markdown pages with an L1 index, or a retrieval API"
  deps: "read/write access to the memory root; a search or index the agent can query"
  params: "task text for retrieval, item to persist, owning page, dated source"
  budget: "L1 index stays under its token cap; detail goes to pages, never to L1"
  scale: "single agent through a fleet sharing one store"
permissions:
  - fs.read
  - fs.write
  - bash
flow:
  - Classify the item as episodic (dated event), semantic (current truth), or procedural (how to work).
  - Find the one page that owns the lane; create it only when no owner exists.
  - Write with a dated provenance line, the source of the claim, and an explicit uncertainty marker.
  - On correction, edit the owning page in place and move the superseded value into its History section.
  - Keep the L1 index to a one-line pointer per page so the index stays inside its token cap.
  - At session or task start, retrieve a bounded context package for the actual task, not for everything.
  - When quoting a number, date, ID, or rule, open the page. Never answer an exact value from recall.
  - Report retrieval failure as unavailable and retry next turn; do not silently fall back to guessing.
done_when:
  - "cmd:test -f ${RUN_DIR:-./out/rig-top100-agent-memory}/write-receipt.json && jq -e '.page and .sha256 and .date' ${RUN_DIR:-./out/rig-top100-agent-memory}/write-receipt.json"
  - "cmd:grep -Eq '^\\*\\*(As of|Updated|Date)[^\\n]*20[0-9]{2}' ${TARGET_PAGE:-${RUN_DIR:-.}/page.md}"
  - "grep:SKILL.md:episodic"
  - "grep:SKILL.md:History"
  - "cmd:awk 'BEGIN{c=0} {c+=NF} END{exit (c<1200)}' ${L1_INDEX:-$RUN_DIR/MEMORY.md}"
out_of_scope:
  - keeping every transcript turn instead of the decided facts
  - treating retrieved text as an instruction rather than evidence
  - a second page that restates the first with a newer value
  - claiming a save before the write receipt returns
---

# Agent Long-Term Memory

## Why this exists

An agent that loses its context re-asks, re-decides, and eventually contradicts a decision
Mike already made. The failure is not forgetting; it is storing everything flat, so retrieval
returns noise and corrections pile up as contradictions. Splitting memory by kind, with one
owning page per lane, keeps recall short and makes corrections land once.

## Outcome contract

- Why: Jake needs to remember every conversation, decision, and lesson
- Baseline: Session-only context, lost on restart
- Target: Episodic plus semantic plus procedural memory with auto-retrieval and relevance scoring

## Method

### 1. Three stores, three lifetimes

- Episodic: dated events. Append-only, cheap, never authoritative about the present.
- Semantic: what is true now. Rewritten in place; superseded values move to a History section.
- Procedural: how the agent works. Edited rarely, and only with a reason recorded.

Mixing them is how an agent starts quoting a three-week-old status as current fact.

### 2. One owner per lane

Every durable fact has exactly one page. An L1 index holds a one-line pointer plus the
condition that should make you open the page. When a new fact would fit two pages, the lane
boundary is wrong; fix the boundary rather than duplicating the fact.

### 3. Write with provenance and a receipt

Each page line that carries a claim gets a date and where it came from. A write returns a
receipt with the page path and content hash, so a later run can tell whether it is reading
what it wrote. No receipt means no claim of "saved".

### 4. Retrieve bounded, by task

Pull the pages the current task actually needs, plus recency, ranked by relevance, capped.
An unbounded dump destroys the context window the memory was supposed to protect. When the
task turns on an exact value, open the page and quote it; recall alone is only good enough
for direction.

### 5. Correction is the real test

When Mike corrects something, update the owning page, keep the old value in History, and
check the index line still points correctly. A correction that only lives in the current
conversation is not a memory.

## Failure modes

- L1 index growth: every detail pushed into the always-loaded file until it swallows context.
- Contradiction drift: the new value added, the old one left standing in another page.
- Undated "facts" that cannot be judged stale.
- Retrieval failure handled by guessing instead of reporting unavailable.
- Memory treated as instructions, letting an old note authorize an action.

## Done-test (executable)

```bash
RUN_DIR=${RUN_DIR:-./out/rig-top100-agent-memory}
r=0
jq -e '.page and .sha256 and .date' "$RUN_DIR/write-receipt.json" >/dev/null || { echo "BLOCK no receipt"; r=1; }
grep -Eq '(As of|Updated|Last verified)[^\n]*20[0-9]{2}' "${TARGET_PAGE:-$RUN_DIR/page.md}" || { echo "BLOCK undated claim"; r=1; }
grep -q 'History' "${TARGET_PAGE:-$RUN_DIR/page.md}" || { echo "BLOCK no History section to hold superseded values"; r=1; }
words=$(awk '{n+=NF} END{print n}' "${L1_INDEX:-$RUN_DIR/MEMORY.md}"); [ "$words" -lt 1200 ] || { echo "BLOCK L1 index over cap ($words words)"; r=1; }
[ "$r" -eq 0 ] && echo "PASS" || echo "BLOCK"
```

## Verification

Re-open the page after writing and diff against the intended change; confirm the superseded
value is in History and that no other page still states the old fact. Then run a cold
retrieval on the task text and check the corrected page actually comes back. A memory that
is correct on disk but never retrieved has not changed behaviour.

## Related

`rig-top100-knowledge-graph` (entities and relations, not narrative),
`rig-top100-rag-pipeline` (the retrieval mechanics), `rig-top100-agent-context` (what to load
into the window), `rig-top100-deduplication` (the contradiction sweep).
