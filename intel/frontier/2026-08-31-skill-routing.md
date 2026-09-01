---
name: frontier-skill-routing
description: Frontier research — routing/selection of skills and tools for LLM agents at scale (2026)
source: frontier
outcome: research-intel: skill routing
verified_on: 2026-08-31
quality_floor: 0.6
---

# Skill Routing at Scale — Frontier Findings (2026-08-31)

## The tool-count ceiling is real
Above ~15–20 tools/skills in context, selection quality and token economy collapse.
Every serious 2025–2026 system selects a *subset* per query rather than showing the
catalog. Published tier guidance (ML & AI in Action survey, Jan 2026):

- 5–50 items: in-context descriptions + dynamic prompting.
- 50–200: semantic retrieval + reranking; embedding fine-tuning pays.
- 200–1000: hierarchical routing with category classifiers, A/B tested.
- 1000+: learned selection models + graph-based routing with continual learning.

## Hybrid retrieval beats either side alone
- ToolPicker: BM25 lexical + dense embeddings fused with **Reciprocal Rank Fusion**,
  then token-budget packing of the chosen schemas. Hybrid beats pure-semantic and
  pure-lexical, especially on lexically-cued queries ("cancel" vs "refund" gap).
- "Retrieval Models Aren't Tool-Savvy" (ACL 2025): off-the-shelf embeddings reach
  <35% completeness@10 on tool corpora; **hard-negative fine-tuning** lifts it markedly.
- TURA and multi-stage cascades: coarse embedding recall → cross-encoder rerank →
  LLM confirmation, keeping latency bounded at thousands of tools.

## Routing granularity matters
Tool-to-Agent Retrieval (arXiv 2511.01854) embeds tools *and their parent agents* in one
vector space with metadata links, returning a single tool or a whole agent bundle
whichever fits the query — 0.83 Recall@5 vs 0.74 for ScaleMCP on LiveMCPBench. Set-level
retrieval (HYSET, arXiv 2607.25718) scores candidate *sets* via hyperedge prediction —
tools are not independent.

## What this means for rig-capabilities
1. Our context_pack already fuses BM25 + dense (ollama nomic-embed) + graph expansion —
   same shape as ToolPicker; we should add explicit RRF (currently weighted union) and a
   token-budget packer cap per lane.
2. TAR's dual-granularity trick maps directly: we index both capabilities and agent
   packs (`agents/<id>/pack.json`) — routing should be able to return *a pack* when the
   query is agent-shaped.
3. Set-level utility is the argument for packs over flat top-k: co-selected assets
   should be scored jointly (our outcome-lanes are a crude version of this).
4. At 4608 assets we are in the "200–1000 → 1000+" tier: keep the lane classifier,
   invest in hard-negative mining from trace logs (assets retrieved-but-unused).

## Sources
- https://github.com/AshwinUgale/toolpicker
- https://ajing.github.io/posts/2026-01-10-tool-selection-optimization-llm-agents-at-scale/
- https://arxiv.org/pdf/2511.01854 (Tool-to-Agent Retrieval, LiveMCPBench)
- https://arxiv.org/html/2607.25718 (HYSET set-level tool retrieval)
- https://arxiv.org/pdf/2508.04604 (TURA three-stage tool retrieval)
- ACL 2025 "Retrieval Models Aren't Tool-Savvy" (hard-negative fine-tuning), cited via survey above
- https://github.com/Epsilon617/ToolScout (execution-aware routing)
