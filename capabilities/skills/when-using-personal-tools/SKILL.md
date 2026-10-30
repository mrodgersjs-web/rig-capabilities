---
name: when-using-personal-tools
description: "When working in Gmail, Notion, Slack, password managers, Office files, PDFs, or browser utilities, use this to route to the right tool skill. Routes to 65 skills; read references/routing.md for the full table."
metadata:
  purpose: meta-skill
  generated-by: skillshilp-upgrade
  category: personal-ops
  skill-count: "65"
done_when:
  - 'grep:capabilities/skills/when-using-personal-tools/SKILL.md:[M]UST NOT load a second child to'
  - 'grep:capabilities/skills/when-using-personal-tools/SKILL.md:[M]UST load exactly ONE child skill per task step'
  - 'grep:capabilities/skills/when-using-personal-tools/references/routing.md:^\| Skill \| Source \| One-liner \| Sub-skills \|'
---

# when-using-personal-tools

Tier-1 meta-skill. Job to be done: When working in Gmail, Notion, Slack, password managers, Office files, PDFs, or browser utilities, use this to route to the right tool skill.

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
1. Scan the quick index below. If nothing obviously matches, read `references/routing.md` for the full 65-skill table with one-line descriptions.
2. Load exactly one child skill. If it names sub-skills, load the one relevant sub-skill.
3. Never load more than one skill plus one sub-skill for a single task step.

## Quick index (top skills)
- **1password** — Read this skill when the user uses 1Password. icon: https://static.asidehq.com/apps/builti
- **apple-passwords** — Use Apple Passwords on macOS when the user asks to save, retrieve, or autofill Apple/iClou
- **aside** — Use this when you need to inspect or update Aside daemon settings, Projects, sessions, rou
- **bitwarden** — Read this skill when the user uses Bitwarden. icon: https://static.asidehq.com/apps/builti
- **browser-harness** — Direct browser control via CDP. Use when the user wants to automate, scrape, test, or inte
- **browser-skill** — Use when the user asks to automate their logged-in Chromium browser: visit and read pages,
- **browser-to-skill** — [ACS-641][ACS-747] HAR-capture a site once, then generate an endpoint skill with self-heal
- **captcha-solver** — Read this skill when a page has a CAPTCHA that needs solving (reCAPTCHA, Turnstile, hCaptc
- **chrome** — Read this when you need to use Chrome extension APIs: managing bookmarks, tabs, windows, t
- **chrome-cowork** — Full-task Chrome cowork agent. Completes multi-step browser jobs end-to-end in Mike's real
- **dashlane** — Read this skill when the user uses Dashlane. icon: https://static.asidehq.com/apps/builtin
- **docx** — Use this skill whenever a Word .docx file must be read, created, inspected, or edited, inc

Full table: `references/routing.md`
