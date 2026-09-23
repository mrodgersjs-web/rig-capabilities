---
name: rig
description: "Route rig tasks to an existing child skill; this router adds no capabilities."
---

<!-- canonical-category-router -->
# rig

Select the relevant child below, read its SKILL.md, and follow its instructions. Do not load unrelated children.

- [cross-family-llm-swarm](/Users/rig128gb/.hermes/skills/rig/cross-family-llm-swarm/SKILL.md) — 4+ external LLM reviewer lanes = real verdicts.
- [rig-adrien-craft](/Users/rig128gb/.hermes/skills/rig/rig-adrien-craft/SKILL.md) — Sister umbrella to rig-adrien-doctrines. Houses Adrien's design-style doctrines that scored below the canonical 70-point ship threshold — typography, color science, motion systems, micro-interactions, etc. Load for deep library lookups; loa
- [rig-doctrine-catalog](/Users/rig128gb/.hermes/skills/rig/rig-doctrine-catalog/SKILL.md) — The single source of truth for every RIG doctrine across all 8 umbrellas. Auto-loads on session start. Knows which doctrines exist, their scores, their paths, and which are ship-grade vs draft vs reject. Use when you need to know 'does RIG 
- [rig-doctrine-router](/Users/rig128gb/.hermes/skills/rig/rig-doctrine-router/SKILL.md) — Given a natural-language intent, route to the right RIG doctrine umbrella + child skill. The single entry point that turns 'I want to build...' into 'load /rig-X-doctrines then load /rig-Y-child'. Auto-loads on session start. Closes the dis
- [rig-meta-substrate](/Users/rig128gb/.hermes/skills/rig/rig-meta-substrate/SKILL.md) — The full doctrine substrate — router, pipeline, scoring rubric, reality-audit, wiring, deploy, seal, push, evolution. One skill that knows where every doctrine infra piece lives and how they chain. Auto-loaded with rig-doctrine-router.
