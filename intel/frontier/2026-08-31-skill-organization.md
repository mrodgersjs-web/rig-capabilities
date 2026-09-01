---
name: frontier-skill-organization
description: Frontier research — how agent-skill libraries are organized, scoped, and discovered at scale (2026)
source: frontier
outcome: research-intel: skill organization
verified_on: 2026-08-31
quality_floor: 0.6
---

# Skill Organization at Scale — Frontier Findings (2026-08-31)

## The format converged: folder + SKILL.md + progressive disclosure
Anthropic's Agent Skills spec (now the de-facto cross-platform format) defines a skill
as a folder with a required `SKILL.md` (YAML frontmatter + instructions) and optional
bundled resources in `scripts/`, `references/`, `assets/`. Loading is three-level:

1. **Metadata** (`name` + `description`) — always in context (~100 words). `name` is
   kebab-case ≤64 chars matching the folder; `description` ≤1024 chars and must carry
   *what it does + when to use it + trigger phrases*. All "when to use" guidance belongs
   in `description`, not the body.
2. **SKILL.md body** — loaded only when the skill triggers; recommended <500 lines.
3. **Bundled resources** — unlimited size, loaded on demand; scripts can *execute*
   without their code ever entering context.

## Scoping is hierarchical, not flat
Claude Code resolves skills across four scopes — enterprise (managed), personal
(`~/.claude/skills`), project (`.claude/skills`, propagating to repo root), and plugin
(namespaced `/plugin:skill`). Nested per-directory skills that clash with parent-scope
names are exposed under a `dir:name` namespace instead of shadowing. Skilldex (arXiv
2604.16911) generalizes this: a package manager + registry with **global / shared /
project scopes**, local-first precedence, a `skillset` abstraction that groups related
skills sharing assets (vocab files, templates, reference docs), and compiler-style
line-level lint against the spec (description specificity, frontmatter validity,
structural conformance) so discoverability stays uniform across hundreds of skills.

## Discovery at 1000+ skills
- AgentSkillOS (arXiv 2603.02176) structures an open skill ecosystem as a **capability
  tree**; a usage-frequency queue selects the active subset per task.
- Category routers (e.g. agent-skill-router) keep resident context at constant cost and
  load leaf skills on demand.
- Registries are metadata-driven; conformance scoring is what keeps search quality from
  decaying as the library grows.

## What this means for rig-capabilities
1. Our `.lanes.json` overlay + taxonomy classify = the category-router pattern; the
   capability-tree idea suggests adding parent/child edges (we have `relates_to`).
2. Description discipline is load-bearing: routing quality *is* description quality.
   The V16 round engine should eventually lint descriptions the way Skilldex does
   (specificity, trigger phrases, length caps).
3. The `dir:name` clash rule validates our `fed:peer` namespacing for federation.
4. We are compliant with the three-level spec: frontmatter contract (V7), body, and
   references/ dirs; nothing to migrate.

## Sources
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- https://anthropics-skills.mintlify.app/spec/overview
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- https://code.claude.com/docs/en/skills.md
- https://arxiv.org/html/2604.16911 (Skilldex)
- https://arxiv.org/html/2603.02176 (AgentSkillOS)
- https://github.com/anthropics/claude-code/issues/68871 (nested namespace rule)
- https://github.com/AnamKwon/agent-skill-router
