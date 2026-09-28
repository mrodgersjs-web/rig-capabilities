---
name: when-shipping-code
description: "When building, debugging, testing, refactoring, or reviewing software, use this to route to the right engineering skill so code ships correct and verified. Routes to 262 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: code-engineering
  skill-count: "262"
---

# when-shipping-code

Tier-1 meta-skill. Job to be done: When building, debugging, testing, refactoring, or reviewing software, use this to route to the right engineering skill so code ships correct and verified.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 262-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **app-studio** — META: build web and mobile apps end to end (11 stages, 13 sub-skills, agents, harnesses, loops, hooks, JEV criteria, 30 typed lessons)
- **agentic-best-practices** — Complete best practices from Ray Amjad's 2,800+ hours with Claude Code. Context window man
- **agentic-coding-school** — Techniques from Ray Amjad's Agentic Coding School (2,800+ hours with Claude Code). Context
- **ai-regression-testing** — Regression testing strategies for AI-assisted development. Sandbox-mode API testing withou
- **ai-slop-cleaner** — Run an anti-slop cleanup/refactor/deslop workflow ---  # AI Slop Cleaner Skill  Reduce AI-
- **ai-user-testing** — Run governed AI user-testing for web, iOS, API, data, AI, vision, accessibility, security,
- **app-store-ship** — Ship Flutter/native apps to Apple App Store + Google Play. ---  # app-store-ship  Ship a F
- **autopilot** — Run a founder-grade autonomous execution lane from the canonical stack pack. ---  # autopi
- **azure-aigateway** — Configure Azure API Management as an AI Gateway for AI models, MCP tools, and agents. WHEN
- **azure-cloud-migrate** — Assess and migrate cross-cloud workloads to Azure with reports and code conversion. Suppor
- **azure-diagnostics** — Debug Azure production issues on Azure using AppLens, Azure Monitor, resource health, and 
- **azure-rbac** — Helps users find the right Azure RBAC role for an identity with least privilege access, th
- **azure-upgrade** — Assess and upgrade Azure workloads between plans, tiers, or SKUs, or modernize Azure SDK d

Full table: `references/routing.md`
