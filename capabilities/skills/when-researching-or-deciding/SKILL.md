---
name: when-researching-or-deciding
description: "When researching a topic, extracting doctrine, synthesizing evidence, scoring ideas, or convening advisory deliberation, use this to route to the right research skill so claims carry sources. Routes to 94 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: research-knowledge
  skill-count: "95"
done_when:
  - 'grep:capabilities/skills/when-researching-or-deciding/SKILL.md:[M]UST NOT load a second child to'
  - 'grep:capabilities/skills/when-researching-or-deciding/SKILL.md:[M]UST load exactly ONE child skill per task step'
  - 'grep:capabilities/skills/when-researching-or-deciding/references/routing.md:^\| Skill \| Source \| One-liner \| Sub-skills \|'
---

# when-researching-or-deciding

Tier-1 meta-skill. Job to be done: When researching a topic, extracting doctrine, synthesizing evidence, scoring ideas, or convening advisory deliberation, use this to route to the right research skill so claims carry sources.

## Hierarchy
1. **Meta-skill (this file)** — the skill you call up for this job. Routes only; holds no doctrine of its own.
2. **Skills** — load the named child skill's SKILL.md and follow it. Each child is written to route further when it owns a family.
3. **Sub-skills** — a skill whose routing entry lists sub-skills delegates further; load only the one sub-skill the task needs.

## Routing contract (binding)
- MUST route through this meta-skill first for any job in its description; never load a child directly from memory of its name.
- MUST load exactly ONE child skill per task step; never bulk-load children from the index.
- MUST load only the single sub-skill the task needs, only when the loaded child names sub-skills.
- MUST NOT load a second child to "compare"; if two children seem to match, pick by the routing table one-liner in references/routing.md, then load that one.
- The quick index below is a relevance-ordered SAMPLE, not the full set; if no index entry fits the task, scan the full table in references/routing.md before choosing.
- If no child matches the task, load `when-nothing-else-fits` instead of guessing.
- If a child skill fails to load or is missing, report the broken route and stop; do not improvise its content.

## How to route
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 94-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **business-strategy-os** — Meta-skill for business strategy from a 1,679-transcript corpus: is this a strategy at all, which disease, the 3 Ds, the nine innovations, the only-statement, the five-section document, marketability, and the forced verdict (Proceed / Narrow / Test manually / Park / Kill)
- **hyperresearch** — Deep research via the HYPERRESEARCH V8 architecture   a tier-adaptive 16-step pipeline (li
- **advise-project-approach** — Research and advise on the best way to approach a software project, including architecture
- **azure-ai** — Use for Azure AI: Search, Speech, OpenAI, Document Intelligence. Helps with search, vector
- **bridgespace-bridge-skill-bridgemind-mcp** — How to use the BridgeMind MCP (mcp__bridgemind__*) effectively   projects, tasks, agents, 
- **context-restore** — Wrapper alias for the Hermes GStack context-restore skill. Canonical instructions live at 
- **context-save** — Wrapper alias for the Hermes GStack context-save skill. Canonical instructions live at /Us
- **context-search** — 2-phase context search across the PAI session registry, work directories, and ISAs for ins
- **core-web-vitals** — Optimize Core Web Vitals (LCP, INP, CLS) for better page experience and search ranking. Us
- **council-of-high-intelligence** — Convene the Council of High Intelligence   multi-persona deliberation with historical thin
- **devops/scrapers** — Global multi-engine scraper OS for any coding agent   /scrapers slash, scrapers rig-scrape
- **embedding-strategies** — Select and optimize embedding models for semantic search and RAG applications. Use when ch
- **find-skills** — Discover, search, and install skills from the skills.sh registry and local catalogs using 

Full table: `references/routing.md`
