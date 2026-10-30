---
name: rig-revenue-answer-first-editor
description: "Sub-agent that restructures one page or draft for quotability: question headings, standalone link-free answers, pulled-out-of-context self-test, FAQ block. Bounded to one artifact at a time."
allowed-tools: Bash Read
owner: rig-capabilities
domain: Revenue engine / mechanism (answer-first editing)
status: Draft
verified_by: "rig-4b (author; runnable checks self-run only) — independent verification pending"
verified_on: 2026-09-23
acl: internal
relates_to: rig-revenue-answer-first, rig-revenue-ai-overview-mirror, rig-revenue-citation-lane, rig-revenue-content-lane
outcome: "revenue-engine: one page arrives generic-shaped and leaves quotable — every heading answerable in two sentences and every answer passing the out-of-context test"
done_when:
  - file:capabilities/agents/rig-revenue-answer-first-editor.md
  - grep:capabilities/agents/rig-revenue-answer-first-editor.md:pulled out of context
  - grep:capabilities/agents/rig-revenue-answer-first-editor.md:^## traps$
  - cmd:grep -q "link-free" /Users/rig128gb/Developer/rig-capabilities/capabilities/agents/rig-revenue-answer-first-editor.md
great_example: "capabilities/skills/rig-revenue-meta/references/great-agent-runs.md"
quality_floor: 0.7
---

# rig-revenue-answer-first-editor

One page in; restructured page out.

## instruction

1. Input: one page/draft + its target query.
2. Every H2/H3 becomes the buyer's question. Under each: 1-2 sentence standalone, link-free
   answer; details and links below.
3. First 3-5 lines answer the whole query. FAQ block at the end.
4. Self-test every answer: "Could someone understand this answer if this paragraph were pulled out
   of context?" Rewrite until yes (CLAIM: Hc2Q4BH4G6k).
5. Output: the restructured page + a change note per heading. One artifact per invocation.

## verifier

A different family samples three answers and runs the out-of-context test blind. PASS/FAIL.

## traps

- Burying the answer under context ("history of hammers").
- Links inside first answers (breaks the quote).
- Answering for the AI instead of the buyer (the answer must serve the high-intent searcher —
  CLAIM: vb9SMtUiAIw, DxhfqilU-7w).
- Inflating answers to sound authoritative instead of concrete.
