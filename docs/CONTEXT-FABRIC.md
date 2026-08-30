# Context Fabric — the infographic, built

Maps the enterprise-architecture infographic (OKF knowledge bundles → knowledge
catalog → discovery index layer → context fabric → runtime context graph +
agent feedback) onto what runs in this repo. One hub, one owner per name:
`rig-capabilities` is simultaneously the knowledge base (canonical assets),
the MCP server (all coding agents), and now the context fabric.

## Layer map

| Infographic layer | Implementation | Where |
|---|---|---|
| Open Knowledge Bundles (Git/SQL/API sources) | Git is real: 86 canonical assets + 9 external harness roots (~3k files), content-hash versioned. **Not built: SQL/API federation** — nothing external is federated today; the `sha` field is the provenance handle any future connector must preserve. | `capabilities/`, `config.json` external_roots |
| Bundle contract (metadata / access / freshness / trust) | `okf.py`: frontmatter contract `owner, domain, status(Stable\|Draft\|Deprecated), version, verified_by/on, acl[], relates_to[]`. Trust = deterministic formula (source base .9/.7/.6 ± status/age modifiers, floor .1). Freshness = Stable/Fresh/Stale/Aging/Deprecated. `okf-check` reports completeness; index carries `okf` per asset. | `rig_capabilities/okf.py` |
| Knowledge catalog | `catalog.py` index: 4.5k+ assets × (kind, source, sha, tags, outcome lane, okf). Identity = name+kind; content sha dedupes; canonical > installed > external precedence. | `.index.json` |
| Discovery index layer — metadata | lanes/domain/tags filter, `min_trust` gate, ACL intersection (single-user rig: ACL is declared, not enforced org-wide — honest gap). | `fabric.context_pack` |
| — vector | Real local embeddings: ollama `nomic-embed-text` @127.0.0.1:11434, cosine over `.embeddings.json` cache keyed `id@sha` (re-embeds only changed content). No ollama → dense tier reports `false` in the pack's `tiers` dict; nothing pretends. | `fabric.build_embeddings/dense_search` |
| — graph | `.graph.json`: declared `relates_to` (w=3) + shared-rare-token edges (Jaccard ≥ .15, top-12/asset); BFS `expand(depth)`. | `fabric.build_graph/expand` |
| — semantic/concept | `.concepts.json`: normalized tags + rare IDF nouns → asset ids (heuristic, not LLM). | `fabric.build_concepts` |
| Context fabric (context as a service) | MCP tools: `capabilities_context_pack` (default entry point — agents stop scavenging filesystems), `capabilities_route`, `capabilities_graph`, `capabilities_concepts`. CLI twins: `pack/route/graph/concepts`. Token budget enforced (`chars/4`), output = markdown with per-bundle provenance lines. | `server.py`, `bin/rig-capabilities` |
| Runtime context graph (session artifact) | Every pack persists `.context/<pack-id>.json`: intent, budget, tier flags, lanes, nodes (id/kind/source/sha/trust/freshness/score/tier core\|adjacent). Sessions can cite, rehydrate, and diff the exact context they ran on. | `.context/` |
| Agent feedback | `capability rate <pack-id> useful\|partial\|wasted [note]` → `.context/ratings.jsonl`; scores feed back via `rig-capabilities outcomes` / trust tuning. | `fabric.rate` |

## Degradation contract

`pack` never fakes a tier. `tiers` in every response says exactly what ran:
`{metadata_filter: true, sparse_bm25: true, dense_ollama: bool, graph: bool}`.
Sparse BM25 (k1=1.5, b=0.75) is stdlib-only and always on, so the fabric
still answers with ollama down — with the gap declared in-band.

## Deliberate gaps

- SQL/API bundle connectors (no external stores wired).
- ACL enforcement beyond intersection filtering (single operator today).
- Concept extraction is IDF heuristics, not LLM-tagged.
- Langfuse observability stack: separate infra decision (see prior phase), not wired.
