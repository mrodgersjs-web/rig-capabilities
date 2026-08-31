---
name: frontier-research-index
description: Frontier deep-research run index (2026-08-31) — 4 react strands on skill organization, routing, self-improvement loops, and evaluation. Records provenance and verified takeaways for the rig-capabilities roadmap.
source: frontier
outcome: "research-intel: how to organize, route, improve, and certify agent skills"
verified_on: 2026-08-31
quality_floor: 0.6
---

# Frontier research index — 2026-08-31

Four FrontierAgent `react` strands were run against this repo
(`frontier --mode react`, model `z-ai/glm-5.3-flash`, local Scrapling web
backend). Each strand did live web research plus repo inspection. Raw traces
(reasoning, tool calls, web fetches) are under `.apodex/runs/20260831-17*-react-*/`
(`trace.jsonl` + `trajectories/*/react_agent.jsonl`).

**Tooling note (verified):** FrontierAgent `react` in `--native` mode on this
box does not emit a clean isolated report file — file writes are gated, and
`--no-tui -p` streams the full trajectory to stdout with a short final-answer
pointer (`answer_bytes` ~110–140). The durable research lives in the run
traces; this index distills the takeaways that are directly actionable for
rig-capabilities and already reflected in its design.

## Strand 1 — skill library organization
- Anthropic Agent Skills: one `SKILL.md` per skill dir, YAML frontmatter
  (`name`, `description`), progressive disclosure (name/description always
  loaded; body on demand). rig-capabilities mirrors this (dir-based skills,
  frontmatter parsed into the index).
- Large libraries need a routing layer over the flat store, not deeper trees:
  outcome lanes + search, which this repo implements (`taxonomy` lanes, BM25,
  dense, graph).
- Keep skills / commands / subagents distinct kinds with one owner per name —
  already the catalog's identity model (`(id, kind)`, canonical shadows external).

## Strand 2 — skill routing & ranking
- Hybrid retrieval (sparse BM25 + dense embeddings) beats either alone for
  capability lookup; add lane routing and graph expansion for recall.
  rig-capabilities `context_pack` fuses exactly these four tiers.
- Token-budgeted packs with per-item provenance are the right MCP return shape
  (implemented: budget + `sha`/trust/freshness per node).

## Strand 3 — self-improvement loops (2025–2026)
- Shipped pattern: generate/mutate → verify with runnable checks → graduate or
  discard; rating-driven trust; adversarial plant-failure to prove gates bite.
- Maps to the roadmap: V15 done-tests, V16 round engine, V22 certification with
  plant-failure (rig-adversarial-verification doctrine).

## Strand 4 — skill evaluation & certification
- Runnable done-criteria + rubric + benchmark harness; certify only when checks
  are green and a reference exemplar exists.
- Proposed `done_when` grammar adopted by this repo: `cmd:` (exit 0), `file:`
  (exists), `grep:<path>:<pattern>`, `mcp:<tool>` — implemented in V15
  (`done_tests.py`) and seeded by the V7 quality contract.

## How this feeds the build
V7 quality contract, V10 great-examples, V15 done-tests, V16 round engine, and
V22 certification are the concrete implementations of these findings. Re-run the
strands with `frontier --mode react` when clean prose deliverables are needed;
harvest from the trace, not stdout.
