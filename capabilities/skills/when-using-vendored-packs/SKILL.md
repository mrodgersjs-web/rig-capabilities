---
name: when-using-vendored-packs
description: "When a task matches a third-party vendored collection (gstack, matt-*, acs-*, corey-*, zazen-*, dwk-* and similar), use this to route into the right pack. Routes to 262 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: vendored-collections
  skill-count: "262"
done_when:
  - 'grep:capabilities/skills/when-using-vendored-packs/SKILL.md:[M]UST NOT load a second child to'
  - 'grep:capabilities/skills/when-using-vendored-packs/SKILL.md:[M]UST load exactly ONE child skill per task step'
  - 'grep:capabilities/skills/when-using-vendored-packs/references/routing.md:^\| Skill \| Source \| One-liner \| Sub-skills \|'
---

# when-using-vendored-packs

Tier-1 meta-skill. Job to be done: When a task matches a third-party vendored collection (gstack, matt-*, acs-*, corey-*, zazen-*, dwk-* and similar), use this to route into the right pack.

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
- **acs-a-quick-build** — Distilled from Agentic Coding School   A Quick Build. Trigger: when the user names or desc
- **acs-add-dir** — Distilled from Agentic Coding School   /add-dir. Trigger: when the user names or describes
- **acs-agent** — Distilled from Agentic Coding School   --agent. Trigger: when the user names or describes 
- **acs-agent-view** — Distilled from Agentic Coding School   Agent View. Trigger: when the user names or describ
- **acs-archiving-plans-after-clear-context** — Distilled from Agentic Coding School   Archiving Plans After Clear Context. Trigger: when 
- **acs-artefact-tool** — Distilled from Agentic Coding School   Artefact Tool. Trigger: when the user names or desc
- **acs-ask-user-question-tool** — Distilled from Agentic Coding School   Ask User Question Tool. Trigger: when the user name
- **acs-auto-memory** — Distilled from Agentic Coding School   Auto Memory. Trigger: when the user names or descri
- **acs-auto-permission-mode** — Distilled from Agentic Coding School   Auto Permission Mode. Trigger: when the user names 
- **acs-autofix-pr** — Distilled from Agentic Coding School   /autofix-pr. Trigger: when the user names or descri
- **acs-batch** — Distilled from Agentic Coding School   /batch. Trigger: when the user names or describes t
- **acs-better-dictation** — Distilled from Agentic Coding School   Better Dictation. Trigger: when the user names or d

Full table: `references/routing.md`
