---
id: pattern-subagent-search-isolate
version: 1
status: draft
updated: 2026-09-24
task: Isolate search in sub-agents so the lead agent only synthesizes and decides
category: prompt-craft
domain: prompt-craft
model_target: unspecified
score: null
license: pattern-with-attribution
source: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
triggers: sub agent research isolate search context lead agent synthesizes research with subagents delegate the search context isolation
compose: 
provenance: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | paraphrased pattern with attribution, not copied text
content_sha256: 6c51ea724a28b45ef4a26be338b358eb11e316ba9ec1c755875c0b1e7e420d9f
---

For research-shaped jobs, isolate the search mess from the judgment: sub-agents search and gather raw context; the lead agent only synthesizes and decides.

Lead prompt shape:
- the decision to be made and the evidence bar it must clear
- the exact output: ranked findings with sources, and anything unknown named as unknown

Sub-agent prompt shape:
- one bounded search objective each
- return findings with source URLs and dates, never conclusions

Why it works: the detailed search context stays inside the sub-agent's window, so the lead's window keeps only what the decision needs. Pair with compaction on long-horizon runs (summarize the critical details and re-initiate), not with more prompt text.

Pattern paraphrased from Anthropic, "Effective context engineering for AI agents" (2025-09-29). Not copied text.
