---
id: rig-hq-sub-j4-recall-first
version: 1
status: draft
tier: sub
department: Intelligence
agent: iris-strategy
parent: rig-hq-prompt-iris-strategy
task: Recurring sub-prompt (J4): surface what is already saved and decided, with sources, before anything new
triggers: recall first, what do we already know, prior decision, saved knowledge
sources: ~/.rig/jake/aos/prompt-research/omp-chat-patterns.md (J4), ~/.rig/jake/aos/maps/aside-links/jtbd.json
provenance: first-party RIG design | uncalibrated draft | PROMPT-DESIGN.md S1-S10
---

# Recall first (J4 recurring)

**Trigger.** Something new is starting and existing knowledge may already answer it.

**Typed inputs.** `question`, `search_surfaces` (Memory OS, estate indexes, project
folders), `depth`, `cite_format`.

**Steps.**
1. Search recall/Memory OS through the authenticated front door first; record the
   queries and hits/misses.
2. Search the estate indexes and project folders too — one surface is not coverage.
3. Assemble what is known/decided with per-item source IDs and status preserved.
4. Only then name the gaps that would need new research.

**Output format.**
```
STATUS: DONE | BLOCKED <reason>
Known: <item> -> <source ID/path> (status)
Decided: <decision + record location>
Gaps: <list>
Memory write: <receipt or none>
```

**Expected output.** A sourced "here is what we already have" before any re-research.

**Done test.** Every item resolves to a source ID/path; the recall hit/miss log exists.

**Failure handling.** Retrieval failure -> report it as unavailable and retry next
turn; never claim memory was loaded on failure.

**Persistence.** Answer file saved; writes go through Memory OS and are verified.

**Redaction.** No secrets in retrieved excerpts.

**Stop / escape hatch.** Contradictory sources -> show both with weights and ask.
