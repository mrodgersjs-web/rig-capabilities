---
name: when-writing-content
description: "When writing articles, newsletters, copy, hooks, or any long-form deliverable, use this to route to the right writing skill so output sounds like Mike and earns its place. Routes to 80 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: content-writing
  skill-count: "80"
done_when:
  - 'grep:capabilities/skills/when-writing-content/SKILL.md:[M]UST NOT load a second child to'
  - 'grep:capabilities/skills/when-writing-content/SKILL.md:[M]UST load exactly ONE child skill per task step'
  - 'grep:capabilities/skills/when-writing-content/references/routing.md:^\| Skill \| Source \| One-liner \| Sub-skills \|'
---

# when-writing-content

Tier-1 meta-skill. Job to be done: When writing articles, newsletters, copy, hooks, or any long-form deliverable, use this to route to the right writing skill so output sounds like Mike and earns its place.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 80-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **angular-migration** — Migrate from AngularJS to Angular using hybrid mode, incremental component rewriting, and 
- **anti-ai-writing** — Edit any piece of writing to remove AI tells. Strips banned words ("delve," "unlock," "lev
- **anti-slop** — Turn AI-written copy into copy a human would ship. Lint for AI tells, rewrite, cleanse wit
- **architecture-decision-records** — Write and maintain Architecture Decision Records (ADRs) following best practices for techn
- **article-writing** — Write articles, guides, blog posts, tutorials, newsletter issues, and other long-form cont
- **avoid-ai-writing** — Audit and rewrite content to remove AI writing patterns ("AI-isms"). Use this skill when a
- **blog-post-template** —      ,   masthead hero figures pull quote     " tags: ["blog", "essay", "case study", "  "
- **bridgespace-bridge-skill-github-commit** — Universal commit-and-push methodology. Stages every local change in the current repo, writ
- **bridgespace-bridge-skill-seo** — Modern (2025/2026) SEO methodology for auditing and writing pages   title tags, meta, head
- **coding-agent-failure-modes** — 11 coding-agent failure modes (write-for-agent, instruction rot, compact-is-not-memory, ho
- **content-automation** — Route content-automation tasks to an existing child skill; this router adds no capabilitie
- **content-automation/linkedin-content-planning** — Use for the Alfred LinkedIn content-planner cron job. ---  # LinkedIn Content Planning (Al
- **ms-\* family (marketingskills, MIT, 11 writing skills)** — copywriting, copy-editing, content-strategy, social, emails, sms, ad-creative, image, video, lead-magnets, sales-enablement; read the ms-product-marketing `.agents/product-marketing.md` context first. Full one-liners in references/routing.md.

Full table: `references/routing.md`
